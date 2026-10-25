import { useEffect, useState } from 'react'
import { okJson } from './safeFetch.js'

const seriesCache = new Map()

// Hourly run series of one POLARIS variant (same rows the Decision Inspector uses) plus the real Nuolja
// weather aligned to the same hours. The partial series of a run still in progress is fine: the replay
// simply covers the hours that exist.
export function useReplayData(variant) {
  const [state, setState] = useState({ series: null, weather: null })
  useEffect(() => {
    if (!variant) return
    let off = false
    const getSeries = seriesCache.has(variant)
      ? Promise.resolve(seriesCache.get(variant))
      : fetch(`/data/trace/${variant}/series.json`, { cache: 'no-store' }).then(okJson).then((j) => { if (j) seriesCache.set(variant, j); return j })
    Promise.all([getSeries, fetch('/data/matched/weather.json').then(okJson)])
      .then(([series, weather]) => { if (!off) setState({ series, weather }) })
      .catch(() => {})
    return () => { off = true }
  }, [variant])
  return state
}

export const SIM = { kPv: 0.051, pvCapKw: 60 }
// Wind is a simulation input (clock-based formula shared by every scenario), never a measurement.
export const windKw = (iso) => 15 + 10 * Math.sin(new Date(iso).getUTCHours() * Math.PI / 6)
