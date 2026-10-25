import { useEffect, useRef, useState } from 'react'
import { O_NODES } from '../../data/optimizerContent.js'

const COL = { inp: '#fbbf24', puzzle: '#22d3ee', lad: '#818cf8', plan: '#e0f2fe', act: '#e4e4e7', meas: '#34d399', err: '#f472b6', fc: '#22d3ee' }
const B = {
  inp: { x: 20, y: 50, w: 250, h: 270 },
  unk: { x: 340, y: 60, w: 240, h: 120 },
  rules: { x: 340, y: 210, w: 240, h: 120 },
  ladder: { x: 650, y: 40, w: 330, h: 340 },
  plan: { x: 1050, y: 60, w: 230, h: 120 },
  act: { x: 1050, y: 230, w: 230, h: 110 },
  meas: { x: 1050, y: 440, w: 230, h: 110 },
  err: { x: 650, y: 440, w: 330, h: 130 },
  fc: { x: 20, y: 440, w: 250, h: 120 },
}
const ROWS = [['j1', 'J1', 'Critical load'], ['j1b', 'J1b', 'Non-critical load'], ['j2', 'J2', 'Battery reserve'], ['j3', 'J3', 'Diesel fuel'], ['j4', 'J4', 'Curtailment']]
const P = {
  p_inp_unk: 'M270 120 C 305 120, 305 120, 340 120',
  p_inp_rules: 'M270 260 C 305 260, 305 270, 340 270',
  p_unk_lad: 'M580 120 C 615 120, 615 150, 650 150',
  p_rules_lad: 'M580 270 C 615 270, 615 250, 650 250',
  p_lad_plan: 'M980 120 H 1050',
  p_plan_act: 'M1165 180 V 230',
  p_act_meas: 'M1165 340 V 440',
  p_meas_err: 'M1050 495 H 980',
  p_err_inp: 'M650 505 H 320 V 300 H 274',
  p_meas_fc: 'M1165 550 V 640 H 145 V 562',
  p_fc_inp: 'M145 440 V 324',
}
const SCHED = {
  0: { cyc: 14, a: [0, 1.8], b: [2, 3.8], lad: [4, 8], c: [8, 9.2], d: [9.2, 10.4], e: [10.6, 11.6], f: [11.8, 13.4], g: [11.8, 13.9], h: [13, 13.9] },
  1: { cyc: 4, a: [0.2, 2.6] },
  2: { cyc: 5, b: [0.3, 2.8] },
  3: { cyc: 5, c: [0.3, 2.0] },
  4: { cyc: 5, d: [0.2, 1.8] },
  5: { cyc: 9, e: [0, 1.4], f: [1.5, 2.8], g: [3, 5.6], h: [3.2, 8.5] },
}
const OWN = { inp: 1, puzzle: 2, ladder: 3, plan: 4, act: 4, meas: 5, err: 5, fc: 5 }
const mkFr = (cyc) => (t) => Math.max(0, Math.min(1, t / cyc))

function Pulse({ path, color, start, end, cyc, n = 2, r = 8 }) {
  const fr = mkFr(cyc)
  return Array.from({ length: n }, (_, i) => {
    const s = start + (end - start) * 0.2 * i
    const e = Math.min(cyc - 0.05, s + (end - start) * 0.7)
    const a = fr(s)
    const b = fr(e)
    return (
      <circle key={i} r={r} fill={color} stroke="#fff" strokeWidth="2" opacity="0" style={{ filter: `drop-shadow(0 0 7px ${color})` }}>
        <animateMotion dur={`${cyc}s`} repeatCount="indefinite" calcMode="linear" keyPoints={a > 0 ? '0;0;1;1' : '0;1;1'} keyTimes={a > 0 ? `0;${a};${b};1` : `0;${b};1`}><mpath href={`#${path}`} /></animateMotion>
        <animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" calcMode="discrete" values={a > 0 ? '0;1;0' : '1;0'} keyTimes={a > 0 ? `0;${a};${b}` : `0;${b}`} />
      </circle>
    )
  })
}

