import { useEffect, useMemo, useRef, useState } from 'react'
import { NODES, LOCKS } from '../../data/pipelineContent.js'
import { windKw, SIM } from '../../data/useReplay.js'

// Pipeline "flow of light" diagram.
//   36 real inputs (5 families, one dot per input)  ->  curved ribbons  ->  40-model forecaster core
//   -> prediction + safety bound  ->  gate (checks + the +1 h alignment)  ->  GAP19 optimizer
//   -> dispatch of the chosen REAL hour drawn as a kilowatt Sankey  ->  loops (hourly, midnight).
// All motion is declarative SVG (animateMotion) on one 14-second cycle, so it can be paused and
// every pulse follows the order in which the data really flows.

const SCHED = {
  0: { cyc: 14, fam: 0.1, ribbon: [0.5, 2.8], core: 2.7, bound: [4.4, 5.6], pred1: [4.0, 4.9], bound1: [4.0, 5.0], gate: 5.0, pred2: [5.4, 6.5], bound2: [5.2, 6.8], wind: [4.8, 6.4], dispatch: [8.8, 10.2], hour: [10.6, 12.4], mid: [10.8, 13.8] },
  1: { cyc: 5, fam: 0.1, ribbon: [0.8, 3.8] },
  2: { cyc: 6, core: 0.4, bound: [2.8, 4.4], bound1: [2.6, 3.6] },
  3: { cyc: 5, pred1: [0.0, 1.0], gate: 1.0, pred2: [1.5, 2.8], wind: [0.4, 2.4], bound2: [1.2, 3.0] },
  4: { cyc: 5 },
  5: { cyc: 8, dispatch: [0, 1.8], hour: [2.4, 4.6], mid: [2.6, 6.6] },
}
const FAM = {
  sun: '#fbbf24', station: '#34d399', terrain: '#a78bfa', nwp: '#38bdf8', combined: '#f472b6',
}
const CORE = '#22d3ee'
const HOUR_C = '#c084fc'
const MID_C = '#22d3ee'
const SRC_C = { solar: '#facc15', wind: '#94a3b8', diesel: '#fb923c', battery: '#34d399' }

const CL = {
  sun: { x: 20, y: 30, w: 270, h: 78, rows: 1 },
  station: { x: 20, y: 124, w: 270, h: 104, rows: 2 },
  terrain: { x: 20, y: 244, w: 270, h: 78, rows: 1 },
  nwp: { x: 20, y: 338, w: 270, h: 104, rows: 2 },
  combined: { x: 20, y: 458, w: 270, h: 78, rows: 1 },
}
const ENTRY = { sun: 215, station: 265, terrain: 315, nwp: 365, combined: 415 }
const CORE_BOX = { x: 440, y: 170, w: 230, h: 310 }
const BOUND_BOX = { x: 440, y: 540, w: 230, h: 84 }
const GATE = { x: 770, y: 300, r: 38 }
const WIND_BOX = { x: 720, y: 430, w: 150, h: 74 }
const OPT = { x: 890, y: 120, w: 340, h: 380 }
const SK = { y0: 700, y1: 930, xl: 270, xr: 1010 }

const PATHS = {
  r_sun: `M290 ${CL.sun.y + CL.sun.h / 2} C 365 ${CL.sun.y + CL.sun.h / 2}, 365 ${ENTRY.sun}, 440 ${ENTRY.sun}`,
  r_station: `M290 ${CL.station.y + CL.station.h / 2} C 365 ${CL.station.y + CL.station.h / 2}, 365 ${ENTRY.station}, 440 ${ENTRY.station}`,
  r_terrain: `M290 ${CL.terrain.y + CL.terrain.h / 2} C 365 ${CL.terrain.y + CL.terrain.h / 2}, 365 ${ENTRY.terrain}, 440 ${ENTRY.terrain}`,
  r_nwp: `M290 ${CL.nwp.y + CL.nwp.h / 2} C 365 ${CL.nwp.y + CL.nwp.h / 2}, 365 ${ENTRY.nwp}, 440 ${ENTRY.nwp}`,
  r_combined: `M290 ${CL.combined.y + CL.combined.h / 2} C 365 ${CL.combined.y + CL.combined.h / 2}, 365 ${ENTRY.combined}, 440 ${ENTRY.combined}`,
  p_pred1: `M670 300 H ${GATE.x - GATE.r}`,
  p_pred2: `M${GATE.x + GATE.r} 300 H ${OPT.x}`,
  p_bound1: `M555 ${CORE_BOX.y + CORE_BOX.h} V ${BOUND_BOX.y}`,
  p_bound2: `M670 582 C 800 582, 900 560, 940 ${OPT.y + OPT.h + 2}`,
  p_wind: `M${WIND_BOX.x + WIND_BOX.w} 467 C 880 467, 880 440, ${OPT.x} 440`,
  p_dispatch: `M1060 ${OPT.y + OPT.h} V 646 H 640 V ${SK.y0 - 18}`,
  p_hour: `M${SK.xr + 12} ${SK.y0 - 14} H 1262 V 330 H ${OPT.x + OPT.w + 4}`,
  p_mid: `M640 ${SK.y1 + 20} H 8 V 176 H 16`,
}

