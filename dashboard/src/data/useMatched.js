import { useEffect, useState } from 'react'
import { okJson } from './safeFetch.js'

// Matched re-run results: every scenario simulated with identical demand, wind and solar.
// Built by scratch/build_matched_aggregates.py -> public/data/matched/aggregates.json.
export function useMatched() {
  const [state, setState] = useState({ loading: true, data: null })
  useEffect(() => {
    let off = false
    let timer
    const load = () =>
      fetch('/data/matched/aggregates.json', { cache: 'no-store' })
        .then(okJson)
        .then((j) => { if (!off) setState({ loading: false, data: j }) })
        .catch(() => { if (!off) setState({ loading: false, data: null }) })
        .finally(() => { if (!off) timer = setTimeout(load, 60_000) })
    load()
    return () => { off = true; clearTimeout(timer) }
  }, [])

  const data = state.data
  let view = null
  if (data?.ready) {
    const S = data.scenarios
    const candidates = ['scenario2_initial_state_exact'].filter((k) => S[k] && S[k].unmet_load_kwh < 0.01)
    const bestId = candidates.sort((a, b) => S[a].diesel_liters - S[b].diesel_liters)[0] ?? 'scenario2_initial_state_exact'
    view = { S, bestId, best: S[bestId], reactive: S.reactive, cand: data.candidates ?? {}, candReady: !!data.cand_ready }
  }
  return { ...state, ready: !!view, view }
}

export const MATCHED_ORDER = ['reactive', 'scenario4', 'scenario3', 'scenario2', 'scenario2_initial_state_exact']
