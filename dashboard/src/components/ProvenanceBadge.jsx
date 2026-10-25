const STYLES = {
  MEASURED: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  SIMULATED: 'bg-cyan-950 text-cyan-400 border-cyan-800',
  THEORETICAL: 'bg-violet-950 text-violet-400 border-violet-800',
  PENDING_VERIFICATION: 'bg-amber-950 text-amber-400 border-amber-800',
  PENDING_RERUN: 'bg-amber-950 text-amber-400 border-amber-800',
  MOCK: 'bg-zinc-800 text-zinc-400 border-zinc-700',
}

const LABELS = {
  MEASURED: 'MEASURED',
  SIMULATED: 'SIMULATED',
  THEORETICAL: 'THEORETICAL',
  PENDING_VERIFICATION: 'PENDING VERIFICATION',
  PENDING_RERUN: 'PENDING RERUN',
  MOCK: 'MOCK / DEMO',
}

export default function ProvenanceBadge({ provenance, className = '' }) {
  const key = provenance || 'MOCK'
  return (
    <span
      className={`tnum inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 text-[15px] font-medium uppercase tracking-wide ${STYLES[key] || STYLES.MOCK} ${className}`}
      title={`Data provenance: ${LABELS[key] || key}`}
    >
      {LABELS[key] || key}
    </span>
  )
}
