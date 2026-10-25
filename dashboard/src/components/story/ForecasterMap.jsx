import { useEffect, useRef, useState } from 'react'
import { F_NODES } from '../../data/forecasterContent.js'

// Mind map of the POLARIS N6 forecaster only. Declarative SVG pulses follow the way data moves
// inside it; each chapter has its own short loop and the other chapters are dimmed.

const COL = { asm: '#fbbf24', base: '#94a3b8', add: '#22d3ee', spe: '#c084fc', mean: '#67e8f9', blend: '#f472b6', mask: '#a1a1aa', unc: '#34d399', out: '#e0f2fe' }

const B = {
  asm: { x: 20, y: 60, w: 250, h: 170 },
  base: { x: 20, y: 310, w: 250, h: 130 },
  add: { x: 340, y: 40, w: 420, h: 250 },
  spe: { x: 340, y: 330, w: 420, h: 190 },
  meanA: { x: 830, y: 105, w: 140, h: 80 },
  meanB: { x: 830, y: 395, w: 140, h: 80 },
  blend: { x: 1040, y: 175, w: 240, h: 230 },
  mask: { x: 1040, y: 445, w: 240, h: 70 },
  spread: { x: 340, y: 590, w: 190, h: 110 },
  bound: { x: 570, y: 590, w: 190, h: 110 },
  reserve: { x: 800, y: 590, w: 190, h: 110 },
  out: { x: 1040, y: 580, w: 240, h: 130 },
}

const P = {
  p_asm_add: 'M270 120 C 305 120, 305 110, 340 110',
  p_asm_spe: 'M270 190 C 310 190, 310 400, 340 400',
  p_base_add: 'M270 350 C 320 350, 300 215, 340 215',
  p_base_spe: 'M270 400 C 300 400, 310 460, 340 460',
  p_add_meanA: 'M760 145 H 830',
  p_spe_meanB: 'M760 435 H 830',
  p_meanA_bl: 'M970 145 C 1005 145, 1005 245, 1040 245',
  p_meanB_bl: 'M970 435 C 1005 435, 1005 335, 1040 335',
  p_bl_mask: 'M1160 405 V 445',
  p_add_spread: 'M760 215 H 795 V 560 H 460 V 590',
  p_spe_spread: 'M435 520 V 590',
  p_spread_bound: 'M530 645 H 570',
  p_bound_res: 'M760 645 H 800',
  p_mask_out: 'M1160 515 V 580',
  p_res_out: 'M990 645 H 1040',
  p_out_opt: 'M1160 710 V 745',
}
const SCHED = {
  0: { cyc: 14, asm: [0, 2.2], blink: 2.4, mean: [4.6, 6.0], blendp: [6.0, 7.4], mask: [7.4, 8.2], unc: [8.4, 10.6], out: [11, 12.6], opt: [12.6, 13.8] },
  1: { cyc: 5, asm: [0.3, 3.2] },
  2: { cyc: 6, blink: 0.2 },
  3: { cyc: 6, mean: [0.2, 1.8], blendp: [2.0, 3.6], mask: [3.8, 4.8] },
  4: { cyc: 6, unc: [0.2, 3.8] },
  5: { cyc: 5, out: [0.2, 2.0], opt: [2.0, 4.0] },
}
const OWN = { asm: 1, base: 1, add: 2, spe: 2, meanA: 3, meanB: 3, blend: 3, mask: 3, spread: 4, bound: 4, reserve: 4, out: 5 }

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
        <animateMotion dur={`${cyc}s`} repeatCount="indefinite" calcMode="linear" keyPoints={a > 0 ? '0;0;1;1' : '0;1;1'} keyTimes={a > 0 ? `0;${a};${b};1` : `0;${b};1`}>
          <mpath href={`#${path}`} />
        </animateMotion>
        <animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" calcMode="discrete" values={a > 0 ? '0;1;0' : '1;0'} keyTimes={a > 0 ? `0;${a};${b}` : `0;${b}`} />
      </circle>
    )
  })
}

function Glow({ x, y, w, h, color, start, end, cyc, peak = 0.22 }) {
  const fr = mkFr(cyc)
  const a = fr(start)
  const b = fr(end)
  return (
    <rect x={x} y={y} width={w} height={h} rx="18" fill={color} opacity="0" pointerEvents="none">
      <animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" calcMode="discrete" values={a > 0 ? `0;${peak};0` : `${peak};0`} keyTimes={a > 0 ? `0;${a};${b}` : `0;${b}`} />
    </rect>
  )
}

