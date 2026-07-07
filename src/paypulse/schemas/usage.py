from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class UsageReportRequest(BaseModel):
    quantity: Decimal = Field(gt=0)
    description: str | None = None
    idempotency_key: str = Field(max_length=255)
    timestamp: datetime | None = None


class UsageRecordResponse(BaseModel):
    id: UUID
    subscription_id: UUID
    quantity: Decimal
    description: str | None
    idempotency_key: str
    billed: bool
    billed_at: datetime | None
    invoice_id: UUID | None
    timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class CurrentUsageResponse(BaseModel):
    subscription_id: UUID
    plan_name: str
    price_per_unit: Decimal | None
    unit_label: str | None
    total_quantity: Decimal
    amount_owed: float
    currency: str
    period_start: datetime
    period_end: datetime
    records: list[UsageRecordResponse]


class UsageReportResponse(BaseModel):
    record: UsageRecordResponse
    created: bool
