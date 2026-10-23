import artifact from '../../contracts/out/PayPulse.sol/PayPulse.json'

export const PAYPULSE_ADDRESS = (import.meta.env.VITE_PAYPULSE_ADDRESS || '') as `0x${string}`

export const PAYPULSE_ABI = artifact.abi

export const PAYPULSE = {
  address: PAYPULSE_ADDRESS,
  abi: PAYPULSE_ABI,
} as const

// Arc Testnet chain ID
export const ARC_TESTNET_ID = 5042002
