# POLARIS STAGE 8.19 — POST-PROMOTION CAUSAL AVAILABILITY CHECKPOINT

**Stage**: POLARIS Stage 8.19 Post-Promotion State Freeze & Causal Availability Checkpoint  
**Timestamp**: `2026-09-13T10:35:00+00:00`  
**Checkpoint Status**: **`CAUSAL_GOVERNANCE_VERIFIED`**  
**Official Operational Champion**: **`Stage 8.19 ABIS GNSS Model (42 features)`**  
**Held-Out ODD Performance**: **Daytime nMAE = `27.0081%`**, **MAE = `34.821405 W/m²`**, **RMSE = `62.748210 W/m²`**, **Bias = `+1.658210 W/m²`**, **Night MAE = `0.000000 W/m²`**  
**Historical Predecessor Champion**: **`Stage 8.17A AROME Structural Disagreement Model (40 features)`**  

---

## 1. Executive Summary & Champion Lock

Following the formal completion of Stage 8.19E promotion reconciliation and the Stage 8.19 Timestamp / $t_0$ Governance Audit, this checkpoint establishes the **authoritative post-promotion state lock**, **authoritative $t_0$ timestamp definition**, **causal availability inventory**, and **Second Governance Lock** for the current POLARIS operational champion.

```
================================================================================
POLARIS OFFICIAL CHAMPION POST-PROMOTION LOCK:
================================================================================
1. Official Champion Model:                         Stage 8.19 ABIS GNSS Model
2. Status:                                          FROZEN_OPERATIONAL_CHAMPION
3. Total Features:                                  42 features
4. Held-Out ODD Daytime MAE:                        34.821405 W/m²
5. Held-Out ODD Daytime nMAE:                       27.0081% (Delta vs 8.17A: -0.3256 pp)
6. Held-Out ODD Daytime RMSE:                       62.748210 W/m² (Delta vs 8.17A: -0.542602 W/m²)
7. Held-Out ODD Daytime Bias:                       +1.658210 W/m²
8. Bootstrap Evidence (10,000 resamples):           Mean ΔMAE = -0.419680 W/m², 98.64% imp.
9. 95% Bootstrap Confidence Interval:               [-0.785420, -0.051210] W/m² (Excludes zero)
10. Causal Governance Audit:                        100% VERIFIED (T_pub <= t0 across all features)
11. Authoritative Forecast Origin (t0):             00:00:00 UTC Day D
12. Benchmark Timezone:                             UTC (+00:00)

AUTHORITATIVE STATUS: STAGE 8.19 ABIS GNSS MODEL IS FROZEN_OPERATIONAL_CHAMPION
================================================================================
```

---

## 2. Authoritative Forecast Origin ($t_0$) & Timestamp Mappings

Under the locked POLARIS benchmark protocol (`POLARIS_v0_1_fixed_24h_benchmark.csv`), the forecast origin $t_0$ and time conventions are defined as:

1. **Benchmark Forecast Origin ($t_0$):** **`00:00:00 UTC` on Day D** (midnight UTC at the start of the 24-hour forecast horizon).
2. **Benchmark Timezone:** Strictly **UTC (`+00:00`)**. No local clock offset is applied in target or predictor datasets.
3. **Local Clock Equivalent:** `01:00:00 CET` (Winter) / `02:00:00 CEST` (Summer) on Day D at Abisko, Sweden ($68.3582^\circ\text{N}, 18.8258^\circ\text{E}$).
4. **Horizon Mapping:** $H1 = \text{00:00:00 UTC Day D}$, $H24 = \text{23:00:00 UTC Day D}$.
5. **SITES Target Semantics:** Period-ending hourly averages. $H1$ (`00:00:00 UTC`) represents the 10-minute average of `23:00, 23:10, 23:20, 23:30, 23:40, 23:50 UTC` from the preceding hour (`23:00-00:00 UTC`).

---

## 3. Complete Causal Availability Inventory (42 Features)

The governing principle of POLARIS causal data integrity dictates:

$$\text{For every feature } f_i: \quad T_{\text{publication}}(f_i) \le t_0$$

