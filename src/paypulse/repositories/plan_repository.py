from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.plan import Plan
from src.paypulse.repositories.base import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Plan)

    async def get_active_plans(self, merchant_id: UUID) -> list[Plan]:
        stmt = select(Plan).where(
            Plan.merchant_id == merchant_id,
            Plan.is_active == True,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_merchant(self, merchant_id: UUID) -> list[Plan]:
        stmt = select(Plan).where(Plan.merchant_id == merchant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
