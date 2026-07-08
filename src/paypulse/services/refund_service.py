from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.enums import BillingType
from src.paypulse.models.cancellation import CancellationPolicy
from src.paypulse.repositories.cancellation_repository import CancellationPolicyRepository


class RefundService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.policy_repo = CancellationPolicyRepository(db)

    async def calculate_refund(
        self,
        subscription,
        policy: CancellationPolicy | None = None,
    ) -> dict:
        plan = subscription.plan
        if plan is None:
            return {"refund_amount": 0, "reason": "no_plan"}

        if plan.billing_type != BillingType.FIXED:
            return {"refund_amount": 0, "reason": "metered_no_refund"}

        if policy is None:
            policy = await self.policy_repo.get_default(subscription.project_id)

        if policy is None:
            return {"refund_amount": 0, "reason": "no_policy"}

        now = datetime.now(UTC)
        period_start = subscription.current_period_start
        period_end = subscription.current_period_end

        total_seconds = (period_end - period_start).total_seconds()
        elapsed_seconds = (now - period_start).total_seconds()

        if total_seconds <= 0:
            return {"refund_amount": 0, "reason": "invalid_period"}

        remaining_ratio = max(0, (total_seconds - elapsed_seconds) / total_seconds)
        base_amount = float(plan.amount) if plan.amount else 0

        if policy.refund_type == "none":
            refund = 0
        elif policy.refund_type == "full":
            if policy.refund_window_days > 0:
                days_used = elapsed_seconds / 86400
                if days_used <= policy.refund_window_days:
                    refund = base_amount
                else:
                    refund = 0
            else:
                refund = base_amount
        elif policy.refund_type == "percentage":
            refund = base_amount * float(policy.refund_percentage or 0) / 100
        elif policy.refund_type == "prorate":
            refund = base_amount * remaining_ratio
        else:
            refund = 0

        refund = max(0, refund - float(policy.cancellation_fee))

        return {
            "refund_amount": round(refund, 2),
            "policy_name": policy.name,
            "refund_type": policy.refund_type,
            "remaining_ratio": round(remaining_ratio, 4),
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "cancellation_fee": float(policy.cancellation_fee),
        }
