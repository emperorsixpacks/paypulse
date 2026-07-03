from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.paypulse.infrastructure.repositories.base import BaseRepository
from src.paypulse.models.organization import Organization
from src.paypulse.types import Error, error


class OrganizationRepository(BaseRepository[Organization]):
    _model = Organization

    async def get_by_id(self, org_id: UUID) -> tuple[Organization | None, Error]:
        return await self.get(org_id)

    async def get_by_slug(self, slug: str) -> tuple[Organization | None, Error]:
        stmt = (
            select(Organization)
            .options(selectinload(Organization.memberships))
            .where(Organization.slug == slug)
        )
        result = await self.session.execute(stmt)
        org = result.scalars().first()
        return org, None

    async def create_organization(self, org: Organization) -> tuple[Organization | None, Error]:
        existing, err = await self.get_by_slug(org.slug)
        if err and str(err) != "not found":
            return None, err
        if existing is not None:
            return None, error("Organization with this slug already exists")
        return await self.create(org)

    async def list_organizations(self, limit: int = 50, offset: int = 0) -> tuple[list[Organization], Error]:
        try:
            stmt = select(Organization).offset(offset).limit(limit)
            result = await self.session.execute(stmt)
            return result.scalars().all(), None
        except Exception as e:
            return [], error(e)

    async def update_organization(self, org_id: UUID, **kwargs) -> tuple[Organization | None, Error]:
        org, err = await self.get(org_id)
        if err:
            return None, err
        return await self.update(org, **kwargs)

    async def delete_organization(self, org_id: UUID) -> Error:
        org, err = await self.get(org_id)
        if err:
            return err
        return await self.delete(org)
