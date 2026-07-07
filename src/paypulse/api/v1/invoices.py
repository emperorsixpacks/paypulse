from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.merchant import Project
from src.paypulse.repositories.invoice_repository import InvoiceRepository
from src.paypulse.schemas.invoice import InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = InvoiceRepository(db)
    invoices = await repo.get_by_project(project.id)
    return [
        InvoiceResponse(
            id=i.id,
            customer_email=i.customer.email if i.customer else "Unknown",
            amount=float(i.amount),
            currency=i.currency,
            status=i.status.value,
            due_date=i.due_date,
            paid_at=i.paid_at,
            created_at=i.created_at,
        )
        for i in invoices
    ]


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

    return InvoiceResponse(
        id=invoice.id,
        customer_email=invoice.customer.email if invoice.customer else "Unknown",
        amount=float(invoice.amount),
        currency=invoice.currency,
        status=invoice.status.value,
        due_date=invoice.due_date,
        paid_at=invoice.paid_at,
        created_at=invoice.created_at,
    )
