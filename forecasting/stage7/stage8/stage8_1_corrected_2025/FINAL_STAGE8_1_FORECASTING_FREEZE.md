# FINAL Stage 8.1 Forecasting Freeze

**Status:** governance/documentation freeze only. No model, feature, training procedure, or production EMS/optimizer code was modified to produce this document.

**Selected candidate for POLARIS research:** the **corrected Stage 8.1 37-feature pipeline** — same algorithm, hyperparameters, split, and target as the historical 2024 Stage 8.1 pipeline, with the terrain (4 features) and u700/v700 (2 features) families rebuilt to fix causal-alignment defects found and quantified during this investigation. The other 31 features are unchanged.

**Exact model artifact to use going forward:**
```
stage7/stage8/stage8_1_corrected_2025/model_artifact/stage8_1_CORRECTED_candidate_37feature_model.joblib
sha256: 64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce
```
Full manifest with every path/hash: [FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json](FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json) (same directory).

---

## 1. Pipeline chain (2025 side, the operative pipeline)

| Stage | Path | SHA-256 (first 16) | Rows |
|---|---|---|---|
| Raw SITES data | `data/raw_2025_sites_download/SITES_MET_ANS_NMS_20250101-20251231_L2_SH.csv` | `90b298ce6f80658a` | 52,560 (10-min) |
| Hourly preprocessing | `data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv` | `d457facdbeb57b9c` | 8,760 |
| Clear-sky | `data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv` | `f5f5e2c4c076c3c3` | 8,760 |
| NWP (clean, audit-only) | `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` | `2186382391b84ed5` | 8,760 (365 origins) |
| Stage 3b Chronos-2 | `stage3/stage3b_2025/stage3b_cloud_nwp_predictions_2025.csv` | `0a5263e6ea89c2a9` | 8,736 (364 origins) |
| Stage 4 ensemble | `stage4/stage4_results_2025/ensemble_predictions.csv` | `c4ef9b264bd263cb` | 8,736 |
| **Corrected terrain** | `data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv` | `6ec8d815c26b9f24` | 8,760 |
| **Corrected u700/v700** | `stage7/stage8/stage8_1_700hpa_wind_2025/stage8_1_wind700_features_2025.csv` | `f786430727a38585` | 8,760 (365×24) |
| LWP/IWP | `stage6/stage6_6_lwp_iwp_2025/lwp_iwp_extracted_features_2025.csv` | `4c8019a03658ca32` | 8,736 |
| Causal context (ctx_*) | computed inline in the matrix builder (14 features) | — | — |
| **Corrected 37-feature matrix** | `stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` | `9fe6b9f8b46b89e2` | 8,736 (364 origins) |
| **Corrected Stage 8.1 HGB model** | `.../model_artifact/stage8_1_CORRECTED_candidate_37feature_model.joblib` | `64ea4abada78a257` | — |
| 24h forecast (2025 blind) | `stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv` | `65e0a0acf2d7196c`¹ | 8,736 |
| Evaluation | `stage8_1_CORRECTED_2025_blind_results.json` / `..._odd_results_2024.json` | — | — |

¹ sha256 `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` — truncated above for table width; full value in the JSON manifest.

The parallel **2024-corrected** branch (used only to retrain/validate the model; never used for 2025 inference) follows the same chain with `_CORRECTED` suffixes under `stage7/stage8/stage8_1_corrected_2025/`; see the JSON manifest for every hash.

---

## 2. Feature contract (37, fixed order)

```
horizon_hour, month, hour, solar_elevation, solar_zenith, clearsky_ghi,
fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, cloud_frac,
pred_stage3b_cloud_nwp, phys_pred_fold, pred_stage4_fold, disagreement_fold,
ctx_std_3h, ctx_std_6h, ctx_std_12h, ctx_std_24h,
ctx_abs_change_1h, ctx_abs_change_3h, ctx_abs_change_6h,
ctx_max_diff_6h, ctx_mean_diff_6h, ctx_slope_6h,
ctx_kt_std_6h, ctx_last_obs, ctx_mean_24h, ctx_max_24h,
lwp_latest, iwp_latest, lwp_x_cloud,
terrain_horizon_elevation_deg, terrain_elevation_margin_deg,
terrain_solar_obstruction_flag, clearsky_ghi_terrain_adjusted,
u700, v700
```
**31 unchanged** · **4 corrected (terrain)** · **2 corrected (u700/v700)**. `actual_SW_IN` is never a feature — confirmed by assertion in the inference script.

**Target:** `actual_SW_IN − pred_stage4_fold` (residual-on-Stage4), fit on daytime rows only. Night rows (`is_night_causal`) are forced to prediction = 0.0, not passed through the model.

