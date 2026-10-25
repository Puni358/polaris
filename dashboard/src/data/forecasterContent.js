// Content for the "Forecaster" tab: everything about the POLARIS N6 solar forecaster and nothing else.
// Facts come from the frozen model file and its manifest (candidate_n6_model.joblib, CANDIDATE_N_MANIFEST.json),
// n6_solar.py and run_candidate_n_experiment.py.

export const F_STEPS = [
  { id: 1, label: 'Inputs ready' },
  { id: 2, label: 'The 40 models' },
  { id: 3, label: 'Average & blend' },
  { id: 4, label: 'Uncertainty & reserve' },
  { id: 5, label: 'Output' },
]

export const F_NODE_STEP = { asm: 1, base: 1, add: 2, spe: 2, meanA: 3, meanB: 3, blend: 3, mask: 3, spread: 4, bound: 4, reserve: 4, out: 5 }
export const F_STEP_NODE = { 1: 'asm', 2: 'add', 3: 'blend', 4: 'bound', 5: 'out' }

export const F_NODES = {
  asm: {
    title: 'Feature assembler',
    plain: 'Collects the 36 clues for each of the next 24 hours into one table, and refuses to continue if anything is wrong.',
    belongs: 'Belongs to the forecaster, not the optimizer. The optimizer builds its own, different table of 432 unknowns and 336 rules.',
    facts: ['24 rows × 36 columns', 'no missing numbers', 'checked before any model runs'],
    blocks: [
      ['What it builds', 'A table with one row per forecast hour (24) and one column per clue (36).'],
      ['Checks before any model runs', 'No column may contain the real outcome (measured sunshine): the forecaster stops instead of guessing.\nNo missing or infinite values in the critical clues.\nThe weather-model file must have arrived before the 00:00 UTC deadline.'],
    ],
  },
  base: {
    title: 'Baseline forecast',
    plain: 'A first guess made from physics and a time-series model. The 40 models only learn how to correct it.',
    facts: ['physics + Chronos-2', 'fitted on 2024 even days only'],
    blocks: [
      ['How it is made', 'baseline = w · Chronos-2 forecast + (1 − w) · physics\nphysics = max(0, clear-sky light · (1 − k · cloud fraction))'],
      ['Why start from a baseline', 'Correcting a good first guess is much easier than predicting sunshine from nothing. The models do not have to learn the daily sun curve again.'],
    ],
  },
  add: {
    title: '25 additive models',
    plain: 'Twenty-five small decision-tree models. Each looks at the 36 clues and says by how many watts per square metre the baseline is wrong. The 25 answers are averaged.',
    facts: ['25 models', 'seeds 100 – 124', 'each sees 78% of the clues', '4 questions deep'],
    blocks: [
      ['What is one model?', 'A gradient-boosted decision tree. A tree asks yes/no questions about the clues (Is the sun above 20°? Is the cloud fraction above 0.6?) and ends on a number: the correction. Boosting adds many small trees one after another, each fixing what the previous ones got wrong.'],
      ['Why 25 of them?', 'Each model is trained with a different random seed and may look at only 78% of the clues at each split, so no two make exactly the same mistakes. Averaging them cancels the individual quirks. This is called bagging.'],
      ['Settings', 'depth 4 · at least 25 samples in every leaf · L2 penalty 15 · loss = absolute error (not thrown off by a few wild hours)'],
      ['Trained on', 'The daytime hours of the 2024 even-numbered forecast days (174 days). The odd-numbered days were kept aside for testing.'],
      ['Their answer', 'ŷ_add = mean over the 25 models of  max(0, baseline + correction)'],
    ],
  },
  spe: {
    title: '15 clearness-ratio specialists',
    plain: 'Fifteen more models that are experts at one thing: correcting the baseline as a share of the clear-sky light. They matter most when the sun is high.',
    facts: ['15 models', 'seeds 500 – 514', 'each sees 80% of the clues', 'bright hours count more'],
    blocks: [
      ['How they differ from the additive models', 'An additive model predicts the correction in W/m². A specialist predicts the correction divided by (clear-sky light + 15 W/m²) and multiplies it back. A 10% mistake is treated as a 10% mistake whether the sky could give 100 or 600 W/m².'],
      ['Training weight', 'Bright hours are weighted by their clear-sky light, so the specialists spend their effort where the sun is strong.'],
      ['Safety cap', 'A specialist’s answer can never exceed 1.25 × clear-sky light or the baseline, whichever is larger.'],
      ['Settings', 'depth 4 · at least 30 samples per leaf · L2 penalty 15 · loss = absolute error'],
      ['Their answer', 'ŷ_kt = mean over the 15 models of  clip( baseline + ratio · (terrain clear-sky + 15),  0,  max(1.25 · clear-sky, baseline) )'],
    ],
  },
  meanA: {
    title: 'Average of the 25',
    plain: 'The middle opinion of the additive group.',
    facts: [],
    blocks: [['Formula', 'ŷ_add = (1 ÷ 25) · Σ of the 25 additive answers']],
  },
  meanB: {
    title: 'Average of the 15',
    plain: 'The middle opinion of the specialist group.',
    facts: [],
    blocks: [['Formula', 'ŷ_kt = (1 ÷ 15) · Σ of the 15 specialist answers']],
  },
  blend: {
    title: 'Blender',
    plain: 'Decides how much to trust the specialists, using the sun’s height. Low sun: only the additive models. High sun with no mountain in the way: up to 55% specialists.',
    belongs: 'This is the “assembler” of the two groups. It is part of the forecaster and happens before anything reaches the optimizer.',
    facts: ['ramp from 22° to 32°', 'maximum specialist weight 0.55', 'zero if a mountain blocks the sun'],
    blocks: [
      ['The rule', 'w = 0 if the sun is below 22° or blocked by terrain\nw = 0.55 · (elevation − 22°) ÷ (32° − 22°) between 22° and 32°\nw = 0.55 above 32°'],
      ['The blend', 'ŷ = (1 − w) · ŷ_add + w · ŷ_kt'],
      ['Why a ramp', 'Low sun and long shadows are where the additive models are most reliable. High sun is where the clearness-ratio view helps. A smooth ramp avoids a sudden switch.'],
    ],
    chart: 'ramp',
  },
  mask: {
    title: 'Night rule',
    plain: 'When the sun is below the horizon, the forecast is exactly zero.',
    facts: [],
    blocks: [['Rule', 'ŷ = 0 whenever solar elevation ≤ 0° or clear-sky light = 0']],
  },
  spread: {
    title: 'Disagreement of the 40',
    plain: 'If the 40 models agree, the forecast is confident. If they disagree, it is not.',
    facts: [],
    blocks: [['Formula', 'scale = standard deviation of the 40 answers + 0.10 · terrain clear-sky + 5 W/m²']],
  },
  bound: {
    title: '90% safety bound',
    plain: 'A pessimistic version of the forecast: real sunshine should be above it nine times out of ten.',
    facts: ['constant 1.859', 'split-conformal'],
    blocks: [
      ['Formula', 'ŷ_low = max(0, ŷ − 1.859 · scale)\nŷ_high = ŷ + 1.859 · scale'],
      ['Where 1.859 comes from', 'It was calibrated on held-out data (split-conformal prediction) so that the lower bound holds for 90% of cases, without assuming the errors follow a bell curve.'],
    ],
  },
  reserve: {
    title: 'Battery reserve',
    plain: 'The more uncertain the next six hours, the more battery the optimizer must keep back.',
    facts: ['never below 15 kWh', '6-hour look-ahead'],
    blocks: [
      ['Formula', 's_hour = k_pv · scale ÷ 0.95\nscale_6h(t) = sum of s_hour over the next 6 h + 100 Wh\nreserve(t) = max( 15 kWh,  1.5702 · scale_6h(t) )'],
      ['Where it goes', 'Straight to the optimizer as the reserve target (priority J2).'],
    ],
  },
  out: {
    title: '24-hour forecast and reserve',
    plain: 'Two things leave the forecaster: the next 24 hours of sunshine, and the battery reserve for each hour.',
    facts: ['made once a day, at 00:00 UTC', 'model file frozen: SHA-256 b1b54c93…'],
    blocks: [
      ['What the optimizer gets', 'solar light for 24 hours (W/m²) → converted to power: min( W/m² × 51 W per W/m², 60 kW )\nbattery reserve target for 24 hours (Wh)'],
      ['Frozen and fingerprinted', 'The model file cannot change without its fingerprint changing: SHA-256 b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197.'],
      ['How often', 'A new forecast is made every midnight (00:00 UTC) from the last 24 hours of real readings.'],
    ],
  },
}

export const dotInfo = (kind, i) => kind === 'add'
  ? { title: `Additive model #${i + 1}`, text: `Random seed ${100 + i}. At each split it may look at 78% of the 36 clues. Trees 4 questions deep, at least 25 samples per leaf. It predicts the baseline’s error in W/m².` }
  : { title: `Clearness-ratio specialist #${i + 1}`, text: `Random seed ${500 + i}. At each split it may look at 80% of the 36 clues. Trees 4 questions deep, at least 30 samples per leaf. It predicts the baseline’s error as a share of clear-sky light.` }
