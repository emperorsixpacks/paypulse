from uuid import UUID

from sqlmodel import select

from src.paypulse.infrastructure.repositories.base import BaseRepository
from src.paypulse.models.membership import Membership, OrgRole
from src.paypulse.types import Error, error


class MembershipRepository(BaseRepository[Membership]):
    _model = Membership

    async def get_by_id(self, membership_id: UUID) -> tuple[Membership | None, Error]:
        return await self.get(membership_id)

    async def get_user_org_membership(
        self, user_id: UUID, organization_id: UUID
    ) -> tuple[Membership | None, Error]:
        stmt = select(Membership).where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        membership = result.scalars().first()
        if membership is None:
            return None, error("not found")
        return membership, None

    async def get_user_memberships(self, user_id: UUID) -> tuple[list[Membership], Error]:
        stmt = select(Membership).where(Membership.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all(), None

    async def get_org_members(self, organization_id: UUID) -> tuple[list[Membership], Error]:
        stmt = select(Membership).where(Membership.organization_id == organization_id)
        result = await self.session.execute(stmt)
        return result.scalars().all(), None

    async def add_member(
        self, user_id: UUID, organization_id: UUID, role: OrgRole = OrgRole.MEMBER
    ) -> tuple[Membership | None, Error]:
        existing, err = await self.get_user_org_membership(user_id, organization_id)
        if err and str(err) != "not found":
            return None, err
        if existing is not None:
            return None, error("User is already a member of this organization")

        membership = Membership(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
        )
        return await self.create(membership)

    async def update_role(
        self, user_id: UUID, organization_id: UUID, role: OrgRole
    ) -> tuple[Membership | None, Error]:
        membership, err = await self.get_user_org_membership(user_id, organization_id)
        if err:
            return None, err
        return await self.update(membership, role=role)

    async def remove_member(self, user_id: UUID, organization_id: UUID) -> Error:
        membership, err = await self.get_user_org_membership(user_id, organization_id)
        if err:
            return err
        return await self.delete(membership)
