#!/usr/bin/env node
/**
 * PayPulse MCP Server
 * ───────────────────
 * Exposes PayPulse budget-metered API calls as MCP tools.
 * Any MCP-compatible agent (Claude Desktop, Cursor, Continue, etc.)
 * can use this server to make HTTP calls through the PayPulse proxy,
 * check remaining budget, and request borrows — all onchain-enforced.
 *
 * Setup:
 *   1. Install: bun add @modelcontextprotocol/sdk
 *   2. Set env vars:
 *        PAYPULSE_URL=https://paypulse.cv   (or your Vercel URL)
 *        PAYPULSE_AGENT_KEY=ppk-myagent-abc123
 *   3. Run: bun run mcp/paypulse-mcp.ts
 *
 * Claude Desktop config (~/Library/Application Support/Claude/claude_desktop_config.json):
 * {
 *   "mcpServers": {
 *     "paypulse": {
 *       "command": "bun",
 *       "args": ["/absolute/path/to/mcp/paypulse-mcp.ts"],
 *       "env": {
 *         "PAYPULSE_URL": "https://paypulse.cv",
 *         "PAYPULSE_AGENT_KEY": "ppk-myagent-abc123"
 *       }
 *     }
 *   }
 * }
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  type Tool,
} from '@modelcontextprotocol/sdk/types.js'

const BASE = (process.env.PAYPULSE_URL ?? 'https://paypulse.cv').replace(/\/$/, '')
const AGENT_KEY = process.env.PAYPULSE_AGENT_KEY ?? ''

if (!AGENT_KEY) {
  console.error('[paypulse-mcp] PAYPULSE_AGENT_KEY is not set. Exiting.')
  process.exit(1)
}

// ── helpers ──────────────────────────────────────────────────────────────────

async function proxyCall(path: string, method = 'GET', body?: unknown): Promise<unknown> {
  const url = `${BASE}/api/proxy${path.startsWith('/') ? path : '/' + path}`
  const res = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-Agent-Key': AGENT_KEY,
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  const json = await res.json()
  if (res.status === 402) {
    return { __paypulse_402: true, remaining: (json as Record<string, unknown>).remaining, detail: json }
  }
  return json
}

async function getBudget(): Promise<unknown> {
  // Budget check is done inline by the proxy — we expose it via the dedicated endpoint
  const res = await fetch(`${BASE}/api/usage`, {
    headers: { 'X-Agent-Key': AGENT_KEY },
  })
  return res.json()
}

async function requestBorrow(amount: string, reason: string): Promise<unknown> {
  const res = await fetch(`${BASE}/api/borrow`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ apiKey: AGENT_KEY, amount, reason }),
  })
  return res.json()
}

// ── tool definitions ──────────────────────────────────────────────────────────

const TOOLS: Tool[] = [
  {
    name: 'paypulse_call',
    description:
      'Make a budget-metered HTTP GET call through the PayPulse proxy. ' +
      'Returns the upstream response. If budget is exhausted, returns a 402 object with remaining balance. ' +
      'Use paypulse_borrow to request more budget.',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'URL path to call on the proxy (e.g. "/get?q=hello" for httpbin GET)',
        },
      },
      required: ['path'],
    },
  },
  {
    name: 'paypulse_post',
    description:
      'Make a budget-metered HTTP POST call through the PayPulse proxy with a JSON body.',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'URL path on the proxy' },
        body: { type: 'object', description: 'JSON body to POST' },
      },
      required: ['path', 'body'],
    },
  },
  {
    name: 'paypulse_usage',
    description: 'Get the recent call history for this agent from the PayPulse proxy.',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'paypulse_borrow',
    description:
      'Request a budget increase from the PayPulse treasury. ' +
      'Auto-approves if amount is under 50% of current allocation and pool has funds. ' +
      'Larger requests enter the 2-of-3 human approver queue.',
    inputSchema: {
      type: 'object',
      properties: {
        amount: {
          type: 'string',
          description: 'Amount in micro-USDC (6 decimals). E.g. "1000000" = 1 USDC.',
        },
        reason: {
          type: 'string',
          description: 'Why you need the extra budget. Shown to human approvers.',
        },
      },
      required: ['amount', 'reason'],
    },
  },
]

// ── server ────────────────────────────────────────────────────────────────────

const server = new Server(
  { name: 'paypulse', version: '1.0.0' },
  { capabilities: { tools: {} } },
)

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }))

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params
  const a = (args ?? {}) as Record<string, unknown>

  let result: unknown

  switch (name) {
    case 'paypulse_call':
      result = await proxyCall(String(a.path), 'GET')
      break
    case 'paypulse_post':
      result = await proxyCall(String(a.path), 'POST', a.body)
      break
    case 'paypulse_usage':
      result = await getBudget()
      break
    case 'paypulse_borrow':
      result = await requestBorrow(String(a.amount), String(a.reason))
      break
    default:
      return {
        content: [{ type: 'text', text: `Unknown tool: ${name}` }],
        isError: true,
      }
  }

  const text = typeof result === 'string' ? result : JSON.stringify(result, null, 2)
  return { content: [{ type: 'text', text }] }
})

// ── start ─────────────────────────────────────────────────────────────────────

const transport = new StdioServerTransport()
await server.connect(transport)
console.error(`[paypulse-mcp] Connected — agent key: ${AGENT_KEY.slice(0, 12)}…`)
