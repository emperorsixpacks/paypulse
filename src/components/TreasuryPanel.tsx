import { useState, useEffect, useRef } from 'react'
import { useAccount, useWriteContract, useWaitForTransactionReceipt, useSwitchChain } from 'wagmi'
import { erc20Abi } from 'viem'
import { toast } from 'sonner'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'
import { getUsdc } from '@/onchain-facts'
import { parseAmount, Amount, usdcDecimalsFor } from '@/onchain-money'
import { usePoolBalance, useTotalHeld } from '../hooks/usePayPulse'
import { ArrowDownToLine, Loader2 } from 'lucide-react'

const usdcFact = getUsdc(ARC_TESTNET_ID)
const USDC_ADDRESS = usdcFact?.address as `0x${string}`

export function TreasuryPanel() {
  const { address, chainId } = useAccount()
  const { switchChain } = useSwitchChain()
  const { data: pool, refetch: refetchPool } = usePoolBalance()
  const { data: held, refetch: refetchHeld } = useTotalHeld()

  const [amount, setAmount] = useState('')
  const [step, setStep] = useState<'idle' | 'approving' | 'depositing' | 'done'>('idle')
  const amountRef = useRef('')   // stable snapshot for effects

  const wrongChain = chainId !== ARC_TESTNET_ID

  const { writeContract: approve, data: approveTx } = useWriteContract()
  const { isSuccess: approveConfirmed, data: approveReceipt } = useWaitForTransactionReceipt({ hash: approveTx })

  const { writeContract: deposit, data: depositTx } = useWriteContract()
  const { isSuccess: depositConfirmed, data: depositReceipt } = useWaitForTransactionReceipt({ hash: depositTx })

  // Step 1→2: approve confirmed → fire deposit
  useEffect(() => {
    if (!approveConfirmed || !approveReceipt || step !== 'approving') return
    const parsed = parseAmount(ARC_TESTNET_ID, amountRef.current)
    // eslint-disable-next-line react/set-state-in-effect -- wagmi receipt-driven state machine
    setStep('depositing')
    deposit({
      ...PAYPULSE,
      functionName: 'deposit',
      args: [parsed.raw],
      chainId: ARC_TESTNET_ID,
    })
  }, [approveConfirmed, approveReceipt]) // eslint-disable-line react-hooks/exhaustive-deps

  // Step 2→done: deposit confirmed
  useEffect(() => {
    if (!depositConfirmed || !depositReceipt || step !== 'depositing') return
    // eslint-disable-next-line react/set-state-in-effect -- wagmi receipt-driven state machine
    setStep('done')
    toast.success(`Deposited $${amountRef.current} USDC into the treasury`)
    // eslint-disable-next-line react/set-state-in-effect -- wagmi receipt-driven state machine
    setAmount('')
    void refetchPool()
    void refetchHeld()
    const t = setTimeout(() => setStep('idle'), 2500)
    return () => clearTimeout(t)
  }, [depositConfirmed, depositReceipt]) // eslint-disable-line react-hooks/exhaustive-deps

  const fmtU = (v: unknown) =>
    typeof v === 'bigint'
      ? `$${Amount.fromRaw(v, usdcDecimalsFor(ARC_TESTNET_ID)).toFixed(2)}`
      : '—'

  function handleDeposit() {
    if (!address || !amount) return
    if (wrongChain) { switchChain({ chainId: ARC_TESTNET_ID }); return }
    amountRef.current = amount
    const parsed = parseAmount(ARC_TESTNET_ID, amount)
    setStep('approving')
    approve({
      address: USDC_ADDRESS,
      abi: erc20Abi,
      functionName: 'approve',
      args: [PAYPULSE.address, parsed.raw],
      chainId: ARC_TESTNET_ID,
    })
  }

  const busy = step === 'approving' || step === 'depositing'

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <div className="flex items-center gap-2 mb-4">
        <ArrowDownToLine size={16} className="text-[var(--accent)]" />
        <h2 className="display font-semibold text-[var(--ink)]">Fund Treasury</h2>
      </div>

      {/* Balance row */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <StatBlock label="Free Pool" value={fmtU(pool)} />
        <StatBlock label="Total Held" value={fmtU(held)} />
      </div>

      {address ? (
        <div className="space-y-3">
          <div>
            <label className="block text-[11px] uppercase tracking-wider text-[var(--subtle)] mb-1">
              Amount (USDC)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--subtle)] text-sm">$</span>
              <input
                type="number"
                min="0"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                disabled={busy}
                className="w-full pl-7 pr-4 py-2.5 rounded-xl bg-[var(--surface-strong)] border border-[var(--border)] text-[var(--ink)] text-sm placeholder-[var(--subtle)] focus:outline-none focus:border-[var(--border-strong)] tabular-nums disabled:opacity-50"
              />
            </div>
          </div>

          {/* Quick amounts */}
          <div className="flex gap-2">
            {['10', '50', '100', '500'].map((v) => (
              <button
                key={v}
                onClick={() => setAmount(v)}
                disabled={busy}
                className="flex-1 py-1.5 rounded-lg border border-[var(--border)] text-[10px] text-[var(--muted)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-colors disabled:opacity-40"
              >
                ${v}
              </button>
            ))}
          </div>

          {/* Step indicator */}
          {busy && (
            <div className="flex gap-3 text-xs text-[var(--subtle)]">
              <span className={step === 'approving' ? 'text-[var(--accent)]' : 'text-[var(--success)]'}>
                {step === 'approving' ? '⏳' : '✓'} 1. Approve
              </span>
              <span className={step === 'depositing' ? 'text-[var(--accent)]' : 'opacity-40'}>
                {step === 'depositing' ? '⏳' : '·'} 2. Deposit
              </span>
            </div>
          )}

          <button
            onClick={handleDeposit}
            disabled={busy || !amount || Number(amount) <= 0}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl font-semibold text-sm transition-colors disabled:opacity-40"
            style={{
              background: step === 'done' ? 'rgba(141,216,159,0.2)' : busy ? 'var(--surface-strong)' : 'var(--accent)',
              color: step === 'done' ? 'var(--success)' : busy ? 'var(--ink)' : '#0d1b2f',
            }}
          >
            {busy && <Loader2 size={14} className="animate-spin" />}
            {step === 'approving'
              ? 'Approving spend…'
              : step === 'depositing'
                ? 'Depositing…'
                : step === 'done'
                  ? 'Deposited!'
                  : wrongChain
                    ? 'Switch to Arc Testnet'
                    : 'Deposit USDC'}
          </button>

          <p className="text-[11px] text-[var(--subtle)] text-center">
            Two transactions: approve USDC spend, then deposit
          </p>
        </div>
      ) : (
        <p className="text-sm text-[var(--subtle)] text-center py-4">Connect wallet to deposit</p>
      )}
    </div>
  )
}

function StatBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-[var(--surface-strong)] px-3 py-2.5">
      <div className="text-[10px] uppercase tracking-wider text-[var(--subtle)] mb-0.5">{label}</div>
      <div className="display font-semibold text-[var(--ink)] tabular-nums text-base">{value}</div>
    </div>
  )
}
