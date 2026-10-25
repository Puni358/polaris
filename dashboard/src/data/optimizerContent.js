// Content for the "Optimizer" tab: the GAP19 optimizer, the five lexicographic priorities, and the feedback loop.
// Facts come from gap19_highs_native.py, the EMS specification reviews (GAP_19), and the scenario scripts.

export const O_STEPS = [
  { id: 1, label: 'What goes in' },
  { id: 2, label: 'The puzzle' },
  { id: 3, label: 'Five priorities' },
  { id: 4, label: 'The plan' },
  { id: 5, label: 'Feedback loop' },
]

export const O_NODE_STEP = { inp: 1, unk: 2, rules: 2, j1: 3, j1b: 3, j2: 3, j3: 3, j4: 3, plan: 4, act: 4, meas: 5, err: 5, fc: 5 }
export const O_STEP_NODE = { 1: 'inp', 2: 'unk', 3: 'j1', 4: 'plan', 5: 'err' }

export const GAP_NAME = {
  title: 'Why is it called “GAP 19”?',
  text: 'While specifying the energy-management system, the open design questions were numbered as “gaps”. GAP 19 was the question “How should the solver realise the priority order?” (one-after-another passes, or solver-native lexicographic optimization). The optimizer is the answer to that gap, so it carries its number: GAP19 + HiGHS, the open-source solver that runs it.',
}

