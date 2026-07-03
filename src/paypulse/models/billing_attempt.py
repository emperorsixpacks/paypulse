import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.paypulse.models.base import Base, BaseModel
from src.paypulse.models.enums import BillingAttemptStatus


class BillingAttempt(BaseModel, Base):
    __tablename__ = "billing_attempts"

    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    status: Mapped[BillingAttemptStatus] = mapped_column(nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    nomba_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    invoice: Mapped["Invoice"] = relationship(back_populates="billing_attempts")
