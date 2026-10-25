import { useEffect, useMemo, useRef } from 'react'
import {
  ComposedChart, Area, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { explainHour, explainFromTrace, hasReasoning, MODES, SOLVER } from '../data/reasoning.js'
import { getTraceRecord, getWhatIf, useTraceDays } from '../data/useTrace.js'
import { classifyStakes, STAKES } from '../data/stakes.js'
import ThoughtFlow from './ThoughtFlow.jsx'

// Real solver trace if that hour was recorded, otherwise the reconstruction.
function explain(series, i, scenarioId) {
  const row = series[i]
  if (!row) return null
  const rec = scenarioId === 'scenario2' ? getTraceRecord(row.timestamp) : null
  return rec ? explainFromTrace(rec) : explainHour(series, i, scenarioId)
}

const TONE = {
  amber: { chip: 'border-amber-700 bg-amber-950/40 text-amber-400', dot: 'bg-amber-400', bar: 'border-amber-700' },
  emerald: { chip: 'border-emerald-700 bg-emerald-950/40 text-emerald-400', dot: 'bg-emerald-400', bar: 'border-emerald-700' },
  cyan: { chip: 'border-cyan-700 bg-cyan-950/40 text-cyan-400', dot: 'bg-cyan-400', bar: 'border-cyan-700' },
  zinc: { chip: 'border-zinc-600 bg-zinc-800/60 text-zinc-300', dot: 'bg-zinc-400', bar: 'border-zinc-600' },
}

const VERDICT = {
  ok: { node: 'border-emerald-700 bg-emerald-950/40 text-emerald-400', icon: '✓' },
  warn: { node: 'border-rose-700 bg-rose-950/40 text-rose-400', icon: '!' },
  action: { node: 'border-amber-700 bg-amber-950/40 text-amber-400', icon: '▲' },
}

const WINDOW_BEFORE = 8
const WINDOW_AFTER = 12

function clock(iso) {
  const d = new Date(iso)
  return `${String(d.getUTCDate()).padStart(2, '0')}/${String(d.getUTCMonth() + 1).padStart(2, '0')} ${String(d.getUTCHours()).padStart(2, '0')}:00`
}

const SCENES = [['why', '1 · Why it decided'], ['next', '2 · Next 24 hours'], ['whatif', '3 · What if…'], ['compare', '4 · Compare models']]

function LadderList({ exp }) {
  return (
    <div className="rounded border border-scada-border bg-scada-panel p-4">
      <h3 className="mb-3 text-[17px] uppercase tracking-wide text-zinc-400">Thought process — in the solver&apos;s priority order</h3>
      <ol className="flex flex-col">
        {exp.ladder.map((s, idx) => {
          const v = VERDICT[s.verdict]
          const last = idx === exp.ladder.length - 1
          return (
            <li key={s.key} className="flex gap-3">
              <div className="flex flex-col items-center">
                <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[16px] font-bold ${v.node}`}>{v.icon}</span>
                {!last && <span className="w-px flex-1 bg-scada-border" />}
              </div>
              <div className={`min-w-0 flex-1 ${last ? '' : 'pb-4'}`}>
                <h4 className="text-[17px] font-semibold text-zinc-200">{idx + 1}. {s.title}</h4>
                <p className="mt-1 text-[17px] leading-relaxed text-zinc-300">{s.text}</p>
              </div>
            </li>
          )
        })}
      </ol>
    </div>
  )
}

export default function ReasoningPanel({ series, scenarioId, playheadIndex, onSelect, scene = 'why', onScene, compare }) {
  const row = series[playheadIndex]
  const instrumented = hasReasoning(row)
  const stamps = useMemo(() => {
    const out = []
    for (let i = Math.max(0, playheadIndex - WINDOW_BEFORE); i <= Math.min(series.length - 1, playheadIndex + WINDOW_AFTER); i++) out.push(series[i].timestamp)
    return out
  }, [series, playheadIndex])
  useTraceDays(scenarioId === 'scenario2' ? stamps : [])
  const exp = explain(series, playheadIndex, scenarioId)

  if (!instrumented || !exp) {
    return (
      <div className="rounded border border-scada-border bg-scada-panel p-6 text-center text-[16px] text-zinc-300">
        <div className="mb-1 text-[17px] font-semibold uppercase tracking-wide text-zinc-400">Optimizer reasoning not recorded for this scenario</div>
        This run did not persist the 24 h forecast horizon, reserve target and planned dispatch the thought process is built from.
        Switch to <span className="text-zinc-300">Scenario 2</span>, the instrumented run.
      </div>
    )
  }

  const tone = TONE[MODES[exp.mode].tone]

  return (
    <div className="grid grid-cols-1 gap-3 lg:grid-cols-[260px_1fr]">
      <DecisionLog series={series} scenarioId={scenarioId} playheadIndex={playheadIndex} onSelect={onSelect} />

      <div className="flex min-w-0 flex-col gap-3">
        {/* Always-visible summary of the hour being explained + the scene switcher */}
        <div className={`sticky top-0 z-20 rounded-lg border-2 bg-scada-bg/95 p-3 backdrop-blur ${tone.bar}`}>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            <span className="tnum text-[18px] font-bold text-white">{clock(row.timestamp)} UTC</span>
            <span className={`rounded border px-2 py-0.5 text-[15px] font-bold tracking-wide ${tone.chip}`}>{MODES[exp.mode].label}</span>
            {exp.startedNow && <span className="rounded border border-amber-700 px-1.5 py-0.5 text-[15px] font-bold text-amber-300">GENERATOR START</span>}
            <span className="tnum text-[17px] font-semibold text-zinc-200">battery {exp.socStart.toFixed(1)} → {exp.socEnd.toFixed(1)}%</span>
            <span className={`tnum text-[17px] font-semibold ${exp.executed > 0 ? 'text-amber-300' : 'text-zinc-200'}`}>diesel {exp.executed.toFixed(0)} kW</span>
          </div>
          <div className="mt-1 text-[18px] font-bold text-zinc-100">{exp.short}</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {SCENES.map(([id, label]) => (
              <button key={id} onClick={() => onScene?.(id)} className={`rounded-lg border-2 px-3 py-1.5 text-[16px] font-bold ${scene === id ? 'border-cyan-400 bg-cyan-950 text-white' : 'border-scada-border text-zinc-300 hover:text-white'}`}>{label}</button>
            ))}
          </div>
        </div>

        {scene === 'why' && (
          <>
            <div className={`rounded-lg border-2 bg-scada-panel p-4 ${tone.bar}`}>
              <div className="mb-1 text-[15px] font-bold uppercase tracking-wide text-zinc-300">Why the model did this</div>
              <p className="text-[20px] font-semibold leading-relaxed text-white">{exp.headline}</p>
            </div>
            {exp.viz ? <ThoughtFlow exp={exp} hourKey={row.timestamp} /> : <LadderList exp={exp} />}
          </>
        )}

        {scene === 'next' && <Lookahead exp={exp} />}

        {scene === 'whatif' && (exp.source === 'trace' ? <WhatIf rec={getTraceRecord(row.timestamp)} wi={getWhatIf(row.timestamp)} /> : <div className="rounded border border-scada-border bg-scada-panel p-4 text-[17px] text-zinc-300">What-if needs the full decision trace.</div>)}

        {scene === 'compare' && compare}

        <p className="px-1 text-[15px] leading-relaxed text-zinc-400">
          {exp.source === 'trace'
            ? 'Every number on this page is the solver\u2019s own recorded input or plan for this hour (full decision trace).'
            : 'Reconstructed from the recorded forecast horizon, reserve target, planned diesel and constraint flags plus the governed solver constants. The solver\u2019s per-step plan was not persisted for this hour; wind is an implied estimate from this run\u2019s own energy balance.'}
        </p>
      </div>
    </div>
  )
}

function Chip({ label, value, accent }) {
  return (
    <div className="rounded border border-scada-border bg-scada-panel2 px-2.5 py-1.5">
      <div className="text-[14px] uppercase tracking-wide text-zinc-400">{label}</div>
      <div className={`tnum text-[18px] ${accent ? 'text-amber-400' : 'text-zinc-200'}`}>{value}</div>
    </div>
  )
}

function DecisionLog({ series, scenarioId, playheadIndex, onSelect }) {
  const activeRef = useRef(null)
  const scrollRef = useRef(null)

  const items = (() => {
    const out = []
    const from = Math.max(0, playheadIndex - WINDOW_BEFORE)
    const to = Math.min(series.length - 1, playheadIndex + WINDOW_AFTER)
    for (let i = from; i <= to; i++) {
      const x = explain(series, i, scenarioId)
      if (x) out.push({ i, ts: series[i].timestamp, mode: x.mode, short: x.short })
    }
    return out
  })()

  useEffect(() => {
    const box = scrollRef.current
    const el = activeRef.current
    if (box && el) box.scrollTop = el.offsetTop - box.clientHeight / 2 + el.clientHeight / 2
  }, [playheadIndex])

  return (
    <div className="flex max-h-[640px] flex-col rounded border border-scada-border bg-scada-panel">
      <div className="border-b border-scada-border px-3 py-2">
        <h3 className="text-[17px] uppercase tracking-wide text-zinc-400">Hourly decision log</h3>
        <p className="text-[15px] text-zinc-400">One reason per hour — click any hour to open its full reasoning.</p>
      </div>
      <div ref={scrollRef} className="relative flex-1 overflow-y-auto">
        {items.map((it) => {
          const active = it.i === playheadIndex
          const tone = TONE[MODES[it.mode].tone]
          return (
            <button
              key={it.i}
              ref={active ? activeRef : null}
              onClick={() => onSelect(it.i)}
              className={`flex w-full items-start gap-2 border-b border-scada-border px-3 py-2 text-left transition-colors ${
                active ? 'bg-scada-panel2' : 'hover:bg-scada-panel2/60'
              }`}
            >
              <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${tone.dot}`} />
              <span className="min-w-0 flex-1">
                <span className={`tnum block text-[15px] ${active ? 'text-amber-400' : 'text-zinc-300'}`}>
                  {clock(it.ts)}{active ? '  ◀ selected' : it.i > playheadIndex ? '  (later)' : ''}
                </span>
                <span className={`block text-[16px] leading-snug ${active ? 'text-zinc-100' : 'text-zinc-400'}`}>{it.short}</span>
              </span>
            </button>
          )
        })}
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-1 border-t border-scada-border px-3 py-2 text-[14px] text-zinc-300">
        <Legend dot="bg-amber-400" t="diesel" />
        <Legend dot="bg-emerald-400" t="renewable charge" />
        <Legend dot="bg-cyan-400" t="discharge" />
        <Legend dot="bg-zinc-400" t="hold" />
      </div>
    </div>
  )
}

