# POLARIS_SOLAR_FORECAST_BRANCH_01 — PHASE 0 DATA & CAUSALITY AUDIT REPORT

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `PHASE 0 — READ-ONLY DATA + CAUSALITY RECONNAISSANCE`  
**Authorization:** `PHASE 0 ONLY`  
**Audit Status:** `PASS / CONDITIONAL`  

---

## 1. Governance Purpose & Boundary Confirmation

This report documents the Phase 0 read-only reconnaissance for the new, independently governed solar forecasting branch `POLARIS_SOLAR_FORECAST_BRANCH_01`.

### Authoritative Frozen Stage 8.1 Boundary
The Stage 8.1 champion remains strictly frozen and immutable:
- **Prediction Artifact:** `stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv`
  - Expected & Actual SHA-256: `213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707` (**MATCH: TRUE**)
- **Feature Matrix:** `stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv`
  - Expected & Actual SHA-256: `e7b304186eef6c7e6135ba7a9aa9d20a4d2f32eeb9b65085ef8e10e34ea0b541` (**MATCH: TRUE**)

---

## 2. Phase 0 Audit Answers (19 Required Questions)

1. **Exact Data Supporting Hourly Causal Forecasting:**
   - Nuolja SITES 2024 5-var hourly dataset (`(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv`), containing 8,784 hourly observations of $SW\_IN$, $TA$, $RH$, $TS$, and $PRECIP$.
   - Astronomical Clear-Sky & Terrain Decomposition dataset (`data/POLARIS_v0_1_clearsky_decomposition.csv`), containing 8,784 hourly calculations of theoretical $clearsky\_ghi$, $solar\_elevation$, $solar\_zenith$, and terrain-shadowed $clearsky\_ghi\_terrain\_adjusted$.
   - Historical lookback observations up to forecast origin $t$.

2. **Maximum Historical Coverage:**
   - Full calendar year 2024: `2024-01-01T00:00:00Z` to `2024-12-31T23:00:00Z` (8,784 total hours, 100.0% coverage, 0 missing hours).

3. **Hourly Resolution:**
   - $1.0$ hour uniform resolution.

4. **NWP Forecast Data:**
   - MEPS/AROME 21x21 spatial grid forecasts (`arome_cache_21x21/`) covering 700hPa wind components ($u700$, $v700$), total cloud cover (`fc_cloud_cover`), 2m temperature (`fc_temperature_2m`), 2m relative humidity (`fc_relative_humidity_2m`), liquid water path (`lwp_latest`), and ice water path (`iwp_latest`).

5. **NWP Issue Times:**
   - Issue times in 2024 archive occur once daily at `00:00 UTC` across 347 origin days.

6. **NWP Forecast Lead Times:**
   - Lead times span 1 to 24 hours ($H1$ to $H24$).

7. **NWP Causal Validity:**
   - **CONDITIONAL**: An NWP input is causally valid at MPC origin $t$ if and only if $t_{issue} \le t$. For origin $t=00:00$ UTC, the 00:00 UTC NWP issue run is directly valid for $H1..H24$. For non-00:00 UTC origins (e.g. $t=06:00$ UTC), NWP features must use the 00:00 UTC issue run with lead-time shift $H_{effective} = H + (t - t_{issue})$.

8. **Satellite Data:**
   - EUMETSAT CMIC cloud microphysics product (archived in Stage 8.14C for 347 origins).

9. **Satellite Resolution:**
   - 15-minute temporal / ~3km spatial resolution.

10. **Causally Constructible Features:**
    - Causal lookback statistics over $[t-k, t]$ for $k \in \{1h, 3h, 6h, 12h, 24h\}$ ($SW\_IN$ mean, std, slope, min, max, clearness index $k_t$).
    - Astronomical clear-sky GHI, terrain obstruction, solar elevation, solar zenith.
    - Calendar encodings (month, hour of day, day of year).
    - NWP forecast variables from valid issue run $t_{issue} \le t$.

