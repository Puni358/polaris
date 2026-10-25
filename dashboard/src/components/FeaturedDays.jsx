import { useEffect, useState } from 'react'
import { okJson } from '../data/safeFetch.js'

export function useFeaturedDays() {
  const [data, setData] = useState(null)
  useEffect(() => {
    let off = false
    fetch('/data/featured_days.json').then(okJson).then((j) => { if (!off) setData(j) }).catch(() => {})
    return () => { off = true }
  }, [])
  return data?.days ?? []
}

const fmtDate = (d) => new Date(`${d}T00:00:00Z`).toUTCString().slice(5, 16)

// Drop-down of the days worth explaining, with a one-paragraph highlight of the selected day.
export default function FeaturedDays({ days, value, onPick, note }) {
  if (!days.length) return null
  const cur = days.find((d) => d.date === value)
  return (
    <div className="rounded-lg border-2 border-amber-600 bg-amber-950/20 p-4">
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-[19px] font-extrabold text-amber-200" htmlFor="featured-day">★ Days worth explaining</label>
        <select
          id="featured-day"
          value={value ?? ''}
          onChange={(e) => onPick(e.target.value || null)}
          className="min-w-[340px] rounded-lg border-2 border-amber-600 bg-scada-panel2 px-3 py-2 text-[18px] font-bold text-white"
        >
          <option value="">Choose a day…</option>
          {days.map((d) => <option key={d.date} value={d.date}>{fmtDate(d.date)} — {d.title}</option>)}
        </select>
        {note && <span className="text-[16px] font-semibold text-zinc-300">{note}</span>}
      </div>
      {cur && (
        <div className="mt-3">
          <div className="flex flex-wrap items-baseline gap-3">
            <span className="text-[22px] font-extrabold text-white">{cur.title}</span>
            <span className="tnum text-[17px] font-bold text-amber-300">{fmtDate(cur.date)}</span>
          </div>
          <p className="mt-1 text-[19px] font-semibold leading-relaxed text-zinc-100">{cur.reason}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {[
              [`${cur.metrics.diesel_l.toFixed(0)} L diesel`, cur.metrics.diesel_l > 0],
              [`${cur.metrics.diesel_hours} h generator`, cur.metrics.diesel_hours > 0],
              [`min battery ${cur.metrics.min_soc_pct.toFixed(1)}%`, true],
              [`${cur.metrics.solar_kwh.toFixed(0)} kWh solar`, true],
              [`${cur.metrics.unserved_kwh.toFixed(1)} kWh load lost`, false],
            ].map(([t, hot]) => (
              <span key={t} className={`tnum rounded-full border px-3 py-1 text-[16px] font-bold ${t.includes('load lost') ? 'border-emerald-600 bg-emerald-950/40 text-emerald-300' : hot ? 'border-orange-700 bg-orange-950/30 text-orange-200' : 'border-scada-border bg-scada-panel2 text-zinc-200'}`}>{t}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
