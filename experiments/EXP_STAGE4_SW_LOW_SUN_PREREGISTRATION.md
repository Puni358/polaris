# POLARIS Preregistration: Stage 4 — SW Low-Sun Stored-Energy Protection (Confirmatory 2025 Holdout)

**Experiment Identifier:** `EXP-STAGE4-SW-LOW-SUN-2025-HOLDOUT`
**Design Version:** `STAGE4-PREREG-v1.0`
**Date (UTC):** 2026-10-05
**Governance Status:** `PREREGISTRATION FROZEN — NOT IMPLEMENTED — NOT EXECUTED`
**Governing Design:** `experiments/STAGE4_SW_SAFE_EFFICIENCY_RESEARCH_DESIGN.md` (design only; where this document is more specific, this document governs)
**Governing Holdout Record:** `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.md` / `.json`
**Governing Contracts (unchanged):** `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.md` / `.json`; `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION_ADDENDUM_NUMERICAL_BOUNDARY.md` / `.json`

This is a governance and preregistration document only. It does not implement, run, or tune any arm. No 2025 candidate outcome has been computed or inspected.

---

## 1. Experiment Identity and Scope

- **Scope:** research-only, synthetic demand and wind, Mount Nuolja (`ANS_NMS`).
- **Confirmatory population:** the 123 origins of 2025-05-01 to 2025-08-31 (Section 8).
- **Discovery/context population:** the 2024 S/SW campaign (`experiments/candidate_s_sw_campaign_2024/`). 2024 provides context only. No Stage 4 arm is executed on 2024 under this preregistration, and no 2024 result is cited as confirmatory evidence.
- **Production boundary:** no production file is modified (Section 15).

---

## 2. Background (Frozen Facts)

Control B (2024, archived): fuel 6603.9802 L; critical-first reliability 93.470303%; proportional reliability 83.694610%; SOC violations 0.

Candidate S (2024, archived): fuel 4804.4646 L (27.25% diesel saving); critical-first 93.834422%; proportional 83.799766%; SOC violations 0. Result: safety gates pass and diesel gate passes.

Candidate SW (2024, archived): fuel 4096.9668 L (37.96% saving); critical-first 93.494355%; proportional 82.603509%; SOC violations 0. Result: **proportional gate fails (−1.091101 pp). SW is not advanced.**

Stage 3 forensic telemetry analysis (observed): mean executed-hour reserve SW 18.3 kWh vs S 54.0 kWh; SW has about 601 kWh more total unmet energy than S, with about 428 kWh of the increase in 00–05 UTC. The reserve-protection mechanism is **inferred, not established**. Stage 3 did not run a counterfactual, so causality is not identified. Stage 4 is the counterfactual.

---

## 3. Hypotheses

- **H0 (null):** reserve protection does not explain the night loss. The loss is equally present in S-L and SW-L.
- **H1 (over-credit):** the renewable credit degrades reliability across the day, regardless of protection. Predicts SW-L still fails the proportional gate while S-L passes, and the wind contrast on proportional reliability stays negative with protection on.
- **H2 (protection removal at low sun):** the loss comes from removing stored-energy protection at low sun, where renewable credit is unreliable. Predicts SW-L passes the proportional gate.

H1 and H2 are not mutually exclusive. The interpretation rules are in Section 14.

---

## 4. The Five Arms

All five arms are executed on the 2025 confirmatory population, with identical execution machinery (Section 12).

| Arm | Renewable credit | Low-sun protection | Role |
|---|---|---|---|
| **Control B** | none (unconditional EBR) | — | Safety and fuel reference. Re-executed on 2025 (Section 9). |
| **S** | solar only | OFF | Reference. Must satisfy the identity S-L(OFF) = S. |
| **SW** | solar + wind | OFF | Reference. Must satisfy the identity SW-L(OFF) = SW. |
| **S-L** | solar only | ON | Efficiency reference; isolates protection under solar-only credit. |
| **SW-L** | solar + wind | ON | **Final candidate.** Tests whether SW's saving survives with protection restored at low sun. |

