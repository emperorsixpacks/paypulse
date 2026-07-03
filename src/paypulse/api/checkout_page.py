from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db
from src.paypulse.core.settings import settings
from src.paypulse.models.enums import CheckoutStatus
from src.paypulse.repositories.checkout_repository import CheckoutRepository
from src.paypulse.repositories.merchant_repository import MerchantRepository
from src.paypulse.repositories.plan_repository import PlanRepository

router = APIRouter(tags=["checkout-page"])


@router.get("/{code}", response_class=HTMLResponse)
async def checkout_page(code: str, db: AsyncSession = Depends(get_db)):
    repo = CheckoutRepository(db)
    session = await repo.get_by_code(code)

    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkout not found")

    if session.status == CheckoutStatus.EXPIRED:
        return HTMLResponse("<h1>This checkout link has expired.</h1>", status_code=410)

    if session.status == CheckoutStatus.COMPLETED:
        return HTMLResponse("<h1>This checkout has already been paid.</h1>")

    if session.status == CheckoutStatus.CANCELLED:
        return RedirectResponse(url=session.cancel_url)

    if session.expires_at <= datetime.now(UTC):
        await repo.mark_expired(code)
        return HTMLResponse("<h1>This checkout link has expired.</h1>", status_code=410)

    plan_repo = PlanRepository(db)
    plan, _ = await plan_repo.get(session.plan_id)

    merchant_repo = MerchantRepository(db)
    # We need the business name — fetch merchant via plan's merchant_id
    # For simplicity, we'll store it or fetch via a join later
    # For now, just render with plan info

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paypulse Checkout</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
        .card {{ background: white; border-radius: 12px; padding: 32px; max-width: 420px; width: 100%; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        h1 {{ font-size: 20px; margin-bottom: 4px; }}
        .plan-info {{ color: #666; margin-bottom: 24px; font-size: 14px; }}
        .amount {{ font-size: 28px; font-weight: 700; margin-bottom: 24px; }}
        .amount span {{ font-size: 14px; font-weight: 400; color: #666; }}
        label {{ display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; color: #333; }}
        input {{ width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; margin-bottom: 16px; }}
        input:focus {{ outline: none; border-color: #6366f1; }}
        button {{ width: 100%; padding: 12px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; }}
        button:hover {{ background: #4f46e5; }}
        .footer {{ text-align: center; margin-top: 16px; font-size: 12px; color: #999; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>{plan.name if plan else "Subscription"}</h1>
        <p class="plan-info">Billing every {plan.interval.value.lower() if plan else "month"}</p>
        <div class="amount">&#8358;{plan.amount:,.2f} <span>/{plan.interval.value.lower() if plan else "month"}</span></div>
        <form method="POST" action="/checkout/{code}/pay">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" value="{session.customer_name or ''}" placeholder="Your name" />

            <label for="email">Email</label>
            <input type="email" id="email" name="email" value="{session.customer_email or ''}" placeholder="you@example.com" required />

            <label for="card_number">Card Number</label>
            <input type="text" id="card_number" name="card_number" placeholder="1234 5678 9012 3456" required />

            <div style="display:flex;gap:12px">
                <div style="flex:1">
                    <label for="expiry">Expiry</label>
                    <input type="text" id="expiry" name="expiry" placeholder="MM/YY" required />
                </div>
                <div style="flex:1">
                    <label for="cvv">CVV</label>
                    <input type="text" id="cvv" name="cvv" placeholder="123" required />
                </div>
            </div>

            <button type="submit">Subscribe</button>
        </form>
        <p class="footer">Powered by Paypulse</p>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html)


@router.post("/{code}/pay")
async def checkout_pay(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    repo = CheckoutRepository(db)
    session = await repo.get_active_by_code(code)

    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkout not found or expired")

    form = await request.form()
    customer_email = form.get("email", session.customer_email)
    customer_name = form.get("name", session.customer_name)

    # TODO: Call Nomba to tokenize card and charge
    # For now, simulate success

    from src.paypulse.models.customer import Customer
    from src.paypulse.models.enums import InvoiceStatus, SubscriptionStatus, BillingAttemptStatus
    from src.paypulse.models.invoice import Invoice
    from src.paypulse.models.subscription import Subscription
    from src.paypulse.models.billing_attempt import BillingAttempt
    from src.paypulse.repositories.customer_repository import CustomerRepository
    from src.paypulse.repositories.subscription_repository import SubscriptionRepository
    from src.paypulse.repositories.invoice_repository import InvoiceRepository
    from src.paypulse.repositories.billing_attempt_repository import BillingAttemptRepository
    from src.paypulse.repositories.plan_repository import PlanRepository
    from datetime import timedelta

    # Get plan
    plan_repo = PlanRepository(db)
    plan, _ = await plan_repo.get(session.plan_id)

    # Create or get customer
    cust_repo = CustomerRepository(db)
    customer = await cust_repo.get_by_email(session.merchant_id, customer_email)
    if customer is None:
        customer = await cust_repo.create({
            "merchant_id": session.merchant_id,
            "email": customer_email,
            "name": customer_name,
        })

    # Create subscription
    sub_repo = SubscriptionRepository(db)
    now = datetime.now(UTC)
    subscription = await sub_repo.create({
        "merchant_id": session.merchant_id,
        "customer_id": customer.id,
        "plan_id": session.plan_id,
        "status": SubscriptionStatus.ACTIVE,
        "current_period_start": now,
        "current_period_end": now + timedelta(days=30),
    })

    # Create invoice
    inv_repo = InvoiceRepository(db)
    invoice = await inv_repo.create({
        "subscription_id": subscription.id,
        "customer_id": customer.id,
        "merchant_id": session.merchant_id,
        "amount": plan.amount,
        "currency": plan.currency,
        "status": InvoiceStatus.PAID,
        "due_date": now,
        "paid_at": now,
    })

    # Create billing attempt
    ba_repo = BillingAttemptRepository(db)
    await ba_repo.create({
        "invoice_id": invoice.id,
        "status": BillingAttemptStatus.SUCCESS,
        "attempt_number": 1,
        "attempted_at": now,
    })

    # Mark session completed
    await repo.mark_completed(code, subscription.id)

    return RedirectResponse(url=session.success_url, status_code=status.HTTP_303_SEE_OTHER)
