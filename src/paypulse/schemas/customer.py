from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CustomerResponse(BaseModel):
    id: UUID
    email: str
    name: str | None
    nomba_customer_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerSubscriptionResponse(BaseModel):
    id: UUID
    plan_name: str
    status: str
    amount: float
    currency: str
    interval: str
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: datetime | None

    model_config = {"from_attributes": True}


class CustomerInvoiceResponse(BaseModel):
    id: UUID
    amount: float
    currency: str
    status: str
    due_date: datetime
    paid_at: datetime | None

    model_config = {"from_attributes": True}


class CustomerDetailResponse(BaseModel):
    customer: CustomerResponse
    subscriptions: list[CustomerSubscriptionResponse]
    invoices: list[CustomerInvoiceResponse]