// ---- declarative pulses ------------------------------------------------------------------------
const mkFr = (cyc) => (t) => Math.max(0, Math.min(1, t / cyc))

function Pulse({ path, color, start, end, r = 8, n = 2, cyc }) {
  const fr = mkFr(cyc)
  return Array.from({ length: n }, (_, i) => {
    const s = start + (end - start) * 0.2 * i
    const e = Math.min(cyc - 0.05, s + (end - start) * 0.7)
    const a = fr(s)
    const b = fr(e)
    const kt = a > 0 ? `0;${a};${b};1` : `0;${b};1`
    const kp = a > 0 ? '0;0;1;1' : '0;1;1'
    const ov = a > 0 ? '0;1;0' : '1;0'
    const ot = a > 0 ? `0;${a};${b}` : `0;${b}`
    return (
      <circle key={i} r={r} fill={color} stroke="#fff" strokeWidth="2" opacity="0" style={{ filter: `drop-shadow(0 0 7px ${color})` }}>
        <animateMotion dur={`${cyc}s`} repeatCount="indefinite" calcMode="linear" keyPoints={kp} keyTimes={kt}>
          <mpath href={`#${path}`} />
        </animateMotion>
        <animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" calcMode="discrete" values={ov} keyTimes={ot} />
      </circle>
    )
  })
}

function Glow({ x, y, w, h, rx = 16, color, start, end, peak = 0.3, cyc }) {
  const fr = mkFr(cyc)
  const a = fr(start)
  const b = fr(end)
  return (
    <rect x={x} y={y} width={w} height={h} rx={rx} fill={color} opacity="0" pointerEvents="none">
      <animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" calcMode="discrete" values={a > 0 ? `0;${peak};0` : `${peak};0`} keyTimes={a > 0 ? `0;${a};${b}` : `0;${b}`} />
    </rect>
  )
}

function Blink({ cx, cy, r, color, start, end, title, cyc }) {
  const fr = mkFr(cyc)
  const a = fr(start)
  const b = fr(end)
  return (
    <circle cx={cx} cy={cy} r={r} fill={color} opacity="0.4">
      <title>{title}</title>
      <animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" calcMode="discrete" values={a > 0 ? '0.4;1;0.4' : '1;0.4'} keyTimes={a > 0 ? `0;${a};${b}` : `0;${b}`} />
    </circle>
  )
}

// ---- Sankey of one real hour --------------------------------------------------------------------
function buildFlows(row) {
  if (!row) return null
  const solar = Math.min(Math.max(0, row.actual_ghi) * SIM.kPv, SIM.pvCapKw)
  const wind = windKw(row.timestamp)
  const diesel = row.diesel_kw
  const load = (row.demand_w ?? 0) / 1000
  const supply = solar + wind + diesel
  const full = row.battery_soc_pct >= 94.5
  const src = { solar, wind, diesel, battery: Math.max(0, load - supply) }
  const surplus = Math.max(0, supply - load)
  const links = []
  if (supply >= load && supply > 0) {
    for (const k of ['solar', 'wind', 'diesel']) {
      const share = src[k] / supply
      links.push({ from: k, to: 'load', v: share * load })
      links.push({ from: k, to: full ? 'waste' : 'charge', v: share * surplus })
    }
  } else {
    for (const k of ['solar', 'wind', 'diesel', 'battery']) links.push({ from: k, to: 'load', v: src[k] })
  }
  return { src, load, surplus, full, links: links.filter((l) => l.v > 0.05), supply }
}