function Legend({ dot, t }) {
  return <span className="flex items-center gap-1"><span className={`h-1.5 w-1.5 rounded-full ${dot}`} />{t}</span>
}

function Lookahead({ exp }) {
  const real = exp.source === 'trace'
  const data = exp.traj.map((s) => ({
    label: `+${s.j}h`,
    diesel: real ? Number(s.diesel.toFixed(2)) : 0,
    soc: real ? Number(s.socPlan.toFixed(1)) : Number(Math.max(0, s.socNoDiesel).toFixed(1)),
    solar: Number(s.solar.toFixed(2)),
    wind: Number(s.wind.toFixed(2)),
    demand: Number(s.demand.toFixed(2)),
  }))
  const solarMax = Math.max(2, Math.ceil(Math.max(...data.map((d) => d.solar)) * 1.25))
  const kwMax = Math.ceil(Math.max(40, ...data.map((d) => Math.max(d.demand, d.wind, d.diesel))) / 10) * 10

  return (
    <div className="rounded border border-scada-border bg-scada-panel p-4">
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-[17px] uppercase tracking-wide text-zinc-400">What the optimizer saw — next 24 planning steps</h3>
        <div className="flex flex-wrap items-center gap-3 text-[15px] text-zinc-300">
          <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#2ee6ff]" /> Forecast solar (own scale →)</span>
          <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#64748b]" /> Implied wind</span>
          <span className="flex items-center gap-1.5"><span className="inline-block h-0.5 w-3 bg-white" /> Demand</span>
          {real && <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#ffb21f]/60" /> Planned diesel</span>}
          <span className="flex items-center gap-1.5"><span className="inline-block h-0 w-3 border-b-2 border-dashed border-[#3df0a0]" /> {real ? 'Planned SOC' : 'SOC if no diesel'}</span>
        </div>
      </div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 8, right: 36, left: 4, bottom: 0 }}>
            <defs>
              <linearGradient id="gSol" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2ee6ff" stopOpacity="0.6" /><stop offset="100%" stopColor="#2ee6ff" stopOpacity="0.04" /></linearGradient>
              <linearGradient id="gWind" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#b9c6d6" stopOpacity="0.4" /><stop offset="100%" stopColor="#b9c6d6" stopOpacity="0.03" /></linearGradient>
            </defs>
            <CartesianGrid stroke="#3f3f46" strokeDasharray="3 4" vertical={false} />
            <XAxis dataKey="label" tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} interval={2} />
            <YAxis yAxisId="kw" domain={[0, kwMax]} allowDecimals={false} tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} width={34} label={{ value: 'kW', angle: -90, position: 'insideLeft', fill: '#d4d4d8', fontSize: 14, fontWeight: 600 }} />
            <YAxis yAxisId="soc" orientation="right" domain={[0, 100]} tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} width={30} />
            <YAxis yAxisId="solar" orientation="right" domain={[0, solarMax]} allowDecimals tick={{ fill: '#2ee6ff', fontSize: 15 }} width={34} label={{ value: 'solar kW', angle: 90, position: 'insideRight', fill: '#2ee6ff', fontSize: 14 }} />
            <Tooltip contentStyle={{ background: '#09090b', border: '2px solid #71717a', fontSize: 16, color: '#fff' }} labelStyle={{ color: '#fff', fontWeight: 700 }} itemStyle={{ color: '#f4f4f5' }} />
            <ReferenceLine yAxisId="soc" y={SOLVER.floorPct} stroke="#ff5a73" strokeWidth={2} strokeDasharray="5 4" label={{ value: '20% floor', fill: '#ff5a73', fontSize: 14, position: 'insideBottomRight' }} />
            <Area yAxisId="kw" dataKey="wind" name="Implied wind (kW)" type="monotone" stroke="#b9c6d6" strokeWidth={1.5} fill="#64748b" fillOpacity={0.22} dot={false} isAnimationActive={false} />
            <Area yAxisId="solar" dataKey="solar" name="Forecast solar (kW)" type="monotone" stroke="#2ee6ff" strokeWidth={3.5} fill="url(#gSol)" dot={{ r: 3.5, fill: '#2ee6ff', strokeWidth: 0 }} isAnimationActive={false} />
            {real && <Bar yAxisId="kw" dataKey="diesel" name="Planned diesel (kW)" fill="#ffb21f" fillOpacity={0.9} isAnimationActive={false} />}
            <Line yAxisId="kw" dataKey="demand" name="Demand (kW)" type="stepAfter" stroke="#ffffff" strokeWidth={2.5} dot={false} isAnimationActive={false} />
            <Line yAxisId="soc" dataKey="soc" name={real ? 'Planned SOC (%)' : 'SOC if no diesel (%)'} stroke="#3df0a0" strokeWidth={3.5} strokeDasharray="6 5" dot={false} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-1 text-[15px] text-zinc-400">
        {exp.stats.noSolar ? 'The forecast contains no solar in this window, so the solar trace sits at zero. ' : ''}Solar has its own cyan axis on the right so its shape is readable; at its true scale it would be a flat line under the demand. Step +0h is the hour being decided. {real ? 'The dashed green line is the battery trajectory of the solver\u2019s own plan; amber bars are the diesel it scheduled.' : 'The dashed green line is the battery if the generator never ran; where it meets the red floor is the problem the plan has to solve.'}
      </p>
    </div>
  )
}

