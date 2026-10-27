# PayPulse

PayPulse is an onchain AI agent treasury. It allocates hard-capped USDC budgets to AI agents, enforces spending through a metering proxy, and handles borrow escalation via a 2-of-3 human multisig — all on Arc Testnet.

---

## Quickstart — Connect an Agent in 3 Steps

### Step 1 — Get a wallet address

**Option A:** Use any EVM address you already control.

**Option B:** Create a Circle developer-controlled wallet (requires `CIRCLE_API_KEY` + `CIRCLE_ENTITY_SECRET` env vars):

```bash
curl -X POST https://paypulse.cv/api/agents/create \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -d '{"name":"research","allocationBps":4000,"periodLength":3600}'
```

Returns `agent.address` and `agent.apiKey` — skip Steps 2a and 2b if you use this route.

---

### Step 2a — Register the agent on-chain

From the **Add Agent** panel in the dashboard, or call the contract directly:

```solidity
treasury.addAgent(
  0xYourAgentAddress,
  4000,   // 40% of pool (basis points)
  3600,   // 1-hour budget period
  false,  // not a lender
  0       // maxLendBps (0 if not a lender)
);
```

---

### Step 2b — Register the agent with the proxy

This gives the agent an API key it will use on every call:

```bash
curl -X POST https://paypulse.cv/api/agents/register \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -d '{"address":"0xYourAgentAddress","name":"research"}'
```

Response:
```json
{
  "ok": true,
  "apiKey": "ppk-research-a1b2c3",
  "name": "research",
  "address": "0xYourAgentAddress"
}
```

Save the `apiKey` — this is the agent's `X-Agent-Key` on every proxy call.

---

### Step 3 — Route calls through the proxy

Keep your upstream URL exactly as-is. Pass it in `X-Upstream-URL`, add your agent key, and put any auth headers for the upstream in `X-Upstream-Headers`:

```bash
# Call any upstream API — budget-metered
curl -X POST "https://paypulse.cv/api/proxy" \
  -H "X-Agent-Key: ppk-research-a1b2c3" \
  -H "X-Upstream-URL: https://api.openai.com/v1/chat/completions" \
  -H "X-Upstream-Headers: {\"Authorization\":\"Bearer sk-...\"}" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"hello"}]}'
```

If budget is exhausted you get a `402`:
```json
{
  "error": "Payment Required",
  "code": "BUDGET_EXHAUSTED",
  "remaining": "0",
  "hint": "POST /api/borrow with your apiKey to request more budget"
}
```

The proxy checks budget on-chain, forwards the full request to the real upstream, returns the upstream response transparently, and settles the draw to the contract.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    PayPulse System                        │
│                                                           │
│  ┌──────────┐    X-Agent-Key   ┌──────────────────────┐  │
│  │  Agent   │─────────────────▶│  Metering Proxy      │  │
│  │ (any AI  │◀──── 402 ────── │  /api/proxy/[path]   │  │
│  │ harness) │                  │                      │  │
│  └──────────┘                  │  1. auth (API key)   │  │
│                                │  2. budget check RPC │  │
│  ┌──────────┐                  │  3. forward upstream │  │
│  │  Human   │  approve/reject  │  4. queue draw()     │  │
│  │ Approver │─────────────────▶│  5. settle onchain   │  │
│  └──────────┘                  └──────────┬───────────┘  │
│                                           │              │
│                                           ▼              │
│                                ┌──────────────────────┐  │
│                                │   PayPulse.sol       │  │
│                                │   Arc Testnet        │  │
│                                │                      │  │
│                                │   poolBalance        │  │
│                                │   agents[].allocation│  │
│                                │   agents[].spent     │  │
│                                │   borrowRequests[]   │  │
│                                └──────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## MCP Server

PayPulse ships an MCP server so any MCP-compatible agent (Claude Desktop, Cursor, Continue) can use the proxy directly as a tool.

### Setup

```bash
# 1. Clone / install
cd mcp/
bun add @modelcontextprotocol/sdk

# 2. Set env vars
export PAYPULSE_URL=https://paypulse.cv
export PAYPULSE_AGENT_KEY=ppk-research-a1b2c3

# 3. Run
bun run mcp/paypulse-mcp.ts
```

### Claude Desktop config

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paypulse": {
      "command": "bun",
      "args": ["/absolute/path/to/mcp/paypulse-mcp.ts"],
      "env": {
        "PAYPULSE_URL": "https://paypulse.cv",
        "PAYPULSE_AGENT_KEY": "ppk-research-a1b2c3"
      }
    }
  }
}
```

### MCP Tools

| Tool | What it does |
|---|---|
| `paypulse_call` | Budget-metered GET through the proxy |
| `paypulse_post` | Budget-metered POST through the proxy |
| `paypulse_usage` | Recent call history for this agent |
| `paypulse_borrow` | Request a budget increase |

---

## Framework Examples

### LangChain (Python)

```python
from langchain.tools import tool
import requests, json

PROXY = "https://paypulse.cv/api/proxy"
KEY = "ppk-research-a1b2c3"

@tool
def call_openai(prompt: str) -> str:
    """Call OpenAI — budget-metered via PayPulse."""
    r = requests.post(
        PROXY,
        headers={
            "X-Agent-Key": KEY,
            "X-Upstream-URL": "https://api.openai.com/v1/chat/completions",
            "X-Upstream-Headers": json.dumps({"Authorization": "Bearer sk-..."}),
            "Content-Type": "application/json",
        },
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
    )
    if r.status_code == 402:
        return f"Budget exhausted. Remaining: {r.json().get('remaining')} micro-USDC."
    return r.json()["choices"][0]["message"]["content"]
