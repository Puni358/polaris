import { useEffect, useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import Donut from '../components/story/Donut.jsx'
import CalendarMap, { DayStrip, OUTCOME, OUTCOME_ORDER, hourOutcome, dayOutcome } from '../components/story/CalendarMap.jsx'
import ProvenanceBadge from '../components/ProvenanceBadge.jsx'
import { classifyStakes } from '../data/stakes.js'
import FeaturedDays, { useFeaturedDays } from '../components/FeaturedDays.jsx'
import { useStakesIndex, TRACE_VARIANTS } from '../data/useTrace.js'
import { okJson } from '../data/safeFetch.js'

const DAY_MS = 86_400_000
const pad = (n) => String(n).padStart(2, '0')

function Card({ title, sub, children, className = '' }) {
  return (
    <div className={`rounded-lg border border-scada-border bg-scada-panel p-4 ${className}`}>
      <h3 className="text-[16px] font-semibold uppercase tracking-[0.14em] text-zinc-300">{title}</h3>
      {sub ? <p className="mb-3 mt-0.5 text-[17px] text-zinc-400">{sub}</p> : <div className="mb-3" />}
      {children}
    </div>
  )
}

function useManifest(variant) {
  const [m, setM] = useState(null)
  useEffect(() => {
    let off = false
    const load = () => fetch(`/data/trace/${variant}/manifest.json`, { cache: 'no-store' }).then(okJson).then((j) => { if (!off) setM(j) }).catch(() => {})
    load()
    const t = setInterval(load, 60_000)
    return () => { off = true; clearInterval(t) }
  }, [variant])
  return m
}

export default function View3DecisionMap({ onNavigateToHour }) {
  const [variant, setVariant] = useState('scenario2_initial_state_exact')
  const [selected, setSelected] = useState(null)
  const featured = useFeaturedDays()
  const [featDay, setFeatDay] = useState(null)
  const manifest = useManifest(variant)
  const { rows } = useStakesIndex(variant)

  const totalHours = manifest?.hours_total ?? 8328
  const startMs = manifest?.days?.[0] ? Date.parse(`${manifest.days[0]}T00:00:00Z`) : Date.parse('2024-01-20T00:00:00Z')
  const totalDays = Math.ceil(totalHours / 24)

  const model = useMemo(() => {
    if (!rows || rows.length === 0) return null
    const days = new Map()
    const byHour = Array.from({ length: 24 }, () => ({ protect: 0, n: 0 }))
    for (const [ts, on, baseFuel, dLoad, dRes, dFuel] of rows) {
      const t = Date.parse(ts)
      const d = Math.floor((t - startMs) / DAY_MS)
      const h = new Date(t).getUTCHours()
      const kind = classifyStakes({ dLoad, dRes, dFuel, baseFuel })
      let info = days.get(d)
      if (!info) { info = { hours: Array(24).fill(null), protectHours: [] }; days.set(d, info) }
      info.hours[h] = { ts, on: on === 1, kind }
      byHour[h].n++
      if (hourOutcome(kind) === 'protect') { info.protectHours.push(h); byHour[h].protect++ }
    }
    const counts = { protect: 0, saved: 0, same: 0, better: 0 }
    let firstProtect = null
    for (const [d, info] of days) {
      info.protectHours.sort((a, b) => a - b)
      info.outcome = dayOutcome(info.hours)
      counts[info.outcome]++
      if (info.outcome === 'protect' && (firstProtect === null || d < firstProtect)) firstProtect = d
    }
    const hourBars = byHour.map((b, h) => ({ h, label: pad(h), days: b.protect }))
    return { days, counts, nDays: days.size, hourBars, firstProtect }
  }, [rows, startMs])

  useEffect(() => { if (model && selected == null) setSelected(model.firstProtect ?? [...model.days.keys()][0]) }, [model, selected])

  const jump = (ts) => onNavigateToHour?.('scenario2', Math.round((Date.parse(ts) - startMs) / 3_600_000), variant)
  const progress = model ? Math.min(1, model.nDays / totalDays) : 0
  const selInfo = model && selected != null ? model.days.get(selected) : null
  const pct = (k) => (model ? Math.round((model.counts[k] / model.nDays) * 100) : 0)

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end justify-between gap-3 px-1">
        <div>
          <h2 className="text-[22px] font-semibold text-zinc-100">Did the model make the right call?</h2>
          <p className="text-[17px] text-zinc-400">We re-ran every hour of the year with the opposite diesel choice. Green = the opposite choice would have lost load or battery reserve.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="h-1.5 w-28 overflow-hidden rounded-full bg-zinc-800"><div className="h-full rounded-full bg-cyan-400" style={{ width: `${progress * 100}%` }} /></div>
            <span className="tnum text-[15px] text-zinc-300">{Math.round(progress * 100)}% of days checked</span>
          </div>
          {TRACE_VARIANTS.length > 1 && <select value={variant} onChange={(e) => { setVariant(e.target.value); setSelected(null) }} className="rounded border border-amber-800 bg-scada-panel2 px-2 py-1 text-[16px] text-amber-300">
            {TRACE_VARIANTS.map((v) => <option key={v.id} value={v.id}>{v.label}</option>)}
          </select>}
          <ProvenanceBadge provenance="SIMULATED" />
        </div>
      </div>

      <FeaturedDays
        days={featured}
        value={featDay}
        note="Picks a day on the calendar and opens its 24 hours."
        onPick={(date) => {
          setFeatDay(date)
          if (date) setSelected(Math.floor((Date.parse(`${date}T00:00:00Z`) - startMs) / DAY_MS))
        }}
      />

      <Card title="Every day of the year">
        {!model ? (
          <div className="flex h-48 items-center justify-center text-[17px] text-zinc-400">No analysed days yet for this run.</div>
        ) : (
          <>
            <CalendarMap days={model.days} startMs={startMs} totalDays={totalDays} selected={selected} onSelect={(d) => { setSelected(d); setFeatDay(null) }} featured={new Set(featured.map((f) => Math.floor((Date.parse(`${f.date}T00:00:00Z`) - startMs) / DAY_MS)))} />
            <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2">
              {OUTCOME_ORDER.map((k) => (
                <span key={k} className="flex items-center gap-2 text-[18px] text-zinc-200">
                  <span className="inline-block h-3.5 w-3.5 rounded" style={{ background: OUTCOME[k].color, opacity: k === 'same' ? 0.55 : 1 }} />
                  {OUTCOME[k].label}
                </span>
              ))}
              <span className="flex items-center gap-2 text-[18px] text-zinc-300"><span className="inline-block h-3.5 w-3.5 rounded bg-[#17171a] ring-1 ring-zinc-700" />Not checked yet</span>
            </div>
            <div className="mt-4 border-t border-scada-border pt-4">
              <DayStrip
                info={selInfo}
                dayLabel={selected != null ? new Date(startMs + selected * DAY_MS).toUTCString().slice(0, 11) : ''}
                onPickHour={jump}
              />
            </div>
          </>
        )}
      </Card>

      {model && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card title="Days by outcome" sub="What the model's choices did, day by day">
            <div className="flex flex-wrap items-center justify-center gap-8 py-2">
              <Donut
                size={210}
                rings={[{ inner: 70, outer: 98, data: OUTCOME_ORDER.filter((k) => model.counts[k] > 0).map((k) => ({ value: model.counts[k], color: OUTCOME[k].color })) }]}
                center={`${model.counts.protect}`}
                sub="days protected"
              />
              <ul className="flex flex-col gap-2.5">
                {OUTCOME_ORDER.map((k) => (
                  <li key={k} className="flex items-center gap-2.5 text-[18px] text-zinc-200">
                    <span className="inline-block h-3.5 w-3.5 rounded" style={{ background: OUTCOME[k].color, opacity: k === 'same' ? 0.55 : 1 }} />
                    <span className="w-44">{OUTCOME[k].label}</span>
                    <span className="tnum text-zinc-300">{model.counts[k]} days · {pct(k)}%</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>

          <Card title="When does it protect load or reserve?" sub="For each hour of the day: on how many days would the OPPOSITE diesel choice have lost load or battery reserve? Taller bar = the model's choice mattered more at that hour.">
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={model.hourBars} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}>
                  <XAxis dataKey="label" tick={{ fill: '#a1a1aa', fontSize: 16 }} axisLine={false} tickLine={false} interval={2} />
                  <YAxis tick={{ fill: '#71717a', fontSize: 15 }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.06)' }}
                    contentStyle={{ background: '#18181b', border: '2px solid #52525b', borderRadius: 8, padding: '10px 14px' }}
                    labelStyle={{ color: '#ffffff', fontSize: 18, fontWeight: 700 }}
                    itemStyle={{ color: '#ffffff', fontSize: 18, fontWeight: 600 }}
                    formatter={(v) => [`${v} of ${model.nDays} days`, 'The opposite diesel choice would have lost load or reserve']}
                    labelFormatter={(l) => `Hour ${l}:00 (UTC)`}
                  />
                  <Bar dataKey="days" radius={[4, 4, 0, 0]} isAnimationActive={false}>
                    {model.hourBars.map((b) => <Cell key={b.h} fill={b.days > 0 ? '#34d399' : '#27272a'} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-center text-[16px] text-zinc-300">hour of the day (UTC)</p>
          </Card>
        </div>
      )}
    </div>
  )
}
