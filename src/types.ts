export interface AgentInfo {
  address: string
  name: string
  allocationBps: bigint
  periodStart: bigint
  periodLength: bigint
  allocation: bigint
  spent: bigint
  isLender: boolean
  maxLendBps: bigint
  active: boolean
}

export interface BorrowRequest {
  id: bigint
  agent: string
  amount: bigint
  reason: string
  status: 0 | 1 | 2 // Pending | Approved | Rejected
  approvals: bigint
  rejections: bigint
}

export type BorrowStatus = 'Pending' | 'Approved' | 'Rejected'

export interface UsageEntry {
  ts: number
  agentAddress: string
  agentName: string
  path: string
  status: number
  chargeUsdc: number
  allowed: boolean
  rejectReason?: string
}

export const AGENT_NAMES: Record<string, string> = {}
