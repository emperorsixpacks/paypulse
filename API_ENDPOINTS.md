# PayPulse API — Complete Endpoint Reference

Base URL: `https://api.paypulse.app/api/v1`

---

## Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/register` | None | Register a new merchant account. Returns JWT + initial API keys. |
| `POST` | `/auth/login` | None | Login with email/password. Returns JWT access token. |
| `GET` | `/auth/me` | JWT | Get current merchant profile. |

---

## Merchants & Projects

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/merchants/me` | JWT | Get merchant profile. |
| `GET` | `/merchants/projects` | JWT | List all projects for the merchant. |
| `POST` | `/merchants/projects` | JWT | Create a new project. Body: `{ "name": "string" }` |
| `GET` | `/merchants/api-keys` | JWT | List all API keys. |
| `POST` | `/merchants/api-keys` | JWT | Generate a new API key. Body: `{ "name": "string", "is_live": false }` |
| `DELETE` | `/merchants/api-keys/{key_id}` | JWT | Revoke an API key. |

---

## Plans

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/plans` | API Key | List all plans for the project. |
| `POST` | `/plans` | API Key | Create a plan. |
| `GET` | `/plans/{plan_id}` | API Key | Get a plan by ID. |
| `PATCH` | `/plans/{plan_id}` | API Key | Update a plan. |
| `DELETE` | `/plans/{plan_id}` | API Key | Deactivate a plan (soft delete). |

### Plan schema

```json
{
  "name": "Growth",
  "amount": 25000,
  "currency": "NGN",
  "interval": "MONTHLY",
  "interval_count": 1,
  "trial_period_days": 0
}
```

`interval` values: `DAILY`, `WEEKLY`, `MONTHLY`, `YEARLY`

---

## Customers

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/customers` | API Key | List all customers for the project. |
| `GET` | `/customers/{customer_id}` | API Key | Get customer detail with subscriptions + invoices. |

---

## Subscriptions

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/subscriptions` | API Key | List subscriptions. Query: `?status_filter=ACTIVE` |
| `GET` | `/subscriptions/{subscription_id}` | API Key | Get subscription detail. |
| `POST` | `/subscriptions/{subscription_id}/cancel` | API Key | Cancel a subscription. |
| `POST` | `/subscriptions/{subscription_id}/usage` | API Key | Report usage (metered plans). |
| `GET` | `/subscriptions/{subscription_id}/usage` | API Key | Get current period usage. |
| `GET` | `/subscriptions/{subscription_id}/usage/history` | API Key | Get usage history. Query: `?from_dt=&to_dt=` |

### Subscription statuses

`ACTIVE`, `PAST_DUE`, `CANCELLED`, `PAUSED`, `TRIALING`, `EXPIRED`

### Cancel request

```json
{
  "cancel_at_period_end": false
}
```

### Usage report request

```json
{
  "quantity": 1500,
  "description": "API calls for Jan 15",
  "idempotency_key": "usage_2026_01_15_api_calls",
  "timestamp": "2026-01-15T14:00:00Z"
}
```

---

## Invoices

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/invoices` | API Key | List all invoices for the project. |
| `GET` | `/invoices/{invoice_id}` | API Key | Get invoice detail. |

### Invoice statuses

`PENDING`, `PAID`, `FAILED`, `VOID`

### Refund statuses

`NONE`, `PENDING`, `PROCESSED`, `FAILED`

---

## Checkout

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/checkout/sessions` | API Key | Create a checkout session. |
| `GET` | `/checkout/sessions` | API Key | List all checkout sessions. |
| `GET` | `/checkout/sessions/{code}` | API Key | Get a checkout session by code. |
| `DELETE` | `/checkout/sessions/{code}` | API Key | Cancel a checkout session. |

### Create session request

```json
{
  "plan_id": "uuid",
  "customer_email": "ade@techcorp.ng",
  "customer_name": "Ade Okonkwo",
  "success_url": "https://yourapp.com/success",
  "cancel_url": "https://yourapp.com/cancel",
  "metadata": { "user_id": "123" }
}
```

### Checkout statuses

`PENDING`, `COMPLETED`, `EXPIRED`, `CANCELLED`

---

## Webhooks

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/webhooks` | API Key + JWT | List webhook endpoints. |
| `POST` | `/webhooks` | API Key + JWT | Register a webhook endpoint. |
| `DELETE` | `/webhooks/{webhook_id}` | API Key + JWT | Delete a webhook endpoint. |

### Create webhook request

```json
{
  "url": "https://yourapp.com/webhooks/paypulse",
  "events": ["invoice.paid", "subscription.cancelled"]
}
```

### Event types

`invoice.paid`, `invoice.failed`, `invoice.created`, `subscription.created`, `subscription.active`, `subscription.cancelled`, `subscription.past_due`, `subscription.expired`, `checkout.completed`, `checkout.expired`

---

## Cancellation Policies

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/cancellation-policies` | API Key + JWT | List policies for the project. |
| `POST` | `/cancellation-policies` | API Key + JWT | Create a cancellation policy. |
| `GET` | `/cancellation-policies/{policy_id}` | API Key + JWT | Get a policy by ID. |
| `PATCH` | `/cancellation-policies/{policy_id}` | API Key + JWT | Update a policy. |
| `DELETE` | `/cancellation-policies/{policy_id}` | API Key + JWT | Delete a policy. |

### Create policy request

```json
{
  "name": "Standard Refund",
  "refund_type": "prorate",
  "refund_percentage": null,
  "refund_window_days": 0,
  "prorate_refund": true,
  "cancellation_fee": 0,
  "apply_to_existing": true,
  "is_default": true
}
```

### Refund types

`none`, `full`, `percentage`, `prorate`

---

## Public (No Auth)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/checkout/{code}/session` | Get public checkout session data. |
| `POST` | `/checkout/{code}/pay` | Process a payment (called by Nomba webhook). |
| `GET` | `/checkout/health` | Health check. |
| `GET` | `/health` | API health check. |

---

## Auth Summary

| Auth Type | Header | Used By |
|-----------|--------|---------|
| API Key | `X-Api-Key: pp_test_xxxx` | Plans, Customers, Subscriptions, Invoices, Checkout |
| JWT | `Authorization: Bearer eyJ...` | Merchants, Auth, API Keys |
| Both | `X-Api-Key` + `Authorization` | Webhooks, Cancellation Policies |
| None | — | Register, Login, Public checkout, Health |
