import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { windKw, SIM } from '../../data/useReplay.js'

const SPEEDS = [
  { id: 'hour', label: '1 hour / sec', hps: 1 },
  { id: 'slow', label: '6 hours / sec', hps: 6 },
  { id: 'normal', label: '1 day / sec', hps: 24 },
  { id: 'fast', label: '1 week / sec', hps: 168 },
]
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const pad = (n) => String(n).padStart(2, '0')

function PixelBar({ frac, color, cells = 14 }) {
  const on = Math.max(0, Math.min(cells, Math.round(frac * cells)))
  return (
    <div className="flex w-full gap-[3px]" aria-hidden>
      {Array.from({ length: cells }, (_, i) => {
        const lit = i < on
        const c = typeof color === 'function' ? color(i / cells) : color
        return <span key={i} className="px-cell h-5 flex-1 rounded-[3px]" style={{ background: lit ? c : '#27272a', boxShadow: lit ? `0 0 6px ${c}66` : 'none' }} />
      })}
    </div>
  )
}

const greens = (t) => (t < 0.5 ? '#22c55e' : t < 0.8 ? '#4ade80' : '#bef264')

function Tag({ real }) {
  return (
    <span className={`rounded px-2 py-0.5 text-[13px] font-bold tracking-wide ${real ? 'bg-emerald-900/70 text-emerald-300' : 'bg-sky-900/70 text-sky-300'}`}>
      {real ? 'REAL DATA' : 'SIMULATED'}
    </span>
  )
}

function Meter({ icon, label, value, unit, frac, color, real, note }) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-scada-border bg-scada-panel2 p-4">
      <div className="flex items-center gap-3">
        <div className="h-14 w-14 shrink-0">{icon}</div>
        <div className="min-w-0">
          <div className="text-[18px] font-bold text-zinc-100">{label}</div>
          <Tag real={real} />
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="tnum text-[36px] font-bold leading-none text-white">{value}</span>
        <span className="text-[18px] font-semibold text-zinc-300">{unit}</span>
      </div>
      <PixelBar frac={frac} color={color} />
      <div className="min-h-[22px] text-[16px] font-semibold text-zinc-300">{note}</div>
    </div>
  )
}

const stroke = { fill: 'none', strokeWidth: 2.4, strokeLinecap: 'round', strokeLinejoin: 'round' }

function TurbineIcon({ windKwNow }) {
  const dur = Math.max(0.7, 5 - windKwNow * 0.17)
  return (
    <svg viewBox="0 0 56 56" className="h-full w-full">
      <line x1="28" y1="30" x2="28" y2="54" stroke="#cbd5e1" {...stroke} />
      <g style={{ transformOrigin: '28px 28px', animation: `spin-blades ${dur}s linear infinite` }} stroke="#e2e8f0" {...stroke}>
        <line x1="28" y1="28" x2="28" y2="5" /><line x1="28" y1="28" x2="48" y2="40" /><line x1="28" y1="28" x2="8" y2="40" />
      </g>
      <circle cx="28" cy="28" r="3.2" fill="#e2e8f0" />
    </svg>
  )
}
const SolarIcon = ({ bright }) => (
  <svg viewBox="0 0 56 56" className="h-full w-full">
    <g stroke="#fde047" {...stroke} opacity={0.25 + bright * 0.75}>
      <circle cx="40" cy="14" r="6" fill="#fde047" />
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => { const a = (i * Math.PI) / 4; return <line key={i} x1={40 + Math.cos(a) * 9} y1={14 + Math.sin(a) * 9} x2={40 + Math.cos(a) * 12.5} y2={14 + Math.sin(a) * 12.5} /> })}
    </g>
    <path d="M6 48 L14 26 H44 L50 48 Z" fill="#0c4a6e" stroke="#7dd3fc" {...stroke} />
    <path d="M21 26 L19 48 M34 26 L33 48 M9 37 H48" stroke="#7dd3fc" strokeWidth="1.6" />
  </svg>
)
const BatteryIcon = ({ soc, color }) => (
  <svg viewBox="0 0 56 56" className="h-full w-full">
    <rect x="6" y="17" width="40" height="24" rx="4" stroke={color} {...stroke} />
    <rect x="46" y="24" width="5" height="10" rx="1.5" fill={color} />
    <rect x="10" y="21" width={32 * (soc / 100)} height="16" rx="2" fill={color} className="px-cell" />
  </svg>
)
const DieselIcon = ({ on }) => (
  <svg viewBox="0 0 56 56" className="h-full w-full">
    <rect x="6" y="20" width="44" height="28" rx="4" stroke={on ? '#fb923c' : '#71717a'} {...stroke} />
    <path d="M30 26 L22 38 H29 L26 46 L36 32 H29 Z" fill={on ? '#fb923c' : 'none'} stroke={on ? '#fb923c' : '#71717a'} strokeWidth="2" />
    <path d="M14 20 V12 H22 V20" stroke={on ? '#fb923c' : '#71717a'} {...stroke} />
    {on && <g className="flow-anim" style={{ opacity: 0.7 }}><circle cx="18" cy="8" r="2.5" fill="#a1a1aa" /><circle cx="24" cy="4" r="2" fill="#a1a1aa" /></g>}
  </svg>
)
const HouseIcon = () => (
  <svg viewBox="0 0 56 56" className="h-full w-full" stroke="#e4e4e7" {...stroke}>
    <path d="M6 28 L28 8 L50 28" /><path d="M12 25 V48 H44 V25" /><rect x="23" y="34" width="10" height="14" fill="#e4e4e7" opacity="0.3" />
  </svg>
)

