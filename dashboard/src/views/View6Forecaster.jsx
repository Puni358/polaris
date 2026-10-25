import { useEffect, useState } from 'react'
import ForecasterMap from '../components/story/ForecasterMap.jsx'
import ProvenanceBadge from '../components/ProvenanceBadge.jsx'
import { F_NODES, F_STEPS, F_NODE_STEP, F_STEP_NODE, dotInfo } from '../data/forecasterContent.js'

function RampChart() {
  // weight given to the 15 specialists against the sun's height (frozen model: ramp 22° → 32°, maximum 0.55)
  const W = 420
  const H = 190
  const px = (deg) => 50 + (deg / 60) * (W - 70)
  const py = (w) => 20 + (1 - w / 0.6) * (H - 60)
  const pts = [[0, 0], [22, 0], [32, 0.55], [60, 0.55]].map(([d, w]) => `${px(d)},${py(w)}`).join(' ')
  return (
    <div className="rounded-md border border-scada-border bg-scada-panel2 p-3">
      <div className="mb-1 text-[15px] font-bold uppercase tracking-wide text-pink-300">How much the specialists get to say</div>
      <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full">
        <line x1="50" y1={py(0)} x2={W - 20} y2={py(0)} stroke="#71717a" strokeWidth="2" />
        <line x1="50" y1="20" x2="50" y2={py(0)} stroke="#71717a" strokeWidth="2" />
        <polyline points={pts} fill="none" stroke="#f472b6" strokeWidth="4.5" strokeLinejoin="round" />
        {[0, 22, 32, 60].map((d) => <text key={d} x={px(d)} y={H - 18} textAnchor="middle" fill="#e4e4e7" fontSize="16" fontWeight="700">{d}°</text>)}
        <text x="44" y={py(0.55) + 5} textAnchor="end" fill="#fbcfe8" fontSize="16" fontWeight="700">0.55</text>
        <text x="44" y={py(0) + 5} textAnchor="end" fill="#e4e4e7" fontSize="16" fontWeight="700">0</text>
        <text x={W / 2} y={H - 1} textAnchor="middle" fill="#a1a1aa" fontSize="15" fontWeight="600">height of the sun above the horizon</text>
      </svg>
    </div>
  )
}

function Panel({ id, dot, onClearDot }) {
  const n = F_NODES[id]
  if (!n) return null
  const d = dot ? dotInfo(dot.kind, dot.i) : null
  return (
    <div className="rounded-lg border-2 border-zinc-600 bg-scada-panel p-5">
      {d && (
        <div className="mb-4 rounded-lg border-2 border-cyan-500 bg-cyan-950/25 p-4">
          <div className="mb-1 flex items-center justify-between"><span className="text-[15px] font-bold uppercase tracking-wide text-cyan-300">One model</span><button onClick={onClearDot} className="text-[15px] font-bold text-zinc-300 hover:text-white">✕ close</button></div>
          <div className="text-[21px] font-extrabold text-white">{d.title}</div>
          <p className="mt-1 text-[18px] font-semibold leading-relaxed text-zinc-100">{d.text}</p>
        </div>
      )}
      <h3 className="mb-2 text-[24px] font-bold text-white">{n.title}</h3>
      <p className="mb-3 text-[19px] font-semibold leading-relaxed text-zinc-100">{n.plain}</p>
      {n.belongs && <p className="mb-3 rounded-md border border-amber-700 bg-amber-950/30 p-3 text-[17px] font-semibold text-amber-200">{n.belongs}</p>}
      {n.facts.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {n.facts.map((f) => <span key={f} className="rounded-full border border-scada-border bg-scada-panel2 px-3 py-1 text-[16px] font-bold text-cyan-200">{f}</span>)}
        </div>
      )}
      <div className="flex flex-col gap-2.5">
        {n.chart === 'ramp' && <RampChart />}
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

export default function View6Forecaster() {
  const [step, setStep] = useState(1) // 0 = show everything
  const [sel, setSel] = useState(F_STEP_NODE[1])
  const [dot, setDot] = useState(null)

  const go = (n) => { const s = Math.max(1, Math.min(5, n)); setStep(s); setSel(F_STEP_NODE[s]); setDot(null) }

  useEffect(() => {
    const onKey = (e) => {
      const tag = (e.target?.tagName || '').toLowerCase()
      if (tag === 'input' || tag === 'select' || tag === 'textarea') return
      if (e.key === 'ArrowRight') { e.preventDefault(); setStep((s) => { const n = Math.min(5, Math.max(1, s + 1)); setSel(F_STEP_NODE[n]); setDot(null); return n }) }
      if (e.key === 'ArrowLeft') { e.preventDefault(); setStep((s) => { const n = Math.max(1, s - 1); setSel(F_STEP_NODE[n]); setDot(null); return n }) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const onSelect = (id) => { setSel(id); setDot(null); const o = F_NODE_STEP[id]; if (o && o !== step) setStep(o) }
  const onDot = (kind, i) => { setDot({ kind, i }); setSel(kind); setStep(2) }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end justify-between gap-2 px-1">
        <div>
          <h2 className="text-[26px] font-bold text-white">Inside the forecaster: POLARIS N6</h2>
          <p className="text-[18px] text-zinc-300">40 models vote, a blender combines them, and the disagreement sets the battery reserve. Use ← → to step through.</p>
        </div>
        <ProvenanceBadge provenance="SIMULATED" />
      </div>

      <div className="flex flex-wrap items-center gap-2 rounded-lg border border-scada-border bg-scada-panel p-3">
        <button onClick={() => go(step - 1)} disabled={step <= 1} className="rounded-lg border border-scada-border px-4 py-2 text-[18px] font-bold text-zinc-100 hover:bg-zinc-800 disabled:opacity-30">◀ Prev</button>
        {F_STEPS.map((s) => (
          <button key={s.id} onClick={() => go(s.id)} className={`rounded-lg border-2 px-3.5 py-2 text-[17px] font-bold ${step === s.id ? 'border-cyan-400 bg-cyan-950 text-white' : 'border-scada-border text-zinc-300 hover:text-white'}`}>
            <span className="tnum mr-2 rounded-full bg-zinc-700 px-2 py-0.5 text-[15px]">{s.id}</span>{s.label}
          </button>
        ))}
        <button onClick={() => go(step + 1)} disabled={step >= 5} className="rounded-lg border border-scada-border px-4 py-2 text-[18px] font-bold text-zinc-100 hover:bg-zinc-800 disabled:opacity-30">Next ▶</button>
        <button onClick={() => { setStep(0); setSel('add'); setDot(null) }} className={`ml-auto rounded-lg border px-3 py-2 text-[17px] font-bold ${step === 0 ? 'border-amber-400 bg-amber-950 text-amber-200' : 'border-scada-border text-zinc-300 hover:text-white'}`}>Show everything</button>
      </div>

      <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-[65fr_35fr]">
        <div className="min-w-0 rounded-lg border border-scada-border bg-scada-panel p-4">
          <ForecasterMap step={step} selected={sel} onSelect={onSelect} dotSel={dot} onDot={onDot} />
        </div>
        <div className="min-w-0 xl:sticky xl:top-3 xl:max-h-[calc(100vh-24px)] xl:overflow-y-auto">
          <Panel id={sel} dot={dot} onClearDot={() => setDot(null)} />
        </div>
      </div>
    </div>
  )
}
