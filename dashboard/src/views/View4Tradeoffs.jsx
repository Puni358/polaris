import ProvenanceBadge from '../components/ProvenanceBadge.jsx'
import { Bulb, Diesel } from '../components/story/Icons.jsx'
import Pending from '../components/story/Pending.jsx'
import { useMatched } from '../data/useMatched.js'

// Forecaster lineage (clean, causal models only). Source: forecasting/reports/other/README_FORECASTING_RESEARCH_COMPENDIUM.md, section 7.
// MAE in W/m². ODD = held-out odd-origin test of 2024 (even origins are used for training / CV);
// BLIND = one-shot 2025 test that was never used for fitting or selection.
const FORECASTERS = [
  { id: 'cand_baseline', name: 'Physical baseline (Chronos-3B + cloud clear-sky)', odd: 43.43, blind: 41.77, tag: 'BASELINE', tone: '#94a3b8' },
  { id: 'cand_successor_v2', name: 'Successor v2 (33 causal inputs)', odd: 38.77, blind: 38.19, tag: 'BASELINE', tone: '#94a3b8' },
  { id: 'cand_k', name: 'Candidate K (35 inputs, baseline-conditioned)', odd: 37.72, blind: 37.46, tag: 'CONTROL', tone: '#38bdf8' },
  { id: 'cand_n1', name: 'Candidate N1 (36 inputs, single model)', odd: 37.46, blind: 37.27, tag: 'ON HOLD', tone: '#fbbf24' },
  { id: 'scenario2_initial_state_exact', name: 'Candidate N6 — used in POLARIS', odd: 37.2, blind: 36.79, tag: 'PASSED ALL GATES', tone: '#34d399', ours: true },
]
const AX_MIN = 34
const AX_MAX = 44

const ROW_STYLE = {
  reactive: { name: 'Basic controller', color: '#94a3b8' },
  scenario4: { name: 'Forecast, no safety cushion', color: '#f59e0b' },
  scenario2_initial_state_exact: { name: 'POLARIS', color: '#34d399', ours: true },
}

function Stat({ big, label, icon, color }) {
  return (
    <div className="flex items-center gap-4 rounded-lg border border-scada-border bg-scada-panel p-4">
      <svg width="46" height="46" viewBox="0 0 40 40" className="shrink-0">{icon}</svg>
      <div>
        <div className="tnum text-[40px] font-semibold leading-none" style={{ color }}>{big}</div>
        <div className="mt-1 text-[17px] font-semibold tracking-wide text-zinc-300">{label}</div>
      </div>
    </div>
  )
}

