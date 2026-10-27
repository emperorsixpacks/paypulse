/**
 * GET|POST|PUT|DELETE /api/proxy/[...path]
 * Budget-metering proxy. Forwards to any upstream URL the agent specifies.
 *
 * Required headers:
 *   X-Agent-Key: ppk-<name>-<id>       — agent identity + budget auth
 *   X-Upstream-URL: https://api.example.com/endpoint  — where to actually send the request
 *
 * Optional:
 *   X-Upstream-Headers: {"Authorization":"Bearer xyz"}  — extra headers to forward upstream (JSON)
 *
 * Flow:
 *  1. Authenticate agent via X-Agent-Key.
 *  2. Check remaining on-chain budget. Reject 402 if exhausted.
 *  3. Forward the request to X-Upstream-URL with original method/body/headers.
 *  4. Queue a draw() for settlement, return upstream response.
 *
 * Usage:
 *   curl -X GET "https://paypulse.cv/api/proxy" \
 *     -H "X-Agent-Key: ppk-research-abc123" \
 *     -H "X-Upstream-URL: https://api.openai.com/v1/models" \
 *     -H "X-Upstream-Headers: {\"Authorization\":\"Bearer sk-...\"}"
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { store, addLog } from '../_store.js'
import { publicClient, CONTRACT_ADDRESS, PAYPULSE_ABI, CHARGE_PER_CALL } from '../_chain.js'
import { runSettle } from '../settle.js'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Agent-Key, X-Upstream-URL, X-Upstream-Headers',
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()

  // 1. Auth
  const apiKey = req.headers['x-agent-key'] as string | undefined
  if (!apiKey) {
    return res.status(401).json({
      error: 'Missing X-Agent-Key header',
      hint: 'Register your agent at POST /api/agents/register to get a key',
    })
  }
  const agent = store.agentRegistry.get(apiKey)
  if (!agent) {
    return res.status(401).json({
      error: 'Unknown agent key',
      hint: 'Register your agent at POST /api/agents/register',
    })
  }

  // 2. Upstream URL
  const upstreamUrl = req.headers['x-upstream-url'] as string | undefined
  if (!upstreamUrl) {
    return res.status(400).json({
      error: 'Missing X-Upstream-URL header',
      hint: 'Set X-Upstream-URL to the full URL you want to call, e.g. https://api.openai.com/v1/chat/completions',
    })
  }
  let parsedUrl: URL
  try {
    parsedUrl = new URL(upstreamUrl)
  } catch {
    return res.status(400).json({ error: 'X-Upstream-URL is not a valid URL' })
  }

  // 3. Check on-chain budget
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
      console.warn('[proxy] budget RPC check failed — allowing in degraded mode')
      remaining = CHARGE_PER_CALL // allow through if RPC is down
    }
  } else {
    remaining = CHARGE_PER_CALL // no contract configured — simulation mode
  }

  if (CONTRACT_ADDRESS && remaining < CHARGE_PER_CALL) {
    addLog({
      ts: Date.now(),
      agentAddress: agent.agentAddress,
      agentName: agent.name,
      path: parsedUrl.hostname + parsedUrl.pathname,
      status: 402,
      chargeUsdc: 0,
      allowed: false,
      rejectReason: `Budget exhausted: ${remaining} remaining, need ${CHARGE_PER_CALL}`,
    })
    return res.status(402).json({
      error: 'Payment Required',
      code: 'BUDGET_EXHAUSTED',
      x402Version: 1,
      remaining: remaining.toString(),
      hint: 'POST /api/borrow with your apiKey to request more budget, or wait for your period to reset.',
      accepts: [{
        scheme: 'exact',
        network: 'arc-testnet',
        maxAmountRequired: CHARGE_PER_CALL.toString(),
        resource: upstreamUrl,
        description: 'PayPulse budget draw',
        mimeType: 'application/json',
        payTo: CONTRACT_ADDRESS,
        maxTimeoutSeconds: 30,
        asset: '0x3600000000000000000000000000000000000000',
        extra: { agentAddress: agent.agentAddress },
      }],
    })
  }

  // 4. Forward to upstream
  const extraHeaders: Record<string, string> = {}
  const xUpstreamHeaders = req.headers['x-upstream-headers'] as string | undefined
  if (xUpstreamHeaders) {
    try {
      Object.assign(extraHeaders, JSON.parse(xUpstreamHeaders))
    } catch {
      return res.status(400).json({ error: 'X-Upstream-Headers must be valid JSON' })
    }
  }

  // Pass through original Content-Type and body
  const forwardHeaders: Record<string, string> = {
    'Content-Type': (req.headers['content-type'] as string) || 'application/json',
    'User-Agent': 'PayPulse-Proxy/1.0',
    ...extraHeaders,
  }

  // Strip PayPulse-specific headers
  delete forwardHeaders['x-agent-key']
  delete forwardHeaders['x-upstream-url']
  delete forwardHeaders['x-upstream-headers']

  let upstreamStatus = 200
  let upstreamBody = ''
  let upstreamContentType = 'application/json'

  try {
    const upRes = await fetch(parsedUrl.toString(), {
      method: req.method ?? 'GET',
      headers: forwardHeaders,
      body: req.method !== 'GET' && req.method !== 'HEAD'
        ? JSON.stringify(req.body)
        : undefined,
    })
    upstreamStatus = upRes.status
    upstreamBody = await upRes.text()
    upstreamContentType = upRes.headers.get('content-type') ?? 'application/json'
  } catch (e) {
    return res.status(502).json({
      error: 'Upstream request failed',
      upstream: parsedUrl.hostname,
      detail: String(e),
    })
  }

  // 5. Queue draw and settle inline
  store.pendingDraws.push({ agentAddress: agent.agentAddress, amount: CHARGE_PER_CALL })
  addLog({
    ts: Date.now(),
    agentAddress: agent.agentAddress,
    agentName: agent.name,
    path: parsedUrl.hostname + parsedUrl.pathname,
    status: upstreamStatus,
    chargeUsdc: Number(CHARGE_PER_CALL),
    allowed: true,
  })
  void runSettle().catch((e) => console.error('[proxy] inline settle failed', e))

  res.setHeader('X-Charge-USDC', CHARGE_PER_CALL.toString())
  res.setHeader('X-Agent-Name', agent.name)
  res.setHeader('X-PayPulse-Remaining', (remaining - CHARGE_PER_CALL).toString())
  res.setHeader('Content-Type', upstreamContentType)
  return res.status(upstreamStatus).send(upstreamBody)
}
