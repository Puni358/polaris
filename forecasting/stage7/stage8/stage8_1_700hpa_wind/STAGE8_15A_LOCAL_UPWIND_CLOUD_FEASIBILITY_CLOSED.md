# POLARIS STAGE 8.15A — CLOSED FEASIBILITY ROUTE CHECKPOINT & REGISTRY

**Date**: 2026-09-13  
**Stage**: POLARIS STAGE 8.15A — LOCAL/UPWIND CLOUD OBSERVATION FEASIBILITY AUDIT  
**Status**: `COMPLETED — CLOSED FEASIBILITY ROUTE CHECKPOINT`  
**Stage 8.15B Execution**: **NOT AUTHORIZED / NOT JUSTIFIED**  
**Active Operational Champion**: Stage 8.1 700 hPa Steering Wind Model (Daytime nMAE = 28.0688%)  
**Governance & Firewall Status**: 100% Compliant (0 ODD target reads, 0 model changes, 0 experiments executed, master benchmark untouched).  

---

## 1. Executive Summary & Authoritative Result

Stage 8.15A evaluated candidate observational cloud sources across 4 major families (Local/All-Sky, Ceilometer/Cloud-Base, Nearby Surface/Sounding, Satellite/Composite) to determine if an independently observed, causally available, spatially representative cloud-state data source exists for the 2024 SITES Nuolja benchmark.

### Authoritative Scientific Conclusion
> **"Stage 8.15A did not identify a local/upwind observational source that simultaneously satisfied the required causal availability, 2024 coverage, spatial/terrain representativeness, information novelty, and operational reproducibility conditions. Therefore Stage 8.15B was not justified."**

---

## 2. Frozen Operational Champion Baseline

All project records remain strictly locked to the Stage 8.1 Operational Champion:

- **Champion Model**: Stage 8.1 700 hPa Steering Wind Model
- **Daytime nMAE**: `28.0688%`
- **Daytime MAE**: `36.188657 W/m²`
- **Daytime RMSE**: `64.219495 W/m²`
- **Daytime Bias**: `+1.439399 W/m²`
- **Night MAE**: `0.0 W/m²`
- **ODD Benchmark Origins**: 173 held-out origins (347 total 2024 benchmark origins)
- **ODD Evaluation Reads**: **0**
- **POLARIS_MASTER_HANDOFF.md**: **UNTOUCHED**

---

## 3. Register of Closed & Audited Routes (Families A – D)

### A. Local / All-Sky Observations

| Route ID | Candidate Source Name | Location / Sensor | Status Classification | Primary Rejection Rationale |
| :---: | :--- | :--- | :---: | :--- |
| **A1** | **Nuolja Summit Sky Camera** | Nuolja Summit ($0.0\text{ km}$) | `REJECTED — DATA NON-EXISTENCE` | No continuous calibrated 2024 all-sky camera archive exists. |
| **A2** | **Abisko ANS Sky Camera** | Abisko ANS ($3.23\text{ km}$ ESE) | `REJECTED — PRODUCT MISMATCH` | Fixed-angle landscape/phenology camera; not a calibrated cloud optical imager. |
| **A3** | **Nuolja Radiation Logger** | Nuolja Summit ($0.0\text{ km}$) | `NOT NOVEL` | 14 radiation persistence, variance, and trend features already in Stage 8.1 champion. |

---

### B. Ceilometer / Cloud-Base Observations

| Route ID | Candidate Source Name | Location / Sensor | Status Classification | Primary Rejection Rationale |
| :---: | :--- | :--- | :---: | :--- |
| **B1** | **Nuolja Summit Ceilometer** | Nuolja Summit ($0.0\text{ km}$) | `REJECTED — NON-EXISTENT` | No 2024 summit ceilometer was installed or operated. |
| **B2** | **Abisko ANS Ceilometer** | Abisko ANS ($3.23\text{ km}$ ESE) | `REJECTED — INSUFFICIENT COVERAGE` | Campaign/episodic operations; lacks continuous 2024 machine-readable archive. |
| **B3** | **Kiruna METAR Ceilometer** | Kiruna ESNQ ($88.4\text{ km}$ ESE) | `REJECTED — SPATIAL/TERRAIN MISMATCH` | ~88.4 km separation and Scandes terrain/inland plateau air-mass mismatch. |
| **B4** | **Regional Ceilometer Net** | Sodankylä/Ivalo ($>100\text{ km}$) | `REJECTED — SPATIAL/TERRAIN MISMATCH` | Relevant candidate stations are too distant and separated by major mountain barriers. |

---

### C. Surface / Sounding Observations

