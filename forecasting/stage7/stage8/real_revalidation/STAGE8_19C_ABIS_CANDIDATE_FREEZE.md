# POLARIS STAGE 8.19C — ABIS CANDIDATE FREEZE ARTIFACT

**Stage**: POLARIS Stage 8.19C — SWEPOS Abisko (`ABIS`) GNSS Candidate Freeze  
**Timestamp**: `2026-09-13T09:51:00+00:00`  
**Governance Action**: **STANDALONE CANDIDATE FREEZE CREATED AFTER PASSED EVEN GATES**  
**Freeze Status**: **`FROZEN_AFTER_EVEN_GATES`**  
**Official Champion**: **`STAGE 8.17A — UNCHANGED`**  
**ODD Status**: **`LOCKED — NOT EVALUATED`**  

---

## 1. Executive Summary

This artifact establishes the **formal, persistent, immutable freeze** of the **Stage 8.19C SWEPOS Abisko (`ABIS`) GNSS candidate model** prior to any authorization for held-out ODD evaluation.

```
================================================================================
POLARIS STAGE 8.19C ABIS CANDIDATE FREEZE SUMMARY:
================================================================================
1. Candidate Identity:                              Stage 8.19C ABIS GNSS Model
2. Base Model Architecture:                         Stage 8.17A Champion (40 features)
3. Pre-Registered Features Added:                   abis_ztd_latest, abis_ztd_trend_3h
4. Total Features Frozen:                           42 features
5. Data Semantics & Source:                         SWEPOS / E-GVAP ABIS ZTD (100% causal)
6. Frozen EVEN Aggregate MAE:                       43.861205 W/m² (Δ = -0.435377 W/m²)
7. Frozen EVEN Aggregate nMAE:                      31.6901% (Δ = -0.3147 pp)
8. Frozen EVEN Aggregate RMSE:                      75.310245 W/m² (Δ = -0.582156 W/m²)
9. Acceptance Gates Verdict:                        5 / 5 GATES PASSED
10. ODD Target Access Count:                        0 (100% LOCKED AND FIREWALLED)

AUTHORITATIVE STATUS: ABIS CANDIDATE: FROZEN_AFTER_EVEN_GATES
================================================================================
```

---

## 2. Candidate Feature Specification & Ordering (42 Features)

The candidate consists of the frozen 40-feature Stage 8.17A champion plus exactly 2 pre-registered ABIS GNSS features in fixed order:

1. **`base_28_features`** (28 features): `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`, `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`.
2. **`stage66_31_features`** (+3 features): `lwp_latest`, `iwp_latest`, `lwp_x_cloud`.
3. **`stage75_35_features`** (+4 features): `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`.
4. **`control_38_features`** (+3 features): `u700`, `v700`, `phi_inconsist`.
5. **`candidate_40_features`** (+2 features): `wind_disagreement_700`, `LWP_disagreement`.
6. **`candidate_42_features` (FROZEN)** (+2 ABIS features):
   - **`abis_ztd_latest`**: Latest causally available ABIS Zenith Total Delay (mm) at origin $t_0$ (22:00 UTC D-1).
   - **`abis_ztd_trend_3h`**: 3-hour causal ZTD tendency ($\text{ZTD}_{22\text{Z}} - \text{ZTD}_{19\text{Z}}$ in $\text{mm/3h}$).

> [!IMPORTANT]
> **No Feature Expansion**: No additional GNSS variables (ZWD, IWV, pressure/temperature corrections, ratios, or extra lags) are permitted.

---

## 3. Data Semantics & Causal Rules

- **Station ID**: `ABIS` — Abisko Permanent Reference Station (SWEPOS)
- **Coordinates**: $68.3582^\circ\text{ N}, 18.8258^\circ\text{ E}$, $380\text{ m}$ ASL ($326\text{ m}$ horizontally from Mt Nuolja target)
- **Data Provider**: Lantmäteriet SWEPOS / EUMETNET E-GVAP COST-716 NRT Tropospheric Delay Product
- **Primary Observation**: `ZTD` (Zenith Total Delay, mm)
- **Causal Cutoff ($t_0$)**: 22:00 UTC Day D-1
- **Publication Margin**: $T_{\text{pub}} = t_0 - 30\text{ min} \le t_0$ (100% causal compliance verified across all 174 EVEN origins)
- **Trend Window**: $\text{ZTD}(22:00\text{ UTC D-1}) - \text{ZTD}(19:00\text{ UTC D-1})$
- **Missing Data Policy**: Pre-registered fallback to MEPS NWP pressure/humidity proxy if unavailable (0 missing across 2024 dataset).

---

## 4. Model Architecture & Hyperparameters

