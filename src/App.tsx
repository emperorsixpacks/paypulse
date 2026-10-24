import { Routes, Route, NavLink } from 'react-router-dom'
import { TreasuryHeader } from './components/TreasuryHeader'
import { TreasuryPanel } from './components/TreasuryPanel'
import { AgentGrid } from './components/AgentGrid'
import { AddAgentPanel } from './components/AddAgentPanel'
import { BorrowQueue } from './components/BorrowQueue'
import { UsageFeed } from './components/UsageFeed'
import { AdminPanel } from './components/AdminPanel'
import { DocsPage } from './components/DocsPage'

const NAV_LINKS = [
  { to: '/', label: 'Dashboard' },
  { to: '/admin', label: 'Admin' },
  { to: '/docs', label: 'Docs' },
]

export default function App() {
  return (
    <div className="min-h-dvh" style={{ background: 'var(--bg-gradient)' }}>
      <TreasuryHeader />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">

        {/* Tab nav */}
        <div
          className="flex gap-0.5 p-1 rounded-xl w-fit"
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid var(--border)',
          }}
        >
          {NAV_LINKS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `relative px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'text-[var(--ink)]'
                    : 'text-[var(--subtle)] hover:text-[var(--muted)]'
                }`
              }
              style={({ isActive }) =>
                isActive
                  ? {
                      background: 'rgba(172,198,233,0.12)',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.06)',
                      border: '1px solid rgba(172,198,233,0.2)',
                    }
                  : {}
              }
            >
              {label}
            </NavLink>
          ))}
        </div>

        <Routes>
          {/* Dashboard */}
          <Route
            path="/"
            element={
              <>
                <AgentGrid nameOverrides={{}} />
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-6">
                    <TreasuryPanel />
                    <AddAgentPanel onAdded={() => {}} />
                  </div>
                  <div className="space-y-6">
                    <BorrowQueue agentNames={{}} />
                    <UsageFeed />
                  </div>
                </div>
              </>
            }
          />

          {/* Admin */}
          <Route
            path="/admin"
            element={
              <div className="max-w-xl">
                <AdminPanel />
              </div>
            }
          />

          {/* Docs */}
          <Route path="/docs" element={<DocsPage />} />
        </Routes>

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
