from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.enums import SubscriptionStatus
from src.paypulse.models.merchant import Project
from src.paypulse.repositories.subscription_repository import SubscriptionRepository
from src.paypulse.schemas.subscription import SubscriptionResponse
from src.paypulse.schemas.usage import (
    CurrentUsageResponse,
    UsageReportRequest,
    UsageReportResponse,
    UsageRecordResponse,
)
from src.paypulse.services.usage_service import UsageService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    status_filter: SubscriptionStatus | None = None,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = SubscriptionRepository(db)
    if status_filter:
        subs = await repo.get_by_status(project.id, status_filter)
    else:
        subs = await repo.get_by_project(project.id)
    return [
        SubscriptionResponse(
            id=s.id,
            customer_email=s.customer.email if s.customer else "Unknown",
            plan_name=s.plan.name if s.plan else "Unknown",
            status=s.status.value,
            amount=float(s.plan.amount) if s.plan and s.plan.amount else 0,
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
    repo = SubscriptionRepository(db)
    sub = await repo.get(UUID(subscription_id))
    if sub is None or sub.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    return SubscriptionResponse(
        id=sub.id,
        customer_email=sub.customer.email if sub.customer else "Unknown",
        plan_name=sub.plan.name if sub.plan else "Unknown",
        status=sub.status.value,
        amount=float(sub.plan.amount) if sub.plan and sub.plan.amount else 0,
        currency=sub.plan.currency if sub.plan else "NGN",
        interval=sub.plan.interval.value if sub.plan else "MONTHLY",
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancelled_at=sub.cancelled_at,
        created_at=sub.created_at,
    )


@router.post("/{subscription_id}/usage", response_model=UsageReportResponse, status_code=status.HTTP_201_CREATED)
async def report_usage(
    subscription_id: str,
    body: UsageReportRequest,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = UsageService(db)
    try:
        record, created = await service.report(
            project_id=project.id,
            subscription_id=UUID(subscription_id),
            quantity=body.quantity,
            description=body.description,
            idempotency_key=body.idempotency_key,
            timestamp=body.timestamp,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return UsageReportResponse(
        record=UsageRecordResponse.model_validate(record),
        created=created,
    )


@router.get("/{subscription_id}/usage", response_model=CurrentUsageResponse)
async def get_current_usage(
    subscription_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = UsageService(db)
    try:
        result = await service.get_current_usage(project.id, UUID(subscription_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return CurrentUsageResponse(
        subscription_id=result["subscription_id"],
        plan_name=result["plan_name"],
        price_per_unit=result["price_per_unit"],
        unit_label=result["unit_label"],
        total_quantity=result["total_quantity"],
        amount_owed=result["amount_owed"],
        currency=result["currency"],
        period_start=result["period_start"],
        period_end=result["period_end"],
        records=[UsageRecordResponse.model_validate(r) for r in result["records"]],
    )


@router.get("/{subscription_id}/usage/history", response_model=list[UsageRecordResponse])
async def get_usage_history(
    subscription_id: str,
    from_dt: str | None = None,
    to_dt: str | None = None,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime

    service = UsageService(db)
    from_parsed = datetime.fromisoformat(from_dt) if from_dt else None
    to_parsed = datetime.fromisoformat(to_dt) if to_dt else None

    try:
        records = await service.get_usage_history(project.id, UUID(subscription_id), from_parsed, to_parsed)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return [UsageRecordResponse.model_validate(r) for r in records]
