import { useEffect, useMemo, useRef, useState } from 'react'
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import ProvenanceBadge from './ProvenanceBadge.jsx'
import ReasoningPanel from './ReasoningPanel.jsx'
import ModelCompare from './ModelCompare.jsx'
import { isFieldAvailable } from '../data/fieldAvailability.js'

const WINDOW_BACK = 48

function hourLabel(iso) {
  const d = new Date(iso)
  return `${String(d.getUTCDate()).padStart(2, '0')}/${String(d.getUTCMonth() + 1).padStart(2, '0')} ${String(d.getUTCHours()).padStart(2, '0')}:00`
}
function padNum(n, width = 3) {
  if (n === null || n === undefined || Number.isNaN(n)) return '—'.padStart(width, ' ')
  return String(Math.round(n)).padStart(width, ' ')
}

function getDiurnalDemandW(hour) {
  if (hour >= 0 && hour <= 5) return 18000.0
  if (hour === 6) return 22000.0
  if (hour === 7) return 30000.0
  if (hour === 8) return 38000.0 // Morning Peak
  if (hour >= 9 && hour <= 17) return 32000.0 // Day Sustained
  if (hour === 18) return 36000.0
  if (hour === 19) return 42000.0 // Evening Peak
  if (hour >= 20 && hour <= 21) return 30000.0
  return 22000.0
}

function getSeasonalMultiplier(month) {
  if (month === 11 || month === 12 || month === 1 || month === 2) return 1.20
  if (month >= 5 && month <= 8) return 0.85
  return 1.00
}

function getIndustrialDemandW(isoTimestamp) {
  const d = new Date(isoTimestamp)
  const hour = d.getUTCHours()
  const month = d.getUTCMonth() + 1
  return Math.min(Math.max(getDiurnalDemandW(hour) * getSeasonalMultiplier(month), 15000.0), 45000.0)
}

