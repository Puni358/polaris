import { useMemo, useState } from 'react'

// Kid-simple year view: one square per DAY (like a contribution calendar), coloured by the
// most important thing the model's decisions did that day. Clicking a day opens its 24 hours.

export const OUTCOME = {
  protect: { label: 'Protected load or reserve', color: '#34d399' },
  saved: { label: 'Saved fuel', color: '#f59e0b' },
  same: { label: 'Either choice was fine', color: '#52525b' },
  better: { label: 'Could do better', color: '#a78bfa' },
}
export const OUTCOME_ORDER = ['protect', 'saved', 'same', 'better']

export const hourOutcome = (kind) =>
  kind === 'critical' || kind === 'reserve' ? 'protect' : kind === 'costly' ? 'saved' : kind === 'better' ? 'better' : 'same'

const DAY_MS = 86_400_000
const CELL = 22
const GAP = 3
const TOP = 22
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const DOW = ['Mon', '', 'Wed', '', 'Fri', '', 'Sun']
const pad = (n) => String(n).padStart(2, '0')

export function dayOutcome(hours) {
  const kinds = hours.filter(Boolean).map((h) => hourOutcome(h.kind))
  if (kinds.includes('protect')) return 'protect'
  if (kinds.includes('better')) return 'better'
  if (kinds.includes('saved')) return 'saved'
  return kinds.length ? 'same' : null
}

export default function CalendarMap({ days, startMs, totalDays, selected, onSelect, featured }) {
  const [tip, setTip] = useState(null)
  const startDow = (new Date(startMs).getUTCDay() + 6) % 7 // Monday = 0
  const cols = Math.ceil((totalDays + startDow) / 7)
  const W = 34 + cols * (CELL + GAP)
  const H = TOP + 7 * (CELL + GAP)

  const monthTicks = useMemo(() => {
    const out = []
    let last = -1
    for (let d = 0; d < totalDays; d++) {
      const dt = new Date(startMs + d * DAY_MS)
      if (dt.getUTCMonth() !== last) {
        last = dt.getUTCMonth()
        out.push({ col: Math.floor((d + startDow) / 7), label: MONTHS[last] })
      }
    }
    return out
  }, [startMs, totalDays, startDow])

  return (
    <div className="relative w-full">
      <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full" onMouseLeave={() => setTip(null)}>
        {monthTicks.map((m) => (
          <text key={m.label + m.col} x={34 + m.col * (CELL + GAP)} y={12} fill="#a1a1aa" fontSize="11">{m.label}</text>
        ))}
        {DOW.map((l, i) => l && (
          <text key={l} x={0} y={TOP + i * (CELL + GAP) + CELL * 0.7} fill="#71717a" fontSize="10">{l}</text>
        ))}
        {Array.from({ length: totalDays }, (_, d) => {
          const col = Math.floor((d + startDow) / 7)
          const row = (d + startDow) % 7
          const info = days.get(d)
          const out = info ? info.outcome : null
          const x = 34 + col * (CELL + GAP)
          const y = TOP + row * (CELL + GAP)
          const isSel = selected === d
          return (
            <g key={d}>
            <rect
              x={x} y={y} width={CELL} height={CELL} rx="5"
              fill={out ? OUTCOME[out].color : '#17171a'}
              fillOpacity={out === 'same' ? 0.55 : 1}
              stroke={isSel ? '#fafafa' : 'none'} strokeWidth="2.5"
              style={{ cursor: info ? 'pointer' : 'default' }}
              onMouseEnter={() => info && setTip({ d, x: x + CELL / 2, y })}
              onClick={() => info && onSelect(d)}
            />
            {featured?.has(d) && (
              <g pointerEvents="none">
                <rect x={x - 2} y={y - 2} width={CELL + 4} height={CELL + 4} rx="7" fill="none" stroke="#fbbf24" strokeWidth="3" />
                <text x={x + CELL / 2} y={y + CELL * 0.74} textAnchor="middle" fill="#09090b" fontSize="17" fontWeight="900">★</text>
              </g>
            )}
            </g>
          )
        })}
      </svg>
      {tip && days.get(tip.d) && (
        <div
          className="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full rounded-md border border-scada-border bg-scada-bg px-3 py-2 text-[17px] shadow-xl"
          style={{ left: `${(tip.x / W) * 100}%`, top: `${(tip.y / H) * 100 - 2}%` }}
        >
          <div className="tnum text-zinc-400">{new Date(startMs + tip.d * DAY_MS).toUTCString().slice(0, 11)}</div>
          <div className="font-medium" style={{ color: OUTCOME[days.get(tip.d).outcome].color }}>{OUTCOME[days.get(tip.d).outcome].label}</div>
          {days.get(tip.d).protectHours.length > 0 && (
            <div className="text-zinc-300">at {days.get(tip.d).protectHours.map((h) => `${pad(h)}:00`).join(', ')}</div>
          )}
        </div>
      )}
    </div>
  )
}

// 24 blocks for the selected day.
export function DayStrip({ info, dayLabel, onPickHour }) {
  if (!info) return null
  return (
    <div>
      <div className="mb-2 flex items-baseline justify-between">
        <span className="text-[18px] font-medium text-zinc-200">{dayLabel}</span>
        <span className="text-[16px] text-zinc-300">24 hours · click one to open it in the Decision Inspector</span>
      </div>
      <div className="grid grid-cols-12 gap-1.5 sm:grid-cols-24" style={{ gridTemplateColumns: 'repeat(24, minmax(0, 1fr))' }}>
        {Array.from({ length: 24 }, (_, h) => {
          const it = info.hours[h]
          const out = it ? hourOutcome(it.kind) : null
          return (
            <button
              key={h}
              disabled={!it}
              onClick={() => it && onPickHour(it.ts)}
              title={it ? `${pad(h)}:00 · ${OUTCOME[out].label} · diesel ${it.on ? 'ON' : 'OFF'}` : ''}
              className="flex flex-col items-center gap-1 disabled:cursor-default"
            >
              <span
                className="flex h-9 w-full items-center justify-center rounded-md text-[15px] font-semibold"
                style={{ background: out ? OUTCOME[out].color : '#17171a', opacity: out === 'same' ? 0.55 : 1, color: '#09090b' }}
              >
                {it?.on ? '⛽' : ''}
              </span>
              <span className="tnum text-[14px] text-zinc-300">{h % 3 === 0 ? pad(h) : ''}</span>
            </button>
          )
        })}
      </div>
      <div className="mt-1 text-[15px] text-zinc-400">⛽ = generator running that hour</div>
    </div>
  )
}
