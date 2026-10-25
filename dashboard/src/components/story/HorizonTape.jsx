import { useEffect, useRef, useState } from 'react'

const SLIDE_MS = 500
const EVERY_MS = 3000
const pad = (n) => String(n).padStart(2, '0')

// Receding 24-hour tape: a conveyor belt that slides one block left every cycle. The left-most block is
// always the committed physical dispatch; the other 23 are the advisory horizon, re-solved every hour.
export default function HorizonTape({ active, baseHour = 8 }) {
  const [currentStartHour, setStart] = useState(0)
  const [isSliding, setSliding] = useState(false)
  const wrapRef = useRef(null)
  const [bw, setBw] = useState(34)

  useEffect(() => {
    if (!wrapRef.current) return undefined
    const measure = () => setBw(wrapRef.current.clientWidth / 24)
    measure()
    const ro = new ResizeObserver(measure)
    ro.observe(wrapRef.current)
    return () => ro.disconnect()
  }, [])

  useEffect(() => {
    if (!active) return undefined
    let inner
    const iv = setInterval(() => {
      setSliding(true)
      inner = setTimeout(() => {
        setStart((h) => h + 1)
        setSliding(false)
      }, SLIDE_MS)
    }, EVERY_MS)
    return () => { clearInterval(iv); clearTimeout(inner) }
  }, [active])

  const blocks = Array.from({ length: 25 }, (_, i) => (baseHour + currentStartHour + i) % 24)
  const t0 = blocks[0]

  return (
    <div className="rounded-lg border border-scada-border bg-scada-panel p-5">
      <h3 className="mb-1 text-[22px] font-bold text-white">The 24-hour window slides forward every hour</h3>
      <p className="mb-4 text-[18px] font-semibold text-zinc-300">Plan made at {pad(t0)}:00 → only the first hour is carried out → one hour later a fresh 24-hour plan starts.</p>

      <div className="relative pt-14">
        <div className="absolute left-0 top-0 text-[17px] font-extrabold text-emerald-300">Committed Physical Dispatch (t₀)</div>
        <div className="absolute right-0 top-0 text-[17px] font-bold text-cyan-300">Advisory horizon — re-solved every hour</div>
        <div className="absolute top-8 h-1.5 rounded bg-cyan-700/60" style={{ left: bw + 6, right: 0 }} />
        <div className="absolute top-8 h-1.5 rounded bg-emerald-400" style={{ left: 0, width: bw }} />

        <div ref={wrapRef} className="relative h-20 overflow-hidden rounded-md bg-scada-bg">
          <div
            className="flex h-full"
            style={{
              width: bw * 25,
              transform: isSliding ? `translateX(-${bw}px)` : 'translateX(0)',
              transition: isSliding ? `transform ${SLIDE_MS}ms ease-in-out` : 'none',
            }}
          >
            {blocks.map((h, i) => (
              <div
                key={`${currentStartHour}-${i}`}
                className="flex shrink-0 items-center justify-center border-r border-scada-bg text-[17px] font-bold"
                style={{ width: bw, background: '#0e3a4a', color: '#a5f3fc' }}
              >
                {pad(h)}
              </div>
            ))}
          </div>
          {/* fixed highlight on the left-most position */}
          <div className="pointer-events-none absolute left-0 top-0 h-full rounded-sm border-[3px] border-emerald-400 bg-emerald-400/20" style={{ width: bw, animation: 'glow-emerald 1.6s ease-in-out infinite' }} />
        </div>
      </div>
      <div className="mt-2 text-[16px] font-semibold text-zinc-400">Hour of day, UTC. The green frame stays put; time flows through it.</div>
    </div>
  )
}
