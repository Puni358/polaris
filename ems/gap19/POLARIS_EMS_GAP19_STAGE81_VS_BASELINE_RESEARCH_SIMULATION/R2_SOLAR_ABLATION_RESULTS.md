# R2 Results — Solar-Forecast Ablation

**Status**: `RESEARCH_SIMULATION_RESULT`. **THIS IS A SOLAR-FORECAST ABLATION, NOT A FULL
RENEWABLE-FORECAST EXPERIMENT.** Wind and demand are deliberately identical
(baseline-persistence) between both arms, verified bit-for-bit at all 347 origins
(`R2_IDENTICAL_INPUT_VERIFICATION.json`: `"all_identical": true`). Only the solar forecast
differs between arms. Governed by `R2_SOLAR_ABLATION_MANIFEST.md`, which reuses R1's frozen
terminal-reserve assumptions unchanged. NOT a production run, NOT stakeholder-authorized, NOT
a claim about real station or operational performance. Raw data:
`R2_FULL_EXPERIMENT_RAW_RESULTS.json` (694 cycles, 347 origins × 2 arms).

**Reproducibility note**: R2's aggregate physical results (diesel, curtailment, battery,
SOC, route, solve status) are numerically identical to R1's, as expected — R2 reuses R1's
exact frozen code paths, config, and inputs (the only new element is the full-window
identical-input verification gate, which R1 had only spot-checked at 4 origins). Only
wall-clock `solve_time_s` differs between the two runs (expected timing noise, not a result).

---

## 1. Pre-flight checks (all passed; run would have STOPped otherwise)

- Frozen manifest hash verification (matrix, model, formula script, decision record, 6
  config YAMLs): **all MATCH**.
- Full-window (347/347 origins) identical wind/demand check: **0 mismatches**.
- Final single-origin smoke test (both arms): **both OPTIMAL**.

## 2. Diesel fuel consumed

| Metric | Baseline | Stage 8.1 corrected | Absolute diff | % diff |
|---|---|---|---|---|
| Planned fuel, NORMAL cycles (L, summed, n=245) | 5,818.32 | 10,849.60 | **+5,031.28 L** | **+86.5%** |
| Planned fuel, EMERGENCY cycles (L, summed, n=102) | 14,240.13 | 14,355.26 | +115.13 L | +0.8% |
| Planned fuel, all 347 cycles (L, summed) | 20,058.44 | 25,204.86 | **+5,146.42 L** | **+25.7%** |
| Realized t0 fuel (actually executed, all 347 cycles, L) | 0.0 | 636.20 | +636.20 L | n/a (baseline used 0) |

## 3. Renewable curtailment

| Metric | Baseline | Stage 8.1 corrected | Absolute diff | % diff |
|---|---|---|---|---|
| Planned curtailment, NORMAL cycles (Wh, summed) | 31,916,981.6 | 10,157,843.9 | **−21,759,137.7 Wh** | **−68.2%** |
| Planned curtailment, EMERGENCY cycles (Wh, summed) | 10,156,566.2 | 10,049,820.7 | −106,745.5 Wh | −1.1% |
| Planned curtailment, all 347 cycles (Wh, summed) | 42,073,547.8 | 20,207,664.6 | **−21,865,883.2 Wh** | **−52.0%** |

## 4. Unmet demand

| | Baseline | Stage 8.1 corrected | Diff |
|---|---|---|---|
| Planned unmet load, all cycles (Wh, summed) | 29,661,600.0 | 29,661,600.0 | **0 — identical at every origin** |

Identical because unmet load here is driven by the demand-side critical-load clip, and demand
is, by R2's own design, identical between arms (§ ablation scope). This metric cannot
distinguish the two forecast engines in this ablation.

## 5. Battery throughput / EFC

