// Horizontal bullet graph: physical hard floor/ceiling as crimson zones,
// dynamic EBR target + deadband as an overlay marker, current SOC as a bar.
// Floor/ceiling values are read from the scenario's own config, never
// hardcoded -- if a scenario's manifest doesn't confirm them, render "—".

export default function SocBulletGraph({ socPct, floorPct = 20, ceilingPct = 95, ebrTargetPct = null, deadbandPct = 0 }) {
  const clamp = (v) => Math.max(0, Math.min(100, v))
  const socX = clamp(socPct)

  return (
    <div className="w-full">
      <div className="relative h-7 w-full overflow-hidden rounded-sm border border-scada-border bg-scada-panel2">
        {/* sub-floor red zone */}
        <div className="absolute inset-y-0 left-0 bg-rose-950/70" style={{ width: `${floorPct}%` }} />
        {/* super-ceiling red zone */}
        <div className="absolute inset-y-0 bg-rose-950/70" style={{ left: `${ceilingPct}%`, right: 0 }} />
        {/* EBR target + deadband overlay (gray target band) */}
        {ebrTargetPct !== null && (
          <div
            className="absolute inset-y-0 bg-zinc-600/30 border-x border-zinc-500/50"
            style={{ left: `${clamp(ebrTargetPct - deadbandPct)}%`, width: `${clamp(deadbandPct * 2) || 0.4}%` }}
            title={`EBR target ${ebrTargetPct.toFixed(1)}% ± ${deadbandPct.toFixed(1)}% deadband`}
          />
        )}
        {/* current SOC bar */}
        <div
          className="absolute inset-y-0 left-0 bg-cyan-500/80 transition-[width] duration-300"
          style={{ width: `${socX}%` }}
        />
        {/* current SOC marker line */}
        <div className="absolute inset-y-0 w-px bg-cyan-200" style={{ left: `${socX}%` }} />
      </div>
      <div className="tnum mt-1 flex justify-between text-[15px] text-zinc-300">
        <span>0%</span>
        <span className="text-rose-500">floor {floorPct}%</span>
        {ebrTargetPct !== null && <span className="text-zinc-400">target {ebrTargetPct.toFixed(0)}%</span>}
        <span className="text-rose-500">ceiling {ceilingPct}%</span>
        <span>100%</span>
      </div>
    </div>
  )
}
