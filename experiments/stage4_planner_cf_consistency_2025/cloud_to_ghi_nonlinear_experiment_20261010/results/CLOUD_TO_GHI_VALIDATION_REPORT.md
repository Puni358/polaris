# POLARIS — Cloud-to-GHI Nonlinear Correction Validation Report

**Date:** 2026-10-10T03:45:36.811719+00:00
**Verdict:** `IMPROVED`
**Protocol Governed By:** [experiments/stage4_planner_cf_consistency_2025/cloud_to_ghi_nonlinear_experiment_20261010/CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md](file://experiments/stage4_planner_cf_consistency_2025/cloud_to_ghi_nonlinear_experiment_20261010/CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md)

---

## 1. Executive Summary

- **Model Selected:** `GHI_candidate = clear_sky_GHI * (1 - cloud_fraction)^gamma` with **gamma = 0.25** (fit solely on 2024 training data).
- **Daylight MAE Performance (2025 Non-Blind, N=242 origins):**
  - Baseline MAE: **85.41 W/m²**
  - Candidate MAE: **59.54 W/m²**
  - Candidate − Baseline Delta MAE: **-25.87 W/m²**
  - **95% Confidence Interval (Stationary Bootstrap, B=2000, block len=10d):** `[-36.59, -14.66] W/m²`
- **Success Criterion:** The 95% CI upper bound (-14.66 W/m²) lies entirely below 0.0 W/m².
- **Blind Dataset Protection:** Strict firewall preserved — **123 blind origins** (2025-05-01 to 2025-08-31) were completely excluded; zero outcome observations accessed.

---

## 2. Model Selection (2024 Training Set Only)

- **Training Dataset:** `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` (SHA-256: `8d24dc72e19e3e42...`)
- **Grid Range:** `[0.10, 1.00]`, step `0.01`
- **Baseline (gamma=1.00) Training Daylight MAE:** 96.7531 W/m²
- **Selected Gamma:** **0.25** (Training Daylight MAE: 70.9255 W/m²)

---

## 3. Physical Bound Checks (2025 Non-Blind Validation)

| Physical Check | Value | Threshold / Bound | Status |
|---|---|---|---|
| Baseline Min GHI | 0.0000 W/m² | >= 0.0 | PASS |
| Baseline Negative Violations | 0 | 0 | PASS |
| Baseline > Clearsky Violations | 0 | 0 | PASS |
| Candidate Min GHI | 0.0000 W/m² | >= 0.0 | PASS |
| Candidate Negative Violations | 0 | 0 | PASS |
| Candidate > Clearsky Violations | 0 | 0 | PASS |

---

## 4. Population Validation Metrics (2025 Non-Blind)

### Daylight Hours (solar_elevation > 0 AND clear_sky_GHI > 0)
- **Sample Size:** 1873 daylight hours across 242 origins
- **Baseline:** MAE = 85.4084 W/m², RMSE = 130.2886 W/m², Bias = -77.3717 W/m²
- **Candidate:** MAE = 59.5419 W/m², RMSE = 93.9226 W/m², Bias = -30.5302 W/m²
- **Paired Difference (Candidate − Baseline):**
  - Delta MAE: **-25.8665 W/m²**
  - 95% Percentile Bootstrap CI: **[-36.5880, -14.6586] W/m²**

### All Hours (24-Hour Horizon)
- **Sample Size:** 5808 total hours across 242 origins
- **Baseline:** MAE = 27.9940 W/m², RMSE = 74.0185 W/m², Bias = -25.4023 W/m²
- **Candidate:** MAE = 19.6524 W/m², RMSE = 53.3788 W/m², Bias = -10.2966 W/m²
- **Paired Difference (Candidate − Baseline):**
  - Delta MAE: **-8.3416 W/m²**
  - 95% Percentile Bootstrap CI: **[-14.6132, -3.4557] W/m²**

---

## 5. Subgroup Analysis (Minimum Size Threshold: N >= 20 Origin-Days)

| Subgroup Dimension | Regime | Origin-Days | Daylight Hours | Baseline MAE | Candidate MAE | Delta MAE | Evaluation Status |
|---|---|---|---|---|---|---|---|
| Season | DJF | 90 | 273 | 35.12 | 26.19 | -8.93 | `EVALUATED` |
| Season | MAM | 61 | 823 | 130.53 | 85.60 | -44.92 | `EVALUATED` |
| Season | SON | 91 | 777 | 55.29 | 43.65 | -11.63 | `EVALUATED` |
| Season | JJA | 0 | N/A | N/A | N/A | N/A | `NOT EVALUATED` (Below protocol minimum size of 20 origin-days) |
| Cloud | Regime Overcast | 141 | 1038 | 94.97 | 68.74 | -26.23 | `EVALUATED` |
| Cloud | Regime Partial | 93 | 770 | 77.24 | 49.71 | -27.53 | `EVALUATED` |
| Cloud | Regime Clear | 8 | N/A | N/A | N/A | N/A | `NOT EVALUATED` (Below protocol minimum size of 20 origin-days) |
| Period | Jan-Apr 2025 | 120 | 1096 | 106.76 | 70.81 | -35.96 | `EVALUATED` |
| Period | Sep-Dec 2025 | 122 | 777 | 55.29 | 43.65 | -11.63 | `EVALUATED` |

---

## 6. Reproducibility & Governance Audit

- **Seed:** `20261010`
- **Bootstrap Method:** Stationary Bootstrap (mean block length = 10 days, B = 2000 resamples, unit = origin-day)
- **Confidence Interval Formulation:** Percentile bootstrap interval (chosen per protocol §1)
- **No Production Promotion:** Research-only evaluation artifact. Production forecasting engines (`causal_nwp_physics.py`), EMS controllers, and dispatch routines remain completely unmodified.
- **Protected Blind Population:** 123 blind origins remain fully preserved for future governance decision.
