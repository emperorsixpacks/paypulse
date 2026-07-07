from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.merchant import Project
from src.paypulse.repositories.subscription_repository import SubscriptionRepository
from src.paypulse.schemas.subscription import SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = SubscriptionRepository(db)
    subs = await repo.get_by_project(project.id)
    return [
        SubscriptionResponse(
            id=s.id,
            customer_email=s.customer.email if s.customer else "Unknown",
            plan_name=s.plan.name if s.plan else "Unknown",
            status=s.status.value,
            amount=float(s.plan.amount) if s.plan else 0,
            currency=s.plan.currency if s.plan else "NGN",
            interval=s.plan.interval.value if s.plan else "MONTHLY",
            current_period_start=s.current_period_start,
            current_period_end=s.current_period_end,
            cancelled_at=s.cancelled_at,
            created_at=s.created_at,
        )
        for s in subs
    ]


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    from src.paypulse.models.billing import Subscription

    repo = SubscriptionRepository(db)
    sub = await repo.get(UUID(subscription_id))
    if sub is None or sub.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    return SubscriptionResponse(
        id=sub.id,
        customer_email=sub.customer.email if sub.customer else "Unknown",
        plan_name=sub.plan.name if sub.plan else "Unknown",
        status=sub.status.value,
        amount=float(sub.plan.amount) if sub.plan else 0,
        currency=sub.plan.currency if sub.plan else "NGN",
        interval=sub.plan.interval.value if sub.plan else "MONTHLY",
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancelled_at=sub.cancelled_at,
        created_at=sub.created_at,
    )
