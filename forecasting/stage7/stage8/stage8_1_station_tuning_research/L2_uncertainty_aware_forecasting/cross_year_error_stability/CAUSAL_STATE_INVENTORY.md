# Causal State & Conditioning Feature Inventory

**Audit Branch**: POLARIS — Forecast-Error Cross-Year Conditional Stability Audit  
**Dataset**: `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`  
**Dataset SHA256**: `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab`  
**Audit Date**: 2026-10-05  

## Executive Summary

A strict causal audit of all 22 columns present in the historical Candidate F residual dataset was conducted to determine eligibility for uncertainty conditioning. To ensure strict non-anticipative operation in production EMS and prevent data leakage, variables are partitioned into five formal governance categories:

- **Class A: Causal / Available at Issuance (14 variables)**: Strictly available at forecast issuance time (00:00 UTC / 18Z NWP cycle) or computed via deterministic celestial geometry. Approved for causal conditioning.
- **Class B: Causal but Release Latency Unresolved (3 variables)**: Derived from ground station sensor telemetry (`ctx_last_obs`, `ctx_std_3h`, `ctx_mean_24h`). While physically preceding the forecast horizon, their real-time telemetry ingestion SLAs and transmission reliability are unverified. **Quarantined from uncertainty models** until an operational data SLA audit is completed.
- **Class C: Noncausal / Future Information (5 variables)**: Realized observations (`actual`), residuals (`residual`, `forecast_error`), and loss functions (`absolute_error`, `squared_error`). **Strictly forbidden** as inputs to any predictive or conditioning model.
- **Class D: Static / Deterministic (0 variables)**: Fixed site constants (e.g. latitude/longitude, panel tilt/capacity) are implicit in Candidate F station tuning.
- **Class E: Unknown (0 variables)**: No unclassified columns exist.

---

## Complete Column Inventory & Governance Classification

| Variable Name | Data Type | Physical Domain | Causal Class | Availability Timing | Operational Usability | Governance Notes |
|:---|:---|:---|:---:|:---|:---|:---|
| `forecast_start` | string (ISO8601) | Temporal origin | **A** | At forecast issuance (18Z / 00:00 UTC) | Valid metadata for origin grouping | Forecast issuance origin timestamp |
| `timestamp` | string (ISO8601) | Temporal target | **A** | Deterministic astronomical time | Valid for diurnal/temporal index | Target valid timestamp |
| `horizon_hour` | integer (6..24) | [6, 24] | **A** | Known at issuance | Valid lead time variable | Lead time from NWP model initialization (18Z) |
| `year` | integer (2020..2023) | [2020, 2023] | **A** | Known at issuance | Split partitioning only; NOT a causal dispatch feature | Calendar year |
| `month` | integer (1..12) | [1, 12] | **A** | Known at issuance | Valid for seasonal categorization | Calendar month |
| `day_of_year` | integer (1..366) | [1, 366] | **A** | Known at issuance | Valid for solar geometry indexing | Day of calendar year |
| `hour` | integer (0..18) | [0, 18] | **A** | Deterministic astronomical time | Valid diurnal state variable | Target hour of day (UTC) |
| `prediction` | float (W/m^2) | [0, 750] | **A** | Output of Candidate F model at issuance | Valid causal state variable | Candidate F GHI solar forecast |
| `solar_elevation` | float (degrees) | [-45, 45] | **A** | Deterministic astronomical calculation | Valid causal state variable | Solar elevation angle above horizon at target location |
| `clearsky_ghi` | float (W/m^2) | [0, 720] | **A** | Deterministic astronomical clear-sky calculation | Valid causal normalization variable | Clear-sky model geometric radiation potential |
| `fc_cloud_cover` | float (%) | [0, 100] | **A** | MEPS NWP model output available at issuance | Valid causal forecast regime variable | NWP forecasted total cloud cover |
| `cloud_frac` | float (0..1) | [0.0, 1.0] | **A** | MEPS NWP output at issuance | Valid causal forecast regime variable | Normalized cloud fraction (fc_cloud_cover / 100) |
| `elevation_x_cloud_frac` | float | [-45, 45] | **A** | Product of causal inputs available at issuance | Valid interaction state variable | Candidate F tree feature |
| `ctx_last_obs` | float (W/m^2) | [0, 38] | **B** | Station sensor measurement prior to 00:00 UTC | UNRESOLVED: sensor latency/dropout not audited | Last observed GHI at station; transmission SLA unresolved |
| `ctx_std_3h` | float (W/m^2) | [0, 11] | **B** | 3-hour pre-issuance sensor history | UNRESOLVED: transmission SLA unresolved | Pre-issuance observation volatility |
| `ctx_mean_24h` | float (W/m^2) | [0, 325] | **B** | 24-hour pre-issuance sensor history | UNRESOLVED: transmission SLA unresolved | 24-hour pre-issuance mean solar observation |
| `split` | string | TRAIN/VAL/BLIND | **A** | Static experimental protocol metadata | Strictly partition definition only | Dataset fold governance label |
| `actual` | float (W/m^2) | [0, 800] | **C** | Realized at target timestamp (future) | TARGET ONLY - strictly forbidden as input | Ground-truth solar sensor observation |
| `residual` | float (W/m^2) | [-600, 600] | **C** | Realized in future (prediction - actual) | TARGET ONLY - strictly forbidden as input | Candidate F forecast error e_t |
| `forecast_error` | float (W/m^2) | [-600, 600] | **C** | Realized in future | TARGET ONLY - strictly forbidden as input | Duplicate of residual |
| `absolute_error` | float (W/m^2) | [0, 600] | **C** | Realized in future | TARGET ONLY - strictly forbidden as input | Absolute magnitude |e_t| |
| `squared_error` | float ((W/m^2)^2) | [0, 360000] | **C** | Realized in future | TARGET ONLY - strictly forbidden as input | Squared error e_t^2 |

