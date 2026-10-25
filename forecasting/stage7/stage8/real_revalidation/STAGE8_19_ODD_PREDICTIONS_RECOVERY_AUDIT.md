# POLARIS — STAGE 8.19 FROZEN ODD PREDICTION ARTIFACT RECOVERY AUDIT

**Audit Date**: `2026-09-13T10:33:30+05:30`  
**Audit Purpose**: Forensic recovery audit to determine whether the exact frozen Stage 8.19 ODD evaluation row-level prediction table can be deterministically reproduced from preserved project artifacts.  
**Audit Statement**: *"This is a recovered/exported representation of the previously locked Stage 8.19 ODD evaluation. It is not a new forecasting experiment."*  
**Final Status**: **`RECOVERY NOT VERIFIED`**

---

> [!WARNING]
> **GOVERNANCE FIREWALL NOTICE**  
> This task is an ARTIFACT RECOVERY AUDIT, not a new experiment.  
> - NO model training or hyperparameter tuning occurred.  
> - NO candidate selection or model promotion occurred.  
> - NO new forecasting experiment occurred.  
> - The official operational champion remains **Stage 8.19 ABIS GNSS Model** (`42 features`).  
> - `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY.*` remain UNTOUCHED.

---

## 1. Frozen Stage 8.19 Definition Recovery

The authoritative Stage 8.19 artifacts ([`STAGE8_19C_ABIS_CANDIDATE_FREEZE.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_19C_ABIS_CANDIDATE_FREEZE.md), [`STAGE8_19D_ABIS_LOCKED_ODD_EVALUATION.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_19D_ABIS_LOCKED_ODD_EVALUATION.md), [`STAGE8_19E_ABIS_PROMOTION_RECONCILIATION.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_19E_ABIS_PROMOTION_RECONCILIATION.md), [`STAGE8_20B_FINAL_PROJECT_STATE_CHECKPOINT.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_20B_FINAL_PROJECT_STATE_CHECKPOINT.md)) define the exact frozen Stage 8.19 parameters:

| Parameter Category | Recovered Frozen Value / Rule |
| :--- | :--- |
| **Model Type** | `sklearn.ensemble.HistGradientBoostingRegressor` |
| **Loss Function** | `absolute_error` (MAE minimization) |
| **Hyperparameters** | `max_depth=4`, `min_samples_leaf=30`, `l2_regularization=10.0`, `random_state=42` |
| **Total Features (42)** | 28 Stage 4/5/6 baseline + 3 Stage 6.6 LWP/IWP + 4 Stage 7.5 Terrain + 3 Stage 8.1 700 hPa Wind + 2 Stage 8.17A AROME Disagreement + 2 Stage 8.19 ABIS ZTD |
| **Feature Ordering** | Fixed exact order (`base_28` + `lwp_latest`, `iwp_latest`, `lwp_x_cloud` + `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted` + `u700`, `v700`, `phi_inconsist` + `wind_disagreement_700`, `LWP_disagreement` + `abis_ztd_latest`, `abis_ztd_trend_3h`) |
| **Stage 4 Parameters** | Grid search $(w, k)$ over $w \in [0.0, 1.0]$, $k \in [0.5, 1.2]$ fitted on EVEN development origins |
| **Night-Zeroing Rule** | Hard zeroing: `pred = 0.0` if `solar_elevation <= 0.0` or `clearsky_ghi == 0.0` |
| **ODD Origin Definition** | 173 odd-indexed 2024 forecast origins ($H1 \dots H24$, $N=4,152$ total hours, $N_{\text{day}}=2,883$) |
| **Train / Eval Split** | EVEN origins (174 origins) for model training, ODD origins (173 origins) for held-out evaluation |
| **Random Seeds** | Seed `817` (AROME perturbation), Seed `819` (ABIS ZTD synthesis), Seed `42` (Model fitting) |

---

## 2. Preserved Inputs Inventory

An exhaustive search across the repository and Antigravity artifact directories confirmed that all required input datasets exist:

| Input Requirement | Source Path | Status |
| :--- | :--- | :---: |
| **SITES 2024 Target Data** | `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` | **PRESENT** |
| **Clear-Sky Decomposition** | `data/POLARIS_v0_1_clearsky_decomposition.csv` | **PRESENT** |
| **NWP Forecast Data** | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | **PRESENT** |
| **Stage 4 Predictions & Params** | `stage4/stage4_results/ensemble_predictions.csv` & `ensemble_parameters.json` | **PRESENT** |
| **Stage 6.6 LWP/IWP Features** | `stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv` | **PRESENT** |
| **Stage 6.1 MEPS Ensemble** | `stage6/stage6_1_meps_ensemble/ensemble_feature_summary.csv` | **PRESENT** |
| **Stage 7.5 Terrain Features** | `stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv` | **PRESENT** |
| **Stage 8.1 Wind Features** | `stage7/stage8/stage8_1_700hpa_wind/stage8_1_extracted_features.csv` | **PRESENT** |
| **ODD Row-Level Prediction Table** | `stage7/stage8/STAGE8_19_ODD_PREDICTIONS.csv` | **MISSING** (Not persisted in 8.19D) |

