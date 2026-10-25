# POLARIS CORRECTION & SAME-FORECASTER CALIBRATION FEASIBILITY AUDIT
## Experiment: EXP-CONFORMAL-TRAJECTORY-OFFLINE

**Date:** 2026-10-05  
**Audit Status:** COMPLETE (REVISED PER AI INDEPENDENT AUDIT)  
**Overall Experiment Status:** HISTORICAL / NOT QUALIFIED FOR STAGE 8.1  
**Feasibility Verdict:** SAME-FORECASTER CALIBRATION BLOCKED — FEASIBILITY NOT ESTABLISHED  

---

## 1. Executive Summary & Audit Context

An independent forensic review of the offline validation experiment `EXP-CONFORMAL-TRAJECTORY-OFFLINE` and its initial correction audit identified both fundamental methodological issues with the experiment itself and numerical/factual errors in the initial reporting:

1. **Forecaster Mismatch in Original Experiment:**
   - **2022 Calibration Split:** Forecast errors were derived from historical **Candidate F** point forecasts.
   - **2023 Reference Split:** Forecast errors were also derived from historical **Candidate F** point forecasts.
   - **2025 Evaluation Split:** Forecast errors were derived from the frozen **corrected Stage 8.1** model (`stage8_1_CORRECTED_candidate_37feature_model.joblib`).
   - **Conclusion:** Candidate F and corrected Stage 8.1 are distinct forecasters with different error distributions. The observed **99.73% simultaneous trajectory coverage** in 2025 is **over-coverage under forecaster mismatch / distribution transfer**, NOT evidence that Stage 8.1 uncertainty is calibrated.

2. **Correction of Initial AGY Audit Errors:**
   - Authoritative coverage figures from [`COVERAGE.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/experiments/EXP_CONFORMAL_TRAJECTORY_OFFLINE/COVERAGE.csv) have been restored; previous erroneous claims (such as claiming 2023 coverage was 97.26% or inventing an unphysical $q_{\mathrm{calib}} = 296.86\text{ Wh}$) have been completely excised.
   - The authoritative 2022 conformal calibration multiplier is $\hat{q}_{\mathrm{cal}} = 3.4674$ (dimensionless scaling multiplier for nominal 90%, rank $k=330$), not an energy quantity.
   - The Stage 8.1 feature contract has been aligned strictly with the authoritative [`STAGE8_1_CORRECTED_MODEL_MANIFEST.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_corrected_2025/model_artifact/STAGE8_1_CORRECTED_MODEL_MANIFEST.json) (`feature_order_37`).
   - The feasibility status of reconstructing historical same-forecaster calibration data is updated from "possible but blocked" to **`SAME-FORECASTER CALIBRATION BLOCKED — FEASIBILITY NOT ESTABLISHED`**.

---

## 2. Authoritative Experimental Numerical Reconciliation

