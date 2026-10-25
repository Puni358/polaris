import { useEffect, useState } from 'react'

const CHECKS = [
  'Every input is stamped before 00:00 (the forecast time)',
  'Weather run 18:00 was published at 20:15, before it is used',
  'No input contains the real outcome (fail closed)',
]
const FAM_COLORS = ['#fbbf24', '#34d399', '#a78bfa', '#22d3ee', '#f472b6']

// "Visual firewall": past data streams through the 00:00 wall, future values bounce off it, the three audit
// checks tick off one by one, and only then does the AUDIT PASS badge unlock the data flow.
export default function FirewallStage({ onPass }) {
  const [ticks, setTicks] = useState(0) // 0..3 checks ticked
  const pass = ticks >= CHECKS.length + 0

  useEffect(() => {
    setTicks(0)
    const timers = []
    for (let i = 1; i <= CHECKS.length; i++) timers.push(setTimeout(() => setTicks(i), 1600 + i * 750))
    timers.push(setTimeout(() => onPass?.(), 1600 + CHECKS.length * 750 + 500))
    return () => timers.forEach(clearTimeout)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="rounded-lg border border-scada-border bg-scada-panel p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-[22px] font-bold text-white">Visual firewall: nothing from the future</h3>
        <span className={`rounded-lg border-2 px-4 py-1.5 text-[19px] font-extrabold tracking-wide ${pass ? 'border-emerald-400 bg-emerald-950 text-emerald-300' : 'border-amber-500 bg-amber-950 text-amber-300'}`} style={pass ? { animation: 'glow-emerald 1.6s ease-in-out infinite' } : undefined}>
          {pass ? '✔ AUDIT PASS' : 'AUDIT RUNNING…'}
        </span>
      </div>

      {/* timeline with the wall */}
      <div className="relative mb-2 h-36 overflow-hidden rounded-md bg-scada-bg">
        <div className="absolute left-[2%] right-[2%] top-[58px] h-1.5 rounded bg-zinc-700" />
        {['18:00|2', '20:15|36', '00:00|74'].map((m) => {
          const [t, x] = m.split('|')
          return (
            <div key={t} className="absolute top-3 -translate-x-1/2 text-center" style={{ left: `${x}%` }}>
              <div className="tnum text-[19px] font-bold text-white">{t}</div>
              <div className="mx-auto mt-1 h-5 w-1 rounded" style={{ background: t === '00:00' ? '#22d3ee' : '#fbbf24' }} />
            </div>
          )
        })}
        <div className="absolute top-24 text-[16px] font-semibold text-amber-200" style={{ left: '2%' }}>weather-model run</div>
        <div className="absolute top-24 text-[16px] font-semibold text-amber-200" style={{ left: '30%' }}>published</div>
        <div className="absolute top-24 text-[16px] font-bold text-cyan-200" style={{ left: '68%' }}>forecast made</div>

        {/* the wall */}
        <div className="absolute bottom-0 top-0 w-3 rounded bg-rose-500/80" style={{ left: '75%', boxShadow: '0 0 16px #f43f5e' }} />
        <div className="absolute right-[2%] top-1.5 w-[22%] text-right text-[15px] font-bold text-rose-300">FIREWALL<br /><span className="font-semibold text-rose-200">future is blocked</span></div>

        {/* past telemetry passes */}
        {FAM_COLORS.flatMap((c, k) => [0, 1].map((n) => (
          <span key={`${k}-${n}`} className="absolute h-3.5 w-3.5 rounded-full" style={{ top: 52 + (k % 3) * 8, background: c, boxShadow: `0 0 8px ${c}`, animation: `fw-pass 3.2s linear ${(k * 2 + n) * 0.32}s infinite` }} />
        )))}
        {/* future values bounce */}
        {[0, 1, 2].map((n) => (
          <span key={`f${n}`} className="absolute h-3.5 w-3.5 rounded-full bg-rose-500" style={{ top: 64 + n * 7, boxShadow: '0 0 8px #f43f5e', animation: `fw-bounce 2.4s ease-in-out ${n * 0.5}s infinite` }} />
        ))}
      </div>

      <ul className="flex flex-col gap-1.5">
        {CHECKS.map((c, i) => (
          <li key={c} className={`flex items-center gap-3 text-[19px] font-semibold transition-colors ${ticks > i ? 'text-emerald-300' : 'text-zinc-500'}`}>
            <span className={`flex h-7 w-7 items-center justify-center rounded-full border-2 text-[16px] font-bold ${ticks > i ? 'border-emerald-400 bg-emerald-950' : 'border-zinc-600'}`}>{ticks > i ? '✓' : ''}</span>
            {c}
          </li>
        ))}
      </ul>
    </div>
  )
}
