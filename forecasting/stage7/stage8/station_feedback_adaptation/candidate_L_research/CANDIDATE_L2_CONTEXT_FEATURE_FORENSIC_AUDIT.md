# Candidate L2 — Historical Station Context Feature Forensic Audit & Frozen-F Reconstruction Gate

**Date**: October 4, 2026  
**Scope**: Candidate L Research — Forensic Audit of 14 Historical Station Context Features (`ctx_*`) and Frozen Candidate F Replay Validity  
**Target Station**: Nuolja / Abisko (`68.362074° N, 18.738875° E`, elev. 920 m)  
**Strict Scope Compliance**: Read-only forensic audit. No neural network trained, Candidate F NOT modified, Candidate J and Stage 8.1 artifacts NOT modified, production code NOT altered.

---

## Executive Summary

Following a critical finding regarding the assignment of `0.0` to 14 historical station-context features (`ctx_std_3h` ... `ctx_max_24h`) across pre-2024 forecast origins, a detailed forensic audit was performed to evaluate whether `0.0` represents an explicitly authorized missing-data fallback or an invalid convenience substitution.

### Forensic Key Findings:

1. **Training Distribution Mismatch**: In the official 2024 training feature matrix (`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`), **0 out of 347 origins** had zero context features (`ctx_mean_24h == 0.0`). Every daytime origin in Candidate F's training set possessed valid, non-zero station context observations (`SW_IN`).
2. **Semantic Distinction**: In physical reality, `0.0` context values occur during **Polar Night** (when $SW_{IN} = 0.0$ W/m² for 24 consecutive hours). Assigning `0.0` to daytime pre-2024 origins where solar zenith is low and irradiance is high introduces an out-of-distribution semantic distortion that Candidate F never encountered during training.
3. **Absence of Pre-2024 Station Data**: A comprehensive search of local repository assets (`data/`) confirms that Mount Nuolja station observations (`SW_IN`) exist only for **2024** and **2025**. No pre-2024 (2020–2023) station observation files exist in the repository or local archives.
4. **Hard-Coded / Proxy Inspections**: `build_candidate_L2_feature_matrix.py` contained multiple hard-coded default and proxy values (`ctx_* = 0.0`, `terrain_horizon_elevation_deg = 5.0`, `pred_stage3b_cloud_nwp = phys_pred_fold`), making the resulting feature matrix an approximation rather than an exact frozen F replay.
5. **Replay Artifact Invalidated**: The 26,011-row historical prediction artifact (`CANDIDATE_L2_FROZEN_F_PREDICTIONS_2020_2023.csv`) generated with `0.0` context substitutions is classified as **invalid for Candidate F performance and residual training evaluation**.

---

## 1. Original Feature-Construction Implementation Audit

