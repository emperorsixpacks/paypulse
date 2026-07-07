from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.checkout import CheckoutSession
from src.paypulse.models.enums import CheckoutStatus, InvoiceStatus
from src.paypulse.repositories.checkout_repository import CheckoutRepository
from src.paypulse.services.customer_service import CustomerService
from src.paypulse.services.subscription_service import SubscriptionService
from src.paypulse.services.invoice_service import InvoiceService
from src.paypulse.services.webhook_service import WebhookService


class NombaWebhookService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.checkout_repo = CheckoutRepository(db)
        self.customer_service = CustomerService(db)
        self.subscription_service = SubscriptionService(db)
        self.invoice_service = InvoiceService(db)
        self.webhook_service = WebhookService(db)

    async def handle_payment_webhook(self, payload: dict, signature: str | None = None) -> bool:
        # TODO: Verify Nomba webhook signature
        order_reference = payload.get("orderReference")
        status = payload.get("status")
        token_key = payload.get("tokenKey")
        customer_email = payload.get("customerEmail")
        customer_name = payload.get("customerName")

        if not order_reference:
            return False

        session = await self.checkout_repo.get_by_code(order_reference)
        if session is None:
            # Try by nomba_order_reference
            from sqlalchemy import select
            stmt = select(CheckoutSession).where(CheckoutSession.nomba_order_reference == order_reference)
            result = await self.db.execute(stmt)
            session = result.scalars().first()

        if session is None or session.status == CheckoutStatus.COMPLETED:
            return True  # Idempotent

        if status != "SUCCESS":
            session.status = CheckoutStatus.EXPIRED
            await self.db.flush()
            return False

        plan = session.plan if hasattr(session, 'plan') else None
        if plan is None:
            from src.paypulse.repositories.plan_repository import PlanRepository
            plan_repo = PlanRepository(self.db)
            plan = await plan_repo.get(session.plan_id)

        customer = await self.customer_service.get_or_create(
            project_id=session.project_id,
            email=customer_email or session.customer_email,
            name=customer_name or session.customer_name,
            nomba_token_key=token_key,
        )

        subscription = await self.subscription_service.create(customer, plan, session)

        await self.invoice_service.create(
            project_id=session.project_id,
            subscription_id=subscription.id,
            customer_id=customer.id,
            amount=float(plan.amount) if plan.amount else 0,
            currency=plan.currency,
            status=InvoiceStatus.PAID,
        )

        session.status = CheckoutStatus.COMPLETED
        await self.db.flush()

        await self.webhook_service.queue_delivery(
            project_id=session.project_id,
            event_type="subscription.created",
            payload={"subscription_id": str(subscription.id), "customer_email": customer.email},
        )

        return True