const firstOn = (arr) => { const k = arr.findIndex((v) => v > 0); return k < 0 ? null : k }
const f1 = (n) => (Math.round(n * 10) / 10).toFixed(1)

// Classifies how much a different step-0 diesel decision would have mattered,
// walking the solver's own priority order (J1 > J1b > J2 > J3).
export function assessWhatIf(rec, wi) {
  const b = rec.objectives, a = wi.alt
  const banned = wi.alt_kind === 'diesel_banned'
  const dLoad = (a.j1_wh + (a.j1b_wh ?? 0)) - (b.j1_wh + (b.j1b_wh ?? 0))
  const dRes = (a.j2_wh - b.j2_wh) / 1000
  const dFuel = a.j3_litres - b.j3_litres
  const fuelPct = b.j3_litres > 0 ? (dFuel / b.j3_litres) * 100 : 0
  const altWord = banned ? 'banning the generator now' : 'forcing the generator on now'
  const fo = { base: firstOn(rec.plan.diesel_kw), alt: firstOn(a.diesel_kw) }
  const move = banned
    ? (fo.alt == null ? 'The plan would then need no diesel at all.' : `The plan would start diesel at +${fo.alt} instead.`)
    : (fo.base == null ? 'The model plans no diesel at all in 24 h.' : `The model plans its first diesel at +${fo.base}.`)
  const kind = classifyStakes({ dLoad, dRes, dFuel, baseFuel: b.j3_litres })
  let text
  if (kind === 'critical') {
    text = `${banned ? 'Banning' : 'Forcing'} diesel here would leave ${f1(dLoad / 1000)} kWh of load unserved. The model's choice is what keeps the load supplied.`
  } else if (kind === 'reserve') {
    text = `${altWord[0].toUpperCase() + altWord.slice(1)} would open a ${f1(dRes)} kWh reserve shortfall. The model's choice protects the reserve.`
  } else if (kind === 'better' && (dLoad < -1 || dRes < -0.05)) {
    text = `${altWord[0].toUpperCase() + altWord.slice(1)} would improve ${dLoad < -1 ? 'load served' : 'the reserve'} — a candidate for changing the rule.`
  } else if (kind === 'neartie') {
    text = `${altWord[0].toUpperCase() + altWord.slice(1)} changes fuel by only ${dFuel >= 0 ? '+' : ''}${f1(dFuel)} L (${fuelPct >= 0 ? '+' : ''}${fuelPct.toFixed(1)}%) and nothing else — load, reserve and curtailment are untouched. This hour is a coin-flip on timing; the same diesel just runs at a different time. ${move}`
  } else if (kind === 'costly') {
    text = `${altWord[0].toUpperCase() + altWord.slice(1)} would burn ${f1(dFuel)} L more over the 24 h plan (+${fuelPct.toFixed(1)}%) with no benefit to load or reserve. The model's choice saves that fuel. ${move}`
  } else {
    text = `${altWord[0].toUpperCase() + altWord.slice(1)} would burn ${f1(-dFuel)} L less (${fuelPct.toFixed(1)}%) with equal load and reserve — the model's choice leaves fuel on the table.`
  }
  return { kind, text, dLoad, dRes, dFuel, fuelPct, banned }
}

