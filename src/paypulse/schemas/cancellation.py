from uuid import UUID

from pydantic import BaseModel


class CancellationPolicyCreate(BaseModel):
    name: str
    refund_type: str = "none"
    refund_percentage: float | None = None
    refund_window_days: int = 0
    prorate_refund: bool = False
    cancellation_fee: float = 0
    apply_to_existing: bool = True
    is_default: bool = False
    extra_data: dict | None = None


class CancellationPolicyUpdate(BaseModel):
    name: str | None = None
    refund_type: str | None = None
    refund_percentage: float | None = None
    refund_window_days: int | None = None
    prorate_refund: bool | None = None
    cancellation_fee: float | None = None
    apply_to_existing: bool | None = None
    is_default: bool | None = None
    extra_data: dict | None = None


class CancellationPolicyResponse(BaseModel):
    id: UUID
    name: str
    refund_type: str
    refund_percentage: float | None
    refund_window_days: int
    prorate_refund: bool
    cancellation_fee: float
    apply_to_existing: bool
    is_default: bool
    created_at: UUID

    model_config = {"from_attributes": True}


class RefundEstimateRequest(BaseModel):
    subscription_id: UUID
    policy_id: UUID | None = None


class RefundEstimateResponse(BaseModel):
    refund_amount: float
    policy_name: str
    refund_type: str
    remaining_ratio: float
    period_start: str
    period_end: str
    cancellation_fee: float
