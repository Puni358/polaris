# POLARIS Stage 6.4 Reproducibility Report

**Experiment Name**: Stage 6.4 MEPS Deterministic Forecast Revision Trajectory EVEN CV  
**Date**: September 12, 2026  
**Status**: COMPLETE — REJECT CANDIDATE / PRESERVE STAGE 5.2 CHAMPION  
**ODD Isolation**: 100% UNTOUCHED (0 ODD origins evaluated or loaded)

---

## 1. Input Datasets & Files

- **Benchmark Master Dataset**: [`stage5/stage5_2_champion_audit/POLARIS_stage5_2_dataset.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage5/stage5_2_champion_audit/POLARIS_stage5_2_dataset.csv)
  - Origins: 347 total (174 EVEN, 173 ODD)
  - Total Rows: 8,328
- **Stage 6.4 MEPS Revision Summary**: [`stage6/stage6_4_meps_revision/meps_revision_feature_summary.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage6/stage6_4_meps_revision/meps_revision_feature_summary.csv)
  - Origins: 347 total
  - Total Rows: 8,328 (joined 1:1 on `forecast_start`, `horizon_hour`)
- **Stage 6.4 Execution Script**: [`stage6/stage6_4_meps_revision/run_stage6_4_audit_and_experiment.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage6/stage6_4_meps_revision/run_stage6_4_audit_and_experiment.py)

---

## 2. Feature Configuration

### Base Stage 5.2 Features (28 features)
- **Temporal (4)**: `sin_hour`, `cos_hour`, `sin_dayofyear`, `cos_dayofyear`
- **Clearsky Target (1)**: `clearsky_sw`
- **Point Solar Parameters (4)**: `solar_zenith_deg`, `solar_azimuth_deg`, `equation_of_time_min`, `solar_declination_deg`
- **MEPS Base Forecasts (10)**: `meps_sw_direct`, `meps_sw_diffuse`, `meps_sw_total`, `meps_clearsky_sw`, `meps_cloud_fraction`, `meps_relative_humidity`, `meps_air_temp`, `meps_pressure`, `meps_wind_speed`, `meps_dew_point`
- **MEPS Point Statistics (9)**: `meps_sw_total_roi_mean`, `meps_sw_total_roi_std`, `meps_sw_total_roi_min`, `meps_sw_total_roi_max`, `meps_cloud_fraction_roi_mean`, `meps_cloud_fraction_roi_std`, `meps_sw_grad_x`, `meps_sw_grad_y`, `meps_sw_laplacian`

### Added Stage 6.4 Revision Trajectory Features (8 features)
1. `rev_cloud_latest`: Latest causally eligible cloud fraction forecast ($f_4$)
2. `rev_cloud_delta_6h`: Short-term cloud forecast revision ($f_4 - f_3$)
3. `rev_cloud_delta_total`: Total cloud forecast revision ($f_4 - f_1$)
4. `rev_cloud_std`: Volatility / trajectory dispersion of cloud forecasts ($\text{std}(f_1, f_2, f_3, f_4)$)
5. `rev_sw_latest`: Latest causally eligible SW_IN forecast ($f_4$)
6. `rev_sw_delta_6h`: Short-term SW_IN forecast revision ($f_4 - f_3$)
7. `rev_sw_delta_total`: Total SW_IN forecast revision ($f_4 - f_1$)
8. `rev_sw_std`: Volatility / trajectory dispersion of SW_IN forecasts ($\text{std}(f_1, f_2, f_3, f_4)$)

---

## 3. Model Architecture & Hyperparameters

- **Stage 4 Linear Baseline**: `Ridge(alpha=10.0)` fitted on 10 core features (`clearsky_sw`, `meps_sw_total`, `meps_cloud_fraction`, `sin_hour`, `cos_hour`, `solar_zenith_deg`, `meps_sw_total_roi_mean`, `meps_sw_total_roi_std`, `meps_sw_grad_x`, `meps_sw_grad_y`)
- **Stage 5 Residual GBDT**: `HistGradientBoostingRegressor`
  - `loss`: `"absolute_error"`
  - `max_depth`: `4`
  - `min_samples_leaf`: `30`
  - `l2_regularization`: `10.0`
  - `random_state`: `42`

---

## 4. CV & Evaluation Protocol

- **Dataset Split**: EVEN origins (174 origins, 4,176 rows total, 2,885 daytime evaluation rows with `clearsky_sw > 10 W/m²`).
- **Validation Strategy**: 5-Fold Forward-Chaining CV on EVEN origins sorted by `forecast_start`:
  - Fold 1: Train 29 origins | Val 29 origins (591 daytime samples)
  - Fold 2: Train 58 origins | Val 29 origins (696 daytime samples)
  - Fold 3: Train 87 origins | Val 29 origins (648 daytime samples)
  - Fold 4: Train 116 origins | Val 29 origins (396 daytime samples)
  - Fold 5: Train 145 origins | Val 29 origins (221 daytime samples)
- **Aggregation Protocol**: Unweighted arithmetic mean across the 5 validation folds (`np.mean([f['mae'] for f in per_fold])`).

---

## 5. Results & Decision Summary

| Model | Agg Daytime MAE (W/m²) | Agg nMAE (%) | Agg RMSE (W/m²) | Improved Folds | Max Fold Degradation | Decision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E0 Control (Stage 5.2 Champion)** | 39.4236 | 41.46% | 62.83 | - | - | Reference |
| **E1 Candidate (Stage 6.4 Revision)** | 39.1579 | 40.23% | 62.11 | 3 / 5 | +0.2857 W/m² | **REJECT** |

### Decision Gate Breakdown
1. **Gate 1 (MAE Improvement $\ge 0.20$ W/m²)**: **PASS** ($\Delta\text{MAE} = -0.2657$ W/m²)
2. **Gate 2 (Improved in $\ge 4/5$ Folds)**: **FAIL** (Improved in 3/5 folds: Folds 3, 4, 5)
3. **Gate 3 (Max Fold Degradation $\le +0.15$ W/m²)**: **FAIL** (Fold 1 degraded by $+0.2857$ W/m²)
4. **Gate 4 (Candidate nMAE $\le$ Control nMAE)**: **PASS** (40.23% vs 41.46%)
5. **Gate 5 (Candidate RMSE $\le$ Control RMSE)**: **PASS** (62.11 vs 62.83 W/m²)

---

## 6. Authoritative Decision & Next Steps

**Decision**: **REJECT STAGE 6.4 CANDIDATE**. Retain Stage 5.2 Architecture A as operational champion.  
**ODD Status**: 100% UNTOUCHED and UNREAD.
