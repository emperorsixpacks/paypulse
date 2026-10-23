/**
 * PayPulse Metering Proxy
 *
 * Agents call APIs through this proxy using an agent API key.
 * On each request: check remaining budget, reject 402 if over cap,
 * forward the request, meter usage, and queue a draw for onchain settlement.
 *
 * Draw calls are batched and settled onchain every 10 seconds.
 */

import { createPublicClient, createWalletClient, http, parseAbi, type Hex } from 'viem'
import { privateKeyToAccount } from 'viem/accounts'
import { arcTestnet } from './chain.js'

const PORT = 3001

// ---------------------------------------------------------------------------
// Config — all addresses from environment, never literals
// ---------------------------------------------------------------------------
const CONTRACT_ADDRESS = (process.env.VITE_PAYPULSE_ADDRESS || '') as Hex
const PROXY_PRIVATE_KEY = (process.env.PROXY_PRIVATE_KEY || '') as Hex

// Cost per proxied call: 0.001 USDC (6 decimals)
const CHARGE_PER_CALL = 1_000n

// ---------------------------------------------------------------------------
// PayPulse ABI (subset needed by proxy)
// ---------------------------------------------------------------------------
const PAYPULSE_ABI = parseAbi([
  'function draw(address agent, uint256 amount) external',
  'function getAgentInfo(address agentAddr) external view returns (uint256 allocationBps, uint256 periodStart, uint256 periodLength, uint256 allocation, uint256 spent, bool isLender, uint256 maxLendBps, bool active)',
])

// ---------------------------------------------------------------------------
// Viem clients
// ---------------------------------------------------------------------------
const transport = http(arcTestnet.rpcUrls.default.http[0])
const publicClient = createPublicClient({ chain: arcTestnet, transport })

let walletClient: ReturnType<typeof createWalletClient> | null = null
if (PROXY_PRIVATE_KEY && PROXY_PRIVATE_KEY.startsWith('0x') && PROXY_PRIVATE_KEY.length >= 66) {
  const account = privateKeyToAccount(PROXY_PRIVATE_KEY)
  walletClient = createWalletClient({ account, chain: arcTestnet, transport })
  console.log(`[PayPulse Proxy] wallet ready: ${account.address}`)
} else {
  console.warn('[PayPulse Proxy] PROXY_PRIVATE_KEY not set — draw() calls will be simulated')
}

// ---------------------------------------------------------------------------
// Agent registry (keyed by API key)
// ---------------------------------------------------------------------------
export interface AgentRecord {
  agentAddress: Hex
  name: string
  apiKey: string
}

const agentRegistry = new Map<string, AgentRecord>()

// ---------------------------------------------------------------------------
// Usage log (ring buffer)
// ---------------------------------------------------------------------------
export interface UsageEntry {
  ts: number
  agentAddress: Hex
  agentName: string
  path: string
  status: number
  chargeUsdc: number
  allowed: boolean
  rejectReason?: string
}

const usageLog: UsageEntry[] = []
const MAX_LOG = 500

function addLog(entry: UsageEntry) {
  usageLog.push(entry)
  if (usageLog.length > MAX_LOG) usageLog.shift()
}

// ---------------------------------------------------------------------------
// Pending draws — batched onchain settlement
// ---------------------------------------------------------------------------
interface PendingDraw {
  agentAddress: Hex
  amount: bigint
}
const pendingDraws: PendingDraw[] = []

async function settleDrawOnchain(agentAddress: Hex, amount: bigint): Promise<boolean> {
  if (!walletClient || !CONTRACT_ADDRESS) {
    console.log(`[settle-sim] ${agentAddress}: ${amount} (simulated, no wallet/contract)`)
    return true
  }
  try {
    const hash = await walletClient.writeContract({
      address: CONTRACT_ADDRESS,
      abi: PAYPULSE_ABI,
      functionName: 'draw',
      args: [agentAddress, amount],
    })
    console.log(`[settle] ${agentAddress}: ${amount} micro-USDC — tx ${hash}`)
    return true
  } catch (e) {
    console.error(`[settle] FAILED ${agentAddress}: ${amount}`, e)
    return false
  }
}

setInterval(async () => {
  if (pendingDraws.length === 0) return
  const batch = pendingDraws.splice(0, pendingDraws.length)
  const totals = new Map<Hex, bigint>()
  for (const d of batch) {
    totals.set(d.agentAddress, (totals.get(d.agentAddress) ?? 0n) + d.amount)
  }
  for (const [addr, total] of totals) {
    await settleDrawOnchain(addr, total)
  }
}, 10_000)

// ---------------------------------------------------------------------------
// Budget helper
// ---------------------------------------------------------------------------
async function getAgentBudget(agentAddress: Hex) {
  if (!CONTRACT_ADDRESS) return null
  try {
    const info = await publicClient.readContract({
      address: CONTRACT_ADDRESS,
      abi: PAYPULSE_ABI,
      functionName: 'getAgentInfo',
      args: [agentAddress],
    })
    return {
      allocation: info[3],
      spent: info[4],
      remaining: info[3] > info[4] ? info[3] - info[4] : 0n,
    }
  } catch {
    return null
  }
}

