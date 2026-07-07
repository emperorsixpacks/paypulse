from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.paypulse.models.enums import BillingInterval


class PlanCreate(BaseModel):
    name: str
    amount: float
    currency: str = "NGN"
    interval: BillingInterval
    interval_count: int = 1
    trial_period_days: int | None = 0


class PlanUpdate(BaseModel):
    name: str | None = None
    amount: float | None = None
    currency: str | None = None
    interval: BillingInterval | None = None
    interval_count: int | None = None
    trial_period_days: int | None = None
    is_active: bool | None = None


class PlanResponse(BaseModel):
    id: UUID
    name: str
    amount: float
    currency: str
    interval: str
    interval_count: int
    trial_period_days: int | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
