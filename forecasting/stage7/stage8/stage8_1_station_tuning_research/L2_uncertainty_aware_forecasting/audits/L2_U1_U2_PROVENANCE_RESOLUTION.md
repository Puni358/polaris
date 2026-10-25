# L2-EXP-01 Blocker Provenance-Resolution Audit (U-1 & U-2)

**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Date**: October 4, 2026  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.36207412° N, 18.73875158° E`)  
**Scope**: Standalone provenance-resolution audit for blockers U-1 and U-2 identified in `design/L2_FIRST_EXPERIMENT_DESIGN.md`.  
**Governance Compliance**: AUDIT ONLY. No neural network trained, no runner created, no experiments rerun, no production or frozen code/artifacts modified, and no external data acquired.

---

## Executive Audit Summary

This audit establishes the full provenance, causal timeline, and authoritative validation status for blockers **U-1** and **U-2** raised in the revised `L2-EXP-01` experiment specification (`design/L2_FIRST_EXPERIMENT_DESIGN.md` §12).

A forensic audit of repository manifests, data acquisitions, reconstruction scripts, and audit logs reveals that the blocking concerns arose from an earlier preliminary reconstruction pass (`CANDIDATE_L2_CONTEXT_FEATURE_FORENSIC_AUDIT.md`) which properly rejected an un-reconstructed artifact that used `0.0` context substitutions. Subsequently, authentic historical 2019–2023 SITES Mount Nuolja station observations were acquired, validated, and used to build the exact 38-feature matrix and exact frozen F predictions. All prior concerns have been fully superseded by validated artifacts and passing forensic gates.

---

## Blocker U-1: Provenance and Causality of 2020–2023 Nuolja Station Observations and Context Features

### STATUS: PASS

### Evidence
1. **Raw Station Observation Acquisition**:
   - Level 2 pyranometer observations ($SW_{IN}$, Apogee SP110 at 2.86 m a.g.l.) covering calendar years 2020 through 2023 (plus late 2019 for rolling context initialization) were acquired directly from the official **SITES Data Portal** (`https://data.fieldsites.se`) for station **`ANS_NMS`** (Mount Nuolja Middle Station AWS).
   - Acquired datasets contain 100% continuous 10-minute cadence readings with zero missing steps and zero NaNs:
     - **2020**: 52,704 rows (leap year), PID `11676.1/CWT5DHNcPD00c8IWgAZtcmrt`
     - **2021**: 52,560 rows, PID `11676.1/t0AeJcJn3RUXzCvdy6X8KWI5`
     - **2022**: 52,560 rows, PID `11676.1/hWUlMbcNhTRvLAZEIJdsvb0u`
     - **2023**: 52,560 rows, PID `11676.1/OL7g8xUD95cnWm5ZFEuoUwNh`
     - **2019**: `SITES_MET_ANS_NMS_20190619-20191231_L2_SH.csv` (supports the 24h rolling context for origin `2020-01-01 00:00:00Z`).
2. **Temporal Alignment**:
   - Station observations are recorded in fixed `UTC+1` (`Etc/GMT-1`, no daylight saving time shifts).
   - The reconstruction pipeline (`build_exact_candidate_L2_feature_matrix.py` lines 97–104) groups 10-minute records (`HH:00` to `HH:50`) into hourly means (`HH:00`), localized to `Etc/GMT-1` and converted to `UTC`.
   - Hourly timestamps match MEPS NWP valid target timestamps and forecast origins exactly.
3. **Causal Availability at Forecast Issuance**:
   - The 24-hour observation context window is strictly $[t_0 - 24\text{h}, t_0)$, ending at $t_0 - 1\text{h}$.
   - All station context features (`ctx_last_obs` = $sw_{-1}$, `ctx_std_3h` = $\text{std}(sw_{-3..-1})$, `ctx_mean_24h` = $\text{mean}(sw_{-24..-1})$) conclude at $t_0 - 1\text{h}$, strictly prior to forecast issuance at $t_0$.
   - Pre-inference audit confirms zero daytime origins with zero context (`ctx_mean_24h == 0.0`), proving authentic station telemetry is present across all 1,369 origins.
4. **Target Observation Alignment**:
   - The ground truth `actual` ($SW_{IN}$, $\text{W/m}^2$) paired in `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` is the exact hourly Level 2 observation from the same pyranometer sensor at target valid timestamp $t$.
   - Exactly 26,011 rows pair with 0 missing actuals (null count = 0).

