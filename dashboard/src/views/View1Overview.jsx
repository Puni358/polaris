import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Cell, LabelList,
} from 'recharts'
import ProvenanceBadge from '../components/ProvenanceBadge.jsx'
import Donut from '../components/story/Donut.jsx'
import FlowDiagram from '../components/story/FlowDiagram.jsx'
import { useCallback, useState } from 'react'
import Pending from '../components/story/Pending.jsx'
import LiveStation from '../components/story/LiveStation.jsx'
import { useReplayData, windKw, SIM } from '../data/useReplay.js'
import { useMatched } from '../data/useMatched.js'
import { useMonthlyStory } from '../data/useMonthly.js'

const C = { sun: '#facc15', diesel: '#f97316', reactive: '#a1a1aa', ours: '#34d399', bad: '#f43f5e', soft: '#27272a' }

function Card({ title, children, className = '' }) {
  return (
    <div className={`rounded-lg border border-scada-border bg-scada-panel p-4 ${className}`}>
      {title && <h3 className="mb-3 text-[16px] font-semibold uppercase tracking-[0.14em] text-zinc-300">{title}</h3>}
      {children}
    </div>
  )
}

const LADDER_STYLE = {
  reactive: { name: 'Basic controller', color: C.reactive },
  scenario4: { name: 'Forecast, no safety cushion', color: '#f59e0b' },
  scenario2_initial_state_exact: { name: 'POLARIS', color: C.ours, ours: true },
}