function Thermometer({ temp }) {
  const t = Math.max(-30, Math.min(25, temp))
  const frac = (t + 30) / 55
  const col = temp <= -10 ? '#60a5fa' : temp <= 0 ? '#93c5fd' : temp <= 10 ? '#fcd34d' : '#fb923c'
  return (
    <svg viewBox="0 0 56 56" className="h-full w-full">
      <rect x="22" y="5" width="12" height="36" rx="6" stroke="#cbd5e1" {...stroke} />
      <circle cx="28" cy="46" r="8" fill={col} stroke="#cbd5e1" strokeWidth="2.4" />
      <rect x="25.5" y={8 + 32 * (1 - frac)} width="5" height={34 - 32 * (1 - frac)} rx="2.5" fill={col} className="px-cell" />
    </svg>
  )
}

// Replays the whole simulated year. `onRow` lets the page share the current hour with other graphics.
export default function LiveStation({ series, weather, onRow }) {
  const total = series?.length ?? 0
  const [idx, setIdx] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState('hour')
  const pos = useRef(0)
  const last = useRef(null)
  const raf = useRef(null)

  const hps = SPEEDS.find((s) => s.id === speed).hps

  const tick = useCallback((t) => {
    if (last.current == null) last.current = t
    const dt = (t - last.current) / 1000
    last.current = t
    pos.current += dt * hps
    if (pos.current >= total - 1) {
      pos.current = total - 1
      setIdx(total - 1)
      setPlaying(false)
      return
    }
    setIdx(Math.floor(pos.current))
    raf.current = requestAnimationFrame(tick)
  }, [hps, total])

  useEffect(() => {
    if (!playing) { last.current = null; return }
    raf.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf.current)
  }, [playing, tick])

  // First hour of each month in the run, plus how sunny that month is (average solar kW), so a
  // sunny month can be picked directly.
  const months = useMemo(() => {
    if (!series) return []
    const out = []
    const seen = new Map()
    for (let i = 0; i < series.length; i++) {
      const m = new Date(series[i].timestamp).getUTCMonth()
      let e = seen.get(m)
      if (!e) { e = { m, start: i, n: 0, sun: 0 }; seen.set(m, e); out.push(e) }
      e.n++
      e.sun += Math.min(Math.max(0, series[i].actual_ghi) * SIM.kPv, SIM.pvCapKw)
    }
    return out.map((e) => ({ ...e, avg: e.sun / e.n }))
  }, [series])

  // Start on a lively spring morning (sun and diesel both in play) instead of the dark first hour of the run.
  const started = useRef(false)
  useEffect(() => {
    if (started.current || !series || series.length < 2000) return
    const i = series.findIndex((r) => { const d = new Date(r.timestamp); return d.getUTCMonth() === 3 && d.getUTCDate() === 12 && d.getUTCHours() === 7 })
    if (i >= 0) { started.current = true; pos.current = i; setIdx(i) }
  }, [series])

  const row = series?.[Math.min(idx, total - 1)]
  useEffect(() => { if (row) onRow?.(row, idx) }, [row, idx, onRow])

  if (!row) {
    return <div className="rounded-lg border border-scada-border bg-scada-panel p-8 text-center text-[18px] text-zinc-300">Loading the station…</div>
  }

  const d = new Date(row.timestamp)
  const wind = windKw(row.timestamp)
  const solar = Math.min(Math.max(0, row.actual_ghi) * SIM.kPv, SIM.pvCapKw)
  const soc = row.battery_soc_pct
  const net = row.battery_net_kw ?? 0
  const diesel = row.diesel_kw
  const load = (row.demand_w ?? 0) / 1000
  const wi = weather ? Math.min(idx, weather.ta.length - 1) : null
  const temp = wi != null ? weather.ta[wi] : null
  const socColor = soc < 30 ? '#f87171' : soc < 50 ? '#fbbf24' : '#34d399'
  const batNote = net > 0.5 ? `▲ charging  +${net.toFixed(1)} kW` : net < -0.5 ? `▼ supplying  ${Math.abs(net).toFixed(1)} kW` : '■ idle'

  const seek = (v) => { pos.current = v; setIdx(v) }
  const sunLabel = (avg) => (avg > 8 ? '☀☀☀ very sunny' : avg > 3 ? '☀☀ sunny' : avg > 0.7 ? '☀ some sun' : 'dark')
  const FULL = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  const lastMonth = months.length ? months[months.length - 1].m : -1

  return (
    <div className="rounded-lg border border-scada-border bg-scada-panel p-5">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
        <button
          onClick={() => { if (idx >= total - 1) seek(0); setPlaying((p) => !p) }}
          className={`flex h-14 min-w-[150px] items-center justify-center gap-2 rounded-lg border-2 px-5 text-[20px] font-bold ${playing ? 'border-amber-500 bg-amber-950 text-amber-300' : 'border-emerald-500 bg-emerald-950 text-emerald-300'}`}
        >
          {playing ? '❚❚  Pause' : '▶  Play'}
        </button>
        <div>
          <div className="tnum text-[32px] font-bold leading-none text-white">
            {DAYS[d.getUTCDay()]} {d.getUTCDate()} {MONTHS[d.getUTCMonth()]} {d.getUTCFullYear()}
          </div>
          <div className="tnum mt-1 text-[22px] font-semibold text-cyan-300">{pad(d.getUTCHours())}:00 <span className="text-[16px] text-zinc-400">UTC · real calendar</span></div>
        </div>
        <div className="ml-auto flex flex-wrap items-center gap-2">
          <select
            value={months.find((e) => e.m === d.getUTCMonth())?.m ?? ''}
            onChange={(e) => { const mo = months.find((x) => x.m === Number(e.target.value)); if (mo) seek(mo.start) }}
            className="rounded-lg border border-scada-border bg-scada-panel2 px-3 py-2 text-[17px] font-semibold text-white"
            aria-label="Jump to month"
          >
            {months.map((e) => <option key={e.m} value={e.m}>{FULL[e.m]} — {sunLabel(e.avg)}</option>)}
            {lastMonth < 11 && <option disabled>(later months still computing)</option>}
          </select>
          {SPEEDS.map((s) => (
            <button
              key={s.id}
              onClick={() => setSpeed(s.id)}
              className={`rounded-lg border px-3 py-2 text-[16px] font-semibold ${speed === s.id ? 'border-zinc-200 bg-zinc-700 text-white' : 'border-scada-border text-zinc-300 hover:text-white'}`}
            >{s.label}</button>
          ))}
        </div>
      </div>

      <input
        type="range" min={0} max={total - 1} value={idx}
        onChange={(e) => { setPlaying(false); seek(Number(e.target.value)) }}
        className="my-4 h-2 w-full cursor-pointer accent-cyan-400"
        aria-label="Position in the year"
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <Meter icon={<TurbineIcon windKwNow={wind} />} label="Wind" real={false} value={wind.toFixed(1)} unit="kW" frac={wind / 25} color={greens} note={wind > 18 ? 'Strong' : wind > 10 ? 'Moderate' : 'Light'} />
        <Meter icon={<SolarIcon bright={Math.min(1, solar / 40)} />} label="Solar" real value={solar.toFixed(1)} unit="kW" frac={solar / 50} color={greens} note={solar < 0.2 ? (d.getUTCMonth() < 2 || d.getUTCMonth() > 9 ? 'Polar night — no sun' : 'No sun right now') : `${Math.round(row.actual_ghi)} W/m² of real sunshine`} />
        <Meter icon={<BatteryIcon soc={soc} color={socColor} />} label="Battery" real={false} value={soc.toFixed(0)} unit="%" frac={soc / 100} color={() => socColor} note={batNote} />
        <Meter icon={<DieselIcon on={diesel > 0} />} label="Diesel generator" real={false} value={diesel > 0 ? diesel.toFixed(0) : 'OFF'} unit={diesel > 0 ? 'kW' : ''} frac={diesel / 100} color={() => '#fb923c'} note={diesel > 0 ? 'Running' : 'Resting'} />
        <Meter icon={<HouseIcon />} label="Station demand" real={false} value={load.toFixed(1)} unit="kW" frac={load / 45} color={() => '#a5b4fc'} note="Lights and equipment" />

        <div className="flex flex-col gap-3 rounded-lg border border-scada-border bg-scada-panel2 p-4">
          <div className="flex items-center gap-3">
            <div className="h-14 w-14 shrink-0"><Thermometer temp={temp ?? 0} /></div>
            <div>
              <div className="text-[18px] font-bold text-zinc-100">Outside weather</div>
              <Tag real />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="tnum text-[36px] font-bold leading-none text-white">{temp != null ? temp.toFixed(1) : '—'}</span>
            <span className="text-[18px] font-semibold text-zinc-300">°C</span>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-1 text-[18px] font-semibold text-zinc-200">
            <span>❄ Snow <b className="tnum text-white">{wi != null ? weather.snow[wi] : '—'} cm</b></span>
            <span>💧 Humidity <b className="tnum text-white">{wi != null ? weather.rh[wi] : '—'}%</b></span>
          </div>
        </div>
      </div>
    </div>
  )
}
