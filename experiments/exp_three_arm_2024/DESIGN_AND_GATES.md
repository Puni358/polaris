# Design and Gates (proposed design, frozen for review only)

This is the design as described in M5 (consolidation brief) and the source protocol (`reports/source_prep/PROTOCOL.md` §4–§7, `PROTOCOL_ADDENDUM_D7a.md`). It is **not approved** (see DECISIONS_LOG).

Implemented in `scripts/run_three_arm_2024.py` (runner), `scripts/calibrate_arm_c.py` (Arm C calibration) and `scripts/gates_three_arm.py` (gates). Every unresolved setting is `null` in `config/EXPERIMENT_CONFIG.json`, and the code refuses to run with a `null` setting.

## 1. Common configuration (identical in every arm)

- **Planner:** Planner-CF v1.2 (`research_numerical_extractor_planner_cf_v1.py`, unmodified), HiGHS threads=1, priorities J1 unmet_crit > J_NC unmet_nc > J2 reserve slack > J3 fuel > J4 curtailment.
- **Executor:** `ResearchRealizationExecutor` (unmodified). Configs from `system/config/*.yaml` via `experiments/run_diesel_reduction_campaign.py:71-83`. Terminal target 100,000 Wh (unchanged). Critical ceiling 11,600 W.
- **Initial state:** `make_initial_state(fs − 1 h)` (`run_diesel_reduction_campaign.py:86-97`): 50% SoC, diesel off, 100 L fuel, last-observed demand 15,000 W and wind 4,500 W.
- **Population:** 123 origins, forecast_start 2024-05-01 … 2024-08-31 at 00:00; t0 = forecast_start − 1 h; 24 hourly re-plans each.
- **Cloud input:** current origin's package only (L1 fix, `scripts/causal_cloud_lookup.py`); hours beyond the package hold the package's last value.
- **Wind and demand forecasts:** `LocalBaselineForecastEngine` (persistence plus diurnal wave), identical in every arm.
- **Realized inputs:** solar = 2024 SITES `actual_SW_IN` → min(51·GHI, 60 kW); wind and demand = the canonical synthetic profiles.
- **Reserve elevation:** `SolarElevationProvider(None)` (pvlib, Etc/GMT-1), never the 2025 decomposition CSV.
- **Rule D:** OFF (M5; D3 PENDING).

## 2. Arms

| Arm | Solar forecast to planner and reserve | Label | Eligibility |
|---|---|---|---|
| PC-Control | causal-NWP γ=1, legacy geometry; governed EBR (`compute_governed_ebr`) | Baseline (keeps its documented 1 h solar-position error) | Denominator |
| A | causal-NWP γ=1, legacy geometry; PC-SW EBR (`compute_variant_sw_ebr`) | `LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT` | Decision-bearing vs Control (reproduction) |
| A-Fix | As A, except pvlib sun position and clear-sky are evaluated at label − 1 h (`scripts/solar_convention.py`). No timestamp is rewritten; cloud, wind, demand, reserve, optimizer, executor and gates are unchanged | `DIAGNOSTIC — NOT PROMOTION-ELIGIBLE` | Reported only |
| B | Realized SITES hourly SW_IN for t+1…t+24, revealed at decision time. Wind, demand and timestamps come from the same causal engine as the other arms. The bundle carries `NONCAUSAL_PERFECT_FORESIGHT_DIAGNOSTIC_ONLY` | `NONCAUSAL — DIAGNOSTIC — NOT DEPLOYABLE` | Never eligible. Enforced: `causal: false`, preflight rejects B in the E1 family, the gate verdict is fixed to `NONCAUSAL DIAGNOSTIC — NOT DEPLOYABLE — NEVER ELIGIBLE`, and `winner` is always `null` |
| C | γ̂ point forecast, clear-sky × (1 − c)^γ̂, with corrected geometry (identical to A-Fix: clear-sky from the label-corrected forecaster at cloud 0). The planner gets the point forecast; the EBR reserve gets the lower bound max(0, min(point, point + q_α(bin))). Needs a validated calibration artifact, and preflight blocks execution without one | `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE (CALIBRATED POINT + LOWER-BOUND RESERVE)` (D10a, M9; was `DIAGNOSTIC — …`) | Decision-bearing vs Control: in the E1 family {A, C} (D10 APPROVED, M7) |