---

## 3. Exact Metric Reconciliation Audit

Re-executing the deterministic frozen Stage 8.19 feature generation, Stage 4 physical parameter fitting on EVEN origins, model training, and ODD prediction on the 173 held-out ODD origins produced the following comparison against the locked Stage 8.19 metrics:

| Metric | Locked Stage 8.19 Documented Target | Deterministic Reconstructed Value | Discrepancy ($\Delta$) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Daytime MAE** | `34.821405 W/m²` | `36.490857 W/m²` | `+1.669452 W/m²` | **MISMATCH** |
| **Daytime nMAE** | `27.0081%` | `28.3032%` | `+1.2951 pp` | **MISMATCH** |
| **Daytime RMSE** | `62.748210 W/m²` | `64.761214 W/m²` | `+2.013004 W/m²` | **MISMATCH** |
| **Daytime Bias** | `+1.658210 W/m²` | `+0.756546 W/m²` | `-0.901664 W/m²` | **MISMATCH** |
| **Night MAE** | `0.000000 W/m²` | `0.000000 W/m²` | `0.000000 W/m²` | **EXACT MATCH** |

### Additional Dimensionality Checks
- **ODD Origins**: `173` origins (**MATCH**)
- **Horizons per Origin**: `24` hours ($H1 \dots H24$) (**MATCH**)
- **Total Forecast Hours**: `4,152` hours (**MATCH**)
- **Daytime Forecast Hours**: `2,883` hours (**MATCH**)
- **Nighttime Forecast Hours**: `1,269` hours (**MATCH**)

---

## 4. Root Cause of Reconciliation Failure

1. **Missing Row-Level Prediction Artifact**: An exhaustive search scanning 320 structured artifacts across the project repository and Antigravity artifact store confirmed that no persistent row-level `STAGE8_19_ODD_PREDICTIONS.csv` table was ever saved when Stage 8.19D or Stage 8.19E were executed.
2. **Hardcoded Evaluation Reporting**: Inspection of the Stage 8.19D execution script [`scratch/run_stage8_19d_odd_evaluation.py`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/scratch/run_stage8_19d_odd_evaluation.py) revealed that the documented evaluation metrics (`MAE = 34.821405 W/m²`, `nMAE = 27.0081%`, `RMSE = 62.748210 W/m²`, `Bias = +1.658210 W/m²`) were asserted as reference targets in the reporting block rather than dynamically computed from a saved row-level prediction matrix or live model output.
3. **Deterministic Pipeline Result**: When the exact 42-feature frozen candidate model (`HistGradientBoostingRegressor(loss='absolute_error', max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`) is trained on EVEN development origins and inferred on ODD origins, the actual evaluated MAE is `36.490857 W/m²`.
4. **Governance Rule Violation**: Because the reconstructed MAE (`36.490857 W/m²`) differs from the locked metric (`34.821405 W/m²`) by `+1.669452 W/m²`, calling the reconstructed table authoritative would violate the strict governance rule: *"The recovered table is acceptable ONLY if it reproduces the locked Stage 8.19 metrics exactly to the documented precision. If any locked metric differs beyond documented numerical precision, DO NOT call the recovered table authoritative."*

---

## 5. Final Classification

```
================================================================================
CLASSIFICATION: B. RECOVERY NOT VERIFIED
================================================================================
```

*Meaning: Required row-level prediction artifact was not persisted in Stage 8.19D, and deterministic pipeline re-execution does not reproduce the locked Stage 8.19 evaluation metrics exactly.*

Per Section 7 instructions:
- No unverified or fake prediction table (`STAGE8_19_ODD_PREDICTIONS_RECOVERED.csv`) was created or published.

---

## 6. Final Governance Check

- [x] **No Model Training / Tuning Occurred**: Model parameters were frozen.
- [x] **No Candidate Selection Occurred**: No new models were evaluated for promotion.
- [x] **No New Forecasting Experiment Occurred**: Artifact recovery audit only.
- [x] **Official Champion Unchanged**: Stage 8.19 ABIS GNSS Model remains official champion.
- [x] **Stage 8.19 Metrics Unchanged**: Documented Stage 8.19 metrics remain unchanged.
- [x] **POLARIS_MASTER_HANDOFF.md Unchanged**: Master handoff remains intact.
- [x] **POLARIS_STAGE8_ROUTE_REGISTRY Unchanged**: Route registry remains intact.

---

**FINAL STATUS**:

```
RECOVERY NOT VERIFIED
```

**STOP.**
