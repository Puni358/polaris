# POLARIS Results Evidence Index & Governance Registry

**Evaluation Directory:** `presentation/polaris_results_20261013/`  
**Generated At:** 2026-10-13  
**Status:** Authoritative Evidence Index Grounded in Frozen Repository Artifacts  
**Current Governed Status:** `winner: null` (No candidate model or optimizer arm is promoted to production)

---

## 1. Summary of Generated Visual Deliverables

| Deliverable | File Path | Format | Status Tag | Primary Evidence Citation |
|---|---|---|---|---|
| **Graph A** | `graph_a_model_leaderboard.png` | PNG (16:9, 300 DPI) | `VALIDATED / CONTAMINATED TAGGED` | `stage7/stage8/stage8_1_station_tuning_research/CANDIDATE_RESULTS.json` |
| **Graph B** | `graph_b_stage_improvements.png` | PNG (16:9, 300 DPI) | `VALIDATED (FROZEN ODD)` | `stage6_6, stage7_5, stage8_1, stage8_1_corrected odd results` |
| **Graph C** | `graph_c_feature_engineering_impact.png` | PNG (16:9, 300 DPI) | `CONTROLLED / ABLATED` | `stage6_6_lwp_iwp`, `stage7_5_terrain_horizon`, `stage8_1_700hpa_wind` |
| **Graph D** | `graph_d_forecast_performance_horizons.png` | PNG (16:9, 300 DPI) | `VALIDATED (MEASURED)` | `stage8_1_CORRECTED_2025_blind_horizon_metrics.csv` & predictions |
| **Graph E** | `graph_e_error_distribution_regimes.png` | PNG (16:9, 300 DPI) | `VALIDATED (MEASURED)` | `stage8_1_CORRECTED_2025_blind_predictions.csv` & forensics report |
| **Graph F** | `graph_f_optimization_diesel_reduction.png` | PNG (16:9, 300 DPI) | `CAUSAL / RELIABILITY AUDITED` | `experiments/exp_three_arm_2024/results/run_20261011T143130Z/RESULTS.json` |
| **Graph G** | `graph_g_pipeline_governance_evolution.png` | PNG (16:9, 300 DPI) | `PROCESS & GOVERNANCE CONTRACT` | Repository governance records, contracts, and forensic audits |
| **Slides PDF** | `POLARIS_PRESENTATION_SLIDES_20261013.pdf` | Multi-Page PDF | `CONSOLIDATED SLIDEDECK` | Comprehensive collection with per-graph talking points & caveats |

---

## 2. Detailed Mapping by Graph

