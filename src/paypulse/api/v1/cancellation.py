from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_with_merchant
from src.paypulse.models.merchant import Project
from src.paypulse.repositories.cancellation_repository import CancellationPolicyRepository
from src.paypulse.schemas.cancellation import (
    CancellationPolicyCreate,
    CancellationPolicyResponse,
    CancellationPolicyUpdate,
)
from src.paypulse.services.refund_service import RefundService

router = APIRouter(prefix="/cancellation-policies", tags=["cancellation-policies"])


@router.get("", response_model=list[CancellationPolicyResponse])
async def list_policies(
    project: Project = Depends(get_project_with_merchant),
    db: AsyncSession = Depends(get_db),
):
    repo = CancellationPolicyRepository(db)
    policies = await repo.get_by_project(project.id)
    return [
        CancellationPolicyResponse(
            id=p.id,
            name=p.name,
            refund_type=p.refund_type,
            refund_percentage=float(p.refund_percentage) if p.refund_percentage else None,
            refund_window_days=p.refund_window_days,
            prorate_refund=p.prorate_refund,
            cancellation_fee=float(p.cancellation_fee),
            apply_to_existing=p.apply_to_existing,
            is_default=p.is_default,
            created_at=p.id,
        )
        for p in policies
    ]


@router.post("", response_model=CancellationPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    body: CancellationPolicyCreate,
    project: Project = Depends(get_project_with_merchant),
    db: AsyncSession = Depends(get_db),
):
    if body.refund_type not in ("none", "full", "percentage", "prorate"):
        raise HTTPException(status_code=400, detail="refund_type must be none/full/percentage/prorate")

    if body.refund_type == "percentage" and body.refund_percentage is None:
        raise HTTPException(status_code=400, detail="refund_percentage required for percentage type")

    repo = CancellationPolicyRepository(db)

    if body.is_default:
        existing = await repo.get_default(project.id)
        if existing:
            existing.is_default = False

    policy = await repo.create({
        "project_id": project.id,
        "name": body.name,
        "refund_type": body.refund_type,
        "refund_percentage": body.refund_percentage,
        "refund_window_days": body.refund_window_days,
        "prorate_refund": body.prorate_refund,
        "cancellation_fee": body.cancellation_fee,
        "apply_to_existing": body.apply_to_existing,
        "is_default": body.is_default,
        "extra_data": body.extra_data,
    })
    await db.commit()

    return CancellationPolicyResponse(
        id=policy.id,
        name=policy.name,
        refund_type=policy.refund_type,
        refund_percentage=float(policy.refund_percentage) if policy.refund_percentage else None,
        refund_window_days=policy.refund_window_days,
        prorate_refund=policy.prorate_refund,
        cancellation_fee=float(policy.cancellation_fee),
        apply_to_existing=policy.apply_to_existing,
        is_default=policy.is_default,
        created_at=policy.id,
    )


@router.get("/{policy_id}", response_model=CancellationPolicyResponse)
async def get_policy(
    policy_id: str,
    project: Project = Depends(get_project_with_merchant),
    db: AsyncSession = Depends(get_db),
):
    repo = CancellationPolicyRepository(db)
    policy = await repo.get(UUID(policy_id))
    if policy is None or policy.project_id != project.id:
        raise HTTPException(status_code=404, detail="Policy not found")

    return CancellationPolicyResponse(
        id=policy.id,
        name=policy.name,
        refund_type=policy.refund_type,
        refund_percentage=float(policy.refund_percentage) if policy.refund_percentage else None,
        refund_window_days=policy.refund_window_days,
        prorate_refund=policy.prorate_refund,
        cancellation_fee=float(policy.cancellation_fee),
        apply_to_existing=policy.apply_to_existing,
        is_default=policy.is_default,
        created_at=policy.id,
    )


@router.patch("/{policy_id}", response_model=CancellationPolicyResponse)
async def update_policy(
    policy_id: str,
    body: CancellationPolicyUpdate,
    project: Project = Depends(get_project_with_merchant),
    db: AsyncSession = Depends(get_db),
):
    repo = CancellationPolicyRepository(db)
    policy = await repo.get(UUID(policy_id))
    if policy is None or policy.project_id != project.id:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = body.model_dump(exclude_unset=True)
    if "refund_type" in update_data and update_data["refund_type"] not in ("none", "full", "percentage", "prorate"):
        raise HTTPException(status_code=400, detail="refund_type must be none/full/percentage/prorate")

    for key, val in update_data.items():
        setattr(policy, key, val)

    if body.is_default:
        existing = await repo.get_default(project.id)
        if existing and existing.id != policy.id:
            existing.is_default = False

    await db.commit()
    await db.refresh(policy)

    return CancellationPolicyResponse(
        id=policy.id,
        name=policy.name,
        refund_type=policy.refund_type,
        refund_percentage=float(policy.refund_percentage) if policy.refund_percentage else None,
        refund_window_days=policy.refund_window_days,
        prorate_refund=policy.prorate_refund,
        cancellation_fee=float(policy.cancellation_fee),
        apply_to_existing=policy.apply_to_existing,
        is_default=policy.is_default,
        created_at=policy.id,
    )


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: str,
    project: Project = Depends(get_project_with_merchant),
    db: AsyncSession = Depends(get_db),
):
    repo = CancellationPolicyRepository(db)
    policy = await repo.get(UUID(policy_id))
    if policy is None or policy.project_id != project.id:
        raise HTTPException(status_code=404, detail="Policy not found")

    await repo.delete(policy.id)
    await db.commit()
