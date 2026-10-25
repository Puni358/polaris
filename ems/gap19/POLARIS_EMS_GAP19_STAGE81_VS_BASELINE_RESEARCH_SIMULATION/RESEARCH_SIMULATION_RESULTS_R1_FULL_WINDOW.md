# Full-Window Research Simulation Results — R1
## Stage 8.1 (Corrected) vs. Baseline Forecast Engine — GAP19 MILP Comparison

**Status**: `RESEARCH_SIMULATION_RESULT` — NOT a production run, NOT a stakeholder-authorized
experiment, NOT a claim about real station or operational performance. Governed by the
frozen `FROZEN_RESEARCH_EXPERIMENT_MANIFEST.md` (R1) and `RESEARCH_EXCEPTION_DECISION_RECORD.md`
in this directory. Raw per-cycle output: `RESEARCH_FULL_EXPERIMENT_RAW_RESULTS.json`
(694 cycles). Run log confirms: manifest hash-verified, final smoke test passed, run
completed with zero STOP conditions, no exceptions, no assumption changes mid-run.

---

## 1. What was run

347 daily origins (2024-01-20 through 2024-12-31 — the full span of the frozen, hash-verified
Stage 8.1 feature matrix; see manifest §3), each evaluated twice — `baseline`
(`LocalBaselineForecastEngine`) and `stage8_1_corrected` (frozen `Stage81CorrectedForecastEngine`)
— for 694 total independent single-step closed-loop evaluations
(ForecastBundle → `EMSControlRouter` → `GAP19HighsNativeOptimizer`/`OptionDFallbackSolver` →
one `DigitalTwinSimulator.step`). Same fixed warmed-up `StationState`, same fixture, same
config YAMLs, same R1-frozen terminal-reserve formula for both arms at every origin; only the
forecast engine differs. Total wall-clock: 246.7s for all 694 cycles.

**Important limitation, stated up front**: `Stage81CorrectedForecastEngine` only overrides the
*solar irradiance* channel; by its own design (`s81_corrected_solar.py`) it falls back to the
same `LocalBaselineForecastEngine` instance as the baseline arm for the *demand* and *wind*
channels. So this comparison isolates the effect of solar-forecast differences only — it is
**not** a comparison of two independently-different demand/wind/solar forecasting systems.

## 2. Route selection — identical between arms

| | NORMAL (GAP19/MILP) | EMERGENCY (OptionD) |
|---|---|---|
| Baseline | 245 | 102 |
| Stage 8.1 corrected | 245 | 102 |

**Route disagreement across all 347 origins: 0.** The router selected the same mode for both
arms at every origin. This is itself a research-simulation finding, not an assumption: with
demand/wind forecasts shared between arms, the router's NORMAL/EMERGENCY decision did not
change when only the solar forecast changed, at any of the 347 origins tested.

## 3. Solve status / reliability

| | NORMAL cycles OPTIMAL | NORMAL cycles non-OPTIMAL | EMERGENCY cycles (OptionD) |
|---|---|---|---|
| Baseline | 245 / 245 (100%) | 0 | 102 (status `OPTION_D_FALLBACK`, not a MILP solve — OptionD's own convention, not a failure) |
| Stage 8.1 corrected | 245 / 245 (100%) | 0 | 102 (same) |

No solver failure, infeasibility, or exception occurred in any of the 694 cycles for either
arm.

| Solve time (NORMAL/MILP cycles only) | Baseline | Stage 8.1 corrected |
|---|---|---|
| Mean | 0.590 s | 0.406 s |
| (EMERGENCY/OptionD cycles, for reference) | ~0.0001 s (closed-form fallback, not a MILP solve) | ~0.0002 s |

## 4. Diesel fuel (NORMAL-route cycles, n=245 each; identical routing means EMERGENCY-route
diesel use is also directly comparable — both reported)

| Metric | Baseline | Stage 8.1 corrected | Absolute diff (Stage8.1 − Baseline) | % diff |
|---|---|---|---|---|
| Planned fuel, NORMAL cycles (L, summed) | 5,818.32 | 10,849.60 | **+5,031.28 L** | **+86.5%** |
| Planned fuel, EMERGENCY cycles (L, summed) | 14,240.13 | 14,355.26 | +115.13 L | +0.8% |
| Planned fuel, all 347 cycles (L, summed) | 20,058.44 | 25,204.86 | **+5,146.42 L** | **+25.7%** |
| Realized t0 fuel (actually executed first hour, all 347 cycles, L) | 0.0 | 636.20 | +636.20 L | n/a (baseline used 0) |

**Stage 8.1's forecast led the MILP to plan — and, at 62 of 347 origins, actually execute at
t0 — more diesel use than the baseline forecast did**, concentrated in the NORMAL/MILP route.

## 5. Unmet demand

| | Baseline | Stage 8.1 corrected | Diff |
|---|---|---|---|
| Planned unmet load, all cycles (Wh, summed) | 29,661,600.0 | 29,661,600.0 | **0 (identical at every one of the 347 origins)** |

