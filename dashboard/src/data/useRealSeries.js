import { useEffect, useState } from 'react'

const cache = new Map()

// Fetches the real per-hour solver CSV (pre-converted to JSON at
// public/data/<scenario>.json) for a scenario. Returns { data, loading,
// error }. Cached in-memory across components/views so switching tabs
// doesn't refetch an 8,328-row file repeatedly.
export function useRealSeries(scenarioId) {
  const [state, setState] = useState(() => {
    const cached = cache.get(scenarioId)
    return cached ? { data: cached, loading: false, error: null } : { data: null, loading: true, error: null }
  })

  useEffect(() => {
    let cancelled = false
    if (cache.has(scenarioId)) {
      setState({ data: cache.get(scenarioId), loading: false, error: null })
      return
    }
    setState({ data: null, loading: true, error: null })
    fetch(`/data/${scenarioId}.json`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((json) => {
        if (cancelled) return
        cache.set(scenarioId, json)
        setState({ data: json, loading: false, error: null })
      })
      .catch((err) => {
        if (cancelled) return
        setState({ data: null, loading: false, error: err.message })
      })
    return () => { cancelled = true }
  }, [scenarioId])

  return state
}