function Dot({ cx, cy, color, start, cyc, onClick, selected, title }) {
  const fr = mkFr(cyc)
  const a = fr(start)
  const b = fr(start + 0.7)
  return (
    <g onClick={onClick} style={{ cursor: 'pointer' }}>
      <circle cx={cx} cy={cy} r="11" fill={color} opacity="0.55" stroke={selected ? '#fff' : 'none'} strokeWidth="3">
        <title>{title}</title>
        {start != null && <animate attributeName="opacity" dur={`${cyc}s`} repeatCount="indefinite" calcMode="discrete" values={a > 0 ? '0.55;1;0.55' : '1;0.55'} keyTimes={a > 0 ? `0;${a};${b}` : `0;${b}`} />}
      </circle>
    </g>
  )
}

export default function ForecasterMap({ step, selected, onSelect, dotSel, onDot }) {
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
  const sel = (id) => selected === id

  const box = (id, color, children, extra = {}) => {
    const b = B[id]
    return (
      <g key={id} style={{ ...dim(id), cursor: 'pointer' }} onClick={click(id)}>
        <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="18" fill={extra.fill ?? '#0f1014'} stroke={color} strokeWidth={sel(id) ? 5 : 2.6} strokeDasharray={extra.dash} />
        {children}
      </g>
    )
  }
  const txt = (id, dy, text, size, fill, weight = 700, dx = null) => {
    const b = B[id]
    return <text x={b.x + (dx ?? b.w / 2)} y={b.y + dy} textAnchor={dx == null ? 'middle' : 'start'} fill={fill} fontSize={size} fontWeight={weight}>{text}</text>
  }

  const addDots = Array.from({ length: 25 }, (_, i) => ({ i, x: B.add.x + 60 + (i % 5) * 75, y: B.add.y + 100 + Math.floor(i / 5) * 32 }))
  const speDots = Array.from({ length: 15 }, (_, i) => ({ i, x: B.spe.x + 60 + (i % 5) * 75, y: B.spe.y + 105 + Math.floor(i / 5) * 32 }))
  const edge = (id, color, w = 4, dash) => <path id={id} d={P[id]} fill="none" stroke={color} strokeWidth={w} strokeOpacity="0.5" strokeDasharray={dash} markerEnd="url(#farr)" />
  const eg = (k, children) => <g style={dim(k)}>{children}</g>

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-3">
        <button onClick={() => setPlaying((p) => !p)} className={`flex h-11 min-w-[170px] items-center justify-center rounded-lg border-2 px-4 text-[18px] font-bold ${playing ? 'border-amber-500 bg-amber-950 text-amber-300' : 'border-emerald-500 bg-emerald-950 text-emerald-300'}`}>{playing ? '❚❚  Pause motion' : '▶  Play motion'}</button>
        <span className="text-[16px] font-semibold text-zinc-300">Click a box, or any dot, to read about it.</span>
      </div>

      <svg key={step} ref={svgRef} viewBox="0 0 1300 770" className="h-auto w-full rounded-lg" role="img" aria-label="Inside the POLARIS N6 forecaster" style={{ background: '#080b10', backgroundImage: 'radial-gradient(rgba(255,255,255,0.07) 1px, transparent 1px)', backgroundSize: '24px 24px' }}>
        <defs>
          <marker id="farr" viewBox="0 0 10 10" refX="8" refY="5" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#d4d4d8" /></marker>
        </defs>

        {/* edges, grouped by the chapter they belong to */}
        {eg('asm', <>{edge('p_asm_add', COL.asm, 7)}{edge('p_asm_spe', COL.asm, 7)}{edge('p_base_add', COL.base, 5)}{edge('p_base_spe', COL.base, 5)}</>)}
        {eg('meanA', <>{edge('p_add_meanA', COL.add, 6)}{edge('p_spe_meanB', COL.spe, 6)}{edge('p_meanA_bl', COL.mean, 6)}{edge('p_meanB_bl', COL.spe, 6)}{edge('p_bl_mask', COL.blend, 6)}</>)}
        {eg('spread', <>{edge('p_add_spread', COL.unc, 3, '8 7')}{edge('p_spe_spread', COL.unc, 3, '8 7')}{edge('p_spread_bound', COL.unc, 5)}{edge('p_bound_res', COL.unc, 5)}</>)}
        {eg('out', <>{edge('p_mask_out', COL.out, 7)}{edge('p_res_out', COL.unc, 5)}{edge('p_out_opt', COL.out, 7)}</>)}

        {/* inputs ready */}
        {box('asm', COL.asm, (
          <>
            {txt('asm', 40, 'Feature assembler', 23, '#fff', 800)}
            {txt('asm', 68, 'builds the clue table', 17, '#fcd34d', 600)}
            {[...Array(6)].map((_, r) => [...Array(9)].map((__, c) => <rect key={`${r}-${c}`} x={B.asm.x + 28 + c * 22} y={B.asm.y + 84 + r * 12} width="18" height="9" rx="2" fill={COL.asm} opacity={0.25 + ((r * 3 + c) % 5) * 0.12} />))}
            {txt('asm', 164, '24 hours × 36 clues', 16, '#e4e4e7', 600)}
            {S.asm && <Glow {...B.asm} color={COL.asm} start={S.asm[0]} end={S.asm[1]} cyc={cyc} />}
          </>
        ))}
        {box('base', COL.base, (
          <>
            {txt('base', 42, 'Baseline forecast', 22, '#fff', 800)}
            {txt('base', 72, 'physics + Chronos-2', 18, '#cbd5e1', 600)}
            {txt('base', 102, 'the first guess to correct', 16, '#94a3b8', 600)}
            {S.asm && <Glow {...B.base} color={COL.base} start={S.asm[0]} end={S.asm[1]} cyc={cyc} />}
          </>
        ))}

        {/* the 40 models */}
        {box('add', COL.add, (
          <>
            {txt('add', 40, '25 additive models', 25, '#fff', 800)}
            {txt('add', 68, 'each corrects the baseline in W/m²', 17, '#67e8f9', 600)}
            {addDots.map((d) => <Dot key={d.i} cx={d.x} cy={d.y} color={COL.add} start={S.blink != null ? S.blink + d.i * 0.05 : null} cyc={cyc} selected={dotSel?.kind === 'add' && dotSel.i === d.i} onClick={(e) => { e.stopPropagation(); onDot('add', d.i) }} title={`Additive model #${d.i + 1}`} />)}
          </>
        ))}
        {box('spe', COL.spe, (
          <>
            {txt('spe', 40, '15 clearness-ratio specialists', 24, '#fff', 800)}
            {txt('spe', 68, 'each corrects it as a share of clear-sky light', 17, '#e9d5ff', 600)}
            {speDots.map((d) => <Dot key={d.i} cx={d.x} cy={d.y} color={COL.spe} start={S.blink != null ? S.blink + 1.4 + d.i * 0.05 : null} cyc={cyc} selected={dotSel?.kind === 'spe' && dotSel.i === d.i} onClick={(e) => { e.stopPropagation(); onDot('spe', d.i) }} title={`Specialist #${d.i + 1}`} />)}
          </>
        ), { })}

        {/* average and blend */}
        {box('meanA', COL.mean, <>{txt('meanA', 36, 'Average', 21, '#fff', 800)}{txt('meanA', 62, 'of the 25', 18, '#67e8f9', 600)}</>)}
        {box('meanB', COL.spe, <>{txt('meanB', 36, 'Average', 21, '#fff', 800)}{txt('meanB', 62, 'of the 15', 18, '#e9d5ff', 600)}</>)}
        {box('blend', COL.blend, (
          <>
            {txt('blend', 38, 'Blender', 25, '#fff', 800)}
            {txt('blend', 64, 'sun height sets the trust', 17, '#fbcfe8', 600)}
            {/* mini ramp: weight of the specialists against sun height */}
            <g transform={`translate(${B.blend.x + 28} ${B.blend.y + 88})`}>
              <line x1="0" y1="100" x2="184" y2="100" stroke="#71717a" strokeWidth="2" />
              <line x1="0" y1="0" x2="0" y2="100" stroke="#71717a" strokeWidth="2" />
              <polyline points="0,100 61,100 112,28 184,28" fill="none" stroke="#f472b6" strokeWidth="4" strokeLinejoin="round" />
              <text x="61" y="122" textAnchor="middle" fill="#d4d4d8" fontSize="14" fontWeight="700">22°</text>
              <text x="112" y="122" textAnchor="middle" fill="#d4d4d8" fontSize="14" fontWeight="700">32°</text>
              <text x="188" y="24" textAnchor="end" fill="#fbcfe8" fontSize="14" fontWeight="700">0.55</text>
            </g>
            {S.blendp && <Glow {...B.blend} color={COL.blend} start={S.blendp[0]} end={S.blendp[1]} cyc={cyc} />}
          </>
        ))}
        {box('mask', COL.mask, <>{txt('mask', 32, 'Night rule', 21, '#fff', 800)}{txt('mask', 56, 'sun below horizon → 0', 16, '#d4d4d8', 600)}</>)}

        {/* uncertainty and reserve */}
        {box('spread', COL.unc, <>{txt('spread', 38, 'Disagreement', 20, '#fff', 800)}{txt('spread', 62, 'of the 40 models', 17, '#6ee7b7', 600)}{txt('spread', 88, '= how unsure', 16, '#a7f3d0', 600)}</>, { dash: '8 6' })}
        {box('bound', COL.unc, <>{txt('bound', 38, '90% bound', 21, '#fff', 800)}{txt('bound', 62, 'pessimistic forecast', 16, '#6ee7b7', 600)}{txt('bound', 88, '× 1.859', 16, '#a7f3d0', 600)}</>, { dash: '8 6' })}
        {box('reserve', COL.unc, <>{txt('reserve', 38, 'Battery reserve', 21, '#fff', 800)}{txt('reserve', 62, 'never below 15 kWh', 16, '#6ee7b7', 600)}{txt('reserve', 88, 'next 6 hours', 16, '#a7f3d0', 600)}</>, { dash: '8 6' })}

        {/* output */}
        {box('out', COL.out, (
          <>
            {txt('out', 40, '24 h solar forecast', 22, '#fff', 800)}
            {txt('out', 68, '+ battery reserve', 20, '#bae6fd', 700)}
            {txt('out', 100, 'made once a day, 00:00 UTC', 15, '#cbd5e1', 600)}
            {S.out && <Glow {...B.out} color={COL.out} start={S.out[0]} end={S.out[1]} cyc={cyc} />}
          </>
        ))}
        <text x="1160" y="765" textAnchor="middle" fill="#e0f2fe" fontSize="19" fontWeight="800" style={dim('out')}>→ to the optimizer</text>

        {/* travelling light */}
        {S.asm && ['p_asm_add', 'p_asm_spe'].map((id) => <Pulse key={id} path={id} color={COL.asm} start={S.asm[0]} end={S.asm[1]} cyc={cyc} n={3} />)}
        {S.asm && ['p_base_add', 'p_base_spe'].map((id) => <Pulse key={id} path={id} color="#cbd5e1" start={S.asm[0] + 0.2} end={S.asm[1]} cyc={cyc} n={2} />)}
        {S.mean && (
          <>
            <Pulse path="p_add_meanA" color={COL.add} start={S.mean[0]} end={S.mean[1]} cyc={cyc} n={3} />
            <Pulse path="p_spe_meanB" color={COL.spe} start={S.mean[0]} end={S.mean[1]} cyc={cyc} n={3} />
          </>
        )}
        {S.blendp && (
          <>
            <Pulse path="p_meanA_bl" color={COL.mean} start={S.blendp[0]} end={S.blendp[1]} cyc={cyc} />
            <Pulse path="p_meanB_bl" color={COL.spe} start={S.blendp[0]} end={S.blendp[1]} cyc={cyc} />
          </>
        )}
        {S.mask && <Pulse path="p_bl_mask" color={COL.blend} start={S.mask[0]} end={S.mask[1]} cyc={cyc} />}
        {S.unc && (
          <>
            <Pulse path="p_add_spread" color={COL.unc} start={S.unc[0]} end={S.unc[0] + 1.6} cyc={cyc} r={7} />
            <Pulse path="p_spe_spread" color={COL.unc} start={S.unc[0]} end={S.unc[0] + 1.2} cyc={cyc} r={7} />
            <Pulse path="p_spread_bound" color={COL.unc} start={S.unc[0] + 1.6} end={S.unc[0] + 2.4} cyc={cyc} />
            <Pulse path="p_bound_res" color={COL.unc} start={S.unc[0] + 2.4} end={S.unc[1]} cyc={cyc} />
          </>
        )}
        {S.out && (
          <>
            <Pulse path="p_mask_out" color={COL.out} start={S.out[0]} end={S.out[1]} cyc={cyc} />
            <Pulse path="p_res_out" color={COL.unc} start={S.out[0] + 0.2} end={S.out[1]} cyc={cyc} />
          </>
        )}
        {S.opt && <Pulse path="p_out_opt" color={COL.out} start={S.opt[0]} end={S.opt[1]} cyc={cyc} n={3} />}
      </svg>
    </div>
  )
}
