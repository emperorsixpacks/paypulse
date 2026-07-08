# PayPulse

A developer-first subscription and recurring billing engine built on **Nomba's** payment infrastructure. Automates plan creation, billing cycles, card tokenization, smart retries, dunning, and usage-based pricing for digital products and SaaS platforms.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy 2.0 (asyncpg), Alembic |
| **Database** | PostgreSQL 16, Redis 7 |
| **Task Queue** | ARQ (Redis Streams) |
| **Frontend** | SvelteKit 5, Tailwind CSS 4, Vite 8 |
| **Docs** | Mintlify (auto-generated OpenAPI) |
| **Deployment** | Docker Compose (6 services) |
| **Package Manager** | uv (Python), npm (JS) |

---

## Directory Structure

```text
paypulse/
├── config/                        # Environment configs (.env.dev, .env.prod)
├── src/
│   ├── paypulse/                  # Python backend
│   │   ├── api/v1/                # FastAPI route handlers (10 routers)
│   │   ├── core/                  # Settings, DB engine, security
│   │   ├── infrastructure/nomba/  # Nomba SDK (HTTP client, DTOs, config)
│   │   ├── models/                # SQLAlchemy models (12 tables)
│   │   ├── repositories/          # Data access layer (9 repos)
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   └── services/              # Business logic (11 services)
│   ├── web/                       # SvelteKit landing page
│   ├── dashboard/                 # SvelteKit merchant dashboard
│   ├── checkout/                  # SvelteKit checkout app
│   └── workers/                   # ARQ background workers
├── docs/                          # Mintlify documentation
├── tests/                         # Pytest test suites
├── API_ENDPOINTS.md               # Full API reference
├── docker-compose.yml             # 6-service orchestration
├── Dockerfile                     # API container
├── pyproject.toml                 # Python dependencies
└── uv.lock                        # uv lockfile
```

---

## Features

### Backend (37 API Endpoints)

**Authentication & Merchants**
- Register, login, JWT auth
- Merchant profile, project CRUD, API key management (test/live)

**Billing Core**
- Plans: CRUD with billing intervals (daily/weekly/monthly/quarterly/annually)
- Subscriptions: list, get, cancel with refund calculation
- Invoices: list, get with refund status tracking
- Checkout sessions: create, get, cancel with shareable links
- Usage reporting and history (metered billing)

**Revenue Operations**
- Cancellation policies: full/none/percentage/prorate refund types, window, fees, default policy
- Webhooks: create/delete endpoints with event subscriptions
- Refund calculation service (prorated by remaining period ratio)

**Background Workers (ARQ)**
- `billing_worker`: Invoice generation, billing attempt execution
- `dunning_worker`: Smart retry logic (24h, 48h, 72h intervals)
- `webhook_worker`: Outbound webhook delivery with retry

### Landing Page (`src/web/`)
- Dark theme (ink + cobalt + lime palette)
- Receipt-style hero with floating invoice cards
- Features grid, stats section, CTA, footer
- Social meta tags (Open Graph, Twitter)
- Space Grotesk / Inter / IBM Plex Mono fonts

### Merchant Dashboard (`src/dashboard/`) — 11 Pages
- **Overview**: MRR, active subs, failed invoices, cancelled stats + recent invoices table
- **Plans**: Full CRUD with create/edit modal, interval formatting
- **Customers**: List + detail view with subscriptions/invoices tabs
- **Subscriptions**: Status filter pills, cancel modal with period-end toggle + refund response
- **Invoices**: Table with refund amount + refund status badges
- **Checkout**: Create session, copy shareable link, cancel
- **Cancellation Policies**: Full CRUD with refund type selector, fee, window, default toggle
- **Webhooks**: Endpoint list + add form with event tags
- **Developers**: API key management (create test/live, revoke, copy)
- **Settings**: Profile display + sign out
- **Login**: Email/password auth, JWT + API key storage

### Documentation (`docs/`)
- Mintlify with PayPulse branding (cobalt/lime/ink)
- Auto-generated OpenAPI spec from FastAPI (28 paths)
- API reference pages using `openapi:` references
- Guides: usage billing, webhooks, cancellation policies