function WhatIf({ rec, wi }) {
  if (!rec) return null
  if (!wi) {
    return (
      <div className="rounded border border-scada-border bg-scada-panel p-4 text-[16px] text-zinc-400">
        Decision stakes for this hour have not been computed yet (the what-if pass is still catching up with the trace).
      </div>
    )
  }
  const as = assessWhatIf(rec, wi)
  const st = STAKES[as.kind]
  const b = rec.objectives, a = wi.alt

  // Only objectives that actually differ are listed; the rest collapse into one line.
  const diffs = []
  const quiet = []
  const push = (k, base, alt, unit, dec = 1) => {
    const d = alt - base
    if (Math.abs(d) < (unit === 'Wh' ? 1.5 : 0.05)) quiet.push(k)
    else diffs.push({ k, base, alt, d, unit, dec })
  }
  push('Critical load unserved', b.j1_wh, a.j1_wh, 'Wh', 0)
  push('Non-critical load unserved', b.j1b_wh, a.j1b_wh ?? 0, 'Wh', 0)
  push('Reserve shortfall', b.j2_wh / 1000, a.j2_wh / 1000, 'kWh')
  push('Fuel over the 24 h plan', b.j3_litres, a.j3_litres, 'L')
  push('Renewables curtailed', b.j4_wh / 1000, a.j4_wh / 1000, 'kWh')
  push('Lowest planned battery level', Math.min(...rec.plan.soc_pct), a.min_soc_pct, '%')
  push('Diesel hours in plan', rec.plan.diesel_hours_planned, a.diesel_hours, 'h', 0)

  const data = rec.plan.diesel_kw.map((v, j) => ({
    label: `+${j}h`,
    mDiesel: v, aDiesel: a.diesel_kw[j],
    mSoc: rec.plan.soc_pct[j], aSoc: a.soc_pct[j],
  }))
  const kwMax = Math.max(20, ...data.map((d) => Math.max(d.mDiesel, d.aDiesel)))

  return (
    <div className="rounded border border-scada-border bg-scada-panel p-4">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-[17px] uppercase tracking-wide text-zinc-400">
          Decision stakes — {as.banned ? 'what if diesel had been banned now?' : 'what if diesel had been forced on now?'}
        </h3>
        <span className={`rounded border px-2 py-0.5 text-[15px] font-semibold tracking-wide ${st.cls}`}>{st.label}</span>
      </div>
      <p className="mb-3 text-[18px] leading-relaxed text-zinc-200">{as.text}</p>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 8, right: 36, left: 4, bottom: 0 }}>
            <defs>
              <linearGradient id="gSol" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2ee6ff" stopOpacity="0.6" /><stop offset="100%" stopColor="#2ee6ff" stopOpacity="0.04" /></linearGradient>
              <linearGradient id="gWind" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#b9c6d6" stopOpacity="0.4" /><stop offset="100%" stopColor="#b9c6d6" stopOpacity="0.03" /></linearGradient>
            </defs>
            <CartesianGrid stroke="#3f3f46" strokeDasharray="3 4" vertical={false} />
            <XAxis dataKey="label" tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} interval={2} />
            <YAxis yAxisId="kw" domain={[0, Math.ceil(kwMax / 10) * 10]} allowDecimals={false} tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} width={34} label={{ value: 'diesel kW', angle: -90, position: 'insideLeft', fill: '#d4d4d8', fontSize: 14, fontWeight: 600 }} />
            <YAxis yAxisId="soc" orientation="right" domain={[0, 100]} tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} width={30} />
            <Tooltip contentStyle={{ background: '#09090b', border: '2px solid #71717a', fontSize: 16, color: '#fff' }} labelStyle={{ color: '#fff', fontWeight: 700 }} itemStyle={{ color: '#f4f4f5' }} />
            <ReferenceLine yAxisId="soc" y={SOLVER.floorPct} stroke="#ff5a73" strokeWidth={2} strokeDasharray="5 4" />
            <Bar yAxisId="kw" dataKey="mDiesel" name="Model's diesel (kW)" fill="#ffb21f" fillOpacity={0.95} isAnimationActive={false} />
            <Bar yAxisId="kw" dataKey="aDiesel" name="Alternative diesel (kW)" fill="#b79cff" fillOpacity={0.85} isAnimationActive={false} />
            <Line yAxisId="soc" dataKey="mSoc" name="Model's battery (%)" stroke="#3df0a0" strokeWidth={3.5} dot={false} isAnimationActive={false} />
            <Line yAxisId="soc" dataKey="aSoc" name="Alternative battery (%)" stroke="#d9ccff" strokeWidth={3.5} strokeDasharray="6 5" dot={false} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="mb-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-[15px] text-zinc-300">
        <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#ffb21f]/75" /> Model&apos;s diesel</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#b79cff]/60" /> Alternative diesel</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-0.5 w-3 bg-[#3df0a0]" /> Model&apos;s battery</span>
        <span className="flex items-center gap-1.5"><span className="inline-block h-0 w-3 border-b-2 border-dashed border-[#d9ccff]" /> Alternative battery</span>
        <span className="text-zinc-400">red line = 20% floor</span>
      </div>

      {diffs.length > 0 && (
        <ul className="mb-2 flex flex-col gap-1">
          {diffs.map((r) => {
            const worse = r.k === 'Lowest planned battery level' ? r.d < 0 : r.k === 'Diesel hours in plan' ? false : r.d > 0
            return (
              <li key={r.k} className="flex items-baseline justify-between gap-3 text-[16px]">
                <span className="text-zinc-300">{r.k}</span>
                <span className="tnum text-zinc-300">
                  {r.base.toFixed(r.dec)} → {r.alt.toFixed(r.dec)} {r.unit}
                  <span className={`ml-2 ${r.k === 'Diesel hours in plan' ? 'text-zinc-400' : worse ? 'text-rose-400' : 'text-emerald-400'}`}>
                    ({r.d > 0 ? '+' : ''}{r.d.toFixed(r.dec)})
                  </span>
                </span>
              </li>
            )
          })}
        </ul>
      )}
      {quiet.length > 0 && (
        <p className="text-[15px] text-zinc-400">No difference in: {quiet.join(', ').toLowerCase()}.</p>
      )}
      <p className="mt-1 text-[15px] text-zinc-400">
        Same inputs re-solved by the optimizer itself; values are its own plan, compared in its priority order (load › reserve › fuel).
        {wi.baseline_match ? '' : ' (The replay chose a tied step-0 diesel differently from the recorded run — treat deltas as indicative.)'}
      </p>
    </div>
  )
}
