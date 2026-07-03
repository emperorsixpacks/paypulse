from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.billing_attempt import BillingAttempt
from src.paypulse.repositories.base import BaseRepository


class BillingAttemptRepository(BaseRepository[BillingAttempt]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, BillingAttempt)

    async def get_by_invoice(self, invoice_id: UUID) -> list[BillingAttempt]:
        stmt = select(BillingAttempt).where(BillingAttempt.invoice_id == invoice_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_due_retries(self, as_of: datetime) -> list[BillingAttempt]:
        stmt = select(BillingAttempt).where(
            BillingAttempt.next_retry_at <= as_of,
            BillingAttempt.next_retry_at.isnot(None),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_attempt_count(self, invoice_id: UUID) -> int:
        stmt = select(func.count()).where(BillingAttempt.invoice_id == invoice_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