| Metric | Baseline | Stage 8.1 corrected | Absolute diff | % diff |
|---|---|---|---|---|
| Planned battery discharge, all cycles (Wh, summed) | 38,109,191.2 | 36,048,030.8 | −2,061,160.4 Wh | −5.4% |
| Planned battery charge, all cycles (Wh, summed) | 41,330,317.3 | 38,711,815.7 | −2,618,501.6 Wh | −6.3% |
| EFC (planned discharge Wh ÷ 200,000 Wh capacity) | 190.5 | 180.2 | −10.3 cycles | −5.4% |

## 6. SOC min / max / mean

| Metric | Baseline | Stage 8.1 corrected |
|---|---|---|
| Realized next-step SOC % (t0, across 347 origins) — min / mean / max | 68.04 / 73.29 / 84.13 | 68.04 / 75.81 / 95.00 |
| Planned SOC % within any single 24h horizon — min / max (across all cycles) | 20.0 / 95.0 | 20.0 / 95.0 |

## 7. Reliability

| Metric | Baseline | Stage 8.1 corrected |
|---|---|---|
| Route selection agreement (of 347 origins) | **347/347 identical** (0 disagreements) | — |
| NORMAL/MILP cycles reaching `OPTIMAL` | 245 / 245 (100%) | 245 / 245 (100%) |
| EMERGENCY cycles (OptionD, own `OPTION_D_FALLBACK` status — not a MILP solve, not a failure) | 102 | 102 |
| Solver failures / infeasibilities (either arm) | 0 | 0 |

## 8. MILP solve time / status

| Metric | Baseline | Stage 8.1 corrected |
|---|---|---|
| Mean solve time, NORMAL/MILP cycles | 0.816 s | 0.570 s |
| Mean solve time, EMERGENCY/OptionD cycles (closed-form, not a MILP solve) | ~0.0002 s | ~0.0002 s |
| Total wall-clock, full run (694 cycles) | 343.4 s | (same run) |

(Solve-time means differ slightly from R1's own run — expected wall-clock measurement noise
between runs on the same machine, not a result of any input or assumption change.)

## 9. Solar forecast accuracy, alongside the control outcomes above

From the companion audit (`R2_AUDIT_AND_STOP_REPORT.md`, Q1), computed against the frozen
matrix's own `actual_SW_IN` ground truth for the same 347×24 rows:

| Engine | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | nMAE |
|---|---|---|---|---|
| Baseline | 179.03 | 257.74 | +164.57 | 2.006 |
| Stage 8.1 corrected | 22.85 | 50.25 | −0.92 | 0.256 |

Stage 8.1's solar forecast is ~8× more accurate (MAE) with near-zero bias, versus the
baseline's large systematic over-prediction. This accuracy gap is the documented mechanism
(see `R1_DIESEL_CAUSALITY_AND_WIND_PROVENANCE_FORENSIC_REPORT.md`) behind §2–§3 above: the
baseline's fixed, always-optimistic solar curve produces forecasted "surplus" that must be
curtailed; Stage 8.1's more accurate (and often lower, on these specific days) forecast
shows less surplus to curtail but more real shortfall to cover with diesel and/or battery.

## 10. What this does NOT establish (unchanged from R1)

- No claim that Stage 8.1 forecasting "wins" operationally — more diesel + less curtailment
  is not inherently better or worse without an authorized cost weighting.
- Does not validate, authorize, or recommend the R1/R2 terminal-reserve formula, margin, or
  floor for any real use.
- Does not resolve DEC-TR-03, DEC-RES-03, SD-07, SD-08, or SD-13.
- **Explicitly not a wind- or demand-forecast evaluation**: no wind forecast was used (none
  exists that is authorized — `R2_AUDIT_AND_STOP_REPORT.md` Q2) and no demand-forecast
  alternative was in scope. This result says nothing about renewable forecasting as a whole,
  only about the solar channel in isolation.

**All results in this document are RESEARCH-SIMULATION ONLY, from a SOLAR-FORECAST ABLATION.**
