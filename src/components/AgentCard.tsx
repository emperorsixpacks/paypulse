import { motion } from 'framer-motion'
import type { AgentInfo } from '../types'
import { Bot, Zap, TrendingUp } from 'lucide-react'

const AGENT_ICONS: Record<string, React.ReactNode> = {
  research: <TrendingUp size={15} />,
  scraper: <Zap size={15} />,
  support: <Bot size={15} />,
}

const AGENT_COLORS: Record<string, string> = {
  research: '#acc6e9',
  scraper: '#8dd89f',
  support: '#f0c27a',
}

function getSlug(name: string) {
  return name.toLowerCase().split(' ')[0]
}

interface Props {
  agent: AgentInfo
  name: string
  selected?: boolean
  onClick?: () => void
}

export function AgentCard({ agent, name, selected, onClick }: Props) {
  const slug = getSlug(name)
  const color = AGENT_COLORS[slug] ?? '#acc6e9'
  const icon = AGENT_ICONS[slug] ?? <Bot size={15} />

  const alloc = Number(agent.allocation)
  const spent = Number(agent.spent)
  const pct = alloc > 0 ? Math.min((spent / alloc) * 100, 100) : 0
  const remaining = alloc - spent
  const isExhausted = remaining <= 0

  const fmtU = (v: number) =>
    (v / 1e6).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })

  const periodSec = Number(agent.periodLength)
  const periodLabel =
    periodSec >= 86400
      ? `${Math.round(periodSec / 86400)}d`
      : periodSec >= 3600
        ? `${Math.round(periodSec / 3600)}h`
        : `${Math.round(periodSec / 60)}m`

  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.015 }}
      whileTap={{ scale: 0.98 }}
      className={`w-full text-left rounded-2xl p-4 border transition-colors ${
        selected
          ? 'border-[var(--border-strong)] bg-[var(--surface-strong)]'
          : 'border-[var(--border)] bg-[var(--surface)] hover:bg-[var(--surface-strong)]'
      }`}
    >
      {/* Top row */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
            style={{ background: color + '22', color }}
          >
            {icon}
          </div>
          <div>
            <div className="text-sm font-semibold text-[var(--ink)] leading-tight">{name}</div>
            <div className="text-[11px] text-[var(--subtle)] mono">{agent.address.slice(0, 8)}…</div>
          </div>
        </div>
        <div className="text-right">
          <div
            className="text-[11px] font-semibold uppercase tracking-wide"
            style={{ color: isExhausted ? 'var(--danger)' : 'var(--success)' }}
          >
            {isExhausted ? 'Exhausted' : 'Active'}
          </div>
          <div className="text-[11px] text-[var(--subtle)]">{(Number(agent.allocationBps) / 100).toFixed(0)}% · {periodLabel}</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-2">
        <div className="flex justify-between text-[11px] text-[var(--subtle)] mb-1">
          <span>Spent</span>
          <span className="tabular-nums">${fmtU(spent)} / ${fmtU(alloc)}</span>
        </div>
        <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: isExhausted ? 'var(--danger)' : color }}
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Bottom row */}
      <div className="flex justify-between text-[11px] text-[var(--subtle)]">
        <span>Remaining: <span className="text-[var(--ink-2)] font-medium tabular-nums">${fmtU(remaining)}</span></span>
        {agent.isLender && (
          <span className="px-1.5 py-0.5 rounded bg-white/10 text-[var(--accent)]">Lender</span>
        )}
      </div>
    </motion.button>
  )
}
