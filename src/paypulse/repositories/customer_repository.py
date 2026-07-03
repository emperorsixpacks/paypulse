from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.customer import Customer
from src.paypulse.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    async def get_by_email(self, merchant_id: UUID, email: str) -> Customer | None:
        stmt = select(Customer).where(
            Customer.merchant_id == merchant_id,
            Customer.email == email,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_merchant(self, merchant_id: UUID) -> list[Customer]:
        stmt = select(Customer).where(Customer.merchant_id == merchant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
