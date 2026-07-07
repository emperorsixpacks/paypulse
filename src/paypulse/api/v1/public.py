from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db
from src.paypulse.services.checkout_service import CheckoutService
from src.paypulse.services.nomba_webhook_service import NombaWebhookService

router = APIRouter(prefix="/checkout", tags=["public-checkout"])


@router.get("/{code}/session")
async def get_checkout_session(code: str, db: AsyncSession = Depends(get_db)):
    service = CheckoutService(db)
    data = await service.get_public_session_data(code)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkout not found or expired")
    return data


@router.post("/{code}/pay")
async def pay_checkout(code: str, body: dict, db: AsyncSession = Depends(get_db)):
    service = NombaWebhookService(db)
    result = await service.handle_payment_webhook({**body, "orderReference": code})
    if result:
        return {"status": "ok"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment processing failed")


@router.get("/health")
async def health():
    return {"status": "ok"}