### Authoritative Artifacts
- `data/POLARIS_HISTORICAL_NUOLJA_ACQUISITION_MANIFEST.json`
- `candidate_L_research/HISTORICAL_NUOLJA_STATION_DATA_ACQUISITION_VALIDATION.md`
- `candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_PROVENANCE_AUDIT.md`
- `CANDIDATE_F_HISTORICAL_REPLAY_FORENSIC_AUDIT.md`
- `candidate_L_research/CANDIDATE_F_RESIDUAL_PROVENANCE_MANIFEST.json`

### Hashes
- **Raw 2020 Station File**: `data/raw_historical_sites_download/SITES_MET_ANS_NMS_20200101-20210101_L2_SH.csv`  
  SHA256: `0964f90c735c3c3d3473c21680066d726aedb6166464e1aa900b410da68df590`
- **Raw 2021 Station File**: `data/raw_historical_sites_download/SITES_MET_ANS_NMS_20210101-20220101_L2_SH.csv`  
  SHA256: `b7401e25c267dd1517cc2bddcba5fc29623915c73c54636fd1343769a8bc58bd`
- **Raw 2022 Station File**: `data/raw_historical_sites_download/SITES_MET_ANS_NMS_20220101-20221231_L2_SH.csv`  
  SHA256: `85652531b70d85346f2c064420976cbdbd2e9e4946dd83b33d013eb9777e72d6`
- **Raw 2023 Station File**: `data/raw_historical_sites_download/SITES_MET_ANS_NMS_20230101-20231231_L2_SH.csv`  
  SHA256: `38bee0f31503f797275a6e59144ba8530361bf2af81d039201af4b4c1e19fd5a`
- **Historical Residual Dataset**: `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`  
  SHA256: `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab`

### Exact Reasoning
The question in U-1 was whether authoritative station observations exist for 2020–2023 or whether context inputs were ungrounded. The audit confirms that the station data was authoritatively acquired from the Swedish Infrastructure for Ecosystem Science (SITES) archive for `ANS_NMS` under persistent identifiers, contains zero missing steps, is strictly causal ($t_0 - 1\text{h}$ cutoff), and provides both the exact context inputs and target ground truth for all 26,011 rows.

### Remaining Uncertainty
None. The station provenance, instrument metadata, coordinates, cadence, timezone conversion, and causal windowing are completely documented and verified.

### Consequence for L2-EXP-01
Blocker U-1 is fully resolved. Features 8 (`ctx_last_obs`), 9 (`ctx_std_3h`), 10 (`ctx_mean_24h`), and the target ground truth `actual` ($SW_{IN}$) are verified as authoritative, causal, and ready for use in L2-EXP-01 training and evaluation.

---

## Blocker U-2: Validity of `CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv` as Residual Basis

### STATUS: PASS

### Evidence
1. **Trace of Prediction Generation**:
   - Generated by script: `candidate_L_research/build_exact_candidate_L2_feature_matrix.py`.
   - Input feature matrix: `candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` (SHA256: `bb5700c9...`).
   - Inference execution: Frozen model `candidateF_elevation_x_cloud.joblib` (SHA256: `e8b89b27...`) applied across all 26,011 rows.
   - Total point prediction: $\hat{y}_F = \max(0, \text{round}(P_{\text{stage4\_fold}} + \hat{R}_F, 4))$, with causal night zeroing applied when $\theta_{\text{elev}} \le 0^\circ$.
   - Output predictions artifact: `candidate_L_research/CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv` (SHA256: `b3e2044b...`).
2. **Forensic Gate Checks**:
   - 0 NaNs and 0 Infs in feature matrix and predictions.
   - 100% row-by-row correlation and timestamp alignment across 1,369 origins and 26,011 rows.
   - Elimination of all proxy substitutions: static 5.0° terrain horizon was replaced with 360° DEM topography profile (`nuolja_horizon_profile_360deg.csv`, SHA256: `0f0dde04...`), and `0.0` context substitutions were replaced with authentic rolling SITES observations.
