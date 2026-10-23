import { motion } from 'framer-motion'
import type { AgentInfo } from '../types'
import { Bot, Zap, TrendingUp, BookOpen } from 'lucide-react'

const AGENT_META: Record<string, { icon: React.ReactNode; color: string; glow: string }> = {
  research:  { icon: <TrendingUp size={14} />, color: '#acc6e9', glow: 'rgba(172,198,233,0.18)' },
  scraper:   { icon: <Zap size={14} />,        color: '#8dd89f', glow: 'rgba(141,216,159,0.18)' },
  support:   { icon: <Bot size={14} />,         color: '#f0c27a', glow: 'rgba(240,194,122,0.18)' },
  default:   { icon: <BookOpen size={14} />,    color: '#acc6e9', glow: 'rgba(172,198,233,0.12)' },
}

function getSlug(name: string) {
  return name.toLowerCase().split(/[\s-_]/)[0]
}

interface Props {
  agent: AgentInfo
  name: string
  selected?: boolean
  onClick?: () => void
}

export function AgentCard({ agent, name, selected, onClick }: Props) {
  const slug = getSlug(name)
  const meta = AGENT_META[slug] ?? AGENT_META.default
  const { color, glow, icon } = meta

  const alloc = Number(agent.allocation)
  const spent = Number(agent.spent)
  const pct = alloc > 0 ? Math.min((spent / alloc) * 100, 100) : 0
  const remaining = alloc - spent
  const isExhausted = remaining <= 0
  const isWarning = pct > 75 && !isExhausted

  const fmtU = (v: number) =>
    (v / 1e6).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  const periodSec = Number(agent.periodLength)
  const periodLabel =
    periodSec >= 86400
      ? `${Math.round(periodSec / 86400)}d`
      : periodSec >= 3600
        ? `${Math.round(periodSec / 3600)}h`
        : `${Math.round(periodSec / 60)}m`

  const barColor = isExhausted
    ? 'var(--danger)'
    : isWarning
      ? '#f0c27a'
      : color

  const statusColor = isExhausted
    ? 'var(--danger)'
    : isWarning
      ? '#f0c27a'
      : 'var(--success)'

  const statusLabel = isExhausted ? 'Exhausted' : isWarning ? 'High usage' : 'Active'

  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.012, boxShadow: `0 0 0 1px ${color}44, 0 8px 32px ${glow}` }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.15 }}
      className="w-full text-left rounded-2xl p-4 border transition-all"
      style={{
        borderColor: selected ? color + '66' : 'var(--border)',
        background: selected
          ? `linear-gradient(135deg, ${glow}, var(--surface))`
          : 'var(--surface)',
      }}
    >
      {/* Top row */}
      <div className="flex items-start justify-between mb-3 gap-2">
        <div className="flex items-center gap-2.5">
          {/* Icon bubble */}
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
            style={{ background: color + '1a', color, border: `1px solid ${color}33` }}
          >
            {icon}
          </div>
          <div>
            <div className="text-sm font-semibold leading-tight" style={{ color: 'var(--ink)' }}>
              {name}
            </div>
            <div className="text-[10px] mono mt-0.5" style={{ color: 'var(--subtle)' }}>
              {agent.address.slice(0, 6)}…{agent.address.slice(-4)}
            </div>
          </div>
        </div>

        {/* Status + period */}
        <div className="text-right shrink-0">
          <div
            className="text-[10px] font-semibold uppercase tracking-wide"
            style={{ color: statusColor }}
          >
            {statusLabel}
          </div>
          <div className="text-[10px] mt-0.5" style={{ color: 'var(--subtle)' }}>
            {(Number(agent.allocationBps) / 100).toFixed(0)}% · {periodLabel}
          </div>
        </div>
      </div>

      {/* Allocation label */}
      <div className="flex justify-between text-[11px] mb-1.5" style={{ color: 'var(--subtle)' }}>
        <span>Budget used</span>
        <span className="tabular-nums" style={{ color: 'var(--ink-2)' }}>
          ${fmtU(spent)}
          <span style={{ color: 'var(--subtle)' }}> / ${fmtU(alloc)}</span>
        </span>
      </div>

      {/* Progress bar — layered with gradient */}
      <div className="relative h-2 rounded-full overflow-hidden mb-3"
        style={{ background: 'rgba(255,255,255,0.07)' }}
      >
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{
            background: isExhausted
              ? `linear-gradient(90deg, ${'var(--danger)'}, #ff9eb0)`
              : `linear-gradient(90deg, ${barColor}, ${barColor}cc)`,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        />
        {/* Glow overlay */}
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ background: `linear-gradient(90deg, transparent, ${barColor}55)` }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.05 }}
        />
      </div>

      {/* Footer row */}
      <div className="flex items-center justify-between">
        <span className="text-[11px]" style={{ color: 'var(--subtle)' }}>
          Remaining:{' '}
          <span
            className="font-semibold tabular-nums"
            style={{ color: isExhausted ? 'var(--danger)' : 'var(--ink-2)' }}
          >
            ${fmtU(Math.max(remaining, 0))}
          </span>
        </span>
        <div className="flex items-center gap-1.5">
          {agent.isLender && (
            <span
              className="text-[9px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded-md"
              style={{ background: 'rgba(172,198,233,0.12)', color: 'var(--accent)' }}
            >
              Lender
            </span>
          )}
          <span
            className="text-[9px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded-md"
            style={{
              background: `${color}1a`,
              color,
            }}
          >
            {(pct).toFixed(0)}%
          </span>
        </div>
      </div>
    </motion.button>
  )
}
