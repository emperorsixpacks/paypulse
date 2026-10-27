/**
 * GET /api/agents/list
 * Returns all agents registered with the proxy (name, address, createdAt).
 * Does NOT return API keys.
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store } from '../_store'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
}

export default function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'GET') return res.status(405).json({ error: 'method not allowed' })

  const agents = Array.from(store.agentRegistry.values()).map(({ name, agentAddress, createdAt }) => ({
    name,
    address: agentAddress,
    createdAt,
  }))

  return res.json({ ok: true, agents })
}
