import { useUsageFeed } from '../hooks/useUsage'
import type { UsageEntry } from '../types'
import { Activity, AlertCircle, CheckCircle2 } from 'lucide-react'

function UsageRow({ entry }: { entry: UsageEntry }) {
  const time = new Date(entry.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <div className={`flex items-center gap-3 py-2 px-3 rounded-lg text-xs transition-colors ${entry.allowed ? 'hover:bg-white/5' : 'bg-[var(--danger)]/5'}`}>
      {entry.allowed ? (
        <CheckCircle2 size={12} className="text-[var(--success)] shrink-0" />
      ) : (
        <AlertCircle size={12} className="text-[var(--danger)] shrink-0" />
      )}

      <span className="mono text-[var(--subtle)] w-20 shrink-0 tabular-nums">{time}</span>

      <span
        className="w-16 shrink-0 font-medium truncate"
        style={{ color: entry.allowed ? 'var(--success)' : 'var(--danger)' }}
      >
        {entry.agentName || entry.agentAddress.slice(0, 8)}
      </span>

      <span className="text-[var(--muted)] flex-1 truncate">{entry.path}</span>

      {entry.allowed ? (
        <span className="mono text-[var(--subtle)] shrink-0">
          ${(entry.chargeUsdc / 1_000_000).toFixed(6)}
        </span>
      ) : (
        <span className="mono text-[var(--danger)] shrink-0 text-[10px]">
          {entry.status === 402 ? '402' : 'ERR'}
        </span>
      )}
    </div>
  )
}

export function ActivityFeed() {
  const { log, error } = useUsageFeed()

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 space-y-3">
      <div className="flex items-center gap-2 mb-1">
        <Activity size={15} className="text-[var(--accent)]" />
        <h3 className="display font-semibold text-[var(--ink)] text-sm">Live API Activity</h3>
        <span className="ml-auto text-[10px] text-[var(--subtle)]">{log.length} entries</span>
        <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)] animate-pulse" />
      </div>

      {error && (
        <div className="text-xs text-[var(--danger)] bg-[var(--danger)]/10 rounded-lg px-3 py-2">
          Proxy offline — start the server with <span className="mono">bun run server</span>
        </div>
      )}

      <div className="space-y-0.5 max-h-72 overflow-y-auto">
        {log.length === 0 && !error ? (
          <div className="text-center py-8 text-[var(--subtle)] text-xs">
            No calls yet — run the simulator to generate activity
          </div>
        ) : (
          log.map((entry, i) => <UsageRow key={i} entry={entry} />)
        )}
      </div>

      <div className="flex gap-3 pt-1 border-t border-[var(--border)] text-xs">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[var(--success)]" />
          <span className="text-[var(--subtle)]">{log.filter((e) => e.allowed).length} allowed</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[var(--danger)]" />
          <span className="text-[var(--subtle)]">{log.filter((e) => !e.allowed).length} blocked (402)</span>
        </div>
      </div>
    </div>
  )
}
