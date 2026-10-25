# POLARIS — Operational Feature Availability & Causality Audit Report (Candidate N6)

**Document Version:** 1.0.0  
**Audit Date:** 2026-10-17  
**Audit Scope:** Candidate N6 36-Feature Inference Contract & Operational Feasibility  
**Target Architecture:** Bagged Additive GBDT + High-Elevation $k_t$ Specialist Ramp  
**Frozen Model Binary:** `candidate_n6_model.joblib` (SHA-256 `b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197`)  
**Auditor:** POLARIS Operational Governance & Safety Assurance  
**Final Governance Status:** `winner: null` (Preserved unchanged; strictly non-production)  

---

## 1. Executive Summary & Audit Decision

### 1.1 Final Audit Decision: `UNPROVEN`
The read-only Operational Feature Availability and Causality Audit for POLARIS Candidate N6 concludes with a final decision of **`UNPROVEN`** (confidence: high in the evidentiary findings; strictly failure-closed on operational readiness).

- **Total Required Features Audited:** 36
  - **PASS:** 9 (25.0%) — Deterministic astronomical ephemeris and static topographic calculations.
  - **FAIL:** 0 (0.0%) — Zero future target leakage, zero post-cutoff observation leakage, and zero same-day zero-lead NWP contamination detected.
  - **UNPROVEN:** 27 (75.0%) — Required external data streams (MEPS 18Z pressure levels, SITES Nuolja station telemetry, and Stage 3b Chronos-2 execution) lack contemporaneous operational arrival/ingestion timestamps in the repository.

### 1.2 Core Finding: Plausible Design, Unproven Operational Timeliness
Candidate N6 represents a clean, sound mathematical design that systematically resolves the fatal training contamination and same-day 00Z MEPS leakage that previously compromised Candidate F:
1. **Zero Target Contamination:** No realized solar irradiance (`actual_SW_IN`, `actual_ghi`), residual labels, or future observations enter the feature matrix.
2. **Clean Causal Baseline:** Candidate N6 conditions on `pred_stage4_clean` using frozen 2024-EVEN parameters (`stage4/stage4_results/ensemble_parameters.json`, SHA-256 `26cfbd19...`), cleanly eliminating the 2025 parameter fitting contamination.
3. **Temporally Plausible NWP Sourcing:** By sourcing cloud microphysics (`lwp_18z_fc`, `iwp_18z_fc`, `u700`, `v700`) from the prior-day 18:00 UTC cycle ($D-1\ 18\text{Z}$), Candidate N6 operates with a **nominal 6-hour lookahead margin** before the $t_0 = 00:00\text{ UTC}$ dispatch cutoff. Given documented provider dissemination latency of ~135 minutes, this yields an estimated nominal buffer of $+3\text{h}45\text{m}$.

**The Blocker:** However, in accordance with the strict governing instructions, **a historical file containing a value at the correct valid time is not sufficient evidence of timely operational availability**. Neither MET Norway's THREDDS server nor the local repository maintains archived operational ingestion logs recording the exact arrival minutes of 18Z pressure-level NetCDF files during 2024 and 2025. Furthermore, the station context features (`ctx_*`) were historically derived from retrospective annual Level 2 files rather than an archived live telemetry daemon.

Consequently, while the model is **theoretically and causally clean**, its operational availability prior to $00:00\text{ UTC}$ remains **`UNPROVEN`**.

---

## 2. The 36-Feature Contract Verification

The authoritative inference contract was inspected read-only against `polaris_inference_runner.py`, `CANDIDATE_N_MANIFEST.json`, and the frozen binary `candidate_n6_model.joblib`:

