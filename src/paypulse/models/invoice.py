import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.paypulse.models.base import Base, BaseModel
from src.paypulse.models.enums import InvoiceStatus


class Invoice(BaseModel, Base):
    __tablename__ = "invoices"

    subscription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscriptions.id"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    merchant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("merchants.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    status: Mapped[InvoiceStatus] = mapped_column(nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    nomba_transaction_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    subscription: Mapped["Subscription"] = relationship(back_populates="invoices")
    billing_attempts: Mapped[list["BillingAttempt"]] = relationship(back_populates="invoice")
