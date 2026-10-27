/**
 * Viem client for Arc Testnet — shared across Vercel API functions.
 * Chain facts are inlined here (verified from Arc Studio onchain-facts registry this session).
 * RPC URL prefers the proxy env vars when available, falls back to the public endpoint.
 */
import { createPublicClient, createWalletClient, http, parseAbi } from 'viem'
import { privateKeyToAccount } from 'viem/accounts'

// Arc Testnet — verified from onchain-facts registry: chainId=5042002, rpcUrls[0] verified
const ARC_TESTNET_CHAIN_ID = 5042002
const ARC_TESTNET_RPC_PUBLIC = 'https://rpc.testnet.arc.io' // arc-studio-allow-onchain-literal

// Prefer the RPC proxy when available (Arc Studio sandbox); fall back to the public endpoint.
const proxyChains = (process.env.RPC_PROXY_CHAINS ?? '').split(',')
const RPC_URL =
  process.env.RPC_PROXY_BASE_URL && proxyChains.includes('Arc_Testnet')
    ? `${process.env.RPC_PROXY_BASE_URL}/api/rpc/Arc_Testnet?_rpc_token=${process.env.RPC_PROXY_TOKEN}`
    : ARC_TESTNET_RPC_PUBLIC

export const arcTestnetChain = {
  id: ARC_TESTNET_CHAIN_ID,
  name: 'Arc Testnet',
  nativeCurrency: { name: 'USDC', symbol: 'USDC', decimals: 18 },
  rpcUrls: { default: { http: [RPC_URL] } },
} as const

const transport = http(RPC_URL)

export const publicClient = createPublicClient({ chain: arcTestnetChain, transport })

export const PAYPULSE_ABI = parseAbi([
  'function draw(address agent, uint256 amount) external',
  'function disburse(address to, uint256 amount) external',
  'function requestBorrow(address agentAddr, uint256 amount, string calldata reason) external',
  'function getAgentInfo(address agentAddr) external view returns (uint256 allocationBps, uint256 periodStart, uint256 periodLength, uint256 allocation, uint256 spent, bool isLender, uint256 maxLendBps, bool active)',
  'function poolBalance() external view returns (uint256)',
  'function proxy() external view returns (address)',
  'function getAgentList() external view returns (address[])',
  'function borrowRequestCount() external view returns (uint256)',
  'function getPendingRequests() external view returns (uint256[])',
  'function getBorrowRequest(uint256 id) external view returns (uint256, address, uint256, string, uint8, uint256, uint256)',
])

export const CONTRACT_ADDRESS = (process.env.VITE_PAYPULSE_ADDRESS ?? '') as `0x${string}`

// Cost per proxied call: 0.001 USDC (1000 micro-USDC, 6 decimals)
export const CHARGE_PER_CALL = 1_000n

export function getWalletClient() {
  const pk = process.env.PROXY_PRIVATE_KEY ?? ''
  if (!pk || !pk.startsWith('0x') || pk.length < 66) return null
  const account = privateKeyToAccount(pk as `0x${string}`)
  return createWalletClient({ account, chain: arcTestnetChain, transport })
}
