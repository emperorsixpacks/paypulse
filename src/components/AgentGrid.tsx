import { useState } from 'react'
import { useAgentList, useAgents } from '../hooks/usePayPulse'
import { AgentCard } from './AgentCard'
import { Users } from 'lucide-react'

// Name map: address → display name (populated by demo seed)
const DEMO_NAMES: Record<string, string> = {}

export function setDemoName(address: string, name: string) {
  DEMO_NAMES[address.toLowerCase()] = name
}

export function AgentGrid({
  nameOverrides = {},
  onSelect,
}: {
  nameOverrides?: Record<string, string>
  onSelect?: (addr: string) => void
}) {
  const { data: list } = useAgentList()
  const addresses = (list ?? []) as `0x${string}`[]
  const agents = useAgents(addresses)
  const [selected, setSelected] = useState<string | null>(null)

  const names: Record<string, string> = { ...DEMO_NAMES, ...nameOverrides }
  const getName = (addr: string) =>
    names[addr.toLowerCase()] ?? `Agent ${addr.slice(2, 6).toUpperCase()}`

  function handleSelect(addr: string) {
    setSelected(addr)
    onSelect?.(addr)
  }

  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <div className="flex items-center gap-2 mb-4">
        <Users size={16} className="text-[var(--accent)]" />
        <h2 className="display font-semibold text-[var(--ink)]">Agents</h2>
        <span className="ml-auto text-[11px] text-[var(--subtle)]">{agents.length} registered</span>
      </div>

      {agents.length === 0 ? (
        <div className="text-sm text-[var(--subtle)] text-center py-8">
          No agents yet. Add agents via the panel below.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
          {agents.map((a) => (
            <AgentCard
              key={a.address}
              agent={a}
              name={getName(a.address)}
              selected={selected === a.address}
              onClick={() => handleSelect(a.address)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
