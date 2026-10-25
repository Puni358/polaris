// Mock per-hour decision records, shaped EXACTLY to the final data contract.
// Every record below carries provenance: "MOCK" explicitly -- components must
// read this field and the global demo ribbon must be visible whenever any
// rendered panel is sourced from mock data. When real CSVs are wired in, this
// generator is deleted wholesale; nothing else should need to change.

const HOURS = 72 // enough to scrub through ~3 winter days in the Decision Inspector

function seededRand(seed) {
  let s = seed
  return () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
}

// Deep-winter-ish synthetic GHI: mostly dark, short faint midday bump.
function synthGhi(hourOfYear, rand) {
  const hod = hourOfYear % 24
  const base = hod >= 10 && hod <= 14 ? 60 * Math.sin(((hod - 10) / 4) * Math.PI) : 0
  const noise = (rand() - 0.5) * 10
  return Math.max(0, base + noise)
}

function synthDemand(hourOfDay, month = 1) {
  const diurnal =
    hourOfDay <= 5 ? 18000
    : hourOfDay === 6 ? 22000
    : hourOfDay === 7 ? 30000
    : hourOfDay === 8 ? 38000
    : hourOfDay <= 17 ? 32000
    : hourOfDay === 18 ? 36000
    : hourOfDay === 19 ? 42000
    : hourOfDay <= 21 ? 30000
    : 22000
  const mult = [11, 12, 1, 2].includes(month) ? 1.2 : [5, 6, 7, 8].includes(month) ? 0.85 : 1.0
  return Math.min(Math.max(diurnal * mult, 15000), 45000)
}

function synthWind(hourOfDay) {
  return 15000 + 10000 * Math.sin((hourOfDay * Math.PI) / 6)
}

function makeForecastHorizon(originHourOfYear, rand, modelVersion, issueTs) {
  const arr = []
  for (let h = 0; h < 24; h++) {
    const trueGhi = synthGhi(originHourOfYear + h, rand)
    // forecast error grows with horizon distance -- proportionally larger
    // uncertainty further out, consistent with the real N6 conformal design
    const noise = (rand() - 0.5) * (6 + h * 1.4)
    arr.push({
      horizon_step: h,
      forecast_ghi: Math.max(0, +(trueGhi + noise).toFixed(1)),
      forecast_issue_timestamp: issueTs,
    })
  }
  return arr
}

function buildScenarioSeries(scenarioId, opts) {
  const {
    seed,
    startSocPct,
    dieselBias, // 0..1 propensity to fire diesel
    ebrOn,
    deadbandWh,
    forecastMode, // 'perfect_foresight' | 'n6_rolling' | 'none'
  } = opts
  const rand = seededRand(seed)
  const rows = []
  let socPct = startSocPct
  let prevDieselKw = 0
  const startDate = new Date('2024-01-20T00:00:00Z')

  for (let i = 0; i < HOURS; i++) {
    const t = new Date(startDate.getTime() + i * 3600 * 1000)
    const decisionTs = t.toISOString()
    const hourOfDay = t.getUTCHours()
    const actualGhi = +synthGhi(i, rand).toFixed(1)
    const demandW = +synthDemand(hourOfDay).toFixed(1)
    const criticalDemandW = 15000.0
    const windW = +synthWind(hourOfDay).toFixed(1)
    const solarW = +(actualGhi * 51.0).toFixed(1)

    const ebrTargetWh = ebrOn ? Math.max(0, 15000 - (deadbandWh || 0)) : 0
    const batteryWh = (socPct / 100) * 200000

    // deficit-driven diesel propensity, scaled by scenario's dieselBias
    const netRenewable = solarW + windW - demandW
    let dieselKw = 0
    if (netRenewable < 0 && (batteryWh < 60000 || rand() < dieselBias)) {
      dieselKw = Math.min(100, Math.max(10, Math.round((-netRenewable / 1000) * (0.6 + dieselBias * 0.8))))
    }
    // ramp smoothing for display realism
    if (Math.abs(dieselKw - prevDieselKw) > 30) {
      dieselKw = prevDieselKw + Math.sign(dieselKw - prevDieselKw) * 30
    }
    prevDieselKw = dieselKw

    const netSurplusW = solarW + windW + dieselKw * 1000 - demandW
    socPct = Math.max(20, Math.min(95, socPct + netSurplusW / 2000))

    const criticalServed = criticalDemandW // patched solver: critical always protected
    const totalServed = Math.min(demandW, solarW + windW + dieselKw * 1000 + Math.max(0, batteryWh - 40000))
    const nonCriticalServed = Math.max(0, Math.min(demandW - criticalDemandW, totalServed - criticalDemandW))
    const j1UnmetCrit = 0.0
    const j1bUnmetNoncrit = Math.max(0, (demandW - criticalDemandW) - nonCriticalServed)

    const forecastIssueTs = decisionTs // RHC: forecast issued at the same hour it's used
    const forecastHorizon =
      forecastMode === 'none'
        ? null
        : makeForecastHorizon(i, rand, forecastMode === 'perfect_foresight' ? 'perfect-foresight-v0' : 'n6-ensemble-v6', forecastIssueTs)

    rows.push({
      decision_timestamp: decisionTs,
      measurement_timestamp: decisionTs,
      forecast_issue_timestamp: forecastMode === 'none' ? null : forecastIssueTs,
      actual_ghi: actualGhi,
      forecast_horizon: forecastHorizon,
      model_version: forecastMode === 'perfect_foresight' ? 'perfect-foresight-v0' : forecastMode === 'n6_rolling' ? 'n6-ensemble-v6' : null,
      causality_verified: forecastMode !== 'none',
      demand_w: demandW,
      critical_demand_w: criticalDemandW,
      battery_soc_pct: +socPct.toFixed(2),
      battery_charge_wh: netSurplusW > 0 ? +Math.min(netSurplusW, 50000).toFixed(1) : 0,
      battery_discharge_wh: netSurplusW < 0 ? +Math.min(-netSurplusW, 50000).toFixed(1) : 0,
      diesel_kw: dieselKw,
      diesel_fuel_liters: dieselKw > 0 ? +(5.0 + dieselKw * 1000 * 0.00025).toFixed(2) : 0,
      fuel_price_eur_per_l: 2.5,
      currency: 'EUR',
      diesel_fuel_cost_eur: dieselKw > 0 ? +((5.0 + dieselKw * 1000 * 0.00025) * 2.5).toFixed(2) : 0,
      ebr_target_wh: ebrOn ? ebrTargetWh : 0,
      reserve_deadband_wh: deadbandWh || 0,
      operating_mode: socPct <= 20.5 ? 'CONSERVATION' : 'NORMAL',
      constraints: [
        { name: 'battery_soc_floor', status: socPct <= 20.5 ? 'ACTIVE' : 'OK', violation_magnitude: 0 },
        { name: 'critical_load_balance', status: 'OK', violation_magnitude: 0 },
        { name: 'reserve_envelope_j2', status: ebrOn && batteryWh < ebrTargetWh + 40000 ? 'BINDING' : 'OK', violation_magnitude: 0 },
      ],
      j1_unmet_crit_w: j1UnmetCrit,
      j1b_unmet_noncrit_w: +j1bUnmetNoncrit.toFixed(1),
      load_served_critical_w: criticalServed,
      load_served_noncritical_w: +nonCriticalServed.toFixed(1),
      renewable_curtailment_wh: 0, // verified zero per our own audit, not "unavailable"
      planned_action: { diesel_kw: dieselKw, battery_charge_wh: netSurplusW > 0 ? netSurplusW : 0, battery_discharge_wh: netSurplusW < 0 ? -netSurplusW : 0 },
      executed_action: { diesel_kw: dieselKw, battery_charge_wh: netSurplusW > 0 ? netSurplusW : 0, battery_discharge_wh: netSurplusW < 0 ? -netSurplusW : 0 },
      provenance: 'MOCK',
    })
  }
  return rows
}

