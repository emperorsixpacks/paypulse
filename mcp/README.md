# PayPulse MCP Server

Budget-metered HTTP calls for AI agents — enforced on-chain via PayPulse.

Every API call your agent makes through this MCP server is:
- Authenticated with your agent key
- Budget-checked against your on-chain allocation
- Forwarded to the real upstream API
- Charged against your USDC allocation
- Rejected with a 402 if you're over cap (with a `paypulse_borrow` escape hatch)

## Prerequisites

- [Bun](https://bun.sh) installed (`curl -fsSL https://bun.sh/install | bash`)
- A PayPulse agent key — register at **https://paypulse.cv** (Admin → Add Agent, then `/api/agents/register`)

## Install

```bash
cd mcp/
bun install
```

## Environment variables

| Variable | Description |
|---|---|
| `PAYPULSE_URL` | Your PayPulse deployment. Use `https://paypulse.cv` or your own Vercel URL. |
| `PAYPULSE_AGENT_KEY` | Your agent API key (`ppk-<name>-<id>`), from `/api/agents/register`. |

## Tools

| Tool | What it does |
|---|---|
| `paypulse_fetch` | Budget-metered HTTP request to any upstream URL |
| `paypulse_budget` | Check remaining budget and recent call history |
| `paypulse_borrow` | Request a budget increase (auto-approves if under 50% threshold) |

---

## Claude Code

Add a `.mcp.json` file to your project root:

```json
{
  "mcpServers": {
    "paypulse": {
      "command": "bun",
      "args": ["/absolute/path/to/mcp/paypulse-mcp.ts"],
      "env": {
        "PAYPULSE_URL": "https://paypulse.cv",
        "PAYPULSE_AGENT_KEY": "ppk-myagent-abc123"
      }
    }
  }
}
```

Then in Claude Code:
```
/mcp
```
You'll see `paypulse` listed with 3 tools.

---

## Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "paypulse": {
      "command": "bun",
      "args": ["/absolute/path/to/mcp/paypulse-mcp.ts"],
      "env": {
        "PAYPULSE_URL": "https://paypulse.cv",
        "PAYPULSE_AGENT_KEY": "ppk-myagent-abc123"
      }
    }
  }
}
```

Restart Claude Desktop. The PayPulse tools appear in the tool picker.

---

## OpenCode

Edit `~/.config/opencode/config.json`:

```json
{
  "mcp": {
    "paypulse": {
      "command": "bun",
      "args": ["/absolute/path/to/mcp/paypulse-mcp.ts"],
      "environment": {
        "PAYPULSE_URL": "https://paypulse.cv",
        "PAYPULSE_AGENT_KEY": "ppk-myagent-abc123"
      }
    }
  }
}
```

---

## Cursor

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "paypulse": {
      "command": "bun",
      "args": ["/absolute/path/to/mcp/paypulse-mcp.ts"],
      "env": {
        "PAYPULSE_URL": "https://paypulse.cv",
        "PAYPULSE_AGENT_KEY": "ppk-myagent-abc123"
      }
    }
  }
}
```

---

## Example usage

Once connected, your agent can say:

> "Call the OpenAI API to summarize this document, using my PayPulse budget."

The agent will use `paypulse_fetch` with:
```json
{
  "upstreamUrl": "https://api.openai.com/v1/chat/completions",
  "method": "POST",
  "upstreamHeaders": { "Authorization": "Bearer sk-..." },
  "body": { "model": "gpt-4o-mini", "messages": [...] }
}
```

If the budget is exhausted, the tool returns:
```json
{
  "error": "Budget exhausted",
  "code": "BUDGET_EXHAUSTED",
  "remaining": "0",
  "hint": "Call paypulse_borrow to request more budget"
}
```

The agent can then call `paypulse_borrow` with a reason, which goes to the human approver queue in the PayPulse dashboard.

---

## How billing works

- Each call costs `CHARGE_PER_CALL` micro-USDC (set in the proxy config, default 1000 = $0.001)
- Draws are settled on-chain to the PayPulse contract after each call
- Budget periods reset automatically (hourly by default)
- Unspent budget returns to the pool on reset
