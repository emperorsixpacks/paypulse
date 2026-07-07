from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.billing import UsageRecord
from src.paypulse.repositories.base import BaseRepository


class UsageRepository(BaseRepository[UsageRecord]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UsageRecord)

    async def create_with_idempotency(
        self,
        project_id: UUID,
        subscription_id: UUID,
        quantity: Decimal,
        description: str | None,
        idempotency_key: str,
        timestamp: datetime,
    ) -> tuple[UsageRecord, bool]:
        stmt = select(UsageRecord).where(
            UsageRecord.idempotency_key == idempotency_key,
            UsageRecord.project_id == project_id,
        )
        result = await self.session.execute(stmt)
        existing = result.scalars().first()
        if existing:
            return existing, False

        record = UsageRecord(
            project_id=project_id,
            subscription_id=subscription_id,
            quantity=float(quantity),
            description=description,
            idempotency_key=idempotency_key,
            timestamp=timestamp,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record, True

    async def get_unbilled(self, subscription_id: UUID) -> list[UsageRecord]:
        stmt = (
            select(UsageRecord)
            .where(UsageRecord.subscription_id == subscription_id, UsageRecord.billed == False)
            .order_by(UsageRecord.timestamp.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def sum_unbilled(self, subscription_id: UUID) -> Decimal:
        stmt = select(func.coalesce(func.sum(UsageRecord.quantity), 0)).where(
            UsageRecord.subscription_id == subscription_id,
            UsageRecord.billed == False,
        )
        result = await self.session.execute(stmt)
        return Decimal(str(result.scalar()))

    async def mark_billed(
        self,
        subscription_id: UUID,
        invoice_id: UUID,
        billed_at: datetime,
    ) -> int:
        stmt = (
            update(UsageRecord)
            .where(UsageRecord.subscription_id == subscription_id, UsageRecord.billed == False)
            .values(billed=True, invoice_id=invoice_id, billed_at=billed_at)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def get_by_subscription(
        self,
        subscription_id: UUID,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
    ) -> list[UsageRecord]:
        conditions = [UsageRecord.subscription_id == subscription_id]
        if from_dt:
            conditions.append(UsageRecord.timestamp >= from_dt)
        if to_dt:
            conditions.append(UsageRecord.timestamp <= to_dt)
        stmt = (
            select(UsageRecord)
            .where(*conditions)
            .order_by(UsageRecord.timestamp.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
