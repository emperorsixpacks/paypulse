/**
 * Shared in-memory store for Vercel serverless functions.
 * Uses a global singleton so state survives warm invocations on the
 * same Lambda instance. Resets on cold start (fine for demo).
 */

export interface AgentRecord {
  agentAddress: string
  name: string
  apiKey: string
}

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

export interface PendingDraw {
  agentAddress: string
  amount: bigint
}

interface Store {
  agentRegistry: Map<string, AgentRecord>
  usageLog: UsageEntry[]
  pendingDraws: PendingDraw[]
}

const g = globalThis as typeof globalThis & { __paypulse_store?: Store }

if (!g.__paypulse_store) {
  g.__paypulse_store = {
    agentRegistry: new Map(),
    usageLog: [],
    pendingDraws: [],
  }
}

export const store = g.__paypulse_store

export function addLog(entry: UsageEntry) {
  store.usageLog.push(entry)
  if (store.usageLog.length > 500) store.usageLog.shift()
}
