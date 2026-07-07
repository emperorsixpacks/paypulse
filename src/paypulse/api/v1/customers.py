from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.merchant import Project
from src.paypulse.repositories.customer_repository import CustomerRepository
from src.paypulse.repositories.subscription_repository import SubscriptionRepository
from src.paypulse.repositories.invoice_repository import InvoiceRepository
from src.paypulse.schemas.customer import (
    CustomerDetailResponse,
    CustomerInvoiceResponse,
    CustomerResponse,
    CustomerSubscriptionResponse,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerResponse])
async def list_customers(
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    from src.paypulse.services.customer_service import CustomerService
    service = CustomerService(db)
    customers = await service.list(project.id)
    return customers


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    from src.paypulse.services.customer_service import CustomerService
    from src.paypulse.services.subscription_service import SubscriptionService
    from src.paypulse.services.invoice_service import InvoiceService

    customer_service = CustomerService(db)
    customer = await customer_service.get(UUID(customer_id), project.id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    sub_service = SubscriptionService(db)
    from src.paypulse.repositories.subscription_repository import SubscriptionRepository
    sub_repo = SubscriptionRepository(db)
    subscriptions = await sub_repo.get_by_customer(customer.id)

    invoice_service = InvoiceService(db)
    from src.paypulse.repositories.invoice_repository import InvoiceRepository
    invoice_repo = InvoiceRepository(db)
    invoices = await invoice_repo.get_by_customer(customer.id)

    return CustomerDetailResponse(
        customer=CustomerResponse.model_validate(customer),
        subscriptions=[
            CustomerSubscriptionResponse(
                id=s.id,
                plan_name=s.plan.name if s.plan else "Unknown",
                status=s.status.value,
                amount=float(s.plan.amount) if s.plan and s.plan.amount else 0,
                currency=s.plan.currency if s.plan else "NGN",
                interval=s.plan.interval.value if s.plan else "MONTHLY",
                current_period_start=s.current_period_start,
                current_period_end=s.current_period_end,
                cancelled_at=s.cancelled_at,
            )
            for s in subscriptions
        ],
        invoices=[
            CustomerInvoiceResponse(
                id=i.id,
                amount=float(i.amount),
                currency=i.currency,
                status=i.status.value,
                due_date=i.due_date,
                paid_at=i.paid_at,
            )
            for i in invoices
        ],
    )
