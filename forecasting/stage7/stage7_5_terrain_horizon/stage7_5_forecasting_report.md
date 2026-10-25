# POLARIS STAGE 7.5 — TERRAIN / HORIZON FORECASTING EXPERIMENT REPORT

**Stage:** Stage 7.5  
**Date:** September 12, 2026  
**Status:** COMPLETE — STAGE_7_5_CANDIDATE_ACCEPTED  
**Final Decision:** STAGE 7.5 EVEN-CV PASS — ODD evaluation requires explicit authorization.  
**Official Operational Champion:** Stage 6.6 LWP/IWP Model (FROZEN & UNTOUCHED)  

---

## 1. Executive Summary

Stage 7.5 tested whether adding 4 surface-aware terrain/horizon radiative geometry features (`terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`) derived from Copernicus DEM 30m beyond the frozen 31-feature Stage 6.6 LWP/IWP champion improves 24-hour surface shortwave radiation forecasting accuracy.

Following the locked governance protocol:
1. **Pre-CV Data Audit**: All 347 clean origins ($8,328$ rows) were verified. Range checks passed with zero NaNs, Infs, or duplicates.
2. **Exact Control Reproduction**: Candidate control E0 perfectly reproduced the frozen Stage 6.6 EVEN CV control baseline (MAE $= 38.280605\text{ W/m}^2$, nMAE $= 40.3918\%$, RMSE $= 60.750856\text{ W/m}^2$).
3. **Candidate E1 Evaluation**: Candidate E1 (35 features: 31 Stage 6.6 + 4 terrain features) achieved an aggregate EVEN CV daytime MAE of $37.835137\text{ W/m}^2$ ($\Delta\text{MAE} = -0.445468\text{ W/m}^2$).
4. **Acceptance Gates Audit**: Candidate E1 **PASSED ALL 5 ACCEPTANCE GATES**.

**Final Status:** `STAGE_7_5_CANDIDATE_ACCEPTED`. Stage 6.6 LWP/IWP remains the official frozen operational champion.

---

## 2. Acceptance Gate Audit

| Gate | Description | Threshold | Candidate Result | Status |
|---|---|---|---|---|
| **Gate 1** | Aggregate MAE | $\le 38.0806\text{ W/m}^2$ | $37.8351\text{ W/m}^2$ | **PASS** |
| **Gate 2** | Multi-Fold Consistency | $\ge 4$ of 5 folds improve | 5 of 5 folds | **PASS** |
| **Gate 3** | Fold Degradation Limit | Max degradation $\le +0.15\text{ W/m}^2$ | $-0.2369\text{ W/m}^2$ | **PASS** |
| **Gate 4** | Aggregate nMAE Limit | $\le 40.39\%$ | $38.52\%$ | **PASS** |
| **Gate 5** | Aggregate RMSE Limit | $\le 60.7509\text{ W/m}^2$ | $60.3072\text{ W/m}^2$ | **PASS** |

---

## 3. Five-Fold Breakdown (Daytime MAE in W/m²)

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Fold Improved? |
|---|---|---|---|---|
| **Fold 1** | 49.8174 | 49.0328 | -0.7846 | **YES** |
| **Fold 2** | 71.0775 | 70.8406 | -0.2369 | **YES** |
| **Fold 3** | 41.2620 | 41.0200 | -0.2419 | **YES** |
| **Fold 4** | 26.8042 | 26.1143 | -0.6899 | **YES** |
| **Fold 5** | 2.4420 | 2.1680 | -0.2740 | **YES** |
