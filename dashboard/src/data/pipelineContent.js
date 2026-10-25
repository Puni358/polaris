// Everything the Pipeline tab shows when a box is clicked. Every formula below is taken from the
// repository code (n6_solar.py, adapters.py, gap19_highs_native.py, sim_inputs.py) or its audit reports.

export const TAGS = {
  real: { label: 'REAL MEASUREMENT', cls: 'bg-emerald-900/70 text-emerald-300' },
  issued: { label: 'FORECAST ISSUED EARLIER', cls: 'bg-amber-900/70 text-amber-300' },
  computed: { label: 'COMPUTED IN ADVANCE', cls: 'bg-violet-900/70 text-violet-300' },
  sim: { label: 'SIMULATION FORMULA', cls: 'bg-sky-900/70 text-sky-300' },
  model: { label: 'MODEL OUTPUT', cls: 'bg-cyan-900/70 text-cyan-300' },
  pending: { label: 'OWNER DECISION PENDING', cls: 'bg-rose-900/70 text-rose-300' },
}

const f = (name, tag) => ({ name, tag })

export const NODES = {
  sun: {
    title: 'Sun & calendar', count: 5, tag: 'computed',
    summary: 'Where the sun is, and how bright a cloudless sky would be. Known long before the forecast.',
    features: [f('month', 'computed'), f('hour', 'computed'), f('solar_elevation', 'computed'), f('solar_zenith', 'computed'), f('clearsky_ghi', 'computed')],
    formulas: [
      ['Sun position', 'elevation = pvlib solar position (SPA) at Nuolja, 68.362°N 18.739°E\nzenith = 90° − elevation'],
      ['Clear-sky light', 'clearsky_ghi = pvlib Ineichen clear-sky model (Linke turbidity)'],
    ],
  },
  station: {
    title: 'Station memory', count: 14, tag: 'real',
    summary: 'The last 24 hours of real sunshine readings from the Nuolja pyranometer. Only readings before the forecast time.',
    features: ['ctx_std_3h', 'ctx_std_6h', 'ctx_std_12h', 'ctx_std_24h', 'ctx_abs_change_1h', 'ctx_abs_change_3h', 'ctx_abs_change_6h', 'ctx_max_diff_6h', 'ctx_mean_diff_6h', 'ctx_slope_6h', 'ctx_kt_std_6h', 'ctx_last_obs', 'ctx_mean_24h', 'ctx_max_24h'].map((n) => f(n, 'real')),
    formulas: [
      ['Spread', 'ctx_std_N = standard deviation of SW_IN over [t0 − N h, t0),  N = 3, 6, 12, 24'],
      ['Changes', 'ctx_abs_change_1h = |SW[t0−1] − SW[t0−2]|\nctx_abs_change_3h = |SW[t0−1] − SW[t0−4]|\nctx_abs_change_6h = |SW[t0−1] − SW[t0−7]|'],
      ['Trend', 'ctx_slope_6h = OLS slope of SW_IN over the last 6 h\nctx_kt_std_6h = std of kt over the last 6 h,  kt = SW_IN ÷ clearsky_ghi'],
      ['Level', 'ctx_last_obs = SW[t0−1]\nctx_mean_24h, ctx_max_24h = mean and max over [t0 − 24 h, t0)'],
    ],
  },
  terrain: {
    title: 'Mountain shading', count: 4, tag: 'computed', star: true,
    summary: 'Built for this station: a 360° terrain profile tells the model when a mountain blocks the sun.',
    features: ['terrain_horizon_elevation_deg', 'terrain_elevation_margin_deg', 'terrain_solar_obstruction_flag', 'clearsky_ghi_terrain_adjusted'].map((n) => f(n, 'computed')),
    formulas: [
      ['Horizon angle', 'terrain_horizon_elevation_deg = horizon angle from a 360° terrain model (DEM ray-tracing)\nat the sun’s azimuth ψ'],
      ['Margin', 'terrain_elevation_margin_deg = solar_elevation − terrain_horizon_elevation_deg'],
      ['Blocked flag', 'terrain_solar_obstruction_flag = 1 if the sun is at or below the horizon line, else 0'],
      ['Adjusted light', 'clearsky_ghi_terrain_adjusted = clearsky_ghi × (1 − obstruction_flag)'],
    ],
  },
  nwp: {
    title: 'Weather forecast', count: 9, tag: 'issued',
    summary: 'MET Norway’s 18:00 UTC model run of the day before, published about 20:15 UTC, so it is known 3 h 45 min before the 00:00 forecast. Lead = 5 + h hours.',
    features: [f('fc_cloud_cover', 'issued'), f('fc_temperature_2m', 'issued'), f('fc_relative_humidity_2m', 'issued'), f('cloud_frac', 'issued'), f('u700', 'issued'), f('v700', 'issued'), f('lwp_18z_fc', 'issued'), f('iwp_18z_fc', 'issued'), f('lwp_x_cloud_18z', 'issued')],
    formulas: [
      ['Cloud fraction', 'cloud_frac = fc_cloud_cover ÷ 100'],
      ['Cloud water', 'lwp_x_cloud_18z = lwp_18z_fc × cloud_frac'],
      ['Timing', 'model run 18:00 UTC (day D−1) → published ≈ 20:15 UTC → forecast made 00:00 UTC (day D)\nvalid time of step h = run time + (5 + h) hours'],
    ],
  },
  combined: {
    title: 'Combined clues', count: 4, tag: 'computed',
    summary: 'Clues built from the others: a physics baseline and cloud-sun interactions.',
    features: [f('elevation_x_cloud_frac', 'computed'), f('elevation_x_transition_cloud', 'computed'), f('pred_stage4_clean', 'computed'), f('clean_attenuation', 'computed')],
    formulas: [
      ['Interactions', 'elevation_x_cloud_frac = solar_elevation × cloud_frac\nelevation_x_transition_cloud = solar_elevation × 1{ 0.2 ≤ cloud_frac < 0.6 }'],
      ['Baseline', 'pred_stage4_clean = w_h · Chronos-2 forecast + (1 − w_h) · phys\nphys = max(0, clearsky_ghi · (1 − k_h · cloud_frac))'],
      ['Attenuation', 'clean_attenuation = clearsky_ghi − pred_stage4_clean'],
    ],
  },
  clues: {
    title: '36 clues', count: 36, tag: 'computed',
    summary: 'Five families of numbers per forecast hour: 5 sun & calendar + 14 station memory + 4 mountain shading + 9 weather forecast + 4 combined.',
    features: [], formulas: [
      ['Safety check', 'The forecaster rejects any input that contains the real outcome (actual_SW_IN, residual_target, …).\nIt stops instead of guessing: “fail closed”.'],
    ],
  },
  n6: {
    title: 'POLARIS N6 forecaster', count: 40, tag: 'model',
    summary: '40 models vote: 25 additive models and 15 clearness-ratio specialists. Output: the next 24 hours of solar light.',
    features: [],
    formulas: [
      ['25 additive models', 'ŷ_add = mean over 25 models of  max(0, baseline + m(x))'],
      ['15 clearness-ratio specialists', 'ŷ_kt = mean over 15 models of  clip( baseline + m(x) · (clearsky_terrain + ε),  0,  max(1.25 · clearsky, baseline) )'],
      ['Blend', 'w = α(elevation) · (1 if the sun is not blocked, else 0)\nα = w_max · clip( (elevation − e_start) ÷ (e_full − e_start), 0, 1 )\nŷ = (1 − w) · ŷ_add + w · ŷ_kt\nŷ = 0 when the sun is below the horizon'],
      ['Refreshed', 'A new forecast is made every midnight (00:00 UTC) from the last 24 h of real readings.'],
    ],
  },
  bound: {
    title: '90% safety bound', count: null, tag: 'model',
    summary: 'How unsure the 40 models are decides how much battery is held back.',
    features: [],
    formulas: [
      ['Spread', 'scale = std of the 40 model outputs + 0.10 · clearsky_terrain + 5 W/m²'],
      ['Lower bound', 'ŷ_low = max(0, ŷ − 1.859 · scale)      (split-conformal, 90% one-sided)'],
      ['Battery reserve', 's_hour = k_pv · scale ÷ 0.95\nscale_6h(t) = Σ s_hour over the next 6 h + 100 Wh\nreserve(t) = max( 15 kWh,  1.5702 · scale_6h(t) )'],
    ],
  },
  bundle: {
    title: 'Hand-off to the optimizer', count: null, tag: 'model',
    summary: 'Everything the optimizer reads for the next 24 hours.',
    features: [],
    formulas: [
      ['Solar power', 'solar_kW = min( sunshine_W/m² · 51 W per W/m²,  60 kW )\n51 = 300 m² × 0.20 efficiency × 0.85 performance ratio'],
      ['Wind & demand', 'Not forecast: simulation formulas, known exactly for the next 24 h.\nwind = 15 kW + 10 kW · sin(hour · π ÷ 6)\ndemand = governed daily profile × season factor, kept between 15 and 45 kW'],
      ['Critical load', '15 kW protected at all times'],
    ],
    note: 'Only solar is predicted. Wind and demand are simulation inputs that the optimizer is given exactly.',
  },
  shift: {
    title: 'The gate: checks, and why 00:00–23:00 becomes 01:00–24:00', count: null, tag: 'computed', wide: true,
    summary: 'The forecaster labels its 24 values 00:00 … 23:00. The optimizer reads them as the hours 01:00 … 24:00. This is deliberate.',
    features: [],
    formulas: [
      ['Checks at the gate', 'exactly 24 hourly steps  ·  power in watts  ·  no negative values  ·  critical load never above total demand\nIf any check fails the optimizer refuses the input (fail closed).'],
      ['Why', 'The optimizer’s step 0 moves the station across the NEXT hour, [t0, t0 + 1 h].\nThat hour is checked against the real value stamped t0 + 1 h.\nA forecast stamped t0 would sit one hour behind the hour it is meant to predict.'],
      ['The shift', 'optimizer step k  ←  forecast value stamped t0 + (k + 1) h,   k = 0 … 22\n(value stamped 01:00 → step 0, … , value stamped 23:00 → step 22)'],
      ['What is left over', 'Step 23 (the hour ending 24:00) has no forecast value, so it is filled:'],
      ['Fill rule in use (C.2 clear-sky ratio)', 'ratio = min( P₂₃ ÷ (cs₂₃ · 51),  1.2 )\nstep 23 = ratio · cs₂₄ · 51,  capped at 60 kW\nif cs₂₃ · 51 < 255 W:  step 23 = cs₂₄ · 51'],
      ['Frozen alternative', 'Decision register OD-02: step 23 = 0 (zero fallback).'],
    ],
    note: 'Only step 0 is ever carried out, so step 23 never reaches the station. Which fill rule is official is an owner decision that is still pending.',
    pendingTag: true,
  },
  wind: {
    title: 'Wind & demand', count: null, tag: 'sim',
    summary: 'Simulation inputs given to the optimizer exactly, the same for every scenario we compare.',
    features: [],
    formulas: [
      ['Wind', 'wind(t) = 15 kW + 10 kW · sin( hour_of_day(t) · π ÷ 6 )'],
      ['Demand', 'demand(t) = clip( daily_profile(hour) × season(month),  15 kW,  45 kW )\ndaily_profile: 18 kW (00–05), 22, 30, 38 (08:00 peak), 32 (09–17), 36, 42 (19:00 peak), 30, 30, 22\nseason: 1.20 in Nov–Feb, 0.85 in May–Aug, 1.00 otherwise'],
    ],
  },
  opt: {
    title: 'GAP19 optimizer', count: null, tag: 'model',
    summary: 'Plans the next 24 hours as a puzzle with 432 unknowns and 336 rules, solving the priorities one after another.',
    features: [],
    formulas: [
      ['Priority order', '1  J1   critical load not served (minimize first)\n2  J1b  non-critical load not served\n3  J2   battery reserve shortfall\n4  J3   diesel fuel (litres)\n5  J4   renewable energy thrown away'],
      ['Battery', 'E[t+1] = E[t] + 0.92 · charge − discharge ÷ 0.92\n20% ≤ battery ≤ 95% of 200 kWh,  charge and discharge ≤ 50 kW'],
      ['Diesel', 'power = 0, or 10 … 100 kW\nfuel = 5 L/h + 0.25 L/kWh,  plus 2 L for every start'],
      ['Reserve rule', 'E[t+1] + shortfall ≥ reserve(t) + 40 kWh'],
    ],
  },
  act: {
    title: 'What it decided, in kilowatts', count: null, tag: 'model',
    summary: 'Only the first hour of the 24-hour plan is carried out. The ribbons show that real hour: width = kilowatts, solar and wind taken from the data, diesel and battery from the plan.',
    features: [],
    formulas: [
      ['Station update', 'surplus = solar + wind + diesel − demand\nbattery ← battery + 0.92 · surplus   (or − |surplus| ÷ 0.92 when negative)\nkept between 20% and 95%'],
      ['Rolling horizon', 'every HOUR: new battery level → new 24-hour plan → carry out hour 1'],
    ],
  },
}

