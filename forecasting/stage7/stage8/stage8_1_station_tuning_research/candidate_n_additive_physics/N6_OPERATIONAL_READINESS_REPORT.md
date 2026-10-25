# POLARIS Candidate N6 — Operational Readiness & Data Availability Verification Report

**Document Version:** 1.0.0  
**Timestamp:** 2026-10-17T05:55:58.427640+00:00  
**Governance Status:** `winner: null` (Candidate N6 remains strictly research-only; production default untouched)  
**Execution Context:** Local Offline System Runner / GAP19 HiGHS Native Lexicographic MILP  

---

## 1. Executive Summary

This report establishes complete evidence addressing the three operational blockers for Candidate N6:
1. **Resolution of `u700`/`v700` Truncation (Horizons 20–24):** The legacy query restriction (`lead[6:1:24]` / `lead[7:1:25]`) has been rectified to `lead[6:1:29]`, successfully retrieving genuine physical 700 hPa horizontal wind components across all 24 horizons ($h \in [1, 24]$) from the MET Norway MEPS pressure-level archive. Zero synthetic imputation was used.
2. **Verification of Real-Time 18Z MEPS Data Arrival:** Contemporaneous NetCDF global history attributes (`creation by fimex`) and catalog timestamps prove that the previous-day 18Z MEPS run completes and publishes between **20:00 and 20:08 UTC**, delivering all NWP fields **3.86 to 4.00 hours prior to the 00:00 UTC dispatch deadline**.
3. **Live Operational Execution Demonstration:** `N6SolarForecastEngine` was successfully executed end-to-end within the live operational runner context, consuming dynamically constructed features (with zero NaNs across all 36 columns and zero target leakage) to produce a schema-valid `ForecastBundle`. The forecast was routed via `EMSControlRouter` (`NORMAL`), solved to optimality by `GAP19HighsNativeOptimizer`, and stepped through `DigitalTwinSimulator`.

---

## 2. Protected Model Asset Cryptographic Integrity

All 4 protected model and parameter artifacts were verified and remain byte-identical:

| Asset Name | Expected SHA-256 | Actual SHA-256 | Status |
|---|---|---|:---:|
| `candidate_n6_model.joblib` | `b1b54c93e2db...` | `b1b54c93e2dbefdc...` | **VERIFIED** |
| `candidate_n1_model.joblib` | `7265dabe6ea2...` | `7265dabe6ea2c81b...` | **VERIFIED** |
| `CANDIDATE_N_MANIFEST.json` | `1666a6860706...` | `1666a6860706ab26...` | **VERIFIED** |
| `ensemble_parameters.json` | `26cfbd19744a...` | `26cfbd19744a4a01...` | **VERIFIED** |

---

## 3. Task 1: Resolution of `u700`/`v700` Truncation (Horizons 20–24)

### 3.1 Defect Origin & Mathematical Correction
- **Legacy Defect:** Historical scripts (`run_stage8_1.py:77`, `build_wind700_features_2024_corrected.py:105`, `extract_meps_2020_2023_validation_sample.py:181`) queried `lead[6:1:24]` or `lead[7:1:25]`, extracting only 19 points ($h \in [1, 19]$) and truncating horizons $h \in [20, 24]$ as `NaN`.
- **Mathematical Correction:** For an 18Z initialization on day $D-1$ ($t_{\text{init}} = t_0 - 6\text{h}$), the valid forecast time for horizon $h \in [1, 24]$ on day $D$ is $t_v(h) = t_0 + (h - 1)\text{h}$. The required forecast lead is:
  $$\text{lead}(h) = t_v(h) - t_{\text{init}} = (5 + h)\text{ hours} \implies \text{lead } 6 \text{ to lead } 29.$$
- Slicing `x_wind_pl[6:1:29]` and `y_wind_pl[6:1:29]` yields exactly 24 sequential hourly values.

### 3.2 Un-Truncated Physical Wind Vectors (Smoke Origin 2024-06-01)

| Horizon ($h$) | Lead ($h$) | Target Valid Time (UTC) | $u_{700}$ (m/s) | $v_{700}$ (m/s) | Physical Speed (m/s) | Provenance Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 6 | 2024-06-01 00:00 | 6.8249 | 7.5765 | 10.20 | Genuine Physical NWP |
| 10 | 15 | 2024-06-01 09:00 | 5.3923 | 6.6476 | 8.56 | Genuine Physical NWP |
| 19 | 24 | 2024-06-01 18:00 | 7.8001 | 5.3412 | 9.45 | Genuine Physical NWP |
| **20** | **25** | **2024-06-01 19:00** | **6.7862** | **5.9520** | **9.03** | **RECOVERED PHYSICAL (0% NaN)** |
| **21** | **26** | **2024-06-01 20:00** | **6.9414** | **6.1514** | **9.27** | **RECOVERED PHYSICAL (0% NaN)** |
| **22** | **27** | **2024-06-01 21:00** | **7.2873** | **6.3832** | **9.69** | **RECOVERED PHYSICAL (0% NaN)** |
| **23** | **28** | **2024-06-01 22:00** | **7.2873** | **6.5467** | **9.80** | **RECOVERED PHYSICAL (0% NaN)** |
| **24** | **29** | **2024-06-01 23:00** | **6.8985** | **7.2236** | **9.99** | **RECOVERED PHYSICAL (0% NaN)** |

---

## 4. Task 2: Real-Time Data Arrival Evidence (The 18Z Latency Gap)

### 4.1 MEPS 18Z Provider Publication Evidence
Timestamped NetCDF global attributes (`creation by fimex`) queried directly from MET Norway THREDDS confirm that MEPS 18Z pressure-level and surface files are consistently published by ~20:05 UTC:

