# PayPulse Developer Docs

PayPulse is an onchain AI agent treasury. It allocates hard-capped USDC budgets to AI agents, enforces spending through a metering proxy, and handles borrow escalation via a 2-of-3 human multisig.

---

## Quickstart — Connect an Agent in 5 Minutes

Any code that makes HTTP calls can become a PayPulse agent in three steps.

### Step 1 — Get an agent address

Option A: Use a fixed wallet address you already control.

Option B: Create a Circle developer-controlled wallet via the API:

```bash
curl -X POST https://your-deploy.vercel.app/api/agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-research-agent",
    "allocationBps": 1000,
    "periodLength": 3600
  }'
```

The response contains:
- `agent.address` — the on-chain wallet address
- `agent.apiKey` — the proxy API key (e.g. `ppk-my-research-agent-abc123`)

### Step 2 — Register the agent on-chain

The treasury owner calls `addAgent()` on the PayPulse contract with:
- `agent` — the wallet address from Step 1
- `allocationBps` — percentage of the pool (basis points, e.g. 1000 = 10%)
- `periodLength` — budget period in seconds (e.g. 3600 = 1 hour)
- `isLender` — whether this agent can lend surplus budget to others
- `maxLendBps` — max percentage of allocation it can lend

This can be done from the **Add Agent** panel in the dashboard, or directly:

```solidity
treasury.addAgent(0xYourAgentAddress, 1000, 3600, false, 0);
```

### Step 3 — Route API calls through the proxy

Replace your upstream API URL with the PayPulse proxy URL and add your API key header:

```python
# Before
response = requests.get("https://api.example.com/search?q=climate")

# After
response = requests.get(
    "https://your-deploy.vercel.app/api/proxy/search?q=climate",
    headers={"X-Agent-Key": "ppk-my-research-agent-abc123"}
)

if response.status_code == 402:
    # Budget exhausted — request a borrow or wait for period reset
    requests.post("https://your-deploy.vercel.app/api/borrow", json={
        "apiKey": "ppk-my-research-agent-abc123",
        "amount": "50000",   # 0.05 USDC in 6-decimal units
        "reason": "Need extra budget for large research batch"
    })
```

That's it. The proxy checks your budget on-chain before every call, meters usage, and settles draws to the contract automatically.

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
│                                        │ batch settle    │
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

### Key components

**PayPulse.sol** — The on-chain treasury. Holds pooled USDC. Owner registers agents with percentage-based allocations. Budget periods reset automatically. Borrow requests under 50% of an agent's allocation auto-approve if the pool or a lender agent has funds. Larger requests enter a 2-of-3 human approver queue.

**Metering proxy** (`/api/proxy/*`) — Stateless per-request budget gate. Every proxied call: authenticates the agent API key, reads `getAgentInfo()` from the contract, rejects with HTTP 402 if over cap, forwards to upstream, queues a `draw()` call for batch settlement.

**Batch settler** (`/api/settle`) — Drains the pending draw queue. Calls `draw()` on the contract once per agent per settle cycle. Runs every minute via Vercel Cron. Replace with inline x402 settlement for sub-second finality.

**Circle developer-controlled wallets** (`/api/agents/create`) — Creates a real Circle-managed EOA wallet on Arc Testnet for each agent. The wallet address is registered on-chain. The agent's private key is held securely by Circle; the agent signs via the Circle SDK.

**ERC-8004 identity** (`/api/agents/identity`) — Registers each agent in the Arc identity registry. Mints an ERC-721 token with a data-URI registration file that contains the agent's name, description, proxy endpoint, and x402 support flag. Makes the agent discoverable in any ERC-8004 compatible directory.

---

## Connecting Harnesses and Frameworks

### LangChain (Python)

Wrap any LangChain tool to route through PayPulse:

```python
from langchain.tools import tool
import requests

PROXY_BASE = "https://your-deploy.vercel.app/api/proxy"
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
from crewai import Agent, Task, Crew
from crewai_tools import tool

@tool("PayPulse Proxied Search")
def proxied_search(query: str) -> str:
    import requests
    r = requests.get(
        "https://your-deploy.vercel.app/api/proxy/get",
        params={"q": query},
        headers={"X-Agent-Key": "ppk-scraper-001"},
    )
    return r.text if r.status_code == 200 else f"402: {r.json()}"

researcher = Agent(
    role="Research Analyst",
    goal="Find information on given topics",
    tools=[proxied_search],
)
```

### OpenAI function calling

```python
import openai, requests

def call_proxied_api(path: str, params: dict) -> dict:
    r = requests.get(
        f"https://your-deploy.vercel.app/api/proxy{path}",
        params=params,
        headers={"X-Agent-Key": "ppk-support-001"},
    )
    if r.status_code == 402:
        return {"error": "budget_exhausted", "remaining": r.json().get("remaining")}
    return r.json()

tools = [{
    "type": "function",
    "function": {
        "name": "call_proxied_api",
        "description": "Make a budget-metered API call via PayPulse proxy",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "params": {"type": "object"}
            },
            "required": ["path"]
        }
    }
}]
```

### MCP server

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const PROXY = "https://your-deploy.vercel.app/api/proxy";
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