Identities (verified by unit tests before execution, Section 12.4):
- With protection OFF, S-L equals S, and SW-L equals SW.
- With protection ON at every hour (L_k = 1 everywhere), S-L and SW-L equal Control B.

---

## 5. Exact Equations

### 5.1 Notation

For origin `o` and origin-day hour index `t` in {0, …, 23}, horizon step `k` ranges over `{t, …, min(t+5, 23)}`. Efficiency `η = 0.92`. Time step `Δt = 1 h`.

- `c_k` = critical demand = `min(11,600 W, D_forecast[k])` (unchanged from the frozen adapter).
- `s_k` = forecast solar power, W, from `bundle.solar_generation.point` (unchanged).
- `w_k` = forecast wind power, W, from `bundle.wind_generation.point` (unchanged).
- `e_k` = solar elevation in degrees at horizon step `k`, per Section 6.
- `L_k = 1[e_k < 15°]` — low-sun indicator, per Section 7.

### 5.2 Equations

**Control B (frozen):**

`E_B[t] = (1/η) Σ_{k=t}^{min(t+5,23)} c_k · Δt`

**S (frozen):**

`E_S[t] = (1/η) Σ_{k=t}^{min(t+5,23)} max(0, c_k − s_k) · Δt`

**SW (frozen):**

`E_SW[t] = (1/η) Σ_{k=t}^{min(t+5,23)} max(0, c_k − s_k − w_k) · Δt`

**S-L (new):**

`E_SL[t] = (1/η) Σ_{k=t}^{min(t+5,23)} max(0, c_k − (1 − L_k)·s_k) · Δt`

**SW-L (new, final candidate):**

`E_SWL[t] = (1/η) Σ_{k=t}^{min(t+5,23)} max(0, c_k − (1 − L_k)·(s_k + w_k)) · Δt`

**Horizon edge (all arms, unchanged):** `E_stage2[23] = max(E_arm[23], E_term)` with `E_term = 100,000 Wh`. The terminal target is not modified by any arm.

### 5.3 Structural Properties (Checked by Unit Test)

1. If `L_k = 1` for all k, then `E_SL = E_SWL = E_B` exactly.
2. If `L_k = 0` for all k, then `E_SL = E_S` and `E_SWL = E_SW` exactly.
3. Pointwise ordering: `E_SW ≤ E_SWL ≤ E_B` and `E_S ≤ E_SL ≤ E_B`.
4. The combination is a per-hour replacement of the renewable credit at low sun. No additive EBR-plus-term combination and no `max(EBR, R)` form is used.

---

## 6. Solar-Elevation Implementation (Frozen, Not Corrected)

- **Module:** `clear_sky/compute_clearsky_2025.py` (SHA-256 `3ac68ee705e9a9ec68044687c5df79100082d9ab172d09baac70dde6be00ed54`). It mirrors `clear_sky/compute_clearsky.py` (2024, locked; SHA-256 `3a649a6ff9f227b5a1819f6cf577d896c6bc1488274a86ccdaaafc29a109c145`).
- **Library:** pvlib 0.16.1, `pvlib.location.Location(...).get_solarposition(times)['elevation']`.
- **Location:** latitude 68.362074° N, longitude 18.738752° E. No elevation argument supplied (pvlib default). No atmospheric assumptions supplied.
- **Timestamp convention:** the naive timestamp `T` of each forecast horizon hour (the `timestamp` column of the causal NWP file) is localized with `tz_localize("Etc/GMT-1")`.
- **Units:** degrees above the horizon.
- **Causality:** `e_k` depends only on the timestamp and the fixed location. It uses no forecast value, no realized value, and no state.
- **Equivalence:** the recomputed elevation matches the `solar_elevation` columns of the frozen feature matrices exactly (2025 CORRECTED: 8,736 rows, max |diff| 0.000000°; 2024 CORRECTED: 8,328 rows, max |diff| 0.000000°). The alternative `tz="UTC"` reading differs by up to 5.53° and matches zero rows.