The authoritative source of numerical coverage in this experiment is [`COVERAGE.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/experiments/EXP_CONFORMAL_TRAJECTORY_OFFLINE/COVERAGE.csv). The table below reflects the exact data recorded by the execution script:

### Simultaneous Trajectory Coverage ($\alpha = 0.10$, Nominal 90%)

| Year | Split Role | Forecaster Evaluated | Origins ($N$) | Method A: AR Variance | Method B: Empirical Quantile (2022) | Method C: Split-Conformal Trajectory | 95% Wilson CI (Method C) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2020** | Train | Candidate F | 366 | 44.54% | 64.48% | 85.79% | [81.84%, 89.00%] |
| **2021** | Train | Candidate F | 365 | 41.37% | 59.73% | 88.22% | [84.51%, 91.14%] |
| **2022** | Calibration | Candidate F | 365 | 41.92% | 62.19% | 90.41% | [86.96%, 93.02%] |
| **2023** | Prior Evidence | Candidate F | 273 | 27.84% | 43.96% | 82.05% | [77.06%, 86.15%] |
| **2025** | Primary Blind | Stage 8.1 Corrected | 364 | 58.79% | 71.15% | 99.73% | [98.46%, 99.95%] |

*(Note: There is no 2024 evaluation row in this experiment. All 2024 data was excluded from offline evaluation).*

### Key Numerical Corrections
1. **Method C 2023 Simultaneous Coverage:** Authoritative value is **82.05%** (224 / 273 origins). The prior claim of 97.26% was incorrect and has been removed.
2. **Conformal Multiplier:** The 2022 calibration yielded a dimensionless trajectory multiplier $\hat{q}_{\mathrm{cal}} = 3.4674$ at $\alpha = 0.10$ ($k = \lceil 366 \times 0.90 \rceil = 330$). No Wh value was computed or reported for $\hat{q}_{\mathrm{cal}}$.
3. **Method A Range:** Actual simultaneous coverage across all evaluated years spans **27.84% to 58.79%** (the narrative claim of "49.8% to 65.0%" in `RESULTS.md` was erroneous).
4. **Method B Range:** Actual simultaneous coverage spans **43.96% to 71.15%** (the narrative claim of "80.5% to 83.2%" in `RESULTS.md` was erroneous).

---

## 3. Physical Inverter Clipping Audit (60 kW)

The physical inverter clipping operator is defined as:
$$P_{\mathrm{pv}} = \min(60{,}000\text{ W}, 51 \times \text{GHI})$$

- **Saturation Threshold:** $\text{GHI}_{\mathrm{clip}} = 60{,}000 / 51 \approx 1{,}176.47\text{ W/m}^2$.
- **Observed Data Bounds (2020–2025):**
  - Maximum actual irradiance recorded: $910.17\text{ W/m}^2$.
  - Maximum forecast irradiance recorded: $710.15\text{ W/m}^2$.
- **Finding:** At no timestep does either actual or forecast irradiance reach $1{,}176.47\text{ W/m}^2$.
- **Status:** **`NO MATERIAL EFFECT IN CURRENT DATA`**.

---

## 4. Conformal Calibration & Evaluation Split Status

The evaluation splits used in the experiment have the following governance status:

- **2022:** `Candidate F calibration set`. Calibrates a multiplier against historical Candidate F error trajectories.
- **2023:** `Candidate F prior/reference evaluation; not a fresh blind calibration test`. Serves only as reference performance under Candidate F.
- **2025:** `Corrected Stage 8.1 forecast evaluation; not eligible for uncertainty calibration because the calibration forecaster differs and the forecast period was already exposed during Stage 8.1 freeze evaluation`.
- **Verdict on 99.73% Coverage:** **`OVER-COVERAGE UNDER FORECASTER MISMATCH`**. It reflects transferring a high-variance Candidate F uncertainty multiplier to a lower-variance Stage 8.1 prediction error distribution, resulting in excessive conservatism (mean width 32,520 Wh vs empirical 18,305 Wh).

---

## 5. Authoritative Stage 8.1 Feature Contract (`feature_order_37`)

Per [`STAGE8_1_CORRECTED_MODEL_MANIFEST.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_corrected_2025/model_artifact/STAGE8_1_CORRECTED_MODEL_MANIFEST.json), the authoritative 37 features of the frozen Stage 8.1 model are strictly:

1. `horizon_hour`
2. `month`
3. `hour`
4. `solar_elevation`
5. `solar_zenith`
6. `clearsky_ghi`
7. `fc_cloud_cover`
8. `fc_temperature_2m`
9. `fc_relative_humidity_2m`
10. `cloud_frac`
11. `pred_stage3b_cloud_nwp`
12. `phys_pred_fold`
13. `pred_stage4_fold`
14. `disagreement_fold`
15. `ctx_std_3h`
16. `ctx_std_6h`
17. `ctx_std_12h`
18. `ctx_std_24h`
19. `ctx_abs_change_1h`
20. `ctx_abs_change_3h`
21. `ctx_abs_change_6h`
22. `ctx_max_diff_6h`
23. `ctx_mean_diff_6h`
24. `ctx_slope_6h`
25. `ctx_kt_std_6h`
26. `ctx_last_obs`
27. `ctx_mean_24h`
28. `ctx_max_24h`
29. `lwp_latest`
30. `iwp_latest`
31. `lwp_x_cloud`
32. `terrain_horizon_elevation_deg`
33. `terrain_elevation_margin_deg`
34. `terrain_solar_obstruction_flag`
35. `clearsky_ghi_terrain_adjusted`
36. `u700`
37. `v700`