11. **Rejected Candidate Features:**
    - Any future observation ($t' > t$).
    - NWP forecast runs issued at $t_{issue} > t$.
    - Unaligned satellite frames lacking verifiable issue timestamps.
    - Zero-padded, forward-filled, or synthetic future vectors.

12. **Missing Resources:**
    - Intra-day NWP issue runs (06:00, 12:00, 18:00 UTC) for 2024.
    - Continuous real-time EUMETSAT CMIC stream for all 8,784 hourly origins.

13. **Feasible Forecast Architectures:**
    - **Architecture A (Causal Baseline Engine):** Persistence / Diurnal Clear-Sky Persistence / Clear-Sky $k_t$ Persistence.
    - **Architecture B (Causal Tabular ML):** Ridge / HistGradientBoosting / XGBoost / LightGBM trained on causal lookback + astronomical + lead-shifted NWP features.
    - **Architecture C (Causal Multi-Head Neural Network):** PyTorch MLP / GRU with 24 distinct output heads for $H1..H24$.

14. **Recommended Train / Validation / Test Split:**
    - **Chronological Split Across 2024:**
      - **Train Set:** `2024-01-01T00:00:00Z` to `2024-08-31T23:00:00Z` (60% ~5,856 hours)
      - **Validation Set:** `2024-09-01T00:00:00Z` to `2024-10-31T23:00:00Z` (20% ~1,464 hours)
      - **Final Test Set (Frozen):** `2024-11-01T00:00:00Z` to `2024-12-31T23:00:00Z` (20% ~1,464 hours)

15. **Model Reproducibility Requirements:**
    - Immutable run directory (`artifacts/model_runs/<run_id>/`).
    - Serialized fitted model binary (`model.joblib` or `model.pt`) with SHA-256 hash.
    - Four machine-readable JSON manifests (`MODEL_MANIFEST.json`, `DATA_MANIFEST.json`, `FEATURE_MANIFEST.json`, `ENVIRONMENT.json`).
    - Human- and machine-readable `REPRODUCTION_INSTRUCTIONS.md`.
    - Mandatory post-training independent replay verification matching original outputs within predeclared tolerance.

16. **24-Hour Rolling Forecast Causal Feasibility:**
    - **YES (CONDITIONAL)**: Feasible at every hourly origin $t \in [1, 8784]$ using strictly causal inputs (lookback, clear-sky, calendar, and lead-shifted NWP).

17. **Exact Blockers:**
    - Sparse 00:00 UTC NWP issue frequency requires lead-time adjustment for intra-day origins ($t \in \{01:00..23:00\}$).

18. **Support for Phase 1 Branch Specification:**
    - **YES (PASS / CONDITIONAL)**. Data and causality reconnaissance justify advancing to Phase 1.

19. **Unverified Assumptions:**
    - Forecast accuracy impact of using 18-hour-old NWP issue runs for late afternoon origins ($t=18:00$ UTC).

---

## 3. Final Required Status Block

```
NEW_FORECASTING_BRANCH =
POLARIS_SOLAR_FORECAST_BRANCH_01

STAGE8_1_MODIFIED =
NO

STAGE8_1_RETRAINED =
NO

STAGE8_1_REPLACED =
NO

NEW_MODEL_TRAINED =
NO

NEW_MODEL_INFERRED =
NO

EMS_MODIFIED =
NO

EMS_EXECUTED =
NO

CANDIDATE_A_IMPLEMENTED =
NO

CANDIDATE_A_EXECUTED =
NO

DATA_CAUSALITY =
PASS

NWP_CAUSAL_AVAILABILITY =
CONDITIONAL

FEATURE_PIPELINE_FEASIBILITY =
PASS

24H_ROLLING_FORECAST_FEASIBILITY =
CONDITIONAL

MODEL_REPRODUCIBILITY_REQUIREMENT =
ESTABLISHED

PHASE0_STATUS =
PASS

NEXT_GOVERNED_STEP =
PHASE0_GOVERNANCE_REVIEW
```
