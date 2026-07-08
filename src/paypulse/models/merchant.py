import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.paypulse.models.base import Base, BaseModel


class Merchant(BaseModel, Base):
    __tablename__ = "merchants"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    projects: Mapped[list["Project"]] = relationship(back_populates="merchant")


class Project(BaseModel, Base):
    __tablename__ = "projects"

    merchant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("merchants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    merchant: Mapped["Merchant"] = relationship(back_populates="projects")
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="project")
    plans: Mapped[list["Plan"]] = relationship(back_populates="project")  # noqa: F821
    customers: Mapped[list["Customer"]] = relationship(back_populates="project")  # noqa: F821
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="project")  # noqa: F821
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="project")  # noqa: F821
    webhook_endpoints: Mapped[list["WebhookEndpoint"]] = relationship(back_populates="project")  # noqa: F821
    cancellation_policies: Mapped[list["CancellationPolicy"]] = relationship(back_populates="project")  # noqa: F821


class ApiKey(BaseModel, Base):
    __tablename__ = "api_keys"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)
    hashed_key: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[uuid.UUID | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="api_keys")
