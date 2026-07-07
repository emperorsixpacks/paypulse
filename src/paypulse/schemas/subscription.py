from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CancelRequest(BaseModel):
    cancel_at_period_end: bool = False


class RefundInfo(BaseModel):
    refund_amount: float
    reason: str = ""
    policy_name: str | None = None
    refund_type: str | None = None
    remaining_ratio: float | None = None
    period_start: str | None = None
    period_end: str | None = None
    cancellation_fee: float | None = None


class SubscriptionResponse(BaseModel):
    id: UUID
    customer_email: str
    plan_name: str
    status: str
    amount: float
    currency: str
    interval: str
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: datetime | None
    cancel_at_period_end: bool
    cancelled_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CancelResponse(BaseModel):
    subscription_id: UUID
    status: str
    cancelled_at: datetime | None
    cancel_at_period_end: bool
    refund: RefundInfo | None = None
