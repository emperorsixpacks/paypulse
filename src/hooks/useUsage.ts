import { useEffect, useState } from 'react'
import type { UsageEntry } from '../types'

export function useUsageFeed() {
  const [log, setLog] = useState<UsageEntry[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function poll() {
      try {
        const res = await fetch('/api/usage')
        if (!res.ok) throw new Error(`${res.status}`)
        const json = (await res.json()) as { log: UsageEntry[] }
        if (!cancelled) {
          setLog(json.log)
          setError(null)
        }
      } catch (e) {
        if (!cancelled) setError(String(e))
      }
    }

    void poll()
    const id = setInterval(() => { void poll() }, 2500)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  return { log, error }
}
