from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InvoiceResponse(BaseModel):
    id: UUID
    customer_email: str
    amount: float
    currency: str
    status: str
    due_date: datetime
    paid_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