The authoritative feature-construction implementation for Candidate F was located and inspected:
- **Primary Source Code**: [`stage7/stage8/stage8_1_corrected_2025/build_corrected_feature_matrix.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_corrected_2025/build_corrected_feature_matrix.py) (and [`scratch/assemble_stage8_1_matrix.py`](file:///home/punith-bs/01polaris%20%28Copy%29/scratch/assemble_stage8_1_matrix.py)).
- **Exact Source Dataset**: SITES Nuolja ground station observed $SW_{IN}$ dataset (`data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` for 2024; `data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv` for 2025).
- **Exact Source Window**: The 24-hour historical window prior to forecast origin time $t_0$, defined as $[t_0 - 24\text{h}, t_0)$.
- **Code Missing-Data Branch**:
  ```python
  if len(ctx_sites) < 24:
      ctx_feature_rows.append({
          "forecast_start": origin_ts,
          "ctx_std_3h": 0.0, "ctx_std_6h": 0.0, "ctx_std_12h": 0.0, "ctx_std_24h": 0.0,
          "ctx_abs_change_1h": 0.0, "ctx_abs_change_3h": 0.0, "ctx_abs_change_6h": 0.0,
          "ctx_max_diff_6h": 0.0, "ctx_mean_diff_6h": 0.0, "ctx_slope_6h": 0.0,
          "ctx_kt_std_6h": 0.0, "ctx_last_obs": 0.0, "ctx_mean_24h": 0.0, "ctx_max_24h": 0.0
      })
  ```

---

## 2. Feature-by-Feature Forensic Audit of the 14 Context Features

| # | Feature Name | Source Dataset | Source Window | Computation / Formula | Missing-Data Code Behavior | 0.0 Authorized vs Convenience | Candidate F Training Rule Match |
|---|---|---|---|---|---|---|---|
| 1 | `ctx_std_3h` | SITES Nuolja $SW_{IN}$ | $[t_0-3\text{h}, t_0)$ | $\text{std}(SW_{IN}[t-3..t])$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 2 | `ctx_std_6h` | SITES Nuolja $SW_{IN}$ | $[t_0-6\text{h}, t_0)$ | $\text{std}(SW_{IN}[t-6..t])$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 3 | `ctx_std_12h` | SITES Nuolja $SW_{IN}$ | $[t_0-12\text{h}, t_0)$ | $\text{std}(SW_{IN}[t-12..t])$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 4 | `ctx_std_24h` | SITES Nuolja $SW_{IN}$ | $[t_0-24\text{h}, t_0)$ | $\text{std}(SW_{IN}[t-24..t])$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 5 | `ctx_abs_change_1h` | SITES Nuolja $SW_{IN}$ | $[t_0-2\text{h}, t_0)$ | $\|SW_{IN}(t-1) - SW_{IN}(t-2)\|$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 6 | `ctx_abs_change_3h` | SITES Nuolja $SW_{IN}$ | $[t_0-4\text{h}, t_0)$ | $\|SW_{IN}(t-1) - SW_{IN}(t-4)\|$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 7 | `ctx_abs_change_6h` | SITES Nuolja $SW_{IN}$ | $[t_0-7\text{h}, t_0)$ | $\|SW_{IN}(t-1) - SW_{IN}(t-7)\|$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 8 | `ctx_max_diff_6h` | SITES Nuolja $SW_{IN}$ | $[t_0-6\text{h}, t_0)$ | $\max(\|\Delta SW_{IN}\|)$ 6h | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 9 | `ctx_mean_diff_6h` | SITES Nuolja $SW_{IN}$ | $[t_0-6\text{h}, t_0)$ | $\text{mean}(\|\Delta SW_{IN}\|)$ 6h | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 10 | `ctx_slope_6h` | SITES Nuolja $SW_{IN}$ | $[t_0-6\text{h}, t_0)$ | Polyfit degree-1 slope 6h | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 11 | `ctx_kt_std_6h` | SITES Nuolja $SW_{IN}$ + ClearSky | $[t_0-6\text{h}, t_0)$ | $\text{std}(K_t)$ where $K_t = SW_{IN}/GHI_{cs}$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 12 | `ctx_last_obs` | SITES Nuolja $SW_{IN}$ | $t_0-1\text{h}$ | $SW_{IN}(t_0-1\text{h})$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 13 | `ctx_mean_24h` | SITES Nuolja $SW_{IN}$ | $[t_0-24\text{h}, t_0)$ | $\text{mean}(SW_{IN}[t-24..t])$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |
| 14 | `ctx_max_24h` | SITES Nuolja $SW_{IN}$ | $[t_0-24\text{h}, t_0)$ | $\max(SW_{IN}[t-24..t])$ | `0.0` if count < 24 | Convenience Substitution | **MISMATCH** (2024 had 100% data) |

---

## 3. Comparison Against Actual 2024/2025 Frozen F Feature Matrices

An empirical inspection of the official 2024 training feature matrix ([`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv)) was performed:

- **Total 2024 Forecast Origins**: 347
- **Origins with `ctx_mean_24h == 0.0` in 2024 Training Data**: **0 out of 347**
- **Daytime Origins with `0.0` Context Features in 2024 Training Data**: **0**

### Conclusion:
Candidate F was trained exclusively on origins where valid 24-hour station context observations were available. When Candidate F evaluates tree splits, non-zero context features (`ctx_last_obs`, `ctx_mean_24h`, `ctx_std_3h`) modulate model residuals based on recent cloud clearing or persistence. Setting these features to `0.0` for daytime origins tricks the model into evaluating tree branches designed for zero-irradiance conditions, introducing uncontrollable prediction distortion.

---

## 4. Availability of Historical 2020–2023 Station Observations

A complete filesystem and data inventory audit was conducted:
1. **Local Repository Inventory**:
   - `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` (2024 only)
   - `data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv` (2024 only)
   - `data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_multivariate.csv` (2025 only)
   - `data/raw_2025_sites_download/SITES_MET_ANS_NMS_20250101-20251231_L2_SH.csv` (2025 only)