Identical because unmet load in this model is driven by the demand-side critical-load clip,
which is computed from the *demand* forecast channel — shared between both arms (§1 limitation).
This metric cannot distinguish the two forecast engines in this experiment design.

## 6. Renewable curtailment

| Metric | Baseline | Stage 8.1 corrected | Absolute diff | % diff |
|---|---|---|---|---|
| Planned curtailment, NORMAL cycles (Wh, summed) | 31,916,981.6 | 10,157,843.9 | **−21,759,137.7 Wh** | **−68.2%** |
| Planned curtailment, EMERGENCY cycles (Wh, summed) | 10,156,566.2 | 10,049,820.7 | −106,745.5 Wh | −1.1% |
| Planned curtailment, all 347 cycles (Wh, summed) | 42,073,547.8 | 20,207,664.6 | **−21,865,883.3 Wh** | **−52.0%** |

Stage 8.1's solar forecast led the MILP to plan substantially less renewable curtailment,
concentrated in the NORMAL/MILP route — consistent with §4's higher diesel use: the two shift
together (less curtailment, more diesel, under the Stage 8.1 forecast in this sample).

## 7. Battery throughput / equivalent full cycles (EFC)

| Metric | Baseline | Stage 8.1 corrected | Absolute diff | % diff |
|---|---|---|---|---|
| Planned battery discharge, all cycles (Wh, summed) | 38,109,191.2 | 36,048,030.8 | −2,061,160.4 Wh | −5.4% |
| Planned battery charge, all cycles (Wh, summed) | 41,330,317.3 | 38,711,815.7 | −2,618,501.6 Wh | −6.3% |
| EFC (planned discharge Wh ÷ 200,000 Wh capacity) | 190.5 | 180.2 | −10.3 cycles | −5.4% |

## 8. SOC trajectory / range

| Metric | Baseline | Stage 8.1 corrected |
|---|---|---|
| Realized next-step SOC % (t0, across all 347 origins) — min / mean / max | 68.04 / 73.29 / 84.13 | 68.04 / 75.81 / 95.00 |
| Planned SOC % within any single 24h horizon — min / max (across all cycles) | 20.0 / 95.0 | 20.0 / 95.0 |

Both arms' plans touch the full configured SOC band (20%–95%) somewhere within some
24h horizon; the realized (t0-only) SOC distribution is similar but the Stage 8.1 arm's
realized SOC reaches higher (up to 95.0% vs 84.1% for baseline) in at least one cycle.
Because each cycle is independent (see §9), this is not a continuous year-long SOC
trajectory — see limitations below.

## 9. Limitations / uncertainty (declared per manifest §6, not discovered after the fact)

- **Independent single-step cycles, not a continuous trajectory.** Each of the 347 origins is
  its own fresh 24h plan with the same fixed warmed-up initial `StationState`; only the plan's
  first hour is actually executed (`simulator.step`). The 23 remaining planned hours per cycle
  are the optimizer's intended dispatch, not a realized outcome — this is why §4–§8 report
  "planned" (24h-horizon) and "realized t0" figures separately, never blended.
- **Demand and wind forecasts are shared between arms** (§1); only solar differs. All
  differences reported above are solar-forecast-driven, not evidence about Stage 8.1's
  (nonexistent, in this engine) demand or wind forecasting.
- **Terminal reserve values are `SIMULATED_RESEARCH_ASSUMPTION`, not authorized.** Every
  number in §4–§8 is conditioned on the R1-frozen formula (40,000 Wh floor + 6h dynamic
  deficit × 1.10 margin). A different (also unauthorized) choice of formula/margin/floor would
  likely shift these results; this experiment does not test sensitivity to that choice.
- **Sample is one historical year (2024) at one fixed initial state**, repeated independently
  347 times — it is not a multi-year or multi-initial-condition study, and says nothing about
  variance across other years or starting conditions.
- **Route selection (§2) is the most assumption-independent finding here** — it does not
  depend on the terminal-reserve formula at all (EMERGENCY-route cycles never read
  `terminal_target_wh` — confirmed by code trace in the earlier governance investigation) and
  is identical between arms for all 347 origins.

## 10. What this does NOT establish

- **No claim that Stage 8.1 forecasting outperforms or underperforms the baseline.** More
  diesel + less curtailment is not, by itself, "better" or "worse" — that judgment would
  require an authorized objective/cost weighting that does not currently exist (see
  `POLARIS_EMS_GAP19_STAGE81_EXPERIMENT_HUMAN_GOVERNANCE_DECISION_PACKAGE/`).
- Does not validate, authorize, or recommend the R1 terminal-reserve formula, the 10% margin,
  or the floor choice for any real use.
- Does not resolve DEC-TR-03, DEC-RES-03, SD-07, SD-08, or SD-13, which remain open exactly as
  recorded in the governance package.
- Is not evidence for or against deploying Stage 8.1 forecasting, or this terminal-reserve
  formulation, in production.

**All results in this document are RESEARCH-SIMULATION ONLY.**
