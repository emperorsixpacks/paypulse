/**
 * GET  /api/settle  — returns pending draws as unsigned calldata for the owner to sign
 * POST /api/settle  — marks draws as settled (called by dashboard after owner confirms tx)
 *
 * No private key on the server. The dashboard reads pending draws, the owner
 * signs draw() calls from their connected wallet, then POSTs to clear the queue.
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store } from './_store.js'
import { CONTRACT_ADDRESS, CHARGE_PER_CALL } from './_chain.js'

export function runSettle() {
  // Aggregate pending draws by agent
  const totals = new Map<string, bigint>()
  for (const d of store.pendingDraws) {
    totals.set(d.agentAddress, (totals.get(d.agentAddress) ?? 0n) + d.amount)
  }
  return Array.from(totals.entries()).map(([agent, amount]) => ({
    agent,
    amount: amount.toString(),
    contract: CONTRACT_ADDRESS,
  }))
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
  if (req.method === 'OPTIONS') return res.status(204).end()

  if (req.method === 'GET') {
    // Return pending draws for the owner to sign
    const pending = runSettle()
    return res.json({
      ok: true,
      pendingDraws: pending,
      totalPending: store.pendingDraws.length,
      chargePerCall: CHARGE_PER_CALL.toString(),
    })
  }

  if (req.method === 'POST') {
    // Owner confirmed the tx — clear the queue
    const count = store.pendingDraws.length
    store.pendingDraws.splice(0, count)
    return res.json({ ok: true, cleared: count })
  }

  return res.status(405).json({ error: 'method not allowed' })
}
