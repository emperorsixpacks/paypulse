import { motion, AnimatePresence } from 'framer-motion'
import { useUsageFeed } from '../hooks/useUsage'
import { CheckCircle2, XCircle, Activity } from 'lucide-react'

export function UsageFeed() {
  const { log, error } = useUsageFeed()

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <div className="flex items-center gap-2 mb-4">
        <Activity size={16} className="text-[var(--accent)]" />
        <h2 className="display font-semibold text-[var(--ink)]">Live Calls</h2>
        <span className="ml-auto text-[10px] text-[var(--subtle)]">via metering proxy</span>
      </div>

      {error ? (
        <div className="text-xs text-[var(--subtle)] text-center py-4 space-y-1">
          <div>No activity yet — run the simulator to generate calls</div>
          <div className="text-[10px] opacity-60">API initializing on first request…</div>
        </div>
      ) : log.length === 0 ? (
        <div className="text-sm text-[var(--subtle)] text-center py-8">
          Waiting for calls… run the simulator to see activity
        </div>
      ) : (
        <div className="space-y-1.5 max-h-72 overflow-y-auto pr-1">
          <AnimatePresence initial={false}>
            {log.slice(0, 40).map((entry, i) => (
              <motion.div
                key={`${entry.ts}-${i}`}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-2.5 py-1.5 px-3 rounded-lg bg-[var(--surface-strong)] text-xs"
              >
                {entry.allowed ? (
                  <CheckCircle2 size={12} className="shrink-0" style={{ color: 'var(--success)' }} />
                ) : (
                  <XCircle size={12} className="shrink-0" style={{ color: 'var(--danger)' }} />
                )}
                <span className="font-medium text-[var(--ink-2)] shrink-0 w-20 truncate">
                  {entry.agentName}
                </span>
                <span className="mono text-[var(--subtle)] truncate flex-1">{entry.path}</span>
                <span
                  className="shrink-0 font-semibold"
                  style={{ color: entry.allowed ? 'var(--success)' : 'var(--danger)' }}
                >
                  {entry.allowed ? `$${(entry.chargeUsdc / 1e6).toFixed(4)}` : '402'}
                </span>
                <span className="shrink-0 text-[var(--subtle)]">
                  {new Date(entry.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  )
}