// The five lexicographic locks of the optimizer, shown one at a time as each priority is solved and clamped.
export const LOCKS = [
  { j: 'J1', name: 'Critical load', short: 'Critical', title: 'Critical Load Protected', formula: 'J₁ ≤ 0', text: 'Enforcing J₁ ≤ 0 (no unserved critical demand).' },
  { j: 'J1b', name: 'Comfort load', short: 'Comfort', title: 'Comfort Load Protected', formula: 'J₁b ≤ J₁b*', text: 'Enforcing J₁b ≤ J₁b* (minimizing comfort deficits without violating J₁).' },
  { j: 'J2', name: 'Safety cushion', short: 'Reserve', title: 'Conformal Reserve Clamped', formula: 'J₂ ≤ J₂*', text: 'Enforcing J₂ ≤ J₂* (battery buffer strictly maintained against weather uncertainty).' },
  { j: 'J3', name: 'Diesel fuel', short: 'Diesel', title: 'Diesel Fuel Minimized', formula: 'J₃ ≤ J₃*', text: 'Enforcing J₃ ≤ J₃* (lowest possible fuel burn given the J₁–J₂ locks).' },
  { j: 'J4', name: 'Wasted sun', short: 'Curtailment', title: 'Curtailment Minimized', formula: 'J₄ minimized', text: 'Final execution plan locked. (Renewable spillage minimized.)' },
]