### 6.1 Timestamp-Offset Caveat (Must Be Read With Every Result)

The implementation has a one-hour offset, which is **not corrected for Stage 4**. Because the naive timestamp is interpreted as UTC+1, the elevation computed at timestamp `T` is the true elevation at UTC instant `T − 1 h`. The observed SW_IN diurnal peak sits at 11:00 in the SITES timestamps, while local solar noon at this longitude is about 10:45 UTC. This is consistent with the SITES timestamps being UTC-labelled. The offset is a property of the frozen implementation that the 2024 campaign and the 2025 feature matrices already use. Correcting it would change the frozen implementation, so it is not done here. Any reported low-sun hour is therefore a low-sun hour in the frozen convention, and is not a physically exact low-sun hour.

---

## 7. The 15° Low-Sun Rule

`L_k = 1` if `e_k < 15°` (strict). `L_k = 0` otherwise, including at exactly 15°.

**Status: 15° is an existing research regime convention, NOT a physical constant and NOT a governance-authorized value.** It appears as the `Low_0_15` / `Mid_15_30` / `High_gt_30` bin in `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/cross_year_error_stability/CROSS_YEAR_ERROR_STABILITY_AUDIT.md` (predates the S/SW campaign) and in `EXP_CONFORMAL_TRAJECTORY_OFFLINE/run_offline_validation.py` line 119. It is frozen for this experiment. It must not be tuned, moved, or replaced after any holdout result is inspected. No other threshold is evaluated.

---

## 8. Exact 2025 Holdout Rule

**Population (frozen):** every 00:00 UTC `forecast_start` from **2025-05-01 through 2025-08-31 inclusive**. Expected: **123 origins, 2,952 origin-hours**.

**Inclusion:** an origin is included if its required inputs are complete (Section 8.1).

**Exclusion:** only for incomplete required inputs. No origin may be excluded on the basis of route, solar elevation, low-sun hours, candidate behaviour, forecast performance, reliability, diesel consumption, or any other outcome.

**Route is diagnostic only.** The population label `operating_mode = NORMAL` is an initial-state setting, not a router decision. Router step-0 reconstruction for 2025 gives EMERGENCY = 123, NORMAL = 0. This is recorded and not used for selection. This supersedes the design document's §14.2 wording "NORMAL-route origins", which is replaced by the frozen calendar rule above.

### 8.1 Input Completeness (Audited, Not Outcome-Based)

| Input | Source | Rows | NaN |
|---|---|---|---|
| Timestamps | SITES SW_IN timeline | 2,952 | 0 |
| Causal NWP (6 genuine variables, 24 h per origin) | `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` | 2,952 (123 origins) | 0 |
| Actual SW_IN (simulator-only realization) | `POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv` | 2,952 | 0 |
| Solar elevation (feature matrix) | `stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` | 2,952 | 0 |
| Clear-sky decomposition | `POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv` | 8,760 | 0 |

Result: PASS. Origins: 123 expected, 123 available, 0 missing.

Demand and realized wind are synthetic formulas with no data input. Forecast wind is the frozen baseline heuristic from the initial state.

### 8.2 Population Status

- 2025 candidate results inspected: **NO**.
- 2025 is untouched confirmatory data for the Stage 4 direction.
- The 2025 Stage 8.1 forecast metrics pre-date this direction and are not used for it.

---

## 9. NWP Provenance and Chain Equivalence

**Conclusion (governance resolution §1): SAME CAUSAL FORECAST CHAIN** for 2024 and 2025.