const SINKS = [
  { id: 'load', label: 'Station', color: '#e4e4e7' },
  { id: 'charge', label: 'Battery charging', color: '#34d399' },
  { id: 'waste', label: 'Wasted', color: '#71717a' },
]
const SOURCES = [
  { id: 'solar', label: 'Solar' },
  { id: 'wind', label: 'Wind' },
  { id: 'diesel', label: 'Diesel' },
  { id: 'battery', label: 'Battery' },
]

function sankeyLayout(flows) {
  if (!flows) return null
  const gap = 16
  const leftTot = SOURCES.reduce((t, n) => t + flows.src[n.id], 0)
  const sinkVal = { load: 0, charge: 0, waste: 0 }
  for (const l of flows.links) sinkVal[l.to] += l.v
  const rightTot = SINKS.reduce((t, n) => t + sinkVal[n.id], 0)
  const avail = SK.y1 - SK.y0 - gap * 3
  const scale = Math.min(5, avail / Math.max(leftTot, rightTot, 1))
  const lh = leftTot * scale + gap * (SOURCES.filter((n) => flows.src[n.id] > 0.05).length - 1)
  const rh = rightTot * scale + gap * (SINKS.filter((n) => sinkVal[n.id] > 0.05).length - 1)
  const lTop = SK.y0 + (SK.y1 - SK.y0 - lh) / 2
  const rTop = SK.y0 + (SK.y1 - SK.y0 - rh) / 2
  const lPos = {}
  let y = lTop
  for (const n of SOURCES) {
    if (flows.src[n.id] <= 0.05) continue
    lPos[n.id] = { y, h: flows.src[n.id] * scale, used: 0 }
    y += flows.src[n.id] * scale + gap
  }
  const rPos = {}
  y = rTop
  for (const n of SINKS) {
    if (sinkVal[n.id] <= 0.05) continue
    rPos[n.id] = { y, h: sinkVal[n.id] * scale, used: 0 }
    y += sinkVal[n.id] * scale + gap
  }
  return { scale, lPos, rPos, sinkVal, lTop, rTop, rBottom: rTop + rh }
}

function Sankey({ flows, lay, onClick }) {
  if (!flows || !lay) return null
  const { scale, lPos, rPos, sinkVal } = lay
  const used = { l: {}, r: {} }
  const ribbons = flows.links.map((l, i) => {
    const a = lPos[l.from]
    const b = rPos[l.to]
    const h = l.v * scale
    const ul = used.l[l.from] ?? 0
    const ur = used.r[l.to] ?? 0
    const y0 = a.y + ul + h / 2
    const y1 = b.y + ur + h / 2
    used.l[l.from] = ul + h
    used.r[l.to] = ur + h
    const mx = (SK.xl + SK.xr) / 2
    const d = `M${SK.xl + 16} ${y0} C ${mx} ${y0}, ${mx} ${y1}, ${SK.xr} ${y1}`
    return { d, h, c: SRC_C[l.from], key: `${l.from}-${l.to}-${i}` }
  })

  return (
    <g onClick={onClick} style={{ cursor: 'pointer' }}>
      {ribbons.map((r) => (
        <g key={r.key}>
          <path d={r.d} fill="none" stroke={r.c} strokeOpacity="0.5" strokeWidth={Math.max(2, r.h)} style={{ transition: 'stroke-width 0.7s ease' }} />
          <path d={r.d} fill="none" stroke="#fff" strokeOpacity="0.7" strokeWidth="3" strokeDasharray="3 18" className="flow-anim" />
        </g>
      ))}
      {SOURCES.filter((n) => flows.src[n.id] > 0.05).map((n) => (
        <g key={n.id}>
          <rect x={SK.xl} y={lPos[n.id].y} width="16" height={Math.max(3, lPos[n.id].h)} rx="3" fill={SRC_C[n.id]} />
          <text x={SK.xl - 12} y={lPos[n.id].y + lPos[n.id].h / 2 + 7} textAnchor="end" fill="#fafafa" fontSize="20" fontWeight="700">{n.label} <tspan fill={SRC_C[n.id]}>{flows.src[n.id].toFixed(1)} kW</tspan></text>
        </g>
      ))}
      {SINKS.filter((n) => sinkVal[n.id] > 0.05).map((n) => (
        <g key={n.id}>
          <rect x={SK.xr} y={rPos[n.id].y} width="16" height={Math.max(3, rPos[n.id].h)} rx="3" fill={n.color} />
          <text x={SK.xr + 28} y={rPos[n.id].y + rPos[n.id].h / 2 + 7} fill="#fafafa" fontSize="20" fontWeight="700">{n.label} <tspan fill={n.color}>{sinkVal[n.id].toFixed(1)} kW</tspan></text>
        </g>
      ))}
    </g>
  )
}