### Graph A — Model Leaderboard (2025 Blind Evaluation)
- **Target:** Solar downwelling shortwave surface irradiance (`actual_SW_IN`, daytime actual > 0 W/m²).
- **Evaluation Split:** Genuinely blind 2025 holdout calendar year (n = 5,978 daytime hours across 365 origins).
- **Primary Metric:** Daytime Mean Absolute Error (MAE in W/m²); Secondary: Mean Bias (W/m²), RMSE (W/m²).
- **Models Plotted & Measured Results:**
  1. **Stage 8.1 Corrected (Frozen Control):** MAE = 35.9745 W/m² | RMSE = 65.9427 W/m² | Bias = +4.0802 W/m² | Tag: `VALIDATED (CONTROL)`
  2. **Candidate C (Horizon-Specific 4 Buckets):** MAE = 36.3793 W/m² (+0.4048 W/m² vs Control) | Bias = +5.1031 W/m² | 95% CI [-0.03, +0.85] | Tag: `VALIDATED EVAL (FAILED TO IMPROVE)`
  3. **Candidate D (OOF Residual Correction):** MAE = 36.0656 W/m² (+0.0911 W/m² vs Control) | Bias = +1.1394 W/m² | 95% CI [-0.49, +0.66] | Tag: `VALIDATED EVAL (VALIDATION OVERFIT)`
  4. **Candidate E (144-Grid Hyperparameter Optimization):** MAE = 35.7928 W/m² (-0.1817 W/m² vs Control) | Bias = +5.3735 W/m² | 95% CI [-0.66, +0.29] | Tag: `VALIDATED EVAL (NOT STATISTICALLY SIGNIFICANT)`
  5. **Phase 3 Elevation Weighting:** MAE = 35.8626 W/m² (-0.1119 W/m² vs Control) | Bias = +5.1920 W/m² | 95% CI [-0.44, +0.22] | Tag: `VALIDATED EVAL (NOT STATISTICALLY SIGNIFICANT)`
  6. **Candidate F (Solar Elevation × Cloud Fraction Interaction):** Reported MAE = 35.4948 W/m² (-0.4797 W/m² vs Control) | Bias = +3.6959 W/m² | Reported CI [-0.7307, -0.2338] | Tag: `CONTAMINATED / NOT CLEAN`
  7. **Candidate G (Candidate F + Transition Cloud Flag):** Reported MAE = 35.5386 W/m² (-0.4359 W/m² vs Control) | Bias = +3.8765 W/m² | Corrected CI [-0.7685, -0.1258] | Tag: `CONTAMINATED / REDUNDANT WITH F`
  8. **Candidate H (Asymmetric Quantile Loss):** MAE = 36.3222 W/m² (+0.3477 W/m² vs Control) | Bias = -10.3269 W/m² | Corrected CI [-0.6653, +1.3460] | Tag: `VALIDATED EVAL (BIAS OVERSHOOT)`
  9. **Candidate I (Targeted High-Elevation Residual):** MAE = 35.5239 W/m² (-0.4506 W/m² vs Control) | Bias = +4.8951 W/m² | Corrected CI [-1.3535, +0.4329] | Tag: `VALIDATED EVAL (NOT STATISTICALLY SIGNIFICANT)`
  10. **Candidate J (Candidate F + Joint Elevation × Transition Interaction):** Reported MAE = 35.3036 W/m² (-0.6709 W/m² vs Control, -0.1912 W/m² vs F) | Bias = +3.6640 W/m² | Corrected CI (J-F) [-0.3484, -0.0364] | Tag: `CONTAMINATED (INHERITS F TARGET LEAKAGE)`
- **Authoritative Evidence Source:**
  - `stage7/stage8/stage8_1_station_tuning_research/CANDIDATE_RESULTS.json`
  - `stage7/stage8/stage8_1_station_tuning_research/CANDIDATE_COMPARISON_REPORT.md`
  - `stage7/stage8/stage8_1_station_tuning_research/TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md`
- **Governed Status:** `winner: null`. Candidate F and Candidate J cannot be promoted because 2025 ensemble parameters (`k_h`/`w_h`) used to construct 4 derived features were fit on realized 2025 solar targets.

---

### Graph B — Improvement Across Project Stages
- **Target:** Solar downwelling shortwave surface irradiance (`actual_SW_IN`).
- **Evaluation Split:** Standard 2024-ODD held-out benchmark split (173 origins, 2,883 daytime hours).
- **Progression of Measured Metrics:**
  - **Stage 5.2 Control:** Daytime MAE = 39.0848 W/m² | Daytime RMSE = 68.9935 W/m² | Daytime Bias = +1.9347 W/m² (Baseline).
  - **Stage 6.6 (+ LWP / IWP Microphysics):** Daytime MAE = 37.0059 W/m² (ΔMAE = -2.0789 W/m², -5.32% relative reduction; paired bootstrap 95% CI [-2.8098, -1.3448] W/m²) | Daytime RMSE = 65.6717 W/m² (ΔRMSE = -3.3218 W/m²).
  - **Stage 7.5 (+ Terrain Horizons & Shadows):** Daytime MAE = 36.6098 W/m² (ΔMAE = -0.7351 W/m² vs Stage 6.6, -1.97% relative reduction; bootstrap 95% CI [-1.3770, -0.1059] W/m²) | Daytime RMSE = 65.3287 W/m² (ΔRMSE = -0.6542 W/m²).
  - **Stage 8.1 Original (+ 700 hPa Wind Advection):** Daytime MAE = 36.1887 W/m² (ΔMAE = -0.4249 W/m² vs Stage 7.5, -1.16% relative reduction; bootstrap 95% CI [-0.8880, +0.0264] W/m²) | Daytime RMSE = 64.2195 W/m² (ΔRMSE = -1.1276 W/m²).
  - **Stage 8.1 Corrected (Causal Demarcation Freeze):** Daytime MAE = 36.2040 W/m² | Daytime RMSE = 64.5752 W/m² | Daytime Bias = +0.9605 W/m² (Hardened baseline for all 2025 evaluations).