3. **Audit Conflict Origin & Chronological Resolution**:
   - **The Conflict**: `design/L2_FIRST_EXPERIMENT_DESIGN.md` §12 cited `CANDIDATE_L2_CONTEXT_FEATURE_FORENSIC_AUDIT.md` (which declared historical predictions invalid).
   - **Chronological Resolution**:
     - At **00:39 UTC**, an initial builder (`build_candidate_L2_feature_matrix.py`) generated an initial artifact named `CANDIDATE_L2_FROZEN_F_PREDICTIONS_2020_2023.csv` using hardcoded `0.0` for context features because pre-2024 station data was not yet present in the repo.
     - At **00:44 UTC**, `CANDIDATE_L2_CONTEXT_FEATURE_FORENSIC_AUDIT.md` audited that preliminary artifact, properly flagged the `0.0` convenience substitution, and marked that preliminary artifact as **invalid**.
     - In direct response, between **00:58 and 01:05 UTC**, authentic historical SITES `ANS_NMS` data (2019–2023) was downloaded and validated (`HISTORICAL_NUOLJA_STATION_DATA_ACQUISITION_VALIDATION.md`).
     - At **01:06 UTC**, `build_exact_candidate_L2_feature_matrix.py` was executed, producing the reconstructed matrix `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` and the exact frozen F prediction artifact **`CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv`** (SHA256: `b3e2044b...`).
     - At **01:07 UTC**, `CANDIDATE_L2_EXACT_38_FEATURE_PROVENANCE_AUDIT.md` and `CANDIDATE_L2_F_RECONSTRUCTION_GATE.md` formally passed the exact reconstruction.
     - At **01:10 UTC**, `CANDIDATE_F_HISTORICAL_REPLAY_FORENSIC_AUDIT.md` passed the 12-item independent forensic gate and confirmed the residual dataset as valid.
   - **Conclusion**: The prior audit's invalidation applied strictly to the old, un-reconstructed artifact `CANDIDATE_L2_FROZEN_F_PREDICTIONS_2020_2023.csv`. It has been completely superseded by `CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv`, which is fully validated and free from unsupported substitutions.

### Authoritative Artifacts
- `candidate_L_research/CANDIDATE_L2_EXACT_F_RECONSTRUCTION_MANIFEST.json`
- `candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_PROVENANCE_AUDIT.md`
- `candidate_L_research/CANDIDATE_L2_F_RECONSTRUCTION_GATE.md`
- `CANDIDATE_F_HISTORICAL_REPLAY_FORENSIC_AUDIT.md`
- `candidate_L_research/CANDIDATE_F_RESIDUAL_PROVENANCE_MANIFEST.json`

### Hashes
- **Frozen Candidate F Model**: `stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib`  
  SHA256: `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84`
- **Exact 38-Feature Historical Matrix**: `candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv`  
  SHA256: `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde`
- **Exact Frozen F Historical Predictions**: `candidate_L_research/CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv`  
  SHA256: `b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0`
- **Historical Candidate F Residual Dataset**: `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`  
  SHA256: `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab`

### Exact Reasoning
The prior audit (`CANDIDATE_L2_CONTEXT_FEATURE_FORENSIC_AUDIT.md`) flagged a legitimate defect in an early draft pipeline where context features were set to `0.0`. That draft artifact was superseded by the exact reconstruction pipeline (`build_exact_candidate_L2_feature_matrix.py`) which used authentic SITES data, dynamic 360° DEM terrain horizon lookups, and the frozen Candidate F model. The resulting exact prediction artifact matches all required hashes and passes all forensic gates.

### Remaining Uncertainty
None. The exact prediction artifact is mathematically reproducible, cryptographically locked, and verified against the frozen Candidate F GBDT model.

### Consequence for L2-EXP-01
Blocker U-2 is fully resolved. `CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv` is confirmed as a valid, untainted, and authoritative residual baseline for L2-EXP-01.

---

## OVERALL VERDICT

### GO: Both blockers resolved

1. **U-1 is resolved (PASS)**: Authoritative 2020–2023 Mount Nuolja AWS observations (`ANS_NMS`) are fully acquired from SITES, verified, temporally aligned, causally bounded ($t_0 - 1\text{h}$), and suitable for target and context features.
2. **U-2 is resolved (PASS)**: `CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv` was generated from the exact 38-feature matrix using frozen Candidate F; the prior audit's invalidation pertained to an early un-reconstructed prototype and has been superseded by the validated exact reconstruction.
