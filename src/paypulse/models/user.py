import uuid

from sqlmodel import Field, Relationship

from src.paypulse.models.base import BaseSQLModel, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, BaseSQLModel, table=True):
    __tablename__ = "users"

    email: str = Field(unique=True, index=True, nullable=False, max_length=255)
    name: str = Field(nullable=False, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    password_hash: str = Field(nullable=False, max_length=255)

    memberships: list["Membership"] = Relationship(back_populates="user")
