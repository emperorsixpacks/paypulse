import { useState, useEffect, useCallback } from 'react'
import { useWriteContract, useWaitForTransactionReceipt, useAccount } from 'wagmi'
import { toast } from 'sonner'
import { CheckCircle, Loader2, RefreshCw } from 'lucide-react'
import { PAYPULSE_ABI, PAYPULSE_ADDRESS } from '../contracts/paypulse'

interface PendingDraw {
  agent: string
  amount: string
  contract: string
}

export function SettlePanel() {
  const { isConnected } = useAccount()
  const [pending, setPending] = useState<PendingDraw[]>([])
  const [loading, setLoading] = useState(false)
  const [currentIdx, setCurrentIdx] = useState<number | null>(null)

  const { writeContract, data: hash } = useWriteContract()
  const { isSuccess } = useWaitForTransactionReceipt({ hash })

  const fetchPending = useCallback(async () => {
    setLoading(true)
    try {
      const r = await fetch('/api/settle')
      const d = await r.json() as { pendingDraws?: PendingDraw[] }
      setPending(d.pendingDraws ?? [])
    } catch {
      toast.error('Failed to fetch pending draws')
    } finally {
      setLoading(false)
    }
  }, [])

  // eslint-disable-next-line react/set-state-in-effect
  useEffect(() => { void fetchPending() }, [fetchPending])

  // After each tx confirms, clear that draw from queue and move to next
  useEffect(() => {
    if (!isSuccess || currentIdx === null) return
    const draw = pending[currentIdx]
    if (!draw) return
    // Notify server the draw was settled
    fetch('/api/settle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent: draw.agent }),
    }).catch(() => {})
    // eslint-disable-next-line react/set-state-in-effect
    setCurrentIdx(null)
    // eslint-disable-next-line react/set-state-in-effect
    setPending((prev) => prev.filter((_, i) => i !== currentIdx))
    toast.success(`Settled draw for ${draw.agent.slice(0, 8)}…`)
  }, [isSuccess, currentIdx, pending])

  function settleAll() {
    if (!PAYPULSE_ADDRESS || pending.length === 0) return
    pending.forEach((draw, idx) => {
      setCurrentIdx(idx)
      writeContract({
        address: PAYPULSE_ADDRESS,
        abi: PAYPULSE_ABI,
        functionName: 'draw',
        args: [draw.agent as `0x${string}`, BigInt(draw.amount)],
      })
    })
  }

  if (!isConnected) return null

  return (
    <div
      className="rounded-2xl border border-[var(--border)] p-5 space-y-4"
      style={{ background: 'var(--surface)' }}
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-[var(--ink)]">Pending Settlements</h3>
          <p className="text-xs text-[var(--subtle)] mt-0.5">
            Sign draw() calls from your wallet to settle agent spend onchain
          </p>
        </div>
        <button
          onClick={() => { void fetchPending() }}
          className="p-1.5 rounded-lg text-[var(--subtle)] hover:text-[var(--ink)] transition-colors"
          style={{ background: 'rgba(255,255,255,0.05)' }}
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {pending.length === 0 ? (
        <div className="flex items-center gap-2 text-xs text-[var(--subtle)]">
          <CheckCircle size={13} className="text-[var(--success)]" />
          No pending draws
        </div>
      ) : (
        <div className="space-y-2">
          {pending.map((d, i) => (
            <div
              key={d.agent}
              className="flex items-center justify-between px-3 py-2 rounded-lg text-xs"
              style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)' }}
            >
              <span className="mono text-[var(--muted)]">{d.agent.slice(0, 10)}…</span>
              <span className="text-[var(--ink)] font-medium">
                {(Number(d.amount) / 1e6).toFixed(4)} USDC
              </span>
              {currentIdx === i && hash && (
                <Loader2 size={12} className="animate-spin text-[var(--accent)]" />
              )}
            </div>
          ))}

          <button
            onClick={settleAll}
            disabled={currentIdx !== null}
            className="w-full py-2 rounded-xl text-xs font-semibold transition-all disabled:opacity-50"
            style={{
              background: 'var(--accent)',
              color: '#0d1b2f',
            }}
          >
            {currentIdx !== null ? (
              <span className="flex items-center justify-center gap-1.5">
                <Loader2 size={12} className="animate-spin" /> Settling…
              </span>
            ) : (
              `Settle ${pending.length} draw${pending.length > 1 ? 's' : ''} from your wallet`
            )}
          </button>
        </div>
      )}
    </div>
  )
}
