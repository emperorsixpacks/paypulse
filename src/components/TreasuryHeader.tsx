import { ConnectKitButton } from 'connectkit'
import { usePoolBalance, useTotalHeld } from '../hooks/usePayPulse'
import { Amount, usdcDecimalsFor } from '@/onchain-money'
import { ARC_TESTNET_ID } from '../contracts/paypulse'
import { Activity } from 'lucide-react'

export function TreasuryHeader() {
  const { data: poolBalance } = usePoolBalance()
  const { data: totalHeld } = useTotalHeld()

  const fmt = (v: unknown) =>
    typeof v === 'bigint'
      ? Amount.fromRaw(v, usdcDecimalsFor(ARC_TESTNET_ID)).toFixed(2)
      : '—'

  return (
    <header className="border-b border-white/10 bg-[var(--surface)] backdrop-blur-md sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[var(--accent)] flex items-center justify-center shrink-0">
            <Activity size={16} className="text-[#0d1b2f]" />
          </div>
          <span className="display font-semibold text-[var(--ink)] text-lg tracking-tight">
            PayPulse
          </span>
          <span className="text-[10px] font-medium uppercase tracking-widest px-1.5 py-0.5 rounded bg-white/10 text-[var(--subtle)]">
            Testnet
          </span>
        </div>

        {/* Stats */}
        <div className="hidden sm:flex items-center gap-6 text-sm">
          <Stat label="Pool (free)" value={`$${fmt(poolBalance)}`} />
          <Stat label="Total held" value={`$${fmt(totalHeld)}`} />
        </div>

        <ConnectKitButton />
      </div>
    </header>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-right">
      <div className="text-[11px] uppercase tracking-wider text-[var(--subtle)]">{label}</div>
      <div className="display font-semibold text-[var(--ink)] tabular-nums">{value}</div>
    </div>
  )
}
