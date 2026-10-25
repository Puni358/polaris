// Shown while the matched re-runs are still computing (numbers are never shown half-finished).
export default function Pending({ data }) {
  const rows = data ? Object.entries(data.scenarios) : []
  return (
    <div className="rounded-lg border border-scada-border bg-scada-panel p-6">
      <h3 className="text-[18px] font-semibold text-zinc-200">Re-running every scenario on identical weather and demand…</h3>
      <p className="mb-4 mt-1 text-[17px] text-zinc-300">Numbers appear here when all five runs finish, so nothing is shown half-computed.</p>
      <div className="flex flex-col gap-2.5">
        {rows.map(([id, a]) => {
          const p = Math.min(1, a.hours / a.hours_total)
          return (
            <div key={id} className="flex items-center gap-3">
              <span className="w-56 shrink-0 text-[17px] text-zinc-300">{a.label}</span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-800"><div className="h-full rounded-full bg-cyan-400" style={{ width: `${p * 100}%` }} /></div>
              <span className="tnum w-12 text-right text-[16px] text-zinc-300">{Math.round(p * 100)}%</span>
            </div>
          )
        })}
        {rows.length === 0 && <div className="text-[17px] text-zinc-400">Waiting for the first results…</div>}
      </div>
    </div>
  )
}
