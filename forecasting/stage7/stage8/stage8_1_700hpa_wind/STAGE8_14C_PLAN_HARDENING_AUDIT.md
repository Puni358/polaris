# POLARIS STAGE 8.14C — BLOCKER PLAN SCIENTIFIC HARDENING AUDIT REPORT

**Stage:** POLARIS Stage 8.14C — Blocker Plan Scientific Hardening Audit  
**Status:** `COMPLETED — HARDENING AUDIT VERIFIED`  
**Current Champion:** `UNCHANGED — STAGE 8.1 700 hPa STEERING WIND MODEL`  
**Current Daytime nMAE:** `28.0688%`  
**Candidate Evaluated:** EUMETSAT NWC SAF PPS CMIC Blocker Resolution Plan V1  
**Audit Classification:** `PLAN_VALID_WITH_CORRECTIONS`  
**Forecasting Experiment Authorized:** `NO`  
**Date:** September 13, 2026  

---

## Executive Summary & Audit Mission

Stage 8.14C performed a **Scientific Hardening Audit** of the 4-step CMIC Blocker Resolution Plan V1 prior to any future implementation. 

The audit evaluated whether the V1 plan's proposed fallbacks (e.g. `ctth_temp`/`ctth_press` and COT zero-imputation during polar night) were scientifically valid, whether CTTH contains novel observational information or merely duplicates rejected NWP vertical cloud profiles (Stage 8.8), and whether the coverage gate ($\ge 90\%$) was physically achievable across a 347-origin Arctic benchmark.

### Mandatory Governance Checklist
- **Model Training Executed:** `NONE`
- **Cross-Validation Executed:** `NONE`
- **Hyperparameter Tuning:** `NONE`
- **Candidate Predictions Generated:** `NONE`
- **ODD Target Access ($SW_{IN}$):** `NONE` (Zero ODD target data read for evaluation)
- **Active Champion Preserved:** `YES` (**Stage 8.1 700 hPa Steering Wind Model**, $36.1887\text{ W/m}^2$ MAE, $28.0688\%$ nMAE)
- **POLARIS_MASTER_HANDOFF.md Modified:** `NO`

---

## 1. Locked Project-State Verification

All audit findings are anchored against the frozen Stage 8.1 Operational Champion:

- **ODD Benchmark Origins:** 173 held-out origins (347 total origins across 2024)
- **Daytime MAE:** `36.188657 W/m²`
- **Daytime nMAE:** `28.0688%` (relative to mean daytime $SW_{IN} = 128.9285\text{ W/m}^2$)
- **Daytime RMSE:** `64.219495 W/m²`
- **Daytime Bias:** `+1.439399 W/m²`
- **Night MAE:** `0.0 W/m²`

---

## 2. Audit 1: CTTH Dependency Audit

### Upstream Input & Inversion Analysis
We inspected the NWC SAF PPS CTTH (Cloud Top Height and Temperature) algorithm schema and product documentation.
- `ctth_press` (Cloud Top Pressure) and `ctth_temp` (Cloud Top Temperature) are derived by mapping multispectral thermal-IR radiances ($10.8\ \mu\text{m}, 12.0\ \mu\text{m}, 13.4\ \mu\text{m}$) against **vertical temperature, pressure, and humidity forecast profiles from NWP models** (ECMWF or MEPS) via a 1D-Var / RTTOV radiative transfer model.

### Overlap with Stage 8.1 & Stage 8.8 Baseline
- **Stage 8.1 Baseline:** Already includes surface/atmospheric NWP thermodynamics (`fc_temperature_2m`, `fc_relative_humidity_2m`).
- **Stage 8.8 Baseline:** Explicitly evaluated MEPS vertical cloud base, cloud top height, and cloud layer thickness features, and **REJECTED** them because cloud vertical geometry failed to provide incremental predictive skill over Stage 8.1 700 hPa steering wind.