function Padlock({ x, y }) {
  return (
    <g transform={`translate(${x} ${y})`} fill="none" stroke="#10b981" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="0" y="9" width="18" height="14" rx="3" fill="#10b981" fillOpacity="0.25" />
      <path d="M4 9 V6 a5 5 0 0 1 10 0 V9" />
    </g>
  )
}

export default function OptimizerMap({ step, lockIdx, selected, onSelect }) {
  const [playing, setPlaying] = useState(true)
  const svgRef = useRef(null)
  const S = SCHED[step] ?? SCHED[0]
  const cyc = S.cyc
  const overview = step === 0
  useEffect(() => {
    const el = svgRef.current
    if (!el || !el.pauseAnimations) return
    if (playing) el.unpauseAnimations()
    else el.pauseAnimations()
  }, [playing, step])

  const dim = (k) => ({ opacity: overview || OWN[k] === step ? 1 : 0.16, transition: 'opacity 0.45s ease' })
  const click = (id) => () => onSelect(id)
  const disp = overview || step > 3 ? 5 : step === 3 ? lockIdx : -1
  const rowState = (i) => (disp > i ? 'locked' : disp === i ? 'solving' : 'pending')
  const edge = (id, color, w = 5, dash) => <path id={id} d={P[id]} fill="none" stroke={color} strokeWidth={w} strokeOpacity="0.5" strokeDasharray={dash} markerEnd="url(#oarr)" />
  const frame = (id, color, dash) => {
    const b = B[id]
    return <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="18" fill="#0f1014" stroke={color} strokeWidth={selected === id ? 5 : 2.6} strokeDasharray={dash} />
  }

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-3">
        <button onClick={() => setPlaying((p) => !p)} className={`flex h-11 min-w-[170px] items-center justify-center rounded-lg border-2 px-4 text-[18px] font-bold ${playing ? 'border-amber-500 bg-amber-950 text-amber-300' : 'border-emerald-500 bg-emerald-950 text-emerald-300'}`}>{playing ? '❚❚  Pause motion' : '▶  Play motion'}</button>
        <span className="text-[16px] font-semibold text-zinc-300">Click a box or a priority to read about it.</span>
      </div>

      <svg key={step} ref={svgRef} viewBox="0 0 1300 680" className="h-auto w-full rounded-lg" role="img" aria-label="Inside the GAP19 optimizer" style={{ background: '#080b10', backgroundImage: 'radial-gradient(rgba(255,255,255,0.07) 1px, transparent 1px)', backgroundSize: '24px 24px' }}>
        <defs>
          <marker id="oarr" viewBox="0 0 10 10" refX="8" refY="5" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#d4d4d8" /></marker>
        </defs>

        <g style={dim('inp')}>
          {edge('p_inp_unk', COL.inp, 6)}{edge('p_inp_rules', COL.inp, 6)}
          <g onClick={click('inp')} style={{ cursor: 'pointer' }}>
            {frame('inp', COL.inp)}
            <text x="145" y="92" textAnchor="middle" fill="#fff" fontSize="23" fontWeight="800">What it is given</text>
            {[['☀  24 h solar forecast', '#fde047'], ['≋  Wind & demand', '#cbd5e1'], ['▣  Battery reserve target', '#67e8f9'], ['▮  Battery level NOW', '#34d399']].map(([t, c], i) => (
              <g key={t}>
                <rect x="38" y={112 + i * 48} width="214" height="38" rx="10" fill="#18181b" stroke={c} strokeWidth={i === 3 ? 3 : 1.5} />
                <text x="52" y={138 + i * 48} fill={c} fontSize="18" fontWeight="700">{t}</text>
              </g>
            ))}
            {S.a && <rect x={B.inp.x} y={B.inp.y} width={B.inp.w} height={B.inp.h} rx="18" fill={COL.inp} opacity="0"><animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" calcMode="discrete" values={`0.18;0`} keyTimes={`0;${mkFr(cyc)(S.a[1])}`} /></rect>}
          </g>
        </g>

        <g style={dim('puzzle')}>
          {edge('p_unk_lad', COL.puzzle, 6)}{edge('p_rules_lad', COL.puzzle, 6)}
          <g onClick={click('unk')} style={{ cursor: 'pointer' }}>
            {frame('unk', COL.puzzle)}
            <text x="460" y="105" textAnchor="middle" fill="#fff" fontSize="34" fontWeight="800">432</text>
            <text x="460" y="134" textAnchor="middle" fill="#fff" fontSize="21" fontWeight="800">unknowns to decide</text>
            <text x="460" y="160" textAnchor="middle" fill="#67e8f9" fontSize="16" fontWeight="600">24 hours × 18 · 96 yes/no switches</text>
          </g>
          <g onClick={click('rules')} style={{ cursor: 'pointer' }}>
            {frame('rules', COL.puzzle)}
            <text x="460" y="255" textAnchor="middle" fill="#fff" fontSize="34" fontWeight="800">336</text>
            <text x="460" y="284" textAnchor="middle" fill="#fff" fontSize="21" fontWeight="800">rules it must obey</text>
            <text x="460" y="310" textAnchor="middle" fill="#67e8f9" fontSize="16" fontWeight="600">physics · limits · reserve</text>
          </g>
        </g>

        <g style={dim('ladder')}>
          {edge('p_lad_plan', COL.lad, 6)}
          {frame('ladder', COL.lad)}
          <text x={B.ladder.x + B.ladder.w / 2} y={B.ladder.y + 40} textAnchor="middle" fill="#fff" fontSize="25" fontWeight="800">GAP19 · HiGHS</text>
          <text x={B.ladder.x + B.ladder.w / 2} y={B.ladder.y + 68} textAnchor="middle" fill="#a5b4fc" fontSize="18" fontWeight="600">one priority at a time</text>
          {ROWS.map(([id, j, name], i) => {
            const y = B.ladder.y + 92 + i * 48
            const st = rowState(i)
            const stroke = selected === id ? '#fff' : st === 'locked' ? '#10b981' : st === 'solving' ? '#06b6d4' : '#64748b'
            const txt = st === 'locked' ? '#6ee7b7' : st === 'solving' ? '#fff' : '#94a3b8'
            return (
              <g key={id} className={st === 'solving' ? 'pulse-solve' : undefined} style={{ cursor: 'pointer' }} onClick={(e) => { e.stopPropagation(); onSelect(id) }}>
                <rect x={B.ladder.x + 22} y={y} width={B.ladder.w - 44} height="40" rx="10" fill={st === 'locked' ? 'rgba(16,185,129,0.15)' : 'transparent'} stroke={stroke} strokeWidth={selected === id ? 5 : st === 'pending' ? 1.6 : 2.6} strokeDasharray={st === 'pending' && selected !== id ? '6 6' : undefined} />
                <text x={B.ladder.x + 40} y={y + 27} fill={txt} fontSize="20" fontWeight="800">{j}</text>
                <text x={B.ladder.x + 96} y={y + 27} fill={txt} fontSize="19" fontWeight="700">{name}</text>
                {st === 'locked' && <Padlock x={B.ladder.x + B.ladder.w - 64} y={y + 8} />}
              </g>
            )
          })}
        </g>

        <g style={dim('plan')}>
          {edge('p_plan_act', COL.plan, 6)}
          <g onClick={click('plan')} style={{ cursor: 'pointer' }}>
            {frame('plan', COL.plan)}
            <text x="1165" y="105" textAnchor="middle" fill="#fff" fontSize="23" fontWeight="800">24-hour plan</text>
            <text x="1165" y="133" textAnchor="middle" fill="#bae6fd" fontSize="17" fontWeight="600">every source, hour by hour</text>
            {[...Array(12)].map((_, i) => <rect key={i} x={1072 + i * 16.5} y={146 + (i % 3) * 3} width="12" height={18 - (i % 3) * 3} rx="2" fill={i === 0 ? '#34d399' : '#22d3ee'} opacity={i === 0 ? 1 : 0.55} />)}
          </g>
          <g onClick={click('act')} style={{ cursor: 'pointer' }}>
            {frame('act', COL.act)}
            <text x="1165" y="275" textAnchor="middle" fill="#fff" fontSize="23" fontWeight="800">Do hour 1 only</text>
            <text x="1165" y="305" textAnchor="middle" fill="#d4d4d8" fontSize="17" fontWeight="600">battery + diesel move</text>
          </g>
        </g>

        <g style={dim('meas')}>
          {edge('p_act_meas', COL.meas, 6)}{edge('p_meas_err', COL.meas, 6)}
          <g onClick={click('meas')} style={{ cursor: 'pointer' }}>
            {frame('meas', COL.meas)}
            <text x="1165" y="485" textAnchor="middle" fill="#fff" fontSize="22" fontWeight="800">Station measured</text>
            <text x="1165" y="514" textAnchor="middle" fill="#6ee7b7" fontSize="17" fontWeight="600">real battery level</text>
          </g>
          <g onClick={click('err')} style={{ cursor: 'pointer' }}>
            {frame('err', COL.err)}
            <text x="815" y="486" textAnchor="middle" fill="#fff" fontSize="24" fontWeight="800">Plan vs reality</text>
            <text x="815" y="516" textAnchor="middle" fill="#fbcfe8" fontSize="18" fontWeight="600">error = measured − planned</text>
            <text x="815" y="545" textAnchor="middle" fill="#f9a8d4" fontSize="17" fontWeight="600">next plan starts from the measured level</text>
          </g>
          {edge('p_err_inp', '#c084fc', 5, '10 8')}
          <text x="470" y="494" textAnchor="middle" fill="#e9d5ff" fontSize="19" fontWeight="800" paintOrder="stroke" stroke="#09090b" strokeWidth="5">EVERY HOUR</text>
        </g>
        <g style={dim('fc')}>
          {edge('p_meas_fc', COL.fc, 5, '10 8')}{edge('p_fc_inp', COL.fc, 5)}
          <g onClick={click('fc')} style={{ cursor: 'pointer' }}>
            {frame('fc', COL.fc, '8 6')}
            <text x="145" y="485" textAnchor="middle" fill="#fff" fontSize="22" fontWeight="800">Forecaster</text>
            <text x="145" y="514" textAnchor="middle" fill="#67e8f9" fontSize="17" fontWeight="600">new forecast every midnight</text>
          </g>
          <text x="600" y="632" textAnchor="middle" fill="#a5f3fc" fontSize="19" fontWeight="800" paintOrder="stroke" stroke="#09090b" strokeWidth="5">EVERY MIDNIGHT: last 24 h of real readings</text>
        </g>

        {S.a && ['p_inp_unk', 'p_inp_rules'].map((id) => <Pulse key={id} path={id} color={COL.inp} start={S.a[0]} end={S.a[1]} cyc={cyc} n={3} />)}
        {S.b && ['p_unk_lad', 'p_rules_lad'].map((id) => <Pulse key={id} path={id} color={COL.puzzle} start={S.b[0]} end={S.b[1]} cyc={cyc} n={3} />)}
        {S.c && <Pulse path="p_lad_plan" color={COL.lad} start={S.c[0]} end={S.c[1]} cyc={cyc} n={3} />}
        {S.d && <Pulse path="p_plan_act" color={COL.plan} start={S.d[0]} end={S.d[1]} cyc={cyc} n={3} />}
        {S.e && <Pulse path="p_act_meas" color={COL.meas} start={S.e[0]} end={S.e[1]} cyc={cyc} n={3} />}
        {S.f && <Pulse path="p_meas_err" color={COL.meas} start={S.f[0]} end={S.f[1]} cyc={cyc} n={2} />}
        {S.g && <Pulse path="p_err_inp" color="#c084fc" start={S.g[0]} end={S.g[1]} cyc={cyc} n={3} />}
        {S.h && <Pulse path="p_meas_fc" color={COL.fc} start={S.h[0]} end={S.h[1]} cyc={cyc} n={3} />}
        {step === 5 && <Pulse path="p_fc_inp" color={COL.fc} start={7.6} end={8.8} cyc={cyc} n={2} />}
      </svg>
    </div>
  )
}
