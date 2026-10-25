import ProvenanceBadge from './ProvenanceBadge.jsx'

function fmt(value, digits = 1) {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString('en-US', { maximumFractionDigits: digits, minimumFractionDigits: 0 })
}

export default function KpiCard({ label, value, unit, delta, deltaGood, provenance, meta, digits = 1, hideProvenance = false }) {
  const unavailable = value === null || value === undefined
  return (
    <div className="flex flex-col gap-2 rounded border border-scada-border bg-scada-panel p-3">
      <div className="flex items-center justify-between">
        <span className="text-[16px] uppercase tracking-wide text-zinc-300">{label}</span>
        {!hideProvenance && <ProvenanceBadge provenance={unavailable ? 'PENDING_RERUN' : provenance} />}
      </div>
      <div className="flex items-baseline gap-1">
        <span className={`tnum text-2xl font-semibold ${unavailable ? 'text-zinc-400' : 'text-zinc-100'}`}>
          {unavailable ? 'UNAVAILABLE' : fmt(value, digits)}
        </span>
        {!unavailable && unit && <span className="tnum self-end pb-0.5 text-[15px] leading-none text-zinc-400">{unit}</span>}
      </div>
      {!unavailable && delta !== undefined && delta !== null && (
        <div className={`tnum text-[17px] ${deltaGood ? 'text-emerald-500' : 'text-rose-500'}`}>{delta}</div>
      )}
      {meta && <div className="text-[15px] text-zinc-400">{meta}</div>}
    </div>
  )
}
