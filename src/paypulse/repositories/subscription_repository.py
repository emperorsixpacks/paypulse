from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.paypulse.models.enums import SubscriptionStatus
from src.paypulse.models.billing import Subscription
from src.paypulse.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Subscription)

    async def get_due_subscriptions(self, as_of: datetime) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_end <= as_of,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_customer(self, customer_id: UUID) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(Subscription.customer_id == customer_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_project(self, project_id: UUID) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(Subscription.project_id == project_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, project_id: UUID, status: SubscriptionStatus) -> list[Subscription]:
        stmt = select(Subscription).where(
            Subscription.project_id == project_id,
            Subscription.status == status,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
