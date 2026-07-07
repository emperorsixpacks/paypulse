from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
    created_at: datetime

    model_config = {"from_attributes": True}
