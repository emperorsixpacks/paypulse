/**
 * GET /api/agents/status
 * Self-check endpoint for agents. Returns registration state + onchain budget in one call.
 * Authenticate with X-Agent-Key header.
 *
 * Response:
 *   { registered: true, name, address, allocation, spent, remaining, periodEndsIn }
 *   { registered: false } — not registered, call /api/agents/register first
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store } from '../_store'
import { publicClient, CONTRACT_ADDRESS, PAYPULSE_ABI } from '../_chain'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Agent-Key',
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'GET') return res.status(405).json({ error: 'method not allowed' })

  const apiKey = req.headers['x-agent-key'] as string | undefined
  if (!apiKey) {
    return res.status(401).json({
      error: 'Missing X-Agent-Key header',
      hint: 'Include your agent API key: X-Agent-Key: ppk-<name>-<id>',
    })
  }

  const agent = store.agentRegistry.get(apiKey)
  if (!agent) {
    return res.status(404).json({
      registered: false,
      hint: 'Register first via POST /api/agents/register',
    })
  }

  // Fetch onchain budget
  let allocation = '0', spent = '0', remaining = '0', periodEndsIn = 'unknown'

  if (CONTRACT_ADDRESS) {
    try {
      const info = await publicClient.readContract({
        address: CONTRACT_ADDRESS,
        abi: PAYPULSE_ABI,
        functionName: 'getAgentInfo',
        args: [agent.agentAddress as `0x${string}`],
      }) as readonly [bigint, bigint, bigint, bigint, bigint, boolean, bigint, boolean]

      const [allocationBps, periodStart, periodLength, alloc, sp] = info
      allocation = alloc.toString()
      spent = sp.toString()
      remaining = alloc > sp ? (alloc - sp).toString() : '0'

      const periodEnd = Number(periodStart) + Number(periodLength)
      const now = Math.floor(Date.now() / 1000)
      periodEndsIn = periodEnd > now ? `${periodEnd - now}s` : 'reset pending'

      void allocationBps // used in contract but not exposed here
    } catch {
      // RPC error — return partial data
    }
  }

  return res.json({
    registered: true,
    name: agent.name,
    address: agent.agentAddress,
    allocation,
    spent,
    remaining,
    periodEndsIn,
    contractAddress: CONTRACT_ADDRESS ?? null,
    hint: allocation === '0'
      ? 'Budget is zero — ask your operator to call addAgent() on the contract or fund via the dashboard'
      : undefined,
  })
}
