# POLARIS — N6 Causal Data Contract Resolution & Hourly RHC Design Report

**Document ID:** `N6_CAUSAL_CONTRACT_AND_HOURLY_RHC_DESIGN_REPORT.md`  
**Tracking ID:** `POLARIS-N6-RHC-CAUSAL-AUDIT-2026-10-21`  
**Date:** 2026-10-21  
**Working Directory:** `/home/punith-bs/01polaris (Copy)`  
**Audit Scope:** Read-Only Source Inspection, Causal Contract Forensic Audit, and Scratch-Only Implementation Specification  
**Execution Clearance:** Strictly Read-Only Investigation (Zero solver solves, zero simulation steps, zero benchmarks, zero production/MDR edits)  
**Governance Invariants:** `winner: null` preserved; 2025 blind data quarantined; model/data hashes verified; `tau_cont` / `epsilon_tol` unset.

---

## 1. Executive Summary & Direct Core Answer

### Direct Answer to the Core Question:
> **What is the smallest causally valid hourly RHC evaluation we can run using the existing artifacts, without changing N6's original data contract or introducing look-ahead?**
>
> **Under strict operational causality, ZERO hours of a rolling 24-hour hourly RHC can be run using existing offline artifacts alone.**
>
> **The Exact Physical and Contractual Reasons:**
> 1. **N6's Original Data Contract Requires 36 Specific Features:** The frozen N6 model ([`stage8_1_CORRECTED_candidate_37feature_model.joblib`](file:///home/punith-bs/01polaris%20%28Copy%29/stage8_1_CORRECTED_candidate_37feature_model.joblib) / [`candidate_n6_model.joblib`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/candidate_n6_model.joblib)) strictly requires a $(24, 36)$ feature matrix. Two mandatory features are `pred_stage4_clean` (Feature 34) and `clean_attenuation` (Feature 35).
> 2. **Stage 4 / Chronos-2 Predictions Only Exist for 00:00 UTC:** As proven by [`stage3/stage3b_cloud_nwp_predictions.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage3/stage3b_cloud_nwp_predictions.csv) and [`stage7/.../build_clean_stage4_baseline.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/build_clean_stage4_baseline.py), Chronos-2 transformer predictions were computed offline exclusively for the 347 origins at `00:00:00 UTC`. There are zero Chronos-2 predictions in the repository for any intra-day origin ($01:00 \dots 23:00\text{ UTC}$).
> 3. **MEPS 18Z Lead Truncation at Lead 30:** MET Norway MEPS NWP records in [`cache_full_acquisition/`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/cache_full_acquisition/) were clamped to lead 30 due to an upstream query bug on `2024-02-01T18Z` ([`fetcher.py` lines 187–195](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/fetcher.py#L187-L195)). For any decision origin $t_k \ge 02:00\text{ UTC}$, a 24-hour lookahead from Day $D-1$ 18Z requires leads $\ge 31$ (up to lead 53 at 23:00 UTC), which were never acquired.
> 4. **GAP19 Optimizer Requires Exactly 24 Horizon Steps:** [`gap19_highs_native.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/gap19_highs_native.py) enforces $H=24$ across all matrix dimensions (`num_base_vars = 360`, `num_total_vars = 408`). It cannot solve a shrinking intra-day horizon ($H_k = 24 - k$) without code refactoring or synthetic padding.
>
> **The Closest Scientifically Defensible Alternatives:**
> * **Alternative 1 (Retrospective Rolling-Slice Experiment — Recommended for Controller Validation):** Run hourly RHC across 168 hours (or 8,304 hours) by rolling across adjacent rows of `candidate_k_2024_clean_matrix.parquet` while recalculating the 14 telemetry context features dynamically from pre-decision history. This exercises the true hourly closed-loop RHC sequence (re-optimizing every hour, committing strictly $u_0$, continuous physical state propagation), with the explicit, documented caveat that rows crossing midnight introduce an **8.25-hour retrospective NWP cycle lookahead** for midday hours.
> * **Alternative 2 (Causal 168-Hour Window with Targeted Lead Acquisition):** Download MEPS 18Z leads 31–53 for just 8 days (June 1–8, 2024; ~120 KB total from MET Norway THREDDS) and run Chronos-2 transformer inference for those 168 hours. This enables a 100% causally valid, zero-lookahead hourly RHC evaluation.

---

## 2. Authoritative Governance Resolution

### 2.1 Resolution of the OD-02 vs. OD-02-C Conflict

An apparent conflict exists in repository documentation regarding the terminal solar alignment contract:

1. **The Canonical Frozen Contract (MDR Pass 22 & Pass 23):**
   * In [`POLARIS_MASTER_DECISION_REGISTER.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_MASTER_DECISION_REGISTER.json) (the machine-readable register, version `1.9.13`), the latest ratified entry is **Pass 23 (2026-10-19)** (`amendment_2026_10_19_twenty_third_pass_od02_freeze`).
   * In [`N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md` lines 1033–1035](file:///home/punith-bs/01polaris%20%28Copy%29/N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md#L1033-L1035), Decision **OD-02 is formally FROZEN**:
     > *"Decision OD-02 is FROZEN. The time-alignment contract (solar point forecast shifted 1..23 -> 0..22, step 23 fallback to 0.0 W/m², demand/wind/EBR unshifted, Policy B pointwise maximum) is sealed for pilot evaluation."*
   * Rationale: Retains runtime dependency isolation and prevents introducing unverified offline files (`POLARIS_v0_1_clearsky_decomposition.csv`). The Arctic polar-day midnight solar potential ($1.2 \dots 6.8\text{ W/m}^2$) is accepted as a documented operational boundary condition.
2. **The Status of Pass 24 / OD-02-C:**
   * At the very bottom of [`POLARIS_MASTER_DECISION_REGISTER.md` lines 1056–1063](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_MASTER_DECISION_REGISTER.md#L1056-L1063), a draft "Pass 24" entry claims Decision OD-02-C deprecated the `[0.0]` fallback in favor of Candidate C.2 (clear-sky ratio).
   * **Forensic Audit Finding:**
     * `POLARIS_MASTER_DECISION_REGISTER.json` does **not** contain Pass 24 or `OD-02-C`.
     * `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md` does **not** contain Pass 24.
     * The version header in `POLARIS_MASTER_DECISION_REGISTER.md` line 3 was **never incremented** beyond Pass 23 / v1.9.13.
     * The cited sensitivity solve (`DIAG-GATEC-U0-SENSITIVITY-2026-10-20`) was executed via [`scratch/run_od02_boundary_diagnostic(23hr_error).py`](file:///home/punith-bs/01polaris%20%28Copy%29/scratch/run_od02_boundary_diagnostic%2823hr_error%29.py#L51-L60) using synthetic flat 500 kW demand and synthetic linear solar, while the formal specification [`scratch/SPEC_OD02_DIAGNOSTIC_PRE_EXECUTION.md` line 6](file:///home/punith-bs/01polaris%20%28Copy%29/scratch/SPEC_OD02_DIAGNOSTIC_PRE_EXECUTION.md#L6) explicitly recorded: `Gate C STRICTLY NOT AUTHORIZED`.
   * **Authoritative Verdict:** **OD-02-C is an unratified scratch draft.** The binding governance standard in MDR v1.9.13 remains **OD-02 (FROZEN with zero terminal fallback)**.
   * However, [`system/evaluation/n6_multi_origin_harness/adapters.py` lines 632–699](file:///home/punith-bs/01polaris%20%28Copy%29/system/evaluation/n6_multi_origin_harness/adapters.py#L632-L699) (`_align_n6_bundle_od02`) was modified to execute Candidate C.2. Running Candidate C.2 in an evaluation without explicit owner authorization constitutes a governance discrepancy.
   * **Crucial Hourly RHC Invariant:** In true hourly RHC, dispatch step 23 is **never executed physically** on the microgrid ($u_0$ uses raw index 1). The first-hour control action $u_0$ is completely decoupled from terminal solar under normal non-emergency reserves.

---

### 2.2 Approved Terminal-Target and Reserve Configuration

1. **Decision OD-01 (Dynamic Terminal Reserve Target):**
   * Approved in MDR Sections 38.1.1 and 39.1.3; implemented in [`system/evaluation/n6_multi_origin_harness/adapters.py` line 821](file:///home/punith-bs/01polaris%20%28Copy%29/system/evaluation/n6_multi_origin_harness/adapters.py#L821) (`_prepare_gap19_terminal_target_config`):
     $$\text{terminal\_target\_wh} = \text{initial\_e\_wh} - \text{min\_e\_wh}$$
   * **Why this is critical:** In [`gap19_highs_native.py` line 304](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/gap19_highs_native.py#L304), the Layer C terminal constraint enforces $E_{\text{next}}[23] + s_{J2}[23] \ge E_{\text{stage2\_target}}[23] + E_{\min}$, where $E_{\min} = 40,000\text{ Wh}$ ($20\%$ SOC).
   * Setting `terminal_reserve_model: "INITIAL_STATE"` directly (as the previous runner did) sets $E_{\text{stage2\_target}}[23] = \text{initial\_e\_wh} = 160,000\text{ Wh}$, forcing the required target to $160,000 + 40,000 = 200,000\text{ Wh}$ ($100\%$ SOC). Because battery max capacity is $95\%$ ($190,000\text{ Wh}$), GAP19 is mathematically forced into a **$10\text{ kWh}$ terminal slack violation** on every solve, forcing full-power diesel generation.
   * By calling `_prepare_gap19_terminal_target_config`, `terminal_target_wh` is set to $160,000 - 40,000 = 120,000\text{ Wh}$. GAP19 then adds $E_{\min} = 40,000\text{ Wh}$, yielding exactly $160,000\text{ Wh}$ ($80\%$ SOC), which is perfectly feasible and eliminates all artificial terminal penalties.
2. **Policy B Reserve Envelope:**
   * Approved in MDR Section 4 item 7; implemented in [`adapters.py` line 1113](file:///home/punith-bs/01polaris%20%28Copy%29/system/evaluation/n6_multi_origin_harness/adapters.py#L1113) (`_prepare_gap19_policy_b_config`):
     $$\text{reserve\_envelope}[t] = \max(\text{critical\_reserve\_6h}[t], \text{conformal\_ebr}[t])$$

---

## 3. N6 Causal-Input Contract & 36-Feature Inventory

The authoritative N6 feature contract was audited against [`polaris_inference_runner.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/polaris_inference_runner.py), [`CANDIDATE_N_MANIFEST.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json), and [`feature_availability_ledger.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/operational_availability_audit/feature_availability_ledger.csv):

### Feature-Level Breakdown (36 Features)

| # | Feature Name | Category | Underlying Source & Timestamp Semantics | Earliest Availability | Arbitrary Hourly Origin? | Archived Matrix Reusability & Risk |
|---|---|---|---|---|---|---|
| **1** | `month` | Astronomical | Calendar month of target timestamp $t_v = t_0 + (h-1)\text{h}$ | Known a priori | **YES** | **SAFE**: Pure calendar arithmetic. |
| **2** | `hour` | Astronomical | UTC hour of target timestamp $t_v \in [0, 23]$ | Known a priori | **YES** | **SAFE**: Pure calendar arithmetic. |
| **3** | `solar_elevation` | Astronomical | Solar elevation angle ($\alpha$) at site at $t_v$ via SPA / pvlib | Known a priori | **YES** | **SAFE**: Deterministic orbital ephemeris. |
| **4** | `solar_zenith` | Astronomical | Solar zenith angle ($90^\circ - \alpha$) at $t_v$ | Known a priori | **YES** | **SAFE**: Deterministic orbital ephemeris. |
| **5** | `clearsky_ghi` | Astronomical | Ineichen clear-sky GHI with Linke turbidity at $t_v$ | Known a priori | **YES** | **SAFE**: Deterministic radiative transfer. |
| **6** | `fc_cloud_cover` | Surface NWP | MEPS 18Z total cloud cover (%) valid at $t_v$; lead $= 5+h$ | $D-1$ ~20:15 UTC | **NO** (needs NWP) | **LEAKAGE RISK**: Hours crossing midnight consume $D$ 18Z before publication. |
| **7** | `fc_temperature_2m` | Surface NWP | MEPS 18Z 2m temperature ($^\circ\text{C}$) valid at $t_v$; lead $= 5+h$ | $D-1$ ~20:15 UTC | **NO** (needs NWP) | **LEAKAGE RISK**: Same NWP vintage boundary. |
| **8** | `fc_relative_humidity_2m` | Surface NWP | MEPS 18Z 2m relative humidity (%) valid at $t_v$; lead $= 5+h$ | $D-1$ ~20:15 UTC | **NO** (needs NWP) | **LEAKAGE RISK**: Same NWP vintage boundary. |
| **9** | `cloud_frac` | Surface NWP | $\text{fc\_cloud\_cover} / 100.0 \in [0.0, 1.0]$ | $D-1$ ~20:15 UTC | **NO** (needs NWP) | **LEAKAGE RISK**: Same NWP vintage boundary. |
| **10** | `ctx_std_3h` | Telemetry | $\sigma(\text{SW\_IN})$ over trailing 3h $[t_0-3\text{h}, t_0)$ | $t_0$ (instantaneous) | **YES** (from SCADA) | **SAFE** if dynamically recomputed from fixture history $[t_{\text{now}}-3\text{h}, t_{\text{now}})$. |
| **11** | `ctx_std_6h` | Telemetry | $\sigma(\text{SW\_IN})$ over trailing 6h $[t_0-6\text{h}, t_0)$ | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **12** | `ctx_std_12h` | Telemetry | $\sigma(\text{SW\_IN})$ over trailing 12h $[t_0-12\text{h}, t_0)$ | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **13** | `ctx_std_24h` | Telemetry | $\sigma(\text{SW\_IN})$ over trailing 24h $[t_0-24\text{h}, t_0)$ | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **14** | `ctx_abs_change_1h` | Telemetry | $\|\text{SW\_IN}[t_0-1] - \text{SW\_IN}[t_0-2]\|$ | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **15** | `ctx_abs_change_3h` | Telemetry | $\|\text{SW\_IN}[t_0-1] - \text{SW\_IN}[t_0-4]\|$ | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **16** | `ctx_abs_change_6h` | Telemetry | $\|\text{SW\_IN}[t_0-1] - \text{SW\_IN}[t_0-7]\|$ | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **17** | `ctx_max_diff_6h` | Telemetry | $\max \|\Delta \text{SW\_IN}\|$ over trailing 6 hours | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **18** | `ctx_mean_diff_6h` | Telemetry | Mean consecutive difference over trailing 6h | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **19** | `ctx_slope_6h` | Telemetry | OLS regression trend slope of $\text{SW\_IN}$ over trailing 6h | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **20** | `ctx_kt_std_6h` | Telemetry | $\sigma(k_t)$ where $k_t = \text{SW\_IN} / \text{GHI}_{\text{cs}}$ over trailing 6h | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **21** | `ctx_last_obs` | Telemetry | Last station observation $\text{SW\_IN}[t_0-1\text{h}]$ | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **22** | `ctx_mean_24h` | Telemetry | $\mu(\text{SW\_IN})$ over trailing 24 hours | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **23** | `ctx_max_24h` | Telemetry | $\max(\text{SW\_IN})$ over trailing 24 hours | $t_0$ | **YES** | **SAFE** if dynamically recomputed. |
| **24** | `terrain_horizon_elevation_deg` | Topography | Horizon elevation profile angle at solar azimuth $\psi(t_v)$ | Static | **YES** | **SAFE**: Static 50m DEM ray-tracing lookup. |
| **25** | `terrain_elevation_margin_deg` | Topography | $\alpha_{\text{elev}}(t_v) - \theta_{\text{horizon}}(\psi(t_v))$ | Static | **YES** | **SAFE**: Deterministic geometry. |
| **26** | `terrain_solar_obstruction_flag` | Topography | Binary obstruction flag: $\mathbf{1}_{\{\Delta \theta \le 0^\circ\}}$ | Static | **YES** | **SAFE**: Deterministic geometry. |
| **27** | `clearsky_ghi_terrain_adjusted` | Topography | Terrain-adjusted GHI ($DHI_{\text{cs}}$ if shaded else $GHI_{\text{cs}}$) | Static | **YES** | **SAFE**: Deterministic radiative geometry. |
| **28** | `u700` | NWP Winds | 700 hPa zonal wind from MEPS 18Z; lead $= 5+h$ | $D-1$ ~20:15 UTC | **NO** (needs NWP) | **LEAKAGE / NaN**: Missing for leads 25..29 in archive. |
| **29** | `v700` | NWP Winds | 700 hPa meridional wind from MEPS 18Z; lead $= 5+h$ | $D-1$ ~20:15 UTC | **NO** (needs NWP) | **LEAKAGE / NaN**: Missing for leads 25..29 in archive. |
| **30** | `lwp_18z_fc` | NWP Physics | MEPS 18Z cloud liquid water path at 700 hPa; lead $= 5+h$ | $D-1$ ~20:15 UTC | **NO** (needs NWP) | **LEAKAGE RISK**: Vintage boundary issue crossing midnight. |
| **31** | `iwp_18z_fc` | NWP Physics | MEPS 18Z cloud ice water path at 700 hPa; lead $= 5+h$ | $D-1$ ~20:15 UTC | **NO** (needs NWP) | **LEAKAGE RISK**: Vintage boundary issue crossing midnight. |
| **32** | `lwp_x_cloud_18z` | Interaction | $\text{lwp\_18z\_fc} \times \text{cloud\_frac}$ | $D-1$ ~20:15 UTC | **NO** | Inherits NWP dependencies. |
| **33** | `elevation_x_cloud_frac` | Interaction | $\text{solar\_elevation} \times \text{cloud\_frac}$ | $D-1$ ~20:15 UTC | **NO** | Inherits NWP dependencies. |
| **34** | `pred_stage4_clean` | Baseline Cond. | Stage 4 blended baseline: $w_h \cdot \text{Chronos2} + (1-w_h) \cdot \text{phys}$ | $t_0 = 00:00\text{ UTC}$ | **NO** (needs Stage 3b) | **MISSING ARTIFACT**: Only pre-computed for 00:00 UTC origins. |
| **35** | `clean_attenuation` | Baseline Cond. | $\text{clearsky\_ghi} - \text{pred\_stage4\_clean}$ | $t_0 = 00:00\text{ UTC}$ | **NO** | Inherits Chronos-2 dependency. |
| **36** | `elevation_x_transition_cloud` | Interaction | $\alpha_{\text{elev}} \times \mathbf{1}_{\{0.2 \le \text{cloud\_frac} < 0.6\}}$ | $D-1$ ~20:15 UTC | **NO** | Inherits NWP dependencies. |

---

## 4. Telemetry and Realized-Value Temporal Alignment

### 4.1 SITES Observation & Aggregation Truth (D7 Reconciliation)
Authoritative verification from [`experiments/exp_three_arm_2024/reports/source_prep/d7/D7_VERIFICATION_REPORT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/experiments/exp_three_arm_2024/reports/source_prep/d7/D7_VERIFICATION_REPORT.md) and [`d7_out.txt`](file:///home/punith-bs/01polaris%20%28Copy%29/experiments/exp_three_arm_2024/reports/source_prep/d7/d7_out.txt):
* **Raw Sensor Basis:** Nuolja Middle Station pyranometer records 10-minute period-ending irradiance with header `TIME ZONE: UTC+1` (fixed, no DST).
* **Hourly Aggregation Formula:** The canonical hourly file `POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv` groups records with `floor('h')`:
  $$\text{Label } HH:00 = \text{mean of raw readings at } [HH:00, HH:10, HH:20, HH:30, HH:40, HH:50]$$
* **Physical Interval Represented:** Because each 10-minute timestamp is period-ending, reading $HH:00$ covers $[(HH-1):50, HH:00]$ and reading $HH:50$ covers $[HH:40, HH:50]$. Therefore, hourly observation $HH:00$ represents the physical window:
  $$[(HH-1):50, HH:50] \quad \text{with midpoint at } HH:20\text{ UTC+1 } ((HH-1):20\text{ UTC})$$

### 4.2 Concrete Index and Timestamp Mapping Table
For a representative forecast origin $t_0 = \text{2024-06-01T00:00:00Z}$:

| Step Index | N6 Raw Index | N6 Stamped Valid Time ($t_v$) | OD-02 Dispatch Step ($k$) | OD-02 Stamped Valid Time | Physical Interval Transition $[t_k, t_{k+1}]$ | Realized Fixture Actual Consumed | Evaluated Actual Observation Stamped | Solar Value Injected into Optimizer |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| — | **0** | `00:00:00Z` | *(dropped)* | — | — | — | — | *Dropped by OD-02 shift* |
| **1** | 1 | `01:00:00Z` | **Step 0** | `01:00:00Z` | $[00:00, 01:00]$ | Fixture row 3649 | `01:00:00Z` | $\hat{P}_{\text{solar}}[0] = P_{\text{raw}}[1]$ |
| **2** | 2 | `02:00:00Z` | **Step 1** | `02:00:00Z` | $[01:00, 02:00]$ | Fixture row 3650 | `02:00:00Z` | $\hat{P}_{\text{solar}}[1] = P_{\text{raw}}[2]$ |
| **3** | 3 | `03:00:00Z` | **Step 2** | `03:00:00Z` | $[02:00, 03:00]$ | Fixture row 3651 | `03:00:00Z` | $\hat{P}_{\text{solar}}[2] = P_{\text{raw}}[3]$ |
| $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ |
| **23** | 23 | `23:00:00Z` | **Step 22** | `23:00:00Z` | $[22:00, 23:00]$ | Fixture row 3671 | `23:00:00Z` | $\hat{P}_{\text{solar}}[22] = P_{\text{raw}}[23]$ |
| **24** | *(none)* | *(missing)* | **Step 23** | `24:00:00Z` | $[23:00, 24:00]$ | Fixture row 3672 | `00:00:00Z` ($D+1$) | **OD-02 Zero Fallback** (`0.0 W`) *(or C.2 Clear-Sky Ratio)* |

### 4.3 Why Direct Mapping (Index 0 $\to$ Step 0) is Physically Contradicted
* In [`simulator.py` lines 38–46](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py#L38-L46), dispatch step 0 advances the plant across the forward hour $[t_0, t_0+1\text{h}]$ and evaluates physical conservation against `actuals_next_step["actual_SW_IN"]` (stamped $t_0+1\text{h}$).
* If raw index 0 were mapped to dispatch step 0, dispatch step 0 would receive N6's prediction stamped $t_0 + 0\text{h}$ (covering $[t_0-10\text{m}, t_0+50\text{m}]$), creating a **1-hour backward lag** relative to the realized environmental conditions ($t_0+1\text{h}$) against which the transition is evaluated.
* Therefore, OD-02's shift (`raw[1:] + [terminal]`) is an **intentional physical synchronization**, not an accidental off-by-one bug.
* **Crucial Hourly RHC Implication:** Because an hourly RHC loop commits **strictly dispatch step 0** ($u_0$), the physical action executed on the microgrid is **always raw N6 index 1**. The terminal slot 23 is never executed physically on the plant.

---

## 5. Audit of Previous Evaluation (`scratch/run_authorized_n6_gap19_evaluation.py`)

A read-only audit of [`scratch/run_authorized_n6_gap19_evaluation.py`](file:///home/punith-bs/01polaris%20%28Copy%29/scratch/run_authorized_n6_gap19_evaluation.py) and its run artifacts ([`scratch/authorized_n6_gap19_eval_2024/`](file:///home/punith-bs/01polaris%20%28Copy%29/scratch/authorized_n6_gap19_eval_2024/)) confirms all reported defects:

1. **Daily Re-Planning Only:** Line 488 loops over 347 origins. Line 189 calls `n6_engine.predict` once, and line 207 calls `optimizer.optimize` once per origin. Exactly 347 optimization solves were executed in total for Mode B.
2. **Open-Loop Plan Execution:** Lines 218–250 execute all 24 hours of each daily plan open-loop via a loop:
   ```python
   for t in range(24):
       curr_st_n6 = simulator.step(curr_st_n6, step_plan, future_actuals[t])
   ```
   Zero intermediate re-forecasting or re-optimization occurred at hours $1 \dots 23$.
3. **Discontinuous Episodic State Resets:** Lines 149–171 hardcode `initial_soc_pct = 80.0` and `initial_fuel_l = 500.0` at the start of every origin. The ending state at hour 24 was discarded; the microgrid reset to 80% SOC and 500 L fuel every midnight.
4. **Terminal Target Violation Bug:** Line 194 set `cfg_n6["terminal_reserve_model"] = "INITIAL_STATE"` and bypassed `_prepare_gap19_terminal_target_config`. In GAP19 line 304, this enforced $E_{\text{next}}[23] + s_{J2}[23] \ge 160\text{ kWh} + 40\text{ kWh} = 200\text{ kWh}$ against a 190 kWh maximum capacity ceiling. This guaranteed an unavoidable $10\text{ kWh}$ slack violation on J2 every day, forcing continuous full-power diesel generation and corrupting fuel burn to 18,298.3 L.
5. **Policy B Bypass:** Line 193 set `cfg_n6["ebr_target_wh"] = aligned_bundle_n6.metadata["ebr_target_wh"]` directly, bypassing `_prepare_gap19_policy_b_config` and failing to compute the pointwise maximum with the 6-hour critical load reserve.
6. **Unratified OD-02-C Execution:** Line 38 imported `_align_n6_bundle_od02` from `adapters.py`, which executed Candidate C.2 clear-sky ratio fallback instead of the frozen OD-02 zero fallback.
7. **Baseline Protocol Parity:** Lines 261–321 evaluated the baseline under the same daily-origin open-loop protocol, starting from 80% SOC and resetting daily.

---

## 6. Static / Mocked Regression Tests (Non-Executing Specification)

To prove compliance without invoking HiGHS or running simulations, the following pure-logic unit assertions are specified for inclusion in `scratch/test_rhc_static_governance.py`:

```python
def test_od01_terminal_target_never_exceeds_feasible_ceiling():
    """Verifies that OD-01 dynamic derivation never forces GAP19 into terminal slack."""
    from system.schemas.station_state import StationState
    from system.evaluation.n6_multi_origin_harness.adapters import _prepare_gap19_terminal_target_config
    
    cfg = {
        "battery": {
            "capacity_wh": 200_000.0,
            "min_soc_pct": 20.0,
            "max_soc_pct": 95.0,
        }
    }
    # Test across all possible initial SOC levels (0% to 100%)
    for soc in [20.0, 50.0, 80.0, 95.0]:
        st = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=soc,
            battery_energy_wh=200_000.0 * (soc / 100.0),
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=15000.0,
            last_observed_wind_generation=10000.0,
            fuel_remaining_liters=500.0
        )
        opt_cfg = _prepare_gap19_terminal_target_config(st, cfg)
        target = opt_cfg["terminal_target_wh"]
        min_e = 40_000.0
        max_e = 190_000.0
        
        # In GAP19: required_lhs = target + min_e
        # Must strictly satisfy: required_lhs <= max_e
        assert target + min_e <= max_e, f"Feasible ceiling exceeded: {target + min_e} > {max_e}"
        assert target >= 0.0, f"Negative target: {target}"

def test_policy_b_pointwise_envelope():
    """Verifies that Policy B enforces combined_reserve = max(crit_6h, conformal_ebr)."""
    from system.evaluation.n6_multi_origin_harness.adapters import _prepare_gap19_policy_b_config
    from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
    
    # Mock bundle with known EBR and critical demand
    bundle = ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp="2024-06-01T00:00:00Z",
        horizon_hours=24,
        timestamps=["2024-06-01T00:00:00Z"] * 24,
        solar_irradiance=TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W/m^2"),
        solar_generation=TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W"),
        wind_generation=TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W"),
        demand=TimeseriesForecast(point=[20000.0]*24, lower=[20000.0]*24, upper=[20000.0]*24, unit="W"),
        demand_critical=TimeseriesForecast(point=[10000.0]*24, lower=[10000.0]*24, upper=[10000.0]*24, unit="W"),
        metadata={
            "SOLAR_FORECAST_SOURCE": "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
            "ebr_target_wh": [50000.0] * 24 # 50 kWh conformal EBR
        }
    )
    cfg = {"critical_demand_w": [10000.0]*24}
    opt_cfg = _prepare_gap19_policy_b_config(bundle, cfg)
    
    # Critical 6h reserve = 6 * 10,000 = 60,000 Wh.
    # Conformal EBR = 50,000 Wh.
    # Pointwise maximum must equal 60,000 Wh!
    assert opt_cfg["ebr_target_wh"][0] == 60000.0

def test_od02_shift_alignment_and_terminal_slot():
    """Verifies raw index 1..23 mapped to step 0..22 and step 23 set to frozen 0.0 W/m²."""
    raw_solar = list(range(100, 2500, 100)) # length 24
    aligned_solar = raw_solar[1:] + [0.0]
    
    assert len(aligned_solar) == 24
    assert aligned_solar[0] == raw_solar[1]
    assert aligned_solar[22] == raw_solar[23]
    assert aligned_solar[23] == 0.0
```

---

## 7. Proposed Hourly RHC Implementation Architecture & Baseline Protocol

The implementation must live entirely in `scratch/run_hourly_n6_gap19_rhc_eval.py`, reusing production classes directly without code mutation:

```text
================================================================================
HOURLY RECEDING-HORIZON CONTROL (RHC) EXECUTION SEQUENCE
================================================================================
Initialize DigitalTwin at 2024-01-20T00:00:00Z:
  S_0 = StationState(SOC=50.0%, Fuel=500.0L, diesel_running=False)

For simulated hour k = 0, 1, 2, ..., N-1 (timestamp t_k):
  1. Inspect DigitalTwin state S_k.
  2. Query trailing 24h SCADA actuals [t_k - 24h, t_k) from fixture.
  3. Dynamically compute 14 context features (ctx_*) via compute_telemetry_context_features.
  4. Assemble (24, 36) feature matrix for horizon [t_k, t_k + 24h).
  5. Generate raw N6 forecast: raw_bundle = n6_engine.predict(S_k, {"n6_feature_matrix": fm}).
  6. Apply frozen OD-02 shift: aligned_bundle = raw_bundle[1:] + [0.0].
  7. Inject OD-01 dynamic terminal target: _prepare_gap19_terminal_target_config(S_k, cfg).
  8. Inject Policy B reserve envelope: _prepare_gap19_policy_b_config(aligned_bundle, cfg).
  9. Route via EMSControlRouter: route = router.evaluate_and_route(S_k, aligned_bundle, cfg).
 10. Solve GAP19 MILP: plan = optimizer.optimize(aligned_bundle, S_k, cfg).
 11. Extract ONLY first action: u_0 = plan[0] = (P_chg[0], P_dis[0], P_diesel[0], ...).
 12. Advance DigitalTwin by 1 hour: S_{k+1} = simulator.step(S_k, u_0, actuals_{k+1}).
 13. Audit fuel monotonicity: assert S_{k+1}.fuel <= S_k.fuel.
 14. Carry forward S_{k+1} to step k+1 with ZERO STATE RESETS.
```

### Baseline Protocol Parity:
The baseline arm (`LocalBaselineForecastEngine`) must be evaluated under the identical protocol:
- Identical starting state $S_0$.
- Hourly re-forecasting and hourly GAP19 re-optimization cadence.
- Execution of strictly $u_0$.
- Identical H1.0 physical actuals consumed by `DigitalTwinSimulator`.
- Identical OD-01 dynamic terminal target handling.

---

## 8. Feasible Evaluation Scopes & Required Authorization

To preserve scientific integrity, three distinct scopes are documented:

| Scope Option | Hours / Solves per Arm | NWP / Feature Source | Causal Integrity | Purpose / Value |
|---|---|---|---|---|
| **Scope A: 168-Hour Smoke Test (June 1–8, 2024)** | 168 hours / 168 solves | Retrospective rolling slice of clean matrix with live telemetry update | Documented 8.25h NWP lookahead across midnight | Verifies controller mechanics, eliminates 10 kWh terminal slack bug, measures $u_0$ sensitivity in ~2 minutes. |
| **Scope B: Full-Year Retrospective RHC (8,304 Hours)** | 8,304 hours / 8,304 solves | Retrospective rolling slice across 2024 with live telemetry update | Documented 8.25h NWP lookahead across midnight | Full-year continuous closed-loop diesel and survivability benchmark (~1.6 hours wall runtime). |
| **Scope C: True Causal RHC with Acquired Leads** | 168 hours (or full year) | Freshly acquired MEPS leads 31–53 + online Chronos-2 inference | 100% operationally causal (zero lookahead) | Gold-standard causal validation; requires acquiring external leads 31–53 and running Chronos-2. |

### Explicit Authorization Boundary:
No execution of Scope A, B, or C is permitted until the user explicitly issues an execution command specifying:
1. Approved Scope (Scope A, B, or C).
2. Approved Terminal Solar Contract (Frozen OD-02 `0.0 W/m²` vs. Ratified OD-02-C `Candidate C.2`).
3. Explicit permission to invoke HiGHS MILP solves in `scratch/`.
