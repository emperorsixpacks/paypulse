import { useWriteContract, useWaitForTransactionReceipt, useAccount, useSwitchChain } from 'wagmi'
import { toast } from 'sonner'
import { CheckCircle2, XCircle, Clock } from 'lucide-react'
import { Amount, usdcDecimalsFor } from '@/onchain-money'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'
import { usePendingRequests } from '../hooks/usePayPulse'
import type { BorrowRequest } from '../types'

interface RequestRowProps {
  req: BorrowRequest
  agentName: string
}

function RequestRow({ req, agentName }: RequestRowProps) {
  const { chainId } = useAccount()
  const { switchChain } = useSwitchChain()

  const { writeContract: approve, data: approveHash, isPending: approvePending } = useWriteContract()
  const { writeContract: reject, data: rejectHash, isPending: rejectPending } = useWriteContract()
  const { isLoading: approveConfirming } = useWaitForTransactionReceipt({ hash: approveHash })
  const { isLoading: rejectConfirming } = useWaitForTransactionReceipt({ hash: rejectHash })

  const isWrongChain = chainId !== ARC_TESTNET_ID
  const busy = approvePending || rejectPending || approveConfirming || rejectConfirming

  const handleApprove = () => {
    if (isWrongChain) { switchChain({ chainId: ARC_TESTNET_ID }); return }
    approve({ ...PAYPULSE, functionName: 'approveBorrow', args: [req.id], chainId: ARC_TESTNET_ID })
    toast('Approving borrow request…')
  }

  const handleReject = () => {
    if (isWrongChain) { switchChain({ chainId: ARC_TESTNET_ID }); return }
    reject({ ...PAYPULSE, functionName: 'rejectBorrow', args: [req.id], chainId: ARC_TESTNET_ID })
    toast('Rejecting borrow request…')
  }

  const amountFmt = Amount.fromRaw(req.amount, usdcDecimalsFor(ARC_TESTNET_ID)).toFixed(4)

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Clock size={13} className="text-amber-400 shrink-0 mt-0.5" />
            <span className="text-sm font-semibold text-[var(--ink)]">
              ${amountFmt} USDC borrow
            </span>
          </div>
          <div className="mt-1 ml-5 text-xs text-[var(--subtle)] mono">
            {agentName || (req.agent.slice(0, 6) + '…' + req.agent.slice(-4))}
          </div>
        </div>
        <div className="flex gap-1 text-xs">
          <span className="text-[var(--success)] tabular-nums">{Number(req.approvals)}/2</span>
          <span className="text-[var(--subtle)]">approvals</span>
        </div>
      </div>

      {req.reason && (
        <p className="text-xs text-[var(--muted)] bg-[var(--surface-muted)] rounded-lg px-3 py-2 leading-relaxed">
          &ldquo;{req.reason}&rdquo;
        </p>
      )}

      <div className="flex gap-2">
        <button
          onClick={handleApprove}
          disabled={busy}
          className="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-[var(--success)]/40 bg-[var(--success)]/10 py-2 text-xs font-semibold text-[var(--success)] hover:bg-[var(--success)]/20 transition-colors disabled:opacity-40"
        >
          <CheckCircle2 size={13} />
          {approvePending ? 'Confirm…' : approveConfirming ? 'Approving…' : 'Approve'}
        </button>
        <button
          onClick={handleReject}
          disabled={busy}
          className="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-[var(--danger)]/40 bg-[var(--danger)]/10 py-2 text-xs font-semibold text-[var(--danger)] hover:bg-[var(--danger)]/20 transition-colors disabled:opacity-40"
        >
          <XCircle size={13} />
          {rejectPending ? 'Confirm…' : rejectConfirming ? 'Rejecting…' : 'Reject'}
        </button>
      </div>
    </div>
  )
}

interface Props {
  agentNames: Record<string, string>
  requests: BorrowRequest[]
}

export function ApprovalsQueue({ agentNames, requests }: Props) {
  const { data: pendingIds } = usePendingRequests()

  const ids = (pendingIds ?? []) as bigint[]
  const pending = requests.filter(
    (r) => r.status === 0 && ids.some((x) => x === r.id),
  )

  return (
    <div className="space-y-3">
      {pending.length === 0 ? (
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center">
          <CheckCircle2 size={24} className="mx-auto mb-2 text-[var(--success)]/60" />
          <p className="text-sm text-[var(--subtle)]">No pending approvals</p>
        </div>
      ) : (
        pending.map((r) => (
          <RequestRow key={String(r.id)} req={r} agentName={agentNames[r.agent] ?? ''} />
        ))
      )}
    </div>
  )
}
