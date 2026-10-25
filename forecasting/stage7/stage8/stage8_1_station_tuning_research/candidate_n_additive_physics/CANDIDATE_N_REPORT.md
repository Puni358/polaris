# POLARIS — Candidate N Additive Physics & High-Elevation Specialist Experiment Report

**Date:** 2026-10-17  
**Status:** COMPLETE (2024-ODD Validation & 2025 Blind Evaluated)  
**Governance:** `winner: null` | Operational Promotion: `false` | Zero Retraining on Blind  
**Location:** [`stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/)

---

## 1. Executive Summary

Following the discovery of the low-elevation / terrain-shading singularity in Candidates L ($k_t$-Jacobian formulation) and M (monotonic constraints), research was directed to develop **Candidate N (Additive Physics & High-Elevation Specialist)**. 

Candidate N resolves the core dilemma between low-elevation stability and high-elevation accuracy:
1. **Low-Elevation Stability ($\theta < 30^\circ$):** Preserves Candidate K's unweighted additive residual target ($r = \text{actual\_SW\_IN} - \text{pred\_stage4\_clean}$) on daytime rows. This avoids dividing by small clear-sky values during twilight and terrain occlusion, maintaining rock-solid low-elevation error ($\sim 25.04\text{ W/m}^2$ on 2024-ODD, $\sim 23.79\text{ W/m}^2$ on 2025 Blind).
2. **Transition-Cloud Physics:** Injects Candidate J's proven `elevation_x_transition_cloud` interaction into the baseline conditioning matrix to form the **pure 36-feature contract** (35 Candidate K features + `elevation_x_transition_cloud`).
3. **Variance Suppression:** Applies a 25-seed feature-subsampled bagged GBDT ensemble (`max_features=0.78`, `min_samples_leaf=25`, `l2_reg=15.0`) to suppress split variance without biasing the L1 conditional median.
4. **High-Elevation $k_t$ Specialist Ramp:** Integrates an unshaded 15-seed bagged $k_t$ specialist ensemble that ramps smoothly into the forecast only when $\theta \ge 22^\circ$ and local terrain obstruction is zero (`terrain_solar_obstruction_flag == 0`), capturing deep optical depth dynamics under direct sunlight.

### Key Empirical Findings
- **2024-ODD Validation Benchmark:** Candidate N6 achieved a daytime validation MAE of **$36.8383\text{ W/m}^2$**, outperforming Candidate K ($37.7169\text{ W/m}^2$) by **$-0.8787\text{ W/m}^2$** (95% Paired Clustered Bootstrap CI: **$[-1.4614, -0.3347]\text{ W/m}^2$**, $p < 0.05$).
- **2025 Blind Generalization:** On the 2025 Blind Partition ($n = 5,978$ daytime rows across $N = 364$ origins), Candidate N6 achieved **$36.7856\text{ W/m}^2$** MAE, outperforming:
  - Clean Stage 4 Physical Baseline ($41.7661\text{ W/m}^2$) by **$-4.9804\text{ W/m}^2$** (95% CI: $[-6.2515, -3.6851]\text{ W/m}^2$, $p < 0.001$).
  - Candidate F Successor v2 ($38.1899\text{ W/m}^2$) by **$-1.4043\text{ W/m}^2$** (95% CI: $[-1.8570, -0.9777]\text{ W/m}^2$, $p < 0.001$).
  - Candidate K Control ($37.4603\text{ W/m}^2$) by **$-0.6746\text{ W/m}^2$** (95% CI: **$[-1.0951, -0.2779]\text{ W/m}^2$**, $p < 0.05$).
- **High-Elevation MAE Reduction:** High-elevation error ($\theta \ge 30^\circ$) on 2025 Blind dropped from $114.49\text{ W/m}^2$ (Clean Stage 4) and $106.70\text{ W/m}^2$ (Candidate K) to **$103.2134\text{ W/m}^2$** (Candidate N6).
- **Low-Elevation Preservation:** Low-elevation error ($\theta < 30^\circ$) on 2025 Blind was preserved at **$23.7924\text{ W/m}^2$** (vs $23.9171\text{ W/m}^2$ for Candidate K and $27.5418\text{ W/m}^2$ for Clean Stage 4).

---

## 2. Preflight Verification & Governance Safeguards

1. **Dataset Integrity & Provenance:**
   - 2024 Development Matrix: [`candidate_k_2024_clean_matrix.parquet`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet) (SHA-256: `4c0a05bf...`).
   - 2025 Blind Inputs: [`candidate_f_successor_18z/dataset_v2/blind.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/blind.csv) joined with [`candidate_f_successor_18z/stage4_clean_baseline/blind_baseline.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/stage4_clean_baseline/blind_baseline.csv).
2. **Zero Retraining on Blind:**
   - Pre-asserted SHA-256 hashes of all `.joblib` model binaries were strictly verified before inference. Zero model weights or hyperparameters were fit, tuned, or updated on 2025 data.
3. **Clean Stage 4 Blind Baseline:**
   - Generated with frozen 2024-EVEN parameters ($w_h, k_h$ from `stage4/stage4_results/ensemble_parameters.json`, SHA-256: `26cfbd19...`). Ground-truth `actual_SW_IN` was strictly excluded from `pred_stage4_clean` computation.
4. **Bootstrap Specification:**
   - Clustered block bootstrap resampled across all forecast origins ($N = 173$ origins for 2024-ODD, $N = 364$ origins for 2025 Blind) with 2,000 draws and seed 42.

---

## 3. Architecture & Model Specification

### 3.1 Feature Contracts

- **Candidate K Base (35 features):**  
  `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`, `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`, `u700`, `v700`, `lwp_18z_fc`, `iwp_18z_fc`, `lwp_x_cloud_18z`, `elevation_x_cloud_frac`, `pred_stage4_clean`, `clean_attenuation`.
- **Candidate N Pure Synthesis (36 features):**  
  Candidate K (35 features) + `elevation_x_transition_cloud`.

### 3.2 Candidate N1 Specification (Single Tree)
- **Model Type:** `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, max_features=1.0, random_state=42)`
- **Target:** $r = \text{actual\_SW\_IN} - \text{pred\_stage4\_clean}$
- **Reconstruction:** $\hat{y} = \max(0.0, \text{pred\_stage4\_clean} + \hat{r}) \cdot \mathbb{I}(\text{causal\_day\_mask})$

### 3.3 Candidate N6 Specification (Bagged Additive + Unshaded $k_t$ Specialist Ramp)
- **Base Additive Ensemble:** 25-seed feature-subsampled GBDT ensemble (`max_features=0.78`, `min_samples_leaf=25`, `l2_reg=15.0`, seeds 100–124) predicting additive residual $r$.
- **High-Elevation $k_t$ Specialist Ensemble:** 15-seed feature-subsampled GBDT ensemble (`max_features=0.80`, `min_samples_leaf=30`, `l2_reg=15.0`, seeds 500–514) trained with sample weight $w_i = \text{GHI\_cs\_terrain}_i + 15.0$ on the clearness residual $r_{kt} = (\text{actual}_i - \text{pred\_stage4}_i) / (\text{GHI\_cs\_terrain}_i + 15.0)$.
- **Smooth Blending Mechanism:**
  $$\alpha(\theta) = 0.55 \cdot \text{clip}\left(\frac{\theta - 22.0^\circ}{10.0^\circ}, 0.0, 1.0\right)$$
  $$w = \alpha(\theta) \cdot (1 - \text{terrain\_solar\_obstruction\_flag})$$
  $$\hat{y}_{\text{N6}} = (1.0 - w) \cdot \hat{y}_{\text{additive\_bagged}} + w \cdot \hat{y}_{kt\_\text{bagged}}$$
  $$\hat{y} = \hat{y}_{\text{N6}} \cdot \mathbb{I}(\text{causal\_day\_mask})$$

---

## 4. 2024-ODD Validation Results (Daytime, n=2,883)

| Model | MAE ($\text{W/m}^2$) | RMSE ($\text{W/m}^2$) | Bias ($\text{W/m}^2$) | LE MAE ($\theta < 30^\circ$) | HE MAE ($\theta \ge 30^\circ$) | HE Bias ($\theta \ge 30^\circ$) | vs K (95% CI) | Gate |
|---|---|---|---|---|---|---|---|---|
| **Clean Stage 4 Baseline** | 43.4508 | 74.8530 | -1.9716 | 29.4482 | 112.3425 | +2.0237 | +5.7339 [+3.97, +7.56] | BASE |
| **Candidate K Control** | 37.7169 | 67.0195 | +0.1062 | 25.0250 | 100.1602 | -2.2565 | +0.0000 [+0.00, +0.00] | CTRL |
| **Candidate N1** | 37.1789 | 66.1190 | +0.3609 | 24.9901 | 97.1466 | -0.5273 | -0.5381 [-1.04, -0.04] | **PASS** |
| **Candidate N6** | **36.8383** | **64.9718** | **+0.2509** | **25.0409** | **94.8802** | **-4.3662** | **-0.8787 [-1.46, -0.33]** | **PASS** |

---

## 5. One-Shot 2025 Blind Evaluation Results (Daytime, n=5,978)

Evaluated strictly once on the genuine 2025 Blind Partition ($N = 364$ origins, $n = 5,978$ daytime rows, zero model retraining):

### 5.1 Primary Metric Comparison

| Model Architecture | Blind MAE ($\text{W/m}^2$) | RMSE ($\text{W/m}^2$) | Bias ($\text{W/m}^2$) | LE MAE ($\theta < 30^\circ$) | HE MAE ($\theta \ge 30^\circ$) | HE Bias ($\theta \ge 30^\circ$) | vs K (95% Bootstrap CI) | Gate |
|---|---|---|---|---|---|---|---|---|
| **Clean Stage 4 Baseline** | 41.7661 | 74.1735 | -7.1523 | 27.5418 | 114.4873 | -10.9374 | +4.3058 [+3.1535, +5.4899] | BASE |
| **Candidate F Successor v2** | 38.1899 | 69.8646 | -2.1984 | 24.6789 | 107.2648 | -10.3394 | +0.7297 [+0.3364, +1.1083] | BASE |
| **Candidate K Control** | 37.4603 | 68.7855 | -3.9954 | 23.9171 | 106.6992 | -12.5825 | +0.0000 [+0.0000, +0.0000] | CTRL |
| **Candidate N1** | 37.2669 | 68.4236 | -3.8720 | 23.8760 | 105.7274 | -10.5378 | -0.1934 [-0.4884, +0.1008] | HOLD |
| **Candidate N6** | **36.7856** | **67.1875** | **-2.9862** | **23.7924** | **103.2134** | **-8.8438** | **-0.6746 [-1.0951, -0.2779]** | **PASS** |

### 5.2 Paired Origin-Level Clustered Bootstrap Comparisons (N=364 Origins, 2,000 Draws)

| Comparison ($\Delta = \text{Candidate} - \text{Reference}$) | $\Delta\text{MAE}$ ($\text{W/m}^2$) | 95% Bootstrap CI | Statistical Gate | Significance Status |
|---|---|---|---|---|
| **Cand N6 vs Clean Stage 4 Baseline** | **-4.9804** | **[-6.2515, -3.6851]** | **PASS** | **Decisive baseline superiority ($p < 0.001$)** |
| **Cand N6 vs Candidate F Successor v2** | **-1.4043** | **[-1.8570, -0.9777]** | **PASS** | **Statistically significant improvement ($p < 0.001$)** |
| **Cand N6 vs Candidate K Control** | **-0.6746** | **[-1.0951, -0.2779]** | **PASS** | **Statistically significant improvement ($p < 0.05$)** |
| **Cand N1 vs Candidate K Control** | **-0.1934** | **[-0.4884, +0.1008]** | HOLD | Directional improvement, overlaps zero |
| **Candidate K vs Candidate F Successor v2** | **-0.7297** | **[-1.1083, -0.3364]** | **PASS** | Candidate K retains superiority over Successor |

---

## 6. Gate-by-Gate Evaluation

| Gate | Criterion | Actual 2025 Blind Metric | Result | Interpretation |
|---|---|---|---|---|
| **Gate 1** | Beat Clean Stage 4 baseline on Blind ($\Delta\text{MAE} \le -4.0\text{ W/m}^2$) | $\Delta\text{MAE} = -4.9804\text{ W/m}^2$ (95% CI: $[-6.25, -3.69]$) | **PASS** | Decisive outperformance of the physical baseline on blind data. |
| **Gate 2** | Beat Candidate F Successor v2 on Blind ($p < 0.05$) | $\Delta\text{MAE} = -1.4043\text{ W/m}^2$ (95% CI: $[-1.86, -0.98]$) | **PASS** | Upper CI bound is strictly negative. |
| **Gate 3** | Beat Candidate K Control on Blind ($p < 0.05$) | $\Delta\text{MAE} = -0.6746\text{ W/m}^2$ (95% CI: $[-1.10, -0.28]$) | **PASS** | Confirms Candidate N6's architectural generalization beyond 2024. |
| **Gate 4** | Low-Elevation Stability on Blind ($\text{LE MAE} \le 24.50\text{ W/m}^2$) | $\text{LE MAE} = 23.7924\text{ W/m}^2$ | **PASS** | No low-sun degradation under Arctic conditions. |

---

## 7. Artifact Verification & Hashes

All generated artifacts are frozen in:  
[`stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/)

