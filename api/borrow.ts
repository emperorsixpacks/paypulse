/**
 * POST /api/borrow
 * Agent-facing borrow request endpoint.
 * Calls requestBorrow() on the PayPulse contract on behalf of the agent.
 *
 * Body: { apiKey: string, amount: string, reason: string }
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store } from './_store'
import { CONTRACT_ADDRESS, getWalletClient, publicClient } from './_chain'
import { parseAbi } from 'viem'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
}

const BORROW_ABI = parseAbi([
  'function requestBorrow(address agentAddr, uint256 amount, string calldata reason) external',
])

export default async function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' })

  const body = req.body as { apiKey?: string; amount?: string; reason?: string }
  if (!body.apiKey || !body.amount || !body.reason) {
    return res.status(400).json({ error: 'apiKey, amount, and reason are required' })
  }

  const agent = store.agentRegistry.get(body.apiKey)
  if (!agent) return res.status(401).json({ error: 'unknown agent key' })

  if (!CONTRACT_ADDRESS) return res.status(503).json({ error: 'contract not configured' })

  const walletClient = getWalletClient()
  if (!walletClient) {
    return res.status(503).json({
      error: 'PROXY_PRIVATE_KEY not configured — borrow requests require a proxy wallet',
    })
  }

  try {
    const amount = BigInt(body.amount)
    const hash = await walletClient.writeContract({
      address: CONTRACT_ADDRESS,
      abi: BORROW_ABI,
      functionName: 'requestBorrow',
      args: [agent.agentAddress as `0x${string}`, amount, body.reason],
    })
    const receipt = await publicClient.waitForTransactionReceipt({ hash })
    return res.json({ ok: true, txHash: hash, blockNumber: receipt.blockNumber.toString() })
  } catch (e) {
    console.error('[borrow]', e)
    return res.status(500).json({ error: 'requestBorrow failed', detail: String(e) })
  }
}
