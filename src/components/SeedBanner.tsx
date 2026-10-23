/**
 * SeedBanner — guides through the 3-agent demo setup.
 * Research (40%) · Scraper (30%) · Support (30%) · 5-min periods.
 *
 * We fire addAgent transactions sequentially by issuing each next tx
 * inside the onSuccess callback of the *previous* receipt — but since
 * wagmi's useWaitForTransactionReceipt keeps isSuccess=true for the
 * life of the component, we gate on the tx hash changing rather than
 * just isSuccess toggling.
 */
import { useState, useEffect, useRef } from 'react'
import { useAccount, useWriteContract, useWaitForTransactionReceipt, useSwitchChain } from 'wagmi'
import { toast } from 'sonner'
import { PAYPULSE, ARC_TESTNET_ID } from '../contracts/paypulse'
import { Info, ChevronRight, Loader2 } from 'lucide-react'
import { useAgentList } from '../hooks/usePayPulse'

const DEMO_SETUP = [
  { name: 'Research', bps: 4000n, period: 300n, isLender: true,  maxLendBps: 2000n },
  { name: 'Scraper',  bps: 3000n, period: 300n, isLender: false, maxLendBps: 0n   },
  { name: 'Support',  bps: 3000n, period: 300n, isLender: false, maxLendBps: 0n   },
]

// Deterministic demo addresses — no real funds, sandbox-only
const DEMO_ADDRESSES: `0x${string}`[] = [
  '0x1111111111111111111111111111111111111111',
  '0x2222222222222222222222222222222222222222',
  '0x3333333333333333333333333333333333333333',
]

export function SeedBanner({ onSeeded }: { onSeeded?: (names: Record<string, string>) => void }) {
  const { data: list } = useAgentList()
  const { address, chainId } = useAccount()
  const { switchChain } = useSwitchChain()

  // step: 0=idle, 1..3=adding agent #step, 4=all done
  const [step, setStep] = useState(0)
  const [dismissed, setDismissed] = useState(false)
  // Track which tx hash we have already handled to avoid double-firing
  const handledHash = useRef<string | undefined>(undefined)

  const wrongChain = chainId !== ARC_TESTNET_ID
  const agentCount = ((list as readonly string[] | undefined) ?? []).length

  const { writeContract, data: hash } = useWriteContract()
  const { isSuccess } = useWaitForTransactionReceipt({ hash })

  useEffect(() => {
    if (!isSuccess || !hash || hash === handledHash.current) return
    if (step === 0 || step > DEMO_SETUP.length) return

    handledHash.current = hash
    const justAdded = step - 1
    toast.success(`${DEMO_SETUP[justAdded].name} added (${step}/${DEMO_SETUP.length})`)

    if (step < DEMO_SETUP.length) {
      // Fire the next addAgent tx
      const next = DEMO_SETUP[step]
      const nextAddr = DEMO_ADDRESSES[step]
      // eslint-disable-next-line react/set-state-in-effect -- wagmi receipt-driven seed chain
      setStep((s) => s + 1)
      writeContract({
        ...PAYPULSE,
        functionName: 'addAgent',
        args: [nextAddr, next.bps, next.period, next.isLender, next.maxLendBps],
        chainId: ARC_TESTNET_ID,
      })
    } else {
      // Done — seed the proxy and report names
      // eslint-disable-next-line react/set-state-in-effect -- wagmi receipt-driven seed chain
      setStep(DEMO_SETUP.length + 1)
      const names: Record<string, string> = {}
      DEMO_ADDRESSES.forEach((addr, i) => { names[addr.toLowerCase()] = DEMO_SETUP[i].name })
      toast.success('All 3 demo agents added! Seeding proxy…')

      fetch('/api/seed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(
          DEMO_SETUP.map((d, i) => ({
            apiKey: `ppk-${d.name.toLowerCase()}-001`,
            name: d.name,
            agentAddress: DEMO_ADDRESSES[i],
          })),
        ),
      })
        .then(() => toast.success('Proxy seeded — simulator ready'))
        .catch(() => {})

      onSeeded?.(names)
    }
  }, [isSuccess, hash]) // eslint-disable-line react-hooks/exhaustive-deps

  // Hide when agents already exist, dismissed, or wallet disconnected
  if (agentCount > 0 || dismissed || !address) return null
  if (step > DEMO_SETUP.length) return null

  function startSeed() {
    if (!address) return
    if (wrongChain) { switchChain({ chainId: ARC_TESTNET_ID }); return }
    const first = DEMO_SETUP[0]
    setStep(1)
    writeContract({
      ...PAYPULSE,
      functionName: 'addAgent',
      args: [DEMO_ADDRESSES[0], first.bps, first.period, first.isLender, first.maxLendBps],
      chainId: ARC_TESTNET_ID,
    })
  }

  const busy = step > 0 && step <= DEMO_SETUP.length
  const label = busy
    ? `Adding ${DEMO_SETUP[step - 1]?.name ?? ''}… (${step}/${DEMO_SETUP.length})`
    : wrongChain
      ? 'Switch to Arc Testnet'
      : 'Add 3 demo agents  (40 / 30 / 30 split)'

  return (
    <div className="rounded-2xl border border-[var(--accent)]/30 bg-[var(--accent)]/[0.06] p-4 flex items-start gap-3">
      <Info size={16} className="shrink-0 mt-0.5 text-[var(--accent)]" />
      <div className="flex-1 min-w-0">
        <div className="text-sm font-semibold text-[var(--ink)] mb-1">Quick demo setup</div>
        <div className="text-xs text-[var(--subtle)] mb-3">
          Adds Research (40%), Scraper (30%), Support (30%) with 5-minute budget periods.
          Each requires one <span className="mono">addAgent</span> transaction signed by the contract owner.
          Then use the Simulator to drain budgets and trigger borrow escalation.
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={startSeed}
            disabled={busy}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-colors disabled:opacity-60"
            style={{ background: 'var(--accent)', color: '#0d1b2f' }}
          >
            {busy
              ? <><Loader2 size={12} className="animate-spin" /> {label}</>
              : <>{label} <ChevronRight size={12} /></>
            }
          </button>
          <button
            onClick={() => setDismissed(true)}
            className="px-3 py-2 rounded-lg text-xs text-[var(--subtle)] hover:text-[var(--ink)] transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  )
}