```

### CrewAI

```python
from crewai_tools import tool
import requests, json

@tool("PayPulse Proxied Request")
def proxied_request(upstream_url: str, payload: dict) -> str:
    """Forward any API call through PayPulse budget gating."""
    r = requests.post(
        "https://paypulse.cv/api/proxy",
        headers={
            "X-Agent-Key": "ppk-scraper-a1b2c3",
            "X-Upstream-URL": upstream_url,
            "Content-Type": "application/json",
        },
        json=payload,
    )
    return r.text if r.status_code == 200 else f"402: {r.json()}"
```

### OpenAI function calling

```python
def call_proxied_api(upstream_url: str, payload: dict, upstream_headers: dict = {}) -> dict:
    import requests, json
    r = requests.post(
        "https://paypulse.cv/api/proxy",
        headers={
            "X-Agent-Key": "ppk-support-a1b2c3",
            "X-Upstream-URL": upstream_url,
            "X-Upstream-Headers": json.dumps(upstream_headers),
            "Content-Type": "application/json",
        },
        json=payload,
    )
    if r.status_code == 402:
        return {"error": "budget_exhausted", "remaining": r.json().get("remaining")}
    return r.json()
```

---

## API Reference

All endpoints are at `https://paypulse.cv`.  
`*` = requires `X-Admin-Key: YOUR_ADMIN_KEY` header.

### `POST /api/agents/register` *

Register an existing wallet address with the proxy. Required before any agent can use the proxy.

**Body:**
```json
{ "address": "0xYourAgentAddress", "name": "research" }
```

**Response:**
```json
{ "ok": true, "apiKey": "ppk-research-a1b2c3", "name": "research", "address": "0x..." }
```

---

### `GET /api/agents/list`

List all agents registered with the proxy (names and addresses only — no API keys).

---

### `POST /api/agents/create` *

Create a new Circle developer-controlled wallet and register it with the proxy in one call. Requires `CIRCLE_API_KEY` + `CIRCLE_ENTITY_SECRET` in Vercel env vars.

**Body:**
```json
{ "name": "research", "allocationBps": 4000, "periodLength": 3600 }
```

**Response:**
```json
{ "ok": true, "agent": { "name": "research", "address": "0x...", "apiKey": "ppk-research-a1b2c3" } }
```

---

### `POST /api/agents/identity` *

Register an agent in the Arc ERC-8004 identity registry. Requires `PROXY_PRIVATE_KEY` + `VITE_IDENTITY_REGISTRY` in env vars.

**Body:**
```json
{ "agentAddress": "0x...", "name": "Research Agent", "description": "..." }
```

---

### `ANY /api/proxy`

Budget-gated proxy. Forwards to any upstream URL. Agent must be registered first.

**Required headers:**
- `X-Agent-Key: ppk-<name>-<id>` — your agent's API key
- `X-Upstream-URL: https://real-api.com/endpoint` — the actual URL to call

**Optional headers:**
- `X-Upstream-Headers: {"Authorization":"Bearer ..."}` — upstream auth (JSON)

**Example:**
```bash
curl -X POST https://paypulse.cv/api/proxy \
  -H "X-Agent-Key: ppk-research-a1b2c3" \
  -H "X-Upstream-URL: https://api.openai.com/v1/chat/completions" \
  -H "X-Upstream-Headers: {\"Authorization\":\"Bearer sk-...\"}" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hello"}]}'
```

**Success (200):** upstream response body + `X-Charge-USDC` and `X-PayPulse-Remaining` headers.

**Budget exhausted (402):**
```json
{
  "error": "Payment Required",
  "code": "BUDGET_EXHAUSTED",
  "remaining": "0",
  "hint": "POST /api/borrow with your apiKey to request more budget"
}
```

---

### `POST /api/borrow`

Request a budget increase. Auto-approves below 50% of allocation if pool has funds. Above that enters the 2-of-3 approver queue visible in the dashboard. Requires `PROXY_PRIVATE_KEY` in env vars.

**Body:**
```json
{ "apiKey": "ppk-research-a1b2c3", "amount": "1000000", "reason": "Large research batch" }
```

---

### `GET /api/usage`

Last 100 proxy calls in reverse-chronological order.

---

### `GET /api/budget/:address`

On-chain budget state for an agent address.

```json
{ "allocation": "10000000", "spent": "420000", "remaining": "9580000" }
```

---

### `POST /api/settle`

Drain the pending draw queue and settle onchain. Called automatically after every proxy call. Can also be triggered manually.

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

Set these in **Vercel → Settings → Environment Variables**.

| Variable | Required | Description |
|---|---|---|
| `VITE_PAYPULSE_ADDRESS` | Yes | `0xf59d0bebdfcdbf4a68505efb91abe68595819993` |
| `PAYPULSE_ADMIN_KEY` | Yes | Random string protecting admin routes. Pass as `X-Admin-Key`. |
| `PROXY_PRIVATE_KEY` | For onchain settlement | Private key of the wallet set as proxy via `setProxy()`. |
| `CIRCLE_API_KEY` | For `/api/agents/create` | Standard Developer API Key from Circle Console. |
| `CIRCLE_ENTITY_SECRET` | For `/api/agents/create` | Entity secret paired with the API key. |
| `VITE_IDENTITY_REGISTRY` | For ERC-8004 | Arc Testnet identity registry contract address. |

```bash
# Generate a strong admin key
openssl rand -hex 32
```
