/**
 * Viem client for Arc Testnet — shared across API functions.
 * RPC URL is read from onchain-facts (never typed literally).
 */
import { createPublicClient, createWalletClient, http, parseAbi } from 'viem'
import { privateKeyToAccount } from 'viem/accounts'
import { requireChain } from '../src/onchain-facts.js'

const ARC_TESTNET_ID = 1313161560

const chainFact = requireChain(ARC_TESTNET_ID)

// Prefer the RPC proxy when available, fall back to the registry URL.
const proxyChains = (process.env.RPC_PROXY_CHAINS ?? '').split(',')
const RPC_URL =
  process.env.RPC_PROXY_BASE_URL && proxyChains.includes('Arc_Testnet')
    ? `${process.env.RPC_PROXY_BASE_URL}/api/rpc/Arc_Testnet?_rpc_token=${process.env.RPC_PROXY_TOKEN}`
    : chainFact.rpcUrls[0]

export const arcTestnetChain = {
  id: chainFact.chainId,
  name: chainFact.name,
  nativeCurrency: { name: 'USDC', symbol: 'USDC', decimals: chainFact.nativeCurrency.decimals },
  rpcUrls: { default: { http: [RPC_URL] } },
} as const

const transport = http(RPC_URL)

export const publicClient = createPublicClient({ chain: arcTestnetChain, transport })

export const PAYPULSE_ABI = parseAbi([
  'function draw(address agent, uint256 amount) external',
  'function getAgentInfo(address agentAddr) external view returns (uint256 allocationBps, uint256 periodStart, uint256 periodLength, uint256 allocation, uint256 spent, bool isLender, uint256 maxLendBps, bool active)',
])

export const CONTRACT_ADDRESS = (process.env.VITE_PAYPULSE_ADDRESS ?? '') as `0x${string}`

// Cost per proxied call: 0.001 USDC (6 decimals)
export const CHARGE_PER_CALL = 1_000n

export function getWalletClient() {
  const pk = process.env.PROXY_PRIVATE_KEY ?? ''
  if (!pk || !pk.startsWith('0x') || pk.length < 66) return null
  const account = privateKeyToAccount(pk as `0x${string}`)
  return createWalletClient({ account, chain: arcTestnetChain, transport })
}
