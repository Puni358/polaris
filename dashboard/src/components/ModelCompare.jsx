import { Fragment, useEffect, useMemo, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useMatched } from '../data/useMatched.js'
import { okJson } from '../data/safeFetch.js'

const BEST = 'scenario2_initial_state_exact'
// Same station, same weather, demand and wind for every row; only the controller or the solar forecaster changes.
const MODELS = [
  { id: 'reactive', label: 'Basic controller', group: 'Controllers', color: '#94a3b8' },
  { id: 'scenario4', label: 'Scenario 4 — forecast, no safety cushion', group: 'Controllers', color: '#f59e0b' },
  { id: 'scenario3', label: 'Scenario 3 — fixed big cushion', group: 'Controllers', color: '#a78bfa' },
  { id: 'scenario2', label: 'Scenario 2 — with the +30 kWh end rule', group: 'Controllers', color: '#22d3ee' },
  { id: BEST, label: 'POLARIS — Scenario 2, end where it started', group: 'POLARIS', color: '#34d399', best: true },
  { id: 'cand_baseline', label: 'Forecaster: physical baseline', group: 'Other forecasters (same optimizer)', color: '#e879f9' },
  { id: 'cand_successor_v2', label: 'Forecaster: Successor v2', group: 'Other forecasters (same optimizer)', color: '#fb7185' },
  { id: 'cand_k', label: 'Forecaster: Candidate K', group: 'Other forecasters (same optimizer)', color: '#22d3ee' },
  { id: 'cand_n1', label: 'Forecaster: Candidate N1', group: 'Other forecasters (same optimizer)', color: '#fde047' },
]
const START = Date.parse('2024-01-20T00:00:00Z')

async function loadDay(model, date, reactive) {
  if (model.id === 'reactive') {
    if (!reactive) return null
    const i0 = Math.round((Date.parse(`${date}T00:00:00Z`) - START) / 3_600_000)
    const rows = reactive.slice(i0, i0 + 24)
    if (rows.length < 24) return null
    return rows.map((r) => ({ soc: r.battery_soc_pct, litres: (r.diesel_fuel_cost ?? 0) / 2.5, kw: r.diesel_kw, lost: (r.unmet_load_w ?? 0) / 1000 }))
  }
  const res = await fetch(`/data/trace/${model.id}/day_${date}.json`).catch(() => null)
  const j = await okJson(res)
  if (!j) return null
  return j.map((r) => ({ soc: r.executed.soc_after_pct, litres: r.executed.fuel_l, kw: r.executed.diesel_kw, lost: r.executed.physics_unserved_kwh }))
}

const sum = (a, k) => a.reduce((s, r) => s + r[k], 0)

