# POLARIS_SOLAR_FORECAST_BRANCH_01 — PHASE 1 GOVERNED BRANCH SPECIFICATION

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `PHASE 1 GOVERNED BRANCH SPECIFICATION`  
**Authorization:** `PHASE 1 BRANCH SPECIFICATION ONLY`  
**Phase 1 Status:** `PASS`  
**Next Governed Step:** `PHASE1_GOVERNANCE_REVIEW`  

---

## 1. Executive Summary & Authorization Boundary

This document establishes the formal, implementation-ready scientific and software specification for the new causal solar forecasting branch `POLARIS_SOLAR_FORECAST_BRANCH_01`.

### Strict Firewall Assertions:
- **STAGE 8.1 FIREWALL**: `STAGE8_1_MODIFIED = NO`, `STAGE8_1_RETRAINED = NO`, `STAGE8_1_REPLACED = NO`. Frozen Stage 8.1 prediction artifacts and feature matrix remain 100% untouched and isolated.
- **CANDIDATE A FIREWALL**: `CANDIDATE_A_IMPLEMENTED = NO`, `CANDIDATE_A_EXECUTED = NO`.
- **EMS FIREWALL**: `EMS_MODIFIED = NO`, `EMS_EXECUTED = NO`. No EnergyOptimizer, DispatchPlan, or DigitalTwin modifications.
- **TRAINING FIREWALL**: `NEW_MODEL_TRAINED = NO`, `NEW_MODEL_INFERRED = NO`, `PHASE2_IMPLEMENTATION_STARTED = NO`. No model fitting or hyperparameter tuning has been performed.

---

## 2. Comprehensive Answers to 23 Phase 1 Specification Questions

1. **Target Definition:**
   - Station-measured solar irradiance ($SW\_IN$) in $\text{W/m}^2$ from the authoritative Nuolja SITES 2024 dataset (`(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv`, column `SW_IN`). Non-negative physical float value.

2. **Temporal Resolution:**
   - $1.0$ hour uniform resolution ($3,600$ seconds).

3. **Supported Forecast Origins:**
   - Every hourly MPC origin $t \in [1..8,784]$ across the entire 2024 calendar year (`2024-01-01T00:00:00Z` to `2024-12-31T23:00:00Z`).

4. **Information Available at Origin $t$:**
   - Observed historical $SW\_IN$ values over $[t-24h, t]$.
   - Deterministic astronomical clear-sky calculations ($clearsky\_ghi$, $solar\_elevation$, $solar\_zenith$, terrain obstruction) computed for target timestamp $t+h$.
   - Calendar encodings (hour of day, month of year).
   - NWP forecast variables from the latest valid issue run $t_{\text{issue}} \le t$.

