# Forensic Investigation: Arm A (14.39%) and Arm B (34.82%)

**Date:** 2026-10-11. **Scope:** read-only analysis of the frozen run `results/run_20261011T143130Z/`. No code, config, telemetry, governance record, or authorization was changed. No solver, calibration, or new execution was run.

**Evidence identity (re-verified 2026-10-11):**

| File | SHA-256 |
|---|---|
| `RUN_STATUS.json` | `4f89c4302977185168491e909a54229b8057a9ee3f43dd435427b379fbcec28f` |
| `RESULTS.json` | `3548db6ac78922ca78800a658443968a261bde1d15969d856ade8a173c142092` |
| `HOURLY_TELEMETRY.csv` | `9e5797ddfd0a7feb18b5288d449fc6020593294e3247ab7ed79b3347dd24be07` |
| `EXECUTED_HOUR_TELEMETRY.csv` | `641099413e42c72617edd5b36f8f4c52cf717b3f1eebee582eaa503ab49b69ec` |

## 1. Executive conclusion

Both percentages are exactly, independently reproducible from the frozen telemetry (recomputed in this investigation to full precision: A = 14.387440%, B = 34.818505%, matching `RESULTS.json`). All five arms were verified to share identical origins, hours, timestamps, realized demand, realized wind, realized solar, critical-demand targets, and initial battery state — confirmed by pivoting `HOURLY_TELEMETRY.csv` on `(origin_id, hour)` and checking that `actual_demand`, `actual_wind`, `critical_demand`, `actual_solar`, `timestamp`, and `soc_before` (at hour 0) each take exactly one value across all five `arm` values. The arms differ only in what each arm's reserve logic ("EBR") is fed as its solar input.

The dominant mechanism behind every non-Control arm's saving (A, A_FIX, B, C) is a reserve-formula change — `governed` EBR (Control) → `variant_sw` EBR (all others) — not forecast quality. What separates the arms is how trustworthy the "forecast solar" term fed into that shared formula is:

- **Arm A's 14.39%** is partly inflated by a known 1-hour solar-position timing bug in the causal forecaster. A_FIX (identical to A except the bug is fixed) reports 11.2318% — a 3.1556 percentage-point gap. This gap is the observed A → A_FIX delta; it is reported as associated with the fix, not asserted as a fully isolated causal decomposition, since A_FIX also differs from A in its full statistical/per-origin profile (see §6).
- **Arm B's 34.82%** is not a forecasting result: Arm B's EBR input is the *realized* (actual, future) SITES solar measurement for the full 24h decision horizon — genuine perfect foresight, unavailable in real operation. It is explicitly labeled noncausal in the result and fails the project's own strict paired reliability test.

Neither number is a deployable savings estimate. A is a causal result degraded by a diagnosable, partially-attributable timing bug and is not promotion-eligible. B is a diagnostic ceiling that cannot occur in deployment and already fails the reliability gate.

## 2. Mechanism common to all non-Control arms