export default function View4Proof() {
  const { data, ready, view } = useMatched()
  if (!ready) {
    return (
      <div className="flex flex-col gap-4">
        <h2 className="px-1 text-[22px] font-semibold text-zinc-100">Proof</h2>
        <Pending data={data} />
      </div>
    )
  }
  const A = view.S
  const R = view.reactive
  const P = view.best
  const litresSaved = Math.round(R.diesel_liters - P.diesel_liters)
  const co2Tonnes = (litresSaved * 2.68) / 1000 // diesel combustion: about 2.68 kg CO2 per litre
  const rows = Object.keys(ROW_STYLE).map((id) => ({ id, ...ROW_STYLE[id], litres: A[id].diesel_liters, lostKwh: A[id].unmet_load_kwh, lostH: A[id].unmet_load_hours }))
  const maxL = Math.max(...rows.map((r) => r.litres))
  const PRICE_ROWS = [
    { label: 'Generator starts', a: R.diesel_starts, b: P.diesel_starts, tone: '#fb923c', delta: `${(P.diesel_starts / R.diesel_starts).toFixed(1)}× ${P.diesel_starts >= R.diesel_starts ? 'more' : 'fewer'}` },
    { label: 'Battery full cycles', a: Math.round(R.battery_cycles), b: Math.round(P.battery_cycles), tone: '#fb923c', delta: `${(P.battery_cycles / R.battery_cycles).toFixed(1)}× ${P.battery_cycles >= R.battery_cycles ? 'more' : 'fewer'}` },
    { label: 'Generator running hours', a: R.diesel_run_hours, b: P.diesel_run_hours, tone: '#34d399', delta: `${Math.abs(Math.round((1 - P.diesel_run_hours / R.diesel_run_hours) * 100))}% ${P.diesel_run_hours <= R.diesel_run_hours ? 'fewer' : 'more'}` },
  ]

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end justify-between gap-2 px-1">
        <div>
          <h2 className="text-[22px] font-semibold text-zinc-100">{litresSaved > 0 ? 'Less diesel. Same lights.' : 'How the options compare'}</h2>
          <p className="text-[17px] text-zinc-400">Same station, same 347 days of weather, demand and wind — three ways to run it.</p>
        </div>
        <ProvenanceBadge provenance="SIMULATED" />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Stat big={`${co2Tonnes.toFixed(0)} t`} label="of CO₂ not emitted (2.68 kg per litre)" color="#6ee7b7" icon={<Diesel c="#34d399" />} />
        <Stat big={`${(litresSaved / 1000).toFixed(1)}k L`} label="diesel not burned" color="#fdba74" icon={<Diesel c="#f97316" />} />
        <Stat big={`${P.unmet_load_hours} h`} label="of power lost" color="#fde68a" icon={<Bulb on c="#facc15" />} />
      </div>

      <div className="rounded-lg border border-scada-border bg-scada-panel p-5">
        <h3 className="mb-3 text-[18px] font-bold text-white">Load not served over the whole year — POLARIS</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {[['Critical load', P.critical_unmet_kwh], ['Non-critical load', P.noncritical_unmet_kwh]].map(([name, v]) => (
            <div key={name} className={`flex items-center justify-between rounded-lg border-2 px-4 py-3 ${(v ?? 0) < 0.05 ? 'border-emerald-600 bg-emerald-950/30' : 'border-rose-600 bg-rose-950/30'}`}>
              <span className="text-[20px] font-bold text-white">{name}</span>
              <span className={`tnum text-[28px] font-extrabold ${(v ?? 0) < 0.05 ? 'text-emerald-300' : 'text-rose-300'}`}>{(v ?? 0).toFixed(1)} kWh {(v ?? 0) < 0.05 ? '✓' : ''}</span>
            </div>
          ))}
        </div>
        <p className="mt-2 text-[16px] font-semibold text-zinc-300">The optimizer&apos;s own plan for every hour that was carried out: 8,328 hours, none shed.</p>
      </div>

      <div className="rounded-lg border border-scada-border bg-scada-panel p-5">
        <h3 className="mb-4 text-[18px] font-bold text-white">Diesel burned over the year, and power lost</h3>
        <div className="flex flex-col gap-4">
          {rows.map((r) => {
            const saving = Math.round((1 - r.litres / A.reactive.diesel_liters) * 100)
            return (
              <div key={r.id} className="grid grid-cols-1 items-center gap-x-4 gap-y-1 lg:grid-cols-[300px_1fr_190px]">
                <div className={`text-[19px] ${r.ours ? 'font-extrabold text-white' : 'font-semibold text-zinc-200'}`}>{r.name}</div>
                <div className="relative h-9 overflow-hidden rounded-md bg-zinc-800/70">
                  <div className="h-full rounded-md" style={{ width: `${(r.litres / maxL) * 100}%`, background: r.color, opacity: r.ours ? 1 : 0.75 }} />
                  <div className="tnum absolute inset-y-0 left-3 flex items-center text-[19px] font-bold text-zinc-950">{Math.round(r.litres).toLocaleString()} L{r.id !== 'reactive' && <span className="ml-3 text-[17px] font-bold">−{saving}%</span>}</div>
                </div>
                <div className={`tnum rounded-md border-2 px-3 py-1.5 text-center text-[18px] font-bold ${r.lostKwh < 0.05 ? 'border-emerald-600 bg-emerald-950/40 text-emerald-300' : 'border-rose-600 bg-rose-950/40 text-rose-300'}`}>
                  {r.lostKwh < 0.05 ? '✓ no power lost' : `${r.lostKwh.toFixed(1)} kWh lost (${r.lostH} h)`}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-rose-900/60 bg-scada-panel p-4">
          <h3 className="mb-3 text-[16px] font-semibold uppercase tracking-[0.14em] text-zinc-300">Forecast, but no safety cushion</h3>
          <div className="flex items-center gap-5">
            <svg width="64" height="64" viewBox="0 0 40 40"><Bulb on={false} /></svg>
            <div>
              <div className="tnum text-[44px] font-semibold leading-none text-rose-400">{A.scenario4.unmet_load_hours} h</div>
              <div className="mt-1 text-[18px] font-semibold text-zinc-300">lost power · {A.scenario4.unmet_load_kwh.toFixed(1)} kWh</div>
            </div>
          </div>
        </div>
        <div className="rounded-lg border border-emerald-900/60 bg-scada-panel p-4">
          <h3 className="mb-3 text-[16px] font-semibold uppercase tracking-[0.14em] text-zinc-300">POLARIS</h3>
          <div className="flex items-center gap-5">
            <svg width="64" height="64" viewBox="0 0 40 40"><Bulb on={P.unmet_load_hours === 0} /></svg>
            <div>
              <div className="tnum text-[44px] font-semibold leading-none text-emerald-400">{P.unmet_load_hours} h</div>
              <div className="mt-1 text-[18px] font-semibold text-zinc-300">lost power</div>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-scada-border bg-scada-panel p-5">
        <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2">
          <h3 className="text-[18px] font-bold text-white">Same optimizer, five forecasters: 14 variants trained, these are the clean ones</h3>
          <span className="text-[16px] font-semibold text-zinc-300">lower is better · error in W/m²</span>
        </div>
        <p className="mb-4 text-[17px] font-semibold text-zinc-300">Trained on even origins, confirmed on held-out odd origins, then tested once on 2025 data. Each forecaster was then run through the same optimizer, weather, demand, wind and battery reserve for the whole year — only the solar forecast changes.</p>
        <div className="flex flex-col gap-5">
          {FORECASTERS.map((m) => (
            <div key={m.name}>
              <div className="mb-1.5 flex flex-wrap items-center gap-3">
                <span className={`text-[19px] ${m.ours ? 'font-extrabold text-white' : 'font-semibold text-zinc-200'}`}>{m.name}</span>
                <span className="rounded px-2 py-0.5 text-[14px] font-bold tracking-wide" style={{ background: `${m.tone}33`, color: m.tone }}>{m.tag}</span>
              </div>
              {[['2024 odd test', m.odd], ['2025 blind', m.blind]].map(([lab, v]) => (
                <div key={lab} className="mb-1 flex items-center gap-3">
                  <span className="w-32 shrink-0 text-[16px] font-semibold text-zinc-300">{lab}</span>
                  <div className="h-7 flex-1 overflow-hidden rounded-md bg-zinc-800/70">
                    <div className="h-full rounded-md" style={{ width: `${((v - AX_MIN) / (AX_MAX - AX_MIN)) * 100}%`, background: m.tone, opacity: m.ours ? 1 : 0.7 }} />
                  </div>
                  <span className="tnum w-24 shrink-0 text-right text-[18px] font-bold text-white">{v.toFixed(2)}</span>
                </div>
              ))}
              {(() => {
                const c = m.id === 'scenario2_initial_state_exact' ? A[m.id] : view.cand?.[m.id]
                const maxLit = Math.max(R.diesel_liters, ...Object.values(view.cand ?? {}).map((x) => x.diesel_liters))
                if (!c) return <div className="mt-1 text-[16px] font-semibold text-amber-300">Diesel run: waiting to start…</div>
                const prog = Math.min(1, c.hours / c.hours_total)
                const done = prog >= 1
                return (
                  <div className="mt-1 flex items-center gap-3">
                    <span className="w-32 shrink-0 text-[16px] font-bold text-orange-300">Diesel, whole year</span>
                    <div className="relative h-7 flex-1 overflow-hidden rounded-md bg-zinc-800/70">
                      <div className="h-full rounded-md" style={{ width: done ? `${(c.diesel_liters / maxLit) * 100}%` : `${prog * 100}%`, background: done ? '#fb923c' : '#78716c', opacity: done ? 1 : 0.6 }} />
                    </div>
                    <span className="tnum w-24 shrink-0 text-right text-[18px] font-bold text-white">{done ? `${Math.round(c.diesel_liters).toLocaleString()} L` : '…'}</span>
                    <span className={`w-28 shrink-0 rounded border px-2 py-0.5 text-center text-[15px] font-bold ${!done ? 'border-amber-600 text-amber-300' : c.unmet_load_kwh < 0.05 ? 'border-emerald-600 text-emerald-300' : 'border-rose-600 text-rose-300'}`}>
                      {!done ? `running ${Math.round(prog * 100)}%` : c.unmet_load_kwh < 0.05 ? '0 kWh lost' : `${c.unmet_load_kwh.toFixed(1)} kWh lost`}
                    </span>
                    {done && <span className="tnum w-40 shrink-0 text-[15px] font-bold text-zinc-200">lowest battery {c.min_soc_pct.toFixed(1)}%</span>}
                  </div>
                )
              })()}
            </div>
          ))}
        </div>
        <p className="mt-4 text-[16px] font-semibold text-zinc-400">Bars start at {AX_MIN} W/m² so the differences are visible. Of the 14 variants, eight failed or were redundant, and two (F and J) are withheld because their inputs were later found not to be causal.</p>
      </div>

      <div className="rounded-lg border border-scada-border bg-scada-panel p-4">
        <h3 className="text-[16px] font-semibold uppercase tracking-[0.14em] text-zinc-300">The price — what POLARIS does more of</h3>
        <div className="mt-4 flex flex-col gap-5">
          {PRICE_ROWS.map((r) => (
            <div key={r.label}>
              <div className="mb-1.5 flex items-baseline justify-between">
                <span className="text-[18px] font-medium text-zinc-200">{r.label}</span>
                <span className="tnum text-[18px] font-semibold" style={{ color: r.tone }}>{r.delta}</span>
              </div>
              {[['Basic controller', r.a, '#71717a'], ['POLARIS', r.b, r.tone]].map(([name, v, col]) => (
                <div key={name} className="mb-1 flex items-center gap-3">
                  <span className="w-28 shrink-0 text-[16px] text-zinc-300">{name}</span>
                  <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-zinc-800/70">
                    <div className="h-full rounded-full" style={{ width: `${(v / Math.max(r.a, r.b)) * 100}%`, background: col }} />
                  </div>
                  <span className="tnum w-16 shrink-0 text-right text-[17px] text-zinc-300">{v.toLocaleString()}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
        <p className="mt-4 text-[16px] leading-relaxed text-zinc-300">
          The fuel savings above already include the energy lost in the battery. Battery ageing and generator maintenance are not priced in this simulation.
        </p>
      </div>
    </div>
  )
}
