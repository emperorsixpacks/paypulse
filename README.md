# Paypulse

Paypulse is a developer-first subscription and recurring billing engine built on top of **Nomba's** payment infrastructure. It automates plan creation, billing cycle execution, card tokenization workflows, smart retries, and dunning cycles for digital products and SaaS platforms.

---

## Design Philosophy & Architecture Decisions

Paypulse is architected to solve the primary challenges of recurring payments in the local market: payment failures, card expirations, and manual charge retry logic. The system is designed based on several core principles:

### 1. Asynchronous Decoupling & Queueing
All database polling, email delivery, webhook notifications, and payment processing requests to Nomba's API are offloaded to background task workers. FastAPI handles incoming requests synchronously and responds instantly, while **Celery** and **Redis** handle heavy or time-delayed execution (such as transaction requeries and charge retries).

### 2. Subscription State Transition Lifecycle
Subscriptions move through a flat, deterministic state machine. This design prevents database race conditions, simplifies merchant system integration, and ensures maximum compatibility with API serialization and graphing engines:
- **Pending**: Customer has initiated checkout but initial payment is not yet verified.
- **Active**: Customer card is tokenized, and the subscription is active.
- **Dunning**: Payment failed. The system schedules automatic retry sweeps (24h, 48h, and 72h intervals) before marking the subscription as expired.
- **Expired/Cancelled**: Subscriptions that have failed all retry periods or have been explicitly terminated.

### 3. Separation of Concerns
The database schemas for customers, plans, invoices, and card tokens are managed in a robust PostgreSQL storage layer, ensuring audit trails are kept for every billing attempt. Paypulse uses Nomba's payment APIs exclusively for checkout ordering and tokenized card charging, delegating secure card data management to the gateway.

---

## Tech Stack

- **Backend Framework**: FastAPI (Python >= 3.13)
- **Task Runner**: Celery (integrated with Redis for event queues and lock states)
- **Database**: PostgreSQL (SQLAlchemy + Asyncpg for asynchronous operations, Alembic for migrations)
- **Package & Environment Manager**: `uv` (modern Python package resolver)
- **Testing**: Pytest

---

## Directory Structure

```text
paypulse/
├── config/                  # Configuration files
├── diagrams/                # Architectural flow charts and lifecycle diagrams
├── src/
│   └── paypulse/
│       ├── api/             # Web API routes and controllers
│       ├── core/            # App setup, settings, utilities, security
│       ├── infrastructure/
│       │   └── nomba/       # Nomba SDK integration (client, dtos, config)
│       └── models/          # Database models (Subscriptions, Customers, Plans)
├── tests/                   # Pytest test suites
├── pyproject.toml           # Project metadata and dependencies
└── uv.lock                  # UV lockfile
```

---

## Getting Started

### 1. Requirements

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv) package manager
- Redis
- PostgreSQL

### 2. Installation

Clone the repository and install dependencies using `uv`:

```bash
uv pip install -e .
```

### 3. Environment Configuration

Create a `.env` file inside `config/` (or set them directly in your environment):

```ini
ENVIRONMENT=dev
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=paypulse
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET_KEY=your_jwt_secret

# Nomba Credentials
NOMBA_BASE_URL=https://sandbox.nomba.com
NOMBA_CLIENT_ID=your_client_id
NOMBA_CLIENT_SECRET=your_client_secret
NOMBA_ACCOUNT_ID=your_account_id
```

### 4. Running the Application

To run the web API server:

```bash
uv run uvicorn src.paypulse.api.main:app --reload
```

---

## Testing

To run the test suite:

```bash
PYTHONPATH=. uv run pytest
```
