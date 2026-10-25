// Scenario manifest -- the UI derives ALL comparability decisions from this
// file, never from a hand-set flag on an individual record.
//
// Real, patched-solver run artifacts landed 2026-10-22. Aggregates (View 1/4)
// below are real and validated. The Decision Inspector (View 2) still runs
// on mock data -- the per-hour causal fields it needs (ebr_target_wh,
// constraints, planned vs executed, full forecast_horizon array) were not
// captured by these runs and require a separate, narrowly scoped
// instrumented pass before View 2 can go real.

export const SCENARIO_MANIFEST = [
  {
    scenario_id: 'reactive',
    label: 'Reactive Baseline',
    run_id: 'ui_dashboard_reactive_baseline.csv',
    code_version: 'reactive_hybrid_a2.py',
    eval_start: '2024-01-20T00:00:00Z',
    eval_end: '2024-12-31T23:00:00Z',
    window_hours: 8328,
    initial_soc_pct: 50.0,
    methodology: 'Zero-forecast, rule-based reactive dispatch (current-timestep only)',
    forecast_mode: 'none',
    validation_status: 'validated',
    evidence_refs: ['unmet_load audit: 0.0 kWh across all 8,328 hours'],
  },
  {
    scenario_id: 'scenario1',
    label: 'Scenario 1 — Perfect Foresight (Theoretical)',
    run_id: 'ui_dashboard_scenario1_instrumented.csv',
    code_version: 'run_n6_rhc_annual_instrumented.py (patched, J1b)',
    eval_start: '2024-01-01T00:00:00Z',
    eval_end: '2024-12-30T23:00:00Z',
    window_hours: 8760,
    initial_soc_pct: 50.0,
    methodology: 'Perfect 24h-ahead foresight (actual GHI fed directly as forecast) -- theoretical ceiling, not achievable in the field',
    forecast_mode: 'perfect_foresight',
    validation_status: 'validated',
    evidence_refs: ['unmet_load audit: 0.0 kWh across all 8,760 hours (post-patch)'],
    not_directly_comparable: true,
    not_comparable_reason: 'Different evaluation window (8,760h vs 8,328h) and perfect-foresight methodology; reference only.',
  },
  {
    scenario_id: 'scenario4',
    label: 'Scenario 4 — Naive N6 ML (No Safety Buffers)',
    run_id: 'ui_dashboard_scenario4.csv',
    code_version: 'run_continuous_ui_rhc_scenario4.py (patched, J1b)',
    eval_start: '2024-01-20T00:00:00Z',
    eval_end: '2024-12-31T23:00:00Z',
    window_hours: 8328,
    initial_soc_pct: 50.0,
    methodology: 'Real N6 rolling forecast, EBR reserve policy fully disabled',
    forecast_mode: 'n6_rolling',
    validation_status: 'validated',
    evidence_refs: ['unmet_load audit: 200.5 kWh across 56/8,328 hours -- genuine resource exhaustion, no reserve buffer to absorb it'],
  },
  {
    scenario_id: 'scenario3',
    label: 'Scenario 3 — N6 ML Paranoid (EBR, no deadband)',
    run_id: 'ui_dashboard_scenario3.csv',
    code_version: 'run_continuous_ui_rhc_scenario3.py (patched, J1b)',
    eval_start: '2024-01-20T00:00:00Z',
    eval_end: '2024-12-31T23:00:00Z',
    window_hours: 8328,
    initial_soc_pct: 50.0,
    methodology: 'Real N6 rolling forecast, EBR conformal reserve policy active, no deadband',
    forecast_mode: 'n6_rolling',
    validation_status: 'validated',
    evidence_refs: ['unmet_load audit: 0.0 kWh across all 8,328 hours'],
  },
  {
    scenario_id: 'scenario2',
    label: 'Scenario 2 — N6 ML Pragmatic (EBR + 10kWh deadband)',
    run_id: 'ui_dashboard_scenario2.csv',
    code_version: 'run_continuous_ui_rhc_scenario2.py (patched, J1b)',
    eval_start: '2024-01-20T00:00:00Z',
    eval_end: '2024-12-31T23:00:00Z',
    window_hours: 8328,
    initial_soc_pct: 50.0,
    methodology: 'Real N6 rolling forecast, EBR conformal reserve policy active, 10kWh reserve deadband',
    forecast_mode: 'n6_rolling',
    validation_status: 'validated',
    evidence_refs: ['unmet_load audit: 0.0 kWh across all 8,328 hours'],
  },
]

// A set is "comparable" only if: same window_hours, validation_status !== 'mock'
// is NOT required for mock-mode browsing, but real ranking in production must
// additionally check validation_status === 'validated'.
export function getComparableScenarioIds(manifest = SCENARIO_MANIFEST) {
  const groups = new Map()
  for (const s of manifest) {
    if (s.not_directly_comparable) continue
    const key = s.window_hours
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(s.scenario_id)
  }
  // Return the largest matched-window group (that's our real comparable set)
  let best = []
  for (const ids of groups.values()) if (ids.length > best.length) best = ids
  return best
}
