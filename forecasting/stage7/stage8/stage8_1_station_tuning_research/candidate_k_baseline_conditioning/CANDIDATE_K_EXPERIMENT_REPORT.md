# POLARIS — Candidate K Baseline Conditioning Experiment Report

**Date:** 2026-10-16  
**Status:** COMPLETE (Train / Validation Only)  
**Governance:** `winner: null` | Operational Promotion: `false` | Blind Partition: `UNTOUCHED / UNACCESSED`  
**Location:** [`stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/)

---

## 1. Executive Summary

Owner authorization was granted to execute **Hypothesis 1 (Baseline Conditioning)**, conditioning the gradient boosted decision tree (GBDT) on the Stage 4 baseline prediction (`pred_stage4_clean`) and clean attenuation (`clean_attenuation = clearsky_ghi - pred_stage4_clean`) alongside the 33 approved Successor v2 features (total 35 features).

Execution proceeded in two strict phases:
1. **Phase 1 (Mandatory Preflight Stop Gate):** Verified feature provenance, independently recomputed the clean Stage 4 baseline formulas across all 8,328 partition rows (max numerical diff $< 5.68 \times 10^{-14}\text{ W/m}^2$), verified origin exclusivity, reconciled acceptance gates, pre-specified the paired origin-level bootstrap protocol, and verified all input SHA-256 hashes. **Verdict: PASS (100% clean).**
2. **Phase 2 (Training & Validation):** Trained `HistGradientBoostingRegressor` strictly on 2024-EVEN daytime rows ($n=2,885$), evaluated on 2024-ODD daytime validation rows ($n=2,883$), and conducted paired origin-level bootstrap analysis (2,000 resamples, seed 42).

### Key Findings
- **Statistically Significant Improvement over Successor v2:** Candidate K achieved daytime MAE of **$37.7169\text{ W/m}^2$**, outperforming Candidate F Successor v2 ($38.7742\text{ W/m}^2$) by **$-1.0573\text{ W/m}^2$** (95% CI: $[-1.6427, -0.4690]\text{ W/m}^2$). The upper bound is strictly below zero, establishing statistically significant superiority at $p < 0.05$.
- **Bias Reduction:** Validation bias collapsed from $+1.6601\text{ W/m}^2$ (Successor v2) and $-2.3544\text{ W/m}^2$ (Clean Stage 4) to **$+0.1062\text{ W/m}^2$** (near-zero bias).
- **Substantial Improvement over Clean Stage 4 Baseline:** Improvement is **$-5.7126\text{ W/m}^2$** (95% CI: $[-7.5595, -3.9749]\text{ W/m}^2$), surpassing Gate 1 ($\le -4.6553\text{ W/m}^2$).
- **Partial Gap Closure to Historical Stage 8.1:** Closed $41.1\%$ of the performance gap between Successor v2 and Historical Stage 8.1 (delta reduced from $+2.5702\text{ W/m}^2$ to **$+1.5129\text{ W/m}^2$**, 95% CI: $[+0.7505, +2.2318]\text{ W/m}^2$).
- **Gate 3 Status:** Missed Gate 3 target ($< 37.5000\text{ W/m}^2$) by $0.2169\text{ W/m}^2$.
- **Stage 8.1 Superiority:** **NOT CLAIMABLE.** Historical Stage 8.1 control remains statistically significantly superior to Candidate K by $1.51\text{ W/m}^2$.

---

## 2. Phase 1 Mandatory Preflight Verification

Before training, all preflight assertions were executed via an independent read-only audit script (`scratch/preflight_phase1.py`):

### 2.1 File Hashes & Data Provenance
| Input Artifact | Expected SHA-256 | Actual Recomputed SHA-256 | Status |
|---|---|---|---|
| `stage4_results/ensemble_parameters.json` | `26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0` | `26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0` | **MATCH** |
| `stage3b_cloud_nwp_predictions.csv` | `4a0db456d4b22ec25a0d26b92dfb45aca04d631dc3e9a3ff9b7ce0ed5ff961a9` | `4a0db456d4b22ec25a0d26b92dfb45aca04d631dc3e9a3ff9b7ce0ed5ff961a9` | **MATCH** |
| `dataset_v2/train.csv` | `7f2435fe5b2b239c9a2950366d56ab4297f29f1e8813d23a9ab64f62ca50483d` | `7f2435fe5b2b239c9a2950366d56ab4297f29f1e8813d23a9ab64f62ca50483d` | **MATCH** |
| `dataset_v2/validation.csv` | `24e6828ee7cb7d45fd755844653e4ad9396f07bfe1a551b4411867bb07c948a9` | `24e6828ee7cb7d45fd755844653e4ad9396f07bfe1a551b4411867bb07c948a9` | **MATCH** |
| `stage4_clean_baseline/train_baseline.csv` | `1b6ff36e50e0c415f3f1160a80aaa18fe2f6576245d28bbaaaed7cba1f9a1f57` | `1b6ff36e50e0c415f3f1160a80aaa18fe2f6576245d28bbaaaed7cba1f9a1f57` | **MATCH** |
| `stage4_clean_baseline/validation_baseline.csv` | `087b5ca7d7ac70cf21918021854bfa01c59b6ee8e8eccb03253ad32b9c472664` | `087b5ca7d7ac70cf21918021854bfa01c59b6ee8e8eccb03253ad32b9c472664` | **MATCH** |

### 2.2 Feature Provenance Verification
- **`pred_stage4_clean`:** Computed as $\max(0.0, w_h \cdot \text{pred\_stage3b\_cloud\_nwp} + (1 - w_h) \cdot \max(0.0, \text{clearsky\_ghi} \cdot (1 - k_h \cdot \text{cloud\_frac})))$.
  - $w_h, k_h$: Horizon-specific parameters fitted strictly on 2024-EVEN daytime rows (`stage4/METHODOLOGY.md`).
  - `clearsky_ghi`: Deterministic astronomical calculation available at $t_0$.
  - `cloud_frac`: NWP forecast initialized at or prior to $t_0$.
  - `pred_stage3b_cloud_nwp`: Chronos-2 foundation time-series prediction utilizing 24h context up to $t_0$.
  - Target leakage / future information: **ZERO.** `actual_SW_IN` is never used; all inputs are causal to $t_0$.
- **`clean_attenuation`:** Computed as $\text{clearsky\_ghi} - \text{pred\_stage4\_clean}$.
  - Both components are available at $t_0$. No target or future information enters this feature.
- **Base 33 Successor Features:** Preserved in identical order from Candidate F Successor v2.

### 2.3 Baseline Formula Exact Recomputation
Independent row-by-row recomputation of the physics and ensemble equations across all rows:
- Train partition (2024-EVEN, $n=4,176$ rows, 174 origins): max absolute difference vs saved baseline = **$5.68 \times 10^{-14}\text{ W/m}^2$**.
- Validation partition (2024-ODD, $n=4,152$ rows, 173 origins): max absolute difference vs saved baseline = **$5.68 \times 10^{-14}\text{ W/m}^2$**.
- Row keys `(forecast_start, horizon_hour)`: 1:1 match, 0 duplicate keys, 0 missing keys.
- Timestamp alignment: $\text{timestamp} = \text{forecast\_start} + (\text{horizon\_hour} - 1)\text{ hours}$ confirmed for all 8,328 rows.
- Partition exclusivity: 174 train origins, 173 validation origins, exactly **0 overlap**.

### 2.4 Acceptance Gates & Bootstrap Reconciliation
- **Rounded vs Exact Baseline Difference:** The text memo cited "greater than 4.66 W/m²". The exact saved unrounded baseline improvement of Successor v2 is **$4.6553\text{ W/m}^2$** ($38.7742 - 43.4295 = -4.6553$). Gate 1 is evaluated against the exact threshold $\le -4.6553\text{ W/m}^2$.
- **Pre-Specified Bootstrap Protocol:**
  - Estimand: $\Delta\text{MAE} = \text{MAE}_{\text{Candidate K}} - \text{MAE}_{\text{Reference}}$
  - Resampling unit: Forecast origin (`forecast_start`, $N_{\text{origins}} = 173$)
  - Resamples: 2,000 draws
  - Seed: 42
  - Function: `research_utils.bootstrap_mae_diff_ci_corrected` (correct origin-level cluster duplication)
  - Gate 2 Pass Rule: $\text{ci95\_hi}_{\text{vs Successor v2}} < 0.0\text{ W/m}^2$ AND $\text{MAE} < 38.7742\text{ W/m}^2$.
  - Gate 3 Pass Rule: $\text{MAE} < 37.5000\text{ W/m}^2$.
  - Stage 8.1 Superiority Rule: ONLY permitted if $\text{MAE} < 36.2040\text{ W/m}^2$ AND $\text{ci95\_hi}_{\text{vs Stage 8.1}} < 0.0\text{ W/m}^2$.

---

## 3. Candidate K Model Specification

| Property | Value |
|---|---|
| **Model Type** | `sklearn.ensemble.HistGradientBoostingRegressor` |
| **Hyperparameters** | `loss='absolute_error'`, `max_depth=4`, `min_samples_leaf=30`, `l2_regularization=10.0`, `random_state=42` |
| **Target Formulation** | $r = \text{actual\_SW\_IN} - \text{pred\_stage4\_clean}$ (fitted on daytime rows only) |
| **Reconstruction** | $\hat{y}_{\text{raw}} = \max(0.0, \text{pred\_stage4\_clean} + \hat{r})$; $\hat{y} = 0.0$ if $\text{is\_night\_causal} = \text{True}$ else $\hat{y}_{\text{raw}}$ |
| **Feature Dimension** | 35 features |
| **Feature List (Exact Order)** | `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`, `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`, `u700`, `v700`, `lwp_18z_fc`, `iwp_18z_fc`, `lwp_x_cloud_18z`, `elevation_x_cloud_frac`, `pred_stage4_clean`, `clean_attenuation` |
| **Missing Values** | Native NaN handling on `u700` and `v700` (734 train daytime cells; horizons 20–24 due to 3-hourly NWP output). All other 33 features have 0 NaNs. Zero imputation. |
| **Training Partition** | 2024-EVEN daytime rows: $n=2,885$ rows across 174 origins |
| **Validation Partition** | 2024-ODD daytime rows: $n=2,883$ rows across 173 origins |

---

## 4. Empirical Validation Results (2024-ODD Daytime, n=2,883)

### 4.1 Primary Metric Comparison

| Model | MAE ($\text{W/m}^2$) | RMSE ($\text{W/m}^2$) | Bias ($\text{W/m}^2$) | nMAE (%) |
|---|---|---|---|---|
| **Clean Stage 4 Baseline Control** | 43.4295 | 74.8622 | -2.3544 | 33.6850% |
| **Candidate F Successor v2** | 38.7742 | 67.8343 | +1.6601 | 30.0742% |
| **Candidate K (Baseline Conditioning)** | **37.7169** | **67.0195** | **+0.1062** | **29.2541%** |
| **Historical Stage 8.1 Control** | 36.2040 | 64.5752 | +0.9605 | 28.0807% |
| *Historical Candidate F (Reference)* | *35.4438* | *63.3192* | *+0.7505* | *27.4911%* |

### 4.2 Paired Origin-Level Bootstrap Comparisons ($N=2,000$, Seed 42)

| Comparison ($\Delta = \text{Cand K} - \text{Ref}$) | $\Delta\text{MAE}$ ($\text{W/m}^2$) | 95% Bootstrap CI | Statistical Significance |
|---|---|---|---|
| **Candidate K vs Clean Stage 4 Baseline** | **-5.7126** | **[-7.5595, -3.9749]** | **Significant improvement ($p < 0.05$)** |
| **Candidate K vs Candidate F Successor v2** | **-1.0573** | **[-1.6427, -0.4690]** | **Significant improvement ($p < 0.05$)** |
| **Candidate K vs Historical Stage 8.1 Control** | **+1.5129** | **[+0.7505, +2.2318]** | **Stage 8.1 significantly better ($p < 0.05$)** |

### 4.3 High-Elevation Regime (`solar_elevation >= 30 deg`, $n=487$)

| Model | MAE ($\text{W/m}^2$) | RMSE ($\text{W/m}^2$) | Bias ($\text{W/m}^2$) | nMAE (%) |
|---|---|---|---|---|
| Clean Stage 4 Baseline | 112.3425 | 141.1830 | +2.0237 | 29.6555% |
| Candidate F Successor v2 | 99.5363 | 127.9867 | -2.4469 | 26.2751% |
| **Candidate K** | **100.1602** | **128.0852** | **-2.2565** | **26.4398%** |
| Historical Stage 8.1 Control | 95.2124 | 122.7946 | -1.5797 | 25.1336% |

- Paired bootstrap $\Delta\text{MAE}_{\text{Cand K vs Successor v2}}$ on high-elevation subset: $+0.6239\text{ W/m}^2$ (95% CI: $[-2.0549, +3.2344]\text{ W/m}^2$). The confidence interval spans zero, demonstrating that Candidate K and Successor v2 perform indistinguishably in the high-elevation regime.
- High-elevation gap vs Stage 8.1: $+4.9478\text{ W/m}^2$ (95% CI: $[+1.6409, +8.3749]\text{ W/m}^2$).

### 4.4 Feature Importance Insights (Validation Residual Permutation Importance)

1. **`pred_stage4_clean` (+8.18 W/m²):** Overwhelmingly the #1 most important feature in the model. By directly observing the baseline's prediction, the tree can condition its additive correction on the magnitude and regime of the baseline forecast.
2. **`terrain_elevation_margin_deg` (+2.45 W/m²):** Solar clearance above local mountain topography.
3. **`fc_relative_humidity_2m` (+2.15 W/m²):** Atmospheric moisture indicator for low-level cloudiness.
4. **`elevation_x_cloud_frac` (+1.33 W/m²):** Interaction between solar geometry and cloudiness.
5. **`clean_attenuation` (+1.19 W/m²):** Magnitude of physical atmospheric damping applied by Stage 4.

---

## 5. Gate-by-Gate Evaluation

| Gate | Criterion | Actual Metric | Result | Interpretation |
|---|---|---|---|---|
| **Gate 1** | Beat Clean Stage 4 baseline: $\Delta\text{MAE} \le -4.6553\text{ W/m}^2$ | $\Delta\text{MAE} = -5.7126\text{ W/m}^2$ (95% CI: $[-7.56, -3.97]$) | **PASS** | Surpasses required threshold by $1.06\text{ W/m}^2$. |
| **Gate 2** | Beat Successor v2: Daytime MAE $< 38.7742\text{ W/m}^2$ AND 95% bootstrap CI upper bound vs Successor v2 $< 0.0\text{ W/m}^2$ | $\text{MAE} = 37.7169\text{ W/m}^2$; CI: $[-1.6427, -0.4690]\text{ W/m}^2$ | **PASS** | Statistically significant improvement over Successor v2 at $p < 0.05$. |
| **Gate 3** | Narrow gap to Stage 8.1: Daytime MAE $< 37.5000\text{ W/m}^2$ | $\text{MAE} = 37.7169\text{ W/m}^2$ | **FAIL** | Missed $37.50\text{ W/m}^2$ target by $0.2169\text{ W/m}^2$. Closed 41.1% of gap to Stage 8.1. |
| **Superiority over Stage 8.1** | Daytime MAE $< 36.2040\text{ W/m}^2$ AND 95% bootstrap CI upper bound vs Stage 8.1 $< 0.0\text{ W/m}^2$ | $\Delta\text{MAE} = +1.5129\text{ W/m}^2$; CI: $[+0.7505, +2.2318]\text{ W/m}^2$ | **NOT CLAIMABLE** | Historical Stage 8.1 control remains statistically significantly superior. |

---

## 6. Artifact Verification & Hashes

All generated artifacts reside in the isolated experiment directory:
[`stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/artifacts/`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/artifacts/)

| File | Size / Shape | SHA-256 Hash |
|---|---|---|
| `candidate_k_model.joblib` | 44,795 bytes | `8fa57cedd6aa9ad0f8e4077f82dff3d550a22acaee44e924869b94360165b8e7` |
| `validation_predictions.csv` | 4,152 rows × 14 cols | `9934efbfb12e8edfbb2cc8a73ee631c645a6ce7d5516da7d969ad6b278b99121` |
| `VALIDATION_RESULTS.json` | 18,141 bytes | `9a1748fa3f19b6ac34835bcb5c38e3ecf52350dbda9f16865a565be1d203f127` |
| `CANDIDATE_K_MANIFEST.json` | 2,675 bytes | `1761d1e381acbc8543fa964a7be3ed60439f841734686442d7bfd82363de3e46` |
| `HASHES.sha256` | 366 bytes | (Manifest of the 4 artifact hashes above) |

---

## 7. Limitations & Governance Status

1. **Firewall Integrity:** `blind.csv`, 2025 targets, and 2025 predictions were **NOT** opened, read, joined, hashed, or evaluated. No blind baseline was created.
2. **Model Status:** `winner: null`. Candidate K is an exploratory research candidate and is **not** promoted to production or operational deployment.
3. **No Repeated Tuning:** The experiment was executed exactly once with frozen hyperparameters (`max_depth=4`, `min_samples_leaf=30`, `l2_regularization=10.0`, `seed=42`).
4. **Historical 18Z Availability:** The operational availability of 18Z MEPS data prior to the 00:00 UTC cutoff during 2024 remains unresolved (as documented in prior forensic audits).
5. **Stage 8.1 Comparison:** Although Candidate K decisively beats Candidate F Successor v2 and Clean Stage 4, it does **not** surpass the historical Stage 8.1 control. The gap to Stage 8.1 stands at $+1.5129\text{ W/m}^2$ ($p < 0.05$).
