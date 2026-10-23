/**
 * GET|POST /api/proxy/[...path]
 * x402-style metering proxy.
 *
 * Flow per request:
 *  1. Authenticate agent via X-Agent-Key header.
 *  2. Read remaining budget from PayPulse contract.
 *  3. If budget < CHARGE_PER_CALL → 402 Payment Required.
 *  4. Queue a draw() call (settled async by /api/settle cron).
 *  5. Forward request to upstream (httpbin.org for demo).
 *  6. Return upstream response with X-Charge-USDC header.
 *
 * For production: replace httpbin.org with real upstream APIs.
 * Set PROXY_PRIVATE_KEY to enable onchain draw() settlement.
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store, addLog } from '../_store.js'
import { publicClient, CONTRACT_ADDRESS, PAYPULSE_ABI, CHARGE_PER_CALL } from '../_chain.js'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Agent-Key',
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()

  const apiKey = req.headers['x-agent-key'] as string | undefined
  if (!apiKey) {
    return res.status(401).json({
      error: 'Missing X-Agent-Key header',
      hint: 'Include your agent API key: X-Agent-Key: ppk-<name>-<id>',
    })
  }

  const agent = store.agentRegistry.get(apiKey)
  if (!agent) {
    return res.status(401).json({ error: 'Unknown agent key' })
  }

  // Reconstruct path
  const pathParam = req.query['path']
  const upstreamPath = Array.isArray(pathParam) ? '/' + pathParam.join('/') : '/' + (pathParam ?? '')

  // Check on-chain budget
  let remaining = 0n
  if (CONTRACT_ADDRESS) {
    try {
      const info = await publicClient.readContract({
        address: CONTRACT_ADDRESS,
        abi: PAYPULSE_ABI,
        functionName: 'getAgentInfo',
        args: [agent.agentAddress as `0x${string}`],
      })
      const allocation = (info as readonly bigint[])[3]
      const spent = (info as readonly bigint[])[4]
      remaining = allocation > spent ? allocation - spent : 0n
    } catch {
      // RPC error — allow through in degraded mode but log it
      console.warn('[proxy] budget check failed, allowing request in degraded mode')
    }
  }

  if (CONTRACT_ADDRESS && remaining < CHARGE_PER_CALL) {
    addLog({
      ts: Date.now(),
      agentAddress: agent.agentAddress,
      agentName: agent.name,
      path: upstreamPath,
      status: 402,
      chargeUsdc: 0,
      allowed: false,
      rejectReason: `Budget exhausted: ${remaining} remaining, need ${CHARGE_PER_CALL}`,
    })

    // x402-compliant response
    return res.status(402).json({
      error: 'Payment Required',
      code: 'BUDGET_EXHAUSTED',
      x402Version: 1,
      accepts: [
        {
          scheme: 'exact',
          network: 'arc-testnet',
          maxAmountRequired: CHARGE_PER_CALL.toString(),
          resource: req.url ?? '/api/proxy',
          description: 'PayPulse budget draw required',
          mimeType: 'application/json',
          payTo: CONTRACT_ADDRESS,
          maxTimeoutSeconds: 30,
          asset: '0x3600000000000000000000000000000000000000',
          extra: { agentAddress: agent.agentAddress },
        },
      ],
      remaining: remaining.toString(),
      hint: 'Request a borrow via POST /api/borrow or wait for your period to reset.',
    })
  }

  // Forward to demo upstream (httpbin.org)
  let upstreamBody = JSON.stringify({ ok: true, agent: agent.name, path: upstreamPath })
  let upstreamStatus = 200
  try {
    const up = await fetch(`https://httpbin.org${upstreamPath}`, {
      method: req.method ?? 'GET',
      headers: { 'Content-Type': 'application/json' },
    })
    upstreamStatus = up.status
    upstreamBody = await up.text()
  } catch {
    upstreamBody = JSON.stringify({ ok: true, demo: true, path: upstreamPath, agent: agent.name })
  }

  // Queue draw for next batch settle
  store.pendingDraws.push({ agentAddress: agent.agentAddress, amount: CHARGE_PER_CALL })

  addLog({
    ts: Date.now(),
    agentAddress: agent.agentAddress,
    agentName: agent.name,
    path: upstreamPath,
    status: upstreamStatus,
    chargeUsdc: Number(CHARGE_PER_CALL),
    allowed: true,
  })

  res.setHeader('X-Charge-USDC', CHARGE_PER_CALL.toString())
  res.setHeader('X-Agent-Name', agent.name)
  res.setHeader('Content-Type', 'application/json')
  return res.status(upstreamStatus).send(upstreamBody)
}
