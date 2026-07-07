from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.enums import SubscriptionStatus
from src.paypulse.repositories.billing_attempt_repository import BillingAttemptRepository
from src.paypulse.repositories.subscription_repository import SubscriptionRepository

RETRY_SCHEDULE = {1: 1, 2: 3, 3: 7}  # attempt -> days until next retry


class DunningService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.attempt_repo = BillingAttemptRepository(db)
        self.subscription_repo = SubscriptionRepository(db)

    async def schedule_retry(self, subscription, amount: float):
        attempt_count = await self.attempt_repo.get_attempt_count(subscription.invoices[-1].id) if subscription.invoices else 0
        next_attempt = attempt_count + 1

        if next_attempt > 3:
            subscription.status = SubscriptionStatus.EXPIRED
            await self.db.flush()
            return

        days = RETRY_SCHEDULE.get(next_attempt, 7)
        await self.attempt_repo.create({
            "invoice_id": subscription.invoices[-1].id if subscription.invoices else None,
            "status": "PENDING",
            "attempt_number": next_attempt,
            "next_retry_at": datetime.now(UTC) + timedelta(days=days),
            "attempted_at": datetime.now(UTC),
        })

        subscription.status = SubscriptionStatus.PAST_DUE
        await self.db.flush()

    async def get_due_retries(self, as_of: datetime):
        return await self.attempt_repo.get_due_retries(as_of)
