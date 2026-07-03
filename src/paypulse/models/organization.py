from sqlmodel import Field, Relationship

from src.paypulse.models.base import Base


class Organization(Base, table=True):
    __tablename__ = "organizations"

    name: str = Field(nullable=False, max_length=255)
    slug: str = Field(unique=True, index=True, nullable=False, max_length=255)
    description: str | None = Field(default=None, max_length=500)

    memberships: list["Membership"] = Relationship(back_populates="organization")