// ---------------------------------------------------------------------------
// HTTP server
// ---------------------------------------------------------------------------
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Agent-Key',
}

const server = Bun.serve({
  port: PORT,

  async fetch(req) {
    const url = new URL(req.url)

    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS })

    // GET /api/usage — dashboard polling
    if (url.pathname === '/api/usage' && req.method === 'GET') {
      return Response.json({ log: usageLog.slice(-100).reverse() }, { headers: CORS })
    }

    // GET /api/agents
    if (url.pathname === '/api/agents' && req.method === 'GET') {
      return Response.json({ agents: Array.from(agentRegistry.values()) }, { headers: CORS })
    }

    // POST /api/seed — register demo agents
    if (url.pathname === '/api/seed' && req.method === 'POST') {
      const body = (await req.json()) as AgentRecord[]
      for (const a of body) agentRegistry.set(a.apiKey, a)
      return Response.json({ ok: true, count: agentRegistry.size }, { headers: CORS })
    }

    // GET /api/budget/:address
    if (url.pathname.startsWith('/api/budget/')) {
      const addr = url.pathname.split('/').at(-1) as Hex
      const budget = await getAgentBudget(addr)
      if (!budget) return Response.json({ error: 'not found' }, { status: 404, headers: CORS })
      return Response.json(
        {
          allocation: budget.allocation.toString(),
          spent: budget.spent.toString(),
          remaining: budget.remaining.toString(),
        },
        { headers: CORS },
      )
    }

    // POST /api/simulate — simulator endpoint for fake API calls
    if (url.pathname === '/api/simulate' && req.method === 'POST') {
      const body = (await req.json()) as { apiKey: string; path?: string }
      const agent = agentRegistry.get(body.apiKey)
      if (!agent)
        return Response.json({ error: 'unknown agent' }, { status: 401, headers: CORS })

      const budget = await getAgentBudget(agent.agentAddress)
      const charge = CHARGE_PER_CALL

      if (!budget || budget.remaining < charge) {
        addLog({
          ts: Date.now(),
          agentAddress: agent.agentAddress,
          agentName: agent.name,
          path: body.path ?? '/api/call',
          status: 402,
          chargeUsdc: 0,
          allowed: false,
          rejectReason: budget
            ? `Exhausted: ${budget.remaining} < ${charge}`
            : 'No contract data',
        })
        return Response.json(
          { error: 'Budget exceeded', code: 'PAYMENT_REQUIRED', remaining: budget?.remaining?.toString() ?? '0' },
          { status: 402, headers: CORS },
        )
      }

      pendingDraws.push({ agentAddress: agent.agentAddress, amount: charge })
      addLog({
        ts: Date.now(),
        agentAddress: agent.agentAddress,
        agentName: agent.name,
        path: body.path ?? '/api/call',
        status: 200,
        chargeUsdc: Number(charge),
        allowed: true,
      })
      return Response.json(
        { ok: true, charged: charge.toString(), agent: agent.name },
        { headers: CORS },
      )
    }

    // Proxy route: /proxy/* — forward to demo httpbin
    if (url.pathname.startsWith('/proxy/')) {
      const apiKey = req.headers.get('X-Agent-Key') ?? ''
      const agent = agentRegistry.get(apiKey)
      if (!agent)
        return Response.json({ error: 'Unknown agent key' }, { status: 401, headers: CORS })

      const budget = await getAgentBudget(agent.agentAddress)
      const charge = CHARGE_PER_CALL

      if (!budget || budget.remaining < charge) {
        addLog({
          ts: Date.now(),
          agentAddress: agent.agentAddress,
          agentName: agent.name,
          path: url.pathname,
          status: 402,
          chargeUsdc: 0,
          allowed: false,
          rejectReason: 'Budget exceeded',
        })
        return Response.json(
          { error: 'Budget exceeded', code: 'PAYMENT_REQUIRED' },
          { status: 402, headers: CORS },
        )
      }

      const fwPath = url.pathname.replace('/proxy', '')
      let upstreamBody = '{"ok":true}'
      let upstreamStatus = 200
      try {
        const up = await fetch(`https://httpbin.org${fwPath}`)
        upstreamStatus = up.status
        upstreamBody = await up.text()
      } catch {
        upstreamBody = JSON.stringify({ error: 'upstream unreachable' })
        upstreamStatus = 503
      }

      pendingDraws.push({ agentAddress: agent.agentAddress, amount: charge })
      addLog({
        ts: Date.now(),
        agentAddress: agent.agentAddress,
        agentName: agent.name,
        path: url.pathname,
        status: upstreamStatus,
        chargeUsdc: Number(charge),
        allowed: true,
      })

      return new Response(upstreamBody, {
        status: upstreamStatus,
        headers: { ...CORS, 'Content-Type': 'application/json', 'X-Charge-USDC': charge.toString() },
      })
    }

    return Response.json({ service: 'PayPulse Metering Proxy', ok: true }, { headers: CORS })
  },
})

console.log(`[PayPulse Proxy] http://localhost:${PORT}`)
export default server