- **Cumulative Validated Gain:** -2.8808 W/m² MAE (-7.37%) and -4.4183 W/m² RMSE (-6.40%) from Stage 5.2 to Stage 8.1.
- **Authoritative Evidence Sources:**
  - `stage6/stage6_6_lwp_iwp/odd_evaluation_results.json`
  - `stage7/stage7_5_terrain_horizon/stage7_5_official_odd_results.json`
  - `stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_results.json`
  - `stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_official_odd_results_2024.json`

---

### Graph C — Feature Engineering Impact & Decomposition
- **Feature Groups & Controlled Comparisons:**
  1. **Cloud Microphysics (MEPS pressure-level LWP & IWP):** Controlled comparison between Stage 5.2 control (29 features) and Stage 6.6 candidate (31 features) on 2024-ODD. Measured impact: -2.08 W/m² MAE (-5.32%), ΔRMSE -3.32 W/m². Status: `VALIDATED PERFORMANCE / REQUISITION CAVEAT` (00Z issuance has ~135 min latency; 18Z proven feasible).
  2. **Topography & Horizon Shadowing (Digital Elevation Model horizon angles & beam shading):** Controlled comparison between Stage 6.6 control (31 features) and Stage 7.5 candidate (35 features) on 2024-ODD. Measured impact: -0.74 W/m² MAE (-1.97%), ΔRMSE -0.65 W/m². Status: `VALIDATED PHYSICS`.
  3. **Upper-Air Steering Wind (700 hPa u and v wind vectors):** Controlled comparison between Stage 7.5 control (35 features) and Stage 8.1 candidate (37 features) on 2024-ODD. Measured impact: -0.42 W/m² MAE (-1.16%), ΔRMSE -1.13 W/m². Status: `VALIDATED DYNAMICS` (Disclosed limitation: horizons 20-24 have inherited NaNs).
  4. **Non-linear Interaction (`solar_elevation × cloud_frac`):** Controlled comparison between Stage 8.1 control (37 features) and Candidate F (38 features). Measured impact: -0.76 W/m² on 2024-ODD validation; reported -0.48 W/m² on 2025 blind. Status: `CONTAMINATED / NOT CLEAN` (2025 target leakage prevents certification of blind gain).
  5. **Transition Cloud Regime Flag (`0.2 ≤ cloud_frac < 0.6`):** Candidate G vs Candidate F. Measured impact: Redundant (+0.04 W/m² worse than F); fails to generalize without bias trade-off. Status: `REDUNDANT`.

---

### Graph D — Forecast Performance Across Horizons and Time
- **Per-Horizon Metrics Source:** `stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_horizon_metrics.csv`
- **Time Series Predictions Source:** `stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv`
- **Key Measured Findings:**
  - Diurnal wave: Error begins low in morning hours (H1 MAE = 3.71 W/m², H2 MAE = 4.31 W/m²).
  - Peak error at solar noon: H12 MAE = 64.08 W/m² (RMSE = 97.23 W/m²), H13 MAE = 62.81 W/m² (RMSE = 96.30 W/m²).
  - Midday bias: Strongest positive overprediction bias occurs at H12 (+17.66 W/m²), H13 (+15.33 W/m²), and H14 (+12.77 W/m²).
  - Night hours: Evaluated with strict night gating (`actual_SW_IN == 0.0` yields exact 0.0 W/m² predictions).
  - **Limitation Disclosed:** `u700`/`v700` have inherited NaNs at horizons 20–24 due to upstream archive lead-time constraints.

---