```
+----+--------------------------------+--------------------------------------+------------+
| #  | Feature Name                   | Physical / Computational Category    | Verdict    |
+----+--------------------------------+--------------------------------------+------------+
| 1  | month                          | Astronomical / Calendar              | PASS       |
| 2  | hour                           | Astronomical / Calendar              | PASS       |
| 3  | solar_elevation                | Astronomical Ephemeris               | PASS       |
| 4  | solar_zenith                   | Astronomical Ephemeris               | PASS       |
| 5  | clearsky_ghi                   | Ineichen Clear-Sky Radiative Model   | PASS       |
| 6  | fc_cloud_cover                 | MEPS 18Z Surface NWP                 | UNPROVEN   |
| 7  | fc_temperature_2m              | MEPS 18Z Surface NWP                 | UNPROVEN   |
| 8  | fc_relative_humidity_2m        | MEPS 18Z Surface NWP                 | UNPROVEN   |
| 9  | cloud_frac                     | Derived Surface Cloud Fraction       | UNPROVEN   |
| 10 | ctx_std_3h                     | Station Telemetry Context (3h)       | UNPROVEN   |
| 11 | ctx_std_6h                     | Station Telemetry Context (6h)       | UNPROVEN   |
| 12 | ctx_std_12h                    | Station Telemetry Context (12h)      | UNPROVEN   |
| 13 | ctx_std_24h                    | Station Telemetry Context (24h)      | UNPROVEN   |
| 14 | ctx_abs_change_1h              | Station Telemetry Context (Step 1h)  | UNPROVEN   |
| 15 | ctx_abs_change_3h              | Station Telemetry Context (Step 3h)  | UNPROVEN   |
| 16 | ctx_abs_change_6h              | Station Telemetry Context (Step 6h)  | UNPROVEN   |
| 17 | ctx_max_diff_6h                | Station Telemetry Context (Max Diff) | UNPROVEN   |
| 18 | ctx_mean_diff_6h               | Station Telemetry Context (Mean Diff)| UNPROVEN   |
| 19 | ctx_slope_6h                   | Station Telemetry Context (OLS Trend)| UNPROVEN   |
| 20 | ctx_kt_std_6h                  | Station Telemetry Context (kt Sigma) | UNPROVEN   |
| 21 | ctx_last_obs                   | Station Telemetry Context (t0 - 1h)  | UNPROVEN   |
| 22 | ctx_mean_24h                   | Station Telemetry Context (Mean 24h) | UNPROVEN   |
| 23 | ctx_max_24h                    | Station Telemetry Context (Max 24h)  | UNPROVEN   |
| 24 | terrain_horizon_elevation_deg  | DEM Topographic Ray-Tracing          | PASS       |
| 25 | terrain_elevation_margin_deg   | Topographic Margin                   | PASS       |
| 26 | terrain_solar_obstruction_flag | Topographic Shading Indicator        | PASS       |
| 27 | clearsky_ghi_terrain_adjusted  | Topographically Occluded GHI         | PASS       |
| 28 | u700                           | MEPS 18Z Pressure Levels (700 hPa)   | UNPROVEN   |
| 29 | v700                           | MEPS 18Z Pressure Levels (700 hPa)   | UNPROVEN   |
| 30 | lwp_18z_fc                     | MEPS 18Z Microphysics (LWP 700 hPa)  | UNPROVEN   |
| 31 | iwp_18z_fc                     | MEPS 18Z Microphysics (IWP 700 hPa)  | UNPROVEN   |
| 32 | lwp_x_cloud_18z                | Non-Linear Microphysics Interaction  | UNPROVEN   |
| 33 | elevation_x_cloud_frac         | Solar Zenith Optical Path Inter.     | UNPROVEN   |
| 34 | pred_stage4_clean              | Stage 4 Clean Blended Baseline       | UNPROVEN   |
| 35 | clean_attenuation              | Baseline Attenuation Metric          | UNPROVEN   |
| 36 | elevation_x_transition_cloud   | Candidate J Transition Inter.        | UNPROVEN   |
+----+--------------------------------+--------------------------------------+------------+
```

---

## 3. Evaluation of Acceptance Criteria

Per Section 7 of the governing specification, the audit evaluated the eight mandatory acceptance gates:

| Gate | Acceptance Criterion | Evaluation Result | Status |
|---|---|---|---|
| **Gate 1** | Complete N6 feature contract verified against frozen model | All 36 features, ordering, and types verified against `candidate_n6_model.joblib` bundle. | **PASS** |
| **Gate 2** | Every feature has documented, legitimate source & lineage | Full mathematical and data lineage traced in `temporal_lineage.md`. | **PASS** |
| **Gate 3** | Source values & derived features available before decision cutoff | Lacks contemporaneous ingestion logs for MEPS 18Z, SITES telemetry, and Stage 3b. | **UNPROVEN** |
| **Gate 4** | Temporal alignment and forecast-cycle selection are correct | 18Z initialization mapped to lead $5+h$ ($h \in [1, 24] \implies \text{leads } 6..29$). | **PASS** |
| **Gate 5** | No future information or retrospective-only data in vector | Zero label/target leakage; retrospective files used historically in lieu of live daemon. | **UNPROVEN** |
| **Gate 6** | Missing, late, or invalid inputs cause safe rejection | `validate_input_features` fails closed on missing features or label columns. | **PASS** |
| **Gate 7** | Bounded non-blind replay using only cutoff-available data | Cannot fabricate timestamps; representative origins fail closed as unproven. | **UNPROVEN** |
| **Gate 8** | Evidence is sufficient to independently audit conclusion | All ledger rows, manifests, and checksums fully documented in audit folder. | **PASS** |

**Summary:** 5 criteria PASS, 3 criteria UNPROVEN, 0 FAIL. A single UNPROVEN criterion prevents operational sign-off.

---

## 4. Deep-Dive: The Critical 18Z MEPS Pressure-Level Question

### 4.1 Contrast with Candidate F (00Z MEPS)
- In the original Candidate F audit, the feature `lwp_latest` was sourced from the **same-day 00Z MEPS cycle** ($t_{\text{init}} = t_0 = 00:00\text{ UTC}$).
- Because MET Norway requires ~135 minutes to compute and disseminate MEPS forecasts, the 00Z output is physically unavailable until ~02:15 UTC.
- Using 00Z MEPS at a 00:00 UTC dispatch cutoff was a **physical impossibility and a temporal causality violation (`FAIL`)**.

