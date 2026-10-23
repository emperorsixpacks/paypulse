import { useState } from 'react'
import { useWriteContract, useWaitForTransactionReceipt, useAccount, useSwitchChain } from 'wagmi'
import { toast } from 'sonner'
import { X, Bot } from 'lucide-react'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'

interface Props {
  onClose: () => void
  onAdded?: () => void
}

export function AddAgentModal({ onClose, onAdded }: Props) {
  const [addr, setAddr] = useState('')
  const [bps, setBps] = useState('4000')
  const [period, setPeriod] = useState('3600')
  const [isLender, setIsLender] = useState(false)
  const [maxLendBps, setMaxLendBps] = useState('2000')
  const [done, setDone] = useState(false)

  const { chainId } = useAccount()
  const { switchChain } = useSwitchChain()

  const { writeContract, data: hash, isPending } = useWriteContract()
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash })

  const busy = isPending || isConfirming
  const isWrongChain = chainId !== ARC_TESTNET_ID

  if (isSuccess && !done) {
    setDone(true)
    toast.success('Agent added successfully')
    onAdded?.()
  }

  const handleAdd = () => {
    if (!addr.startsWith('0x') || addr.length !== 42) {
      toast.error('Enter a valid Ethereum address')
      return
    }
    const bpsNum = parseInt(bps, 10)
    if (isNaN(bpsNum) || bpsNum <= 0 || bpsNum > 10000) {
      toast.error('Allocation must be 1–10000 bps')
      return
    }
    const periodNum = parseInt(period, 10)
    if (isNaN(periodNum) || periodNum < 60) {
      toast.error('Period must be at least 60 seconds')
      return
    }

    if (isWrongChain) {
      switchChain({ chainId: ARC_TESTNET_ID })
      return
    }

    writeContract({
      ...PAYPULSE,
      functionName: 'addAgent',
      args: [addr as `0x${string}`, BigInt(bpsNum), BigInt(periodNum), isLender, BigInt(parseInt(maxLendBps, 10) || 0)],
      chainId: ARC_TESTNET_ID,
    })
  }

  const pctDisplay = (parseInt(bps, 10) / 100).toFixed(1)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div
        className="relative w-full max-w-sm rounded-2xl border border-[var(--border-strong)] bg-[var(--surface-muted)] p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <Bot size={18} className="text-[var(--accent)]" />
            <h2 className="display font-semibold text-[var(--ink)] text-lg">Add Agent</h2>
          </div>
          <button onClick={onClose} className="text-[var(--subtle)] hover:text-[var(--ink)] transition-colors">
            <X size={18} />
          </button>
        </div>

        {done ? (
          <div className="text-center py-4 space-y-3">
            <div className="text-2xl font-bold display text-[var(--success)]">Agent Added</div>
            <p className="text-[var(--muted)] text-sm">The agent has been registered and its budget allocated.</p>
            <button onClick={onClose} className="w-full rounded-xl bg-[var(--accent)] text-[#0d1b2f] font-semibold py-3 hover:bg-[var(--accent-hover)] transition-colors mt-2">
              Close
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <Field label="Agent Address">
              <input
                type="text"
                placeholder="0x..."
                value={addr}
                onChange={(e) => setAddr(e.target.value)}
                disabled={busy}
                className="input-field"
              />
            </Field>

            <Field label={`Allocation — ${pctDisplay}% of pool`}>
              <input
                type="range"
                min="100"
                max="5000"
                step="100"
                value={bps}
                onChange={(e) => setBps(e.target.value)}
                disabled={busy}
                className="w-full accent-[#acc6e9]"
              />
              <div className="flex justify-between text-xs text-[var(--subtle)] mt-1">
                <span>1%</span><span>{pctDisplay}%</span><span>50%</span>
              </div>
            </Field>

            <Field label="Period Length">
              <div className="grid grid-cols-4 gap-1.5">
                {[['1 min', '60'], ['1 hr', '3600'], ['1 day', '86400'], ['1 wk', '604800']].map(([label, val]) => (
                  <button
                    key={val}
                    onClick={() => setPeriod(val)}
                    disabled={busy}
                    className={`rounded-lg border py-1.5 text-xs transition-colors disabled:opacity-40 ${period === val ? 'border-[var(--accent)] text-[var(--accent)] bg-[var(--surface)]' : 'border-[var(--border)] text-[var(--subtle)] hover:border-[var(--accent)]'}`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </Field>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsLender(!isLender)}
                disabled={busy}
                className={`relative w-10 h-5 rounded-full transition-colors flex items-center ${isLender ? 'bg-[var(--accent)]' : 'bg-[var(--surface-muted)] border border-[var(--border)]'}`}
              >
                <span className={`absolute w-3.5 h-3.5 rounded-full bg-white shadow transition-transform ${isLender ? 'translate-x-5' : 'translate-x-1'}`} />
              </button>
              <span className="text-sm text-[var(--muted)]">Can lend surplus budget</span>
            </div>

            {isLender && (
              <Field label={`Max Lend — ${(parseInt(maxLendBps, 10) / 100).toFixed(0)}% of allocation`}>
                <input
                  type="range"
                  min="0"
                  max="5000"
                  step="500"
                  value={maxLendBps}
                  onChange={(e) => setMaxLendBps(e.target.value)}
                  disabled={busy}
                  className="w-full accent-[#acc6e9]"
                />
              </Field>
            )}

            <button
              onClick={handleAdd}
              disabled={busy || !addr}
              className="w-full rounded-xl bg-[var(--accent)] text-[#0d1b2f] font-semibold py-3 hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-40"
            >
              {isWrongChain ? 'Switch Network' : isPending ? 'Confirm in wallet…' : isConfirming ? 'Adding…' : 'Add Agent'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs uppercase tracking-wider text-[var(--subtle)]">{label}</label>
      {children}
    </div>
  )
}
