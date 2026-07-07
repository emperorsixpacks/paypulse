from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.merchant import Project
from src.paypulse.schemas.checkout import CheckoutSessionCreate, CheckoutSessionResponse
from src.paypulse.core.settings import settings
from src.paypulse.services.checkout_service import CheckoutService

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("/sessions", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    body: CheckoutSessionCreate,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = CheckoutService(db)
    result = await service.create_session(
        project_id=project.id,
        plan_id=body.plan_id,
        customer_email=body.customer_email,
        customer_name=body.customer_name,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        metadata=body.metadata,
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found or inactive")

    session = result["session"]
    return CheckoutSessionResponse(
        id=session.id,
        code=session.code,
        checkout_url=result["checkout_url"],
        status=session.status,
        expires_at=session.expires_at,
        plan_id=session.plan_id,
        created_at=session.created_at,
    )


@router.get("/sessions", response_model=list[CheckoutSessionResponse])
async def list_checkout_sessions(
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = CheckoutService(db)
    sessions = await service.list(project.id)
    return [
        CheckoutSessionResponse(
            id=s.id,
            code=s.code,
            checkout_url=s.nomba_checkout_link or f"{settings.CHECKOUT_BASE_URL}/{s.code}",
            status=s.status,
            expires_at=s.expires_at,
            plan_id=s.plan_id,
            created_at=s.created_at,
        )
        for s in sessions
    ]


@router.get("/sessions/{code}", response_model=CheckoutSessionResponse)
async def get_checkout_session(
    code: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = CheckoutService(db)
    session = await service.get_by_code(code, project.id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return CheckoutSessionResponse(
        id=session.id,
        code=session.code,
        checkout_url=session.nomba_checkout_link or f"{settings.CHECKOUT_BASE_URL}/{session.code}",
        status=session.status,
        expires_at=session.expires_at,
        plan_id=session.plan_id,
        created_at=session.created_at,
    )


@router.delete("/sessions/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_checkout_session(
    code: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    service = CheckoutService(db)
    cancelled = await service.cancel(code, project.id)
    if cancelled is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not pending")
