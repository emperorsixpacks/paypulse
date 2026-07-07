from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.merchant import Project
from src.paypulse.repositories.plan_repository import PlanRepository
from src.paypulse.schemas.plan import PlanCreate, PlanResponse, PlanUpdate

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanResponse])
async def list_plans(
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = PlanRepository(db)
    plans = await repo.get_by_project(project.id)
    return plans


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    body: PlanCreate,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = PlanRepository(db)
    plan = await repo.create({
        "project_id": project.id,
        "name": body.name,
        "amount": body.amount,
        "currency": body.currency,
        "interval": body.interval,
        "interval_count": body.interval_count,
        "trial_period_days": body.trial_period_days,
    })
    return plan


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = PlanRepository(db)
    plan = await repo.get(UUID(plan_id))
    if plan is None or plan.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.patch("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    body: PlanUpdate,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = PlanRepository(db)
    plan = await repo.get(UUID(plan_id))
    if plan is None or plan.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    updates = body.model_dump(exclude_unset=True)
    updated = await repo.update(plan.id, updates)
    return updated


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = PlanRepository(db)
    plan = await repo.get(UUID(plan_id))
    if plan is None or plan.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    await repo.delete(plan.id)
