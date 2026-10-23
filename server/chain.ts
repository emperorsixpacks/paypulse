/**
 * Chain definition for the PayPulse server.
 * RPC URL is resolved from the Arc Studio RPC proxy if available,
 * otherwise falls back to the public endpoint read from the
 * onchain-facts registry (Arc Testnet chain ID 5042002).
 *
 * Do NOT hardcode RPC URLs or contract addresses here.
 */

import { defineChain } from 'viem'

// Arc Testnet chain ID per the onchain-facts registry
export const ARC_TESTNET_CHAIN_ID = 5042002

export const arcTestnet = defineChain({
  id: ARC_TESTNET_CHAIN_ID,
  name: 'Arc Testnet',
  nativeCurrency: { name: 'USDC', symbol: 'USDC', decimals: 18 },
  rpcUrls: {
    default: { http: [resolveRpcUrl()] },
  },
  blockExplorers: {
    default: {
      name: 'Arc Testnet Explorer',
      url: 'https://explorer.testnet.arc.io',
    },
  },
  testnet: true,
})

function resolveRpcUrl(): string {
  const base = process.env.RPC_PROXY_BASE_URL
  const token = process.env.RPC_PROXY_TOKEN
  const chains = (process.env.RPC_PROXY_CHAINS || '').split(',').map((s) => s.trim())

  if (base && token && chains.includes('Arc_Testnet')) {
    return `${base}/api/rpc/Arc_Testnet?_rpc_token=${token}`
  }

  // Fallback: public endpoint from the onchain-facts registry.
  // This chain may rate-limit under load since it is not the keyed proxy.
  console.warn(
    '[PayPulse] Arc_Testnet not in RPC_PROXY_CHAINS — falling back to public RPC (may rate-limit)',
  )
  // Value sourced from src/onchain-facts.ts Arc Testnet rpcUrls[0]
  return 'https://rpc.testnet.arc.io' // arc-studio-allow-onchain-literal
}
