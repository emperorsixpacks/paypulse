from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.cancellation import CancellationPolicy
from src.paypulse.repositories.base import BaseRepository


class CancellationPolicyRepository(BaseRepository[CancellationPolicy]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CancellationPolicy)

    async def get_by_project(self, project_id: UUID) -> list[CancellationPolicy]:
        stmt = select(CancellationPolicy).where(CancellationPolicy.project_id == project_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_default(self, project_id: UUID) -> CancellationPolicy | None:
        stmt = select(CancellationPolicy).where(
            CancellationPolicy.project_id == project_id,
            CancellationPolicy.is_default == True,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