// Which chapter owns which box, and which box the inspector shows when a chapter opens.
export const NODE_STEP = { sun: 1, station: 1, terrain: 1, nwp: 1, combined: 1, clues: 1, n6: 2, bound: 2, shift: 3, wind: 3, opt: 4, act: 5 }
export const STEP_NODE = { 1: 'clues', 2: 'n6', 3: 'shift', 4: 'opt', 5: 'act' }
export const STEPS = [
  { id: 1, label: 'Inputs & firewall' },
  { id: 2, label: 'Forecaster' },
  { id: 3, label: 'Gate' },
  { id: 4, label: 'Optimizer' },
  { id: 5, label: 'Dispatch & loops' },
]

// ---------------------------------------------------------------------------------------------
// Plain-language detail for every one of the 36 inputs: full name, meaning, how it is calculated,
// where the data comes from (with a link) and when it is available. Source links are the public
// pages of the data providers and libraries named in the repository.
// ---------------------------------------------------------------------------------------------
const L = {
  pvlibPos: ['pvlib solar position (NREL SPA algorithm)', 'https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.solarposition.get_solarposition.html'],
  spa: ['NREL Solar Position Algorithm', 'https://midcdc.nrel.gov/solpos/spa.html'],
  ineichen: ['pvlib Ineichen clear-sky model', 'https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.ineichen.html'],
  sites: ['SITES data portal — Nuolja Middle Station (Abisko)', 'https://data.fieldsites.se'],
  meps: ['MET Norway MEPS forecast archive (THREDDS)', 'https://thredds.met.no/thredds/catalog.html'],
  mepsDocs: ['MET Norway numerical weather prediction documentation', 'https://github.com/metno/NWPdocs/wiki'],
  dem: ['Copernicus DEM GLO-30 (elevation model)', 'https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model'],
  chronos: ['Chronos time-series forecasting models', 'https://github.com/amazon-science/chronos-forecasting'],
}
const src = (k) => ({ label: L[k][0], url: L[k][1] })

