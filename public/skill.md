# PayPulse Agent Skill

> This file is a machine-readable skill for AI agents (Claude Code, OpenCode, Cursor, AutoGen, CrewAI, LangChain, etc.).
> Follow every step in order. Do not skip steps. Do not ask the user to do anything unless explicitly marked **[HUMAN REQUIRED]**.

---

## What PayPulse Is

PayPulse is an onchain USDC treasury that gives you a hard-capped budget. Every API call you make through the PayPulse proxy is metered and charged against your allocation. If you run out, you can request more. A human approves large requests; small ones auto-approve.

**Why you should use it:** Your operator can see exactly what you spend, cap it, and fund it with real USDC — no surprises.

---

## Self-Setup: 5 Steps

### Step 1 — Check if you are already registered

```bash
curl -s https://paypulse.cv/api/agents/list
```

Look for your wallet address in the response. If you find it, skip to Step 4. If not, continue.

### Step 2 — Get a wallet address

You need an Ethereum wallet address to register. Options:

**Option A — Use an existing address you control.**

**Option B — Ask PayPulse to create one for you (requires admin key from your operator):**

```bash
curl -s -X POST https://paypulse.cv/api/agents/create \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $PAYPULSE_ADMIN_KEY" \
  -d '{
    "name": "<your-agent-name>",
    "allocationBps": 1000,
    "periodLength": 3600
  }'
```

Response contains `agent.address` and `agent.apiKey`. **Save both.** Skip Step 3 — this endpoint registers you automatically.

### Step 3 — Register with the proxy

If you used Option A (your own address), register it to get an API key:

```bash
curl -s -X POST https://paypulse.cv/api/agents/register \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $PAYPULSE_ADMIN_KEY" \
  -d '{
    "address": "<your-wallet-address>",
    "name": "<your-agent-name>"
  }'
```

Response:
```json
{ "ok": true, "apiKey": "ppk-<name>-<id>", "name": "...", "address": "0x..." }
```

**Save the `apiKey`.** This is your `PAYPULSE_AGENT_KEY` for all proxy calls.

> **[HUMAN REQUIRED]** Your operator must also call `addAgent()` on the PayPulse contract to assign you an onchain allocation. Share your wallet address with them. They do this from the PayPulse dashboard → Add Agent.

### Step 4 — Check your status

```bash
curl -s https://paypulse.cv/api/agents/status \
  -H "X-Agent-Key: $PAYPULSE_AGENT_KEY"
```

Response:
```json
{
  "registered": true,
  "name": "my-agent",
  "address": "0x...",
  "allocation": "1000000",
  "spent": "0",
  "remaining": "1000000",
  "periodEndsIn": "3412s"
}
```

All amounts are in micro-USDC (6 decimals). `1000000` = 1.00 USDC.

If `allocation` is `"0"`, your operator has not yet assigned you an onchain budget. Ask them to do so.

### Step 5 — Configure the MCP server

Install dependencies:
```bash
cd mcp/
bun install
```

Set environment variables:
```bash
export PAYPULSE_URL=https://paypulse.cv
export PAYPULSE_AGENT_KEY=ppk-<name>-<id>   # from Step 3
```

**Claude Code** — add to `.mcp.json` in your project root:
```json
{
  "mcpServers": {
    "paypulse": {
      "command": "bun",
      "args": ["<absolute-path-to-repo>/mcp/paypulse-mcp.ts"],
      "env": {
        "PAYPULSE_URL": "https://paypulse.cv",
        "PAYPULSE_AGENT_KEY": "ppk-<name>-<id>"
      }
    }
  }
}
```

**OpenCode** — add to `~/.config/opencode/config.json`:
```json
{
  "mcp": {
    "paypulse": {
      "command": "bun",
      "args": ["<absolute-path-to-repo>/mcp/paypulse-mcp.ts"],
      "environment": {
        "PAYPULSE_URL": "https://paypulse.cv",
        "PAYPULSE_AGENT_KEY": "ppk-<name>-<id>"
      }
    }
  }
}
```

**Claude Desktop** — add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "paypulse": {
      "command": "bun",
      "args": ["<absolute-path-to-repo>/mcp/paypulse-mcp.ts"],
      "env": {
        "PAYPULSE_URL": "https://paypulse.cv",
        "PAYPULSE_AGENT_KEY": "ppk-<name>-<id>"
      }
    }
  }
}
```

---

## Using the MCP Tools

Once connected, you have three tools:

### `paypulse_fetch`

Call any upstream API through your budget. If your budget is exhausted you get a `BUDGET_EXHAUSTED` response — call `paypulse_borrow` to request more.

```
paypulse_fetch({
  upstreamUrl: "https://api.openai.com/v1/chat/completions",
  method: "POST",
  upstreamHeaders: { "Authorization": "Bearer sk-..." },
  body: { "model": "gpt-4o-mini", "messages": [{ "role": "user", "content": "Hello" }] }
})
```

### `paypulse_budget`

Check how much budget you have left this period.

```
paypulse_budget()
→ { allocation: "1000000", spent: "42000", remaining: "958000", periodEndsIn: "3412s" }
```

### `paypulse_borrow`

Request more budget. Amounts under 50% of your allocation auto-approve if the pool has funds. Larger amounts go to a human approver queue.

```
paypulse_borrow({
  amount: "500000",
  reason: "Need extra budget to process a large document batch"
})
```

---

## Decision Tree: What to Do When You Get a 402

```
Got 402 BUDGET_EXHAUSTED
  │
  ├─ Call paypulse_budget()
  │    ├─ remaining == 0 AND periodEndsIn < 300s → wait for period reset, retry
  │    └─ remaining == 0 AND periodEndsIn > 300s → call paypulse_borrow()
  │
  └─ paypulse_borrow() response:
       ├─ { autoApproved: true } → retry the original call immediately
       └─ { pending: true, requestId: "N" } → notify operator, wait for approval
```

---

## Verification Checklist

Run these to confirm everything is working:

```bash
# 1. Confirm registered
curl -s https://paypulse.cv/api/agents/list | grep <your-address>

# 2. Confirm budget
curl -s https://paypulse.cv/api/budget/<your-address>

# 3. Test a proxied call (replace with any real API)
curl -s -X POST https://paypulse.cv/api/proxy \
  -H "X-Agent-Key: $PAYPULSE_AGENT_KEY" \
  -H "X-Upstream-URL: https://httpbin.org/get" \
  -H "Content-Type: application/json"
# → should return httpbin response with X-Charge-USDC header

# 4. Confirm usage logged
curl -s https://paypulse.cv/api/usage | head -c 200
```

---

## Environment Variables Reference

| Variable | Where to set | Description |
|---|---|---|
| `PAYPULSE_URL` | MCP server env | PayPulse deployment URL. Use `https://paypulse.cv`. |
| `PAYPULSE_AGENT_KEY` | MCP server env | Your agent's API key (`ppk-<name>-<id>`). |
| `PAYPULSE_ADMIN_KEY` | Only for self-registration | Admin key from your operator. Only needed for Steps 2–3. Never store long-term. |

---

## Contract

**PayPulse.sol** — `0xf59d0bebdfcdbf4a68505efb91abe68595819993` on Arc Testnet

[View on Explorer →](https://explorer.testnet.arc.io/address/0xf59d0bebdfcdbf4a68505efb91abe68595819993)
