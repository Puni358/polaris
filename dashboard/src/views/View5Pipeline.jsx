import { useCallback, useEffect, useMemo, useState } from 'react'
import PipelineMap from '../components/story/PipelineMap.jsx'
import FirewallStage from '../components/story/FirewallStage.jsx'
import HorizonTape from '../components/story/HorizonTape.jsx'
import ProvenanceBadge from '../components/ProvenanceBadge.jsx'
import { useMatched } from '../data/useMatched.js'
import { useReplayData, SIM } from '../data/useReplay.js'
import { NODES, TAGS, LOCKS, NODE_STEP, STEP_NODE, STEPS, FEATURE_INFO, WHEN } from '../data/pipelineContent.js'

const FAMILY_WHEN = { sun: WHEN.calc, station: WHEN.station, terrain: WHEN.terrain, nwp: WHEN.nwp, combined: WHEN.comb }

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const SOLVE_MS = 800

// A few real hours that tell different stories, picked from the run.
function pickExamples(series) {
  if (!series) return []
  const sunKw = (r) => Math.min(Math.max(0, r.actual_ghi) * SIM.kPv, SIM.pvCapKw)
  const m = (r) => new Date(r.timestamp).getUTCMonth()
  const rules = [
    ['Winter peak: diesel steps in', (r) => [0, 1, 10, 11].includes(m(r)) && r.diesel_kw > 0 && r.demand_w >= 36000],
    ['Night: the battery carries the station', (r) => [0, 1, 10, 11].includes(m(r)) && r.diesel_kw === 0 && r.battery_net_kw < -12],
    ['Spring: sun and wind cover the load', (r) => [2, 3].includes(m(r)) && r.diesel_kw === 0 && sunKw(r) > 15],
    ['Midnight sun: surplus charges the battery', (r) => [4, 5, 6].includes(m(r)) && sunKw(r) > 30 && r.battery_net_kw > 8 && r.battery_soc_pct < 94],
    ['Battery full: surplus is wasted', (r) => [4, 5, 6, 7].includes(m(r)) && r.battery_soc_pct >= 94.5 && r.battery_net_kw > 2],
    ['Diesel runs and charges the battery', (r) => r.diesel_kw > 0 && r.battery_net_kw > 20],
  ]
  const out = []
  for (const [caption, test] of rules) {
    const i = series.findIndex(test)
    if (i >= 0) out.push({ caption, row: series[i] })
  }
  return out
}

function Tag({ t }) {
  const x = TAGS[t]
  return <span className={`rounded px-2 py-0.5 text-[14px] font-bold tracking-wide ${x.cls}`}>{x.label}</span>
}

