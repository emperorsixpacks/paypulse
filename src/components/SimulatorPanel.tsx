import { useState, useRef } from 'react'
import { toast } from 'sonner'
import { Play, Square, Zap } from 'lucide-react'

// These must match the deterministic addresses in SeedBanner
const DEMO_AGENT_ADDRESSES: Record<string, `0x${string}`> = {
  Research: '0x1111111111111111111111111111111111111111',
  Scraper:  '0x2222222222222222222222222222222222222222',
  Support:  '0x3333333333333333333333333333333333333333',
}

// Demo agent API keys (seeded from the simulator seed step)
const DEMO_AGENTS = [
  { key: 'ppk-research-001', name: 'Research', path: '/get?agent=research' },
  { key: 'ppk-scraper-001', name: 'Scraper', path: '/post?agent=scraper' },
  { key: 'ppk-support-001', name: 'Support', path: '/get?agent=support' },
]

interface SimState {
  running: boolean
  calls: number
  rejected: number
}

export function SimulatorPanel() {
  const [sim, setSim] = useState<SimState>({ running: false, calls: 0, rejected: 0 })
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const callCountRef = useRef(0)

  async function seedAgents() {
    try {
      const res = await fetch('/api/seed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(
          DEMO_AGENTS.map((a) => ({
            apiKey: a.key,
            name: a.name,
            agentAddress: DEMO_AGENT_ADDRESSES[a.name],
          })),
        ),
      })
      if (!res.ok) throw new Error(`seed failed: ${res.status}`)
      toast.success('Demo agents registered with proxy')
    } catch (e) {
      toast.error(String(e))
    }
  }

  async function fireCall() {
    callCountRef.current++
    // Round-robin across agents; make support hit cap faster by calling twice as often
    const weights = [1, 1, 2]
    const totalWeight = weights.reduce((a, b) => a + b, 0)
    let pick = callCountRef.current % totalWeight
    let agentIdx = 0
    for (let i = 0; i < weights.length; i++) {
      if (pick < weights[i]) { agentIdx = i; break }
      pick -= weights[i]
    }
    const agent = DEMO_AGENTS[agentIdx]

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey: agent.key, path: agent.path }),
      })
      await res.json()
      setSim((s) => ({
        ...s,
        calls: s.calls + 1,
        rejected: s.rejected + (res.status === 402 ? 1 : 0),
      }))

      if (res.status === 402) {
        toast.error(`${agent.name} hit budget cap — 402`, { duration: 3000 })
      }
    } catch {
      // ignore network errors from background sim
    }
  }

  function startSim() {
    if (intervalRef.current) return
    setSim((s) => ({ ...s, running: true }))
    intervalRef.current = setInterval(() => { void fireCall() }, 600)
  }

  function stopSim() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setSim((s) => ({ ...s, running: false }))
  }

  async function runBorrowScenario() {
    toast('Firing borrow scenario…')
    // Fire rapid calls to exhaust support agent, then request a borrow
    for (let i = 0; i < 8; i++) {
      await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey: 'ppk-support-001', path: '/get?scenario=exhaust' }),
      })
    }
    toast.success('Support agent exhausted — check Live Calls for 402s')
  }

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <div className="flex items-center gap-2 mb-4">
        <Zap size={16} className="text-[var(--accent)]" />
        <h2 className="display font-semibold text-[var(--ink)]">Demo Simulator</h2>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <StatChip label="Calls fired" value={sim.calls.toString()} />
        <StatChip label="Rejected (402)" value={sim.rejected.toString()} color="var(--danger)" />
      </div>

      <div className="space-y-2">
        <button
          onClick={() => { void seedAgents() }}
          className="w-full py-2.5 rounded-xl text-sm font-semibold border border-[var(--border)] text-[var(--ink-2)] hover:bg-[var(--surface-strong)] transition-colors"
        >
          1. Register demo agents with proxy
        </button>

        <div className="flex gap-2">
          <button
            onClick={sim.running ? stopSim : startSim}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-colors"
            style={{
              background: sim.running ? 'rgba(232,109,122,0.15)' : 'var(--accent)',
              color: sim.running ? 'var(--danger)' : '#0d1b2f',
            }}
          >
            {sim.running ? <><Square size={14} /> Stop</> : <><Play size={14} /> 2. Start traffic</>}
          </button>
        </div>

        <button
          onClick={() => { void runBorrowScenario() }}
          className="w-full py-2.5 rounded-xl text-sm font-semibold border border-[var(--border)] text-[var(--ink-2)] hover:bg-[var(--surface-strong)] transition-colors"
        >
          3. Exhaust Support agent (triggers 402)
        </button>
      </div>

      <div className="mt-4 p-3 rounded-xl bg-[var(--surface-strong)] text-[11px] text-[var(--subtle)] leading-relaxed">
        <strong className="text-[var(--ink-2)]">Flow:</strong> Research 40% · Scraper 30% · Support 30%.
        Step 3 exhausts Support, causing 402s. Use the contract to request a borrow — small ones auto-approve,
        large ones appear in the Borrow Queue above for 2-of-3 human approval.
      </div>
    </div>
  )
}

function StatChip({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded-xl bg-[var(--surface-strong)] px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-[var(--subtle)]">{label}</div>
      <div
        className="display font-semibold text-lg tabular-nums mt-0.5"
        style={{ color: color ?? 'var(--ink)' }}
      >
        {value}
      </div>
    </div>
  )
}