export default function ModelCompare({ date }) {
  const { view } = useMatched()
  const [reactive, setReactive] = useState(null)
  const [days, setDays] = useState({}) // id -> rows | null
  const [on, setOn] = useState(() => new Set(['reactive', 'scenario4', BEST]))

  useEffect(() => { fetch('/data/matched/reactive.json').then(okJson).then(setReactive).catch(() => {}) }, [])
  useEffect(() => {
    if (!date || !reactive) return undefined
    let off = false
    setDays({})
    Promise.all(MODELS.map(async (m) => [m.id, await loadDay(m, date, reactive)])).then((pairs) => { if (!off) setDays(Object.fromEntries(pairs)) })
    return () => { off = true }
  }, [date, reactive])

  const stats = useMemo(() => {
    const o = {}
    for (const m of MODELS) {
      const d = days[m.id]
      if (!d) { o[m.id] = null; continue }
      o[m.id] = { litres: sum(d, 'litres'), hours: d.filter((r) => r.kw > 0).length, minSoc: Math.min(...d.map((r) => r.soc)), lost: sum(d, 'lost') }
    }
    return o
  }, [days])

  const chart = useMemo(() => {
    if (!Object.keys(days).length) return []
    return Array.from({ length: 24 }, (_, h) => {
      const row = { hour: `${String(h).padStart(2, '0')}:00` }
      for (const m of MODELS) {
        const d = days[m.id]
        if (!d) continue
        row[`soc_${m.id}`] = +d[h].soc.toFixed(1)
        row[`cum_${m.id}`] = +d.slice(0, h + 1).reduce((s, r) => s + r.litres, 0).toFixed(1)
      }
      return row
    })
  }, [days])

  if (!date) {
    return <div className="rounded-lg border border-scada-border bg-scada-panel p-5 text-[18px] font-semibold text-zinc-300">Pick a day above to compare every controller and forecaster on that same day.</div>
  }
  const best = stats[BEST]
  const yearOf = (id) => (id === BEST ? view?.S?.[BEST] : id.startsWith('cand_') ? view?.cand?.[id] : view?.S?.[id])

  const verdict = (id) => {
    if (id === BEST) return { t: 'reference', c: 'text-emerald-300' }
    const s = stats[id]
    if (!s || !best) return { t: '—', c: 'text-zinc-400' }
    const d = s.litres - best.litres
    const tol = Math.max(1, best.litres * 0.01)
    if (s.lost > best.lost + 0.05) return { t: `loses ${s.lost.toFixed(1)} kWh of load`, c: 'text-rose-300' }
    if (Math.abs(d) <= tol) return { t: 'about the same', c: 'text-zinc-200' }
    return d > 0 ? { t: `worse: +${d.toFixed(0)} L`, c: 'text-rose-300' } : { t: `better: ${d.toFixed(0)} L`, c: 'text-emerald-300' }
  }
  const yearVerdict = (id) => {
    const y = yearOf(id)
    const b = view?.S?.[BEST]
    if (!y || !b) return { t: '—', c: 'text-zinc-400' }
    if (id.startsWith('cand_') && !(y.hours >= y.hours_total)) return { t: `running ${Math.round((y.hours / y.hours_total) * 100)}%`, c: 'text-amber-300' }
    if (id === BEST) return { t: `${Math.round(y.diesel_liters).toLocaleString()} L`, c: 'text-emerald-300' }
    const d = y.diesel_liters - b.diesel_liters
    const tag = Math.abs(d) <= b.diesel_liters * 0.01 ? 'about the same' : d > 0 ? `worse +${(d / 1000).toFixed(1)}k L` : `better ${(d / 1000).toFixed(1)}k L`
    return { t: `${Math.round(y.diesel_liters).toLocaleString()} L · ${tag}${y.unmet_load_kwh >= 0.05 ? ` · ${y.unmet_load_kwh.toFixed(1)} kWh lost` : ''}`, c: Math.abs(d) <= b.diesel_liters * 0.01 ? 'text-zinc-200' : d > 0 ? 'text-rose-300' : 'text-emerald-300' }
  }
  const groups = [...new Set(MODELS.map((m) => m.group))]
  const toggle = (id) => setOn((s) => { const n = new Set(s); if (n.has(id)) n.delete(id); else n.add(id); return n })
  const shown = MODELS.filter((m) => on.has(m.id) && days[m.id])

  return (
    <div className="rounded-lg border border-scada-border bg-scada-panel p-5">
      <h3 className="text-[22px] font-bold text-white">Same day, every controller and forecaster</h3>
      <p className="mb-3 text-[17px] font-semibold text-zinc-300">Identical weather, demand and wind. Only the controller, or the solar forecaster feeding the same optimizer, changes. The right-hand column adds the full year so one day never tells the whole story.</p>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] border-collapse text-left">
          <thead>
            <tr className="text-[15px] font-bold uppercase tracking-wide text-zinc-300">
              <th className="px-2 py-2">Show</th><th className="px-2 py-2">Model</th><th className="px-2 py-2">Diesel this day</th><th className="px-2 py-2">Gen. hours</th><th className="px-2 py-2">Min battery</th><th className="px-2 py-2">Load lost</th><th className="px-2 py-2">vs POLARIS (this day)</th><th className="px-2 py-2">Full year</th>
            </tr>
          </thead>
          <tbody>
            {groups.map((g) => (
              <Fragment key={g}>
                <tr><td colSpan={8} className="bg-scada-panel2 px-2 py-1 text-[15px] font-bold text-cyan-300">{g}</td></tr>
                {MODELS.filter((m) => m.group === g).map((m) => {
                  const s = stats[m.id]
                  const v = verdict(m.id)
                  const yv = yearVerdict(m.id)
                  return (
                    <tr key={m.id} className={`border-t border-scada-border text-[17px] ${m.best ? 'bg-emerald-950/20' : ''}`}>
                      <td className="px-2 py-2"><input type="checkbox" checked={on.has(m.id)} onChange={() => toggle(m.id)} className="h-5 w-5" style={{ accentColor: m.color }} /></td>
                      <td className="px-2 py-2 font-bold" style={{ color: m.color }}>{m.label}</td>
                      <td className="tnum px-2 py-2 font-bold text-white">{s ? `${s.litres.toFixed(0)} L` : '—'}</td>
                      <td className="tnum px-2 py-2 text-zinc-100">{s ? s.hours : '—'}</td>
                      <td className="tnum px-2 py-2 text-zinc-100">{s ? `${s.minSoc.toFixed(1)}%` : '—'}</td>
                      <td className={`tnum px-2 py-2 font-bold ${s && s.lost > 0.05 ? 'text-rose-300' : 'text-emerald-300'}`}>{s ? `${s.lost.toFixed(1)} kWh` : '—'}</td>
                      <td className={`px-2 py-2 font-bold ${v.c}`}>{s || m.best ? v.t : (m.id.startsWith('cand_') ? 'run not at this day yet' : '—')}</td>
                      <td className={`px-2 py-2 font-semibold ${yv.c}`}>{yv.t}</td>
                    </tr>
                  )
                })}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-[15px] font-semibold text-zinc-400">Perfect-foresight “Scenario 1” is not shown: it was only simulated on a different window and set of inputs, so it cannot be compared fairly.</p>

      {shown.length > 0 && (
        <div className="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-2">
          {[['soc', 'Battery level through the day (%)', '%'], ['cum', 'Diesel burned so far (litres)', ' L']].map(([k, title, unit]) => (
            <div key={k}>
              <div className="mb-1 text-[17px] font-bold text-white">{title}</div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chart} margin={{ top: 6, right: 10, left: -6, bottom: 0 }}>
                    <CartesianGrid stroke="#27272a" strokeDasharray="2 4" vertical={false} />
                    <XAxis dataKey="hour" tick={{ fill: '#d4d4d8', fontSize: 14 }} interval={3} />
                    <YAxis tick={{ fill: '#d4d4d8', fontSize: 14 }} width={46} domain={k === 'soc' ? [0, 100] : [0, 'auto']} unit={unit.trim()} />
                    <Tooltip contentStyle={{ background: '#18181b', border: '2px solid #52525b' }} labelStyle={{ color: '#fff', fontSize: 16, fontWeight: 700 }} itemStyle={{ color: '#fff', fontSize: 15 }} />
                    {k === 'soc' && <Legend wrapperStyle={{ fontSize: 14 }} />}
                    {shown.map((m) => <Line key={m.id} dataKey={`${k}_${m.id}`} name={m.label.replace('Forecaster: ', '').replace(' — Scenario 2, end where it started', '')} stroke={m.color} strokeWidth={m.best ? 4 : 2.2} dot={false} isAnimationActive={false} />)}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