| Element | 2024 (campaign, locked) | 2025 (holdout) |
|---|---|---|
| Generator | `clear_sky/audit_clean_nwp_windows.py` (`c8f1a2204af1703296e32658e5d8890e2bd7f876d554a2b1a5ee46f1bc50ad21`) | `clear_sky/audit_clean_nwp_windows_2025.py` (`5d38d1c4976bffd53a114b652e610d299a713a0bd62e14031a9b661150ce724c`), replica with year substitution |
| NWP file | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` (`8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16`) | `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` (`2186382391b84ed5464982e036b0b7bc8208c6818b8131f29a382c6ee149dbb5`) |
| Manifest | — | `data/POLARIS_v0_1_future_weather_forecasts_2025_MANIFEST.json` (`534ed055d632950c474e4a38ff11b4b31f16955e6dff5968b7acabd31edf14cf`) |
| Source | Open-Meteo previous-runs API, `https://previous-runs-api.open-meteo.com/v1/forecast` | same |
| Model | `metno_seamless` | same |
| Variables | six `*_previous_day1` variables | same |
| Schema | ten columns, identical | identical |
| Imputation | none; PASS only if all 24 horizons are non-null for all six variables | same |
| Horizon convention | horizon 1 at the forecast_start hour (verified) | same |
| Origin source | locked benchmark CSV (365 origins) | derived from SITES SW_IN timeline (365 origins); same 00:00 UTC convention |

Known differences:
- **Origin source** differs (above). The forecast chain does not differ.
- **Label inconsistency:** the Stage 8.1 freeze labels the 2025 file "NWP (clean, audit-only)". The 2025 manifest describes it as an exact replica of the locked method. This is classified as a documentation label error, not a chain difference. The Stage 8.1 freeze is not altered.

**Release-time caveat (not verified, identical in both years):** the repository does not independently establish the real-world release time of `previous_day1` values relative to each origin. This preregistration does **not** claim that this proves real-time operational availability. The release convention is assumed, not verified. Every confirmatory claim must carry this caveat.

---

## 10. Leakage Controls

1. 2024 is discovery/context only. The 2025 population is the only confirmatory population.
2. No 2025 candidate outcome is inspected before execution is complete and the frozen analysis is run.
3. Actual (realized) solar is firewalled from forecast generation. Planning uses only `bundle.*.point` forecast quantities, the timestamp-based ephemeris, and state.
4. Realized wind is simulator-only. It enters the executor and post-hoc accounting, never a plan.
5. Realized demand enters the executor and post-hoc accounting only.
6. No post-hoc tuning of any value: the 15° threshold, the 100 kWh terminal, the 0.055 W τ, the efficiency, the SOC bounds, the diesel model, and the solver tolerances are all fixed.
7. No candidate-specific post-processing. The only permitted post-processing is the frozen numerical residue rule (τ = 0.055 W) from the addendum, applied identically to all arms.
8. Identical execution machinery across arms (Section 12.3).
9. Production files are unchanged (Section 15).

---

## 11. Safety Gates (Unchanged Contract, Evaluated on 2025)

A candidate must pass **all three** against Control B re-executed on the same 2025 origins:

1. **Critical-first reliability:** `ΔR_CF = R_CF(candidate) − R_CF(Control B) ≥ 0.00 pp`.
2. **Proportional critical reliability:** `ΔR_P = R_P(candidate) − R_P(Control B) ≥ 0.00 pp`.
3. **SOC floor:** zero realized SOC below 20.00% in any hour of any origin.

Reliability is aggregated over the 123 origins (2,952 hours) and computed exactly as in the frozen campaign:
- Critical-first: `Σ_t min(d_crit,t, served_t) / Σ_t d_crit,t`, with `d_crit,t = min(11,600 W, d_real,t)`.
- Proportional: `Σ_t served_t · d_crit,t / d_real,t / Σ_t d_crit,t`.

Safety precedes efficiency. A candidate failing any safety gate is rejected regardless of fuel.

---

## 12. Diesel Gate (Evaluated Only If All Safety Gates Pass)

For each candidate (S-L and SW-L) against Control B, with origin-paired saving `Δ_o = Fuel_ControlB(o) − Fuel_candidate(o)` in litres:

