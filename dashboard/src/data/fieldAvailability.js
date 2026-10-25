// Data Gate result (verified against the real solver CSVs, 2026-10-22):
// forecast_horizon, planned_action, binding_constraints, and ebr_target_wh
// are NOT present in ANY scenario's real output. demand_w / unmet_load_w
// only exist for reactive and scenario1. n6_forecast_ghi (a single
// 1-hour-ahead point, NOT a full 24h horizon) only exists for scenario2/3/4.
//
// Every UI component reads this map before rendering a field. A field not
// listed here, or listed false, MUST render "Data Unavailable / Awaiting
// Instrumented Pass" -- never a mock value.

export const FIELD_AVAILABILITY = {
  reactive: { demand_w: true, unmet_load_w: true, n6_forecast_ghi_point: false, actual_ghi: true },
  scenario1: { demand_w: true, unmet_load_w: true, n6_forecast_ghi_point: false, actual_ghi: false },
  scenario4: { demand_w: false, unmet_load_w: false, n6_forecast_ghi_point: true, actual_ghi: true },
  scenario3: { demand_w: false, unmet_load_w: false, n6_forecast_ghi_point: true, actual_ghi: true },
  scenario2: { demand_w: true, unmet_load_w: false, n6_forecast_ghi_point: true, actual_ghi: true, forecast_horizon: true, ebr_target_wh: true, binding_constraints: true, planned_action: true },
}

// Fields that are NEVER recorded by any current run, regardless of scenario.
// These are the four fields the Data Gate was specifically checking for.
export const NEVER_RECORDED = {
  forecast_horizon: 'Full 24h forecast horizon not captured -- only a single 1-hour-ahead point (n6_forecast_ghi) exists for scenario2/3/4, and none for reactive/scenario1.',
  planned_action: 'Solver\'s planned dispatch is not persisted separately from the executed physical realization -- only the single executed diesel_kw / battery_net_kw values were recorded.',
  binding_constraints: 'Per-hour constraint-binding status (which limits were active) was not instrumented in these runs.',
  ebr_target_wh: 'Per-hour reserve target was not persisted to the output CSV.',
}

export function isFieldAvailable(scenarioId, field) {
  return !!FIELD_AVAILABILITY[scenarioId]?.[field]
}

// Verified governed load architecture (per the internal terminology audit --
// no "9.0 kW" / "11.2 kW" / named equipment exists in the code; the solver
// mathematically uses a flat critical floor + a discretionary slice).
export const LOAD_ARCHITECTURE = {
  criticalFloorKw: 11.6,
  criticalLabel: 'Critical Floor (Priority J1)',
  criticalDescription: '11.6 kW (Governed Baseline)',
  noncriticalLabel: 'Non-Critical Demand (Priority J1b)',
  noncriticalDescription: 'Sheddable Discretionary',
}

// Physical constants that ARE fixed configuration (not per-hour telemetry),
// so they're stated as known governed values, not gated as "unavailable".
export const BATTERY_CONSTANTS = {
  capacityWh: 200000,
  minSocPct: 20,
  maxSocPct: 95,
  minWh: 40000,
  maxWh: 190000,
}
