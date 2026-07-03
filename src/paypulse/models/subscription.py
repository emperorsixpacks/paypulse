import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.paypulse.models.base import Base, BaseModel
from src.paypulse.models.enums import SubscriptionStatus


class Subscription(BaseModel, Base):
    __tablename__ = "subscriptions"

    merchant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("merchants.id"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id"), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(nullable=False)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="subscription")