### Scientific Verdict & Classification
- **Classification:** `NWP_DERIVED` & `REDUNDANT`
- **Audit Decision:** **REJECTED AS AN OPTICAL FALLBACK.** CTTH parameters are strongly NWP-derived profile inversions, NOT direct observations of optical transmissivity (`cot`). Using CTTH as a polar-night fallback re-introduces the rejected Stage 8.8 NWP vertical cloud geometry under a satellite name.

---

## 3. Audit 2: Non-Optical CMIC Variable Audit

Audit of NWC SAF PPS variables that remain active outside daylight optical conditions ($SZA > 84^\circ$):

| Variable Name | Physical Meaning | Variable Category | Polar-Night Status | Novelty vs Stage 8.1 | Hardened Usage Decision |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `cma` | Cloud Mask (Thermal IR Mode) | `OBSERVED / RETRIEVED` | **AVAILABLE 24/7/365** | **GENUINELY NOVEL** | **VALID THERMAL FALLBACK:** Observed binary cloud presence grid derived from 11/12 $\mu\text{m}$ thermal channels. |
| `phase` | Cloud Thermodynamic Phase | `OBSERVED / RETRIEVED` | **PARTIALLY AVAILABLE** | **PARTIALLY NOVEL** | **VALID THERMAL FALLBACK:** Top-of-cloud liquid vs ice phase. |
| `ctth_press` | Cloud Top Pressure | `NWP_DERIVED` | AVAILABLE 24/7/365 | **REDUNDANT** | **EXCLUDED:** Redundant with Stage 8.8 (REJECTED). |
| `cot` | Cloud Optical Thickness | `OBSERVED / RETRIEVED` | **FILL VALUE (-9999)** | **GENUINELY NOVEL** | **PRIMARY DAYLIGHT OPTICAL FEATURE.** |

---

## 4. Audit 3: Missingness Semantics & Prohibited Zero-Imputation

### Prohibited Zero-Imputation Rule
Setting missing optical retrievals to $\text{COT} = 0$ during polar night ($SZA > 84^\circ$) is physically false:
- $\text{COT} = 0$ represents a crystal-clear, transparent atmosphere with zero cloud extinction.
- During Arctic polar night, the sky may be overcast with dense stratus ($\text{COT} = 20 - 50$). Imputing $\text{COT} = 0$ injects false clear-sky signals into the model.

### 6-State Discrete Retrieval Model
V2 establishes an explicit 6-state discrete missingness/retrieval schema:

1. **`VALID_OPTICAL`**: $SZA \le 84^\circ$, valid daytime COT/CER optical retrieval, quality flag pass.
2. **`POLAR_NIGHT`**: $SZA > 84^\circ$ (Astronomical polar night or low sun). Optical solar channels return fill value (-9999). Represented via an explicit binary indicator `is_polar_night = 1` and masked NaN / separate feature branch.
3. **`LOW_SUN_INVALID`**: $80^\circ < SZA \le 84^\circ$ where optical retrievals exhibit severe stray light / low signal-to-noise ratio.
4. **`NO_GRANULE`**: Satellite overpass did not occur within origin window or granule missing from provider server.
5. **`QUALITY_REJECTED`**: Granule present, but pixel flagged for heavy snow/ice surface corruption or $\theta_s > 65^\circ$.
6. **`CAUSALITY_REJECTED`**: Granule present and valid, but publication timestamp $T_{pub} > t_0$ (fails operational causality).

---

## 5. Audit 4: 347-Origin Accounting Schema