1. **Two-sided Wilcoxon signed-rank test** on `{Δ_o}`, with `p < 0.05`. Applied as a Holm adjustment across the two candidate diesel tests (S-L, SW-L), so the smaller p must be below 0.025 and the larger below 0.05.
2. **BCa 95% bootstrap CI** of the mean paired saving: lower bound **strictly > 0 L/origin**. Origin-paired resampling, 10,000 resamples, seed 42.

Both conditions are required. The 40% target is **not** a gate (Section 13).

---

## 13. 40% Target (Not a Gate)

Target: `(Fuel_ControlB − Fuel_SW-L) / Fuel_ControlB ≥ 0.40` over the 123 origins, on 2025.

The target is reported. It does not gate advancement. A candidate that passes every safety and diesel gate with a saving below 40% is a valid, reportable result. It does not satisfy the target.

---

## 14. Primary Endpoint, Factorial Contrasts, and Interpretation

### 14.1 Primary Endpoints

1. **Confirmatory gates (primary):** the three safety gates and the diesel gate (Sections 11–12), for SW-L and S-L against Control B.
2. **Primary decision candidate:** SW-L. S-L is the efficiency reference.

### 14.2 Factorial Contrasts (Frozen, Exactly These Four)

Each contrast is an origin-paired difference (per origin, in the stated unit), reported with a BCa 95% CI (Section 15, item 4). The contrasts are descriptive. They do not gate advancement.

| # | Contrast | Meaning |
|---|---|---|
| C1 | `SW − S` | Wind effect without protection |
| C2 | `SW-L − SW` | Protection effect under solar+wind |
| C3 | `S-L − S` | Protection effect under solar-only |
| C4 | `(SW-L − SW) − (S-L − S)` | **Interaction (primary mechanism diagnostic)** |

C4 is algebraically identical to `(SW-L − S-L) − (SW − S)`.

Outcomes for each contrast, in this priority order:
- **Primary outcome for C4:** per-origin proportional critical reliability (pp).
- Secondary outcomes for all contrasts: per-origin fuel (L), per-origin critical-first reliability (pp), total unmet (kWh), and curtailment (kWh).

Per-origin reliability uses the same formulas as Section 11 restricted to the origin's 24 hours.

No contrast may be substituted, added, or dropped after results are seen.

### 14.3 Interpretation Matrix

| Result on 2025 holdout | Interpretation | Action |
|---|---|---|
| SW-L passes all gates, saving ≥ 40%, CI > 0 | Target achieved safely | Document; second confirmatory holdout before any claim beyond research |
| SW-L passes all gates, saving < 40%, CI > 0 | Protection costs part of SW's saving | Report trade-off; do not claim the target |
| SW-L fails proportional; S-L passes; wind contrast on proportional reliability (SW-L − S-L) negative with CI excluding zero | H1 partly supported: wind credit degrades reliability even with protection | Abandon wind credit in daylight; keep S-L as the efficiency reference |
| SW-L fails proportional; S-L also fails | H2 not supported | Abandon low-sun protection direction; record failure mechanism as unresolved |
| SW-L passes; S-L passes; C4 CI excludes zero | Wind effect depends on protection (H2) | Report; any further work is a new preregistered design |
| Any candidate fails the SOC floor | Safety failure | Reject regardless of fuel |

---

## 15. Statistical Procedure (Frozen)

1. **Pairing:** origin-paired. Each origin contributes one paired difference per contrast or gate.
2. **Ordering:** differences are sorted by origin index before any analysis.
3. **Diesel test:** two-sided Wilcoxon signed-rank (Section 12), Holm across the two candidate diesel tests.
4. **Bootstrap:** BCa, 95%, 10,000 resamples of origins with replacement, seed 42 (`numpy.random.default_rng(42)`).
5. **Statistic:** mean of the paired difference (L/origin for fuel, pp for reliability).
6. **Accounting conventions reported in parallel:** proportional critical accounting and critical-first accounting, both as in Section 11.
7. **No post-hoc statistical choices:** no alternative test, transform, outlier removal, subgroup, or resample count is chosen after results are seen. The only permitted subgroups are the pre-declared night stratum (`L_k = 1` hours) and router-mode stratum.

