import type { VercelRequest, VercelResponse } from '@vercel/node'
import { publicClient, PAYPULSE_ABI, CONTRACT_ADDRESS } from '../_chain'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'GET') return res.status(405).json({ error: 'method not allowed' })

  const addr = req.query['address'] as string
  if (!addr || !addr.startsWith('0x')) return res.status(400).json({ error: 'invalid address' })

  if (!CONTRACT_ADDRESS) return res.status(503).json({ error: 'contract not configured' })

  try {
    const info = await publicClient.readContract({
      address: CONTRACT_ADDRESS,
      abi: PAYPULSE_ABI,
      functionName: 'getAgentInfo',
      args: [addr as `0x${string}`],
    })
    const allocation = info[3] as bigint
    const spent = info[4] as bigint
    return res.json({
      allocation: allocation.toString(),
      spent: spent.toString(),
      remaining: (allocation > spent ? allocation - spent : 0n).toString(),
    })
  } catch (e) {
    return res.status(404).json({ error: 'agent not found or RPC error', detail: String(e) })
  }
}