## 3. Comparisons (reported separately)

1. **A vs A-Fix:** effect of correcting the forecaster's solar position. Diagnostic. No direction is assumed.
2. **A-Fix vs C:** corrected PC-SW vs the calibrated forecast and reserve. C uses the corrected geometry, so this pair differs only in the forecast and reserve method.
3. **Arms in the E1 family vs PC-Control:** the gated comparison against the governed baseline. The family is **{A, C} (D10 APPROVED, M7, as PROTOCOL §7)**, Holm m = 2. A-Fix is diagnostic only. The gate code evaluates E1 only over the configured family. Every arm's fuel, reliability and S1–S3 (and S4 if adopted) are reported regardless.
4. **B:** diagnostic upper bound on the value of perfect solar information. Never a winner.

## 4. Gates

| Gate | Definition | Status |
|---|---|---|
| S1 | ΔR_CF = R_CF(arm) − R_CF(PC-Control) ≥ 0.00 pp, aggregate | Recorded baseline gate (`planner_cf_statistics.py:7`) |
| S2 | ΔR_P ≥ 0.00 pp | Recorded baseline gate (`:8`) |
| S3 | Zero arm-hours with realized SoC < 20.00% | Recorded baseline gate (`:9`) |
| E1 | Two-sided paired Wilcoxon on per-origin fuel Δ (control − arm, unadjusted litres), Holm-adjusted across the fixed configured family p < 0.05, AND that arm's iid BCa 95% (two-sided) lower bound > 0 L/origin (10,000 resamples, `default_rng(42)`); no CI multiplicity correction. Counts only if S1–S4-strict pass | Recorded. **Family: {A, C} (D10 APPROVED, M7)** |
| S4 (point) | U(arm) ≤ U(PC-Control): total realized unmet Wh (Σ `unmet_load` × 1 h, fsum) over the identical paired (origin, hour) cells. Ties pass. No tolerance. Any missing, unpaired, duplicate, non-finite or non-optimal cell makes it NOT EVALUABLE, which counts as FAIL. Also reported vs Arm A | **APPROVED (D2, M6)** |
| S4-strict | Reported separately. Stationary block bootstrap of mean paired per-origin ΔU (chronological), mean block 10 days, 10,000 resamples, seed 42; PASS iff the upper bound ≤ 0 Wh/origin. Both S4 and S4-strict must pass | **ADOPTED (D6, M6).** ΔU = U_arm − U_ctrl (positive = worse), so upper ≤ 0 is the non-regression direction (verified). Seed 42 is the project lead's decision (M7). Interval: two-sided 95% upper (97.5th percentile), **APPROVED (M8)** |
| T40 | ≥ 40% fuel reduction | Report-only |

Neither S4 nor S4-strict has been silently chosen or dropped. Execution is blocked until D2 and D6 are decided.

**Further unresolved gate settings** (each `null` in the config; preflight and `gates_three_arm.evaluate` refuse while any is unresolved):
- **G-a (D6):** S4-strict interval, one-sided 95 % upper bound or the upper end of a two-sided 95 % interval. The protocol says "upper 95 % bound" without saying which.
- **G-b (D6):** S4-strict bootstrap seed. None is recorded. E1's `default_rng(42)` belongs to E1's BCa and is not assumed to carry over.
- **G-c (D4):** the primary fuel metric, unadjusted or SoC-parity-adjusted. If adjusted, the fuel-per-kWh factor f is needed, and no repository document defines it.
- **G-d (D10):** the E1 Holm family.
- **Block length and resamples for S4-strict** (10 days, 10,000) are PROPOSED, not APPROVED.

**Rule:** lower fuel with any applicable reliability gate failing is **not an improvement**.

