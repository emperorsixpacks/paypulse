/**
 * POST /api/borrow
 * Returns unsigned calldata for a requestBorrow() transaction.
 * The agent signs and submits the transaction from their own wallet.
 *
 * Body: { apiKey: string, amount: string, reason: string }
 * Response: { calldata, to, agent, amount } — agent signs this with their wallet
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store } from './_store.js'
import { CONTRACT_ADDRESS, PAYPULSE_ABI } from './_chain.js'
import { encodeFunctionData } from 'viem'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Agent-Key',
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' })

  const apiKey = (req.headers['x-agent-key'] as string) ?? (req.body as Record<string, string>)?.apiKey
  const body = req.body as { amount?: string; reason?: string }

  if (!apiKey || !body.amount || !body.reason) {
    return res.status(400).json({ error: 'X-Agent-Key header (or apiKey), amount, and reason are required' })
  }

  const agent = store.agentRegistry.get(apiKey)
  if (!agent) return res.status(401).json({ error: 'unknown agent key' })

  if (!CONTRACT_ADDRESS) return res.status(503).json({ error: 'contract not configured' })

  const amount = BigInt(body.amount)

  // Return unsigned calldata — the agent signs from their own wallet
  const calldata = encodeFunctionData({
    abi: PAYPULSE_ABI,
    functionName: 'requestBorrow',
    args: [agent.agentAddress as `0x${string}`, amount, body.reason],
  })

  return res.json({
    ok: true,
    to: CONTRACT_ADDRESS,
    calldata,
    agent: agent.agentAddress,
    amount: amount.toString(),
    reason: body.reason,
    hint: 'Sign and submit this transaction from your agent wallet to request a budget increase.',
  })
}
