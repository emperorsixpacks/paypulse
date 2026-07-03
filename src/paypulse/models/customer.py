import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.paypulse.models.base import Base, BaseModel


class Customer(BaseModel, Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("email", "merchant_id", name="uq_customer_email_merchant"),
    )

    merchant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("merchants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nomba_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    card_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="customer")