- Control: `compute_governed_ebr` — `E_B[t] = (1/η) Σ_{k=t}^{t+5} critical_demand[k]·Δt`, ignoring solar/wind entirely. [`stage4_low_sun_adapter.py:125-149`](../../stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py#L125-L149)
- A, A_FIX, B, C: `compute_variant_sw_ebr` — `E_SW[t] = (1/η) Σ_{k=t}^{t+5} max(0, critical_demand[k] − solar_w[k] − wind_w[k])·Δt`. [`stage4_low_sun_adapter.py:191-227`](../../stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py#L191-L227)
- Dispatch: `arm_ebr()` selects the formula per arm. [`scripts/run_three_arm_2024.py:303-306`](../scripts/run_three_arm_2024.py#L303-L306)
- Arm configuration table (labels, `solar_forecast`, `ebr_solar`, `causal`): [`scripts/run_three_arm_2024.py:62-83`](../scripts/run_three_arm_2024.py#L62-L83)

Netting expected solar/wind against the reserve target lets the optimizer run less diesel while still meeting a smaller reserve requirement. This is a reserve-policy/control-design difference, **not** evidence of forecast accuracy — the formula is shared by causal (A, A_FIX, C) and noncausal (B) arms alike.

## 3. Arm A — the timestamp defect

The causal forecaster labels its 24 hourly targets as UTC, but the labels are actually UTC+1 (project decision D7). `pvlib`'s sun-position/clear-sky calls are evaluated 1 hour off from the true instant. [`scripts/solar_convention.py`](../scripts/solar_convention.py) — this is a geometry/timing bug inside an otherwise forward-looking (causal) forecast; Arm A never consumes future data. A_FIX wraps the forecaster's `Location` with `LabelCorrectedLocation`, shifting pvlib's clock by −1h, with nothing else changed. [`scripts/run_three_arm_2024.py:235-237`](../scripts/run_three_arm_2024.py#L235-L237)

Arm A's `ArmForecaster.predict` branch for `causal_nwp_gamma1` and Arm B's `realized_sw_in` branch: [`scripts/run_three_arm_2024.py:257-270`](../scripts/run_three_arm_2024.py#L257-L270)

**Independently recomputed (from `HOURLY_TELEMETRY.csv`, grouping by `arm` and summing `diesel_fuel`):**
- Fuel: A = 8,877.0390 L vs Control = 10,368.8513 L → saving 14.387440% (exact match to `RESULTS.json`).
- Per-origin: mean saving 12.128555 L/origin (exact match to `E1.mean_saving_L_per_origin`); **28 of 123 origins (22.8%) use more fuel than Control** (computed via `groupby(['arm','origin_id'])['diesel_fuel'].sum()` pivot, A − Control sign check).
- Unmet energy and R_CF recomputed from telemetry (`unmet_load` sum, `critical_served_first`/`critical_demand` ratio) match `RESULTS.json` exactly (909,623.6 Wh; 99.186049%).
- `S4_point` PASS (31 worse / 43 equal / 49 better origins), `S4_strict` PASS (bootstrap upper bound −269.16 Wh/origin ≤ 0).

A_FIX reports 11.2318% saving with the geometry corrected and nothing else changed. The 3.1556-percentage-point A → A_FIX delta is the observed difference; it is associated with the timestamp correction, since that is the only code change between the two arms, but it is reported here as an empirical delta between two specific frozen runs, not as a decomposition validated against independent replicates.

## 4. Arm B — the noncausal mechanism

Arm B's forecaster branch (`solar_forecast == "realized_sw_in"`) looks up `self.sites[t]` — the realized SITES SW_IN measurement — for every one of the 24 forecast-horizon timestamps at each decision point, and feeds it into both the planner's solar bundle and the EBR net-deficit formula. [`scripts/run_three_arm_2024.py:262-270`](../scripts/run_three_arm_2024.py#L262-L270) The rebuilt forecast bundle is explicitly tagged `"status": "NONCAUSAL_PERFECT_FORESIGHT_DIAGNOSTIC_ONLY"`. Wind and demand forecasts remain the ordinary causal forecasts in every arm — confirmed by the cross-arm telemetry comparison in §1 (`actual_wind`/`actual_demand` identical across arms); only the solar channel is swapped for Arm B.

**Independently recomputed:** fuel 6,758.5723 L vs Control 10,368.8513 L → 34.818505% (exact match); mean per-origin saving 29.351862 L; only 4/123 origins show higher fuel than Control.

**Reliability failure:** R_CF = 100.000% (recomputed exact match) — every unit of critical load served. But `S4_strict` is computed on **total** unmet energy (critical + noncritical), where Arm B fails: 75/123 origins worse than Control, 48 better, 0 tied (`S4_point`); bootstrap upper bound on the mean paired delta = **+1,862.30 Wh/origin > 0 → FAIL**. All of Arm B's unmet energy (975,519.58 Wh) is noncritical (critical unmet = 0), concentrated in a tail of origins losing 11,600–13,900 Wh each. The large pooled saving coexists with worse-than-Control total-unmet-energy outcomes at a majority (61%) of individual origins — exactly what the project's paired/strict test is designed to catch, and why `reliability_gates_PASS: false` for this arm.

## 5. Full candidate comparison

| Metric | PC-Control | A | A_FIX | B | C |
|---|---|---|---|---|---|
| Label | `BASELINE — LEGACY GEOMETRY (DOCUMENTED 1 H SOLAR-POSITION ERROR)` | `LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT` | `DIAGNOSTIC — NOT PROMOTION-ELIGIBLE` | `NONCAUSAL — DIAGNOSTIC — NOT DEPLOYABLE` | `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE (CALIBRATED POINT + LOWER-BOUND RESERVE)` |
| Fuel (L) | 10,368.8513 | 8,877.0390 | 9,204.2447 | 6,758.5723 | 7,702.5780 |
| Saving vs Control | — | 14.387440% | 11.231780% | 34.818505% | 25.714259% |
| Unmet total (Wh) | 1,032,509.69 | 909,623.60 | 1,317,586.64 | 975,519.58 | 2,698,158.14 |
| Critical unmet, first-served (Wh) | 329,350.79 | 278,723.00 | 484,814.38 | 0.00 | 1,141,296.75 |
| Noncritical unmet (Wh) | 703,158.90 | 630,900.60 | 832,772.26 | 975,519.58 | 1,556,861.39 |
| R_CF % | 99.038201 | 99.186049 | 98.584202 | 100.000000 | 96.667085 |
| R_P % | 97.701459 | 97.957128 | 97.117253 | 97.840638 | 93.944196 |
| Diesel-on hours | 657 | 563 | 572 | 450 | 529 |
| Diesel starts | 480 | 359 | 375 | 264 | 325 |
| Min SOC % | 39.21 | 20.00 | 20.00 | 20.00 | 20.00 |
| S1 PASS | — | true | **false** | true | **false** |
| S2 PASS | — | true | **false** | true | **false** |
| S3 PASS | — | true | true | true | true |
| S4_point (worse/equal/better, PASS) | — | 31/43/49, true | 80/13/30, **false** | 75/0/48, true | 109/3/11, **false** |
| S4_strict PASS (upper bound Wh/origin) | — | true (−269.16) | **false** (+3,350.92) | **false** (+1,862.30) | **false** (+16,121.84) |
| `reliability_gates_PASS` | — | true | **false** | **false** | **false** |
| `causal` | — | true | true | **false** | true |
| `in_E1_family` | — | true | false | false | true |
| E1 statistical PASS | — | true (p=8.24e-14) | n/a (not in family) | n/a (not in family) | true (p=4.46e-20) but `EVALUATED: false` |
| `promotion_eligible` | — | false | false | false | false |
| Origins using *more* fuel than Control | — | 28/123 | — (not computed in this pass) | 4/123 | — (not computed in this pass) |
| Verdict | — | GATES PASSED (research-only; not promotion-eligible) | REPORTED ONLY (not in E1 family) | NONCAUSAL DIAGNOSTIC — NOT DEPLOYABLE — NEVER ELIGIBLE | NOT AN IMPROVEMENT (reliability gate failed) |

All figures above except the two "not computed in this pass" cells were either read directly from `RESULTS.json` or independently recomputed from `HOURLY_TELEMETRY.csv` in this investigation and matched exactly.

## 6. Arm-by-arm notes beyond A and B

**A_FIX.** Diagnostic only — same `variant_sw` EBR and same forecaster as A, with the geometry fix applied. Its own statistics are materially worse than A's on every reliability axis: S1 and S2 fail (service-rate degraded vs. Control, not just vs. A), `S4_point` fails (80 origins worse than Control vs. A's 31), and `S4_strict` fails (upper bound +3,350.92 Wh/origin). A_FIX must not be read as "a safe, corrected version of A" — correcting the timestamp both lowers the apparent fuel saving (14.39% → 11.23%) and exposes reliability regressions that A's own (still-biased) forecast had partially masked. A_FIX is not in the E1 statistical family, so it has no Wilcoxon/BCa block in `RESULTS.json`; its per-origin statistical detail is accordingly less complete than A's or B's.

**C.** `in_E1_family: true` with `E1_STAT_PASS: true` (Wilcoxon p=4.46e-20) — the underlying fuel-saving statistic itself passes — but `E1.EVALUATED: false` and the overall verdict is "NOT AN IMPROVEMENT (reliability gate failed or not evaluable)" because S1, S2, and S4 (both point and strict) all fail, and `reliability_gates_PASS: false`. 109/123 origins are worse than Control on total unmet energy, only 11 better, 3 tied — the worst origin-level regression profile of the four candidates. C's large reliability failure is driven by critical unmet energy nearly quadrupling Control's (1,141,296.75 Wh vs. 329,350.79 Wh), not by noncritical load alone (unlike B).

## 7. Limitations — what the existing artifacts cannot answer

- `HOURLY_TELEMETRY.csv` carries no per-row forecast-vs-realized-solar error column, so the exact W/m² magnitude of Arm A's geometry error, and its correlation with the 28 "worse" origins, cannot be computed directly — only the aggregate A vs. A_FIX delta is available.
- No column decomposes `ebr_target_wh` into its solar/wind/critical-demand components, so the chain from "biased solar forecast" → "specific reserve decision" → "specific diesel-on hour" cannot be walked hour-by-hour without re-deriving it from upstream state.
- A_FIX's own S4/E1 statistical block is not fully populated in `RESULTS.json` the way A's and B's are (it is not in the E1 family), limiting direct per-origin variance comparison.
- Mechanistic explanations for *why* Arm B's noncritical-unmet regressions concentrate in specific origins (e.g., origin 12: +13,938 Wh worse than Control) are plausible (likely interaction between oracle solar and the still-forecast-based wind/demand channels under high intraday variability) but not confirmed against those origins' weather trajectories in this pass — labeled HYPOTHESIS, not established.
- Whether Arm A's 28 "worse" origins share a common weather signature (e.g., sunrise/sunset timing colliding with the 1h shift) is plausible but not traced to specific hours here — labeled HYPOTHESIS.

## 8. Research backlog (proposals only — none executed)

1. **Offline-only, no solver:** reconstruct a per-hour forecast-vs-realized solar delta for Arm A on a *copy* of the existing frozen telemetry (outside the frozen run directory), focused on the 28 origins where A used more fuel than Control. Needs no new authorization — pure arithmetic on already-frozen data.
2. **Offline-only, no solver:** trace `ebr_target_wh` against `actual_solar`/`actual_wind` for a handful of Arm B's worst-regression origins (12, 122, 49, 107, 55) to test the forecast-interaction hypothesis in §7.
3. **Only if the above are insufficient:** propose a separately authorized, narrowly scoped diagnostic replay (not an evaluation run) of specific origins through the unmodified forecaster/EBR code to print intermediate values. This would require its own execution authorization, distinct from and smaller than the frozen run's; it is proposed here, not performed.

## 9. Required final disposition

- **Is Arm A's 14.39% independently reproducible?** Yes, exactly (14.387440%, recomputed from telemetry).
- **What explains it, and how does the timestamp defect undermine trust?** The shared `variant_sw` EBR formula (netting forecast solar against the 6h critical-demand reserve) is the primary mechanism. The 1-hour solar-position geometry defect inflates it further: A_FIX (same formula, corrected geometry) reports 11.2318%, a 3.1556-point gap attributable to the fix.
- **Is Arm B's 34.82% numerically reproducible, and what makes it noncausal?** Yes, exactly (34.818505%). Noncausal because its solar input is the realized SITES measurement for the full future horizon — true perfect foresight, unavailable at real decision time.
- **How much of Arm B's fuel reduction is associated with poorer reliability?** Pooled total unmet energy is lower than Control's, but 75/123 origins (61%) are worse than Control individually, and the strict paired bootstrap test fails (upper bound +1,862.30 Wh/origin > 0); the project's own reliability gate already rejects this arm.
- **Which findings are established vs. hypotheses?** Established: the EBR-formula mechanism, A's defect-attributable 3.1556-point gap, B's noncausal input mechanism, B's and C's per-origin reliability failures, full origin/hour/demand/wind/state parity across all five arms (independently verified). Hypotheses: the fine-grained per-hour causal chain from forecast bias to specific dispatch decisions in A's and B's worst-regression origins.
- **Safest next experiment:** an offline, read-only derived-column analysis on a copy of the existing frozen telemetry (§8, item 1) — no new solver run, no new authorization needed.

**Governance decision unchanged by this investigation:** `winner: null`; no arm promotion-eligible; no file in `results/run_20261011T143130Z/` was modified; no execution authorization was created, consumed, or altered; no R5 work performed.
