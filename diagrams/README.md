# Architecture & Flow Diagrams

This directory contains visual representations and step-by-step text walkthroughs of Paypulse's architecture, subscription lifecycle, and core transactional workflows built on top of the Nomba API.

---

## Diagrams List & Walkthroughs

### 1. [System Architecture](system_architecture.png)
Provides a high-level modular view of how the client layers, FastAPI web server, Celery worker pool, PostgreSQL/Redis databases, and Nomba API integrate.

![System Architecture](system_architecture.png)

#### **Technical Walkthrough:**
1. **Merchant Portal** registers plans and sets up client parameters via the **FastAPI Web Server** using the `POST /checkout/sessions` endpoint.
2. The **FastAPI Web Server** queries and updates state in **PostgreSQL** and publishes tasks (like webhook dispatches and card debits) to **Redis**.
3. **Celery Task Workers** poll Redis to execute recurring payments asynchronously using Nomba's APIs.
4. If a transaction succeeds or fails, Celery notifies the **Merchant Webhook** and sends receipt or failure warnings via the **Resend Email Service**.

---

### 2. [Subscription Lifecycle State Machine](subscription_lifecycle.png)
Illustrates subscription state transitions from creation (`Pending`/`AwaitingPayment`), to execution (`Active`), and through failure recovery (`Dunning` retries) to finalization (`Expired`/`Cancelled`).

![Subscription Lifecycle](subscription_lifecycle.png)

#### **State Walkthrough:**
1. **Pending**: Initiated when a checkout session URL is generated.
   - Transitions to **FailedInitial** if the customer closes the session or the payment expires.
   - Transitions to **Active** once initial checkout payment is processed and a secure card `tokenKey` is created.
2. **Active**: The primary state of a paid subscription.
   - Stays **Active** if each billing cycle charge succeeds.
   - Transitions to **Dunning** if a recurring charge attempt fails.
   - Transitions to **Cancelled** if terminated by the merchant or customer.
3. **Dunning**: Automatic recovery state.
   - Schedules three subsequent retry tasks over a 72-hour period (Retry 1 after 24h, Retry 2 after 48h, and Retry 3 after 72h).
   - Transitions back to **Active** if any retry charge succeeds.
   - Transitions to **Expired** if all three retries fail.
4. **Cancelled**: Terminal state. No further charges are attempted.

---

### 3. [Checkout & Tokenization Flow](checkout_flow.png)
Sequence diagram outlining the initial checkout initialization, redirection to Nomba, token generation, webhook collection, and subscription activation.

![Checkout & Tokenization Flow](checkout_flow.png)

#### **Execution Sequence Walkthrough:**
1. The merchant backend requests a checkout session from Paypulse (`POST /checkout/sessions`).
2. Paypulse authenticates with Nomba (`POST /v1/auth/token/issue` if the token has expired) and requests a tokenized checkout order (`POST /v1/checkout/order` with `tokenizeCard=true`).
3. Nomba returns a unique transaction `orderReference` and a checkout redirect URL (`checkoutLink`).
4. The merchant redirects the customer to Nomba's payment gateway page.
5. Once the customer pays and passes OTP/PIN check, Nomba notifies Paypulse via a POST Webhook, providing the payment status and the card's `tokenKey`.
6. Paypulse saves the `tokenKey` in PostgreSQL, marks the subscription as **Active**, and fires a `subscription.activated` webhook to the merchant backend.

---

### 4. [Recurring Billing & Dunning Cycle](recurring_billing_flow.png)
Sequence diagram illustrating background worker tasks scanning due bills, charging saved tokens, handling success actions, and triggering retry intervals on failures.

![Recurring Billing Flow](recurring_billing_flow.png)

#### **Execution Sequence Walkthrough:**
1. A Celery cron worker scans PostgreSQL for subscriptions whose `next_billing_date` is less than or equal to the current time.
2. For each due subscription, the worker refreshes the Nomba auth token if expired (`POST /v1/auth/token/refresh`) and charges the card using the saved token (`POST /v1/checkout/tokenized-card-payment`).
3. **On Success**:
   - Updates `next_billing_date` in PostgreSQL and marks the invoice as **Paid**.
   - Sends a confirmation email to the user via Resend and fires an `invoice.paid` webhook to the merchant backend.
4. **On Failure** (e.g. Card expired or Insufficient funds):
   - Paypulse sets the subscription state to **Dunning** and increments `retry_count`.
   - Sends a failed-payment email to the customer with a link to update their payment method.
   - Fires a `payment.failed` webhook to the merchant backend.
   - Schedules the next payment retry task 24 hours later.
