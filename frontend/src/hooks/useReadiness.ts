/** useReadiness hook — polls the backend's /ready endpoint for real per-component status. */

import { useEffect, useState } from 'react'
import type { ReadinessResponse } from '../types/api'

const POLL_INTERVAL_MS = 15_000

export function useReadiness() {
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function poll() {
      try {
        const res = await fetch('/ready')
        const data: ReadinessResponse = await res.json()
        if (!cancelled) {
          setReadiness(data)
          setLoading(false)
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unknown error')
          setLoading(false)
        }
      }
    }

    poll()
    const id = window.setInterval(poll, POLL_INTERVAL_MS)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [])

  return { readiness, loading, error }
}
