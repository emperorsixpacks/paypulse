import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.enums import BillingType, InvoiceStatus
from src.paypulse.repositories.usage_repository import UsageRepository
from src.paypulse.services.invoice_service import InvoiceService
from src.paypulse.services.subscription_service import SubscriptionService
from src.paypulse.services.dunning_service import DunningService
from src.paypulse.services.webhook_service import WebhookService


@dataclass
class BillingResult:
    success: bool = False
    skipped: bool = False
    reason: str | None = None
    invoice=None


class BillingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.usage_repo = UsageRepository(db)
        self.invoice_service = InvoiceService(db)
        self.subscription_service = SubscriptionService(db)
        self.dunning_service = DunningService(db)
        self.webhook_service = WebhookService(db)

    async def charge_subscription(self, subscription) -> BillingResult:
        plan = subscription.plan
        customer = subscription.customer

        if plan.billing_type == BillingType.FIXED:
            amount = float(plan.amount)
        elif plan.billing_type == BillingType.METERED:
            total_quantity = await self.usage_repo.sum_unbilled(subscription.id)
            if total_quantity == Decimal("0"):
                await self.subscription_service.extend_period(subscription)
                return BillingResult(skipped=True, reason="no_usage")
            amount = float(total_quantity * Decimal(str(plan.price_per_unit)))
        else:
            return BillingResult(skipped=True, reason="unknown_billing_type")

        # TODO: Replace with real Nomba tokenized card charge
        # nomba_response = await nomba_client.charge_tokenized(...)
        # For now simulate success
        nomba_ref = f"nomba_{secrets.token_urlsafe(16)}"
        charge_success = True

        if charge_success:
            invoice = await self.invoice_service.create(
                project_id=subscription.project_id,
                subscription_id=subscription.id,
                customer_id=customer.id,
                amount=amount,
                currency=plan.currency,
                status=InvoiceStatus.PAID,
                nomba_ref=nomba_ref,
            )

            if plan.billing_type == BillingType.METERED:
                await self.usage_repo.mark_billed(
                    subscription_id=subscription.id,
                    invoice_id=invoice.id,
                    billed_at=datetime.now(UTC),
                )

            await self.subscription_service.extend_period(subscription)

            await self.webhook_service.queue_delivery(
                project_id=subscription.project_id,
                event_type="invoice.paid",
                payload={"invoice_id": str(invoice.id), "amount": amount, "currency": plan.currency},
            )

            return BillingResult(success=True, invoice=invoice)
        else:
            await self.dunning_service.schedule_retry(subscription, amount)
            await self.webhook_service.queue_delivery(
                project_id=subscription.project_id,
                event_type="payment.failed",
                payload={"subscription_id": str(subscription.id), "amount": amount},
            )
            return BillingResult(success=False)