export default function View1Overview() {
  const { data, ready, view } = useMatched()
  const { months, loading } = useMonthlyStory(view?.bestId)
  const replay = useReplayData(view?.bestId ?? 'scenario2_initial_state_exact')
  const [now, setNow] = useState(null)
  const onRow = useCallback((row) => setNow(row), [])
  const flow = now && {
    solar: Math.min(Math.max(0, now.actual_ghi) * SIM.kPv, SIM.pvCapKw),
    wind: windKw(now.timestamp),
    diesel: now.diesel_kw,
    battery: Math.max(0, -(now.battery_net_kw ?? 0)),
    load: (now.demand_w ?? 0) / 1000,
  }
  const live = <LiveStation series={replay.series} weather={replay.weather} onRow={onRow} />
  if (!ready) {
    return (
      <div className="flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-2 px-1">
          <h2 className="text-[19px] font-semibold text-zinc-100">Nuolja research station</h2>
          <ProvenanceBadge provenance="SIMULATED" />
        </div>
        {live}
        <Card title="How POLARIS decides"><FlowDiagram flow={flow} /></Card>
        <Pending data={data} />
      </div>
    )
  }
  const A = view.S
  const R = view.reactive
  const P = view.best
  const saved = R.diesel_liters - P.diesel_liters
  const savedPct = Math.round((saved / R.diesel_liters) * 100)
  const hoursOnR = Math.round((R.diesel_run_hours / R.hours_total) * 100)
  const hoursOnP = Math.round((P.diesel_run_hours / P.hours_total) * 100)
  const ladder = Object.keys(LADDER_STYLE).map((id) => ({ id, ...LADDER_STYLE[id], litres: Math.round(A[id].diesel_liters), unmetH: A[id].unmet_load_hours }))
  const best = Math.min(...ladder.map((l) => l.litres))

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2 px-1">
        <div className="flex items-baseline gap-3">
          <h2 className="text-[19px] font-semibold text-zinc-100">Nuolja research station</h2>
          <span className="tnum text-[16px] text-zinc-300">68.4°N · 1,160 m · arctic Sweden</span>
        </div>
        <ProvenanceBadge provenance="SIMULATED" />
      </div>

      {live}

      <Card title="How POLARIS decides">
        <FlowDiagram flow={flow} />
        <div className="mt-3 flex flex-wrap items-center gap-2 text-[16px]">
          <span className="mr-1 text-zinc-400">It protects, in this order:</span>
          {['Lights on', 'Comfort loads', 'Safety cushion', 'Save fuel', 'Waste no sun'].map((t, i) => (
            <span key={t} className="flex items-center gap-1.5 rounded-full border border-scada-border bg-scada-panel2 px-2.5 py-1 text-zinc-300">
              <span className="tnum flex h-4 w-4 items-center justify-center rounded-full bg-zinc-700 text-[14px] text-zinc-200">{i + 1}</span>{t}
            </span>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card title="Diesel burned">
          <div className="flex flex-col items-center gap-3">
            <Donut
              rings={[{ inner: 62, outer: 86, data: [{ value: P.diesel_liters, color: C.ours }, { value: saved, color: C.soft }] }]}
              center={`−${savedPct}%`}
              sub="fuel"
            />
            <div className="flex w-full justify-between text-[16px]">
              <span className="flex items-center gap-1.5 text-zinc-400"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: C.ours }} />POLARIS <b className="tnum text-zinc-200">{Math.round(P.diesel_liters / 1000)}k L</b></span>
              <span className="flex items-center gap-1.5 text-zinc-300"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: C.soft }} />Saved <b className="tnum text-zinc-300">{(saved / 1000).toFixed(1)}k L</b></span>
            </div>
          </div>
        </Card>

        <Card title="Generator running time">
          <div className="flex flex-col items-center gap-3">
            <Donut
              rings={[
                { inner: 72, outer: 88, data: [{ value: hoursOnR, color: C.reactive }, { value: 100 - hoursOnR, color: C.soft }] },
                { inner: 48, outer: 66, data: [{ value: hoursOnP, color: C.ours }, { value: 100 - hoursOnP, color: C.soft }] },
              ]}
              center={`${hoursOnR}→${hoursOnP}%`}
              sub="of the year"
            />
            <div className="flex w-full justify-between text-[16px]">
              <span className="flex items-center gap-1.5 text-zinc-400"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: C.reactive }} />Basic {hoursOnR}%</span>
              <span className="flex items-center gap-1.5 text-zinc-400"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: C.ours }} />POLARIS {hoursOnP}%</span>
            </div>
          </div>
        </Card>

        <Card title="Lights kept on">
          <div className="flex flex-col items-center gap-3">
            <Donut
              rings={[{ inner: 62, outer: 86, data: [{ value: 100 - (P.unmet_load_hours / P.hours_total) * 100, color: C.ours }, { value: (P.unmet_load_hours / P.hours_total) * 100, color: C.bad }] }]}
              center={`${(100 - (P.unmet_load_hours / P.hours_total) * 100).toFixed(P.unmet_load_hours ? 1 : 0)}%`}
              sub="load served"
            />
            <div className="text-center text-[16px] text-zinc-400">
              <b className={`tnum ${P.unmet_load_kwh < 0.01 ? 'text-emerald-400' : 'text-rose-400'}`}>{P.unmet_load_kwh.toFixed(1)} kWh</b> unmet over <b className="tnum text-zinc-200">{P.hours_total.toLocaleString()}</b> hours
            </div>
          </div>
        </Card>
      </div>

      <Card title="When the sun leaves, the diesel starts">
        {loading || !months ? (
          <div className="flex h-64 items-center justify-center text-[17px] text-zinc-400">Loading…</div>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={months} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="#27272a" strokeDasharray="2 4" vertical={false} />
                <XAxis dataKey="month" tick={{ fill: '#a1a1aa', fontSize: 17 }} axisLine={false} tickLine={false} />
                <YAxis yAxisId="sun" tick={{ fill: '#a16207', fontSize: 15 }} axisLine={false} tickLine={false} width={38} />
                <YAxis yAxisId="l" orientation="right" tick={{ fill: '#c2410c', fontSize: 15 }} axisLine={false} tickLine={false} width={38} />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  contentStyle={{ background: '#121214', border: '1px solid #27272a', fontSize: 16 }}
                  formatter={(v, n) => [n === 'Sunshine' ? `${v} kWh/day` : `${v} L/day`, n]}
                />
                <Bar yAxisId="sun" dataKey="sun" name="Sunshine" fill={C.sun} fillOpacity={0.5} radius={[4, 4, 0, 0]} isAnimationActive={false} />
                <Line yAxisId="l" dataKey="reactive" name="Basic controller" stroke={C.reactive} strokeWidth={2.5} dot={{ r: 3 }} isAnimationActive={false} />
                <Line yAxisId="l" dataKey="polaris" name="POLARIS" stroke={C.ours} strokeWidth={3} dot={{ r: 3.5 }} isAnimationActive={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-[16px] text-zinc-400">
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-3 rounded-sm" style={{ background: C.sun, opacity: 0.5 }} />Sunshine (kWh per day)</span>
          <span className="flex items-center gap-1.5"><span className="h-0.5 w-4" style={{ background: C.reactive }} />Basic controller (litres per day)</span>
          <span className="flex items-center gap-1.5"><span className="h-0.5 w-4" style={{ background: C.ours }} />POLARIS (litres per day)</span>
        </div>
      </Card>

      <Card title="Diesel over the year — three ways to run the station">
        <div className="h-60 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={ladder} layout="vertical" margin={{ top: 4, right: 70, left: 8, bottom: 0 }}>
              <XAxis type="number" hide domain={[0, 'dataMax']} />
              <YAxis type="category" dataKey="name" width={250} tick={{ fill: '#d4d4d8', fontSize: 17 }} axisLine={false} tickLine={false} />
              <Bar dataKey="litres" radius={[0, 6, 6, 0]} barSize={26} isAnimationActive={false}>
                {ladder.map((l) => <Cell key={l.id} fill={l.color} fillOpacity={l.ours ? 1 : 0.55} />)}
                <LabelList dataKey="litres" position="right" formatter={(v) => `${v.toLocaleString()} L`} fill="#e4e4e7" fontSize={17} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-1 flex flex-wrap items-center gap-4 text-[16px] text-zinc-400">
          {A.scenario4.unmet_load_hours > 0 && <span className="flex items-center gap-1.5"><span className="inline-block h-2.5 w-2.5 rounded-full bg-rose-500" />“No safety cushion” lost power for <b className="tnum text-rose-300">{A.scenario4.unmet_load_hours} hours</b></span>}
          <span className="ml-auto tnum text-zinc-400">same weather · same demand · same wind</span>
        </div>
      </Card>
    </div>
  )
}