5. **Timestamping Rule:**
   - For every feature input: $t_{\text{available}} \le t$. Future information ($t' > t$) is strictly forbidden.

6. **Causally Valid Features:**
   - Historical lookback statistics ($SW\_IN$ mean, std, min, max, slope over 1h-24h lookbacks).
   - Astronomical clear-sky irradiance and terrain-shadowed clear-sky GHI.
   - Target calendar variables ($hour\_of\_day$, $month\_of\_year$).
   - AROME NWP features ($fc\_cloud\_cover$, $fc\_temperature\_2m$, $u700$, $v700$) issued at $t_{\text{issue}} \le t$.

7. **Conditional Features:**
   - NWP features are valid iff $t_{\text{issue}} \le t$ with lead-time shift $H_{\text{effective}} = H + (t - t_{\text{issue}})$.

8. **Unavailable Features:**
   - Intra-day NWP issue runs (06:00, 12:00, 18:00 UTC) in the 2024 archive.
   - Real-time satellite EUMETSAT CMIC stream across all origins.
   - Future observations ($t' > t$).

9. **NWP Issue Run Selection Rule:**
   - Deterministically select the latest NWP issue run $t_{\text{issue}}$ satisfying $t_{\text{issue}} \le t$.

10. **Effective NWP Lead-Time Calculation:**
    - $H_{\text{effective}} = H + (t - t_{\text{issue}})$.

11. **Complete 24-Hour Horizon Guarantee:**
    - The model produces 24 distinct output predictions $[SW\_IN(t+1), \dots, SW\_IN(t+24)]$ using direct multi-output regression or 24 horizon-specific estimators ($H1..H24$).

12. **Missing Feature Policy:**
    - **Fail Closed**: If any required feature is missing at origin $t$, raise `ModelGovernanceError`. Zero-filling, forward-filling, synthetic substitution, or future truth leak are strictly forbidden.

13. **Baseline Methods:**
    - **Baseline 1 (Persistence):** $SW\_IN(t+h) = SW\_IN(t)$
    - **Baseline 2 (Diurnal Clear-Sky Persistence):** $SW\_IN(t+h) = \text{clearsky}(t+h) \times \frac{SW\_IN(t)}{\text{clearsky}(t)}$
    - **Baseline 3 (Clear-Sky $k_t$ Persistence):** $k_t(t) = \frac{SW\_IN(t)}{\text{clearsky}(t)}$, $SW\_IN(t+h) = k_t(t) \times \text{clearsky}(t+h)$

14. **Chronological Data Splits:**
    - **Train Period:** `2024-01-01T00:00:00Z` to `2024-08-31T23:00:00Z` (5,856 hours, 66.67%)
    - **Validation Period:** `2024-09-01T00:00:00Z` to `2024-10-31T23:00:00Z` (1,464 hours, 16.67%)
    - **Test Period (Frozen):** `2024-11-01T00:00:00Z` to `2024-12-31T23:00:00Z` (1,464 hours, 16.66%)

15. **Forecasting Metrics:**
    - Overall MAE ($\text{W/m}^2$), RMSE ($\text{W/m}^2$), Bias ($\text{W/m}^2$), Daytime MAE/RMSE, Nighttime MAE/Bias, and Per-Horizon $H1..H24$ MAE/RMSE.

16. **Eligible Model Families:**
    - Ridge Regression, HistGradientBoostingRegressor, XGBoost, LightGBM, and PyTorch Multi-Head Neural Networks.

17. **Required Training Artifacts:**
    - Complete 34-item reproducibility package stored in `artifacts/model_runs/RUN_<id>/`, including serialized fitted model binary, SHA-256 hashes, 4 JSON manifests, training log, prediction CSV/JSON, and independent replay verification report.

18. **Fitted Model Serialization:**
    - `.joblib` format for tabular tree/linear models; `.pt` format for PyTorch neural models.

19. **Model Hashing Protocol:**
    - SHA-256 hash computed directly on serialized model binary bytes and recorded in `model.sha256` and `MODEL_MANIFEST.json`.

20. **Independent Replay Protocol:**
    - Isolated Python process loads model from disk, verifies SHA-256 hash, runs inference on test features, and compares predictions against `predictions.json` within $\text{atol}=1e-5, \text{rtol}=1e-5$.

21. **Criteria for `MODEL_TRAINING_STATUS = REPRODUCIBLE`:**
    - Assigned iff all 34 reproducibility checklist items pass AND independent replay verification succeeds within declared tolerance.

22. **Conditions Blocking EMS Promotion:**
    - `MODEL_TRAINING_STATUS != REPRODUCIBLE`, replay failure, SHA-256 mismatch, missing manifest, unverified causality, or lack of explicit EMS authorization.

23. **Post-Phase 1 Conditional Items:**
    - Empirical evaluation of forecast skill degradation for late intra-day origins ($t=18:00$ UTC) using 18-hour-old NWP issue runs.

---

## 3. Required Final Status Block

```
NEW_FORECASTING_BRANCH =
POLARIS_SOLAR_FORECAST_BRANCH_01

PHASE0_STATUS =
PASS

PHASE1_STATUS =
PASS

STAGE8_1_MODIFIED =
NO

STAGE8_1_RETRAINED =
NO

STAGE8_1_REPLACED =
NO

CANDIDATE_A_IMPLEMENTED =
NO

CANDIDATE_A_EXECUTED =
NO

NEW_MODEL_TRAINED =
NO

NEW_MODEL_INFERRED =
NO

EMS_MODIFIED =
NO

EMS_EXECUTED =
NO

DATA_CAUSALITY =
PASS

NWP_CAUSAL_AVAILABILITY =
CONDITIONAL

24H_ROLLING_FORECAST_FEASIBILITY =
CONDITIONAL

FEATURE_PIPELINE_SPECIFICATION =
COMPLETE

REPRODUCIBILITY_SPECIFICATION =
COMPLETE

MODEL_TRAINING_AUTHORIZATION =
NOT_GRANTED

EMS_INTEGRATION_AUTHORIZATION =
NOT_GRANTED

NEXT_GOVERNED_STEP =
PHASE1_GOVERNANCE_REVIEW
```
