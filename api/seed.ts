import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store } from './_store.js'
import type { AgentRecord } from './_store.js'

export default function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Agent-Key')

  if (req.method === 'OPTIONS') return res.status(204).end()

  if (req.method === 'GET') {
    return res.json({ agents: Array.from(store.agentRegistry.values()) })
  }

  if (req.method === 'POST') {
    const body = req.body as AgentRecord[]
    if (!Array.isArray(body)) return res.status(400).json({ error: 'expected array' })
    for (const a of body) store.agentRegistry.set(a.apiKey, a)
    return res.json({ ok: true, count: store.agentRegistry.size })
  }

  return res.status(405).json({ error: 'method not allowed' })
}
