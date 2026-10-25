import { useEffect, useState } from 'react'
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import OptimizerMap from '../components/story/OptimizerMap.jsx'
import ProvenanceBadge from '../components/ProvenanceBadge.jsx'
import { O_NODES, O_STEPS, O_NODE_STEP, O_STEP_NODE } from '../data/optimizerContent.js'
import { okJson } from '../data/safeFetch.js'

const DAYS = [
  ['2024-04-12', 'Spring day'],
  ['2024-06-15', 'Midnight-sun day'],
  ['2024-01-24', 'Polar-night day'],
  ['2024-10-10', 'Autumn day'],
]
const VARIANT = 'scenario2_initial_state_exact'

function FeedbackDay() {
  const [di, setDi] = useState(0)
  const [rows, setRows] = useState(null)
  useEffect(() => {
    let off = false
    setRows(null)
    fetch(`/data/trace/${VARIANT}/day_${DAYS[di][0]}.json`)
      .then(okJson)
      .then((j) => {
        if (off || !j) return
        setRows(j.map((r) => ({
          hour: `${String(new Date(r.timestamp).getUTCHours()).padStart(2, '0')}:00`,
          planned: +r.plan.soc_pct[0].toFixed(2),
          actual: +r.executed.soc_after_pct.toFixed(2),
          error: +(r.executed.soc_after_pct - r.plan.soc_pct[0]).toFixed(2),
        })))
      })
    return () => { off = true }
  }, [di])
  const maxErr = rows ? Math.max(...rows.map((r) => Math.abs(r.error))) : 0
  return (
    <div className="rounded-lg border border-scada-border bg-scada-panel p-5">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-[22px] font-bold text-white">Plan vs reality — one real day</h3>
        <div className="flex flex-wrap gap-2">
          {DAYS.map(([d, l], i) => <button key={d} onClick={() => setDi(i)} className={`rounded-lg border px-3 py-1.5 text-[16px] font-bold ${di === i ? 'border-cyan-400 bg-cyan-950 text-white' : 'border-scada-border text-zinc-300 hover:text-white'}`}>{l}</button>)}
        </div>
      </div>
      <p className="mb-3 text-[18px] font-semibold text-zinc-200">Each hour the optimizer predicts the battery level at the end of the hour. The station then reports the real level. The next plan starts from the real one, so the gap never accumulates.</p>
      {!rows ? <div className="py-10 text-center text-[18px] text-zinc-400">Loading a real day…</div> : (
        <>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="#27272a" strokeDasharray="2 4" vertical={false} />
                <XAxis dataKey="hour" tick={{ fill: '#d4d4d8', fontSize: 14 }} interval={2} />
                <YAxis yAxisId="soc" domain={[0, 100]} tick={{ fill: '#d4d4d8', fontSize: 14 }} width={44} unit="%" />
                <YAxis yAxisId="err" orientation="right" tick={{ fill: '#f9a8d4', fontSize: 14 }} width={48} unit=" pp" />
                <Tooltip contentStyle={{ background: '#18181b', border: '2px solid #52525b' }} labelStyle={{ color: '#fff', fontSize: 17, fontWeight: 700 }} itemStyle={{ color: '#fff', fontSize: 16 }} />
                <Legend wrapperStyle={{ fontSize: 16, color: '#e4e4e7' }} />
                <Bar yAxisId="err" isAnimationActive={false} dataKey="error" name="Error (real − planned, % points)" fill="#f472b6" opacity={0.8} />
                <Line yAxisId="soc" isAnimationActive={false} dataKey="planned" name="Planned battery level" stroke="#22d3ee" strokeWidth={2.5} strokeDasharray="6 5" dot={false} />
                <Line yAxisId="soc" isAnimationActive={false} dataKey="actual" name="Real battery level" stroke="#34d399" strokeWidth={3} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-2 text-[17px] font-semibold text-zinc-300">Largest one-hour error this day: <span className="tnum font-bold text-pink-300">{maxErr.toFixed(2)} percentage points</span>. It does not carry into the next hour: every plan restarts from the measured level.</p>
        </>
      )}
    </div>
  )
}

