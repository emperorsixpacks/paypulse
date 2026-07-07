from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.paypulse.core.security import generate_api_key, verify_password
from src.paypulse.models.merchant import ApiKey, Merchant, Project
from src.paypulse.repositories.base import BaseRepository


class MerchantRepository(BaseRepository[Merchant]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Merchant)

    async def get_by_email(self, email: str) -> Merchant | None:
        stmt = select(Merchant).where(Merchant.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Project)

    async def get_by_merchant(self, merchant_id: UUID) -> list[Project]:
        stmt = select(Project).where(Project.merchant_id == merchant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_api_key(self, project_id: UUID) -> Project | None:
        stmt = (
            select(Project)
            .options(selectinload(Project.api_key))
            .where(Project.id == project_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()


class ApiKeyRepository(BaseRepository[ApiKey]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ApiKey)

    async def create_for_project(self, project_id: UUID, name: str, is_live: bool) -> tuple[ApiKey, str]:
        full_key, hashed_key = generate_api_key(is_live)
        prefix = full_key[:8]
        api_key = ApiKey(
            project_id=project_id,
            name=name,
            key_prefix=prefix,
            hashed_key=hashed_key,
        )
        self.session.add(api_key)
        await self.session.flush()
        await self.session.refresh(api_key)
        return api_key, full_key

    async def get_by_prefix(self, key_prefix: str) -> ApiKey | None:
        stmt = (
            select(ApiKey)
            .options(selectinload(ApiKey.project).selectinload(Project.merchant))
            .where(ApiKey.key_prefix == key_prefix, ApiKey.is_active == True)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def verify_key(self, plain_key: str) -> Project | None:
        prefix = plain_key[:8]
        api_key = await self.get_by_prefix(prefix)
        if api_key is None:
            return None
        if not verify_password(plain_key, api_key.hashed_key):
            return None
        return api_key.project

    async def revoke(self, key_id: UUID) -> bool:
        stmt = select(ApiKey).where(ApiKey.id == key_id)
        result = await self.session.execute(stmt)
        api_key = result.scalars().first()
        if api_key is None:
            return False
        api_key.is_active = False
        await self.session.flush()
        return True