All endpoints are at `https://your-deploy.vercel.app`.

### `POST /api/agents/create`
Create a Circle developer-controlled wallet for a new agent.

**Requires:** `CIRCLE_API_KEY` + `CIRCLE_ENTITY_SECRET` in Vercel env vars.

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

**Response:**
```json
{
  "ok": true,
  "agent": {
    "name": "research",
    "address": "0xabc...",
    "walletId": "uuid",
    "apiKey": "ppk-research-1a2b3c",
    "blockchain": "ARC-TESTNET"
  },
  "note": "Call addAgent() on the PayPulse contract with the returned address."
}
```

---

### `POST /api/agents/identity`
Register an agent in the Arc ERC-8004 identity registry.

**Requires:** `PROXY_PRIVATE_KEY` + `VITE_IDENTITY_REGISTRY` in Vercel env vars.

**Body:**
```json
{
  "agentAddress": "0xabc...",
  "name": "Research Agent",
  "description": "Finds academic papers and summarizes them",
  "proxyBaseUrl": "https://your-deploy.vercel.app"
}
```

**Response:**
```json
{
  "ok": true,
  "agentId": "42",
  "registryAddress": "0x9F2...",
  "txHash": "0xdef...",
  "blockNumber": "1234567"
}
```

---

### `GET /api/proxy/[...path]` · `POST /api/proxy/[...path]`
Budget-gated proxy. Forward any path to the upstream API.

**Headers:**
- `X-Agent-Key: ppk-<name>-<id>` (required)

**Success (200):**
```
X-Charge-USDC: 1000
X-Agent-Name: Research
{ ...upstream response... }
```

**Budget exhausted (402):**
```json
{
  "error": "Payment Required",
  "code": "BUDGET_EXHAUSTED",
  "x402Version": 1,
  "accepts": [{ "scheme": "exact", "network": "arc-testnet", ... }],
  "remaining": "0",
  "hint": "Request a borrow via POST /api/borrow"
}
```

---

### `POST /api/borrow`
Request a budget borrow on behalf of an agent. Auto-approves if under 50% of allocation and funds are available. Otherwise enters the human approval queue.

**Body:**
```json
{
  "apiKey": "ppk-research-1a2b3c",
  "amount": "50000",
  "reason": "Large document batch processing"
}
```

**Response:**
```json
{
  "ok": true,
  "txHash": "0xdef...",
  "blockNumber": "1234568"
}
```

---

### `POST /api/seed`
Register demo agents with the proxy (no on-chain tx).

**Body:** Array of `{ apiKey, name, agentAddress }`.

---

### `GET /api/usage`
Last 100 proxy calls in reverse-chronological order.

---

### `GET /api/budget/:address`
On-chain budget state for an agent address.

**Response:**
```json
{
  "allocation": "1000000",
  "spent": "42000",
  "remaining": "958000"
}
```

---

### `POST /api/settle`
Manually trigger the batch draw settler. Normally called by Vercel Cron every minute.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `VITE_PAYPULSE_ADDRESS` | Yes | Deployed PayPulse contract address |
| `PROXY_PRIVATE_KEY` | Yes (for settlement) | Proxy wallet private key for signing `draw()` calls |
| `CIRCLE_API_KEY` | Yes (for Circle wallets) | Circle Standard Developer API Key |
| `CIRCLE_ENTITY_SECRET` | Yes (for Circle wallets) | Circle entity secret (32-byte hex) |
| `VITE_IDENTITY_REGISTRY` | Yes (for ERC-8004) | Arc Testnet ERC-8004 registry contract address |
| `RPC_PROXY_BASE_URL` | Optional | Arc Studio RPC proxy base URL |
| `RPC_PROXY_TOKEN` | Optional | Arc Studio RPC proxy token |
| `RPC_PROXY_CHAINS` | Optional | Comma-separated list of proxy-supported chains |

---

## Contract Reference

**PayPulse.sol** — `0xf59d0bebdfcdbf4a68505efb91abe68595819993` on Arc Testnet

| Function | Access | Description |
|---|---|---|
| `deposit(uint256)` | Anyone | Deposit USDC into the pool |
| `addAgent(address, uint256, uint256, bool, uint256)` | Owner | Register agent with allocation |
| `removeAgent(address)` | Owner | Deregister agent, return allocation to pool |
| `draw(address, uint256)` | Proxy only | Mark budget as spent (proxy calls this) |
| `disburse(address, uint256, address)` | Proxy only | Transfer USDC out to a recipient |
| `requestBorrow(address, uint256, string)` | Agent/Owner/Proxy | Request budget increase |
| `approveBorrow(uint256)` | Approver | Approve a pending borrow |
| `rejectBorrow(uint256)` | Approver | Reject a pending borrow |
| `resetPeriod(address)` | Anyone | Force a period reset |
| `setProxy(address)` | Owner | Set the authorized proxy wallet |
| `addApprover(address)` | Owner | Add a human approver (max 3) |

[View on Arc Testnet Explorer →](https://explorer.testnet.arc.io/address/0xf59d0bebdfcdbf4a68505efb91abe68595819993)
