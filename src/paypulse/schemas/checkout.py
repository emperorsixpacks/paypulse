from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.paypulse.models.enums import CheckoutStatus


class CheckoutSessionCreate(BaseModel):
    plan_id: UUID
    customer_email: EmailStr | None = None
    customer_name: str | None = None
    success_url: str
    cancel_url: str
    metadata: dict | None = None


class CheckoutSessionResponse(BaseModel):
    id: UUID
    code: str
    checkout_url: str
    status: CheckoutStatus
    expires_at: datetime
    plan_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CheckoutPageData(BaseModel):
    session_code: str
    plan_name: str
    amount: Decimal
    currency: str
    interval: str
    business_name: str
    customer_email: str | None = None
    customer_name: str | None = None