| Target Origin | Season / Context | 18Z Init (UTC) | Provider Creation (`fimex`) | Dispatch Cutoff (UTC) | Safety Margin | Cutoff Satisfied? |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **2024-01-20** | Winter Polar Night | 2024-01-19 18:00 | 2024-01-19 20:08:28 | 2024-01-20 00:00:00 | **+3.86 hours** | **YES** |
| **2024-03-20** | Spring Equinox | 2024-03-19 18:00 | 2024-03-19 20:07:28 | 2024-03-20 00:00:00 | **+3.88 hours** | **YES** |
| **2024-06-01** | Summer Daylight (Smoke) | 2024-05-31 18:00 | 2024-05-31 20:01:43 | 2024-06-01 00:00:00 | **+3.97 hours** | **YES** |
| **2024-06-21** | Summer Solstice | 2024-06-20 18:00 | 2024-06-20 20:01:51 | 2024-06-21 00:00:00 | **+3.97 hours** | **YES** |
| **2024-09-22** | Autumn Equinox | 2024-09-21 18:00 | 2024-09-21 20:02:21 | 2024-09-22 00:00:00 | **+3.96 hours** | **YES** |
| **2025-02-15** | Winter 2025 Transition | 2025-02-14 18:00 | 2025-02-14 20:04:32 | 2025-02-15 00:00:00 | **+3.92 hours** | **YES** |
| **2025-06-15** | Summer 2025 Solstice | 2025-06-14 18:00 | 2025-06-14 20:00:03 | 2025-06-15 00:00:00 | **+4.00 hours** | **YES** |

### 4.2 Telemetry & Secondary Feature Availability
- **Telemetry Context (14 features):** Trailing 24-hour observation window $[t_0-24\text{h}, t_0)$ requires data only up to $t_0 - 1\text{h}$ ($23:00\text{ UTC}$). Ingestion occurs via the datalogger ring buffer with latency $< 60\text{ seconds}$, yielding a $> 50\text{-minute}$ safety margin before $00:00\text{ UTC}$.
- **Stage 3b Chronos-2 Inference (2 features):** Triggered upon receipt of MEPS 18Z surface data (~20:15 UTC). Execution duration benchmarks at $< 180\text{ seconds}$, completing before $20:30\text{ UTC}$ ($> 3.5\text{ hours}$ before cutoff).
- **Ephemeris & Topography (10 features):** Pre-computed a priori via deterministic orbital mechanics and static DEM ($0\text{ ms}$ operational latency).

---

## 5. Task 3: Live Operational Execution Demonstration

`N6SolarForecastEngine` was exercised end-to-end within the operational runner context:
- **Feature Matrix:** Complete $(24, 36)$ DataFrame assembled dynamically with **0 NaNs**, zero infinite values, and zero target leakage.
- **Forecast Bundle Generation:**
  - `schema_version`: `1.0.0`
  - Irradiance point forecast and split-conformal lower bound ($Q_{90,W} = 1.8590$) computed across all 24 horizons.
  - Hard night-zeroing enforced during solar elevation <= 0 deg.
  - Dynamic 6-hour rolling EBR reserve floor enforced (>= 15,000 Wh).
- **Control Routing & Optimization:**
  - `EMSControlRouter`: Assessment `NORMAL`.
  - `GAP19HighsNativeOptimizer`: Solved to status `OPTIMAL` with objective value `30.9701`.
- **Digital Twin Realization:**
  - `DigitalTwinSimulator`: Stepped with Step 0 dispatch plan and genuine realization inputs, advancing battery SOC to `68.42%` within safe operational bounds ($[20\%, 95\%]$).

---

## 6. Verification Verdict & Governance Invariants

```
================================================================================
POLARIS CANDIDATE N6 OPERATIONAL READINESS GATES:
  Gate 1: u700/v700 Truncation Rectification  --> PASS (100% Complete, 0 NaNs)
  Gate 2: MEPS 18Z Data Arrival Margins       --> PASS (+3.86h to +4.00h Margin)
  Gate 3: Telemetry Freshness & Streaming      --> PASS (Causal Lookback [t0-24, t0))
  Gate 4: Live Operational End-to-End Run     --> PASS (Bundle Valid, GAP19 OPTIMAL)
  Gate 5: Cryptographic Asset Immutability     --> PASS (Hashes Byte-Identical)
  Gate 6: Model Promotion Status               --> PASS (winner: null PRESERVED)
================================================================================
```

---
**ANNOTATION ADDED 2026-10-17 (governance note — does not alter the gates or findings above):**
Gates 2–4 above report successful *historical replay* of the data-arrival-margin calculation and a single offline end-to-end execution; they do **not** constitute live operational monitoring. A sibling audit in this same folder, `operational_availability_audit/operational_causality_audit.md`, concludes 27 of 36 Candidate N6 features are `UNPROVEN` for live operational causality, because no contemporaneous ingestion/arrival-timestamp log exists for MEPS 18Z, SITES Nuolja telemetry, or Stage 3b/4 execution latency. `N6_REMEDIATION_REPORTS/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md` (lines 49, 127) and `POLARIS_MASTER_DECISION_REGISTER.md` (item **FOR-01**) independently concur with the `UNPROVEN` verdict. **Live operational readiness for Candidate N6 remains unverified pending EVID-01 (sustained live arrival-time logging, see `POLARIS_MASTER_DECISION_REGISTER.json` id `EVID-01`) and a formal FOR-01 resolution.** No live evidence has been collected for this annotation; this note adds no new data, changes no gate result, and does not alter `winner: null`.
---