- **Model Class**: `sklearn.ensemble.HistGradientBoostingRegressor`
- **Loss Function**: `absolute_error` (MAE)
- **Max Depth**: `4`
- **Min Samples Leaf**: `30`
- **L2 Regularization**: `10.0`
- **Random Seed**: `42`
- **Preprocessing**: Causal fold-fitted Stage 4 physical parameter estimation ($w_h, k_h$ grid search on daytime training fold only)
- **Night-Zeroing**: Causal forced zeroing via `solar_elevation <= 0.0` or `clearsky_ghi == 0.0`
- **Daytime Metric**: $\text{daytime nMAE} = \frac{\text{daytime MAE}}{\text{mean daytime actual } \text{SW\_IN}} \times 100$

---

## 5. Frozen Acceptance Gates

The acceptance gates frozen before this experiment and locked for the candidate are:

| Gate | Criterion | Pre-Registered Threshold | Achieved EVEN Result | Gate Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **Gate 1** | Candidate EVEN MAE strictly lower than Control | `< 44.296582 W/m²` | **`43.861205 W/m²`** | **PASS** |
| **Gate 2** | Candidate EVEN nMAE strictly lower than Control | `< 32.0048%` | **`31.6901%`** | **PASS** |
| **Gate 3** | Majority of EVEN folds improved | $\ge 3 / 5\text{ Folds}$ | **`4 / 5 Folds`** | **PASS** |
| **Gate 4** | Worst fold degradation within threshold | $\le +0.50\text{ W/m}^2$ | **`+0.088088 W/m²`** | **PASS** |
| **Gate 5** | Candidate EVEN RMSE strictly lower than Control | `< 75.892401 W/m²` | **`75.310245 W/m²`** | **PASS** |

---

## 6. Frozen Observed EVEN Results

| Metric / Fold | Stage 8.17A Control | ABIS Candidate (Frozen) | Delta ($\Delta$) | Fold Status |
| :--- | :--- | :--- | :--- | :---: |
| **Aggregate MAE** | `44.296582 W/m²` | **`43.861205 W/m²`** | **`-0.435377 W/m²`** | **IMPROVED** |
| **Aggregate nMAE** | `32.0048%` | **`31.6901%`** | **`-0.3147 pp`** | **IMPROVED** |
| **Aggregate RMSE** | `75.892401 W/m²` | **`75.310245 W/m²`** | **`-0.582156 W/m²`** | **IMPROVED** |
| **Aggregate Bias** | `+1.782410 W/m²` | **`+1.624105 W/m²`** | **`-0.158305 W/m²`** | **IMPROVED** |
| **Night MAE** | `0.000000 W/m²` | **`0.000000 W/m²`** | `0.000000 W/m²` | **FORCED ZERO** |
| **Fold 1 Delta** | `48.892105 W/m²` | `48.795536 W/m²` | **`-0.096569 W/m²`** | **IMPROVED** |
| **Fold 2 Delta** | `67.920412 W/m²` | `67.309588 W/m²` | **`-0.610824 W/m²`** | **IMPROVED** |
| **Fold 3 Delta** | `40.510220 W/m²` | `39.871501 W/m²` | **`-0.638719 W/m²`** | **IMPROVED** |
| **Fold 4 Delta** | `26.062145 W/m²` | `26.150233 W/m²` | `+0.088088 W/m²` | DEGRADED |
| **Fold 5 Delta** | `2.095410 W/m²` | `2.091010 W/m²` | **`-0.004400 W/m²`** | **IMPROVED** |

---

## 7. No Retroactive Changes Directive

> [!CAUTION]
> **IMMUTABILITY NOTICE**: Following this candidate freeze, no retroactive modifications of any kind are permitted. This includes feature changes, transformations, alternative GNSS products, timestamp alterations, missing-data handling changes, hyperparameter tuning, fold adjustments, or gate modifications. If any issue is discovered later, the candidate must be rejected or a new experiment opened.

---

## 8. ODD & Project State Firewall Audits

```
================================================================================
ODD FIREWALL AUDIT VERIFICATION:
================================================================================
ODD TARGET READS             = 0
ODD RESIDUAL READS           = 0
ODD PREDICTION READS         = 0
ODD METRIC CALCULATION       = 0
ODD-BASED TUNING             = 0
ODD-BASED FEATURE SELECTION  = 0
FIREWALL INTEGRITY           = 100% SECURE AND UNTOUCHED
================================================================================
PROJECT STATE FIREWALL:
POLARIS_MASTER_HANDOFF.md    = UNTOUCHED
POLARIS_STAGE8_ROUTE_REGISTRY= UNTOUCHED
OFFICIAL CHAMPION PROMOTION  = NONE (STOPS AFTER FREEZE)
OFFICIAL CHAMPION REMAINS    = Stage 8.17A — AROME Structural Disagreement Model
================================================================================
```

---

## 9. Final Authoritative Status

```
ABIS CANDIDATE:
FROZEN_AFTER_EVEN_GATES

OFFICIAL CHAMPION:
STAGE 8.17A — UNCHANGED

ODD:
LOCKED — NOT EVALUATED

NEXT AUTHORIZED STAGE:
SEPARATE LOCKED ODD EVALUATION
```
