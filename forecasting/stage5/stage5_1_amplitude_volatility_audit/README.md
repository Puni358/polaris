# POLARIS Stage 5.1 — High-Irradiance Amplitude & Recent-Volatility Regime Audit

## Overview
This directory contains the code, data artifacts, plots, and scientific decision summary for **Stage 5.1** of the POLARIS forecasting research project.

Stage 5.1 investigates whether the remaining Stage 4 error (particularly hard errors where $|error| > 150$ W/m², accounting for ~36% of total daytime absolute error) is primarily:
1. An **amplitude-calibration problem** (systematic compression at high irradiance $>500$ W/m²), OR
2. A **regime/transition problem** predictable via causal recent-volatility features.

---

## Executive Summary & Decision

- **Baseline Verification**: Stage 4 official champion predictions reproduced exactly on 173 ODD test origins (Daytime MAE = 43.4508 W/m², nMAE = 33.70%, RMSE = 74.8530 W/m², Bias = -1.9716 W/m²).
- **Amplitude Calibration (Part C)**: 5 candidate amplitude calibration models (Global Affine, Piecewise Affine, Isotonic Regression, Horizon-Aware Affine, Solar-Aware Calibration) were fitted on EVEN origins ONLY. **None improved overall daytime MAE on EVEN CV** compared to Stage 4 Baseline (37.5547 W/m²). C2 Piecewise Affine was the best calibration candidate on EVEN CV (40.7162 W/m², $\Delta \text{MAE} = +3.1614$ W/m²), while C1 Global Affine yielded 42.4645 W/m² ($\Delta \text{MAE} = +4.9098$ W/m²).
- **Volatility Predictability (Parts D & E)**: Causal 24h SW_IN volatility features (`std_6h`, `abs_change_6h`, `kt_std`, `slope`) strongly predict hard-error risk ($|error| > 150$ W/m²) with **CV ROC-AUC = 0.7598** and **PR-AUC = 0.2766** (vs baseline prevalence of 0.0650).
- **Volatility Correction (Part F)**: Simple linear volatility-based additive corrections failed to improve overall daytime MAE (EVEN CV $\Delta \text{MAE} = +16.9216$ W/m²).
- **Final ODD Test Evaluation (Part H)**: Evaluated frozen models on 173 ODD origins. Global Affine (C1) yielded ODD Daytime MAE = 44.9402 W/m² ($\Delta \text{MAE} = +1.4894$ W/m²). 10,000 origin-level paired bootstrap resamples yielded mean $\Delta \text{MAE} = +1.4892$ W/m² (95% CI: [+1.0977, +1.8794] W/m²).
- **Final Classification**: **B — Useful diagnostic signal but no forecast improvement**

---

## Scientific Answer & Next Experiment

> **Is Stage 4 primarily suffering from a correctable calibration problem, or from missing regime/transition information that requires a fundamentally different forecasting model?**

**Answer**: The evidence is consistent with a **regime/transition problem** rather than a static amplitude-calibration problem. Post-hoc amplitude calibration does not improve overall daytime MAE across horizons and regimes. Volatility features carry strong diagnostic signal identifying when hard errors occur (ROC-AUC ~0.76), indicating that hard errors coincide with volatile transition regimes, but simple linear corrections cannot resolve these transitions.

**Next Experiment**: Proceed to **Stage 5.2 — Specialist Hard-Weather / Regime-Transition Model**, focusing on non-linear regime-aware architecture or mixture-of-experts for volatile weather transitions.

---

## Generated Artifacts

### CSV Data Files
- [`stage4_baseline_verification.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/stage4_baseline_verification.csv) — Stage 4 baseline reproduction verification.
- [`irradiance_bin_forensics.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/irradiance_bin_forensics.csv) — Performance metrics binned by Stage 4 forecast magnitude.
- [`amplitude_calibration_cv.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/amplitude_calibration_cv.csv) — Forward-chaining CV metrics on EVEN origins for candidate amplitude calibrations.
- [`amplitude_calibration_test.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/amplitude_calibration_test.csv) — Frozen ODD test evaluation for amplitude calibration models.
- [`volatility_features.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/volatility_features.csv) — Metadata and statistics of pre-forecast causal volatility features.
- [`hard_error_prediction_cv.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/hard_error_prediction_cv.csv) — Hard-error classification and regression predictability results.
- [`volatility_correction_cv.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/volatility_correction_cv.csv) — CV results for simple volatility-aware forecast corrections.
- [`stage5_1_test_results.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/stage5_1_test_results.csv) — Final frozen ODD test results and 10,000 bootstrap CI.
- [`per_horizon_results.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/per_horizon_results.csv) — Performance breakdown by forecast horizon group.
- [`regime_results.csv`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/regime_results.csv) — Performance breakdown by solar elevation and actual irradiance regimes.

### Plots
- [`01_actual_vs_stage4_prediction.png`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/01_actual_vs_stage4_prediction.png)
- [`02_amplitude_bias_by_forecast_bin.png`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/02_amplitude_bias_by_forecast_bin.png)
- [`03_high_irradiance_calibration.png`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/03_high_irradiance_calibration.png)
- [`04_volatility_vs_absolute_error.png`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/04_volatility_vs_absolute_error.png)
- [`05_hard_error_probability.png`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/05_hard_error_probability.png)
- [`06_horizon_performance.png`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/06_horizon_performance.png)
- [`07_stage4_vs_stage5_1.png`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/07_stage4_vs_stage5_1.png)

### Reports
- [`README.md`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/README.md) — Comprehensive documentation.
- [`final_summary.txt`](file:///home/punith-bs/01polaris (Copy)/stage5/stage5_1_amplitude_volatility_audit/final_summary.txt) — Executive decision report.