| File | Size / Shape | SHA-256 Hash |
|---|---|---|
| `candidate_n1_model.joblib` | 84,412 bytes | `7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7` |
| `candidate_n6_model.joblib` | 3,411,510 bytes | `b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197` |
| `validation_predictions.csv` | 4,152 rows × 14 cols | `bf4485283c10a2bcd63112a5c5be10581af6c35ba8f60a3ce201c10f50ea633c` |
| `VALIDATION_RESULTS.json` | 3,334 bytes | `ae5a02d2404b8da404a502b2ea93d50fe18e7352619dcb60a6a0a950c74c4df2` |
| `CANDIDATE_N_MANIFEST.json` | 4,524 bytes | `1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031` |
| `blind_2025_predictions.csv` | 8,736 rows × 16 cols | `3c03e35b1bce2b0b10efc56731c6e641306caa9333b9d5797068f491fb233027` |
| `BLIND_2025_RESULTS.json` | 4,078 bytes | `2d7893cb6fda849019c7dc9d355e0aaa893a0ac148dfb1aecca8b03609abf1a5` |
| `HASHES.sha256` | 619 bytes | (Manifest of the 7 artifact hashes above) |

---

## 8. Limitations & Governance Status

1. **Firewall Integrity:** The 2025 blind evaluation was executed in strict one-shot mode. Models were trained exclusively on 2024-EVEN. Zero hyperparameter tuning or architectural adjustments were made post-blind evaluation.
2. **Model Status:** `winner: null`. While Candidate N6 decisively outperforms all prior models on both 2024 validation and 2025 blind, operational promotion remains subject to project governance review.
3. **Operational 18Z Pre-Cutoff Availability:** The historical availability of MEPS 18Z pressure-level forecasts prior to the 00:00 UTC dispatch cutoff remains an unverified operational question.
