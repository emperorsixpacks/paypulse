import { useState } from 'react'
import { TreasuryHeader } from './components/TreasuryHeader'
import { TreasuryPanel } from './components/TreasuryPanel'
import { AgentGrid } from './components/AgentGrid'
import { AddAgentPanel } from './components/AddAgentPanel'
import { BorrowQueue } from './components/BorrowQueue'
import { UsageFeed } from './components/UsageFeed'
import { SimulatorPanel } from './components/SimulatorPanel'
import { SeedBanner } from './components/SeedBanner'
import { AdminPanel } from './components/AdminPanel'

type Tab = 'dashboard' | 'admin'

export default function App() {
  const [agentNames, setAgentNames] = useState<Record<string, string>>({})
  const [tab, setTab] = useState<Tab>('dashboard')

  function mergeNames(names: Record<string, string>) {
    setAgentNames((prev) => ({ ...prev, ...names }))
  }

  return (
    <div className="min-h-dvh" style={{ background: 'var(--bg-gradient)' }}>
      <TreasuryHeader />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">

        {/* Demo seed banner */}
        <SeedBanner onSeeded={mergeNames} />

        {/* Tab nav */}
        <div className="flex gap-1 p-1 rounded-xl bg-[var(--surface)] border border-[var(--border)] w-fit">
          {(['dashboard', 'admin'] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors"
              style={{
                background: tab === t ? 'var(--surface-strong)' : 'transparent',
                color: tab === t ? 'var(--ink)' : 'var(--subtle)',
              }}
            >
              {t}
            </button>
          ))}
        </div>

        {tab === 'dashboard' && (
          <>
            {/* Agent burn overview */}
            <AgentGrid nameOverrides={agentNames} />

            {/* Middle row: treasury + borrow queue */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left column */}
              <div className="space-y-6">
                <TreasuryPanel />
                <AddAgentPanel onAdded={() => {}} />
              </div>

              {/* Right column */}
              <div className="space-y-6">
                <BorrowQueue agentNames={agentNames} />
                <SimulatorPanel />
              </div>
            </div>

            {/* Live call feed */}
            <UsageFeed />
          </>
        )}

        {tab === 'admin' && (
          <div className="max-w-xl">
            <AdminPanel />
          </div>
        )}

        {/* Contract footer */}
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 flex flex-col sm:flex-row items-start sm:items-center gap-2 text-xs text-[var(--subtle)]">
          <span className="font-medium text-[var(--ink-2)]">PayPulse Contract</span>
          <span className="mono break-all">{import.meta.env.VITE_PAYPULSE_ADDRESS}</span>
          <a
            href={`https://explorer.testnet.arc.io/address/${import.meta.env.VITE_PAYPULSE_ADDRESS}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--accent)] hover:underline shrink-0 sm:ml-auto"
          >
            View on explorer →
          </a>
        </div>
      </main>
    </div>
  )
}
