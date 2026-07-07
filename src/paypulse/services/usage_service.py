from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.enums import BillingType, SubscriptionStatus
from src.paypulse.repositories.plan_repository import PlanRepository
from src.paypulse.repositories.subscription_repository import SubscriptionRepository
from src.paypulse.repositories.usage_repository import UsageRepository


class UsageService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.usage_repo = UsageRepository(db)
        self.plan_repo = PlanRepository(db)
        self.sub_repo = SubscriptionRepository(db)

    async def report(
        self,
        project_id: UUID,
        subscription_id: UUID,
        quantity: Decimal,
        description: str | None,
        idempotency_key: str,
        timestamp: datetime | None = None,
    ):
        sub = await self.sub_repo.get(subscription_id)
        if sub is None or sub.project_id != project_id:
            raise ValueError("Subscription not found")
        if sub.status not in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING):
            raise ValueError("Subscription is not active")

        plan = sub.plan
        if plan is None:
            from src.paypulse.repositories.plan_repository import PlanRepository
            plan_repo = PlanRepository(self.db)
            plan = await plan_repo.get(sub.plan_id)

        if plan.billing_type != BillingType.METERED:
            raise ValueError("Cannot report usage on a FIXED plan")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        record, created = await self.usage_repo.create_with_idempotency(
            project_id=project_id,
            subscription_id=subscription_id,
            quantity=quantity,
            description=description,
            idempotency_key=idempotency_key,
            timestamp=timestamp or datetime.now(UTC),
        )
        return record, created

    async def get_current_usage(self, project_id: UUID, subscription_id: UUID):
        sub = await self.sub_repo.get(subscription_id)
        if sub is None or sub.project_id != project_id:
            raise ValueError("Subscription not found")

        plan = sub.plan
        if plan is None:
            from src.paypulse.repositories.plan_repository import PlanRepository
            plan_repo = PlanRepository(self.db)
            plan = await plan_repo.get(sub.plan_id)

        records = await self.usage_repo.get_unbilled(subscription_id)
        total_quantity = await self.usage_repo.sum_unbilled(subscription_id)
        amount_owed = total_quantity * Decimal(str(plan.price_per_unit or 0))

        return {
            "subscription_id": subscription_id,
            "plan_name": plan.name,
            "price_per_unit": plan.price_per_unit,
            "unit_label": plan.unit_label,
            "total_quantity": total_quantity,
            "amount_owed": float(amount_owed),
            "currency": plan.currency,
            "period_start": sub.current_period_start,
            "period_end": sub.current_period_end,
            "records": records,
        }

    async def get_usage_history(
        self,
        project_id: UUID,
        subscription_id: UUID,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
    ):
        sub = await self.sub_repo.get(subscription_id)
        if sub is None or sub.project_id != project_id:
            raise ValueError("Subscription not found")
        return await self.usage_repo.get_by_subscription(subscription_id, from_dt, to_dt)