---

## Detailed Category Analysis

### 1. Class A: Causal Forecast-State Features (Approved for Conditioning)
1. **Solar Geometry (`solar_elevation`, `hour`, `day_of_year`, `timestamp`)**: Computed purely from astronomical celestial mechanics given site latitude and longitude. Perfectly deterministic and available indefinitely into the future. Crucially dictates the theoretical upper bound on solar generation.
2. **Clear-Sky Normalization (`clearsky_ghi`)**: Ineichen-Perez or Haurwitz clear-sky theoretical irradiance under zero cloud cover. Deterministic geometric potential.
3. **NWP Weather Forecast State (`fc_cloud_cover`, `cloud_frac`)**: Numerical weather predictions produced by the operational MEPS NWP model run (18Z cycle), completely available before the 00:00 UTC forecast issuance.
4. **Model Interaction Terms (`elevation_x_cloud_frac`, `prediction`)**: Candidate F model output and engineered features derived strictly from Class A inputs.
5. **Horizon Lead Time (`horizon_hour`)**: Discrete lead time step ($k \in [6..24]$). Known deterministically at planning time.

### 2. Class B: Telemetry Context Features (Quarantined)
- **`ctx_last_obs`**: Last recorded ground-station GHI observation prior to 00:00 UTC.
- **`ctx_std_3h`**: 3-hour pre-issuance rolling standard deviation of ground station sensor readings.
- **`ctx_mean_24h`**: 24-hour pre-issuance rolling mean of ground station sensor readings.

> **Governance Finding**: In historical retrospective datasets, context features are retroactively aligned without simulating realistic network packet drops, sensor maintenance lockouts, or SCADA ingestion delays. Using them in real-time uncertainty conditioning risks silent fallback failures during telemetry loss. They remain **quarantined** until latency SLAs are formally audited.

### 3. Class C: Realized Targets & Errors (Strictly Forbidden as Conditioning Inputs)
- **`actual`**, **`residual`**, **`forecast_error`**, **`absolute_error`**, **`squared_error`**.
- Any usage of these variables during regime selection or envelope lookup represents catastrophic noncausal data leakage.

---

## Approved Candidate Regimes for Stability Audit
Based strictly on Class A variables, the following physically interpretable candidate conditioning schemes were approved and tested:
1. **Solar Elevation Angle**: `Low_0_15` ($0^\circ \le \alpha < 15^\circ$), `Mid_15_30` ($15^\circ \le \alpha < 30^\circ$), `High_gt_30` ($\alpha \ge 30^\circ$).
2. **Forecast Cloud Fraction**: `Clear` ($c < 0.20$), `Partial` ($0.20 \le c \le 0.80$), `Overcast` ($c > 0.80$).
3. **Forecast Clearness Index ($\hat{k}_t = \hat{y}_t / \text{cs}_t$)**: `Low_kt_lt_0.3`, `Mid_kt_0.3_0.7`, `High_kt_gt_0.7`.
4. **Clear-Sky Irradiance Level**: `Low_cs_0_150` ($0\text{--}150\text{ W/m}^2$), `Mid_cs_150_450` ($150\text{--}450\text{ W/m}^2$), `High_cs_gt_450` ($>450\text{ W/m}^2$).
5. **Bivariate Cloud $\times$ Elevation**: Full interaction of 3 cloud tiers $\times$ 3 elevation tiers (9 operational regimes).
6. **Seasonal Baseline**: `DJF`, `MAM`, `JJA`, `SON`.
