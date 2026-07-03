from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_merchant_from_api_key
from src.paypulse.models.enums import CheckoutStatus
from src.paypulse.models.merchant import Merchant
from src.paypulse.repositories.checkout_repository import CheckoutRepository
from src.paypulse.repositories.plan_repository import PlanRepository
from src.paypulse.schemas.checkout import CheckoutSessionCreate, CheckoutSessionResponse
from src.paypulse.core.settings import settings

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("/sessions", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    body: CheckoutSessionCreate,
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    plan_repo = PlanRepository(db)
    plan, err = await plan_repo.get(body.plan_id)
    if err or plan is None or plan.merchant_id != merchant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    checkout_repo = CheckoutRepository(db)
    code = CheckoutSession.generate_code()

    session_data = {
        "merchant_id": merchant.id,
        "plan_id": body.plan_id,
        "code": code,
        "customer_email": body.customer_email,
        "customer_name": body.customer_name,
        "success_url": body.success_url,
        "cancel_url": body.cancel_url,
        "expires_at": CheckoutSession.default_expiry(),
        "extra_data": body.metadata,
    }

    session = await checkout_repo.create(session_data)

    return CheckoutSessionResponse(
        id=session.id,
        code=session.code,
        checkout_url=f"{settings.CHECKOUT_BASE_URL}/{session.code}",
        status=session.status,
        expires_at=session.expires_at,
        plan_id=session.plan_id,
        created_at=session.created_at,
    )


@router.get("/sessions", response_model=list[CheckoutSessionResponse])
async def list_checkout_sessions(
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = CheckoutRepository(db)
    sessions = await repo.get_by_merchant(merchant.id)
    return [
        CheckoutSessionResponse(
            id=s.id,
            code=s.code,
            checkout_url=f"{settings.CHECKOUT_BASE_URL}/{s.code}",
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
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = CheckoutRepository(db)
    session = await repo.get_by_code(code)
    if session is None or session.merchant_id != merchant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return CheckoutSessionResponse(
        id=session.id,
        code=session.code,
        checkout_url=f"{settings.CHECKOUT_BASE_URL}/{session.code}",
        status=session.status,
        expires_at=session.expires_at,
        plan_id=session.plan_id,
        created_at=session.created_at,
    )


@router.delete("/sessions/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_checkout_session(
    code: str,
    merchant: Merchant = Depends(get_merchant_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = CheckoutRepository(db)
    session = await repo.get_by_code(code)
    if session is None or session.merchant_id != merchant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.status != CheckoutStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not pending")

    session.status = CheckoutStatus.CANCELLED
    await db.flush()