**Reporting for every arm:** fuel (L, % vs Control), U, critical unmet (first and proportional), non-critical unmet, R_CF, R_P, ΔR_CF, ΔR_P, SoC < 20% hours, min SoC, curtailment, diesel-on hours, starts, fuel-starvation hours, optimizer status counts, busbar violations, end SoC, held-cloud hours.

**Invalid runs:** any failed origin or hour makes the arm INVALID. Every gate then reads NOT EVALUABLE, which counts as FAIL. No imputation, no dropped origins.

## 5. Statistical limits

- The 123 origins are consecutive days. Weather persistence makes them serially correlated (lag-4 residual autocorrelation is documented in `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:22`, cited in PROTOCOL.md §7). The iid Wilcoxon and BCa in E1 therefore overstate the effective sample size.
- The block-bootstrap intervals are reported as a **separate secondary analysis**. They do not replace E1 unless D6 says so.
- Episodes reset daily (50% SoC, 100 L), so the results describe day-scale behaviour, not seasonal battery or fuel management.
- Wind and demand are synthetic, and their forecasts are biased. Realized PV is a proxy (51·GHI), **not field-validated PV performance**.

## 6. What this experiment cannot show

- The 2024 May–Aug window **was used in previous campaigns** (`EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024`, `candidate_s_sw_campaign_2024`). It is **not a fresh independent holdout**. Results are offline-benchmark evidence only.
- It cannot certify final model superiority or that the 40% diesel-reduction goal has been reached.
- The quarantined 2025 window is spent and is not used. No 2025 file is read.

## Decision pass 2026-10-11 (after M6)

See `reports/DECISION_RESOLUTION_2026-10-11.md`.
- **Decided:** D2 (S4 point) APPROVED. D4 primary metric = unadjusted litres, APPROVED. D6: strict S4, method, block and resamples APPROVED; seed 42 recorded under the M6 instruction.
- **Open:**
  - D6 interval (recommended two-sided 95% upper).
  - D10 family conflict.
  - The D4 secondary SoC-parity application (recommended per-origin; the formula and f ∈ {0.30, 0.75} are in PROTOCOL §7).
  - Arm C A1–A6 recommendations.
- **Correction:** item G-c above was wrong. f is defined in PROTOCOL §7.

## Decision pass 2026-10-11 (after M7)

See `reports/DECISION_RESOLUTION_M7_2026-10-11.md`.
- **Decided:** D10 = {A, C} (G-d closed). D6 seed 42 confirmed as the project lead's decision (G-b closed).
- **Open:** G-a, the D6 interval (project-lead proposal: two-sided 95% upper); the D4 secondary application (per-origin recommended); Arm C A1–A6 and A8; D5 values.

## Decision follow-up 2026-10-11 (after M8)

See `reports/DECISION_FOLLOWUP_M8_2026-10-11.md`.
- **Decided:** D6 fully approved, including the interval (G-a closed).
- **New blocker D10a:** PROTOCOL §7 classes C as a "Research-only candidate", while the D7a addendum labels C `DIAGNOSTIC`. The E1 family {A, C} (D10) and "nothing promotion-eligible" are unaffected. Amendment proposed in `reports/PROPOSED_AMENDMENT_D7a-1.md`; the runner's C label is unchanged until it is approved.
- **Still open:** D4 secondary application; Arm C A1–A6 and A8; D5 values and two unverified citations.

## M9 (2026-10-11)

See `reports/DECISION_RESOLUTION_M9_2026-10-11.md`.
- **D10a resolved:** C is a research-only candidate (PROTOCOL §7), not promotion-eligible; `PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md`. A-Fix stays a diagnostic; B stays noncausal and never eligible; nothing is promotion-eligible.
- **D4 secondary:** applied per origin; reported with f = 0.30 and 0.75; never decision-bearing.
- **New reported diagnostics:** `arm_c_evaluation_coverage` (per-bin coverage of C's lower bound after the run); D7a §6 items J2 reserve shortfall, fuel-exhausted hours, mean final SoC.
- **Interpretation:** C vs PC-Control mixes the geometry fix and the calibration; C vs A-Fix isolates the calibration (diagnostic).
