# Paypulse

Paypulse is a developer-first subscription and recurring billing engine built on top of **Nomba's** payment infrastructure. It automates plan creation, billing cycle execution, card tokenization workflows, smart retries, and dunning cycles for digital products and SaaS platforms.

---

## Features

- **Automated Billing Cycles**: Cron-scheduled checks to charge due subscriptions automatically.
- **Card Tokenization Management**: First-payment card tokenization via Nomba Checkout flows, with secure token storage for recurrent automatic debiting.
- **Smart Dunning & Failure Recovery**: Configurable multi-day retry intervals (e.g., 24h, 48h, 72h) with webhook callbacks and email alerts on failed charge attempts.
- **Robust Client SDK Wrapper**: Up-to-date HTTP client wrapper implementing Nomba's API (Account management, Bank transfers, Virtual accounts, Online checkouts, Tokenized card operations, and Transaction requeries).

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