All 347 benchmark origins must receive an auditable state classification in [`STAGE8_14C_CMIC_ORIGIN_STATE_SCHEMA.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_700hpa_wind/STAGE8_14C_CMIC_ORIGIN_STATE_SCHEMA.csv):

- Columns: `origin_id`, `t0`, `acquisition_time`, `processing_time`, `publication_time`, `causality_pass`, `granule_available`, `valid_optical`, `polar_night`, `quality_pass`, `final_feature_state`, `rejection_reason`.
- Accounting is performed purely via timestamp and metadata matching without reading target SW_IN values.

---

## 6. Audit 5: Coverage Gate Review

### Analysis of the $\ge 90\%$ Usable-Origin Threshold
- The full-year 347-origin benchmark contains 57 polar-night origins ($16.4\%$).
- Daytime optical retrievals (`cot`, `eff_radius`) can **NEVER** exceed $83.6\%$ (290 / 347 origins).
- Requiring $\ge 90\%$ overall coverage on raw optical COT across all 347 origins is **physically impossible** and represents an unachievable engineering threshold.

### Hardened Dual-Gate Structure
V2 replaces the simplistic $\ge 90\%$ threshold with two explicit predeclared criteria:
1. **Daylight Origin Optical Gate:** $\ge 90\%$ usable optical retrievals within the 290 **Daylight Origins** ($SZA \le 84^\circ$).
2. **347-Origin Benchmark Completeness Gate:** 100% of 347 origins must receive an auditable state classification in the origin schema without dropping origins or violating the locked 347-origin benchmark protocol!

---

## 7. Required Plan Corrections & Final Classification

### Required Corrections Summary:
1. **Correction 1:** Remove `ctth_temp`/`ctth_press` as a fallback for novel optical information; replace with `cma` (Thermal-IR Cloud Mask) which is a direct 24/7 observation.
2. **Correction 2:** Prohibit zero-imputation of `cot`/`eff_radius` during polar night ($SZA > 84^\circ$); use explicit `is_polar_night` indicator flags and NaN masking / dual-branch features.
3. **Correction 3:** Replace unachievable $\ge 90\%$ overall optical coverage gate with Daylight Origin Optical Coverage Gate ($\ge 90\%$ of daylight origins) and 347-Origin Dual-Branch Benchmark Gate.
4. **Correction 4:** Publish [`STAGE8_14C_CMIC_BLOCKER_RESOLUTION_PLAN_V2.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_700hpa_wind/STAGE8_14C_CMIC_BLOCKER_RESOLUTION_PLAN_V2.md) containing these hardened scientific specifications.

### Final Hardening Classification: **`PLAN_VALID_WITH_CORRECTIONS`**

---

## 8. Required Final Decision Output Format

=============================================================  
STAGE 8.14C PLAN HARDENING DECISION  
=============================================================  

STATUS:  
`COMPLETED — SCIENTIFIC HARDENING AUDIT VERIFIED`  

CURRENT CHAMPION:  
`UNCHANGED — STAGE 8.1 700 hPa STEERING WIND MODEL`  

CURRENT DAYTIME nMAE:  
`28.0688%`  

PLAN CLASSIFICATION:  
`PLAN_VALID_WITH_CORRECTIONS`  

CTTH DEPENDENCY VERDICT:  
`NWP_DERIVED & REDUNDANT (EXCLUDED AS OPTICAL FALLBACK)`  

NON-OPTICAL FALLBACK:  
`OBSERVED THERMAL CLOUD MASK (cma)`  

MISSINGNESS SEMANTICS:  
`6-STATE DISCRETE MODEL (ZERO-IMPUTATION OF COT PROHIBITED)`  

COVERAGE GATE SPECIFICATION:  
`DAYLIGHT ORIGIN OPTICAL GATE (>=90% OF DAYLIGHT ORIGINS) + 347-ORIGIN BENCHMARK GATE`  

REVISED PLAN PUBLISHED:  
`STAGE8_14C_CMIC_BLOCKER_RESOLUTION_PLAN_V2.md`  

FORECASTING EXPERIMENT AUTHORIZED:  
`NO`  

NEXT ACTION:  
`ACQUIRE EUMETSAT DATA STORE 2024 ARCHIVE AND VERIFY T_pub TIMESTAMPS ACCORDING TO REVISED V2 PLAN BEFORE PROPOSING STAGE 8.15`  

IMPORTANT GOVERNANCE BOUNDARY:  
Stage 8.14C Scientific Hardening verifies the theoretical and methodological structure of the blocker plan. It does not authorize a forecasting experiment, does not alter the Stage 8.1 Champion, and does not evaluate ODD targets.  

=============================================================  
