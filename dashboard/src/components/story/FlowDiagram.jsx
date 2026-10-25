import { Sun, Cloud, Wind, Battery, Diesel, House, Brain } from './Icons.jsx'

// "How POLARIS decides" — forecast in, 24 h plan, four power sources, station out,
// and the loop that repeats every hour.
export default function FlowDiagram({ flow }) {
  const w = (kw) => (flow ? 2 + Math.min(9, (kw || 0) / 6) : 2)
  const active = (kw) => !flow || (kw || 0) > 0.5
  const keyOf = { Solar: 'solar', Wind: 'wind', Battery: 'battery', Diesel: 'diesel' }
  const arrow = (d, color = '#52525b', dash, key, kw) => {
    const on = key == null || active(kw)
    return (
      <path
        key={key ?? d} d={d} fill="none" stroke={color} strokeWidth={key == null ? 2 : w(kw)}
        strokeOpacity={on ? 1 : 0.18} strokeDasharray={flow && key != null && on ? '10 8' : dash}
        className={flow && key != null && on ? 'flow-anim' : undefined}
        markerEnd="url(#arr)"
      />
    )
  }
  const src = [
    { y: 14, icon: <Sun x={14} y={8} />, label: 'Solar', c: '#facc15' },
    { y: 74, icon: <Wind x={14} y={8} />, label: 'Wind', c: '#94a3b8' },
    { y: 134, icon: <Battery x={12} y={8} />, label: 'Battery', c: '#34d399' },
    { y: 194, icon: <Diesel x={14} y={8} />, label: 'Diesel', c: '#f97316', tag: 'last resort' },
  ]
  return (
    <svg viewBox="0 0 960 312" className="h-auto w-full" role="img" aria-label="Forecast feeds the optimizer, which chooses between solar, wind, battery and diesel to supply the station">
      <defs>
        <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" orient="auto-start-reverse">
          <path d="M0 0 L10 5 L0 10 z" fill="#71717a" />
        </marker>
      </defs>

      {/* 1 forecast */}
      <g>
        <rect x="14" y="80" width="170" height="120" rx="14" fill="#121214" stroke="#27272a" strokeWidth="1.5" />
        <Sun x={42} y={96} /><Cloud x={84} y={102} />
        <text x="99" y="160" textAnchor="middle" fill="#e4e4e7" fontSize="19" fontWeight="600">Weather forecast</text>
        <text x="99" y="180" textAnchor="middle" fill="#71717a" fontSize="15">next 24 hours</text>
      </g>
      {arrow('M188 140 H262')}

      {/* 2 optimizer */}
      <g>
        <rect x="266" y="60" width="230" height="160" rx="16" fill="#0b2a30" stroke="#22d3ee" strokeWidth="2" />
        <Brain x={361} y={74} />
        <text x="381" y="144" textAnchor="middle" fill="#e4e4e7" fontSize="21" fontWeight="700">POLARIS</text>
        <text x="381" y="164" textAnchor="middle" fill="#67e8f9" fontSize="15">plans the next 24 h</text>
        <text x="381" y="184" textAnchor="middle" fill="#67e8f9" fontSize="15">in order of importance</text>
      </g>

      {/* 3 sources */}
      {src.map((s) => (
        <g key={s.label} transform={`translate(540 ${s.y})`}>
          <rect width="170" height="56" rx="12" fill="#121214" stroke={s.c} strokeOpacity="0.7" strokeWidth="1.5" />
          {s.icon}
          <text x="66" y={s.tag ? 24 : 34} fill="#e4e4e7" fontSize="19" fontWeight="600">{s.label}</text>
          {s.tag && <text x="66" y="42" fill={s.c} fontSize="14">{s.tag}</text>}
        </g>
      ))}
      {src.map((s) => arrow(`M500 140 C 520 140, 520 ${s.y + 28}, 536 ${s.y + 28}`, s.c, undefined, `a-${s.label}`, flow?.[keyOf[s.label]]))}
      {src.map((s) => arrow(`M714 ${s.y + 28} C 740 ${s.y + 28}, 740 140, 760 140`, s.c, undefined, `b-${s.label}`, flow?.[keyOf[s.label]]))}

      {/* 4 station */}
      <g>
        <rect x="764" y="80" width="182" height="120" rx="14" fill="#121214" stroke="#e4e4e7" strokeOpacity="0.5" strokeWidth="1.5" />
        <House x={835} y={90} />
        <text x="855" y="146" textAnchor="middle" fill="#e4e4e7" fontSize="19" fontWeight="600">Research station</text>
        <rect x="782" y="158" width="68" height="26" rx="6" fill="#4c0519" stroke="#f43f5e" />
        <text x="816" y="175" textAnchor="middle" fill="#fda4af" fontSize="14" fontWeight="600">Critical</text>
        <rect x="858" y="158" width="76" height="26" rx="6" fill="#422006" stroke="#f59e0b" />
        <text x="896" y="175" textAnchor="middle" fill="#fcd34d" fontSize="14" fontWeight="600">Comfort</text>
      </g>

      {/* loop */}
      <path d="M855 204 C 855 300, 381 300, 381 226" fill="none" stroke="#a78bfa" strokeWidth="2" strokeDasharray="6 5" markerEnd="url(#arr)" />
      <rect x="500" y="276" width="200" height="26" rx="13" fill="#1e1b4b" stroke="#a78bfa" />
      <text x="600" y="293" textAnchor="middle" fill="#c4b5fd" fontSize="15" fontWeight="600">repeats every hour</text>
    </svg>
  )
}
