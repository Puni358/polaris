// Small hand-drawn SVG icons used by the story pages. All draw inside a 40x40 box
// at (x, y) so they can be dropped straight into a larger <svg>.

const stroke = { fill: 'none', strokeWidth: 2.2, strokeLinecap: 'round', strokeLinejoin: 'round' }

export function Sun({ x = 0, y = 0, c = '#facc15' }) {
  const rays = Array.from({ length: 8 }, (_, i) => {
    const a = (i * Math.PI) / 4
    return <line key={i} x1={20 + Math.cos(a) * 12} y1={20 + Math.sin(a) * 12} x2={20 + Math.cos(a) * 18} y2={20 + Math.sin(a) * 18} stroke={c} {...stroke} />
  })
  return <g transform={`translate(${x} ${y})`}><circle cx="20" cy="20" r="8" fill={c} />{rays}</g>
}

export function Cloud({ x = 0, y = 0, c = '#94a3b8' }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <path d="M11 28 h18 a6 6 0 0 0 0 -12 a8 8 0 0 0 -15 -2 a7 7 0 0 0 -3 14 z" stroke={c} {...stroke} />
    </g>
  )
}

export function Wind({ x = 0, y = 0, c = '#94a3b8' }) {
  return (
    <g transform={`translate(${x} ${y})`} stroke={c} {...stroke}>
      <line x1="20" y1="22" x2="20" y2="38" />
      <circle cx="20" cy="20" r="2" fill={c} />
      <path d="M20 20 L20 4" /><path d="M20 20 L33 27" /><path d="M20 20 L7 27" />
    </g>
  )
}

export function Battery({ x = 0, y = 0, c = '#34d399', level = 0.65 }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <rect x="6" y="11" width="26" height="18" rx="3" stroke={c} {...stroke} />
      <rect x="32" y="16" width="3.5" height="8" rx="1" fill={c} />
      <rect x="9" y="14" width={20 * level} height="12" rx="1.5" fill={c} opacity="0.85" />
    </g>
  )
}

export function Diesel({ x = 0, y = 0, c = '#f97316' }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <path d="M20 5 C13 15 10 20 10 25 a10 10 0 0 0 20 0 C30 20 27 15 20 5 z" stroke={c} {...stroke} />
      <path d="M21 17 L16 26 h6 l-3 7" stroke={c} {...stroke} />
    </g>
  )
}

export function House({ x = 0, y = 0, c = '#e4e4e7' }) {
  return (
    <g transform={`translate(${x} ${y})`} stroke={c} {...stroke}>
      <path d="M6 20 L20 7 L34 20" />
      <path d="M10 18 V33 H30 V18" />
      <rect x="17" y="24" width="6" height="9" fill={c} opacity="0.3" />
    </g>
  )
}

export function Brain({ x = 0, y = 0, c = '#22d3ee' }) {
  // A simple chip / decision-node glyph: square with pins and a small tree inside.
  return (
    <g transform={`translate(${x} ${y})`} stroke={c} {...stroke}>
      <rect x="9" y="9" width="22" height="22" rx="3" />
      {[14, 20, 26].map((v) => <g key={v}><line x1={v} y1="4" x2={v} y2="9" /><line x1={v} y1="31" x2={v} y2="36" /><line x1="4" y1={v} x2="9" y2={v} /><line x1="31" y1={v} x2="36" y2={v} /></g>)}
      <circle cx="20" cy="15" r="1.8" fill={c} /><circle cx="15" cy="25" r="1.8" fill={c} /><circle cx="25" cy="25" r="1.8" fill={c} />
      <path d="M20 17 L15 23 M20 17 L25 23" />
    </g>
  )
}

export function Bulb({ x = 0, y = 0, on = true, c = '#facc15' }) {
  const col = on ? c : '#52525b'
  return (
    <g transform={`translate(${x} ${y})`} stroke={col} {...stroke}>
      <path d="M14 26 a9 9 0 1 1 12 0 c-1.5 1.5 -2 3 -2 5 h-8 c0 -2 -0.5 -3.5 -2 -5 z" fill={on ? c : 'none'} fillOpacity="0.25" />
      <line x1="16" y1="35" x2="24" y2="35" />
      {!on && <path d="M9 9 L31 31" stroke="#f43f5e" />}
    </g>
  )
}
