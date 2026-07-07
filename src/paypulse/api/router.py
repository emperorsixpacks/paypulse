from fastapi import APIRouter

from src.paypulse.api.v1.auth import router as auth_router
from src.paypulse.api.v1.checkout import router as checkout_router
from src.paypulse.api.v1.customers import router as customers_router
from src.paypulse.api.v1.invoices import router as invoices_router
from src.paypulse.api.v1.merchants import router as merchants_router
from src.paypulse.api.v1.plans import router as plans_router
from src.paypulse.api.v1.public import router as public_router
from src.paypulse.api.v1.subscriptions import router as subscriptions_router
from src.paypulse.api.v1.webhooks import router as webhooks_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(merchants_router)
api_router.include_router(plans_router)
api_router.include_router(checkout_router)
api_router.include_router(customers_router)
api_router.include_router(subscriptions_router)
api_router.include_router(invoices_router)
api_router.include_router(webhooks_router)
api_router.include_router(public_router)