---

## 16. Reporting

Required for every arm and every contrast: fuel (L), paired saving (L and %), median saving, diesel-on hours, startups, battery charge and discharge, curtailment, total unmet, critical unmet under both conventions, SOC minimum, EMERGENCY and NORMAL hour counts, residue-correction counts and magnitudes (τ rule), and the worst ten origins per contrast.

---

## 17. Implementation Boundary

Permitted (research-only) after this preregistration is frozen and hash-guarded:
- Stage 4 adapter.
- Stage 4 unit tests.
- Stage 4 runner.
- Stage 4 campaign artifacts.

Forbidden: any change to production code, the existing S/SW preregistration, the numerical-boundary addendum, or any frozen S/SW campaign artifact.

### 17.1 Required Startup Hash Guards

The runner must verify each of these SHA-256 values before execution and abort on mismatch:

| Guard | Path | SHA-256 |
|---|---|---|
| GAP19 solver | `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| DispatchPlan | `system/schemas/dispatch_plan.py` | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` |
| Causal NWP forecaster | `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` |
| S/SW adapter | `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/candidate_s_sw_adapter.py` | `a3ba73ad32ed2be20c0f197689081abf64402da41205a674fe76a15767e40de4` |
| S/SW preregistration (MD) | `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.md` | `1f018b1aba2651950b8cd5474ee9ea4dd2c6db6e9d9a584b1a5791eb59e80be5` |
| S/SW preregistration (JSON) | `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.json` | `3607876afea7cea169887faa3b92c7a21142e9fbc5bd38ac93a6b72351342ba4` |
| Numerical-boundary addendum (MD) | `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION_ADDENDUM_NUMERICAL_BOUNDARY.md` | `228474e1100d4ce4a1c1470198125d699ddd3d9c0bf1f91678f4373f8e1d0054` |
| Numerical-boundary addendum (JSON) | `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION_ADDENDUM_NUMERICAL_BOUNDARY.json` | `94c6f623a35628bd5f4efab40557c8fa99395fdf81b4c6c665ab0af968d7bfdd` |
| Solar elevation module | `clear_sky/compute_clearsky_2025.py` | `3ac68ee705e9a9ec68044687c5df79100082d9ab172d09baac70dde6be00ed54` |
| 2025 NWP file | `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` | `2186382391b84ed5464982e036b0b7bc8208c6818b8131f29a382c6ee149dbb5` |
| 2025 NWP manifest | `data/POLARIS_v0_1_future_weather_forecasts_2025_MANIFEST.json` | `534ed055d632950c474e4a38ff11b4b31f16955e6dff5968b7acabd31edf14cf` |
| Governance resolution (MD) | `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.md` | `22e67a16a90ef90fa88b248614a83d853511a33619548272535e05615314d7a7` |
| Governance resolution (JSON) | `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.json` | `f96fd97c812f44e88455c966c500a3874a99f07b8ae94744759d0fac6b461bf7` |

### 17.2 Frozen Telemetry Reference (2024, Read-Only)

Control B telemetry (2024) `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/hourly_trace_123_frozen_b/hourly_telemetry_123_frozen_b.json`, SHA-256 `13359f2742a0eecce14dc1c506ce0a933a9a5a441082120f83adf21d8c3f48e5`, used as discovery context only.

### 17.3 Identical Machinery

All five arms use `RobustTelemetryRunner`, the same research extractor, the same τ rule, and the same accounting. Only the `ebr_target_wh` construction differs between arms.

### 17.4 Required Unit Tests (Before Execution)

1. Per-hour replacement reproduces S and SW exactly when `L_k = 0` everywhere.
2. Per-hour replacement reproduces Control B exactly when `L_k = 1` everywhere.
3. Governed EBR branch at low sun reproduces `compute_governed_ebr` exactly.
4. Pointwise ordering in Section 5.3 (item 3) holds on the 2025 inputs.
5. Solar-elevation function reproduces the frozen feature matrix values (Section 6).