function Panel({ id, lockShown, lockedCount, activeStep, feat, onFeat, onOffline }) {
  const n = NODES[id]
  if (!n) return null
  const info = feat ? FEATURE_INFO[feat] : null
  const L = lockShown != null ? LOCKS[lockShown] : null
  return (
    <div className="rounded-lg border-2 border-zinc-600 bg-scada-panel p-5">
      {id === 'opt' && activeStep === 4 && (
        <div className={`mb-4 rounded-lg border-2 p-4 transition-colors ${L ? 'border-emerald-500 bg-emerald-950/30' : 'border-slate-600 bg-slate-900/40'}`}>
          {L ? (
            <>
              <div className="mb-1 text-[16px] font-bold tracking-wide text-emerald-300">Priority {lockShown + 1} of 5 · {L.j} {lockShown < lockedCount ? '· LOCKED' : '· solving'}</div>
              <div className="text-[22px] font-extrabold text-white">{L.title}</div>
              <div className="tnum mt-1 text-[20px] font-bold text-emerald-300">{L.formula}</div>
              <p className="mt-1 text-[18px] font-semibold text-zinc-100">{L.text}</p>
            </>
          ) : (
            <p className="text-[18px] font-semibold text-zinc-200">Click J1, J1b, J2, J3 or J4 on the diagram to lock that priority and read what it guarantees.</p>
          )}
        </div>
      )}
      {info && (
        <div className="mb-4 rounded-lg border-2 border-cyan-500 bg-cyan-950/25 p-4">
          <div className="mb-1 flex items-center justify-between gap-2">
            <span className="tnum rounded bg-zinc-800 px-2 py-0.5 text-[15px] font-bold text-cyan-200">{feat}</span>
            <button onClick={() => onFeat(null)} className="text-[15px] font-bold text-zinc-300 hover:text-white">✕ close</button>
          </div>
          <div className="text-[22px] font-extrabold text-white">{info.full}</div>
          <div className="mt-2 text-[15px] font-bold uppercase tracking-wide text-cyan-300">What it means</div>
          <p className="text-[18px] font-semibold leading-relaxed text-zinc-100">{info.meaning}</p>
          <div className="mt-2 text-[15px] font-bold uppercase tracking-wide text-cyan-300">How it is calculated</div>
          <pre className="tnum whitespace-pre-wrap text-[17px] leading-relaxed text-zinc-100">{info.how}</pre>
          <div className="mt-2 text-[15px] font-bold uppercase tracking-wide text-cyan-300">Source</div>
          {info.source.length === 0 ? (
            <p className="text-[18px] font-semibold text-zinc-100">Calculated from the calendar. No outside data.</p>
          ) : (
            <ul className="flex flex-col gap-1">
              {info.source.map((so) => (
                <li key={so.url}><a href={so.url} target="_blank" rel="noreferrer" className="text-[18px] font-bold text-sky-300 underline hover:text-sky-200">{so.label} ↗</a></li>
              ))}
            </ul>
          )}
          <div className="mt-2 text-[15px] font-bold uppercase tracking-wide text-cyan-300">When we get it</div>
          <p className="text-[18px] font-semibold leading-relaxed text-zinc-100">{info.when}</p>
        </div>
      )}
      <div className="mb-2 flex flex-wrap items-center gap-3">
        <h3 className="text-[22px] font-bold text-white">{n.title}</h3>
        {n.count != null && n.count > 0 && <span className="tnum rounded-full bg-zinc-700 px-3 py-0.5 text-[17px] font-bold text-white">{n.count}</span>}
        <Tag t={n.tag} />
        {n.pendingTag && <Tag t="pending" />}
      </div>
      <p className="mb-3 text-[18px] leading-relaxed text-zinc-200">{n.summary}</p>
      {FAMILY_WHEN[id] && <p className="mb-3 rounded-md border border-scada-border bg-scada-panel2 p-3 text-[17px] font-semibold text-zinc-100"><span className="font-bold text-cyan-300">When we get it: </span>{FAMILY_WHEN[id]}</p>}
      {n.features.length > 0 && <p className="mb-2 text-[16px] font-semibold text-zinc-300">Click an input name for its full name, meaning, formula and source.</p>}
      {n.features.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {n.features.map((f) => (
            <button key={f.name} onClick={() => onFeat(f.name)} className={`tnum rounded-md border px-2 py-0.5 text-[15px] font-semibold hover:border-cyan-400 ${feat === f.name ? 'border-cyan-400 bg-cyan-950 text-white' : 'border-scada-border bg-scada-panel2 text-zinc-100'}`} title="Click for the full name, meaning and source">{f.name}</button>
          ))}
        </div>
      )}
      <div className="flex flex-col gap-2.5">
        {n.formulas.map(([label, text]) => (
          <div key={label} className="rounded-md border border-scada-border bg-scada-panel2 p-3">
            <div className="mb-1 text-[15px] font-bold uppercase tracking-wide text-cyan-300">{label}</div>
            <pre className="tnum whitespace-pre-wrap text-[16.5px] leading-relaxed text-zinc-100">{text}</pre>
          </div>
        ))}
      </div>
      {(id === 'clues' || FAMILY_WHEN[id]) && <button onClick={onOffline} className="mt-3 rounded-lg border-2 border-amber-500 bg-amber-950 px-4 py-2 text-[18px] font-bold text-amber-200">Can it run offline? ▸</button>}
      {n.note && <p className="mt-3 rounded-md border border-amber-800 bg-amber-950/30 p-3 text-[17px] font-semibold text-amber-200">{n.note}</p>}
    </div>
  )
}