export const MOCK_SERIES = {
  reactive: buildScenarioSeries('reactive', { seed: 11, startSocPct: 50, dieselBias: 0.55, ebrOn: false, deadbandWh: 0, forecastMode: 'none' }),
  scenario1: buildScenarioSeries('scenario1', { seed: 22, startSocPct: 50, dieselBias: 0.05, ebrOn: false, deadbandWh: 0, forecastMode: 'perfect_foresight' }),
  scenario4: buildScenarioSeries('scenario4', { seed: 33, startSocPct: 50, dieselBias: 0.02, ebrOn: false, deadbandWh: 0, forecastMode: 'n6_rolling' }),
  scenario3: buildScenarioSeries('scenario3', { seed: 44, startSocPct: 50, dieselBias: 0.5, ebrOn: true, deadbandWh: 0, forecastMode: 'n6_rolling' }),
  scenario2: buildScenarioSeries('scenario2', { seed: 55, startSocPct: 50, dieselBias: 0.38, ebrOn: true, deadbandWh: 10000, forecastMode: 'n6_rolling' }),
}

// Scenario-level aggregate KPIs (mock, in the final shape the real patched
// reruns will fill). Used by View 1 KPI cards and the View 4 scatter.
export const MOCK_AGGREGATES = {
  // This one is REAL: independently verified in the audit (0.0 kWh unmet
  // load across all 8,328 hours), not a mock placeholder like the rest below.
  reactive: { diesel_liters: 54167.02, diesel_run_hours: 6412, diesel_starts: 320, battery_cycles: 44.38, battery_cycling_loss_kwh: 1476.8, fuel_cost_eur: 135417.57, unmet_load_kwh: 0.0, window_hours: 8328, provenance: 'SIMULATED', run_id: 'ui_dashboard_reactive_baseline.csv' },
  scenario1: { diesel_liters: null, diesel_run_hours: null, diesel_starts: null, battery_cycles: null, battery_cycling_loss_kwh: null, fuel_cost_eur: null, unmet_load_kwh: null, window_hours: 8760, provenance: 'PENDING_RERUN', note: 'Patched rerun in progress -- pre-patch number (710 L) discarded, do not display.' },
  scenario4: { diesel_liters: null, diesel_run_hours: null, diesel_starts: null, battery_cycles: null, battery_cycling_loss_kwh: null, fuel_cost_eur: null, unmet_load_kwh: null, window_hours: 8328, provenance: 'PENDING_RERUN' },
  scenario3: { diesel_liters: null, diesel_run_hours: null, diesel_starts: null, battery_cycles: null, battery_cycling_loss_kwh: null, fuel_cost_eur: null, unmet_load_kwh: null, window_hours: 8328, provenance: 'PENDING_RERUN' },
  scenario2: { diesel_liters: null, diesel_run_hours: null, diesel_starts: null, battery_cycles: null, battery_cycling_loss_kwh: null, fuel_cost_eur: null, unmet_load_kwh: null, window_hours: 8328, provenance: 'PENDING_RERUN' },
}
