// Optimizer reasoning reconstruction -- "why did the model do that this hour?"
//
// Every number below comes from a RECORDED field of the instrumented run
// (forecast_horizon, ebr_target_wh, planned_diesel_kw, binding_constraints,
// demand_w, battery_soc_pct, battery_net_kw, diesel_kw) combined with the
// governed constants of the solver (battery 200 kWh / 20-95 %, diesel 10-100 kW,
// 5 L/h + 0.25 L/kWh fuel curve, K_pv 51 W per W/m^2, objective ladder
// J1 > J1b > J2 > J3 > J4). Nothing is invented: the solver's own duals and
// planned 24 h trajectory were not persisted, so the narrative is a faithful
// reconstruction of what the solver SAW and the hierarchy it optimizes, not a
// dump of its internals. Wind supply was not recorded per step; look-ahead
// balances use forecast SOLAR plus an "implied wind" estimate (median of the
// run's own energy-balance residual for that hour of day), always labelled.

export const SOLVER = {
  capacityKwh: 200,
  floorPct: 20,
  ceilingPct: 95,
  floorKwh: 40,
  ceilingKwh: 190,
  eta: 0.92,
  kPv: 0.051, // kW per W/m^2
  pvCapKw: 60,
  dieselMinKw: 10,
  dieselMaxKw: 100,
  fuelBaseLh: 5,
  fuelMargLkwh: 0.25,
  startupL: 2,
  fuelPrice: 2.5,
  initialSocPct: 50,
}

// Deadband only exists in the "pragmatic" scenario.
const DEADBAND_KWH = { scenario2: 10 }

const fuelLitres = (kw) => (kw > 0 ? SOLVER.fuelBaseLh + SOLVER.fuelMargLkwh * kw : 0)
const f1 = (n) => (Math.round(n * 10) / 10).toFixed(1)
const f0 = (n) => String(Math.round(n))

export const MODES = {
  DIESEL_CHARGE: { label: 'DIESEL BATCH · CHARGING', tone: 'amber' },
  DIESEL_SUPPORT: { label: 'DIESEL SUPPORT', tone: 'amber' },
  RENEW_CHARGE: { label: 'CHARGING FROM RENEWABLES', tone: 'emerald' },
  DISCHARGE: { label: 'BATTERY DISCHARGE · DIESEL OFF', tone: 'cyan' },
  HOLD: { label: 'HOLD · DIESEL OFF', tone: 'zinc' },
}

// Wind (and any other non-solar supply) was not recorded per step, but it is
// recoverable from the run's own energy balance: surplus = solar + other +
// diesel - demand. The median of that residual per hour-of-day is used as the
// "implied other supply" in look-ahead balances and is always labelled as such.
const windCache = new WeakMap()
export function impliedWindByHour(series) {
  if (windCache.has(series)) return windCache.get(series)
  const buckets = Array.from({ length: 24 }, () => [])
  for (const r of series) {
    if (r.battery_net_kw == null || r.demand_w == null || r.actual_ghi == null || !r.timestamp) continue
    const resid = r.battery_net_kw - Math.min(r.actual_ghi * SOLVER.kPv, SOLVER.pvCapKw) - r.diesel_kw + r.demand_w / 1000
    buckets[new Date(r.timestamp).getUTCHours()].push(resid)
  }
  const med = buckets.map((b) => {
    if (!b.length) return 0
    b.sort((x, y) => x - y)
    return Math.max(0, b[Math.floor(b.length / 2)])
  })
  windCache.set(series, med)
  return med
}

export function hasReasoning(row) {
  return !!row && Array.isArray(row.forecast_horizon) && row.planned_diesel_kw != null
}

