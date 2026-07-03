from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.checkout import CheckoutSession
from src.paypulse.models.enums import CheckoutStatus
from src.paypulse.repositories.base import BaseRepository


class CheckoutRepository(BaseRepository[CheckoutSession]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CheckoutSession)

    async def get_by_code(self, code: str) -> CheckoutSession | None:
        stmt = select(CheckoutSession).where(CheckoutSession.code == code)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active_by_code(self, code: str) -> CheckoutSession | None:
        stmt = select(CheckoutSession).where(
            CheckoutSession.code == code,
            CheckoutSession.status == CheckoutStatus.PENDING,
            CheckoutSession.expires_at > datetime.now(UTC),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_merchant(self, merchant_id: UUID) -> list[CheckoutSession]:
        stmt = (
            select(CheckoutSession)
            .where(CheckoutSession.merchant_id == merchant_id)
            .order_by(CheckoutSession.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_completed(self, code: str, subscription_id: UUID) -> CheckoutSession | None:
        session = await self.get_by_code(code)
        if session is None:
            return None
        session.status = CheckoutStatus.COMPLETED
        session.completed_at = datetime.now(UTC)
        session.subscription_id = subscription_id
        await self.session.flush()
        await self.session.refresh(session)
        return session

    async def mark_expired(self, code: str) -> CheckoutSession | None:
        session = await self.get_by_code(code)
        if session is None:
            return None
        session.status = CheckoutStatus.EXPIRED
        await self.session.flush()
        return session