// ---- main component -----------------------------------------------------------------------------
function Padlock({ x, y, c }) {
  return (
    <g transform={`translate(${x} ${y})`} fill="none" stroke={c} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="0" y="9" width="18" height="14" rx="3" fill={c} fillOpacity="0.25" />
      <path d="M4 9 V6 a5 5 0 0 1 10 0 V9" />
    </g>
  )
}

const OWNER = { fam: 1, core: 2, gate: 3, opt: 4, out: 5 }

export default function PipelineMap({ activeStep, auditPass, solveIdx, lockSel, onLock, selected, onSelect, exampleRow, exampleLabel, onPrev, onNext, auto, setAuto }) {
  const [playing, setPlaying] = useState(true)
  const svgRef = useRef(null)
  const flows = useMemo(() => buildFlows(exampleRow), [exampleRow])
  const lay = useMemo(() => sankeyLayout(flows), [flows])
  // Loop and dispatch lines start/end exactly on the diagram's bars.
  const hourD = lay ? `M${SK.xr + 8} ${lay.rTop} V ${lay.rTop - 26} H 1262 V 330 H ${OPT.x + OPT.w + 4}` : PATHS.p_hour
  const midD = lay ? `M${SK.xr + 8} ${lay.rBottom} V ${lay.rBottom + 16} H ${SK.xr + 60} V 950 H 8 V 176 H 16` : PATHS.p_mid
  const dispatchD = lay ? `M1060 ${OPT.y + OPT.h} V 646 H 640 V ${Math.min(lay.lTop, lay.rTop) - 12}` : PATHS.p_dispatch

  const S = SCHED[activeStep] ?? SCHED[0]
  const cyc = S.cyc
  const fr = mkFr(cyc)
  const overview = activeStep === 0
  const flowOpen = overview || activeStep > 1 || auditPass

  useEffect(() => {
    const el = svgRef.current
    if (!el || !el.pauseAnimations) return
    if (playing) el.unpauseAnimations()
    else el.pauseAnimations()
  }, [playing, activeStep, auditPass])

  const dim = (g) => ({ opacity: overview || OWNER[g] === activeStep ? 1 : 0.16, transition: 'opacity 0.45s ease' })
  const click = (id) => () => onSelect(id)
  const sel = (id) => selected === id

  const families = ['sun', 'station', 'terrain', 'nwp', 'combined']
  const ribbonW = (k) => 5 + NODES[k].count * 0.9
  const showRibbonPulse = S.ribbon && flowOpen

  const coreDots = Array.from({ length: 40 }, (_, i) => ({
    i,
    x: CORE_BOX.x + 30 + (i % 8) * 24.5,
    y: CORE_BOX.y + 120 + Math.floor(i / 8) * 28,
    add: i < 25,
  }))

  const dispIdx = overview || activeStep >= 5 ? 5 : activeStep === 4 ? solveIdx : -1
  const rowState = (i) => (dispIdx > i ? 'locked' : dispIdx === i ? 'solving' : 'pending')

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-3">
        <button
          onClick={() => setPlaying((p) => !p)}
          className={`flex h-11 min-w-[170px] items-center justify-center rounded-lg border-2 px-4 text-[18px] font-bold ${playing ? 'border-amber-500 bg-amber-950 text-amber-300' : 'border-emerald-500 bg-emerald-950 text-emerald-300'}`}
        >
          {playing ? '❚❚  Pause motion' : '▶  Play motion'}
        </button>
        <span className="text-[16px] font-semibold text-zinc-300">Click a box for its formula.</span>
      </div>

      <svg key={`${activeStep}-${flowOpen}`} ref={svgRef} viewBox="0 0 1300 1000" className="h-auto w-full rounded-lg" role="img" aria-label="POLARIS data flow" style={{ background: '#080b10', backgroundImage: 'radial-gradient(rgba(255,255,255,0.07) 1px, transparent 1px)', backgroundSize: '24px 24px' }}>
        <defs>
          <marker id="parr2" viewBox="0 0 10 10" refX="8" refY="5" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#d4d4d8" /></marker>
        </defs>

        {/* ===== chapter 1: inputs + ribbons ===== */}
        <g style={dim('fam')}>
          {families.map((k) => (
            <path key={k} id={`r_${k}`} d={PATHS[`r_${k}`]} fill="none" stroke={FAM[k]} strokeOpacity={flowOpen ? 0.4 : 0.12} strokeWidth={ribbonW(k)} strokeLinecap="round" strokeDasharray={flowOpen ? undefined : '10 10'} />
          ))}
          {families.map((k) => {
            const b = CL[k]
            const n = NODES[k]
            const cols = 7
            return (
              <g key={k} onClick={click(k)} style={{ cursor: 'pointer' }}>
                <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="14" fill="#101114" stroke={FAM[k]} strokeWidth={sel(k) ? 4 : 2} strokeOpacity={sel(k) ? 1 : 0.7} />
                <text x={b.x + 14} y={b.y + 28} fill="#fafafa" fontSize="21" fontWeight="700">{n.star ? '★ ' : ''}{n.title}</text>
                <text x={b.x + b.w - 14} y={b.y + 28} textAnchor="end" fill={FAM[k]} fontSize="21" fontWeight="800">{n.count}</text>
                {n.features.map((f, i) => (
                  S.fam != null
                    ? <Blink key={f.name} cx={b.x + 22 + (i % cols) * 36} cy={b.y + 52 + Math.floor(i / cols) * 26} r="9" color={FAM[k]} start={S.fam + 0.05 * i} end={S.fam + 0.05 * i + 0.8} title={f.name} cyc={cyc} />
                    : <circle key={f.name} cx={b.x + 22 + (i % cols) * 36} cy={b.y + 52 + Math.floor(i / cols) * 26} r="9" fill={FAM[k]} opacity="0.6"><title>{f.name}</title></circle>
                ))}
              </g>
            )
          })}
          {activeStep === 1 && (
            <g>
              <rect x="308" y="110" width="124" height="44" rx="22" fill={auditPass ? '#052e1b' : '#3a2204'} stroke={auditPass ? '#10b981' : '#f59e0b'} strokeWidth="3" />
              <text x="370" y="139" textAnchor="middle" fill={auditPass ? '#6ee7b7' : '#fcd34d'} fontSize="19" fontWeight="800">{auditPass ? '✔ AUDIT PASS' : 'AUDITING…'}</text>
            </g>
          )}
          {showRibbonPulse && families.map((k) => <Pulse key={k} path={`r_${k}`} color={FAM[k]} start={S.ribbon[0]} end={S.ribbon[1]} r={8} n={3} cyc={cyc} />)}
        </g>

        {/* ===== chapter 2: forecaster + safety bound ===== */}
        <g style={dim('core')}>
          <path id="p_bound1" d={PATHS.p_bound1} fill="none" stroke={CORE} strokeWidth="4" strokeOpacity="0.45" strokeDasharray="8 7" markerEnd="url(#parr2)" />
          <g onClick={click('n6')} style={{ cursor: 'pointer' }}>
            <rect x={CORE_BOX.x} y={CORE_BOX.y} width={CORE_BOX.w} height={CORE_BOX.h} rx="26" fill="#07222b" stroke={CORE} strokeWidth={sel('n6') ? 5 : 3} />
            <text x={CORE_BOX.x + CORE_BOX.w / 2} y={CORE_BOX.y + 44} textAnchor="middle" fill="#fff" fontSize="26" fontWeight="800">POLARIS N6</text>
            <text x={CORE_BOX.x + CORE_BOX.w / 2} y={CORE_BOX.y + 72} textAnchor="middle" fill="#67e8f9" fontSize="19" fontWeight="600">forecaster · 40 models</text>
            <text x={CORE_BOX.x + CORE_BOX.w / 2} y={CORE_BOX.y + 104} textAnchor="middle" fill="#a5f3fc" fontSize="17">36 in → 24 h out</text>
            {coreDots.map((d) => (
              S.core != null
                ? <Blink key={d.i} cx={d.x} cy={d.y} r="9" color={d.add ? '#22d3ee' : '#c084fc'} start={S.core + d.i * 0.04} end={S.core + d.i * 0.04 + 0.9} title={d.add ? 'additive model' : 'clearness-ratio specialist'} cyc={cyc} />
                : <circle key={d.i} cx={d.x} cy={d.y} r="9" fill={d.add ? '#22d3ee' : '#c084fc'} opacity="0.55"><title>{d.add ? 'additive model' : 'clearness-ratio specialist'}</title></circle>
            ))}
            <circle cx={CORE_BOX.x + 34} cy={CORE_BOX.y + CORE_BOX.h - 52} r="8" fill="#22d3ee" />
            <text x={CORE_BOX.x + 52} y={CORE_BOX.y + CORE_BOX.h - 46} fill="#e0f2fe" fontSize="18" fontWeight="600">25 additive models</text>
            <circle cx={CORE_BOX.x + 34} cy={CORE_BOX.y + CORE_BOX.h - 24} r="8" fill="#c084fc" />
            <text x={CORE_BOX.x + 52} y={CORE_BOX.y + CORE_BOX.h - 18} fill="#e0f2fe" fontSize="18" fontWeight="600">15 specialists</text>
          </g>
          <g onClick={click('bound')} style={{ cursor: 'pointer' }}>
            <rect x={BOUND_BOX.x} y={BOUND_BOX.y} width={BOUND_BOX.w} height={BOUND_BOX.h} rx="16" fill="#0b1b24" stroke={CORE} strokeWidth={sel('bound') ? 4 : 2} strokeDasharray="7 5" />
            <text x={BOUND_BOX.x + BOUND_BOX.w / 2} y={BOUND_BOX.y + 36} textAnchor="middle" fill="#fff" fontSize="21" fontWeight="800">90% safety bound</text>
            <text x={BOUND_BOX.x + BOUND_BOX.w / 2} y={BOUND_BOX.y + 62} textAnchor="middle" fill="#67e8f9" fontSize="17" fontWeight="600">→ battery reserve</text>
            {S.bound && <Glow x={BOUND_BOX.x} y={BOUND_BOX.y} w={BOUND_BOX.w} h={BOUND_BOX.h} color={CORE} start={S.bound[0]} end={S.bound[1]} peak={0.2} cyc={cyc} />}
          </g>
          <text x="566" y="520" fill="#a5f3fc" fontSize="16" fontWeight="700" paintOrder="stroke" stroke="#09090b" strokeWidth="5">confidence</text>
          {S.core != null && <Glow x={CORE_BOX.x} y={CORE_BOX.y} w={CORE_BOX.w} h={CORE_BOX.h} rx={26} color={CORE} start={S.core} end={S.core + 1.8} peak={0.14} cyc={cyc} />}
          {S.bound1 && <Pulse path="p_bound1" color="#a5f3fc" start={S.bound1[0]} end={S.bound1[1]} r={7} n={2} cyc={cyc} />}
        </g>

        {/* ===== chapter 3: gate + wind + hand-off channels ===== */}
        <g style={dim('gate')}>
          <path id="p_pred1" d={PATHS.p_pred1} fill="none" stroke={CORE} strokeWidth="8" strokeOpacity="0.55" />
          <path id="p_pred2" d={PATHS.p_pred2} fill="none" stroke="#e0f2fe" strokeWidth="8" strokeOpacity="0.55" markerEnd="url(#parr2)" />
          <path id="p_bound2" d={PATHS.p_bound2} fill="none" stroke={CORE} strokeWidth="4" strokeOpacity="0.45" strokeDasharray="8 7" markerEnd="url(#parr2)" />
          <path id="p_wind" d={PATHS.p_wind} fill="none" stroke="#94a3b8" strokeWidth="5" strokeOpacity="0.55" markerEnd="url(#parr2)" />
          <text x="701" y="276" textAnchor="middle" fill="#e0f2fe" fontSize="18" fontWeight="700" paintOrder="stroke" stroke="#09090b" strokeWidth="5">24 h</text>
          <g onClick={click('wind')} style={{ cursor: 'pointer' }}>
            <rect x={WIND_BOX.x} y={WIND_BOX.y} width={WIND_BOX.w} height={WIND_BOX.h} rx="14" fill="#101114" stroke="#94a3b8" strokeWidth={sel('wind') ? 4 : 2} />
            <text x={WIND_BOX.x + WIND_BOX.w / 2} y={WIND_BOX.y + 32} textAnchor="middle" fill="#fff" fontSize="19" fontWeight="800">Wind & demand</text>
            <text x={WIND_BOX.x + WIND_BOX.w / 2} y={WIND_BOX.y + 58} textAnchor="middle" fill="#cbd5e1" fontSize="16" fontWeight="600">known formulas</text>
            {S.wind && <Glow x={WIND_BOX.x} y={WIND_BOX.y} w={WIND_BOX.w} h={WIND_BOX.h} rx={14} color="#94a3b8" start={S.wind[0]} end={S.wind[1]} peak={0.18} cyc={cyc} />}
          </g>
          <g onClick={click('shift')} style={{ cursor: 'pointer' }}>
            <circle cx={GATE.x} cy={GATE.y} r={GATE.r} fill="#0b1220" stroke="#fda4af" strokeWidth={sel('shift') ? 6 : 3.5} />
            <text x={GATE.x} y={GATE.y + 8} textAnchor="middle" fill="#fecdd3" fontSize="24" fontWeight="800">+1 h</text>
            <text x={GATE.x} y={GATE.y - 52} textAnchor="middle" fill="#fda4af" fontSize="17" fontWeight="700">GATE</text>
            <text x={GATE.x} y={GATE.y + 66} textAnchor="middle" fill="#fda4af" fontSize="15" fontWeight="600">checks + align</text>
            {S.gate != null && (
              <circle cx={GATE.x} cy={GATE.y} r={GATE.r} fill="none" stroke="#fda4af" strokeWidth="5" opacity="0">
                <animate attributeName="r" dur={`${cyc}s`} repeatCount="indefinite" values={`${GATE.r};${GATE.r};${GATE.r + 26};${GATE.r + 26}`} keyTimes={`0;${fr(S.gate)};${fr(S.gate + 0.8)};1`} />
                <animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" values="0;0;0.9;0;0" keyTimes={`0;${fr(S.gate)};${fr(S.gate + 0.1)};${fr(S.gate + 0.8)};1`} />
              </circle>
            )}
          </g>
          {S.pred1 && <Pulse path="p_pred1" color={CORE} start={S.pred1[0]} end={S.pred1[1]} r={9} n={2} cyc={cyc} />}
          {S.pred2 && <Pulse path="p_pred2" color="#e0f2fe" start={S.pred2[0]} end={S.pred2[1]} r={9} n={2} cyc={cyc} />}
          {S.bound2 && <Pulse path="p_bound2" color="#a5f3fc" start={S.bound2[0]} end={S.bound2[1]} r={7} n={2} cyc={cyc} />}
          {S.wind && <Pulse path="p_wind" color="#cbd5e1" start={S.wind[0]} end={S.wind[1]} r={7} n={2} cyc={cyc} />}
        </g>

        {/* ===== chapter 4: optimizer with the lexicographic waterfall ===== */}
        <g style={dim('opt')} onClick={click('opt')} role="button" cursor="pointer">
          <rect x={OPT.x} y={OPT.y} width={OPT.w} height={OPT.h} rx="22" fill="#0d1018" stroke="#818cf8" strokeWidth={sel('opt') ? 5 : 3} />
          <text x={OPT.x + OPT.w / 2} y={OPT.y + 44} textAnchor="middle" fill="#fff" fontSize="26" fontWeight="800">GAP19 optimizer</text>
          <text x={OPT.x + OPT.w / 2} y={OPT.y + 72} textAnchor="middle" fill="#a5b4fc" fontSize="18" fontWeight="600">one priority at a time</text>
          {LOCKS.map((L, i) => {
            const y = OPT.y + 96 + i * 56
            const st = rowState(i)
            const stroke = lockSel === i ? '#ffffff' : st === 'locked' ? '#10b981' : st === 'solving' ? '#06b6d4' : '#64748b'
            const fill = st === 'locked' ? 'rgba(16,185,129,0.15)' : 'transparent'
            const txt = st === 'locked' ? '#6ee7b7' : st === 'solving' ? '#ffffff' : '#64748b'
            return (
              <g key={L.j} className={st === 'solving' ? 'pulse-solve' : undefined} style={{ transition: 'all 0.3s', cursor: 'pointer' }} onClick={(e) => { e.stopPropagation(); onLock?.(i) }}>
                <rect x={OPT.x + 24} y={y} width={OPT.w - 48} height="46" rx="10" fill={fill} stroke={stroke} strokeWidth={lockSel === i ? 5 : st === 'pending' ? 1.6 : 2.6} strokeDasharray={st === 'pending' ? '6 6' : undefined} strokeOpacity={st === 'pending' && lockSel !== i ? 0.55 : 1} />
                <text x={OPT.x + 42} y={y + 31} fill={txt} fontSize="21" fontWeight="800">{L.j}</text>
                <text x={OPT.x + 98} y={y + 31} fill={txt} fontSize="20" fontWeight="700">{L.short}</text>
                {st === 'locked' && <Padlock x={OPT.x + OPT.w - 66} y={y + 10} c="#10b981" />}
                {st === 'solving' && <text x={OPT.x + OPT.w - 40} y={y + 30} textAnchor="end" fill="#67e8f9" fontSize="14" fontWeight="800">SOLVING</text>}
                {st === 'pending' && <text x={OPT.x + OPT.w - 40} y={y + 30} textAnchor="end" fill="#64748b" fontSize="14" fontWeight="700">PENDING</text>}
              </g>
            )
          })}
        </g>

        {/* ===== chapter 5: dispatch, kilowatt ribbons, loops ===== */}
        <g style={dim('out')}>
          <path id="p_dispatch" d={dispatchD} fill="none" stroke="#e4e4e7" strokeWidth="8" strokeOpacity="0.5" markerEnd="url(#parr2)" />
          <path id="p_hour" d={hourD} fill="none" stroke={HOUR_C} strokeWidth="4" strokeDasharray="10 8" markerEnd="url(#parr2)" />
          <path id="p_mid" d={midD} fill="none" stroke={MID_C} strokeWidth="4" strokeDasharray="10 8" markerEnd="url(#parr2)" />
          <text x="1074" y="590" fill="#e4e4e7" fontSize="18" fontWeight="700" paintOrder="stroke" stroke="#09090b" strokeWidth="5">hour-1 plan</text>
          <g onClick={click('act')} style={{ cursor: 'pointer' }}>
            <text x="270" y="672" fill="#fff" fontSize="23" fontWeight="800">What it decided, in kilowatts</text>
          </g>
          <Sankey flows={flows} lay={lay} onClick={click('act')} />
          {lay && <circle cx={SK.xr + 8} cy={lay.rTop} r="7" fill="#c084fc" stroke="#fff" strokeWidth="2" />}
          {lay && <circle cx={SK.xr + 8} cy={lay.rBottom} r="7" fill="#22d3ee" stroke="#fff" strokeWidth="2" />}
          <text x="1292" y="560" textAnchor="middle" fill="#e9d5ff" fontSize="20" fontWeight="800" transform="rotate(-90 1292 560)">EVERY HOUR: re-plan with the new battery level</text>
          <rect x="240" y="962" width="640" height="34" rx="17" fill="#083344" stroke={MID_C} strokeWidth="2" />
          <text x="560" y="986" textAnchor="middle" fill="#a5f3fc" fontSize="20" fontWeight="800">EVERY MIDNIGHT: new forecast with the last 24 h of real readings</text>
          {S.dispatch && <Pulse path="p_dispatch" color="#f4f4f5" start={S.dispatch[0]} end={S.dispatch[1]} r={9} n={3} cyc={cyc} />}
          {S.hour && <Pulse path="p_hour" color={HOUR_C} start={S.hour[0]} end={S.hour[1]} r={9} n={2} cyc={cyc} />}
          {S.mid && <Pulse path="p_mid" color={MID_C} start={S.mid[0]} end={S.mid[1]} r={9} n={3} cyc={cyc} />}
        </g>
      </svg>

      {(activeStep === 5 || overview) && (
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <span className="text-[17px] font-bold text-white">Real hour in the kilowatt diagram:</span>
          <button onClick={onPrev} className="rounded-lg border border-scada-border px-3 py-1.5 text-[17px] font-bold text-zinc-100 hover:bg-zinc-800">◀ Previous</button>
          <span className="tnum min-w-[260px] rounded-lg bg-zinc-800 px-3 py-1.5 text-center text-[17px] font-bold text-white">{exampleLabel}</span>
          <button onClick={onNext} className="rounded-lg border border-scada-border px-3 py-1.5 text-[17px] font-bold text-zinc-100 hover:bg-zinc-800">Next ▶</button>
          <label className="flex items-center gap-2 text-[16px] font-semibold text-zinc-200">
            <input type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} className="h-5 w-5 accent-cyan-400" /> auto
          </label>
        </div>
      )}
    </div>
  )
}