---

## 18. Advancement Criteria

All of the following must hold on the 2025 holdout:
- SW-L passes all three safety gates.
- The SW-L diesel gate passes (Section 12).
- The protection effect C2 is reported with its CI.
- The wind contrast (SW-L − S-L) on proportional reliability is non-negative, or its CI includes zero.
- A second confirmatory holdout (2026 prospective, or a further preregistered split) reproduces the safety result.

Any further efficiency work toward 40% must be a new preregistered design (for example the governed-minimum hybrid), not a re-tuning of SW-L.

---

## 19. Failure Criteria

A candidate fails if any of the following hold on the 2025 holdout:
1. `ΔR_CF < 0.00 pp`.
2. `ΔR_P < 0.00 pp`.
3. Any realized SOC below 20.00%.
4. Diesel gate not met (Wilcoxon not significant after Holm, or BCa lower bound ≤ 0), even if safety passes. The candidate is not advanced but is still reported.
5. Any genuine simultaneous charge/discharge violation (unresolved under τ = 0.055 W), or any optimizer infeasibility.
6. Fewer than 123 complete origins, or any unreported arm-hour.

**Abandonment (Section 18 of the design, adopted):** abandon the wind-credit-plus-protection direction if SW-L fails the proportional gate on the holdout while S-L passes and the wind contrast is significantly negative; if SW-L fails on both discovery and holdout in the same direction; if the solar-elevation input cannot be shown causal from the forecast chain; if the 2025 chain cannot be shown equivalent; or if low-sun protection causes curtailment large enough to offset the saving (reported as a finding about the realization rule, not a tuning opportunity).

---

## 20. Known Caveats

1. **Synthetic benchmark:** demand, realized wind, and the wind baseline are synthetic formulas. Results are research evidence and do not generalize to physical operation or physical wind regimes.
2. **Release-time semantics of `previous_day1` are not verified** by the repository (Section 9). Claims of real-time operational availability are not made.
3. **One-hour solar-elevation offset** is frozen and uncorrected (Section 6.1). The 15° boundary is therefore a convention in the frozen timestamp frame.
4. **15° is a research convention**, not a physical or governance constant (Section 7).
5. **Origin-source difference** between 2024 and 2025 (Section 9). The chain is the same, but the origin list is derived differently.
6. **Stage 3 mechanism is inferred.** Only the 2×2 factorial identifies the protection effect and the wind effect given protection, and only on the 2025 holdout.
7. **Population label NORMAL** is an initial-state setting. All 2025 origins are EMERGENCY at step 0 (Section 8).
8. **Control B on 2025 is re-executed**, because no archived 2025 Control B exists. Safety gates are therefore evaluated against a 2025 Control B run with the same machinery.
9. **The Holm adjustment** on the two diesel tests is applied here, which is a clarification of the design document's §12 family (six tests). The safety gates are deterministic threshold checks and carry no p-value.
10. **Design-doc supersessions recorded:** §14.2 "NORMAL-route origins" is superseded by the calendar rule (Section 8). §5 and §9 "S and SW not re-run" is superseded by re-execution of all five arms on 2025 (Section 4).

---

## 21. Production and Frozen-Artifact Boundary

- No production file is modified by this preregistration.
- The existing S/SW preregistration (MD and JSON), its numerical-boundary addendum (MD and JSON), and the frozen S/SW campaign artifacts under `experiments/candidate_s_sw_campaign_2024/` and `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/` are not modified.
- The governance resolution (MD and JSON) is not modified.
- No 2025 candidate outcome has been inspected.

---

## 22. Status

**PREREGISTRATION FROZEN.** This document was written and hashed before any Stage 4 implementation, execution, or 2025 candidate inspection. Its SHA-256 is recorded in the companion JSON, `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.json`. This Markdown must not be edited after that hash is recorded.