---

## Getting Started

### Requirements

- Python >= 3.13
- Node.js >= 20
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose (optional)

### Quick Start (Docker)

```bash
# Start all services
sudo docker compose up -d

# Services:
#   API        → http://localhost:8000
#   Web        → http://localhost:3000
#   Dashboard  → http://localhost:3001
#   Docs       → http://localhost:3002
#   PostgreSQL → localhost:5432
#   Redis      → localhost:6379
```

### Quick Start (Local)

```bash
# Install Python deps
uv sync

# Install JS deps
cd src/web && npm install && cd ../..
cd src/dashboard && npm install && cd ../..

# Create config/.env (see config/.env.dev for template)

# Run API
uv run uvicorn src.paypulse.main:app --reload

# Run landing page
cd src/web && npm run dev

# Run dashboard
cd src/dashboard && npm run dev
```

### Environment Variables

```ini
ENVIRONMENT=dev
DB_USER=paypulse
DB_PASSWORD=paypulse_dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=paypulse
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET_KEY=your_jwt_secret

# Nomba (sandbox)
NOMBA_CLIENT_ID=
NOMBA_CLIENT_SECRET=
NOMBA_ACCOUNT_ID=
```

### Database Migrations

```bash
# Generate migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

---

## Deploying to a VPS

Production deployment uses Docker Compose with Nginx reverse proxy and Let's Encrypt SSL.

### Architecture

```text
Internet → :443 (HTTPS)
  ├── api.paypulse.cv      → Nginx → API container (:8000)
  └── dashboard.paypulse.cv → Nginx → Dashboard container (:3000)

Redis runs locally on the VPS.
Database is hosted externally on Neon PostgreSQL.
```

### Prerequisites

- Ubuntu/Debian VPS (RackNerd, DigitalOcean, Hetzner, etc.)
- Two DNS A records pointing to your VPS IP:
  ```
  api.paypulse.cv      → YOUR_VPS_IP
  dashboard.paypulse.cv → YOUR_VPS_IP
  ```
- SSH root access to the VPS

### Step 1: Configure Environment

Edit `config/.env.production` with your real secrets:

```bash
# Generate a secure JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Fill in these values in config/.env.production:
#   JWT_SECRET_KEY=<generated secret>
#   NOMBA_CLIENT_ID=<production credentials>
#   NOMBA_CLIENT_SECRET=<production credentials>
#   NOMBA_ACCOUNT_ID=<production credentials>
#   RESEND_API_KEY=<your Resend API key>
```

### Step 2: Deploy

```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Clone the repo
git clone https://github.com/anomalyco/paypulse.git /opt/paypulse
cd /opt/paypulse

# Run the one-script setup
bash deploy.sh
```

The script will:
1. Install Docker, Nginx, Certbot, UFW firewall
2. Build and start API, Dashboard, Redis, Nginx containers
3. Prompt to issue SSL certificates once DNS has propagated
4. Start serving over HTTPS

### Step 3: Verify

```bash
# Health check
curl https://api.paypulse.cv/health

# Dashboard
open https://dashboard.paypulse.cv
```

### Managing Services

```bash
cd /opt/paypulse

# View logs
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f dashboard

# Restart all services
docker compose -f docker-compose.prod.yml restart

# Update after git pull
git pull
docker compose -f docker-compose.prod.yml up -d --build

# Stop all services
docker compose -f docker-compose.prod.yml down
```

### Files Added for VPS Deployment

| File | Purpose |
|---|---|
| `docker-compose.prod.yml` | Production compose (API + Dashboard + Redis + Nginx + Certbot) |
| `config/.env.production` | Production environment variables (gitignored) |
| `nginx/api.conf` | Nginx reverse proxy for `api.paypulse.cv` with SSL |
| `nginx/dashboard.conf` | Nginx reverse proxy for `dashboard.paypulse.cv` with SSL |
| `nginx/default.conf` | HTTP-only config for initial certbot setup |
| `deploy.sh` | One-command VPS setup script |

---

## Testing

```bash
PYTHONPATH=. uv run pytest
```

---

## License

Private. All rights reserved.
