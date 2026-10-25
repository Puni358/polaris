import { useEffect, useState, useMemo } from 'react'
import { okJson } from './safeFetch.js'

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const K_PV_KW = 0.051
const PRICE = 2.5

// Average sunshine energy and diesel litres per day, by month, for the basic controller and for POLARIS,
// from the matched re-runs. Averages (not totals) so the partial first month does not look small.
export function useMonthlyStory(polarisVariant) {
  const [raw, setRaw] = useState(null)
  useEffect(() => {
    if (!polarisVariant) return
    let off = false
    Promise.all([
      fetch('/data/matched/reactive.json').then(okJson),
      fetch(`/data/trace/${polarisVariant}/series.json`, { cache: 'no-store' }).then(okJson),
    ]).then(([reactive, polaris]) => { if (!off) setRaw({ reactive, polaris }) }).catch(() => {})
    return () => { off = true }
  }, [polarisVariant])

  const months = useMemo(() => {
    if (!raw) return null
    const acc = MONTHS.map((m) => ({ month: m, hours: 0, sun: 0, dReactive: 0, dPolaris: 0 }))
    const n = Math.min(raw.reactive.length, raw.polaris.length)
    for (let i = 0; i < n; i++) {
      const p = raw.polaris[i]
      const r = raw.reactive[i]
      const a = acc[new Date(p.timestamp).getUTCMonth()]
      a.hours += 1
      a.sun += Math.min(Math.max(0, p.actual_ghi) * K_PV_KW, 60)
      a.dPolaris += (p.diesel_fuel_cost ?? 0) / PRICE
      a.dReactive += (r.diesel_fuel_cost ?? 0) / PRICE
    }
    return acc.filter((a) => a.hours > 0).map((a) => {
      const days = a.hours / 24
      return { month: a.month, sun: Math.round(a.sun / days), reactive: Math.round(a.dReactive / days), polaris: Math.round(a.dPolaris / days) }
    })
  }, [raw])
  return { months, loading: !months }
}