function Panel({ id }) {
  const n = O_NODES[id]
  if (!n) return null
  return (
    <div className="rounded-lg border-2 border-zinc-600 bg-scada-panel p-5">
      <h3 className="mb-2 text-[24px] font-bold text-white">{n.title}</h3>
      <p className="mb-3 text-[19px] font-semibold leading-relaxed text-zinc-100">{n.plain}</p>
      {n.facts.length > 0 && <div className="mb-3 flex flex-wrap gap-2">{n.facts.map((f) => <span key={f} className="rounded-full border border-scada-border bg-scada-panel2 px-3 py-1 text-[16px] font-bold text-cyan-200">{f}</span>)}</div>}
      <div className="flex flex-col gap-2.5">
        {n.blocks.map(([label, text]) => (
          <div key={label} className="rounded-md border border-scada-border bg-scada-panel2 p-3">
            <div className="mb-1 text-[15px] font-bold uppercase tracking-wide text-cyan-300">{label}</div>
            <pre className="tnum whitespace-pre-wrap text-[17px] leading-relaxed text-zinc-100">{text}</pre>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function View7Optimizer() {
  const [step, setStep] = useState(1)
  const [sel, setSel] = useState(O_STEP_NODE[1])
  const [lockIdx, setLockIdx] = useState(0)
  const [auto, setAuto] = useState(false)

  const go = (n) => { const s = Math.max(1, Math.min(5, n)); setStep(s); setSel(O_STEP_NODE[s]); if (s === 3) { setLockIdx(0); setAuto(false) } }
  useEffect(() => {
    const onKey = (e) => {
      const tag = (e.target?.tagName || '').toLowerCase()
      if (tag === 'input' || tag === 'select' || tag === 'textarea') return
      if (e.key === 'ArrowRight') { e.preventDefault(); setStep((s) => { const n = Math.min(5, Math.max(1, s + 1)); setSel(O_STEP_NODE[n]); if (n === 3) { setLockIdx(0); setAuto(false) } return n }) }
      if (e.key === 'ArrowLeft') { e.preventDefault(); setStep((s) => { const n = Math.max(1, s - 1); setSel(O_STEP_NODE[n]); if (n === 3) { setLockIdx(0); setAuto(false) } return n }) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])
  useEffect(() => {
    if (!auto) return undefined
    const t = setInterval(() => setLockIdx((i) => { if (i >= 5) { setAuto(false); return 5 } const n = i + 1; setSel(['j1', 'j1b', 'j2', 'j3', 'j4'][Math.min(4, n - 1)]); return n }), 800)
    return () => clearInterval(t)
  }, [auto])

  const ROWIDS = ['j1', 'j1b', 'j2', 'j3', 'j4']
  const onSelect = (id) => {
    setSel(id)
    const o = O_NODE_STEP[id]
    if (o && o !== step) { setStep(o); if (o === 3) setLockIdx(0) }
    const ri = ROWIDS.indexOf(id)
    if (ri >= 0) { setAuto(false); setLockIdx((cur) => Math.max(cur, ri + 1)) }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end justify-between gap-2 px-1">
        <div>
          <h2 className="text-[26px] font-bold text-white">Inside the optimizer: GAP19</h2>
          <p className="text-[18px] text-zinc-300">It plans 24 hours, carries out one, measures the real result, and plans again. Use ← → to step through.</p>
        </div>
        <ProvenanceBadge provenance="SIMULATED" />
      </div>

      <div className="flex flex-wrap items-center gap-2 rounded-lg border border-scada-border bg-scada-panel p-3">
        <button onClick={() => go(step - 1)} disabled={step <= 1} className="rounded-lg border border-scada-border px-4 py-2 text-[18px] font-bold text-zinc-100 hover:bg-zinc-800 disabled:opacity-30">◀ Prev</button>
        {O_STEPS.map((s) => (
          <button key={s.id} onClick={() => go(s.id)} className={`rounded-lg border-2 px-3.5 py-2 text-[17px] font-bold ${step === s.id ? 'border-cyan-400 bg-cyan-950 text-white' : 'border-scada-border text-zinc-300 hover:text-white'}`}><span className="tnum mr-2 rounded-full bg-zinc-700 px-2 py-0.5 text-[15px]">{s.id}</span>{s.label}</button>
        ))}
        <button onClick={() => go(step + 1)} disabled={step >= 5} className="rounded-lg border border-scada-border px-4 py-2 text-[18px] font-bold text-zinc-100 hover:bg-zinc-800 disabled:opacity-30">Next ▶</button>
        <button onClick={() => { setStep(0); setSel('j1') }} className={`ml-auto rounded-lg border px-3 py-2 text-[17px] font-bold ${step === 0 ? 'border-amber-400 bg-amber-950 text-amber-200' : 'border-scada-border text-zinc-300 hover:text-white'}`}>Show everything</button>
      </div>

      <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-[65fr_35fr]">
        <div className="flex min-w-0 flex-col gap-4">
          <div className="rounded-lg border border-scada-border bg-scada-panel p-4">
            <OptimizerMap step={step} lockIdx={lockIdx} selected={sel} onSelect={onSelect} />
          </div>
          {step === 3 && (
            <div className="flex flex-wrap items-center gap-3 rounded-lg border border-scada-border bg-scada-panel p-4">
              <span className="text-[18px] font-bold text-white">Priorities locked: {lockIdx} of 5</span>
              <button onClick={() => { setLockIdx(0); setAuto(true); setSel('j1') }} className="rounded-lg border-2 border-emerald-500 bg-emerald-950 px-4 py-2 text-[18px] font-bold text-emerald-300">▶ Run all in order</button>
              <button onClick={() => { setAuto(false); setLockIdx(0) }} className="rounded-lg border border-scada-border px-4 py-2 text-[18px] font-bold text-zinc-100 hover:bg-zinc-800">↺ Reset</button>
              <span className="text-[17px] font-semibold text-zinc-300">or click J1 … J4 to lock them one at a time</span>
            </div>
          )}
          {(step === 5 || step === 0) && <FeedbackDay />}
        </div>
        <div className="min-w-0 xl:sticky xl:top-3 xl:max-h-[calc(100vh-24px)] xl:overflow-y-auto">
          <Panel id={sel} />
        </div>
      </div>
    </div>
  )
}
