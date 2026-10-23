/**
 * POST /api/agents/create
 * Creates a Circle developer-controlled wallet for a new agent,
 * registers it with the proxy, and returns its on-chain address.
 *
 * Body: { name: string, allocationBps: number, periodLength: number, isLender?: boolean, maxLendBps?: number }
 * Requires CIRCLE_API_KEY + CIRCLE_ENTITY_SECRET in env.
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store } from '../_store.js'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' })

  const apiKey = process.env.CIRCLE_API_KEY
  const entitySecret = process.env.CIRCLE_ENTITY_SECRET ?? process.env.ENTITY_SECRET

  if (!apiKey || !entitySecret) {
    return res.status(503).json({
      error: 'Circle credentials not configured',
      hint: 'Set CIRCLE_API_KEY and CIRCLE_ENTITY_SECRET in Vercel environment variables',
    })
  }

  const body = req.body as {
    name: string
    allocationBps?: number
    periodLength?: number
    isLender?: boolean
    maxLendBps?: number
  }

  if (!body.name) return res.status(400).json({ error: 'name is required' })

  try {
    // Lazy-import so the module isn't bundled when creds are absent
    const { initiateDeveloperControlledWalletsClient } = await import('@circle-fin/developer-controlled-wallets')
    const sdk = initiateDeveloperControlledWalletsClient({ apiKey, entitySecret })

    // Ensure a wallet set exists (stored in global singleton)
    let walletSetId = (globalThis as Record<string, unknown>).__paypulse_wallet_set_id as string | undefined
    if (!walletSetId) {
      const wsRes = await sdk.createWalletSet({ name: 'PayPulse Agent Wallets' })
      walletSetId = wsRes.data?.walletSet?.id
      if (!walletSetId) throw new Error('Failed to create wallet set')
      ;(globalThis as Record<string, unknown>).__paypulse_wallet_set_id = walletSetId
    }

    // Create one EOA wallet on ARC-TESTNET
    const walletsRes = await sdk.createWallets({
      accountType: 'EOA',
      blockchains: ['ARC-TESTNET'],
      count: 1,
      walletSetId,
      metadata: [{ name: body.name, refId: `paypulse-agent-${Date.now()}` }],
    })

    const wallet = walletsRes.data?.wallets?.[0]
    if (!wallet?.address) throw new Error('Wallet creation returned no address')

    const apiKeyForAgent = `ppk-${body.name.toLowerCase().replace(/\s+/g, '-')}-${Date.now().toString(36)}`

    // Register with local proxy store
    store.agentRegistry.set(apiKeyForAgent, {
      agentAddress: wallet.address as `0x${string}`,
      name: body.name,
      apiKey: apiKeyForAgent,
    })

    return res.json({
      ok: true,
      agent: {
        name: body.name,
        address: wallet.address,
        walletId: wallet.id,
        apiKey: apiKeyForAgent,
        blockchain: 'ARC-TESTNET',
        allocationBps: body.allocationBps ?? 1000,
        periodLength: body.periodLength ?? 3600,
        isLender: body.isLender ?? false,
        maxLendBps: body.maxLendBps ?? 0,
      },
      note: 'Call addAgent() on the PayPulse contract with the returned address to activate the budget.',
    })
  } catch (e) {
    console.error('[agents/create]', e)
    return res.status(500).json({ error: 'wallet creation failed', detail: String(e) })
  }
}
