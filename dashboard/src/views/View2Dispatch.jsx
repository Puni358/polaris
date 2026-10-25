import { useEffect, useState } from 'react'
import DecisionInspector from '../components/DecisionInspector.jsx'
import FeaturedDays, { useFeaturedDays } from '../components/FeaturedDays.jsx'
import ProvenanceBadge from '../components/ProvenanceBadge.jsx'
import { SCENARIO_MANIFEST } from '../data/manifest.js'
import { useRealSeries } from '../data/useRealSeries.js'
import { useTraceSeries, setTraceVariant, TRACE_VARIANTS } from '../data/useTrace.js'

export default function View2Dispatch({ jumpTarget }) {
  const [scenarioId, setScenarioId] = useState('scenario2')
  const [initialHourIndex, setInitialHourIndex] = useState(null)
  const [jumpNonce, setJumpNonce] = useState(0)
  const featured = useFeaturedDays()
  const [featDay, setFeatDay] = useState(null)

  // Cross-view navigation from View 1 / View 3 markers: switch scenario and
  // jump to the exact hour, overriding whatever the user had manually scrubbed to.
  useEffect(() => {
    if (jumpTarget) {
      if (jumpTarget.variant) setVariant(jumpTarget.variant)
      setScenarioId(jumpTarget.scenarioId)
      setInitialHourIndex(jumpTarget.hourIndex)
      setJumpNonce((n) => n + 1)
    }
  }, [jumpTarget])

  const stored = useRealSeries(scenarioId)
  // Scenario 2 has a full decision trace (every solver input and the whole 24-step plan).
  const [variant, setVariant] = useState('scenario2_initial_state_exact')
  setTraceVariant(variant)
  const trace = useTraceSeries(scenarioId === 'scenario2', variant)
  const traced = scenarioId === 'scenario2' && trace.series
  const data = traced ? trace.series : stored.data
  const loading = scenarioId === 'scenario2' ? !trace.done || (!trace.series && stored.loading) : stored.loading
  const error = stored.error

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-scada-border bg-scada-panel px-4 py-2">
        <h2 className="text-[17px] uppercase tracking-wide text-zinc-400">Decision Inspector — Why the optimizer did what it did, hour by hour</h2>
        <div className="flex items-center gap-2">
          {scenarioId === 'scenario2' && TRACE_VARIANTS.length > 1 && (
            <select
              value={variant}
              onChange={(e) => { setVariant(e.target.value); setInitialHourIndex(null) }}
              className="tnum rounded border border-amber-800 bg-scada-panel2 px-2 py-1 text-[17px] text-amber-300"
              title="Which end-of-horizon energy rule the traced run used"
            >
              {TRACE_VARIANTS.map((v) => <option key={v.id} value={v.id}>{v.label}</option>)}
            </select>
          )}
          <select
            value={scenarioId}
            onChange={(e) => { setScenarioId(e.target.value); setInitialHourIndex(null) }}
            className="tnum rounded border border-scada-border bg-scada-panel2 px-2 py-1 text-[17px] text-zinc-200"
          >
            {SCENARIO_MANIFEST.map((s) => (
              <option key={s.scenario_id} value={s.scenario_id}>{s.label}</option>
            ))}
          </select>
          <ProvenanceBadge provenance="SIMULATED" />
        </div>
      </div>

      {scenarioId === 'scenario2' && traced && (
        <FeaturedDays
          days={featured}
          value={featDay}
          note="All three graphs below follow the day you pick."
          onPick={(date) => {
            setFeatDay(date)
            const f = featured.find((d) => d.date === date)
            if (!f) return
            const start = Date.parse(trace.series[0].timestamp)
            const idx = Math.round((Date.parse(`${date}T00:00:00Z`) + f.focusHour * 3600000 - start) / 3600000)
            if (idx >= 0 && idx < trace.series.length) { setInitialHourIndex(idx); setJumpNonce((n) => n + 1) }
          }}
        />
      )}

      {scenarioId === 'scenario2' && trace.done && (
        <div className={`rounded border px-3 py-1.5 text-[16px] ${traced ? 'border-emerald-800 bg-emerald-950/20 text-emerald-400' : 'border-zinc-700 bg-scada-panel text-zinc-300'}`}>
          {traced
            ? `Full decision trace: ${trace.manifest?.hours_done ?? trace.series.length} / ${trace.manifest?.hours_total ?? 8328} hours recorded — the reasoning below is the solver's own plan.`
            : 'No decision trace found yet — showing the stored run with reconstructed reasoning.'}
        </div>
      )}

      {loading && <div className="rounded border border-scada-border bg-scada-panel p-8 text-center text-[17px] text-zinc-400">Loading real telemetry…</div>}
      {error && <div className="rounded border border-rose-800 bg-rose-950/30 p-8 text-center text-[17px] text-rose-500">Failed to load: {error}</div>}
      {data && (
        <DecisionInspector
          key={`${scenarioId}-${variant}-${traced ? 't' : 's'}`}
          series={data}
          scenarioId={scenarioId}
          jumpNonce={jumpNonce}
          initialHourIndex={initialHourIndex ?? (jumpTarget?.scenarioId === scenarioId ? jumpTarget.hourIndex : 20)}
        />
      )}


    </div>
  )
}
