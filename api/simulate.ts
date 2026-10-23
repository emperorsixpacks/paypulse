import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store, addLog } from './_store.js'
import { publicClient, PAYPULSE_ABI, CONTRACT_ADDRESS, CHARGE_PER_CALL } from './_chain.js'

async function getAgentBudget(agentAddress: `0x${string}`) {
  if (!CONTRACT_ADDRESS) return null
  try {
    const info = await publicClient.readContract({
      address: CONTRACT_ADDRESS,
      abi: PAYPULSE_ABI,
      functionName: 'getAgentInfo',
      args: [agentAddress],
    })
    const allocation = info[3] as bigint
    const spent = info[4] as bigint
    return { allocation, spent, remaining: allocation > spent ? allocation - spent : 0n }
  } catch {
    return null
  }
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Agent-Key')

  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' })

  const body = req.body as { apiKey?: string; path?: string }
  const agent = store.agentRegistry.get(body.apiKey ?? '')
  if (!agent) return res.status(401).json({ error: 'unknown agent' })

  const budget = await getAgentBudget(agent.agentAddress as `0x${string}`)
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
        : 'No contract data (no VITE_PAYPULSE_ADDRESS set?)',
    })
    return res.status(402).json({
      error: 'Budget exceeded',
      code: 'PAYMENT_REQUIRED',
      remaining: budget?.remaining?.toString() ?? '0',
    })
  }

  store.pendingDraws.push({ agentAddress: agent.agentAddress, amount: charge })
  addLog({
    ts: Date.now(),
    agentAddress: agent.agentAddress,
    agentName: agent.name,
    path: body.path ?? '/api/call',
    status: 200,
    chargeUsdc: Number(charge),
    allowed: true,
  })

  return res.json({ ok: true, charged: charge.toString(), agent: agent.name })
}
