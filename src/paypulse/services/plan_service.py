from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.enums import BillingType
from src.paypulse.repositories.plan_repository import PlanRepository


class PlanService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = PlanRepository(db)

    async def create(self, project_id: UUID, data: dict):
        billing_type = data.get("billing_type", BillingType.FIXED)
        if billing_type == BillingType.FIXED and not data.get("amount"):
            raise ValueError("amount is required for FIXED plans")
        if billing_type == BillingType.METERED and not data.get("price_per_unit"):
            raise ValueError("price_per_unit is required for METERED plans")
        return await self.repo.create({**data, "project_id": project_id})

    async def get(self, plan_id: UUID, project_id: UUID):
        plan = await self.repo.get(plan_id)
        if plan is None or plan.project_id != project_id:
            return None
        return plan

    async def list(self, project_id: UUID):
        return await self.repo.get_by_project(project_id)

    async def update(self, plan_id: UUID, project_id: UUID, data: dict):
        plan = await self.get(plan_id, project_id)
        if plan is None:
            return None
        # amount, price_per_unit, interval, billing_type are immutable
        forbidden = {"amount", "price_per_unit", "interval", "interval_count", "billing_type"}
        filtered = {k: v for k, v in data.items() if k not in forbidden}
        if not filtered:
            return plan
        return await self.repo.update(plan.id, filtered)

    async def deactivate(self, plan_id: UUID, project_id: UUID) -> bool:
        plan = await self.get(plan_id, project_id)
        if plan is None:
            return False
        await self.repo.update(plan.id, {"is_active": False})
        return True
