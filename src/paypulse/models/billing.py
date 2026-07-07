import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.paypulse.models.base import Base, BaseModel
from src.paypulse.models.enums import (
    BillingAttemptStatus,
    BillingInterval,
    BillingType,
    InvoiceStatus,
    SubscriptionStatus,
)


class Plan(BaseModel, Base):
    __tablename__ = "plans"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    billing_type: Mapped[BillingType] = mapped_column(nullable=False, default=BillingType.FIXED)
    amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    price_per_unit: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    unit_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    interval: Mapped[BillingInterval] = mapped_column(nullable=False)
    interval_count: Mapped[int] = mapped_column(Integer, default=1)
    trial_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="plan")
    project: Mapped["Project"] = relationship(back_populates="plans")  # noqa: F821


class Subscription(BaseModel, Base):
    __tablename__ = "subscriptions"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id"), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(nullable=False)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="subscriptions")  # noqa: F821
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")  # noqa: F821
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="subscription")
    usage_records: Mapped[list["UsageRecord"]] = relationship(back_populates="subscription")  # noqa: F821
    project: Mapped["Project"] = relationship(back_populates="subscriptions")  # noqa: F821


class Invoice(BaseModel, Base):
    __tablename__ = "invoices"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    subscription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscriptions.id"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    status: Mapped[InvoiceStatus] = mapped_column(nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    nomba_transaction_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    subscription: Mapped["Subscription"] = relationship(back_populates="invoices")
    customer: Mapped["Customer"] = relationship(back_populates="invoices")  # noqa: F821
    billing_attempts: Mapped[list["BillingAttempt"]] = relationship(back_populates="invoice")
    usage_records: Mapped[list["UsageRecord"]] = relationship(back_populates="invoice")  # noqa: F821
    project: Mapped["Project"] = relationship(back_populates="invoices")  # noqa: F821


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


class UsageRecord(BaseModel, Base):
    __tablename__ = "usage_records"
    __table_args__ = (
        {"comment": "Append-only usage records for METERED billing"},
    )

    subscription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscriptions.id"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    billed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    billed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("invoices.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    subscription: Mapped["Subscription"] = relationship(back_populates="usage_records")  # noqa: F821
    invoice: Mapped["Invoice | None"] = relationship(back_populates="usage_records")  # noqa: F821
    project: Mapped["Project"] = relationship()  # noqa: F821
