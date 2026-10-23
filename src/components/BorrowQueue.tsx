import { useEffect } from 'react'
import { useAccount, useWriteContract, useWaitForTransactionReceipt, useSwitchChain } from 'wagmi'
import { toast } from 'sonner'
import { motion, AnimatePresence } from 'framer-motion'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'
import { usePendingRequests, useBorrowRequest } from '../hooks/usePayPulse'
import { CheckCircle, XCircle, Clock } from 'lucide-react'

const BORROW_STATUS_LABELS = ['Pending', 'Approved', 'Rejected']

function BorrowRow({
  id,
  agentNames,
  onVote,
}: {
  id: bigint
  agentNames: Record<string, string>
  onVote?: () => void
}) {
  const req = useBorrowRequest(id)
  const { address, chainId } = useAccount()
  const { switchChain } = useSwitchChain()
  const wrongChain = chainId !== ARC_TESTNET_ID

  const { writeContract: approve, data: approveTx } = useWriteContract()
  const { writeContract: reject, data: rejectTx } = useWriteContract()
  const { isSuccess: approveOk, data: approveReceipt } = useWaitForTransactionReceipt({ hash: approveTx })
  const { isSuccess: rejectOk, data: rejectReceipt } = useWaitForTransactionReceipt({ hash: rejectTx })

  useEffect(() => {
    if (approveOk && approveReceipt) { toast.success(`Approved borrow #${id}`); onVote?.() }
  }, [approveOk, approveReceipt]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (rejectOk && rejectReceipt) { toast.error(`Rejected borrow #${id}`); onVote?.() }
  }, [rejectOk, rejectReceipt]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!req) return null

  const fmtU = (v: bigint) =>
    (Number(v) / 1e6).toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 })

  const agentLabel = agentNames[req.agent.toLowerCase()] ?? `${req.agent.slice(0, 8)}…`
  const statusLabel = BORROW_STATUS_LABELS[req.status]

  function handleApprove() {
    if (wrongChain) { switchChain({ chainId: ARC_TESTNET_ID }); return }
    approve({ ...PAYPULSE, functionName: 'approveBorrow', args: [id], chainId: ARC_TESTNET_ID })
  }
  function handleReject() {
    if (wrongChain) { switchChain({ chainId: ARC_TESTNET_ID }); return }
    reject({ ...PAYPULSE, functionName: 'rejectBorrow', args: [id], chainId: ARC_TESTNET_ID })
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="rounded-xl border border-[var(--border)] bg-[var(--surface-strong)] p-4"
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div>
          <div className="flex items-center gap-2 mb-0.5">
            <Clock size={13} className="text-[var(--subtle)]" />
            <span className="text-xs text-[var(--subtle)]">Request #{id.toString()}</span>
            <span
              className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded font-medium"
              style={{
                background:
                  req.status === 0
                    ? 'rgba(172,198,233,0.15)'
                    : req.status === 1
                      ? 'rgba(141,216,159,0.15)'
                      : 'rgba(232,109,122,0.15)',
                color:
                  req.status === 0
                    ? 'var(--accent)'
                    : req.status === 1
                      ? 'var(--success)'
                      : 'var(--danger)',
              }}
            >
              {statusLabel}
            </span>
          </div>
          <div className="text-sm font-semibold text-[var(--ink)]">
            {agentLabel} wants{' '}
            <span className="text-[var(--accent)] tabular-nums">${fmtU(req.amount)} USDC</span>
          </div>
          <div className="text-xs text-[var(--subtle)] mt-0.5 italic">"{req.reason}"</div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-[11px] text-[var(--subtle)]">
            {req.approvals.toString()}/2 approvals
          </div>
        </div>
      </div>

      {req.status === 0 && address && (
        <div className="flex gap-2 mt-3">
          <button
            onClick={handleApprove}
            className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-semibold transition-colors"
            style={{ background: 'rgba(141,216,159,0.15)', color: 'var(--success)' }}
          >
            <CheckCircle size={13} /> Approve
          </button>
          <button
            onClick={handleReject}
            className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-semibold transition-colors"
            style={{ background: 'rgba(232,109,122,0.12)', color: 'var(--danger)' }}
          >
            <XCircle size={13} /> Reject
          </button>
        </div>
      )}
    </motion.div>
  )
}

export function BorrowQueue({
  agentNames,
}: {
  agentNames: Record<string, string>
}) {
  const { data: pendingIds } = usePendingRequests()

  const ids = (pendingIds ?? []) as bigint[]

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock size={16} className="text-[var(--accent)]" />
          <h2 className="display font-semibold text-[var(--ink)]">Borrow Queue</h2>
        </div>
        {ids.length > 0 && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--accent)]/20 text-[var(--accent)] font-medium">
            {ids.length} pending
          </span>
        )}
      </div>

      {ids.length === 0 ? (
        <div className="text-center py-8 text-[var(--subtle)] text-sm">
          No pending borrow requests
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {ids.map((id) => (
              <BorrowRow key={id.toString()} id={id} agentNames={agentNames} />
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  )
}