| Route ID | Candidate Source Name | Location / Sensor | Status Classification | Primary Rejection Rationale |
| :---: | :--- | :--- | :---: | :--- |
| **C1** | **Abisko ANS Surface Rad** | Abisko ANS ($3.23\text{ km}$ ESE) | `REJECTED` | Evaluated in Stage 8.3 CV and REJECTED (+0.63 W/m² MAE degradation). |
| **C2** | **Riksgränsen Weather** | Riksgränsen ($\approx 30\text{ km}$ W) | `NOT NOVEL / REDUNDANT` | Surface T/RH information is substantially represented by existing MEPS RH/state. |
| **C3** | **Bodø Radiosonde** | Bodø ($\approx 220\text{ km}$ WSW) | `REJECTED` | Low cadence (12h) and large maritime separation (220 km); non-causal for hourly origins. |

---

### D. Satellite / Composite Observations

| Route ID | Candidate Source Name | Location / Sensor | Status Classification | Primary Rejection Rationale |
| :---: | :--- | :--- | :---: | :--- |
| **D1** | **EUMETSAT NWC SAF CMIC** | Nuolja Swaths ($<1.0\text{ km}$) | `CONDITIONAL / BLOCKED` | Live Data Store route unverified (`EO:EUM:DAT:MULT:PPS-CMIC` HTTP 404, 0/188 live collections); open THREDDS coverage (70.11%) below >=90% gate; 27 swaths lack verified $T_{pub}$; polar night optical fill values. |
| **D2** | **EUMETSAT OCA CDR 0617** | EUMETSAT Catalogue | `REJECTED — TEMPORAL CUTOFF` | Live REST metadata confirms coverage ends 2019-08-31; cannot support 2024 benchmark. |
| **D3** | **NASA VIIRS Science L2** | NASA LAADS ($<2.5\text{ km}$) | `BLOCKED — OPERATIONALLY NON-CAUSAL` | Standard science-product publication latency (3–8h) occurs after required $t_0$. |
| **D4** | **NASA VIIRS NRT L2** | NASA LANCE ($<2.5\text{ km}$) | `BLOCKED — OPERATIONALLY NON-CAUSAL` | Dissemination latency (1–3h) remains non-causal for near-$t_0$ passes; no 2024 archive. |
| **D5** | **Meteosat SEVIRI/FCI** | Geostationary ($0^\circ\text{N}$) | `REJECTED` | Extreme high-latitude viewing geometry ($\theta_s = 76.54^\circ$) and parallax ($20.9\text{ km}$). |
| **D6** | **NORDRAD Radar Composite** | Kiruna Radar ($>85\text{ km}$) | `REJECTED` | Radar geometry/terrain limitations (beam overshooting $>2000\text{ m}$ ASL) and hydrometeor mismatch. |

---

## 4. Future-AI Mandatory Route Firewall Directives

**ALL FUTURE AI AGENTS OPERATING ON POLARIS MUST OBEY THE FOLLOWING FIREWALL DIRECTIVES:**

1. **GENERAL ROUTE PROTECTION**:
   > *"DO NOT RECOMMEND ANY STAGE 8.15A ROUTE LISTED ABOVE AS A NEW IDEA. THESE ROUTES HAVE ALREADY BEEN INVESTIGATED AND THEIR STATUS/REJECTION REASONS ARE PART OF THE POLARIS RESEARCH STATE."*

2. **FOR PPS-CMIC (`EO:EUM:DAT:MULT:PPS-CMIC`)**:
   > *"DO NOT reopen PPS-CMIC merely because it appears in external research recommendations. Reopening requires a materially different and independently verified product identifier/access pathway plus empirical 2024 coverage and causal publication evidence."*

3. **FOR OPTICAL CLOUD ANALYSIS (`EO:EUM:DAT:0617`)**:
   > *"DO NOT recommend OCA CDR 0617 for the 2024 benchmark; its verified record ends in 2019."*

4. **FOR VIIRS SATELLITE PRODUCTS (`CLDPROP_L2_VIIRS`)**:
   > *"DO NOT treat acquisition time as equivalent to operational availability. Any reopening requires verified publication/availability timestamps satisfying the locked t0 causality rule."*

5. **FOR LOCAL / NEARBY INSTRUMENTS**:
   > *"DO NOT infer representativeness from geographic proximity alone. Spatial distance, terrain separation, observing geometry, and actual cloud-regime representativeness must be demonstrated."*

---

## 5. Next-Route Handoff Instructions

1. **Stage 8.15B Status**: **NOT EXECUTED / NOT AUTHORIZED**.
2. **Next Scientific Route**: The next research stage must target a **NEW, materially different hypothesis**.
3. **Mandatory Pre-Feasibility Checklist for Future Agents**:
   - Must read `STAGE8_15A_LOCAL_UPWIND_CLOUD_FEASIBILITY_CLOSED.md` and `POLARIS_STAGE8_ROUTE_REGISTRY.json`.
   - Must inspect all previous Stage 8.x closure artifacts (Stage 8.0, 8.3, 8.4, 8.5, 8.6, 8.8, 8.9A, 8.10, 8.12, 8.13, 8.14B, 8.14C, 8.15A).
   - Must explicitly demonstrate that the proposed route is materially different from every closed/rejected route prior to beginning any data extraction or feasibility code execution.
