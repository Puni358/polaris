import { useEffect, useReducer, useRef } from 'react'
import { okJson } from './safeFetch.js'

// Full decision trace written by scratch/run_scenario2_full_trace.py.
// Day chunks are fetched lazily and cached, so scrubbing never loads more than
// the day(s) around the playhead.

// The active variant (terminal-rule experiment) is module state set by View 2; every cache
// key includes it so switching variants never mixes records.
export const TRACE_VARIANTS = [
  { id: 'scenario2_initial_state_exact', label: 'Exact rule (end where it started)' },
]
let VARIANT = 'scenario2_initial_state_exact'
export function setTraceVariant(v) { VARIANT = v; manifestPromise = null }
const baseOf = () => `/data/trace/${VARIANT}`
const ck = (day) => `${VARIANT}|${day}`
const dayCache = new Map() // 'YYYY-MM-DD' -> Map(isoTimestamp -> record) | 'missing'
const inflight = new Set()
const whatifCache = new Map() // day -> Map(iso -> whatif record)
const whatifInflight = new Set()
let manifestPromise = null

export function loadTraceManifest() {
  if (!manifestPromise) {
    manifestPromise = fetch(`${baseOf()}/manifest.json`, { cache: 'no-store' })
      .then(okJson)
      .catch(() => null)
  }
  return manifestPromise
}

export function refreshTraceManifest() {
  manifestPromise = null
  return loadTraceManifest()
}

function dayOf(ts) { return String(ts).slice(0, 10) }

export function getTraceRecord(ts) {
  const d = dayCache.get(ck(dayOf(ts)))
  return d ? d.get(new Date(ts).toISOString()) ?? d.get(ts) ?? null : null
}

export function getWhatIf(ts) {
  const d = whatifCache.get(ck(dayOf(ts)))
  return d ? d.get(new Date(ts).toISOString()) ?? d.get(ts) ?? null : null
}

// Fetches the day of every timestamp passed; re-renders the caller when chunks land.
export function useTraceDays(timestamps) {
  const [, bump] = useReducer((x) => x + 1, 0)
  const alive = useRef(true)
  useEffect(() => { alive.current = true; return () => { alive.current = false } }, [])
  const key = timestamps.map(dayOf).filter((v, i, a) => a.indexOf(v) === i).join(',')

  useEffect(() => {
    const base = baseOf()
    for (const day of key.split(',').filter(Boolean)) {
      const k = ck(day)
      if (dayCache.has(k) || inflight.has(k)) continue
      inflight.add(k)
      fetch(`${base}/day_${day}.json`)
        .then(okJson)
        .then((rows) => {
          if (rows) {
            const m = new Map()
            for (const r of rows) m.set(r.timestamp, r)
            // also index by canonical ISO so "+00:00" vs "Z" never matters
            for (const r of rows) m.set(new Date(r.timestamp).toISOString(), r)
            dayCache.set(k, m)
          }
        })
        .catch(() => {})
        .finally(() => { inflight.delete(k); if (alive.current) bump() })
      if (!whatifCache.has(k) && !whatifInflight.has(k)) {
        whatifInflight.add(k)
        fetch(`${base}/whatif_${day}.json`)
          .then(okJson)
          .then((rows) => {
            if (!rows) return
            const m = new Map()
            for (const r of rows) { m.set(r.timestamp, r); m.set(new Date(r.timestamp).toISOString(), r) }
            whatifCache.set(k, m)
          })
          .catch(() => {})
          .finally(() => { whatifInflight.delete(k); if (alive.current) bump() })
      }
    }
  }, [key])
}

// Slim per-hour series of the traced run (same row schema as scenario2.json).
// Returns { series, manifest } or nulls while loading / when no trace exists.
export function useTraceSeries(enabled, variant = 'scenario2_initial_state_exact') {
  const [state, setState] = useReducer((_, a) => a, { series: null, manifest: null, done: false })
  useEffect(() => {
    if (!enabled) { setState({ series: null, manifest: null, done: true }); return }
    let cancelled = false
    setTraceVariant(variant)
    Promise.all([
      refreshTraceManifest(),
      fetch(`${baseOf()}/series.json`, { cache: 'no-store' }).then(okJson).catch(() => null),
    ]).then(([manifest, series]) => {
      if (cancelled) return
      setState({ series: series && series.length > 24 ? series : null, manifest, done: true })
    })
    return () => { cancelled = true }
  }, [enabled, variant])
  return state
}

// Ranked-decisions index (scratch/build_stakes_index.py). Re-fetched every minute while the run is partial.
export function useStakesIndex(variant, enabled = true) {
  const [state, setState] = useReducer((_, a) => a, { rows: null, generated: null })
  useEffect(() => {
    if (!enabled) { setState({ rows: null, generated: null }); return }
    let cancelled = false
    let timer
    const load = () =>
      fetch(`/data/trace/${variant}/stakes_index.json`, { cache: 'no-store' })
        .then(okJson)
        .then((j) => { if (!cancelled && j) setState({ rows: j.rows, generated: j.generated }) })
        .catch(() => {})
        .finally(() => { if (!cancelled) timer = setTimeout(load, 60_000) })
    load()
    return () => { cancelled = true; clearTimeout(timer) }
  }, [variant, enabled])
  return state
}