*(Features such as `solar_azimuth`, `clearsky_dni`, `total_cloud_cover`, `hour_sin`, `day_of_year_sin`, and `ctx_ghi_lag1` are NOT in the Stage 8.1 contract and must not be described as such).*

---

## 6. Calibration Feasibility Audit Across Candidate Periods

| Period | Usable Origins | Stage 8.1 Exposure History | Feature Pipeline Availability | Eligibility & Feasibility Status |
| :---: | :---: | :---: | :---: | :---: |
| **2020–2023** | 1,369 | None (Out-of-sample) | **MISSING** (Historical dataset only contains Candidate F inputs) | **BLOCKED — FEASIBILITY NOT ESTABLISHED** |
| **2024 EVEN** | 174 | Model Training Set ($n=2,885$ daytime rows) | Available in frozen artifacts | **INELIGIBLE — TRAINING SET** (Circular leakage) |
| **2024 ODD** | 173 | Candidate Selection Set ($n=2,883$ daytime rows) | Available in frozen artifacts | **INELIGIBLE — DEVELOPMENT EXPOSURE** (Selection bias) |
| **2025** | 364 | Blind Freeze Benchmark ($n=8,736$ rows) | Available in frozen artifacts | **INELIGIBLE — TEST SET / FREEZE EXPOSURE** (Holdout reuse) |

### Scientific Status of Historical Reconstruction:
**`FEASIBILITY NOT ESTABLISHED`**  
The claim that historical reconstruction of the 37-feature matrix for 2020–2023 is merely "blocked waiting for implementation" is rejected. We have not demonstrated that an uncorrupted causal replay can definitely be executed. Specifically, the following dependencies remain unresolved:
- Historical `pred_stage3b_cloud_nwp` causal pipeline availability across 2020–2023.
- Historical `pred_stage4_fold` and dependent `disagreement_fold` generation.
- Causal issuance and as-of timestamp provenance for rolling context features (`ctx_*`).
- Corrected historical $u_{700}$ and $v_{700}$ upper-air wind extraction pipeline provenance.
- Historical liquid and ice water path (`lwp_latest`, `iwp_latest`) causal as-of provenance.

Until these dependencies are empirically demonstrated and audited, same-forecaster calibration feasibility remains **NOT ESTABLISHED**.

---

## 7. Status of Proposed Future Evaluation Splits

The previously suggested split (`2020–2022 calibration → 2023 validation → 2025 evaluation`) is **`PROPOSED ONLY — NOT AUTHORIZED`** and **`REQUIRES FUTURE PROVENANCE/ELIGIBILITY REVIEW`**. No experimental split may be authorized until a verified same-forecaster dataset is demonstrated.

---

## 8. Requirements for Future Uncertainty Evaluation Protocols

A scientifically defensible uncertainty envelope evaluation cannot rely solely on a one-sided coverage threshold ($\ge 87\%$). Future preregistrations must enforce:
1. **A target coverage requirement** (nominal $1 - \alpha$).
2. **An explicit upper bound against excessive over-coverage** (to prevent unconstrained, economically useless conservatism).
3. **An envelope width and sharpness criterion** (bounding Wh reserve requirements).
*Exact numerical thresholds must be formally preregistered prior to any future experiment.*

---

## 9. Governance & Architectural Freeze

- **GAP19 Status:** `UNCHANGED`
- **EMS Status:** `UNCHANGED`
- **Stage 8.1 Frozen Model Artifact:** `UNCHANGED`
- **Production Configuration:** `UNCHANGED`
- **Risk-to-Reserve Experiments:** `NONE AUTHORIZED`
- **Closed-Loop Uncertainty Experiments:** `NONE AUTHORIZED`
