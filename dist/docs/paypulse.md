# PayPulse

PayPulse is an onchain AI agent treasury. It allocates hard-capped USDC budgets to AI agents, enforces spending through a metering proxy, and handles borrow escalation via a 2-of-3 human multisig — all on Arc Testnet.

---

## Quickstart — Connect an Agent in 3 Steps

Any code that makes HTTP calls can become a PayPulse agent.

### Step 1 — Get an agent address

Option A: Use a wallet address you already control.

Option B: Create a Circle developer-controlled wallet via the API:

```bash
curl -X POST https://paypulse.cv/api/agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "research",
    "allocationBps": 4000,
    "periodLength": 3600
  }'
```

Returns `agent.address` and `agent.apiKey`.

### Step 2 — Register the agent on-chain

From the **Add Agent** panel in the dashboard, or directly:

```solidity
treasury.addAgent(
  0xYourAgentAddress,
  4000,   // 40% of pool (basis points)
  3600,   // 1-hour budget period
  false,  // not a lender
  0
);
```

### Step 3 — Route API calls through the proxy

Replace your upstream API URL with the PayPulse proxy and add your API key:

```python
# Before
response = requests.get("https://api.example.com/search?q=climate")

# After — budget-metered
response = requests.get(
    "https://paypulse.cv/api/proxy/search?q=climate",
    headers={"X-Agent-Key": "ppk-research-abc123"}
)

if response.status_code == 402:
    # Budget exhausted — request a borrow or wait for period reset
    requests.post("https://paypulse.cv/api/borrow", json={
        "apiKey": "ppk-research-abc123",
        "amount": "50000",
        "reason": "Need extra budget for large research batch"
    })
```

The proxy checks budget on-chain before every call, meters usage, and settles draws to the contract automatically.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PayPulse System                       │
│                                                          │
│  ┌──────────┐    API key    ┌─────────────────────────┐ │
│  │  Agent   │──────────────▶│   Metering Proxy        │ │
│  │ (any AI  │◀──── 402 ────│   /api/proxy/[...path]  │ │
│  │  harness)│               │                         │ │
│  └──────────┘               │  1. auth (X-Agent-Key)  │ │
│                             │  2. budget check (RPC)  │ │
│  ┌──────────┐               │  3. forward upstream    │ │
│  │ Human    │  approve/     │  4. queue draw()        │ │
│  │ Approver │──reject──────▶│                         │ │
│  └──────────┘               └──────────┬──────────────┘ │
│                                        │ settle          │
│                                        ▼ (every 1 min)  │
│                             ┌─────────────────────────┐ │
│                             │  PayPulse.sol            │ │
│                             │  (Arc Testnet)           │ │
│                             │                          │ │
│                             │  poolBalance             │ │
│                             │  agents[].allocation     │ │
│                             │  agents[].spent          │ │
│                             │  borrowRequests[]        │ │
│                             └─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**PayPulse.sol** holds pooled USDC. Agents get percentage-based allocations that reset every period. Borrows under 50% of allocation auto-approve if pool has funds. Larger requests enter a 2-of-3 human multisig queue.

**Metering proxy** (`/api/proxy/*`) authenticates the API key, reads on-chain budget, rejects with 402 if over cap, forwards the request, and queues a `draw()` for settlement.

**Batch settler** (`/api/settle`) runs every minute and drains the draw queue.

---

## Connecting Harnesses and Frameworks

### LangChain (Python)

```python
from langchain.tools import tool
import requests

PROXY_BASE = "https://paypulse.cv/api/proxy"
AGENT_KEY = "ppk-research-001"

@tool
def web_search(query: str) -> str:
    """Search the web. Budget-metered via PayPulse."""
    resp = requests.get(
        f"{PROXY_BASE}/get",
        params={"q": query},
        headers={"X-Agent-Key": AGENT_KEY},
    )
    if resp.status_code == 402:
        return f"Budget exhausted. Remaining: {resp.json().get('remaining')} micro-USDC."
    return resp.json().get("args", {}).get("q", "no result")
```

### CrewAI

```python
from crewai_tools import tool

@tool("PayPulse Proxied Search")
def proxied_search(query: str) -> str:
    import requests
    r = requests.get(
        "https://paypulse.cv/api/proxy/get",
        params={"q": query},
        headers={"X-Agent-Key": "ppk-scraper-001"},
    )
    return r.text if r.status_code == 200 else f"402: {r.json()}"
```

### OpenAI function calling

```python
def call_proxied_api(path: str, params: dict) -> dict:
    import requests
    r = requests.get(
        f"https://paypulse.cv/api/proxy{path}",
        params=params,
        headers={"X-Agent-Key": "ppk-support-001"},
    )
    if r.status_code == 402:
        return {"error": "budget_exhausted", "remaining": r.json().get("remaining")}
    return r.json()
```

### MCP server

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const PROXY = "https://paypulse.cv/api/proxy";
const KEY = process.env.AGENT_API_KEY!;

const server = new Server({ name: "paypulse-mcp", version: "1.0.0" }, {
  capabilities: { tools: {} },
});

