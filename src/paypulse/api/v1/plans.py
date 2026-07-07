from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.merchant import Project
from src.paypulse.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from src.paypulse.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanResponse])
async def list_plans(
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = PlanService(db)
    plans = await service.list(project.id)
    return plans


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    body: PlanCreate,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = PlanService(db)
    try:
        plan = await service.create(project.id, body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return plan


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = PlanService(db)
    plan = await service.get(UUID(plan_id), project.id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.patch("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    body: PlanUpdate,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = PlanService(db)
    updates = body.model_dump(exclude_unset=True)
    plan = await service.update(UUID(plan_id), project.id, updates)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = PlanService(db)
    deleted = await service.deactivate(UUID(plan_id), project.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
