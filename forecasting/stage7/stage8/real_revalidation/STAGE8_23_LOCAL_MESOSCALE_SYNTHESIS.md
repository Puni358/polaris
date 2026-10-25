# STAGE 8.23 — LOCAL / MESOSCALE ATMOSPHERIC REGIME SYNTHESIS

**Stage:** POLARIS Stage 8.23 — Local & Mesoscale Atmospheric Regime Research  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $675\text{ m a.s.l.}$)  
**Forecast Lead Times:** $H1 \dots H24$ Surface Shortwave Irradiance ($SW_{IN}$)  
**Date:** September 13, 2026  
**Final Feasibility Decision:** **`FEASIBLE`**  
**Active Operational Champion:** **`UNCHANGED — STAGE 8.1 37-FEATURE HGB CHAMPION`**  

---

## 1. Executive Feasibility Synthesis

This document synthesizes the findings from the AI assistant and GPT research briefs ([`STAGE8_23_LOCAL_MESOSCALE_BRIEF.md`](file:///home/punith-bs/01polaris%20(Copy)/stage7/stage8/real_revalidation/STAGE8_23_LOCAL_MESOSCALE_BRIEF.md) and [`STAGE8_23_LOCAL_MESOSCALE_GPT_BRIEF.md`](file:///home/punith-bs/01polaris%20(Copy)/stage7/stage8/real_revalidation/STAGE8_23_LOCAL_MESOSCALE_GPT_BRIEF.md)) regarding the feasibility of local and mesoscale atmospheric information for SITES Nuolja in 2024.

The core research question evaluated is:
> *"Can POLARIS obtain causally available, historically accessible, spatially relevant local/mesoscale atmospheric information for Nuolja 2024 that is genuinely novel relative to the frozen Stage 8.1 feature set?"*

**Synthesis Finding:** **YES. A GENUINELY NEW INFORMATION AXIS EXISTS.**  
While regional radiosondes (Bodø/Luleå) and weather radar (NORDRAD) fail due to publication delays, 12-hour staleness, distance, and mountain beam blockage, **direct local ground observations of boundary-layer temperature (`TA`), relative humidity (`RH`), dew-point depression ($\text{TA} - \text{TD}$), and local valley-slope thermal inversion gradients ($\text{TA}_{\text{Nuolja}} - \text{TA}_{\text{Abisko}}$) at $t \le t_0$ represent a verified, causally available NEW INFORMATION AXIS**.

---

## 2. Candidate Evaluation Matrix Across Feasibility Gates (F1 – F10)

| Candidate Source / Axis | F1 Exist. | F2 Causal | F3 2024 Cover. | F4 Spatial | F5 Temp. | F6 Novelty | F7 Access | F8 Physics | F9 Impl. | F10 Overall Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Direct Nuolja Ground Obs ($\text{TA}, \text{RH}, \Delta \text{TA}_{6h}$)** | **PASS** | **PASS** | **PASS** (100%) | **PASS** ($0\text{ km}$) | **PASS** (1h) | **HIGH** | **PASS** | **PASS** | **PASS** | **FEASIBLE** |
| **2. Valley-Slope Inversion ($\text{TA}_{\text{Nuolja}} - \text{TA}_{\text{Abisko}}$)** | **PASS** | **PASS** | **PASS** (>98%) | **PASS** ($3\text{ km}$) | **PASS** (1h) | **HIGH** | **PASS** | **PASS** | **PASS** | **FEASIBLE** |
| **3. Orographic Froude Regime ($Fr = \frac{U_{\text{cross}}}{N \cdot H}$)** | **PASS** | **PASS** | **PASS** (100%) | **PASS** (Scandes) | **PASS** (1h) | **MOD** | **PASS** | **PASS** | **PASS** | **FEASIBLE** |
| **4. Radiosondes (Bodø 01152 / Luleå 02185)** | **PASS** | **FAIL** ($t_{\text{pub}}>t_0$) | **FAIL** (12h gap) | **FAIL** (>200 km) | **FAIL** | **PASS** | **PASS** | **PASS** | **FAIL** | **NOT FEASIBLE** |
| **5. NORDRAD Weather Radar Composite** | **PASS** | **COND** | **COND** | **FAIL** (Beam block) | **PASS** | **PASS** | **COND** | **FAIL** | **FAIL** | **NOT FEASIBLE** |

---

## 3. Detailed Breakdown of Feasibility Gates

### F1 — PRODUCT EXISTENCE: PASS
Ground meteorological observations (`TA`, `RH`, `PRECIP`, `TA_STD`, `TS_-0.01m`) exist in `POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` and SITES Abisko ANS dataset.

### F2 — CAUSAL AVAILABILITY: PASS
Ground observations for $t \le t_0$ are logged locally and available at forecast start $t_0 = 00:00\text{ UTC}$. Radiosonde soundings at 00:00 UTC arrive after $00:45\text{ UTC}$ ($t_{\text{pub}} > t_0$, `CAUSAL_FAIL`), while 12:00 UTC soundings are 12 hours stale.

### F3 — EMPIRICAL 2024 COVERAGE: PASS
SITES Nuolja logger data is 100% complete across all 8,784 hours of 2024.

### F4 — SPATIAL REPRESENTATIVENESS: PASS
Colocated directly at SITES Nuolja ($675\text{ m a.s.l.}$). Paired Abisko ANS logger is $3\text{ km}$ away ($385\text{ m a.s.l.}$). Distant radiosondes ($> 200\text{ km}$) and blocked weather radar fail spatial representativeness.

### F5 — TEMPORAL RESOLUTION: PASS
Hourly resolution matching POLARIS forecast origins.

### F6 — INFORMATION NOVELTY: HIGH (PASS)
- **Baseline Inventory (Stage 8.1 37 Features):** Stage 8.1 contains target $SW_{IN}$ context (`ctx_last_obs`, etc.) and MEPS $2\text{m}$ grid forecasts (`fc_temperature_2m`), but **zero local ground temperature or RH observations prior to $t_0$**.
- **Novel Features Identified:**
  1. `ctx_ta_last_obs`, `ctx_rh_last_obs`: Local ground boundary-layer thermal & moisture state at $t_0$.
  2. `ctx_dew_point_depression`: $\text{TA} - \text{TD}$ at $t_0$ (direct indicator of ground-level fog/stratus saturation).
  3. `ctx_ta_change_6h`: $\text{TA}(t_0) - \text{TA}(t_0 - 6\text{h})$ (front passage indicator).
  4. `ctx_valley_inversion_delta`: $\text{TA}_{\text{Nuolja}}(t_0) - \text{TA}_{\text{Abisko}}(t_0)$ (local thermal inversion strength).

### F7 — HISTORICAL ACCESS: PASS
Persisted in workspace `data/` directory.

### F8 — PHYSICAL LINK TO $SW_{IN}$: PASS
Local boundary-layer saturation ($\text{TA} - \text{TD} < 1^\circ\text{C}$) directly governs low-level cloud base formation and mountain summit fog immersion. Strong valley inversions ($\text{TA}_{\text{Nuolja}} > \text{TA}_{\text{Abisko}}$) trap fog in the valley floor leaving Nuolja clear, whereas un-inverted profiles allow cloud decks to cap the mountain summit.

### F9 — CAUSAL IMPLEMENTABILITY: PASS
Pure causal historical window $t \le t_0$.

### F10 — OVERALL FEASIBILITY: FEASIBLE

---

## 4. Strongest Verified Candidates & Exact Unresolved Evidence

### Strongest Candidates
1. **Local Nuolja Boundary-Layer State at $t \le t_0$:** Air temperature (`TA`), Relative Humidity (`RH`), Dew-Point Depression ($\text{TA} - \text{TD}$), and 6h Temperature Trend ($\Delta \text{TA}_{6h}$).
2. **Valley-Slope Inversion Delta:** $\Delta T_{\text{inversion}} = \text{TA}_{\text{Nuolja}}(t_0) - \text{TA}_{\text{Abisko}}(t_0)$.
3. **Orographic Froude Regime Indicator:** $Fr = \frac{U_{\text{cross}}}{N \cdot H_{\text{scandes}}}$.

### Exact Unresolved Evidence
- **Pre-Registration Requirement:** An experiment design specification (`STAGE8_23_EXPERIMENT_SPECIFICATION.md`) must be formally locked before any model training or CV evaluation is executed.

---

## 5. Final Decision & Governance Statement

### FINAL DECISION: **`FEASIBLE`**

> [!TIP]
> **RECOMMENDED FOR EXPERIMENT DESIGN:**
> Local ground boundary-layer observations (`TA`, `RH`, $\text{TA} - \text{TD}$, $\Delta T_{\text{inversion}}$) represent a verified, causally available, spatially representative **NEW INFORMATION AXIS** completely absent from the frozen Stage 8.1 37-feature champion.
>
> **Next Step:** Proceed to Phase 0 Experiment Specification pre-registration. No experiment execution or model training is authorized by this research task.

### Governance Firewall Compliance Statement

1. **Experiment Code Executed:** `NONE` (Zero model training, zero cross-validation).
2. **ODD Target Access:** `NONE` (Zero ODD target values read or evaluated).
3. **Operational Champion:** `UNCHANGED` (Stage 8.1 37-feature HGB champion preserved, Daytime nMAE = $28.0688\%$).
4. **Governance Files:** `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY` remain untouched.