server.setRequestHandler("tools/call", async (req) => {
  const { path = "/get", params = {} } = req.params.arguments as Record<string, unknown>;
  const url = new URL(`${PROXY}${path}`);
  Object.entries(params as Record<string, string>).forEach(([k, v]) => url.searchParams.set(k, v));
  const r = await fetch(url.toString(), { headers: { "X-Agent-Key": KEY } });
  const body = await r.json();
  return {
    content: [{ type: "text", text: r.status === 402 ? `402: ${body.error}` : JSON.stringify(body) }],
  };
});

await server.connect(new StdioServerTransport());
```

---

## API Reference

All endpoints are at `https://paypulse.cv`.

### `POST /api/agents/create`

Create a Circle developer-controlled wallet for a new agent.

**Auth required:** `Authorization: Bearer <PAYPULSE_ADMIN_KEY>` or `X-Admin-Key: <PAYPULSE_ADMIN_KEY>`

**Body:**
```json
{
  "name": "research",
  "allocationBps": 4000,
  "periodLength": 3600,
  "isLender": true,
  "maxLendBps": 2000
}
```

**Example:**
```bash
curl -X POST https://paypulse.cv/api/agents/create \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: your-admin-key" \
  -d '{"name":"research","allocationBps":4000,"periodLength":3600}'
```

**Response:**
```json
{
  "ok": true,
  "agent": {
    "name": "research",
    "address": "0xabc...",
    "apiKey": "ppk-research-1a2b3c"
  }
}
```

---

### `POST /api/agents/identity`

Register an agent in the Arc ERC-8004 identity registry.

**Body:**
```json
{
  "agentAddress": "0xabc...",
  "name": "Research Agent",
  "description": "Finds academic papers and summarizes them",
  "proxyBaseUrl": "https://paypulse.cv"
}
```

---

### `GET /api/proxy/[...path]` · `POST /api/proxy/[...path]`

Budget-gated proxy. Add `X-Agent-Key: ppk-<name>-<id>` to every request.

**Success (200):** upstream response plus `X-Charge-USDC` header.

**Budget exhausted (402):**
```json
{
  "error": "Payment Required",
  "code": "BUDGET_EXHAUSTED",
  "remaining": "0",
  "hint": "Request a borrow via POST /api/borrow"
}
```

---

### `POST /api/borrow`

Request a budget increase. Auto-approves if under 50% threshold and pool has funds.

**Body:**
```json
{
  "apiKey": "ppk-research-1a2b3c",
  "amount": "50000",
  "reason": "Large document batch"
}
```

---

### `GET /api/usage`

Last 100 proxy calls in reverse-chronological order.

---

### `GET /api/budget/:address`

On-chain budget state for an agent address.

```json
{ "allocation": "1000000", "spent": "42000", "remaining": "958000" }
```

---

## Contract Reference

**PayPulse.sol** — `0xf59d0bebdfcdbf4a68505efb91abe68595819993` on Arc Testnet

| Function | Access | Description |
|---|---|---|
| `deposit(uint256)` | Anyone | Deposit USDC into the pool |
| `addAgent(address, uint256, uint256, bool, uint256)` | Owner | Register agent with allocation |
| `removeAgent(address)` | Owner | Deregister agent |
| `draw(address, uint256)` | Proxy only | Mark budget as spent |
| `disburse(address, uint256, address)` | Proxy only | Transfer USDC out |
| `requestBorrow(address, uint256, string)` | Agent/Owner/Proxy | Request budget increase |
| `approveBorrow(uint256)` | Approver | Approve a pending borrow |
| `rejectBorrow(uint256)` | Approver | Reject a pending borrow |
| `resetPeriod(address)` | Anyone | Force a period reset |
| `setProxy(address)` | Owner | Set the authorized proxy wallet |
| `addApprover(address)` | Owner | Add a human approver (max 3) |

[View on Arc Testnet Explorer →](https://explorer.testnet.arc.io/address/0xf59d0bebdfcdbf4a68505efb91abe68595819993)

---

## Environment Variables

Set these in your Vercel project: **Settings → Environment Variables**.

| Variable | Required | Description |
|---|---|---|
| `VITE_PAYPULSE_ADDRESS` | Yes | Deployed contract address — `0xf59d0bebdfcdbf4a68505efb91abe68595819993` |
| `PAYPULSE_ADMIN_KEY` | Yes | Any strong random string. Protects `/api/agents/create` and `/api/agents/identity`. Pass as `X-Admin-Key` header. |
| `PROXY_PRIVATE_KEY` | Yes (onchain) | Private key of the wallet registered as proxy on-chain via `setProxy()`. Signs `draw()` and `disburse()` calls. |
| `CIRCLE_API_KEY` | For wallet creation | Standard Developer API Key from [Circle Console](https://console.circle.com). |
| `CIRCLE_ENTITY_SECRET` | For wallet creation | Entity secret paired with the API key. Register once via the Admin tab. |
| `VITE_IDENTITY_REGISTRY` | For ERC-8004 | Arc Testnet identity registry address (from Arc docs). |

**Generate a strong admin key:**
```bash
openssl rand -hex 32
```