export const O_NODES = {
  inp: {
    title: 'What the optimizer is given',
    plain: 'Every hour it receives the next 24 hours of solar, wind and demand, the battery reserve it must keep, and the battery’s level right now.',
    facts: ['24 hours ahead', 'battery level measured now'],
    blocks: [
      ['Solar', 'The forecaster’s 24-hour sunshine, converted to power: min( W/m² × 51 W per W/m², 60 kW ).'],
      ['Wind and demand', 'Known formulas in this simulation (not forecast), the same for every scenario we compare.'],
      ['Reserve target', 'From the forecaster’s 90% safety bound: never below 15 kWh. Priority J2 protects it.'],
      ['Battery now', 'The measured energy in the battery at the start of the hour. This is the number that closes the feedback loop.'],
    ],
  },
  unk: {
    title: '432 unknowns to decide',
    plain: 'For each of the 24 hours it must decide how every source and the battery behave. That is 18 decisions per hour: 432 in total.',
    facts: ['24 hours × 18', '96 of them are yes/no switches'],
    blocks: [
      ['Decided every hour', 'solar used · wind used · solar wasted · wind wasted\nbattery charge · battery discharge · battery energy afterwards\ndiesel power · load served · load not served · flexible load'],
      ['The yes/no switches', 'charging on? · discharging on? · diesel on? · diesel starting?\nThe diesel switch is why this is a mixed-integer puzzle (MILP): a generator is either off or running at 10 kW or more.'],
      ['Extra unknowns', 'unserved critical load, unserved non-critical load and reserve shortfall for each hour.'],
    ],
  },
  rules: {
    title: '336 rules it may not break',
    plain: 'The physics and the limits of the equipment. Every plan has to obey all of them.',
    facts: ['physics', 'equipment limits', 'reserve'],
    blocks: [
      ['Energy balance', 'solar used + wind used + diesel + battery discharge = load served + battery charge + flexible load'],
      ['Battery', 'energy next hour = energy now + 0.92 · charge − discharge ÷ 0.92\n20% ≤ battery ≤ 95% of 200 kWh · charge and discharge ≤ 50 kW · never both at once'],
      ['Diesel', 'power is 0, or between 10 kW and 100 kW · every start is counted'],
      ['Reserve', 'energy next hour + shortfall ≥ reserve target + 40 kWh (the 20% floor)'],
    ],
  },
  j1: {
    title: 'J1 — Critical load',
    plain: 'First priority. Never leave the critical load without power.',
    facts: ['priority 1 of 5', 'unit: Wh not served', 'goal: zero'],
    blocks: [
      ['What it measures', 'The energy (Wh) of critical demand that the plan fails to serve. Critical load is a protected 15 kW at all times.'],
      ['How it is solved', 'The solver first minimizes J1 on its own. Once the best value is found, it is locked: no lower priority may make it worse.'],
      ['In practice', 'The optimizer will burn diesel to protect critical load. It will never shed critical load to save fuel.'],
    ],
  },
  j1b: {
    title: 'J1b — Non-critical load',
    plain: 'Second priority. Keep comfort and other non-critical loads on, as long as that does not endanger J1.',
    facts: ['priority 2 of 5', 'unit: Wh not served'],
    blocks: [
      ['What it measures', 'The energy of non-critical demand (everything above the 15 kW protected floor) that the plan fails to serve.'],
      ['Why it exists', 'Added later as a fix. Without it, the solver had no reason to serve non-critical load once J1 and the reserve were met, and would drop it for free rather than spend a litre of fuel.'],
      ['Result in our year', '0.0 kWh of non-critical load was shed in all 8,328 hours.'],
    ],
  },
  j2: {
    title: 'J2 — Battery reserve',
    plain: 'Third priority. Keep the safety cushion the forecaster asked for, and finish the 24-hour plan at a healthy battery level.',
    facts: ['priority 3 of 5', 'unit: Wh short of the reserve'],
    blocks: [
      ['What it measures', 'How far the battery falls short of the required reserve, summed over the 24 hours. The reserve comes from the forecaster’s uncertainty (never below 15 kWh).'],
      ['End-of-day rule', 'At the last hour of the plan the target also includes the starting battery level, so each plan finishes where it started (less the 10 kWh deadband).'],
      ['Why it ranks above fuel', 'A reserve shortfall can mean a blackout one cloudy night later, so the optimizer will pay for diesel to avoid it.'],
    ],
  },
  j3: {
    title: 'J3 — Diesel fuel',
    plain: 'Fourth priority. With every protection above locked, use the least fuel possible.',
    facts: ['priority 4 of 5', 'unit: litres'],
    blocks: [
      ['What it measures', 'Litres of diesel over the 24-hour plan.'],
      ['The fuel curve', 'litres = 5 L per running hour + 0.25 L per kWh + 2 L for every start\nThe 5 L per hour is why running hard in short blocks beats idling.'],
      ['Why it is only fourth', 'Fuel is the thing we want to save, but never at the price of load or reserve.'],
    ],
  },
  j4: {
    title: 'J4 — Curtailment',
    plain: 'Last priority. Waste as little solar and wind as possible.',
    facts: ['priority 5 of 5', 'unit: Wh wasted'],
    blocks: [
      ['What it measures', 'Renewable energy that is thrown away because the battery is full and the load is already met.'],
      ['Why last', 'Wasted sun costs nothing in fuel or safety, so it only breaks ties once everything else is settled.'],
    ],
  },
  plan: {
    title: 'The 24-hour plan',
    plain: 'The result is a complete schedule for the next 24 hours: what every source does, hour by hour.',
    facts: ['24 steps', 'optimal for all five priorities in order'],
    blocks: [
      ['How the priorities are enforced', 'HiGHS runs in lexicographic mode with blending switched off. Each objective is solved in order, and the previous optimum is held with zero tolerance, so a lower priority can never degrade a higher one.'],
      ['Why not one weighted sum?', 'A weighted sum can trade a little critical load for a lot of fuel. Strict priorities cannot.'],
    ],
  },
  act: {
    title: 'Carry out hour 1 only',
    plain: 'Only the first hour of the plan is carried out. The other 23 hours are advice that is thrown away and re-planned next hour.',
    facts: ['rolling horizon', 'one hour committed'],
    blocks: [
      ['Why only one hour', 'The forecast for hour 12 is less reliable than the one for hour 1. By the time hour 2 arrives, the optimizer will know more, so it plans again.'],
      ['Station update', 'surplus = solar + wind + diesel − demand\nbattery ← battery + 0.92 · surplus (or − |surplus| ÷ 0.92 when negative), kept between 20% and 95%'],
    ],
  },
  meas: {
    title: 'The station is measured',
    plain: 'After the hour, the real battery level is read. It is the result of the real sunshine and the real demand, not the forecast.',
    facts: ['real battery level'],
    blocks: [['Why it matters', 'If the sun was weaker than forecast, the battery ends lower than the plan expected. The measurement carries that surprise.']],
  },
  err: {
    title: 'Plan versus reality',
    plain: 'The plan said the battery would be at one level; the measurement says another. The difference is the error, and the next plan starts from the real level.',
    facts: ['error-correcting', 'every hour'],
    blocks: [
      ['What “feedback” means here', 'Every hour: measure → compare with what the plan expected → plan again from the measured state. The gap between plan and reality is never allowed to build up.'],
      ['Technical name', 'This is negative feedback: it reduces error. (Positive feedback would amplify it.) Closed-loop control with a receding horizon.'],
      ['What we do not claim', 'The optimizer does not retrain itself. It corrects by always starting from the measured state. The forecaster learns from yesterday’s weather only through its “station memory” inputs, refreshed every midnight.'],
    ],
    chart: 'day',
  },
  fc: {
    title: 'Back to the forecaster, every midnight',
    plain: 'Once a day the forecaster receives the last 24 hours of real sunshine readings and makes a fresh 24-hour forecast.',
    facts: ['every 00:00 UTC'],
    blocks: [['How the error reaches the forecaster', 'The 14 station-memory inputs are built from the previous day’s measurements, so a cloudier-than-expected day changes tomorrow’s forecast.']],
  },
}
