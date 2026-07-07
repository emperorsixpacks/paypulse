import secrets
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.settings import settings
from src.paypulse.models.checkout import CheckoutSession
from src.paypulse.repositories.checkout_repository import CheckoutRepository
from src.paypulse.repositories.plan_repository import PlanRepository


class CheckoutService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = CheckoutRepository(db)
        self.plan_repo = PlanRepository(db)

    async def create_session(
        self,
        project_id: UUID,
        plan_id: UUID,
        customer_email: str | None = None,
        customer_name: str | None = None,
        success_url: str = "",
        cancel_url: str = "",
        metadata: dict | None = None,
    ):
        plan = await self.plan_repo.get(plan_id)
        if plan is None or plan.project_id != project_id or not plan.is_active:
            return None

        code = CheckoutSession.generate_code()

        # TODO: Call Nomba POST /v1/checkout/orders
        nomba_order_ref = f"ord_{secrets.token_urlsafe(16)}"
        nomba_checkout_link = f"{settings.CHECKOUT_BASE_URL}/{code}"

        session = await self.repo.create({
            "project_id": project_id,
            "plan_id": plan_id,
            "code": code,
            "customer_email": customer_email,
            "customer_name": customer_name,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "nomba_order_reference": nomba_order_ref,
            "nomba_checkout_link": nomba_checkout_link,
            "expires_at": CheckoutSession.default_expiry(),
            "extra_data": metadata,
        })

        return {
            "session": session,
            "checkout_url": nomba_checkout_link,
        }

    async def get_by_code(self, code: str, project_id: UUID):
        session = await self.repo.get_by_code(code)
        if session is None or session.project_id != project_id:
            return None
        return session

    async def get_active_by_code(self, code: str):
        return await self.repo.get_active_by_code(code)

    async def list(self, project_id: UUID):
        return await self.repo.get_by_project(project_id)

    async def cancel(self, code: str, project_id: UUID):
        from src.paypulse.models.enums import CheckoutStatus
        session = await self.get_by_code(code, project_id)
        if session is None or session.status != CheckoutStatus.PENDING:
            return None
        session.status = CheckoutStatus.CANCELLED
        await self.db.flush()
        return session

    async def get_public_session_data(self, code: str):
        session = await self.repo.get_active_by_code(code)
        if session is None:
            return None
        plan = await self.plan_repo.get(session.plan_id)
        if plan is None:
            return None
        return {
            "code": session.code,
            "plan_name": plan.name,
            "amount": float(plan.amount) if plan.amount else float(plan.price_per_unit or 0),
            "currency": plan.currency,
            "interval": plan.interval.value,
            "customer_email": session.customer_email,
            "customer_name": session.customer_name,
            "success_url": session.success_url,
            "cancel_url": session.cancel_url,
            "expires_at": session.expires_at.isoformat(),
        }