export default function View5Pipeline() {
  const [activeStep, setActiveStep] = useState(1) // 0 = overview, 1..5 = chapters
  const [sel, setSel] = useState(STEP_NODE[1])
  const [feat, setFeat] = useState(null)
  const [auditPass, setAuditPass] = useState(false)
  const [solveIdx, setSolveIdx] = useState(-1) // -1 not in chapter 4, otherwise number of locked priorities 0..5
  const [lockSel, setLockSel] = useState(null)
  const [autoRun, setAutoRun] = useState(false)

  const { view } = useMatched()
  const { series } = useReplayData(view?.bestId ?? 'scenario2_initial_state_exact')
  const examples = useMemo(() => pickExamples(series), [series])
  const [ex, setEx] = useState(0)
  const [auto, setAuto] = useState(false)
  useEffect(() => {
    if (!auto || examples.length < 2) return undefined
    const t = setInterval(() => setEx((i) => (i + 1) % examples.length), 8000)
    return () => clearInterval(t)
  }, [auto, examples.length])
  const cur = examples[Math.min(ex, Math.max(0, examples.length - 1))]
  const d = cur ? new Date(cur.row.timestamp) : null
  const label = cur ? `${DAYS[d.getUTCDay()]} ${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]} ${String(d.getUTCHours()).padStart(2, '0')}:00 — ${cur.caption}` : 'Loading a real hour…'

  const goStep = useCallback((n) => {
    const s = Math.max(1, Math.min(5, n))
    setActiveStep(s)
    setSel(STEP_NODE[s])
    setFeat(null)
  }, [])

  // Presenter keys: wireless clickers send ArrowLeft / ArrowRight.
  useEffect(() => {
    const onKey = (e) => {
      const tag = (e.target?.tagName || '').toLowerCase()
      if (tag === 'input' || tag === 'select' || tag === 'textarea') return
      if (e.key === 'ArrowRight') { e.preventDefault(); setActiveStep((s) => { const n = Math.min(5, Math.max(1, s + 1)); setSel(STEP_NODE[n]); return n }) }
      if (e.key === 'ArrowLeft') { e.preventDefault(); setActiveStep((s) => { const n = Math.max(1, s - 1); setSel(STEP_NODE[n]); return n }) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  // Chapter 1 re-runs the audit every time it opens; later chapters need it passed.
  useEffect(() => { if (activeStep === 1) setAuditPass(false) }, [activeStep])

  // Chapter 4 starts with every priority pending; the presenter locks them one at a time by clicking,
  // or presses "Run all" to lock them in order, 800 ms apart.
  useEffect(() => {
    if (activeStep !== 4) { setSolveIdx(-1); setLockSel(null); setAutoRun(false); return }
    setSolveIdx(0)
    setLockSel(null)
    setAutoRun(false)
  }, [activeStep])
  useEffect(() => {
    if (!autoRun) return undefined
    const t = setInterval(() => {
      setSolveIdx((i) => {
        const n = Math.min(5, (i < 0 ? 0 : i) + 1)
        setLockSel(n - 1)
        if (n >= 5) setAutoRun(false)
        return n
      })
    }, SOLVE_MS)
    return () => clearInterval(t)
  }, [autoRun])
  const onLock = (i) => {
    setAutoRun(false)
    setSolveIdx((cur) => Math.max(cur, i + 1))
    setLockSel(i)
    setSel('opt')
  }

  const onSelect = (id) => {
    setSel(id)
    setFeat(null)
    const owner = NODE_STEP[id]
    if (owner && owner !== activeStep) setActiveStep(owner)
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end justify-between gap-2 px-1">
        <div>
          <h2 className="text-[26px] font-bold text-white">How POLARIS works, end to end</h2>
          <p className="text-[18px] text-zinc-300">Use ← → (or the buttons) to step through the five chapters.</p>
        </div>
        <ProvenanceBadge provenance="SIMULATED" />
      </div>

      {/* chapter stepper */}
      <div className="flex flex-wrap items-center gap-2 rounded-lg border border-scada-border bg-scada-panel p-3">
        <button onClick={() => goStep(activeStep - 1)} disabled={activeStep <= 1} className="rounded-lg border border-scada-border px-4 py-2 text-[18px] font-bold text-zinc-100 hover:bg-zinc-800 disabled:opacity-30">◀ Prev</button>
        {STEPS.map((s) => (
          <button
            key={s.id}
            onClick={() => goStep(s.id)}
            className={`rounded-lg border-2 px-3.5 py-2 text-[17px] font-bold transition-colors ${activeStep === s.id ? 'border-cyan-400 bg-cyan-950 text-white' : 'border-scada-border text-zinc-300 hover:text-white'}`}
          >
            <span className="tnum mr-2 rounded-full bg-zinc-700 px-2 py-0.5 text-[15px]">{s.id}</span>{s.label}
          </button>
        ))}
        <button onClick={() => goStep(activeStep + 1)} disabled={activeStep >= 5} className="rounded-lg border border-scada-border px-4 py-2 text-[18px] font-bold text-zinc-100 hover:bg-zinc-800 disabled:opacity-30">Next ▶</button>
        <button onClick={() => { setActiveStep(0); setSel('n6') }} className={`ml-auto rounded-lg border px-3 py-2 text-[17px] font-bold ${activeStep === 0 ? 'border-amber-400 bg-amber-950 text-amber-200' : 'border-scada-border text-zinc-300 hover:text-white'}`}>Show everything</button>
      </div>

      <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-[65fr_35fr]">
        <div className="flex min-w-0 flex-col gap-4">
          <div className="rounded-lg border border-scada-border bg-scada-panel p-4">
            <PipelineMap
              activeStep={activeStep}
              auditPass={auditPass}
              solveIdx={solveIdx}
              lockSel={lockSel}
              onLock={onLock}
              selected={sel}
              onSelect={onSelect}
              exampleRow={cur?.row}
              exampleLabel={label}
              onPrev={() => setEx((i) => (i - 1 + examples.length) % Math.max(1, examples.length))}
              onNext={() => setEx((i) => (i + 1) % Math.max(1, examples.length))}
              auto={auto}
              setAuto={setAuto}
            />
          </div>
          {activeStep === 4 && (
            <div className="flex flex-wrap items-center gap-3 rounded-lg border border-scada-border bg-scada-panel p-4">
              <span className="text-[18px] font-bold text-white">Priorities locked: {Math.max(0, solveIdx)} of 5</span>
              <button onClick={() => { setSolveIdx(0); setLockSel(null); setAutoRun(true) }} className="rounded-lg border-2 border-emerald-500 bg-emerald-950 px-4 py-2 text-[18px] font-bold text-emerald-300">▶ Run all in order</button>
              <button onClick={() => { setAutoRun(false); setSolveIdx(0); setLockSel(null) }} className="rounded-lg border border-scada-border px-4 py-2 text-[18px] font-bold text-zinc-100 hover:bg-zinc-800">↺ Reset</button>
              <span className="text-[17px] font-semibold text-zinc-300">or click a priority on the diagram</span>
            </div>
          )}
          {activeStep === 1 && <FirewallStage onPass={() => setAuditPass(true)} />}
          {(activeStep === 5 || activeStep === 0) && <HorizonTape active={activeStep === 5} baseHour={cur ? new Date(cur.row.timestamp).getUTCHours() : 8} />}
        </div>

        <div className="min-w-0 xl:sticky xl:top-3 xl:max-h-[calc(100vh-24px)] xl:overflow-y-auto">
          <Panel id={sel} lockShown={activeStep === 4 ? lockSel : null} lockedCount={Math.max(0, solveIdx)} activeStep={activeStep} feat={feat} onFeat={setFeat} onOffline={() => onSelect('offline')} />
        </div>
      </div>
    </div>
  )
}
