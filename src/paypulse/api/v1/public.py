from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db
from src.paypulse.models.checkout import CheckoutSession
from src.paypulse.models.enums import CheckoutStatus
from src.paypulse.models.plan import Plan
from src.paypulse.repositories.checkout_repository import CheckoutRepository
from src.paypulse.repositories.plan_repository import PlanRepository

router = APIRouter(prefix="/checkout", tags=["public-checkout"])


@router.get("/{code}/session")
async def get_checkout_session(code: str, db: AsyncSession = Depends(get_db)):
    repo = CheckoutRepository(db)
    session = await repo.get_active_by_code(code)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkout not found or expired")

    plan_repo = PlanRepository(db)
    plan = await plan_repo.get(session.plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    return {
        "id": str(session.id),
        "code": session.code,
        "status": session.status.value,
        "plan_name": plan.name,
        "amount": float(plan.amount),
        "currency": plan.currency,
        "interval": plan.interval.value,
        "customer_email": session.customer_email,
        "customer_name": session.customer_name,
        "success_url": session.success_url,
        "cancel_url": session.cancel_url,
        "expires_at": session.expires_at.isoformat(),
    }


@router.post("/{code}/pay")
async def pay_checkout(code: str, body: dict, db: AsyncSession = Depends(get_db)):
    repo = CheckoutRepository(db)
    session = await repo.get_active_by_code(code)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkout not found or expired")

    # TODO: integrate Nomba charge here
    # For now, simulate success
    return {
        "success": True,
        "redirect_url": session.success_url,
    }
