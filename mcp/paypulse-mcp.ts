#!/usr/bin/env node
/**
 * PayPulse MCP Server v2
 * ──────────────────────
 * Exposes PayPulse budget-metered HTTP calls as MCP tools.
 * Works with Claude Code, Claude Desktop, OpenCode, Cursor, Continue,
 * or any MCP-compatible agent.
 *
 * Every call through this server is:
 *  1. Authenticated with your agent API key
 *  2. Budget-checked on-chain against your PayPulse allocation
 *  3. Forwarded to the real upstream API if budget is available
 *  4. Charged against your allocation (draw settled on-chain)
 *  5. Returned transparently to the calling agent
 *
 * SETUP
 * ─────
 * 1. Register your agent at https://paypulse.cv/api/agents/register
 *    (or via the PayPulse dashboard Add Agent panel)
 *    → you get a ppk-<name>-<id> API key
 *
 * 2. Set env vars:
 *      PAYPULSE_URL=https://paypulse.cv
 *      PAYPULSE_AGENT_KEY=ppk-myagent-abc123
 *
 * 3. Run:  bun run mcp/paypulse-mcp.ts
 *
 * CONFIG for Claude Desktop
 * ─────────────────────────
 * ~/Library/Application Support/Claude/claude_desktop_config.json:
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
 *
 * CONFIG for Claude Code (.mcp.json in project root)
 * ───────────────────────────────────────────────────
 * {
 *   "mcpServers": {
 *     "paypulse": {
 *       "command": "bun",
 *       "args": ["./mcp/paypulse-mcp.ts"],
 *       "env": {
 *         "PAYPULSE_URL": "https://paypulse.cv",
 *         "PAYPULSE_AGENT_KEY": "ppk-myagent-abc123"
 *       }
 *     }
 *   }
 * }
 *
 * CONFIG for OpenCode (~/.config/opencode/config.json)
 * ─────────────────────────────────────────────────────
 * {
 *   "mcp": {
 *     "paypulse": {
 *       "command": "bun",
 *       "args": ["/absolute/path/to/mcp/paypulse-mcp.ts"],
 *       "environment": {
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
  console.error('[paypulse-mcp] ERROR: PAYPULSE_AGENT_KEY is not set.')
  console.error('[paypulse-mcp] Get a key at: ' + BASE + '/docs')
  process.exit(1)
}

// ── proxy helper ──────────────────────────────────────────────────────────────

async function proxyRequest(
  upstreamUrl: string,
  method: string,
  upstreamHeaders: Record<string, string>,
  body?: unknown,
): Promise<{ status: number; data: unknown; charged?: string; remaining?: string }> {
  const res = await fetch(`${BASE}/api/proxy`, {
    method: method.toUpperCase(),
    headers: {
      'Content-Type': 'application/json',
      'X-Agent-Key': AGENT_KEY,
      'X-Upstream-URL': upstreamUrl,
      ...(Object.keys(upstreamHeaders).length > 0
        ? { 'X-Upstream-Headers': JSON.stringify(upstreamHeaders) }
        : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  const charged = res.headers.get('X-Charge-USDC') ?? undefined
  const remaining = res.headers.get('X-PayPulse-Remaining') ?? undefined

  let data: unknown
  const ct = res.headers.get('content-type') ?? ''
  try {
    data = ct.includes('application/json') ? await res.json() : await res.text()
  } catch {
    data = await res.text()
  }

  return { status: res.status, data, charged, remaining }
}

async function getBudget(agentAddress?: string): Promise<unknown> {
  const url = agentAddress
    ? `${BASE}/api/budget/${agentAddress}`
    : `${BASE}/api/usage`
  const res = await fetch(url, { headers: { 'X-Agent-Key': AGENT_KEY } })
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
    name: 'paypulse_fetch',
    description:
      'Make a budget-metered HTTP request to any upstream API through the PayPulse proxy. ' +
      'The request is authenticated, budget-checked on-chain, forwarded to the real API, ' +
      'and charged against your allocation. Returns the upstream response. ' +
      'If budget is exhausted, returns a 402 with remaining balance — use paypulse_borrow to get more.',
    inputSchema: {
      type: 'object' as const,
      properties: {
        upstreamUrl: {
          type: 'string',
          description: 'The full URL of the real API to call. E.g. "https://api.openai.com/v1/chat/completions"',
        },
        method: {
          type: 'string',
          enum: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
          description: 'HTTP method. Defaults to GET.',
        },
        upstreamHeaders: {
          type: 'object',
          description: 'Headers to forward to the upstream API (e.g. Authorization). Do NOT include X-Agent-Key here.',
          additionalProperties: { type: 'string' },
        },
        body: {
          type: 'object',
          description: 'JSON body for POST/PUT/PATCH requests.',
        },
      },
      required: ['upstreamUrl'],
    },
  },
  {
    name: 'paypulse_budget',
    description:
      'Check your current PayPulse budget: allocation, amount spent, and remaining balance for this period. ' +
      'Also shows recent call history. Use this before making expensive calls to confirm you have budget.',
    inputSchema: {
      type: 'object' as const,
      properties: {
        agentAddress: {
          type: 'string',
          description: 'Optional: on-chain wallet address of the agent to check. If omitted, returns recent usage log.',
        },
      },
    },
  },
  {
    name: 'paypulse_borrow',
    description:
      'Request a budget increase from the PayPulse treasury. ' +
      'Amounts under 50% of your current allocation auto-approve immediately if the pool has funds. ' +
      'Larger requests enter the 2-of-3 human approver queue (visible in the dashboard). ' +
      'Use this when paypulse_fetch returns a 402.',
    inputSchema: {
      type: 'object' as const,
      properties: {
        amount: {
          type: 'string',
          description: 'Amount in micro-USDC (6 decimals). "1000000" = 1 USDC, "500000" = 0.50 USDC.',
        },
        reason: {
          type: 'string',
          description: 'Why you need the extra budget. This is shown to human approvers in the dashboard.',
        },
      },
      required: ['amount', 'reason'],
    },
  },
]

// ── server ────────────────────────────────────────────────────────────────────

const server = new Server(
  { name: 'paypulse', version: '2.0.0' },
  { capabilities: { tools: {} } },
)

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }))

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params
  const a = (args ?? {}) as Record<string, unknown>

  try {
    let result: unknown

    switch (name) {
      case 'paypulse_fetch': {
        const upstreamUrl = String(a.upstreamUrl)
        const method = String(a.method ?? 'GET')
        const upstreamHeaders = (a.upstreamHeaders ?? {}) as Record<string, string>
        const body = a.body

        const r = await proxyRequest(upstreamUrl, method, upstreamHeaders, body)

        if (r.status === 402) {
          result = {
            error: 'Budget exhausted',
            code: 'BUDGET_EXHAUSTED',
            remaining: r.remaining ?? '0',
            hint: 'Call paypulse_borrow to request more budget',
            detail: r.data,
          }
        } else {
          result = {
            status: r.status,
            charged_usdc: r.charged ? (Number(r.charged) / 1e6).toFixed(6) + ' USDC' : undefined,
            remaining_usdc: r.remaining ? (Number(r.remaining) / 1e6).toFixed(6) + ' USDC' : undefined,
            data: r.data,
          }
        }
        break
      }

      case 'paypulse_budget':
        result = await getBudget(a.agentAddress ? String(a.agentAddress) : undefined)
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

  } catch (err) {
    return {
      content: [{ type: 'text', text: `Error: ${String(err)}` }],
      isError: true,
    }
  }
})

// ── start ─────────────────────────────────────────────────────────────────────

const transport = new StdioServerTransport()
await server.connect(transport)
console.error(`[paypulse-mcp] v2 ready — key: ${AGENT_KEY.slice(0, 12)}… → ${BASE}`)
