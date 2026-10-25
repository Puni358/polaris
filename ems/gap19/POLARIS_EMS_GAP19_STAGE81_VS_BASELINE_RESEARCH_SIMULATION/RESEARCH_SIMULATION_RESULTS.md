# Research Simulation Results
## Stage 8.1 (Corrected) vs. Baseline Forecast Engine — GAP19 MILP Comparison

**Status**: `RESEARCH_SIMULATION_RESULT` — NOT a production run, NOT a stakeholder-authorized
experiment, NOT a claim about real station or operational performance. Governed by
`RESEARCH_EXCEPTION_DECISION_RECORD.md` in this directory. Raw output:
`RESEARCH_SIMULATION_RAW_RESULTS.json`.

---

## What was run

5 independent single-cycle closed-loop evaluations (ForecastBundle → `EMSControlRouter` →
`GAP19HighsNativeOptimizer` → `DigitalTwinSimulator.step`), each run twice — once with
`LocalBaselineForecastEngine` (synthetic persistence/diurnal baseline), once with the frozen
`Stage81CorrectedForecastEngine` (hash-verified, `FROZEN_MODEL_SHA256` matched) — at daily
origins 2024-06-01 through 2024-06-05, all using the same warmed-up `StationState` (SOC 80%,
diesel running) and the same real H1.0 fixture data. All production code
(`system/*`, `gap19_highs_native.py`, `worker.py`, `*.yaml`) ran unmodified. The only input
this script supplied that production code does not currently supply is
`terminal_target_wh`, computed per-cycle from each arm's own forecast using the
`SIMULATED_RESEARCH_ASSUMPTION` formula frozen in `RESEARCH_EXCEPTION_DECISION_RECORD.md`.
**This is 5 independent single-step evaluations, not one continuous multi-day trajectory** —
no attempt was made to simulate the 23 hours between daily origins.

---

## Results table

| Origin | Engine | Route | `terminal_target_wh` (simulated) | Constraint status | Battery discharge @t0 (W) | Diesel @t0 (W) | Next SOC % |
|---|---|---|---|---|---|---|---|
| 2024-06-01 | baseline | NORMAL | 148,596.5 | OPTIMAL | 12,100.0 | 0.0 | 73.42 |
| 2024-06-01 | stage8_1_corrected | NORMAL | 145,351.8 | OPTIMAL | 8,774.8 | 0.0 | 75.23 |
| 2024-06-02 | baseline | NORMAL | 148,596.5 | OPTIMAL | 12,100.0 | 0.0 | 73.42 |
| 2024-06-02 | stage8_1_corrected | NORMAL | 143,049.6 | OPTIMAL | 8,487.5 | 0.0 | 75.39 |
| 2024-06-03 | baseline | NORMAL | 148,596.5 | OPTIMAL | 12,100.0 | 0.0 | 73.42 |
| 2024-06-03 | stage8_1_corrected | NORMAL | 141,645.3 | OPTIMAL | 12,100.0 | 0.0 | 73.42 |
| 2024-06-04 | baseline | NORMAL | 119,924.7 | OPTIMAL | 12,100.0 | 0.0 | 73.42 |
| 2024-06-04 | stage8_1_corrected | NORMAL | 114,913.5 | OPTIMAL | 12,100.0 | 0.0 | 73.42 |
| 2024-06-05 | baseline | NORMAL | 143,544.8 | OPTIMAL | 12,100.0 | 0.0 | 73.42 |
| 2024-06-05 | stage8_1_corrected | NORMAL | 138,614.5 | OPTIMAL | 12,100.0 | 0.0 | 73.42 |

All 10 cycles routed `NORMAL` (GAP19/MILP, not OptionD/EMERGENCY) and all solved `OPTIMAL` —
i.e., the previously-blocking `MISSING_GOVERNED_INPUT` error (see
`HUMAN_GOVERNANCE_DECISION_PACKAGE.md`) did not recur once `terminal_target_wh` was supplied,
for either arm, at any of the 5 origins tested.

## Observations (research-simulation only, no operational claim)

- Across all 5 origins, the simulated `terminal_target_wh` computed from the Stage 8.1
  forecast was consistently lower than the one computed from the baseline forecast
  (differences of roughly 2,000–5,500 Wh). This follows mechanically from the
  `SIMULATED_RESEARCH_ASSUMPTION` formula: Stage 8.1's solar predictions differ from the
  baseline's synthetic diurnal curve, which changes the forecasted deficit the formula sums
  over the trailing 6h window.
- On 2 of 5 origins (06-01, 06-02), the differing `terminal_target_wh` combined with
  differing forecasted demand/solar to produce different first-timestep battery discharge
  decisions between the two arms. On the other 3 origins, both arms produced the same t0
  decision.
- No diesel use occurred at t0 in any cycle; all differences surfaced in the
  battery-charge/discharge split.
- **No conclusion is drawn about which forecast engine is "better."** These are MILP
  responses to two different forecast inputs under an unauthorized, simulated terminal-reserve
  assumption, in a 5-point single-step sample. They do not estimate fuel savings, reliability
  improvement, or any other operational metric, and must not be cited as such.

---

## What this result does NOT establish

- It does not validate or invalidate `terminal_reserve_model`, the specific formula used, the
  10% margin, or the floor-equals-technical-minimum choice — all remain
  `SIMULATED_RESEARCH_ASSUMPTION` / `NOT_STAKEHOLDER_AUTHORIZED`.
  Operational and policy conclusions, see `POLARIS_EMS_GAP19_STAGE81_EXPERIMENT_HUMAN_GOVERNANCE_DECISION_PACKAGE/`.
- It does not resolve DEC-TR-03, DEC-RES-03, SD-07, SD-08, or SD-13, which remain open exactly
  as recorded in that package.
- It is not evidence for or against deploying Stage 8.1 forecasting in production.
