// Per Rule 1 (the Data Gate): a field not recorded by the real solver runs
// must render this, never a mock/fabricated value. `reason` should name
// specifically what's missing.
export default function DataUnavailable({ reason, compact = false }) {
  if (compact) {
    return <span className="tnum text-amber-600" title={reason}>UNAVAILABLE</span>
  }
  return (
    <div className="rounded border border-dashed border-amber-800/60 bg-amber-950/20 px-2 py-1.5">
      <div className="text-[15px] font-medium uppercase tracking-wide text-amber-600">
        Data Unavailable / Awaiting Instrumented Pass
      </div>
      {reason && <div className="mt-0.5 text-[15px] text-zinc-400">{reason}</div>}
    </div>
  )
}
