import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum
from sqlmodel import Column, Field, Relationship

from src.paypulse.models.base import Base


class OrgRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Membership(Base, table=True):
    __tablename__ = "memberships"

    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", nullable=False, index=True)
    role: OrgRole = Field(
        sa_column=Column(SAEnum(OrgRole, name="org_role", create_constraint=True), nullable=False, default=OrgRole.MEMBER),
        default=OrgRole.MEMBER,
    )

    user: "User" = Relationship(back_populates="memberships")
    organization: "Organization" = Relationship(back_populates="memberships")