export function explainHour(series, i, scenarioId) {
  const row = series[i]
  if (!hasReasoning(row)) return null
  const prev = i > 0 ? series[i - 1] : null

  const socStart = prev ? prev.battery_soc_pct : SOLVER.initialSocPct
  const socEnd = row.battery_soc_pct
  const eStart = (socStart / 100) * SOLVER.capacityKwh
  const aboveFloor = Math.max(0, eStart - SOLVER.floorKwh)
  const prevDiesel = prev ? prev.diesel_kw : 0

  const planned = row.planned_diesel_kw
  const executed = row.diesel_kw
  const net = row.battery_net_kw ?? 0 // + charging surplus, - discharging
  const demandNow = (row.demand_w ?? 0) / 1000

  // ---- 24 planning steps exactly as the solver paired them: step j sees
  // forecast_horizon[j] and the demand at hour t+j.
  const windByHour = impliedWindByHour(series)
  const steps = []
  for (let j = 0; j < row.forecast_horizon.length; j++) {
    const r = series[i + j]
    const dem = r?.demand_w != null ? r.demand_w / 1000 : j === 0 ? demandNow : null
    if (dem == null) break
    const solar = Math.min(Math.max(0, row.forecast_horizon[j]) * SOLVER.kPv, SOLVER.pvCapKw)
    const hod = new Date(r?.timestamp ?? row.timestamp).getUTCHours()
    const wind = windByHour[hod] ?? 0
    steps.push({ j, ts: r?.timestamp ?? row.timestamp, solar, wind, demand: dem, net: solar + wind - dem, netSolarOnly: solar - dem })
  }

  // Solar-only, no-diesel battery trajectory (what the battery faces if the model does nothing).
  let e = eStart
  let floorStep = null
  let minE = eStart
  const traj = steps.map((s) => {
    e = s.net >= 0 ? Math.min(SOLVER.ceilingKwh, e + s.net * SOLVER.eta) : e + s.net / SOLVER.eta
    if (e <= SOLVER.floorKwh && floorStep === null) floorStep = s.j
    e = Math.max(SOLVER.floorKwh - 60, e) // allow dipping below to show the breach depth
    minE = Math.min(minE, e)
    return { ...s, socNoDiesel: (e / SOLVER.capacityKwh) * 100 }
  })

  const sum = (arr, k, n) => arr.slice(0, n).reduce((a, s) => a + s[k], 0)
  const solar3 = sum(steps, 'solar', 3), dem3 = sum(steps, 'demand', 3)
  const solar6 = sum(steps, 'solar', 6), dem6 = sum(steps, 'demand', 6)
  const solarAll = sum(steps, 'solar', 24), demAll = sum(steps, 'demand', 24)
  const coverAll = demAll > 0 ? (solarAll / demAll) * 100 : 0
  const cover3 = dem3 > 0 ? (solar3 / dem3) * 100 : 0
  const windAll = sum(steps, 'wind', 24)
  const deficitAll = demAll - solarAll - windAll
  const peak = steps.reduce((m, s) => (s.solar > m.solar ? s : m), { solar: 0, j: 0 })
  const solarCoversStep = steps.find((s) => s.j > 0 && s.solar >= s.demand)?.j ?? null
  const noSolar = solarAll < 5 // kWh across the whole window
  const autonomyH = demandNow > 0 ? aboveFloor / (demandNow / SOLVER.eta) : Infinity

  // ---- Reserve (J2)
  const ebrKwh = (row.ebr_target_wh ?? 0) / 1000
  const deadband = DEADBAND_KWH[scenarioId] ?? 0
  const reserveReq = Math.max(0, ebrKwh - deadband)
  const reserveMet = aboveFloor >= reserveReq

  const binding = row.binding_constraints ?? []

  // ---- Mode
  const dieselOn = executed > 0
  let mode
  if (dieselOn) mode = net > 0.5 ? 'DIESEL_CHARGE' : 'DIESEL_SUPPORT'
  else if (net > 0.5) mode = 'RENEW_CHARGE'
  else if (net < -0.5) mode = 'DISCHARGE'
  else mode = 'HOLD'

  const startedNow = dieselOn && prevDiesel <= 0
  const stoppedNow = !dieselOn && prevDiesel > 0

  // ---- Decision drivers (what actually decided it)
  let driver, headline, short
  const nearFloor = socStart <= SOLVER.floorPct + 3 || autonomyH < 1.5
  if (dieselOn) {
    if (nearFloor) {
      driver = 'FLOOR'
      headline = `Battery is only ${f1(aboveFloor)} kWh above the 20% hard floor (~${f1(autonomyH)} h of load). Hard limit beats fuel cost, so diesel runs at ${f1(executed)} kW.`
      short = `Diesel ${f0(executed)} kW · protecting 20% floor`
    } else if (!reserveMet) {
      driver = 'RESERVE'
      headline = `Battery holds ${f1(aboveFloor)} kWh above floor but the reserve target needs ${f1(reserveReq)} kWh. Reserve shortfall (J2) outranks fuel (J3), so diesel runs at ${f1(executed)} kW.`
      short = `Diesel ${f0(executed)} kW · rebuilding reserve`
    } else if (floorStep !== null || deficitAll > 0) {
      driver = 'ENERGY_BUDGET'
      const when = floorStep !== null ? `the battery would hit the floor at step +${floorStep}` : `forecast solar plus typical wind cover only ${f0(((solarAll + windAll) / demAll) * 100)}% of the next 24 h demand`
      headline = noSolar
        ? `No usable solar in the 24 h forecast, so ${when}. The plan must finish the horizon with more stored energy than it started with (see the reserve step), which leaves a ${f0(Math.max(0, deficitAll))} kWh gap (after typical wind) that only diesel can fill — and running it hard and in blocks is the cheapest way.`
        : deficitAll > 0
          ? `${when[0].toUpperCase() + when.slice(1)} (${f0(deficitAll)} kWh deficit over 24 h after solar and typical wind). Diesel is needed to meet the end-of-horizon energy target; running it at ${f1(executed)} kW keeps fuel per kWh low.`
          : `The 24 h balance is positive (+${f0(-deficitAll)} kWh), but the energy arrives too late: the battery would hit the floor at step +${floorStep} before solar and wind refill it. Diesel bridges that timing gap at ${f1(executed)} kW.`
      short = noSolar ? `Diesel ${f0(executed)} kW · no solar in forecast` : `Diesel ${f0(executed)} kW · ${f0(coverAll)}% solar cover`
    } else {
      driver = 'TIMING'
      headline = `Solar looks sufficient overall (${f0(coverAll)}% of demand) and the battery is healthy, yet diesel runs at ${f1(executed)} kW. The solver is shifting fuel burn into this hour; the planned and executed values agree.`
      short = `Diesel ${f0(executed)} kW · timing shift`
    }
  } else if (mode === 'RENEW_CHARGE') {
    driver = 'SURPLUS'
    headline = `Renewables exceed demand by ${f1(net)} kW, so the battery charges for free. No diesel is needed — fuel (J3) stays at zero.`
    short = `Charging +${f1(net)} kW from surplus`
  } else if (socStart >= SOLVER.ceilingPct - 1.5) {
    driver = 'CEILING'
    headline = `Battery is at ${f1(socStart)}% — essentially at the 95% ceiling — so there is nowhere to put extra energy. Diesel stays off and the battery carries the load.`
    short = `Hold · battery full`
  } else if (solarCoversStep !== null && (floorStep === null || floorStep > solarCoversStep) && !noSolar) {
    driver = 'WAIT_FOR_SOLAR'
    headline = `Solar is forecast to cover the load outright by step +${solarCoversStep} (peak ${f1(peak.solar)} kW at +${peak.j}). The battery's ${f1(aboveFloor)} kWh bridges that gap, so burning diesel now would only waste fuel.`
    short = `No diesel · bridging to solar at +${solarCoversStep}`
  } else if (floorStep === null) {
    driver = 'BATTERY_ENOUGH'
    headline = `The battery (${f1(aboveFloor)} kWh above floor) plus forecast solar (${f0(coverAll)}% of 24 h demand) never reaches the floor within the horizon. No need to start the generator.`
    short = `No diesel · battery sufficient`
  } else {
    driver = 'DEFER'
    headline = `Unaided, the battery (${f1(aboveFloor)} kWh usable) lasts until step +${floorStep}, so diesel is not needed yet. Starting now would burn the same 5 L/h fixed fuel per running hour as starting later, and the plan is re-solved every hour — fresher forecasts may remove the need to run at all.`
    short = `No diesel · battery lasts to +${floorStep}`
  }

  // ---- Reasoning ladder (follows the solver's priority order)
  const ladder = []

  ladder.push({
    key: 'state',
    title: 'Where is the battery?',
    tag: 'STATE',
    verdict: nearFloor ? 'warn' : 'ok',
    text: `Start of hour: ${f1(socStart)}% = ${f1(eStart)} kWh, i.e. ${f1(aboveFloor)} kWh usable above the 20% floor. At the current ${f1(demandNow)} kW load that is ~${Number.isFinite(autonomyH) ? f1(autonomyH) : '∞'} h of autonomy.`,
    facts: [
      ['SOC (start → end)', `${f1(socStart)}% → ${f1(socEnd)}%`],
      ['Usable above floor', `${f1(aboveFloor)} kWh`],
      ['Load now', `${f1(demandNow)} kW`],
    ],
  })

  ladder.push({
    key: 'forecast',
    title: 'What does the next 24 h look like?',
    tag: 'LOOK-AHEAD',
    verdict: noSolar ? 'warn' : 'ok',
    text: noSolar
      ? `The forecast shows essentially no solar for the whole window (${f1(solarAll)} kWh against ${f0(demAll)} kWh of demand). Nothing is coming to refill the battery.`
      : `Next 3 steps: forecast solar ${f1(solar3)} kWh vs demand ${f1(dem3)} kWh (${f0(cover3)}% cover). Over 24 steps: ${f0(solarAll)} kWh solar vs ${f0(demAll)} kWh demand (${f0(coverAll)}%). ${solarCoversStep !== null ? `Solar alone first covers the load at step +${solarCoversStep}, peaking at ${f1(peak.solar)} kW (+${peak.j}).` : 'Solar never fully covers the load on its own in this window.'}`,
    facts: [
      ['Solar next 3 / 6 steps', `${f1(solar3)} / ${f1(solar6)} kWh`],
      ['Implied wind next 3 steps', `${f1(sum(steps, 'wind', 3))} kWh`],
      ['Demand next 3 / 6 steps', `${f1(dem3)} / ${f1(dem6)} kWh`],
      ['24 h solar cover', `${f0(coverAll)}%`],
    ],
  })

  ladder.push({
    key: 'safety',
    title: 'Is anything unsafe? (J1 critical → J1b non-critical)',
    tag: 'PRIORITY 1–2',
    verdict: floorStep !== null ? 'warn' : 'ok',
    text: floorStep !== null
      ? `Without any diesel, forecast solar plus the run's typical wind would still let the battery hit the 20% floor at step +${floorStep}, at which point critical load goes unserved. Removing that risk is what the plan has to do before it worries about fuel.`
      : `Without any diesel, forecast solar plus typical wind keeps the battery above the 20% floor for all 24 steps (lowest ${f0((minE / SOLVER.capacityKwh) * 100)}%). Critical load is never at risk.`,
    facts: [
      ['Floor hit (no diesel)', floorStep !== null ? `step +${floorStep}` : 'never in 24 h'],
      [floorStep !== null ? 'Shortfall below floor' : 'Lowest projected SOC', floorStep !== null ? `${f0(SOLVER.floorKwh - minE)} kWh` : `${f0((minE / SOLVER.capacityKwh) * 100)}%`],
      ['Binding constraints', binding.length ? binding.join(', ') : 'none (interior solution)'],
    ],
  })

  ladder.push({
    key: 'reserve',
    title: 'Reserve buffer (J2 – EBR)',
    tag: 'PRIORITY 3',
    verdict: reserveMet ? 'ok' : 'warn',
    text: `Conformal reserve target is ${f1(ebrKwh)} kWh${deadband ? `, relaxed by the ${deadband} kWh deadband to ${f1(reserveReq)} kWh` : ''}. The battery holds ${f1(aboveFloor)} kWh above the floor, so the reserve is ${reserveMet ? `satisfied and not the deciding factor here (it only bites when the battery is within ${f1(reserveReq)} kWh of the floor)` : 'SHORT — this alone forces a response'}. The solver's end-of-horizon rule is stricter than it sounds: the terminal target is the starting energy (${f1(eStart)} kWh) but is applied on top of the 40 kWh floor, so after the ${deadband} kWh deadband the plan must finish ~${f1(Math.min(SOLVER.ceilingKwh, eStart + SOLVER.floorKwh - deadband))} kWh high — about ${f1(Math.min(SOLVER.ceilingKwh, eStart + SOLVER.floorKwh - deadband) - eStart)} kWh above where it started.`,
    facts: [
      ['EBR target', `${f1(ebrKwh)} kWh`],
      ['Effective requirement', `${f1(reserveReq)} kWh`],
      ['Held above floor', `${f1(aboveFloor)} kWh`],
    ],
  })

  // Fuel step
  const ratePerKwhChosen = executed > 0 ? fuelLitres(executed) / executed : 0
  const ratePerKwhMin = fuelLitres(SOLVER.dieselMinKw) / SOLVER.dieselMinKw
  const costNow = fuelLitres(executed) * SOLVER.fuelPrice
  const avoided = fuelLitres(SOLVER.dieselMinKw) * SOLVER.fuelPrice
  ladder.push({
    key: 'fuel',
    title: 'Is diesel worth it? (J3 fuel)',
    tag: 'PRIORITY 4',
    verdict: dieselOn ? 'action' : 'ok',
    text: dieselOn
      ? `${startedNow ? 'Generator STARTS this hour (+' + SOLVER.startupL + ' L start-up). ' : 'Generator keeps running. '}${f1(executed)} kW burns ${f1(fuelLitres(executed))} L (${f1(costNow)} cost units) = ${ratePerKwhChosen.toFixed(2)} L/kWh. Running at the 10 kW minimum would cost ${ratePerKwhMin.toFixed(2)} L/kWh, because the 5 L/h fixed burn is spread over fewer kWh — that is why the solver prefers fewer, harder runs.`
      : `Diesel stays OFF. The cheapest possible run (10 kW) still burns ${f1(fuelLitres(SOLVER.dieselMinKw))} L ≈ ${f1(avoided)} cost units per hour from the 5 L/h fixed burn${stoppedNow ? '; the generator stops after last hour’s run' : ''}, so it only starts when the higher priorities require it.`,
    facts: [
      ['Planned diesel', `${f1(planned)} kW`],
      ['Executed diesel', `${f1(executed)} kW`],
      [dieselOn ? 'Fuel this hour' : 'Fuel avoided (min run)', dieselOn ? `${f1(fuelLitres(executed))} L` : `${f1(fuelLitres(SOLVER.dieselMinKw))} L`],
    ],
  })

  const absNet = Math.abs(net)
  ladder.push({
    key: 'renew',
    title: 'Use of renewables and the battery (J4 curtailment)',
    tag: 'PRIORITY 5',
    verdict: 'ok',
    text: mode === 'DIESEL_CHARGE'
      ? `Generation exceeds load by ${f1(net)} kW; the surplus goes into the battery (×${SOLVER.eta} round-trip loss) = +${f1(net * SOLVER.eta)} kWh stored.`
      : mode === 'RENEW_CHARGE'
        ? `Surplus of ${f1(net)} kW is stored (+${f1(net * SOLVER.eta)} kWh after losses) instead of being curtailed.`
        : mode === 'DISCHARGE'
          ? `Load exceeds supply by ${f1(absNet)} kW; the battery covers it (−${f1(absNet / SOLVER.eta)} kWh drawn including losses).`
          : mode === 'DIESEL_SUPPORT'
            ? `Diesel plus renewables fall ${f1(absNet)} kW short of the load; the battery makes up the difference.`
            : `Supply and demand are balanced within ±0.5 kW; the battery stays idle.`,
    facts: [
      ['Battery net', `${net >= 0 ? '+' : ''}${f1(net)} kW`],
      ['Energy change', `${f1((socEnd - socStart) * 2)} kWh`],
    ],
  })

  return {
    mode, driver, headline, short,
    socStart, socEnd, eStart, aboveFloor, demandNow, planned, executed, net,
    startedNow, stoppedNow, ladder, traj,
    stats: { windAll, solar3, dem3, solarAll, demAll, coverAll, deficitAll, floorStep, peak, solarCoversStep, noSolar },
  }
}

