import { useEffect, useRef, useState } from 'react'

// "What the optimizer is thinking": six cards that light up one after another for the hour being inspected.
// It replaces the long written ladder; click any card to open the full written reasoning for that step.

function AnimNumber({ to, active, digits = 1, suffix = '', from = 0 }) {
  const [v, setV] = useState(from)
  const raf = useRef(null)
  useEffect(() => {
    cancelAnimationFrame(raf.current)
    if (!active) { setV(from); return undefined }
    const t0 = performance.now()
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / 900)
      const e = 1 - Math.pow(1 - p, 3)
      setV(from + (to - from) * e)
      if (p < 1) raf.current = requestAnimationFrame(tick)
    }
    raf.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf.current)
  }, [to, active, from])
  return <span className="tnum">{v.toFixed(digits)}{suffix}</span>
}

function BatteryIcon({ level, floorMark, color }) {
  return (
    <svg viewBox="0 0 120 64" className="h-16 w-28">
      <rect x="4" y="8" width="100" height="48" rx="8" fill="none" stroke="#a1a1aa" strokeWidth="3" />
      <rect x="104" y="22" width="9" height="20" rx="3" fill="#a1a1aa" />
      <rect x="8" y="12" width={92 * Math.max(0, Math.min(1, level / 100))} height="40" rx="5" fill={color} style={{ transition: 'width 0.9s ease' }} />
      {floorMark && <line x1={8 + 92 * 0.2} y1="4" x2={8 + 92 * 0.2} y2="60" stroke="#f43f5e" strokeWidth="3" strokeDasharray="4 3" />}
    </svg>
  )
}

const socColor = (v) => (v < 30 ? '#f87171' : v < 50 ? '#fbbf24' : '#34d399')

function Bar({ label, value, max, color, active, unit = 'kWh' }) {
  return (
    <div className="mb-1.5">
      <div className="flex justify-between text-[17px] font-bold text-zinc-100"><span>{label}</span><span className="tnum">{value.toFixed(0)} {unit}</span></div>
      <div className="h-3.5 overflow-hidden rounded-full bg-zinc-800">
        <div className="h-full rounded-full" style={{ width: active ? `${Math.min(100, (value / Math.max(1, max)) * 100)}%` : '0%', background: color, transition: 'width 1s ease' }} />
      </div>
    </div>
  )
}

const VERD = { ok: '✓', warn: '!', action: '▲' }
const VCOL = { ok: 'border-emerald-600 text-emerald-300', warn: 'border-rose-600 text-rose-300', action: 'border-amber-500 text-amber-300' }

