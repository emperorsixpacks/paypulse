import { useReadContract, useReadContracts } from 'wagmi'
import type { Abi } from 'viem'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'
import type { AgentInfo, BorrowRequest } from '../types'

export function usePoolBalance() {
  return useReadContract({
    ...PAYPULSE,
    functionName: 'poolBalance',
    chainId: ARC_TESTNET_ID,
    query: { refetchInterval: 5000 },
  })
}

export function useTotalHeld() {
  return useReadContract({
    ...PAYPULSE,
    functionName: 'totalHeld',
    chainId: ARC_TESTNET_ID,
    query: { refetchInterval: 5000 },
  })
}

export function useAgentList() {
  return useReadContract({
    ...PAYPULSE,
    functionName: 'getAgentList',
    chainId: ARC_TESTNET_ID,
    query: { refetchInterval: 5000 },
  })
}

export function useAgentInfo(address: `0x${string}` | undefined) {
  return useReadContract({
    ...PAYPULSE,
    functionName: 'getAgentInfo',
    args: address ? [address] : undefined,
    chainId: ARC_TESTNET_ID,
    query: { enabled: !!address, refetchInterval: 4000 },
  })
}

export function useAgents(addresses: `0x${string}`[]): AgentInfo[] {
  const contracts = addresses.map((addr) => ({
    address: PAYPULSE.address,
    abi: PAYPULSE.abi as Abi,
    functionName: 'getAgentInfo' as const,
    args: [addr] as [`0x${string}`],
    chainId: ARC_TESTNET_ID,
  }))

  const { data } = useReadContracts({
    contracts,
    query: { enabled: addresses.length > 0, refetchInterval: 4000 },
  })

  if (!data) return []
  return addresses
    .map((addr, i) => {
      const r = data[i]
      if (r.status !== 'success' || !r.result) return null
      const [allocationBps, periodStart, periodLength, allocation, spent, isLender, maxLendBps, active] = r.result as [bigint, bigint, bigint, bigint, bigint, boolean, bigint, boolean]
      return { address: addr, name: '', allocationBps, periodStart, periodLength, allocation, spent, isLender, maxLendBps, active }
    })
    .filter(Boolean) as AgentInfo[]
}

export function usePendingRequests() {
  return useReadContract({
    ...PAYPULSE,
    functionName: 'getPendingRequests',
    chainId: ARC_TESTNET_ID,
    query: { refetchInterval: 4000 },
  })
}

export function useBorrowRequest(id: bigint | undefined): BorrowRequest | null {
  const { data } = useReadContract({
    ...PAYPULSE,
    functionName: 'getBorrowRequest',
    args: id !== undefined ? [id] : undefined,
    chainId: ARC_TESTNET_ID,
    query: { enabled: id !== undefined, refetchInterval: 3000 },
  })

  if (!data) return null
  const [rid, agent, amount, reason, status, approvals, rejections] = data as [bigint, string, bigint, string, number, bigint, bigint]
  return { id: rid, agent, amount, reason, status: status as 0 | 1 | 2, approvals, rejections }
}

export function useApproverList() {
  return useReadContract({
    ...PAYPULSE,
    functionName: 'getApproverList',
    chainId: ARC_TESTNET_ID,
    query: { refetchInterval: 10000 },
  })
}