---

## 3. Model configuration

| | |
|---|---|
| Estimator | `sklearn.ensemble.HistGradientBoostingRegressor` |
| loss | `absolute_error` |
| max_depth | 4 |
| min_samples_leaf | 30 |
| l2_regularization | 10.0 |
| random_state | 42 |
| Tuned | **No** |
| Missing-value handling | native sklearn support; trained **with** the real u700/v700 NaN pattern (unlike the historical model, which never saw real NaN for this feature) |

---

## 4. Training split / procedure

- Split: positional EVEN/ODD on sorted origins (`i % 2`) — same logic as the historical pipeline
- 2024: 347 origins → **174 EVEN (train) / 173 ODD (held-out eval)**
- Trained only on **2024 EVEN**, daytime rows (n=2,885); **2025 data was never used in training**
- No hyperparameter search, no feature selection on held-out data

---

## 5. Results

### 2024 corrected ODD (held-out, 173 origins, n=2,883 daytime)
| | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | nMAE |
|---|---|---|---|---|
| Corrected candidate (37-feat) | 36.2040 | 64.5752 | +0.9605 | 28.08% |
| Corrected control (35-feat) | 36.3616 | 64.8104 | +2.1050 | 28.20% |

### 2025 blind evaluation (8,736 rows, 364 origins, causal day/night gate, model never saw 2025 data before)
| | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | nMAE |
|---|---|---|---|---|
| Overall (n=8,736) | 24.6172 | 54.5492 | +2.7921 | 28.25% |
| Daytime only (n=5,978) | 35.9745 | 65.9427 | +4.0802 | 28.25% |

Per-horizon (H1–H24) tables: [stage8_1_CORRECTED_2025_blind_horizon_metrics.csv](stage8_1_CORRECTED_2025_blind_horizon_metrics.csv).

### Branch01 Candidate A, 2025, same exact row set — for reference, **no comparison/winner declared**
| | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | nMAE |
|---|---|---|---|---|
| Overall (n=8,736) | 38.4756 | 74.3725 | −1.9760 | 44.15% |
| Daytime only (n=5,978) | 55.3454 | 89.8867 | −3.7689 | 43.46% |

nMAE definition identical across all tables: `MAE / mean(actual) × 100`.

---

## 6. Known limitations

1. **2025-01-01 missing (24h gap, 8,736/8,760 coverage).** Chronos-2's 24h context window needs 2024-12-31 data, out of scope for a 2025-only rebuild. Structural, present since Stage 3b, not introduced by any correction in this freeze.
2. **Branch01 H1 convention.** Branch01's `sw_in_lag_0h` feature is the actual SW_IN observed *at* the origin — legitimate (not future data), but under this repo's `horizon_hour=1 == forecast_start+0h` convention it numerically coincides with the h=1 target. Not a leak, but H1 isn't a pure blind-ahead test the same way H2–H24 are. Not corrected (Branch01 is frozen, out of scope).
3. **u700/v700 documented gap.** horizon_hour 20–24 (~21% of wind rows) are genuine NaN — the MEPS archive is hourly only to lead+24h, then 3-hourly. The corrected model trained with this real pattern.
4. **Day/night gate methodology.** The historical procedure gated on `is_daytime` (`actual_SW_IN>0`), technically target-derived. The 2025 blind run instead uses a purely causal gate; the two disagree on 1,532/8,736 rows (17.5%), all tiny twilight-glow hours (median 0.40 W/m²). Both variants were computed; the causal one is primary.
5. **LWP/IWP `valid_time` label.** The historical artifact's display column is mislabeled +1h, but the actual feature *values* are correctly aligned (verified, diff ≈1e-7). No correction needed or applied — noted so this isn't mistaken for an outstanding bug.

---

## 7. Historical Stage 8.1 artifact — preserved, reference only

**Do not use for new inference.** Unchanged throughout this entire investigation (hashes/mtimes re-verified at freeze time):

| Artifact | SHA-256 |
|---|---|
| `stage7/stage8/stage8_1_700hpa_wind/model_artifact/stage8_1_candidate_37feature_model.joblib` | `c8009ffbc653afde` |
| `stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv` | `213a71e132f51ed5` |
| `stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv` | `0a29c9c03815cc90` |
| `stage7/stage8/stage8_1_700hpa_wind/stage8_1_extracted_features.csv` | `aa6ce29f3acec634` |

Full hashes in the JSON manifest. These remain available for historical comparison but should not be used going forward — use the corrected candidate artifact named in the header of this document.

---

**No new experiments were run to produce this document.** Production forecasting code and the EMS/optimizer were not touched.