export default function DecisionInspector({ series, scenarioId, initialHourIndex, jumpNonce }) {
  const [playheadIndex, setPlayheadIndex] = useState(Math.min(initialHourIndex ?? 20, series.length - 1))
  const [isPlaying, setIsPlaying] = useState(false)
  const intervalRef = useRef(null)
  const [scene, setScene] = useState('why')
  const [showFc, setShowFc] = useState(false)

  // External jump (from View 1 / View 3 markers) overrides the playhead.
  useEffect(() => {
    if (initialHourIndex != null) {
      setIsPlaying(false)
      setPlayheadIndex(Math.min(initialHourIndex, series.length - 1))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialHourIndex, jumpNonce])

  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setPlayheadIndex((p) => {
          if (p >= series.length - 1) { setIsPlaying(false); return p }
          return p + 1
        })
      }, 800)
    }
    return () => clearInterval(intervalRef.current)
  }, [isPlaying, series.length])

  const row = series[playheadIndex]

  const dieselMax = useMemo(() => {
    let maxD = 40 // Ensure at least 40 kW headroom for 25-35 kW station demand
    for (const r of series) {
      if (r.diesel_kw != null && r.diesel_kw > maxD) maxD = r.diesel_kw
      if (r.demand_w != null && (r.demand_w / 1000) > maxD) maxD = r.demand_w / 1000
    }
    const roundUp = (v, step) => Math.max(step, Math.ceil((v * 1.15) / step) * step)
    return roundUp(maxD, 10)
  }, [series])

  const { chartData, ghiMax } = useMemo(() => {
    const sliceStart = Math.max(0, playheadIndex - WINDOW_BACK)
    const sliceEnd = Math.min(series.length, playheadIndex + 25)
    const windowed = series.slice(sliceStart, sliceEnd)

    const data = windowed.map((r, i) => {
      const isPastOrPresent = (sliceStart + i) <= playheadIndex
      const offset = (sliceStart + i) - playheadIndex
      let futureForecast = null
      if (!isPastOrPresent) {
        if (row?.forecast_horizon && offset >= 1 && offset <= 24) {
          futureForecast = row.forecast_horizon[offset - 1]
        } else {
          futureForecast = r.n6_forecast_ghi ?? null
        }
      }

      // Forecast that was issued one hour BEFORE this hour (horizon[0] of the previous origin),
      // so the forecast can still be compared with the recorded value after the hour has passed.
      let pastForecast = null
      if (isPastOrPresent) {
        const prevRow = series[sliceStart + i - 1]
        pastForecast = prevRow ? (prevRow.forecast_horizon?.[0] ?? prevRow.n6_forecast_ghi ?? null) : null
      }

      let demandKw = null
      if (isPastOrPresent) {
        if (r.demand_w != null) {
          demandKw = r.demand_w / 1000
        } else if (r.timestamp) {
          demandKw = getIndustrialDemandW(r.timestamp) / 1000
        }
      }

      return {
        label: hourLabel(r.timestamp),
        actual_ghi: isPastOrPresent ? (r.actual_ghi ?? null) : null,
        battery_soc_pct: isPastOrPresent ? (r.battery_soc_pct ?? null) : null,
        diesel_kw: isPastOrPresent ? (r.diesel_kw ?? null) : null,
        demand_kw: demandKw,
        past_forecast_ghi: pastForecast,
        future_forecast_ghi: futureForecast,
        n6_forecast_ghi: r.n6_forecast_ghi ?? null,
      }
    })

    // Dynamic GHI scaling: compute peak over the active 72-hour aperture
    let maxGhi = 0
    for (const r of windowed) {
      if (r.actual_ghi != null && r.actual_ghi > maxGhi) maxGhi = r.actual_ghi
      if (r.n6_forecast_ghi != null && r.n6_forecast_ghi > maxGhi) maxGhi = r.n6_forecast_ghi
    }
    const roundUp = (v, step) => Math.max(step, Math.ceil((v * 1.15) / step) * step)
    // Scale dynamically with 15% headroom, but clamp upper bound to 200 W/m²
    // for this winter dataset to prevent anomalous spikes from squashing the curves
    const dynamicGhi = roundUp(maxGhi, 50)
    const clampedGhi = Math.min(200, dynamicGhi)

    return { chartData: data, ghiMax: clampedGhi }
  }, [series, playheadIndex])

  if (!row) {
    return (
      <div className="rounded border border-amber-800 bg-amber-950/30 p-4 text-center text-[16px] text-amber-500">
        No telemetry row available at this playhead position.
      </div>
    )
  }

  const hasForecastPoint = useMemo(() => {
    return isFieldAvailable(scenarioId, 'n6_forecast_ghi_point') || series.some((r) => r.n6_forecast_ghi != null)
  }, [scenarioId, series])

  return (
    <div className="flex flex-col gap-3">
    <div className="flex flex-col gap-3 rounded border border-scada-border bg-scada-panel p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-3">
          <h3 className="text-[17px] uppercase tracking-wide text-zinc-400">Run timeline</h3>
          <div className="flex flex-wrap items-center gap-3 text-[15px] text-zinc-400">
            <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#ffffff]" /> Demand kW</span>
            <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#2ee6ff]" /> Actual GHI (Past)</span>
            {hasForecastPoint && (
              <span className="flex items-center gap-1.5"><span className="inline-block h-0 w-3 border-b-2 border-[#b79cff]" /> Forecast issued 1h earlier (Past)</span>
            )}
            {hasForecastPoint && (
              <span className="flex items-center gap-1.5"><span className="inline-block h-0 w-3 border-b-2 border-dashed border-[#b79cff]" /> N6 Forecast (Future)</span>
            )}
            <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#3df0a0]" /> Battery SOC</span>
            <span className="flex items-center gap-1.5"><span className="inline-block h-2 w-3 rounded-sm bg-[#ff8a3d]" /> Diesel kW</span>
            <span className="flex items-center gap-1.5"><span className="inline-block h-0 w-3 border-b-2 border-dashed border-[#ffb21f]" /> Playhead (T=0)</span>
          </div>
        </div>
        <ProvenanceBadge provenance="SIMULATED" />
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 8, right: 44, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="gGhi" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2ee6ff" stopOpacity="0.55" /><stop offset="100%" stopColor="#2ee6ff" stopOpacity="0.03" /></linearGradient>
            </defs>
            <CartesianGrid stroke="#3f3f46" strokeDasharray="3 4" vertical={false} />
            <XAxis dataKey="label" tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} interval={Math.floor(chartData.length / 8)} />
            <YAxis yAxisId="ghi" domain={[0, ghiMax]} tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} width={42} label={{ value: 'W/m²', angle: -90, position: 'insideLeft', fill: '#d4d4d8', fontSize: 14, fontWeight: 600 }} />
            <YAxis yAxisId="soc" orientation="right" domain={[0, 100]} tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} width={32} />
            <YAxis yAxisId="diesel" orientation="right" domain={[0, dieselMax]} tick={{ fill: '#e4e4e7', fontSize: 15, fontWeight: 600 }} width={36} label={{ value: 'kW', angle: 90, position: 'insideRight', fill: '#d4d4d8', fontSize: 14, fontWeight: 600 }} />
            <Tooltip contentStyle={{ background: '#09090b', border: '2px solid #71717a', fontSize: 16, color: '#fff' }} labelStyle={{ color: '#fff', fontWeight: 700 }} itemStyle={{ color: '#f4f4f5' }} />
            <ReferenceLine x={hourLabel(row.timestamp)} stroke="#ffb21f" strokeWidth={2} strokeDasharray="5 4" yAxisId="ghi" />
 {hasForecastPoint && (
              <Line yAxisId="ghi" dataKey="past_forecast_ghi" name="Forecast issued 1h earlier (GHI)" stroke="#b79cff" strokeWidth={3} dot={false} connectNulls={false} />
            )}
            <Area yAxisId="ghi" dataKey="actual_ghi" name="Actual GHI (recorded)" stroke="#2ee6ff" strokeWidth={3} fill="url(#gGhi)" dot={false} connectNulls={false} />
            {hasForecastPoint && (
              <Line yAxisId="ghi" dataKey="future_forecast_ghi" name="Future Forecast GHI (N6)" stroke="#b79cff" strokeWidth={3.5} strokeDasharray="6 5" dot={false} connectNulls={false} />
            )}
            <Line yAxisId="soc" dataKey="battery_soc_pct" name="Battery SOC % (recorded)" stroke="#3df0a0" strokeWidth={3} dot={false} connectNulls={false} />
            <Line yAxisId="diesel" dataKey="diesel_kw" name="Diesel kW (recorded)" type="stepAfter" stroke="#ff8a3d" strokeWidth={3} dot={false} connectNulls={false} />
            <Line yAxisId="diesel" dataKey="demand_kw" name="Station Demand (kW)" type="stepAfter" stroke="#ffffff" strokeWidth={2.5} dot={false} connectNulls={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {Array.isArray(row.forecast_horizon) && (
        <button onClick={() => setShowFc((v) => !v)} className="self-start rounded-lg border border-scada-border px-3 py-1.5 text-[16px] font-bold text-zinc-100 hover:bg-zinc-800">{showFc ? '▾ Hide' : '▸ Show'} the model&apos;s 24-hour forecast numbers</button>
      )}
      {showFc && Array.isArray(row.forecast_horizon) && (
        <div className="rounded border border-scada-border bg-scada-panel2 px-3 py-2">
          <div className="mb-1.5 flex flex-wrap items-baseline justify-between gap-2">
            <span className="text-[15px] font-semibold tracking-wide text-zinc-300">Forecast the model made at {hourLabel(row.timestamp)} — next {row.forecast_horizon.length} hours (GHI W/m² · PV kW)</span>
            <span className="text-[15px] text-zinc-400">solar-free hours are dimmed</span>
          </div>
          <div className="flex gap-1 overflow-x-auto pb-1">
            {row.forecast_horizon.map((v, k) => {
              const t = new Date(new Date(row.timestamp).getTime() + (k + 1) * 3600_000)
              const strength = Math.min(1, v / 60)
              return (
                <div
                  key={k}
                  className={`flex min-w-[52px] flex-col items-center rounded border px-1.5 py-1 ${v > 0.5 ? 'border-cyan-800' : 'border-scada-border opacity-50'}`}
                  style={{ background: `rgba(34, 211, 238, ${(0.06 + strength * 0.35).toFixed(2)})` }}
                  title={`+${k + 1}h · ${hourLabel(t.toISOString())}`}
                >
                  <span className="tnum text-[14px] text-zinc-300">+{k + 1}h {String(t.getUTCHours()).padStart(2, '0')}:00</span>
                  <span className="tnum text-[16px] text-zinc-100">{v.toFixed(1)}</span>
                  <span className="tnum text-[14px] text-cyan-400">{(Math.min(v * 0.051, 60)).toFixed(2)} kW</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="flex flex-col gap-2 rounded bg-scada-panel2 px-3 py-2">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1 rounded border border-scada-border p-0.5">
            <button className="rounded px-2 py-1 text-[17px] text-zinc-300 hover:bg-scada-panel" onClick={() => { setIsPlaying(false); setPlayheadIndex((p) => Math.max(0, p - 1)) }}>◀ STEP</button>
            <button className="rounded px-2 py-1 text-[17px] text-zinc-300 hover:bg-scada-panel" onClick={() => { setIsPlaying(false); setPlayheadIndex((p) => Math.min(series.length - 1, p + 1)) }}>STEP ▶</button>
          </div>
          <div className="h-6 w-px bg-scada-border" />
          <button className="rounded border border-amber-700 bg-amber-950 px-4 py-1.5 text-[17px] font-semibold text-amber-400 hover:border-amber-500" onClick={() => setIsPlaying((p) => !p)}>
            {isPlaying ? '❙❙ PAUSE' : '▶ PLAY'}
          </button>
          <div className="h-6 w-px bg-scada-border" />
          <span className="tnum whitespace-pre text-[16px] text-zinc-400">
            [ T={hourLabel(row.timestamp)} | SOC:{padNum(row.battery_soc_pct)}% | DIESEL:{padNum(row.diesel_kw)}kW ]
          </span>
        </div>
        <input type="range" min={0} max={series.length - 1} value={playheadIndex} onChange={(e) => { setIsPlaying(false); setPlayheadIndex(Number(e.target.value)) }} className="w-full accent-amber-500" />
      </div>

    </div>
      <ReasoningPanel
        scene={scene}
        onScene={setScene}
        compare={<ModelCompare date={row.timestamp.slice(0, 10)} />}
        series={series}
        scenarioId={scenarioId}
        playheadIndex={playheadIndex}
        onSelect={(i) => { setIsPlaying(false); setPlayheadIndex(i) }}
      />
    </div>
  )
}
