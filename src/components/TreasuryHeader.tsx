import { ConnectKitButton } from 'connectkit'
import { usePoolBalance, useTotalHeld } from '../hooks/usePayPulse'
import { Amount, usdcDecimalsFor } from '@/onchain-money'
import { ARC_TESTNET_ID } from '../contracts/paypulse'

function PayPulseMark() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="32" height="32" rx="10" fill="#acc6e9" fillOpacity="0.15" />
      <rect x="0.5" y="0.5" width="31" height="31" rx="9.5" stroke="#acc6e9" strokeOpacity="0.3" />
      {/* pulse line */}
      <polyline
        points="5,16 9,16 11,10 14,22 17,13 19,19 21,16 27,16"
        stroke="#acc6e9"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  )
}

export function TreasuryHeader() {
  const { data: poolBalance } = usePoolBalance()
  const { data: totalHeld } = useTotalHeld()

  const fmt = (v: unknown) =>
    typeof v === 'bigint'
      ? Amount.fromRaw(v, usdcDecimalsFor(ARC_TESTNET_ID)).toFixed(2)
      : '—'

  return (
    <header
      className="sticky top-0 z-30 border-b"
      style={{
        borderColor: 'var(--border)',
        background: 'rgba(13,27,47,0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-2.5 shrink-0">
          <PayPulseMark />
          <span className="display font-semibold text-[var(--ink)] text-[1.05rem] tracking-tight leading-none">
            PayPulse
          </span>
          <span
            className="hidden sm:inline text-[9px] font-semibold uppercase tracking-[0.12em] px-1.5 py-0.5 rounded-md"
            style={{ background: 'rgba(172,198,233,0.12)', color: 'var(--subtle)' }}
          >
            Testnet
          </span>
        </div>

        {/* Hero stats */}
        <div className="hidden md:flex items-center gap-px">
          <StatPill label="Pool Available" value={`$${fmt(poolBalance)}`} />
          <div className="w-px h-6 mx-3" style={{ background: 'var(--border)' }} />
          <StatPill label="Total Reserved" value={`$${fmt(totalHeld)}`} dimmed />
        </div>

        <ConnectKitButton />
      </div>
    </header>
  )
}

function StatPill({
  label,
  value,
  dimmed,
}: {
  label: string
  value: string
  dimmed?: boolean
}) {
  return (
    <div className="text-right px-2">
      <div
        className="text-[10px] uppercase tracking-[0.08em] mb-0.5"
        style={{ color: 'var(--subtle)' }}
      >
        {label}
      </div>
      <div
        className="display text-base font-semibold tabular-nums leading-none"
        style={{ color: dimmed ? 'var(--muted)' : 'var(--ink)' }}
      >
        {value}
      </div>
    </div>
  )
}
