from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.merchant import Project
from src.paypulse.repositories.invoice_repository import InvoiceRepository
from src.paypulse.schemas.invoice import InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["invoices"])


def _invoice_to_response(i) -> InvoiceResponse:
    return InvoiceResponse(
        id=i.id,
        customer_email=i.customer.email if i.customer else "Unknown",
        amount=float(i.amount),
        currency=i.currency,
        status=i.status.value,
        due_date=i.due_date,
        paid_at=i.paid_at,
        refund_amount=float(i.refund_amount) if i.refund_amount else 0,
        refund_status=i.refund_status.value if hasattr(i.refund_status, "value") else i.refund_status,
        refund_reason=i.refund_reason,
        created_at=i.created_at,
    )


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = InvoiceRepository(db)
    invoices = await repo.get_by_project(project.id)
    return [_invoice_to_response(i) for i in invoices]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    from src.paypulse.models.billing import Invoice

    repo = InvoiceRepository(db)
    invoice = await repo.get(UUID(invoice_id))
    if invoice is None or invoice.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    return _invoice_to_response(invoice)
