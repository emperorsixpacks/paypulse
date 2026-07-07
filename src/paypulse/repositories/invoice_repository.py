from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.enums import InvoiceStatus
from src.paypulse.models.billing import Invoice
from src.paypulse.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Invoice)

    async def get_by_customer(self, customer_id: UUID) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.customer_id == customer_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_subscription(self, subscription_id: UUID) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.subscription_id == subscription_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_project(self, project_id: UUID) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.project_id == project_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending(self, project_id: UUID) -> list[Invoice]:
        stmt = select(Invoice).where(
            Invoice.project_id == project_id,
            Invoice.status == InvoiceStatus.PENDING,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
