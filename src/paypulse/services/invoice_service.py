from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.enums import InvoiceStatus
from src.paypulse.repositories.invoice_repository import InvoiceRepository


class InvoiceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = InvoiceRepository(db)

    async def create(
        self,
        project_id: UUID,
        subscription_id: UUID,
        customer_id: UUID,
        amount: float,
        currency: str,
        status: InvoiceStatus,
        nomba_ref: str | None = None,
    ):
        return await self.repo.create({
            "project_id": project_id,
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "amount": amount,
            "currency": currency,
            "status": status,
            "due_date": datetime.now(UTC),
            "paid_at": datetime.now(UTC) if status == InvoiceStatus.PAID else None,
            "nomba_transaction_ref": nomba_ref,
        })

    async def get(self, invoice_id: UUID, project_id: UUID):
        invoice = await self.repo.get(invoice_id)
        if invoice is None or invoice.project_id != project_id:
            return None
        return invoice

    async def list(self, project_id: UUID, status: InvoiceStatus | None = None):
        if status:
            from sqlalchemy import select
            from src.paypulse.models.billing import Invoice
            stmt = select(Invoice).where(
                Invoice.project_id == project_id,
                Invoice.status == status,
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        return await self.repo.get_by_project(project_id)

    async def mark_paid(self, invoice_id: UUID, nomba_ref: str | None = None):
        invoice = await self.repo.get(invoice_id)
        if invoice:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_at = datetime.now(UTC)
            if nomba_ref:
                invoice.nomba_transaction_ref = nomba_ref
            await self.db.flush()
        return invoice

    async def mark_failed(self, invoice_id: UUID):
        invoice = await self.repo.get(invoice_id)
        if invoice:
            invoice.status = InvoiceStatus.FAILED
            await self.db.flush()
        return invoice
