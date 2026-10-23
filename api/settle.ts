/**
 * Batch draw settler — called by Vercel Cron every 10 seconds.
 * Drains the pendingDraws queue and calls draw() on the PayPulse contract.
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store } from './_store.js'
import { PAYPULSE_ABI, CONTRACT_ADDRESS, getWalletClient } from './_chain.js'

export const config = { maxDuration: 30 }

export default async function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*')

  if (req.method === 'OPTIONS') return res.status(204).end()

  if (store.pendingDraws.length === 0) {
    return res.json({ ok: true, settled: 0, message: 'nothing to settle' })
  }

  const batch = store.pendingDraws.splice(0, store.pendingDraws.length)

  // Aggregate by agent address
  const totals = new Map<string, bigint>()
  for (const d of batch) {
    totals.set(d.agentAddress, (totals.get(d.agentAddress) ?? 0n) + d.amount)
  }

  const walletClient = getWalletClient()
  if (!walletClient || !CONTRACT_ADDRESS) {
    console.log(`[settle-sim] ${batch.length} draws simulated (no wallet/contract configured)`)
    return res.json({ ok: true, settled: batch.length, simulated: true })
  }

  const results: { agent: string; amount: string; tx?: string; error?: string }[] = []

  for (const [addr, total] of totals) {
    try {
      const hash = await walletClient.writeContract({
        address: CONTRACT_ADDRESS,
        abi: PAYPULSE_ABI,
        functionName: 'draw',
        args: [addr as `0x${string}`, total],
      })
      console.log(`[settle] ${addr}: ${total} — tx ${hash}`)
      results.push({ agent: addr, amount: total.toString(), tx: hash })
    } catch (e) {
      console.error(`[settle] FAILED ${addr}: ${total}`, e)
      results.push({ agent: addr, amount: total.toString(), error: String(e) })
    }
  }

  return res.json({ ok: true, settled: results.length, results })
}