2. **Pre-2024 Station Data Availability**:
   - **Result**: NO pre-2024 (2020–2023) station observation files exist in local directories or archives for Mount Nuolja ($SW_{IN}$).

---

## 5. Feature Reconstruction vs. UNAVAILABLE Marking

Because pre-2024 station observations do NOT exist in the repository:
- The 14 station-context features **CANNOT** be reconstructed for 2020–2023.
- Marking these 14 features as `0.0` is an unauthorized substitution.
- These 14 features MUST be marked **UNAVAILABLE** for the 2020–2023 historical period.
- Consequently, exact frozen Candidate F model inference is **IMPOSSIBLE** for pre-2024 origins using the 38-feature contract.

---

## 6. Classification of Historical F Prediction Artifact

The 26,011-row historical F prediction artifact ([`CANDIDATE_L2_FROZEN_F_PREDICTIONS_2020_2023.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_L2_FROZEN_F_PREDICTIONS_2020_2023.csv)) was produced by injecting `0.0` for all 14 context features during daytime historical forecasts.

### Verdict Classification:
**D. Invalid for F performance/residual evaluation.**

---

## 7. Audit of `build_candidate_L2_feature_matrix.py` Default & Proxy Values

A line-by-line audit of [`build_candidate_L2_feature_matrix.py`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/build_candidate_L2_feature_matrix.py) identified the following hard-coded/default/proxy substitutions:

1. **Context Features (`ctx_*`)** (Lines 115–116):
   - `df[ctx] = 0.0` for all 14 context features.
   - *Status*: **UNSUPPORTED SUBSTITUTION** (violates training distribution).
2. **Terrain Features** (Lines 118–121):
   - `df['terrain_horizon_elevation_deg'] = 5.0` (hard-coded flat 5.0° horizon).
   - `df['terrain_elevation_margin_deg'] = df['solar_elevation'] - 5.0`.
   - `df['terrain_solar_obstruction_flag'] = np.where(df['solar_elevation'] <= 5.0, 1.0, 0.0)`.
   - `df['clearsky_ghi_terrain_adjusted'] = np.where(df['terrain_solar_obstruction_flag'] == 1.0, 0.0, df['clearsky_ghi'])`.
   - *Status*: **APPROXIMATION** (2024/2025 baseline uses exact 360° azimuth terrain horizon profile lookup from `nuolja_terrain_features_2024_CORRECTED.csv`).
3. **Stage 3B Cloud NWP & Disagreement** (Lines 103, 113):
   - `df['pred_stage3b_cloud_nwp'] = df['phys_pred_fold']`.
   - `df['disagreement_fold'] = |pred_stage3b_cloud_nwp - phys_pred_fold| = 0.0`.
   - *Status*: **PROXY SUBSTITUTION** (In 2024 training, Stage 3B was an distinct cloud model output; forcing equality sets disagreement feature identically to 0.0).
4. **Microphysics Missing Fillna** (Lines 86–87):
   - `df['lwp_latest'].fillna(0.0)` and `df['iwp_latest'].fillna(0.0)`.
   - *Status*: **FILLNA CONVENIENCE** (Standard handling when 00Z MEPS run is unaligned).

---

## 8. Final Multi-Level Provenance & Reconstruction Verdicts

- **RAW MEPS PROVENANCE**: **PASS**  
  *(1,369 historical MEPS forecast origins acquired, 2020-01-01 to 2023-09-30 continuous, 100% deterministic extraction, 0 synthetic values, verified against MET Norway THREDDS archive).*

- **DERIVED CONTEXT FEATURE PROVENANCE**: **FAIL**  
  *(Pre-2024 station observations $SW_{IN}$ do not exist locally; the 14 context features were replaced with unauthorized `0.0` convenience substitutions that mismatch training semantics).*

- **EXACT F RECONSTRUCTION**: **BLOCKED**  
  *(Exact frozen Candidate F model historical replay is BLOCKED because the 38-feature contract requires authentic historical 24-hour station context observations).*

- **HISTORICAL F PREDICTIONS VALID FOR RESIDUAL TRAINING**: **BLOCKED**  
  *(The 26,011-row prediction artifact generated with zero context substitutions is invalid for F residual training or residual evaluation).*

- **NN TRAINING**: **LOCKED**  
  *(Neural network training remains strictly locked until an authorized protocol for handling historical missing context features is established).*
