from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = CustomerRepository(db)

    async def get_or_create(
        self,
        project_id: UUID,
        email: str,
        name: str | None = None,
        nomba_token_key: str | None = None,
    ):
        existing = await self.repo.get_by_email(project_id, email)
        if existing:
            if nomba_token_key:
                existing.nomba_token_key = nomba_token_key
                await self.db.flush()
            return existing
        return await self.repo.create({
            "project_id": project_id,
            "email": email,
            "name": name,
            "nomba_token_key": nomba_token_key,
        })

    async def get(self, customer_id: UUID, project_id: UUID):
        customer = await self.repo.get(customer_id)
        if customer is None or customer.project_id != project_id:
            return None
        return customer

    async def list(self, project_id: UUID):
        return await self.repo.get_by_project(project_id)
