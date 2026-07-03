import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.paypulse.models.base import Base, BaseModel
from src.paypulse.models.enums import BillingInterval


class Plan(BaseModel, Base):
    __tablename__ = "plans"

    merchant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("merchants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    interval: Mapped[BillingInterval] = mapped_column(nullable=False)
    interval_count: Mapped[int] = mapped_column(Integer, default=1)
    trial_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="plan")