where $t_0$ is the benchmark forecast origin (`00:00:00 UTC Day D`). **Observed future actual target values (`actual_SW_IN`) are NEVER used for feature construction, preprocessing, model selection, hyperparameter tuning, or prediction correction.**

Below is the compact causal availability breakdown across all 7 feature families:

| Family | Feature Names | Count | Data Source | Valid-Time Rel. to $t_0$ | Publication Rel. to $t_0$ | Causal Status |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **A. SW_IN Context** | `ctx_std_3h` $\dots$ `ctx_max_24h` | 14 | SITES Nuolja Station ($SW\_IN$) | Past 24h ($t_0-24\text{h} \dots t_0$) | $T_{\text{pub}} \le t_0$ (0 min) | **VERIFIED** |
| **B. Solar Geometry** | `solar_elevation`, `solar_zenith`, `month`, `hour` | 4 | NREL SPA Solar Algorithm | Valid time ($t_0 + h$) | Deterministic constant | **VERIFIED** |
| **C. Clear-Sky Physics** | `clearsky_ghi`, `phi_inconsist` | 2 | Solis Clear-Sky + MEPS LWP | Valid time ($t_0 + h$) | $T_{\text{pub}} \le t_0 - 2.5\text{h}$ | **VERIFIED** |
| **D. MEPS NWP Features** | `fc_cloud_cover` $\dots$ `v700`, `meps_mean_*` | 16 | MET Norway MEPS 2.5km (18Z D-1) | Valid time ($t_0 + h$) | $T_{\text{pub}} \le t_0 - 2.5\text{h}$ | **VERIFIED** |
| **E. Structural Disagreement** | `wind_disagreement_700`, `LWP_disagreement` | 2 | AROME-Arctic vs MEPS (18Z D-1) | Valid time ($t_0 + h$) | $T_{\text{pub}} \le t_0 - 2.5\text{h}$ | **VERIFIED** |
| **F. Terrain & Horizon** | `terrain_horizon_elevation_deg` $\dots$ `clearsky_ghi_terrain_adjusted` | 4 | Lantmäteriet 2m DEM + Horizon | Valid time ($t_0 + h$) | Static topography | **VERIFIED** |
| **G. ABIS GNSS Features** | `abis_ztd_latest`, `abis_ztd_trend_3h` | 2 | SWEPOS E-GVAP COST-716 Product | 22:00 UTC D-1 ($t_0 - 2\text{h}$) | $T_{\text{pub}} \le t_0 - 30\text{ min}$ | **VERIFIED** |

---

## 4. Precision Record on ABIS GNSS Causality

The integration of SWEPOS station **`ABIS`** tropospheric delay observations adheres strictly to the causal parameters established during Stage 8.19:

- **Station ID & Name**: `ABIS` — Abisko Permanent Reference Station (SWEPOS)
- **Coordinates & Altitude**: $68.3582^\circ\text{ N}, 18.8258^\circ\text{ E}$, $380\text{ m}$ ASL ($326\text{ m}$ horizontally from target)
- **Data Provider**: Lantmäteriet SWEPOS / EUMETNET E-GVAP COST-716 NRT Tropospheric Delay Product
- **Primary Variable**: Zenith Total Delay (`ZTD`, mm)
- **Latest Causal Observation**: `22:00:00 UTC Day D-1` ($t_0 - 2\text{ hours}$)
- **Publication Lag & Cutoff**: Processing & NRT dissemination completed by `23:30:00 UTC Day D-1` ($T_{\text{pub}} \le t_0 - 30\text{ min}$)
- **2024 Archive Completeness**: 100.0% coverage across all 347 forecast origins (0 missing records)
- **3-Hour Tendency Definition**: $\text{ZTD}(22:00\text{ UTC D-1}) - \text{ZTD}(19:00\text{ UTC D-1})$ in $\text{mm/3h}$

> [!IMPORTANT]
> **Scientific Terminology Guardrail**: `ZTD` is defined strictly as **GNSS-derived zenith total delay (ZTD), used as an independent observation-derived atmospheric feature**. It must NOT be described as a direct measurement of cloud liquid water content, nor as a direct measurement of cloud optical depth.

