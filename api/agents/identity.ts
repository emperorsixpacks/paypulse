/**
 * POST /api/agents/identity
 * Builds the ERC-8004 registration URI and returns unsigned calldata.
 * The agent signs and submits register() from their own wallet.
 *
 * Body: { agentAddress: string, name: string, description?: string, proxyBaseUrl?: string }
 * Response: { calldata, to, agentUri, registrationFile }
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { requireAdminKey } from '../_auth.js'
import { encodeFunctionData, parseAbi } from 'viem'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
}

const REGISTRY_ABI = parseAbi([
  'function register(string calldata agentURI) external returns (uint256)',
])

export default async function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' })
  if (requireAdminKey(req, res)) return

  const IDENTITY_REGISTRY = process.env.VITE_IDENTITY_REGISTRY as `0x${string}` | undefined
  if (!IDENTITY_REGISTRY) {
    return res.status(503).json({
      error: 'VITE_IDENTITY_REGISTRY not configured',
      hint: 'Set VITE_IDENTITY_REGISTRY in Vercel environment variables.',
    })
  }

  const body = req.body as {
    agentAddress?: string
    name?: string
    description?: string
    proxyBaseUrl?: string
  }
  if (!body.agentAddress || !body.name) {
    return res.status(400).json({ error: 'agentAddress and name are required' })
  }

  const baseUrl = body.proxyBaseUrl ?? process.env.VITE_APP_URL ?? 'https://paypulse.cv'

  const registrationFile = {
    type: 'https://eips.ethereum.org/EIPS/eip-8004#registration-v1',
    name: body.name,
    description: body.description ?? `PayPulse budget-metered agent: ${body.name}`,
    services: [
      { name: 'web', endpoint: baseUrl },
      { name: 'proxy', endpoint: `${baseUrl}/proxy`, version: '1.0' },
    ],
    x402Support: true,
    active: true,
    agentAddress: body.agentAddress,
    paypulseContract: process.env.VITE_PAYPULSE_ADDRESS ?? '',
  }

  const agentUri =
    'data:application/json;base64,' +
    Buffer.from(JSON.stringify(registrationFile)).toString('base64')

  const calldata = encodeFunctionData({
    abi: REGISTRY_ABI,
    functionName: 'register',
    args: [agentUri],
  })

  return res.json({
    ok: true,
    to: IDENTITY_REGISTRY,
    calldata,
    agentUri,
    registrationFile,
    hint: 'Sign and submit this transaction from your agent wallet to register its ERC-8004 identity.',
  })
}
