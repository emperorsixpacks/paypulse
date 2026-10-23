/**
 * POST /api/agents/identity
 * Registers an agent in the Arc ERC-8004 identity registry and returns its agentId.
 *
 * Body: { agentAddress: string, name: string, description?: string, proxyBaseUrl?: string }
 *
 * The registration file is built as a data:application/json;base64 URI (fully on-chain, no IPFS needed).
 * PROXY_PRIVATE_KEY signs the registry.register() call.
 * VITE_IDENTITY_REGISTRY holds the ERC-8004 registry address on Arc Testnet.
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { createWalletClient, createPublicClient, http, parseAbi } from 'viem'
import { privateKeyToAccount } from 'viem/accounts'
import { requireChain } from '../../src/onchain-facts.js'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
}

const REGISTRY_ABI = parseAbi([
  'function register(string calldata agentURI) external returns (uint256)',
  'function tokenOfOwnerByIndex(address owner, uint256 index) external view returns (uint256)',
  'function balanceOf(address owner) external view returns (uint256)',
])

export default async function handler(req: VercelRequest, res: VercelResponse) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v))
  if (req.method === 'OPTIONS') return res.status(204).end()
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' })

  const pk = process.env.PROXY_PRIVATE_KEY ?? ''
  if (!pk || !pk.startsWith('0x') || pk.length < 66) {
    return res.status(503).json({
      error: 'PROXY_PRIVATE_KEY not configured',
      hint: 'Set PROXY_PRIVATE_KEY in Vercel environment variables.',
    })
  }

  const IDENTITY_REGISTRY = process.env.VITE_IDENTITY_REGISTRY as `0x${string}` | undefined
  if (!IDENTITY_REGISTRY) {
    return res.status(503).json({
      error: 'VITE_IDENTITY_REGISTRY not configured',
      hint: 'Set VITE_IDENTITY_REGISTRY in Vercel environment variables.',
    })
  }

  const body = req.body as {
    agentAddress: string
    name: string
    description?: string
    proxyBaseUrl?: string
  }
  if (!body.agentAddress || !body.name) {
    return res.status(400).json({ error: 'agentAddress and name are required' })
  }

  const ARC_TESTNET_ID = 1313161560
  const chainFact = requireChain(ARC_TESTNET_ID)
  const proxyChains = (process.env.RPC_PROXY_CHAINS ?? '').split(',')
  const rpcUrl =
    process.env.RPC_PROXY_BASE_URL && proxyChains.includes('Arc_Testnet')
      ? `${process.env.RPC_PROXY_BASE_URL}/api/rpc/Arc_Testnet?_rpc_token=${process.env.RPC_PROXY_TOKEN}`
      : chainFact.rpcUrls[0]

  const chain = {
    id: chainFact.chainId,
    name: chainFact.name,
    nativeCurrency: { name: 'USDC', symbol: 'USDC', decimals: chainFact.nativeCurrency.decimals },
    rpcUrls: { default: { http: [rpcUrl] } },
  } as const

  const transport = http(rpcUrl)
  const account = privateKeyToAccount(pk as `0x${string}`)
  const walletClient = createWalletClient({ account, chain, transport })
  const publicClient = createPublicClient({ chain, transport })

  const baseUrl = body.proxyBaseUrl ?? process.env.VITE_APP_URL ?? 'https://your-deploy.vercel.app'

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

  try {
    const hash = await walletClient.writeContract({
      address: IDENTITY_REGISTRY,
      abi: REGISTRY_ABI,
      functionName: 'register',
      args: [agentUri],
    })

    const receipt = await publicClient.waitForTransactionReceipt({ hash })

    // Read back the token id just minted
    const balance = await publicClient.readContract({
      address: IDENTITY_REGISTRY,
      abi: REGISTRY_ABI,
      functionName: 'balanceOf',
      args: [account.address],
    })

    let agentId: bigint | null = null
    if ((balance as bigint) > 0n) {
      agentId = (await publicClient.readContract({
        address: IDENTITY_REGISTRY,
        abi: REGISTRY_ABI,
        functionName: 'tokenOfOwnerByIndex',
        args: [account.address, (balance as bigint) - 1n],
      })) as bigint
    }

    return res.json({
      ok: true,
      agentId: agentId?.toString() ?? null,
      registryAddress: IDENTITY_REGISTRY,
      txHash: hash,
      blockNumber: receipt.blockNumber.toString(),
      registrationFile,
    })
  } catch (e) {
    console.error('[agents/identity]', e)
    return res.status(500).json({ error: 'identity registration failed', detail: String(e) })
  }
}