---

## 5. ODD Firewall & Governance Audit

```
================================================================================
GOVERNANCE & FIREWALL AUDIT SUMMARY:
================================================================================
1. Pre-ODD Candidate Freeze Artifact Created?       YES (STAGE8_19C_ABIS_CANDIDATE_FREEZE)
2. ODD Target Access Before Freeze?                 0% (ZERO ODD access pre-freeze)
3. Pre-Registered EVEN Acceptance Gates Evaluated? YES (All 5 EVEN gates passed)
4. ODD Control Reproduction Verified?              YES (35.241085 W/m² exact match)
5. ODD Feature Selection / Tuning Occurred?         NO (0 ODD tuning / 0 feature changes)
6. Official Champion Promoted Post-Reconciliation?  YES (Stage 8.19 ABIS GNSS Model)
7. Master Handoff & Registry Reconciled?            YES (Updated & 100% bitwise consistent)
8. Benchmark Timestamp Audit Reconciled?            YES (t0 = 00:00 UTC Day D verified)
================================================================================
```

---

## 6. Rules & Directives for Future Experiments

1. **New Benchmark Control**: All future candidate models must be evaluated against **Stage 8.19 ABIS GNSS Model** (42 features, ODD Daytime MAE = `34.821405 W/m²`, nMAE = `27.0081%`).
2. **ODD Locking Rule**: The ODD set remains strictly locked and firewalled. No future candidate may read ODD targets prior to passing all EVEN acceptance gates and establishing a standalone candidate freeze artifact on disk.
3. **Causal Prerequisite**: Any proposed feature source must provide verified publication time $T_{\text{pub}} \le t_0$ before EVEN CV evaluation ($t_0 = \text{00:00:00 UTC Day D}$).

---

## 7. Conservative Scientific Guardrails

The defensible scientific conclusion from Stage 8.19 is:

> **"All features used by the frozen Stage 8.19 model were verified against the authoritative benchmark $t_0$ convention ($t_0 = \text{00:00:00 UTC Day D}$), with data availability/publication time no later than $t_0$. Under the locked POLARIS benchmark and governance protocol, the frozen Stage 8.19 ABIS GNSS candidate (`abis_ztd_latest` + `abis_ztd_trend_3h`) improved the held-out ODD benchmark relative to Stage 8.17A ($\Delta\text{MAE} = -0.419680\text{ W/m}^2$, $98.64\%$ bootstrap probability of improvement)."**

**Prohibited Overclaims**:
- Do NOT claim that ABIS proves GNSS is universally useful for all solar forecasting applications.
- Do NOT claim that ZTD directly measures cloud water or cloud optical depth.
- Do NOT claim that GNSS observations at 380m ASL are perfectly representative of summit cloud microphysics.
- Do NOT claim that the remaining forecasting error is physically irreducible.

---

## 8. Second Governance Lock — No Feature Grinding

Future research must prioritize **genuinely independent information sources**.

> [!CAUTION]
> **SECOND GOVERNANCE LOCK: NO FEATURE GRINDING**  
> Do NOT pursue additional experiments that merely:  
> 1. Algebraically transform existing features.  
> 2. Spatially differentiate existing NWP fields without a strong, physics-backed independent-information justification.  
> 3. Repackage existing disagreement signals into different metrics or nonlinear aggregations.  
> 4. Add arbitrary neighboring-grid statistics from the same NWP run.  
> 5. Create increasingly complex versions of the same information.  

A future candidate feature must first demonstrate all 6 pre-experiment criteria before an EVEN-only experiment can be authorized:
1. **Information Novelty** (Genuinely independent data source)
2. **Causal Availability** ($T_{\text{pub}} \le t_0 = \text{00:00:00 UTC Day D}$)
3. **Empirical Coverage** ($\ge 90\%$ valid data across 2024)
4. **Spatial Representativeness** (Physical alignment with target)
5. **Clear Physical Relevance** (Direct connection to atmospheric radiative attenuation)
6. **Low Redundancy** (Low mutual information with the 42 champion features)
