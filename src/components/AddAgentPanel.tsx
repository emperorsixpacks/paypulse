import { useState, useEffect } from 'react'
import { useAccount, useWriteContract, useWaitForTransactionReceipt, useSwitchChain } from 'wagmi'
import { toast } from 'sonner'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'
import { UserPlus } from 'lucide-react'

export function AddAgentPanel({ onAdded }: { onAdded?: () => void }) {
  const { address, chainId } = useAccount()
  const { switchChain } = useSwitchChain()

  const [form, setForm] = useState({
    agentAddress: '',
    allocationBps: '',
    periodLength: '3600',
    isLender: false,
    maxLendBps: '0',
  })
  const [busy, setBusy] = useState(false)

  const wrongChain = chainId !== ARC_TESTNET_ID

  const { writeContract, data: hash } = useWriteContract()
  const { isSuccess, data: receipt } = useWaitForTransactionReceipt({ hash })

  useEffect(() => {
    if (!isSuccess || !receipt || !busy) return
    // eslint-disable-next-line react/set-state-in-effect -- wagmi receipt-driven reset
    setBusy(false)
    toast.success('Agent added successfully')
    // eslint-disable-next-line react/set-state-in-effect -- wagmi receipt-driven reset
    setForm({ agentAddress: '', allocationBps: '', periodLength: '3600', isLender: false, maxLendBps: '0' })
    onAdded?.()
  }, [isSuccess, receipt]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!address) return
    if (wrongChain) { switchChain({ chainId: ARC_TESTNET_ID }); return }

    const bps = BigInt(Math.round(Number(form.allocationBps) * 100))
    const period = BigInt(form.periodLength)
    const maxLend = BigInt(Math.round(Number(form.maxLendBps) * 100))

    setBusy(true)
    writeContract({
      ...PAYPULSE,
      functionName: 'addAgent',
      args: [form.agentAddress as `0x${string}`, bps, period, form.isLender, maxLend],
      chainId: ARC_TESTNET_ID,
    })
  }

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <div className="flex items-center gap-2 mb-4">
        <UserPlus size={16} className="text-[var(--accent)]" />
        <h2 className="display font-semibold text-[var(--ink)]">Add Agent</h2>
      </div>

      {address ? (
        <form onSubmit={handleSubmit} className="space-y-3">
          <Field label="Agent Address">
            <input
              type="text"
              value={form.agentAddress}
              onChange={(e) => setForm((f) => ({ ...f, agentAddress: e.target.value }))}
              placeholder="0x…"
              className={inputCls}
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Allocation %">
              <input
                type="number"
                min="0"
                max="100"
                step="0.01"
                value={form.allocationBps}
                onChange={(e) => setForm((f) => ({ ...f, allocationBps: e.target.value }))}
                placeholder="40"
                className={inputCls}
              />
            </Field>
            <Field label="Period (seconds)">
              <input
                type="number"
                min="60"
                value={form.periodLength}
                onChange={(e) => setForm((f) => ({ ...f, periodLength: e.target.value }))}
                className={inputCls}
              />
            </Field>
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-[var(--ink-2)] cursor-pointer select-none">
              <input
                type="checkbox"
                checked={form.isLender}
                onChange={(e) => setForm((f) => ({ ...f, isLender: e.target.checked }))}
                className="w-4 h-4 rounded accent-[var(--accent)]"
              />
              Can lend surplus
            </label>
            {form.isLender && (
              <div className="flex-1">
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={form.maxLendBps}
                  onChange={(e) => setForm((f) => ({ ...f, maxLendBps: e.target.value }))}
                  placeholder="Max lend %"
                  className={inputCls}
                />
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={busy || !form.agentAddress || !form.allocationBps}
            className="w-full py-2.5 rounded-xl font-semibold text-sm transition-colors disabled:opacity-40"
            style={{ background: 'var(--accent)', color: '#0d1b2f' }}
          >
            {busy ? 'Adding…' : wrongChain ? 'Switch to Arc Testnet' : 'Add Agent'}
          </button>
        </form>
      ) : (
        <p className="text-sm text-[var(--subtle)] text-center py-4">Connect wallet to manage agents</p>
      )}
    </div>
  )
}

const inputCls =
  'w-full px-3 py-2 rounded-xl bg-[var(--surface-strong)] border border-[var(--border)] text-[var(--ink)] text-sm placeholder-[var(--subtle)] focus:outline-none focus:border-[var(--border-strong)]'

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-[11px] uppercase tracking-wider text-[var(--subtle)] mb-1">
        {label}
      </label>
      {children}
    </div>
  )
}
