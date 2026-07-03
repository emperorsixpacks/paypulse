import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.paypulse.models.base import Base, BaseModel
from src.paypulse.models.enums import CheckoutStatus


class CheckoutSession(BaseModel, Base):
    __tablename__ = "checkout_sessions"

    merchant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("merchants.id"), nullable=False, index=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[CheckoutStatus] = mapped_column(nullable=False, default=CheckoutStatus.PENDING)
    success_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    cancel_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subscriptions.id"), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    @staticmethod
    def generate_code() -> str:
        return secrets.token_urlsafe(24)

    @staticmethod
    def default_expiry() -> datetime:
        return datetime.now(UTC) + timedelta(hours=24)
