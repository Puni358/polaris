import { PieChart, Pie, Cell } from 'recharts'

// Ring chart with a big number in the middle. `rings` is an array of
// { data:[{value,color}], inner, outer } drawn from the outside in.
export default function Donut({ rings, size = 190, center, sub }) {
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <PieChart width={size} height={size}>
        {rings.map((r, i) => (
          <Pie
            key={i}
            data={r.data}
            dataKey="value"
            startAngle={90}
            endAngle={-270}
            innerRadius={r.inner}
            outerRadius={r.outer}
            stroke="#09090b"
            strokeWidth={2}
            isAnimationActive={false}
          >
            {r.data.map((d, k) => <Cell key={k} fill={d.color} />)}
          </Pie>
        ))}
      </PieChart>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <div className="tnum text-[34px] font-semibold leading-none text-zinc-100">{center}</div>
        {sub && <div className="mt-1 text-[15px] uppercase tracking-wide text-zinc-300">{sub}</div>}
      </div>
    </div>
  )
}
