import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.paypulse.models.base import Base, BaseModel


class CancellationPolicy(BaseModel, Base):
    __tablename__ = "cancellation_policies"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    refund_type: Mapped[str] = mapped_column(String(20), nullable=False, default="none")
    refund_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    refund_window_days: Mapped[int] = mapped_column(Integer, default=0)
    prorate_refund: Mapped[bool] = mapped_column(Boolean, default=False)
    cancellation_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    apply_to_existing: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="cancellation_policies")  # noqa: F821