// Lightweight per-hour summary for the decision log (avoids building the full ladder).
export function summarizeHour(series, i, scenarioId) {
  const x = explainHour(series, i, scenarioId)
  return x ? { mode: x.mode, driver: x.driver, short: x.short } : null
}


// ---------------------------------------------------------------------------
// REAL reasoning from the full decision trace (scratch/run_scenario2_full_trace.py).
// Everything here is the solver's own plan and inputs -- nothing is inferred.
// ---------------------------------------------------------------------------
const sumA = (a, n = a.length) => a.slice(0, n).reduce((x, y) => x + y, 0)

export function explainFromTrace(rec) {
  if (!rec) return null
  const { state, inputs, reserve, plan, objectives: ob, executed: ex } = rec
  const socStart = state.soc_before_pct
  const eStart = state.energy_before_kwh
  const aboveFloor = Math.max(0, eStart - SOLVER.floorKwh)
  const executed = ex.diesel_kw
  const planned = ex.planned_diesel_kw
  const net = ex.net_surplus_kw
  const demandNow = ex.demand_kw
  const socEnd = ex.soc_after_pct

  const n = plan.diesel_kw.length
  const traj = Array.from({ length: n }, (_, j) => ({
    j,
    solar: inputs.solar_kw[j],
    wind: inputs.wind_kw[j],
    demand: inputs.demand_kw[j],
    diesel: plan.diesel_kw[j],
    socPlan: plan.soc_pct[j],
    curtail: plan.curtail_kw[j],
  }))

  const solar3 = sumA(inputs.solar_kw, 3), wind3 = sumA(inputs.wind_kw, 3), dem3 = sumA(inputs.demand_kw, 3)
  const solarAll = sumA(inputs.solar_kw), windAll = sumA(inputs.wind_kw), demAll = sumA(inputs.demand_kw)
  const solarUsed = sumA(plan.solar_used_kw), windUsed = sumA(plan.wind_used_kw)
  const curtailAll = sumA(plan.curtail_kw)
  const dieselKwh = sumA(plan.diesel_kw)
  const peak = traj.reduce((m, s) => (s.solar > m.solar ? s : m), { solar: 0, j: 0 })
  const noSolar = solarAll < 5
  const firstDiesel = plan.first_diesel_step
  const blockStarts = plan.diesel_block_starts
  const dieselHours = plan.diesel_hours_planned
  const minSoc = Math.min(...plan.soc_pct)
  const minSocStep = plan.soc_pct.indexOf(minSoc)
  const endEnergyPlan = (plan.soc_pct[n - 1] / 100) * SOLVER.capacityKwh
  const requiredEnd = reserve.required_energy_kwh[n - 1]
  const requiredMid = reserve.required_energy_kwh[0]
  const termBinding = requiredEnd > requiredMid + 1 && endEnergyPlan <= requiredEnd + 1.5
  const termLift = requiredEnd - eStart
  const unmetAll = sumA(plan.unmet_kw)
  const shortfall = sumA(plan.reserve_shortfall_kwh)
  const autonomyH = demandNow > 0 ? aboveFloor / (demandNow / SOLVER.eta) : Infinity

  const dieselOn = executed > 0
  let mode
  if (dieselOn) mode = net > 0.5 ? 'DIESEL_CHARGE' : 'DIESEL_SUPPORT'
  else if (net > 0.5) mode = 'RENEW_CHARGE'
  else if (net < -0.5) mode = 'DISCHARGE'
  else mode = 'HOLD'
  const startedNow = ex.generator_started
  const stoppedNow = !dieselOn && state.diesel_running_before

  const solarNote = noSolar
    ? 'The forecast has no solar in this window.'
    : `Solar is in the plan: ${f0(solarUsed)} kWh used over 24 steps (peak ${f1(peak.solar)} kW at +${peak.j})${curtailAll > 0.5 ? `, ${f0(curtailAll)} kWh curtailed` : ', none wasted'}.`

  let driver, headline, short
  if (unmetAll > 0.01 || ob.j1_wh > 0) {
    driver = 'UNSERVED'
    headline = `Even with every resource the plan cannot serve all load (${f1(unmetAll)} kWh unmet). Diesel is used to limit that. ${solarNote}`
    short = `Unmet load in plan · diesel ${f0(executed)} kW`
  } else if (dieselOn) {
    if (shortfall > 0.01) {
      driver = 'RESERVE'
      headline = `The reserve target cannot be fully met even with this run (${f1(shortfall)} kWh short). Reserve outranks fuel, so diesel runs at ${f1(executed)} kW. ${solarNote}`
      short = `Diesel ${f0(executed)} kW · reserve short`
    } else if (minSoc <= 20.5 && minSocStep <= 8) {
      driver = 'FLOOR'
      headline = `Without this run the battery would be driven to the 20% floor by step +${minSocStep}. Diesel starts now at ${f1(executed)} kW (plan: ${dieselHours} diesel hours in ${blockStarts} block${blockStarts === 1 ? '' : 's'}, ${f0(ob.j3_litres)} L). ${solarNote}`
      short = `Diesel ${f0(executed)} kW · floor in ${minSocStep} h`
    } else if (termBinding) {
      driver = 'TERMINAL'
      headline = `The plan must finish the 24 h at ${f0(requiredEnd)} kWh (${f0(requiredEnd / 2)}%), ${f0(Math.max(0, termLift))} kWh above where it started, and forecast solar + wind (${f0(solarAll + windAll)} kWh) do not cover demand (${f0(demAll)} kWh) plus that lift. Diesel runs ${dieselHours} h in ${blockStarts} block${blockStarts === 1 ? '' : 's'}, starting now. ${solarNote}`
      short = `Diesel ${f0(executed)} kW · end-of-day target +${f0(Math.max(0, termLift))} kWh`
    } else {
      driver = 'ENERGY_BUDGET'
      headline = `Supply (solar + wind ${f0(solarAll + windAll)} kWh) falls short of demand (${f0(demAll)} kWh) over 24 h, so the plan schedules ${dieselHours} diesel hours and begins now at ${f1(executed)} kW. ${solarNote}`
      short = `Diesel ${f0(executed)} kW · energy shortfall`
    }
  } else if (mode === 'RENEW_CHARGE') {
    driver = 'SURPLUS'
    headline = `Renewables exceed demand by ${f1(net)} kW, so the battery charges for free; ${firstDiesel == null ? 'the plan needs no diesel at all in 24 h' : `the plan's first diesel is not until +${firstDiesel}`}. ${solarNote}`
    short = `Charging +${f1(net)} kW from surplus`
  } else if (firstDiesel == null) {
    driver = 'NO_DIESEL_NEEDED'
    headline = `The plan runs the whole 24 h without diesel: battery plus solar and wind are enough (lowest planned SOC ${f0(minSoc)}%). ${solarNote}`
    short = 'No diesel needed in 24 h'
  } else {
    driver = 'DEFERRED'
    headline = `The plan postpones diesel to step +${firstDiesel}: until then the battery, solar and wind carry the load (planned SOC falls to ${f0(plan.soc_pct[Math.max(0, firstDiesel - 1)])}%). Same fuel cost later, and the plan is re-solved every hour. ${solarNote}`
    short = `No diesel · plan starts it at +${firstDiesel}`
  }

  const ladder = []
  ladder.push({
    key: 'state', title: 'Where is the battery?', tag: 'STATE', verdict: autonomyH < 1.5 ? 'warn' : 'ok',
    text: `Start of hour: ${f1(socStart)}% = ${f1(eStart)} kWh, ${f1(aboveFloor)} kWh above the 20% floor — about ${Number.isFinite(autonomyH) ? f1(autonomyH) : '∞'} h of the current ${f1(demandNow)} kW load.`,
    facts: [['SOC (start → end)', `${f1(socStart)}% → ${f1(socEnd)}%`], ['Usable above floor', `${f1(aboveFloor)} kWh`], ['Generator before', state.diesel_running_before ? 'running' : 'off']],
  })
  ladder.push({
    key: 'forecast', title: 'What did the solver expect from the next 24 h?', tag: 'INPUTS',
    verdict: noSolar ? 'warn' : 'ok',
    text: `Forecast solar ${f1(solar3)} kWh, wind ${f1(wind3)} kWh vs demand ${f1(dem3)} kWh in the next 3 steps; over 24 steps solar ${f0(solarAll)} kWh, wind ${f0(windAll)} kWh vs demand ${f0(demAll)} kWh. ${solarNote}`,
    facts: [['Solar 3 / 24 steps', `${f1(solar3)} / ${f0(solarAll)} kWh`], ['Wind 3 / 24 steps', `${f1(wind3)} / ${f0(windAll)} kWh`], ['Demand 3 / 24 steps', `${f1(dem3)} / ${f0(demAll)} kWh`]],
  })
  ladder.push({
    key: 'safety', title: 'Is any load at risk? (J1 critical → J1b non-critical)', tag: 'PRIORITY 1–2',
    verdict: unmetAll > 0.01 ? 'warn' : 'ok',
    text: unmetAll > 0.01
      ? `The plan leaves ${f1(unmetAll)} kWh of load unserved (J1 ${f1(ob.j1_wh)} Wh, J1b ${f1(ob.j1b_wh)} Wh).`
      : `The plan serves all critical and non-critical load in all 24 steps (J1 = ${f0(ob.j1_wh)}, J1b = ${f0(ob.j1b_wh)}). Lowest planned SOC is ${f1(minSoc)}% at step +${minSocStep}.`,
    facts: [['J1 / J1b', `${f0(ob.j1_wh)} / ${f0(ob.j1b_wh)} Wh`], ['Lowest planned SOC', `${f1(minSoc)}% (+${minSocStep})`], ['Binding constraints', rec.binding_constraints.length ? rec.binding_constraints.join(', ') : 'none']],
  })
  ladder.push({
    key: 'reserve', title: 'Reserve and end-of-horizon energy (J2)', tag: 'PRIORITY 3',
    verdict: shortfall > 0.01 ? 'warn' : termBinding ? 'action' : 'ok',
    text: `EBR target ${f1(reserve.ebr_target_kwh)} kWh (minus the ${f0(reserve.deadband_kwh)} kWh deadband). The plan must also hold ${f1(requiredEnd)} kWh at step +${n - 1}: that is ${f1(eStart)} kWh start + ${f0(reserve.floor_kwh)} kWh floor offset − ${f0(reserve.deadband_kwh)} kWh deadband, i.e. ${f1(termLift)} kWh ${termLift >= 0 ? 'above' : 'below'} the starting energy. The plan ends at ${f1(endEnergyPlan)} kWh — ${termBinding ? 'exactly on that requirement, so the rule is driving diesel' : 'comfortably clear of it'}. Reserve shortfall: ${f1(shortfall)} kWh.`,
    facts: [['Required at +' + (n - 1), `${f1(requiredEnd)} kWh`], ['Plan ends at', `${f1(endEnergyPlan)} kWh`], ['J2 shortfall', `${f1(ob.j2_wh / 1000)} kWh`]],
  })
  const fuelNow = executed > 0 ? SOLVER.fuelBaseLh + SOLVER.fuelMargLkwh * executed : 0
  ladder.push({
    key: 'fuel', title: 'Diesel schedule in the plan (J3 fuel)', tag: 'PRIORITY 4', verdict: dieselOn ? 'action' : 'ok',
    text: `Plan total: ${f0(dieselKwh)} kWh of diesel over ${dieselHours} h in ${blockStarts} block${blockStarts === 1 ? '' : 's'} = ${f1(ob.j3_litres)} L${dieselKwh > 0 ? ` (${(ob.j3_litres / dieselKwh).toFixed(2)} L/kWh)` : ''}. ${dieselOn ? `${startedNow ? 'Generator starts now (+2 L start-up). ' : 'Generator keeps running. '}This hour: ${f1(executed)} kW burning ${f1(fuelNow)} L.` : firstDiesel == null ? 'No diesel is planned at all.' : `First planned run is at step +${firstDiesel}.`}`,
    facts: [['Planned diesel now', `${f1(planned)} kW`], ['Planned diesel hours', `${dieselHours} h`], ['Plan fuel', `${f1(ob.j3_litres)} L`]],
  })
  const unserved = ex.physics_unserved_kwh, curt = ex.physics_curtailed_kwh
  ladder.push({
    key: 'renew', title: 'How this hour actually played out', tag: 'OUTCOME', verdict: unserved > 0.01 ? 'warn' : 'ok',
    text: `Actual solar ${f1(ex.actual_solar_kw)} kW + wind ${f1(ex.wind_kw)} kW + diesel ${f1(executed)} kW vs demand ${f1(demandNow)} kW → battery ${net >= 0 ? '+' : ''}${f1(net)} kW. SOC ${f1(socStart)}% → ${f1(socEnd)}% (plan expected ${f1(plan.soc_pct[0])}%).${unserved > 0.01 ? ` Battery hit the floor: ${f1(unserved)} kWh would have gone unserved.` : ''}${curt > 0.01 ? ` Battery hit the ceiling: ${f1(curt)} kWh curtailed.` : ''}`,
    facts: [['Plan SOC after', `${f1(plan.soc_pct[0])}%`], ['Actual SOC after', `${f1(socEnd)}%`], ['Unserved (physics)', `${f1(unserved)} kWh`]],
  })

  return {
    source: 'trace', mode, driver, headline, short,
    socStart, socEnd, eStart, aboveFloor, demandNow, planned, executed, net,
    startedNow, stoppedNow, ladder, traj,
    stats: { solarAll, windAll, demAll, noSolar, peak, firstDiesel },
    viz: {
      aboveFloor, autonomyH, solarAll, windAll, demAll, minSoc, minSocStep, requiredEnd, endEnergyPlan, termBinding, termLift,
      shortfall, dieselOn, executed, fuelNow, dieselHours, blockStarts, firstDiesel, unmetAll, litresPlan: ob.j3_litres, peak,
    },
  }
}
