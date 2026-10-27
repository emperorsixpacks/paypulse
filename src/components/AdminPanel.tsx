import { useState, useEffect } from 'react'
import { useWriteContract, useWaitForTransactionReceipt, useAccount, useSwitchChain } from 'wagmi'
import { toast } from 'sonner'
import { Settings, ShieldCheck, CheckCircle2 } from 'lucide-react'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'
import { useApproverList, useProxy } from '../hooks/usePayPulse'

const LS_PROXY = 'paypulse:proxyAddr'
const LS_APPROVER = 'paypulse:approverAddr'

export function AdminPanel() {
  const [proxyAddr, setProxyAddr] = useState(() => localStorage.getItem(LS_PROXY) ?? '')
  const [approverAddr, setApproverAddr] = useState(() => localStorage.getItem(LS_APPROVER) ?? '')
  const { chainId } = useAccount()
  const { switchChain } = useSwitchChain()

  const { data: currentProxy } = useProxy()
  const { data: approvers } = useApproverList()

  const { writeContract: setProxy, data: proxyHash, isPending: proxyPending } = useWriteContract()
  const { isLoading: proxyConfirming, isSuccess: proxyOk, data: proxyReceipt } = useWaitForTransactionReceipt({ hash: proxyHash })

  const { writeContract: addApprover, data: approverHash, isPending: approverPending } = useWriteContract()
  const { isLoading: approverConfirming, isSuccess: approverOk, data: approverReceipt } = useWaitForTransactionReceipt({ hash: approverHash })

  // Persist inputs to localStorage
  useEffect(() => { localStorage.setItem(LS_PROXY, proxyAddr) }, [proxyAddr])
  useEffect(() => { localStorage.setItem(LS_APPROVER, approverAddr) }, [approverAddr])

  // eslint-disable-next-line react/set-state-in-effect
  useEffect(() => { if (proxyOk && proxyReceipt) toast.success('Proxy address set onchain') }, [proxyOk, proxyReceipt])
  // eslint-disable-next-line react/set-state-in-effect
  useEffect(() => { if (approverOk && approverReceipt) toast.success('Approver added onchain') }, [approverOk, approverReceipt])

  const wrongChain = chainId !== ARC_TESTNET_ID
  const ensure = () => { if (wrongChain) { switchChain({ chainId: ARC_TESTNET_ID }); return false }; return true }

  const handleSetProxy = () => {
    if (!ensure()) return
    if (!proxyAddr.startsWith('0x')) { toast.error('Invalid address'); return }
    setProxy({ ...PAYPULSE, functionName: 'setProxy', args: [proxyAddr as `0x${string}`], chainId: ARC_TESTNET_ID })
  }

  const handleAddApprover = () => {
    if (!ensure()) return
    if (!approverAddr.startsWith('0x')) { toast.error('Invalid address'); return }
    addApprover({ ...PAYPULSE, functionName: 'addApprover', args: [approverAddr as `0x${string}`], chainId: ARC_TESTNET_ID })
  }

  const proxyStr = typeof currentProxy === 'string' ? currentProxy : ''
  const proxyIsSet = proxyStr && proxyStr !== '0x0000000000000000000000000000000000000000'

  return (
    <div className="space-y-4">
      {/* Set Proxy */}
      <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Settings size={15} className="text-[var(--accent)]" />
          <h3 className="display font-semibold text-[var(--ink)] text-sm">Metering Proxy</h3>
          {proxyIsSet && (
            <span className="ml-auto flex items-center gap-1 text-[10px] font-medium" style={{ color: 'var(--success)' }}>
              <CheckCircle2 size={11} />
              Set
            </span>
          )}
        </div>

        {/* Show current onchain proxy */}
        {proxyIsSet && (
          <div className="rounded-lg px-3 py-2 text-xs space-y-0.5" style={{ background: 'var(--surface-muted)', border: '1px solid var(--border)' }}>
            <div className="text-[10px] uppercase tracking-wide" style={{ color: 'var(--subtle)' }}>Current proxy</div>
            <div className="mono break-all" style={{ color: 'var(--muted)' }}>{proxyStr}</div>
          </div>
        )}

        <p className="text-xs text-[var(--subtle)]">
          Set the authorized proxy wallet that can call <span className="mono">draw()</span>. Use the wallet address matching your <span className="mono">PROXY_PRIVATE_KEY</span> env var.
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="0x... proxy wallet address"
            value={proxyAddr}
            onChange={(e) => setProxyAddr(e.target.value)}
            disabled={proxyPending || proxyConfirming}
            className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface-muted)] px-3 py-2.5 text-xs text-[var(--ink)] placeholder-[var(--subtle)] focus:outline-none focus:border-[var(--accent)] disabled:opacity-50"
          />
          <button
            onClick={handleSetProxy}
            disabled={proxyPending || proxyConfirming || !proxyAddr}
            className="rounded-xl bg-[var(--accent)] text-[#0d1b2f] font-semibold px-4 py-2.5 text-xs hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-40"
          >
            {proxyPending ? 'Confirm…' : proxyConfirming ? 'Setting…' : proxyIsSet ? 'Update' : 'Set'}
          </button>
        </div>
      </div>

      {/* Approvers */}
      <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 space-y-4">
        <div className="flex items-center gap-2">
          <ShieldCheck size={15} className="text-[var(--accent)]" />
          <h3 className="display font-semibold text-[var(--ink)] text-sm">Human Approvers</h3>
          <span className="ml-auto text-xs text-[var(--subtle)]">
            {(approvers as readonly string[] | undefined)?.length ?? 0}/3 set · 2-of-3 required
          </span>
        </div>

        {Boolean(approvers) && (approvers as readonly string[]).length > 0 && (
          <div className="space-y-1">
            {(approvers as readonly `0x${string}`[]).map((a) => (
              <div key={a} className="flex items-center gap-2 mono text-xs text-[var(--muted)] bg-[var(--surface-muted)] rounded-lg px-3 py-2">
                <CheckCircle2 size={11} style={{ color: 'var(--success)', flexShrink: 0 }} />
                {a}
              </div>
            ))}
          </div>
        )}

        {(!approvers || (approvers as readonly string[]).length < 3) && (
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="0x... approver address"
              value={approverAddr}
              onChange={(e) => setApproverAddr(e.target.value)}
              disabled={approverPending || approverConfirming}
              className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface-muted)] px-3 py-2.5 text-xs text-[var(--ink)] placeholder-[var(--subtle)] focus:outline-none focus:border-[var(--accent)] disabled:opacity-50"
            />
            <button
              onClick={handleAddApprover}
              disabled={approverPending || approverConfirming || !approverAddr}
              className="rounded-xl bg-[var(--surface-muted)] border border-[var(--border)] text-[var(--muted)] font-semibold px-4 py-2.5 text-xs hover:border-[var(--accent)] hover:text-[var(--accent)] transition-colors disabled:opacity-40"
            >
              {approverPending ? 'Confirm…' : approverConfirming ? 'Adding…' : 'Add'}
            </button>
          </div>
        )}

        <p className="text-xs text-[var(--subtle)]">
          Max 3 approvers. Borrow requests above 50% of allocation need 2 approvals.
        </p>
      </div>
    </div>
  )
}