### Graph E — Error Distribution & Solar Elevation Regime Analysis
- **Residual Distribution:** 5,978 daytime hours on 2025 blind data. Mean bias: +4.08 W/m²; Median: -0.37 W/m²; Std Dev: 65.82 W/m²; 90% coverage interval: [-85.4, +98.7] W/m².
- **Elevation Regime Forensics (Sourced from `CANDIDATE_F_RESULTS.json` & `ERROR_FORENSICS_REPORT.md`):**
  - **Low Elevation (< 10°):** Daytime MAE = 12.4 W/m², Bias = -0.95 W/m² (8.2% of total error).
  - **Mid Elevation (10° to 30°):** Daytime MAE = 38.2 W/m², Bias = +1.82 W/m² (45.9% of total error).
  - **High Elevation (≥ 30°, n = 978):** Daytime MAE = 100.93 W/m², Bias = +13.75 W/m² (45.9% of total error).
  - **Key Mechanistic Insight:** High solar elevation accounts for only 16.4% of daytime hours but generates 45.9% of total absolute error and drives severe systematic overprediction (+13.75 W/m²).

---

### Graph F — POLARIS Optimization and Diesel Reduction (EXP-THREE-ARM-2024)
- **Dataset & Setup:** 2024 SITES Nuolja data, 123 origins, 2,952 simulated operational hours.
- **Execution Evidence:** `experiments/exp_three_arm_2024/results/run_20261011T143130Z/RESULTS.json` (SHA256: `3548db6ac7...`), 14,760 total solves (2,952 per arm × 5 arms, 100% optimal/feasible).
- **Measured Outcomes:**
  1. **PC-Control (Baseline — Governed 6h EBR):** Fuel = 10,368.85 L | Unmet = 1,032.51 kWh (Critical: 329.35 kWh, Noncritical: 703.16 kWh) | R_CF = 99.04% | R_P = 97.70% | Diesel Hours = 657 h (480 starts) | Status: Baseline reference.
  2. **Arm A (Causal NWP + Variant SW-EBR, legacy 1h clock defect):** Fuel = 8,877.04 L (-14.39% saving) | Unmet = 909.62 kWh (Critical: 278.72 kWh) | R_CF = 99.19% | Status: `PROVISIONAL / NOT CLEAN` (Saving inflated by ~3.16 pp due to 1h solar position clock defect; 28/123 origins consume more fuel than control).
  3. **Arm A_FIX (Causal NWP + Variant SW-EBR, clock fixed):** Fuel = 9,204.24 L (-11.23% saving) | Unmet = 1,317.59 kWh (Critical: 484.81 kWh, +47% increase!) | R_CF = 98.58% | Status: `DIAGNOSTIC / FAILED RELIABILITY` (Fails gates S1, S2, S4 point and strict; unmasks reliability flaws).
  4. **Arm B (Noncausal Oracle / Perfect Foresight):** Fuel = 6,758.57 L (-34.82% saving) | Unmet = 975.52 kWh (Critical: 0.0 kWh) | R_CF = 100.0% | Status: `NONCAUSAL DIAGNOSTIC / NOT DEPLOYABLE` (Consumes future realized solar; fails strict paired gate S4 with 75/123 origins performing worse than control).
  5. **Arm C (Calibrated Point + Lower-Bound Quantile Reserve):** Fuel = 7,702.58 L (-25.71% saving) | Unmet = 2,698.16 kWh (Critical: 1,141.30 kWh, 3.5× control!) | R_CF = 96.67% | Status: `REJECTED / FAILED RELIABILITY` (Fails S1, S2, S4 point and strict; severe critical load shedding).
- **Governed Status:** `winner: null` (`RESULTS.json` `winner_note: "No arm in EXP-THREE-ARM-2024 is promotion-eligible; a winner change needs a separate governance decision."`).

---

### Graph G — Pipeline Evolution, Governance Firewalls, and Current Boundary
- **Process Diagram:** Visual summary tracing baseline inputs through feature additions, forensic error discovery, and institutional governance decisions.
- **Audit Findings Enforced:**
  1. MEPS 00Z product has operational publication latency (~135 min), but 18Z causal replacement is feasible.
  2. 2025 ensemble parameters (`k_h`/`w_h`) contain target leakage on 2025 blind data.
  3. Candidate F successor dataset v2 passed independent dataset audit.
  4. Model training, evaluation, and production deployment remain strictly blocked pending governance review.
  5. Governed status `winner: null` is preserved.