export default function ThoughtFlow({ exp, hourKey }) {
  const [step, setStep] = useState(0) // number of cards revealed (0..6)
  const [playing, setPlaying] = useState(true)
  const [open, setOpen] = useState(null)

  useEffect(() => { setStep(0); setPlaying(true) }, [hourKey])
  useEffect(() => {
    if (!playing) return undefined
    if (step >= 6) return undefined
    const t = setTimeout(() => setStep((s) => s + 1), step === 0 ? 400 : 1500)
    return () => clearTimeout(t)
  }, [step, playing])

  const v = exp.viz
  if (!v) return null
  const L = exp.ladder
  const maxE = Math.max(v.solarAll + v.windAll, v.demAll, 1)
  const lowestC = socColor(v.minSoc)

  const cards = [
    {
      key: 'state', title: 'Battery right now', verdict: L[0]?.verdict,
      body: (on) => (
        <>
          <BatteryIcon level={on ? exp.socStart : 0} color={socColor(exp.socStart)} />
          <div className="text-[30px] font-extrabold text-white"><AnimNumber to={exp.socStart} active={on} suffix="%" /></div>
          <div className="text-[17px] font-semibold text-zinc-200">{v.aboveFloor.toFixed(0)} kWh above the floor · about {Number.isFinite(v.autonomyH) ? v.autonomyH.toFixed(1) : '∞'} h of load</div>
        </>
      ),
    },
    {
      key: 'forecast', title: 'Next 24 hours', verdict: L[1]?.verdict,
      body: (on) => (
        <>
          <Bar label="Sun" value={v.solarAll} max={maxE} color="#facc15" active={on} />
          <Bar label="Wind" value={v.windAll} max={maxE} color="#94a3b8" active={on} />
          <Bar label="Need" value={v.demAll} max={maxE} color="#e4e4e7" active={on} />
          <div className="mt-1 text-[17px] font-semibold text-zinc-200">{v.solarAll < 5 ? 'No sun in the forecast' : `Sun peaks at ${v.peak.solar.toFixed(0)} kW (+${v.peak.j} h)`}</div>
        </>
      ),
    },
    {
      key: 'safety', title: 'Is any load at risk?', verdict: L[2]?.verdict,
      body: (on) => (
        <>
          <BatteryIcon level={on ? v.minSoc : exp.socStart} floorMark color={lowestC} />
          <div className="text-[28px] font-extrabold text-white">lowest <AnimNumber to={v.minSoc} from={exp.socStart} active={on} suffix="%" /></div>
          <div className="text-[17px] font-semibold text-zinc-200">{v.unmetAll > 0.01 ? `${v.unmetAll.toFixed(1)} kWh of load unserved` : 'all load served · plan stays above the red 20% line'}</div>
        </>
      ),
    },
    {
      key: 'reserve', title: 'Reserve and end of day', verdict: L[3]?.verdict,
      body: (on) => (
        <>
          <Bar label="Must hold at the end" value={v.requiredEnd} max={190} color="#f472b6" active={on} />
          <Bar label="Plan ends at" value={v.endEnergyPlan} max={190} color="#22d3ee" active={on} />
          <div className="mt-1 text-[17px] font-semibold text-zinc-200">{v.termBinding ? 'The end-of-day rule is what drives the diesel' : 'Comfortably clear of the requirement'}</div>
        </>
      ),
    },
    {
      key: 'fuel', title: 'Diesel decision', verdict: L[4]?.verdict,
      body: (on) => (
        <>
          <div className="flex items-center gap-3">
            <svg viewBox="0 0 64 64" className="h-16 w-16">
              <rect x="6" y="22" width="52" height="30" rx="6" fill="none" stroke={v.dieselOn ? '#fb923c' : '#71717a'} strokeWidth="3" />
              <path d="M34 28 L26 40 H33 L30 50 L42 35 H34 Z" fill={v.dieselOn ? '#fb923c' : 'none'} stroke={v.dieselOn ? '#fb923c' : '#71717a'} strokeWidth="2" className={on && v.dieselOn ? 'pulse-solve' : undefined} />
              <path d="M14 22 V12 H24 V22" fill="none" stroke={v.dieselOn ? '#fb923c' : '#71717a'} strokeWidth="3" />
            </svg>
            <div className="text-[30px] font-extrabold text-white">{v.dieselOn ? <><AnimNumber to={v.executed} active={on} digits={0} /> kW</> : 'OFF'}</div>
          </div>
          <div className="text-[17px] font-semibold text-zinc-200">{v.dieselOn ? `${v.fuelNow.toFixed(0)} L this hour · plan: ${v.dieselHours} h in ${v.blockStarts} block${v.blockStarts === 1 ? '' : 's'}` : v.firstDiesel == null ? 'No diesel needed in 24 h' : `Next planned run at +${v.firstDiesel} h`}</div>
        </>
      ),
    },
    {
      key: 'result', title: 'What actually happened', verdict: L[5]?.verdict,
      body: (on) => (
        <>
          <div className="flex items-center gap-2 text-[26px] font-extrabold text-white">
            <AnimNumber to={exp.socStart} active={on} suffix="%" /> <span className={exp.net >= 0 ? 'text-emerald-300' : 'text-cyan-300'}>{exp.net >= 0 ? '▲' : '▼'}</span> <AnimNumber to={exp.socEnd} from={exp.socStart} active={on} suffix="%" />
          </div>
          <BatteryIcon level={on ? exp.socEnd : exp.socStart} color={socColor(exp.socEnd)} />
          <div className="text-[17px] font-semibold text-zinc-200">battery {exp.net >= 0 ? '+' : ''}{exp.net.toFixed(1)} kW · load {exp.demandNow.toFixed(1)} kW</div>
        </>
      ),
    },
  ]

  return (
    <div className="rounded-lg border border-scada-border bg-scada-panel p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-[20px] font-bold text-white">What the optimizer is thinking</h3>
        <div className="flex gap-2">
          <button onClick={() => { setStep(0); setPlaying(true) }} className="rounded-lg border border-scada-border px-3 py-1.5 text-[16px] font-bold text-zinc-100 hover:bg-zinc-800">↺ Replay</button>
          <button onClick={() => { setPlaying(false); setStep(6) }} className="rounded-lg border border-scada-border px-3 py-1.5 text-[16px] font-bold text-zinc-100 hover:bg-zinc-800">Show all</button>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((c, i) => {
          const on = step > i
          const current = step === i + 1 && playing
          const vv = c.verdict ?? 'ok'
          return (
            <button
              key={c.key}
              onClick={() => { setPlaying(false); setStep(6); setOpen(open === i ? null : i) }}
              className={`flex min-h-[200px] flex-col gap-2 rounded-xl border-2 p-4 text-left transition-all duration-500 ${on ? 'opacity-100' : 'opacity-25'} ${current ? 'border-cyan-400 bg-cyan-950/30 shadow-[0_0_20px_rgba(34,211,238,0.35)]' : open === i ? 'border-white bg-scada-panel2' : 'border-scada-border bg-scada-panel2'}`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="flex items-center gap-2 text-[18px] font-bold text-zinc-100"><span className="tnum flex h-7 w-7 items-center justify-center rounded-full bg-zinc-700 text-[15px]">{i + 1}</span>{c.title}</span>
                {on && <span className={`flex h-7 w-7 items-center justify-center rounded-full border-2 text-[16px] font-extrabold ${VCOL[vv]}`}>{VERD[vv]}</span>}
              </div>
              <div className="flex flex-1 flex-col justify-center gap-1">{c.body(on)}</div>
            </button>
          )
        })}
      </div>
      {open != null && L[open] && (
        <div className="mt-3 rounded-lg border-2 border-white/60 bg-scada-panel2 p-4">
          <div className="mb-1 flex items-center justify-between"><span className="text-[19px] font-bold text-white">{L[open].title}</span><button onClick={() => setOpen(null)} className="text-[15px] font-bold text-zinc-300 hover:text-white">✕ close</button></div>
          <p className="text-[18px] font-semibold leading-relaxed text-zinc-100">{L[open].text}</p>
          <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1">{L[open].facts.map(([k, val]) => <span key={k} className="text-[16px] font-semibold text-zinc-300">{k}: <span className="tnum font-bold text-white">{val}</span></span>)}</div>
        </div>
      )}
      <p className="mt-2 text-[16px] font-semibold text-zinc-400">Tap any card for the full written reasoning. Priority order inside the solver: J1 critical › J1b non-critical › J2 reserve › J3 fuel › J4 curtailment.</p>
    </div>
  )
}