export const WHEN = {
  calc: 'Known in advance: calculated from the calendar and the station’s position. No data download needed.',
  station: 'Measured on site: the Nuolja pyranometer logs every 10 minutes. Only readings before the forecast time are used. Works offline.',
  terrain: 'Static: computed once from the elevation model and stored as a file. Works offline.',
  nwp: 'Weather-model run at 18:00 UTC the day before, published about 20:15 UTC. It must be downloaded before the 00:00 UTC forecast (3 h 45 min to spare). Once stored, it works offline.',
  comb: 'Computed at 00:00 UTC from the inputs above. Works offline.',
}

const stationInfo = (full, meaning, how) => ({ full, meaning, how, source: [src('sites')], when: WHEN.station })
const nwpInfo = (full, meaning, how) => ({ full, meaning, how, source: [src('meps'), src('mepsDocs')], when: WHEN.nwp })

export const FEATURE_INFO = {
  month: { full: 'Month of the year', meaning: 'Which month the forecast hour falls in (1 to 12). The sun’s height and the length of the day change through the year.', how: 'month = calendar month of the hour being forecast', source: [], when: WHEN.calc },
  hour: { full: 'Hour of the day (UTC)', meaning: 'Which hour of the day is being forecast (0 to 23). Sunshine follows a daily rise and fall.', how: 'hour = clock hour of the forecast time, in UTC', source: [], when: WHEN.calc },
  solar_elevation: { full: 'Sun elevation angle', meaning: 'How high the sun is above the horizon, in degrees. 0° means on the horizon, 90° straight overhead, negative means night.', how: 'Calculated from the date, time and the station’s position (68.362°N, 18.739°E) with the NREL Solar Position Algorithm.', source: [src('pvlibPos'), src('spa')], when: WHEN.calc },
  solar_zenith: { full: 'Sun zenith angle', meaning: 'The angle between straight up and the sun, in degrees. It is the sun’s distance from the top of the sky.', how: 'zenith = 90° − solar elevation', source: [src('pvlibPos')], when: WHEN.calc },
  clearsky_ghi: { full: 'Clear-sky global horizontal irradiance (W/m²)', meaning: 'How much sunshine power would reach a flat surface if the sky had no clouds at all. It is the ceiling for any forecast.', how: 'pvlib Ineichen clear-sky model, using the sun’s position and an atmospheric haze value (Linke turbidity).', source: [src('ineichen')], when: WHEN.calc },

  ctx_std_3h: stationInfo('Sunshine variability, last 3 hours (W/m²)', 'How much the measured sunshine moved up and down in the last 3 hours. High means flickering clouds.', 'standard deviation of the hourly sunshine readings over [forecast time − 3 h, forecast time)'),
  ctx_std_6h: stationInfo('Sunshine variability, last 6 hours (W/m²)', 'Same measure over the last 6 hours.', 'standard deviation of sunshine over [forecast time − 6 h, forecast time)'),
  ctx_std_12h: stationInfo('Sunshine variability, last 12 hours (W/m²)', 'Same measure over the last 12 hours.', 'standard deviation of sunshine over [forecast time − 12 h, forecast time)'),
  ctx_std_24h: stationInfo('Sunshine variability, last 24 hours (W/m²)', 'Same measure over the whole last day.', 'standard deviation of sunshine over [forecast time − 24 h, forecast time)'),
  ctx_abs_change_1h: stationInfo('Sunshine change over the last hour (W/m²)', 'How much the sunshine changed between the two most recent hours.', '|SW(t0−1) − SW(t0−2)|,  SW = measured sunshine, t0 = forecast time'),
  ctx_abs_change_3h: stationInfo('Sunshine change over the last 3 hours (W/m²)', 'How much the sunshine changed over about 3 hours.', '|SW(t0−1) − SW(t0−4)|'),
  ctx_abs_change_6h: stationInfo('Sunshine change over the last 6 hours (W/m²)', 'How much the sunshine changed over about 6 hours.', '|SW(t0−1) − SW(t0−7)|'),
  ctx_max_diff_6h: stationInfo('Biggest hour-to-hour jump in the last 6 hours (W/m²)', 'The largest single change between two neighbouring hours: a sign of fast-moving clouds.', 'max of |SW(h) − SW(h−1)| over the last 6 hours'),
  ctx_mean_diff_6h: stationInfo('Average hour-to-hour change in the last 6 hours (W/m²)', 'Whether the sunshine has been rising or falling on average.', 'mean of SW(h) − SW(h−1) over the last 6 hours'),
  ctx_slope_6h: stationInfo('Sunshine trend over the last 6 hours (W/m² per hour)', 'The direction and speed of the recent change in sunshine.', 'slope of a straight line fitted (ordinary least squares) to the last 6 hourly readings'),
  ctx_kt_std_6h: stationInfo('Clearness variability, last 6 hours', 'How much the clearness index moved. The clearness index is measured sunshine divided by clear-sky sunshine, so it removes the effect of the sun’s height.', 'standard deviation of kt = SW_IN ÷ clearsky_ghi over the last 6 hours'),
  ctx_last_obs: stationInfo('Most recent measured sunshine (W/m²)', 'The latest reading before the forecast time: the best hint of what the next hour looks like.', 'SW(t0−1), the last hourly reading before the forecast'),
  ctx_mean_24h: stationInfo('Average sunshine over the last 24 hours (W/m²)', 'How sunny the last day was overall.', 'mean of SW over [t0 − 24 h, t0)'),
  ctx_max_24h: stationInfo('Peak sunshine in the last 24 hours (W/m²)', 'The brightest hour of the last day.', 'max of SW over [t0 − 24 h, t0)'),

  terrain_horizon_elevation_deg: { full: 'Mountain horizon height in the sun’s direction (°)', meaning: 'How high the mountains rise above the horizon exactly where the sun is. If the sun is lower than this, the mountain hides it.', how: 'Ray-tracing over a 360° profile from the elevation model, looked up at the sun’s compass direction (azimuth).', source: [src('dem')], when: WHEN.terrain },
  terrain_elevation_margin_deg: { full: 'Sun height above the mountain line (°)', meaning: 'How far the sun is above (positive) or below (negative) the mountain skyline.', how: 'margin = solar elevation − mountain horizon height', source: [src('dem'), src('pvlibPos')], when: WHEN.terrain },
  terrain_solar_obstruction_flag: { full: 'Sun blocked by the mountain? (1 = yes)', meaning: 'A yes/no flag. 1 means the mountain is hiding the sun’s disc at that hour.', how: 'flag = 1 if the sun is at or below the mountain horizon line, otherwise 0', source: [src('dem')], when: WHEN.terrain },
  clearsky_ghi_terrain_adjusted: { full: 'Clear-sky sunshine after mountain shading (W/m²)', meaning: 'The clear-sky ceiling with the mountains taken into account: zero when the sun is blocked.', how: 'clearsky_ghi × (1 − obstruction flag)', source: [src('ineichen'), src('dem')], when: WHEN.terrain },

  fc_cloud_cover: nwpInfo('Forecast total cloud cover (%)', 'How much of the sky the weather model expects to be covered by cloud at the forecast hour.', 'Taken directly from the MEPS model output for the station location.'),
  fc_temperature_2m: nwpInfo('Forecast air temperature at 2 m (°C)', 'Temperature the weather model expects near the ground. It helps the model tell fog, snow and cloud situations apart.', 'Taken directly from the MEPS model output.'),
  fc_relative_humidity_2m: nwpInfo('Forecast relative humidity at 2 m (%)', 'How moist the air near the ground is expected to be. Humid air favours low cloud and haze.', 'Taken directly from the MEPS model output.'),
  cloud_frac: nwpInfo('Cloud fraction (0 to 1)', 'The same cloud cover as a fraction instead of a percentage, ready to multiply with other inputs.', 'cloud_frac = fc_cloud_cover ÷ 100'),
  u700: nwpInfo('Forecast east–west wind at 700 hPa (m/s)', 'The wind about 3 km up (the 700 hPa pressure level) blowing from west to east. It carries clouds towards the station.', 'Taken directly from the MEPS model output.'),
  v700: nwpInfo('Forecast north–south wind at 700 hPa (m/s)', 'The wind at the same height blowing from south to north.', 'Taken directly from the MEPS model output.'),
  lwp_18z_fc: nwpInfo('Forecast cloud liquid water path (g/m²)', 'The amount of liquid water in the cloud above the station. More water means a thicker, darker cloud.', 'Taken directly from the MEPS 18:00 UTC run.'),
  iwp_18z_fc: nwpInfo('Forecast cloud ice water path (g/m²)', 'The amount of ice in the cloud above the station. Ice clouds such as cirrus dim the sun differently from water clouds.', 'Taken directly from the MEPS 18:00 UTC run.'),
  lwp_x_cloud_18z: nwpInfo('Cloud water × cloud fraction', 'Combines how much cloud there is with how thick it is.', 'lwp_x_cloud_18z = lwp_18z_fc × cloud_frac'),

  elevation_x_cloud_frac: { full: 'Sun height × cloud fraction', meaning: 'Clouds block more sunshine when the sun is high, because there is more sunshine to block. This input lets the model see that directly.', how: 'solar_elevation × cloud_frac', source: [src('pvlibPos')], when: WHEN.comb },
  elevation_x_transition_cloud: { full: 'Sun height × “partly cloudy” flag', meaning: 'Partly cloudy skies are the hardest to forecast. This input is the sun’s height when the cloud fraction is between 0.2 and 0.6, and zero otherwise.', how: 'solar_elevation × 1{ 0.2 ≤ cloud_frac < 0.6 }', source: [src('pvlibPos')], when: WHEN.comb },
  pred_stage4_clean: { full: 'Physics + Chronos-2 baseline forecast (W/m²)', meaning: 'A first-guess forecast that blends a physical cloud model with the Chronos-2 time-series model. The 40 models then learn only the correction to it.', how: 'w_h · Chronos-2 forecast + (1 − w_h) · phys;   phys = max(0, clearsky_ghi · (1 − k_h · cloud_frac)). The blend weights w_h and k_h were fitted on the 2024 even-origin data only.', source: [src('chronos'), src('ineichen')], when: WHEN.comb },
  clean_attenuation: { full: 'Clouds’ expected dimming (W/m²)', meaning: 'How much sunshine the baseline expects clouds to take away from the clear-sky ceiling.', how: 'clearsky_ghi − pred_stage4_clean', source: [src('ineichen')], when: WHEN.comb },
}

// Answer to the judges' question: can it run offline?
NODES.offline = {
  title: 'Can it run offline?',
  count: null,
  tag: 'real',
  summary: 'Almost completely. Only one thing has to be downloaded, once a day, and it is stored on site.',
  features: [],
  formulas: [
    ['Already on site', 'Sun and calendar: calculated.\nMountain shading: a stored file made from the elevation model.\nStation memory: measured by the station’s own sensor.\nCombined clues: calculated from the above.'],
    ['One daily download', 'The MET Norway weather-model run of 18:00 UTC is published about 20:15 UTC.\nOur forecast is made at 00:00 UTC, so the file has been available for 3 h 45 min.\nOnce stored on the station, the forecaster needs no internet connection.'],
    ['If the download is missing', 'The system does not guess. It can fall back to a simple on-site forecaster (persistence plus clear-sky). The repository marks that fallback as an unvalidated prototype.'],
  ],
}
NODE_STEP.offline = 1
