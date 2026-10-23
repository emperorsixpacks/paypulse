import { useState } from 'react'
import { useWriteContract, useWaitForTransactionReceipt, useAccount, useSwitchChain } from 'wagmi'
import { erc20Abi } from 'viem'
import { toast } from 'sonner'
import { X, DollarSign } from 'lucide-react'
import { getUsdc, requireChain, buildTxExplorerUrl } from '@/onchain-facts'
import { parseAmount, Amount, usdcDecimalsFor } from '@/onchain-money'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'

interface Props {
  onClose: () => void
}

export function DepositModal({ onClose }: Props) {
  const [amount, setAmount] = useState('')
  const [step, setStep] = useState<'idle' | 'approving' | 'depositing' | 'done'>('idle')

  const { chainId } = useAccount()
  const { switchChain } = useSwitchChain()

  const usdcFact = getUsdc(ARC_TESTNET_ID)!
  const chain = requireChain(ARC_TESTNET_ID)

  const { writeContract: approve, data: approveHash } = useWriteContract()
  const { isLoading: isApproving, isSuccess: approveOk } = useWaitForTransactionReceipt({
    hash: approveHash,
  })

  const { writeContract: deposit, data: depositHash } = useWriteContract()
  const { isLoading: isDepositing, isSuccess: depositOk } = useWaitForTransactionReceipt({
    hash: depositHash,
  })

  const isWrongChain = chainId !== ARC_TESTNET_ID

  const handleDeposit = () => {
    if (!amount || isNaN(Number(amount)) || Number(amount) <= 0) {
      toast.error('Enter a valid USDC amount')
      return
    }
    if (isWrongChain) {
      switchChain({ chainId: ARC_TESTNET_ID })
      return
    }

    const parsed = parseAmount(ARC_TESTNET_ID, amount)
    setStep('approving')
    approve({
      address: usdcFact.address as `0x${string}`,
      abi: erc20Abi,
      functionName: 'approve',
      args: [PAYPULSE.address, parsed.raw],
      chainId: ARC_TESTNET_ID,
    })
  }

  // Once approve tx confirms, fire deposit
  if (approveOk && step === 'approving') {
    setStep('depositing')
    const parsed = parseAmount(ARC_TESTNET_ID, amount)
    deposit({
      ...PAYPULSE,
      functionName: 'deposit',
      args: [parsed.raw],
      chainId: ARC_TESTNET_ID,
    })
  }

  if (depositOk && step === 'depositing') {
    setStep('done')
    toast.success(`Deposited $${Amount.fromRaw(parseAmount(ARC_TESTNET_ID, amount).raw, usdcDecimalsFor(ARC_TESTNET_ID)).toFixed(2)} USDC`)
  }

  const busy = isApproving || isDepositing || step === 'approving' || step === 'depositing'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div
        className="relative w-full max-w-sm rounded-2xl border border-[var(--border-strong)] bg-[var(--surface-muted)] p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <DollarSign size={18} className="text-[var(--accent)]" />
            <h2 className="display font-semibold text-[var(--ink)] text-lg">Fund Treasury</h2>
          </div>
          <button onClick={onClose} className="text-[var(--subtle)] hover:text-[var(--ink)] transition-colors">
            <X size={18} />
          </button>
        </div>

        {step === 'done' ? (
          <div className="text-center py-6 space-y-3">
            <div className="text-3xl font-bold display text-[var(--success)]">Deposited</div>
            <p className="text-[var(--muted)] text-sm">
              ${amount} USDC added to the treasury pool.
            </p>
            {depositHash && (
              <a
                href={buildTxExplorerUrl(ARC_TESTNET_ID, depositHash)}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block text-xs text-[var(--accent)] hover:underline mt-1"
              >
                View on {chain.name} explorer
              </a>
            )}
            <button
              onClick={onClose}
              className="mt-4 w-full rounded-xl bg-[var(--accent)] text-[#0d1b2f] font-semibold py-3 hover:bg-[var(--accent-hover)] transition-colors"
            >
              Close
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-xs uppercase tracking-wider text-[var(--subtle)] mb-1.5">
                Amount (USDC)
              </label>
              <div className="relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--subtle)] text-sm font-medium">$</span>
                <input
                  type="number"
                  min="0.000001"
                  step="1"
                  placeholder="100"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  disabled={busy}
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] pl-8 pr-4 py-3 text-[var(--ink)] text-sm placeholder-[var(--subtle)] focus:outline-none focus:border-[var(--accent)] disabled:opacity-50"
                />
              </div>
            </div>

            <div className="flex gap-2">
              {['10', '50', '100', '500'].map((v) => (
                <button
                  key={v}
                  onClick={() => setAmount(v)}
                  disabled={busy}
                  className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--surface)] py-1.5 text-xs text-[var(--muted)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-colors disabled:opacity-40"
                >
                  ${v}
                </button>
              ))}
            </div>

            <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3 space-y-1.5 text-xs text-[var(--subtle)]">
              <div className="flex justify-between">
                <span>Step 1</span>
                <span className={approveOk ? 'text-[var(--success)]' : ''}>
                  {isApproving ? 'Approving...' : approveOk ? 'Approved' : 'Approve USDC spend'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Step 2</span>
                <span className={depositOk ? 'text-[var(--success)]' : ''}>
                  {isDepositing ? 'Depositing...' : depositOk ? 'Deposited' : 'Deposit to treasury'}
                </span>
              </div>
            </div>

            <button
              onClick={handleDeposit}
              disabled={busy || !amount}
              className="w-full rounded-xl bg-[var(--accent)] text-[#0d1b2f] font-semibold py-3 hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-40"
            >
              {isWrongChain ? 'Switch Network' : busy ? (step === 'approving' ? 'Approving…' : 'Depositing…') : 'Deposit'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
