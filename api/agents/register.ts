/**
 * POST /api/agents/register
 * Register an existing wallet address with the PayPulse proxy.
 * This is the required step between "I have an address" and "I can use the proxy".
 *
 * Body: { address: string, name: string }
 * Auth: X-Admin-Key header required
 *
 * Returns: { ok: true, apiKey: string }
 * The apiKey is what the agent passes as X-Agent-Key on every proxy call.
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { requireAdminKey } from '../_auth'
import { store } from '../_store'
import { isAddress } from 'viem'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Admin-Key, Authorization',
}

function generateApiKey(name: string): string {
  const slug = name.toLowerCase().replace(/[^a-z0-9]/g, '-').slice(0, 16)
  const rand = Math.random().toString(36).slice(2, 8)
  return `ppk-${slug}-${rand}`
}

export default function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' })
  if (requireAdminKey(req, res)) return

  const body = req.body as { address?: string; name?: string }

  if (!body.address || !body.name) {
    return res.status(400).json({ error: 'address and name are required' })
  }

  if (!isAddress(body.address)) {
    return res.status(400).json({ error: 'address must be a valid EVM address' })
  }

  // Check if already registered — return existing key
  for (const [key, agent] of store.agentRegistry.entries()) {
    if (agent.agentAddress.toLowerCase() === body.address.toLowerCase()) {
      return res.json({
        ok: true,
        apiKey: key,
        name: agent.name,
        address: agent.agentAddress,
        note: 'agent already registered — returning existing key',
      })
    }
  }

  const apiKey = generateApiKey(body.name)
  store.agentRegistry.set(apiKey, {
    apiKey,
    name: body.name,
    agentAddress: body.address,
    walletId: '',
    createdAt: Date.now(),
  })

  return res.json({
    ok: true,
    apiKey,
    name: body.name,
    address: body.address,
  })
}
