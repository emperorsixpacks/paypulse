from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.enums import BillingInterval, InvoiceStatus, SubscriptionStatus
from src.paypulse.repositories.subscription_repository import SubscriptionRepository


class SubscriptionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = SubscriptionRepository(db)

    async def create(self, customer, plan, session=None):
        now = datetime.now(UTC)
        period_end = self._calculate_period_end(now, plan.interval, plan.interval_count)

        status = SubscriptionStatus.ACTIVE
        trial_end = None
        if plan.trial_period_days and plan.trial_period_days > 0:
            status = SubscriptionStatus.TRIALING
            trial_end = now + timedelta(days=plan.trial_period_days)
            period_end = trial_end

        subscription = await self.repo.create({
            "project_id": plan.project_id,
            "customer_id": customer.id,
            "plan_id": plan.id,
            "status": status,
            "current_period_start": now,
            "current_period_end": period_end,
            "trial_end": trial_end,
        })

        if session:
            session.subscription_id = subscription.id
            await self.db.flush()

        return subscription

    async def get(self, subscription_id: UUID, project_id: UUID):
        sub = await self.repo.get(subscription_id)
        if sub is None or sub.project_id != project_id:
            return None
        return sub

    async def list(self, project_id: UUID, status: SubscriptionStatus | None = None):
        if status:
            return await self.repo.get_by_status(project_id, status)
        return await self.repo.get_by_project(project_id)

    async def cancel(self, subscription_id: UUID, project_id: UUID, cancel_at_period_end: bool = False):
        sub = await self.get(subscription_id, project_id)
        if sub is None:
            return None
        if cancel_at_period_end:
            sub.cancel_at_period_end = True
        else:
            sub.status = SubscriptionStatus.CANCELLED
            sub.cancelled_at = datetime.now(UTC)
        await self.db.flush()
        return sub

    async def extend_period(self, subscription):
        subscription.current_period_start = subscription.current_period_end
        subscription.current_period_end = self._calculate_period_end(
            subscription.current_period_end,
            subscription.plan.interval,
            subscription.plan.interval_count,
        )
        await self.db.flush()

    async def mark_past_due(self, subscription_id: UUID):
        sub = await self.repo.get(subscription_id)
        if sub:
            sub.status = SubscriptionStatus.PAST_DUE
            await self.db.flush()

    async def mark_expired(self, subscription_id: UUID):
        sub = await self.repo.get(subscription_id)
        if sub:
            sub.status = SubscriptionStatus.EXPIRED
            await self.db.flush()

    def _calculate_period_end(self, start: datetime, interval: BillingInterval, count: int) -> datetime:
        if interval == BillingInterval.DAILY:
            return start + timedelta(days=count)
        elif interval == BillingInterval.WEEKLY:
            return start + timedelta(weeks=count)
        elif interval == BillingInterval.MONTHLY:
            month = start.month + count
            year = start.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            day = min(start.day, 28)
            return start.replace(year=year, month=month, day=day)
        elif interval == BillingInterval.YEARLY:
            return start.replace(year=start.year + count)
        return start + timedelta(days=30)