### 4.2 Candidate N6 (18Z MEPS Successor Lineage)
- Candidate N6 switches to the prior-day 18:00 UTC cycle ($t_{\text{init}} = t_0 - 6\text{h}$).
- Target valid time $t_v = t_0 + (h - 1)\text{h}$ maps to forecast lead:
  $$\text{lead} = 5 + h \implies \text{lead } 6 \text{ to lead } 29$$
- At cutoff ($00:00\text{ UTC}$), the 18Z cycle is **6 hours old**.
- Accounting for the nominal 135-minute dissemination latency, the 18Z data is expected to be published around **20:15 UTC** on Day $D-1$.
- This provides a **theoretical positive margin of $+3\text{h}45\text{m}$** prior to dispatch.

### 4.3 Why 18Z Remains UNPROVEN
1. **No Ingestion Timestamps:** The files in the repository (`cache_full_acquisition/`, `cache_lead6_v2/`) were retrieved via OPeNDAP queries in 2026. The repository preserves no contemporaneous logs recording the exact minute when MET Norway published `meps_det_pl_*.ncml` on each operational day of 2024 or 2025.
2. **Product Tier Disparity:** Pressure-level files (`meps_det_pl`) are much larger and more computationally intensive than surface files (`meps_det_sfc`), often experiencing publication lags.
3. **Documented Delays:** Historical incident reports from MET Norway confirm that MEPS dissemination delays of several hours occur intermittently due to HPC maintenance or assimilation bottlenecks.
4. **Governing Constraint:** The governing mandate explicitly specifies: *"A historical file containing a value at the correct valid time is not sufficient evidence of timely availability. If the necessary publication or ingestion timestamps cannot be established, mark the affected feature UNPROVEN."*

---

## 5. Station Context & Stage 4 Clean Baseline Findings

### 5.1 Station Telemetry Context (`ctx_*`)
- The 14 features (`ctx_std_3h` ... `ctx_max_24h`) strictly examine historical observations over $[t_0-24\text{h}, t_0)$.
- There is **zero future target leakage**.
- However, in research development, these values were extracted from retrospective Level 2 annual CSV files from the SITES Data Portal (`SITES_MET_ANS_NMS_*_L2_SH.csv`).
- In live microgrid operations, POLARIS cannot query annual research archives; it must ingest real-time datalogger telemetry from Nuolja Middle Station. Because no operational telemetry streaming daemon or arrival log exists in the repository, this source is **`UNPROVEN`**.

### 5.2 Stage 4 Clean Baseline (`pred_stage4_clean`, `clean_attenuation`)
- The formula:
  $$pred_{\text{stage4, clean}} = \max\left(0.0,\ w_h \cdot pred_{\text{stage3b, cloud, nwp}} + (1.0 - w_h) \cdot \max(0, GHI_{\text{cs}} \cdot (1 - k_h \cdot \text{cloud}\_\text{frac}))\right)$$
- Utilizes frozen 2024-EVEN parameters $(w_h, k_h)$ (SHA-256 `26cfbd19...`).
- This completely remedies the training contamination found in Candidate F.
- However, `pred_stage3b_cloud_nwp` was generated via offline batch inference of Chronos-2. Without an operational service benchmark proving Chronos-2 execution completes within minutes before $00:00\text{ UTC}$, this dependency inherits **`UNPROVEN`**.

---

## 6. Pre-Existing Data Quality Finding: `u700`/`v700` Missing Values

An independent inspection of `dataset_v2` and `candidate_k_2024_clean_matrix.parquet` confirmed that for **all origins across both 2024 and 2025**, columns `u700` and `v700` are NaN for horizons $h \in [20, 24]$ (leads 25..29).
- **Origin of Defect:** Inherited from the legacy Stage 8.1 700 hPa wind extraction script (`run_stage8_1.py:77`), which restricted its OPeNDAP query to `lead[7:1:25]` (covering horizons 1–19).
- **Safety Impact:** Scikit-learn's `HistGradientBoostingRegressor` natively handles NaNs by assigning missing values to the optimal split direction determined during training on 2024-EVEN. This does not crash inference, but represents a known information loss for evening and late-night horizons.

---

## 7. Governance, Scope & Integrity Safeguards

- **No Retraining or Parameter Alteration:** Zero models were retrained, refitted, or tuned.
- **No Modification of Frozen Artifacts:** `candidate_n6_model.joblib`, `candidate_n1_model.joblib`, `CANDIDATE_N_MANIFEST.json`, and `HASHES.sha256` remain byte-identical to their approved states.
- **No Blind Partition Access:** No 2025 blind evaluation was rerun, inspected, or transformed.
- **No Production Dispatch:** HiGHS solver, GAP19 MILP, and EMS replays were not executed.
- **Winner Status Preserved:** `winner: null` remains strictly in effect. Candidate N6 is NOT promoted.
