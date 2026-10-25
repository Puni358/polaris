// Shared classification of "how much would a different step-0 diesel decision have mattered".
// Walks the solver's own priority order: load (J1/J1b) > reserve (J2) > fuel (J3).
// Inputs are alternative-minus-model deltas: dLoad in Wh, dRes in kWh, dFuel in litres.

export function classifyStakes({ dLoad, dRes, dFuel, baseFuel }) {
  if (dLoad > 1) return 'critical'
  if (dRes > 0.05) return 'reserve'
  if (dLoad < -1 || dRes < -0.05) return 'better'
  if (Math.abs(dFuel) < Math.max(0.5, Math.abs(baseFuel) * 0.005)) return 'neartie'
  return dFuel > 0 ? 'costly' : 'better'
}

export const STAKES = {
  critical: { label: 'CRITICAL', cls: 'border-rose-700 bg-rose-950/40 text-rose-400' },
  reserve: { label: 'RESERVE RISK', cls: 'border-rose-700 bg-rose-950/40 text-rose-400' },
  costly: { label: 'COSTLY', cls: 'border-amber-700 bg-amber-950/40 text-amber-400' },
  neartie: { label: 'NEAR-TIE', cls: 'border-zinc-600 bg-zinc-800/60 text-zinc-300' },
  better: { label: 'ALTERNATIVE BETTER', cls: 'border-emerald-700 bg-emerald-950/40 text-emerald-400' },
}
