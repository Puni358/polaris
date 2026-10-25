# POLARIS STAGE 8 — RESEARCH ROUTE REGISTRY & CLOSED ROUTE INDEX

**Last Updated**: 2026-09-13  
**Document Purpose**: Authoritative Registry of All Audited, Closed, Blocked, and Conditional Research Routes  
**Current Operational Champion**: Stage 8.1 700 hPa Steering Wind Model (Daytime nMAE = 28.0688%)  

---

## 1. Governance Directive for Future AI Agents

> **CRITICAL INSTRUCTION FOR ALL FUTURE AGENTS:**  
> **DO NOT RECOMMEND ANY CLOSED OR BLOCKED ROUTE LISTED IN THIS REGISTRY AS A NEW IDEA. THESE ROUTES HAVE ALREADY BEEN INVESTIGATED AND THEIR REJECTION REASONS ARE PART OF THE FROZEN POLARIS RESEARCH STATE.**

### Route Classifications Defined:
1. **`CLOSED / REJECTED`**: Experimentally evaluated and proven to degrade performance, or physically non-viable / non-existent.
2. **`BLOCKED`**: Operationally non-causal ($T_{pub} > t_0$), missing required retrospective archives, or geometrically non-viable.
3. **`CONDITIONAL`**: Feasibility gate not yet met (e.g. coverage below gate, unverified API endpoints); requires materially new empirical evidence to reopen.
4. **`NOT NOVEL`**: Information is already substantially or fully represented within the Stage 8.1 37-feature inventory.
5. **`UNEXPLORED`**: Genuinely new scientific hypotheses not present in this registry.

---

## 2. Frozen Operational Champion Baseline

- **Model Name**: Stage 8.1 700 hPa Steering Wind Model
- **Daytime nMAE**: `28.0688%`
- **Daytime MAE**: `36.188657 W/m²`
- **Daytime RMSE**: `64.219495 W/m²`
- **Daytime Bias**: `+1.439399 W/m²`
- **Night MAE**: `0.0 W/m²`
- **Status**: **FROZEN OPERATIONAL CHAMPION**

---

## 3. Comprehensive Master Index of All Investigated Stage 8.x Routes

| Stage ID | Candidate Route / Source Name | Status | Primary Killing / Rejection Reason |
| :---: | :--- | :---: | :--- |
| **Stage 8.0 / 8.10** | MEPS Model-Level Vertical Profiles (65 Levels) | `REJECTED` | NWP model forecast output, NOT an independent observation. Integrated LWP/IWP trajectories already in Stage 8.1. |
| **Stage 8.3** | Abisko Ground Radiation (`SW_IN_DIR`, `SW_IN_DIFF`) | `REJECTED` | Evaluated in 5-fold CV (+0.63 W/m² MAE degradation). Valley floor radiation does not transfer summit cloud attenuation. |
| **Stage 8.4 / 8.14B** | NASA VIIRS Science L2 (`CLDPROP_L2_VIIRS`) | `BLOCKED` | Dissemination latency is 3–8 hours ($T_{pub} > t_0$). Optical retrievals fail during polar night ($SZA > 84^\circ$). |
| **Stage 8.5** | MEPS Spatial Cloud Advection | `REJECTED` | Evaluated in CV (+0.38 pp nMAE degradation). Mountain condensation/evaporation breaks 2D advection assumptions. |
| **Stage 8.6** | CAMS Solar Radiation & Cloud Parameters | `REJECTED` | Multi-day dissemination latency; derived from NWP reanalysis. |
| **Stage 8.8** | MEPS Vertical Cloud Geometry (CTTH / Cloud Base) | `REJECTED` | NWP cloud geometry features proved redundant with Stage 8.1 steering wind features. |
| **Stage 8.9A** | Independent Cloud-State Audit | `REJECTED` | Concluded `FAIL_CONFIRMED` for independent cloud-state/motion sources. |
| **Stage 8.12** | MEPS Ensemble Uncertainty Spread | `UNAPPROVED` | Ensemble spread conditioning remains unapproved for production model. |
| **Stage 8.13** | Satellite-Cloud Real-Time Operational Audit | `REJECTED` | Real-time operational execution blocked by dissemination latency and polar night fill. |
| **Stage 8.14B / 8.14C** | EUMETSAT NWC SAF PPS CMIC (`EO:EUM:DAT:MULT:PPS-CMIC`) | `CONDITIONAL` | Live EUMETSAT Data Store route returned HTTP 404 (absent from 188 live collections); public THREDDS optical coverage 70.11% (fails >=90% gate); 27 swaths lack verified $T_{pub}$; polar night fill values. |
| **Stage 8.14C Live** | EUMETSAT Optimal Cloud Analysis CDR (`EO:EUM:DAT:0617`) | `REJECTED` | Live REST metadata confirmed record ends August 2019; CLOSED for 2024 benchmark. |
| **Stage 8.15A-A1** | Nuolja Summit Sky Camera | `REJECTED` | No continuous calibrated 2024 all-sky camera archive exists. |
| **Stage 8.15A-A2** | Abisko ANS Sky Camera | `REJECTED` | Fixed-angle landscape phenology camera; non-calibrated for cloud optical thickness. |
| **Stage 8.15A-A3** | Nuolja Radiation Logger Context | `NOT NOVEL` | 14 surface radiation persistence/variance features already in Stage 8.1. |
| **Stage 8.15A-B1** | Nuolja Summit Ceilometer | `REJECTED` | Non-existent; no ceilometer installed on Nuolja summit in 2024. |
| **Stage 8.15A-B2** | Abisko ANS Ceilometer | `REJECTED` | Campaign-based; lacks continuous 2024 machine-readable archive. |
| **Stage 8.15A-B3** | Kiruna METAR Ceilometer (ESNQ) | `REJECTED` | 88.4 km separation across Scandes ridge; inland plateau air mass mismatch. |
| **Stage 8.15A-B4** | Regional Ceilometers (Sodankylä, Ivalo, Tromsø) | `REJECTED` | Extreme distance (>100–250 km) across mountain barriers. |
| **Stage 8.15A-C2** | Riksgränsen Upwind Station | `NOT NOVEL` | Surface T/RH redundant with MEPS 2m RH in Stage 8.1. |
| **Stage 8.15A-C3** | Bodø Radiosonde Sounding | `REJECTED` | 12h resolution, 220 km maritime separation; non-causal for hourly origins. |
| **Stage 8.15A-D4** | NASA VIIRS NRT L2 (`CLDPROP_L2_VIIRS_*_NRT`) | `BLOCKED` | Dissemination latency (1–3h) remains non-causal for near-$t_0$ passes; no 2024 archive. |
| **Stage 8.15A-D5** | Meteosat SEVIRI / MTG Geostationary Imagery | `REJECTED` | Viewing zenith $\theta_s = 76.54^\circ$; severe parallax ($20.9\text{ km}$) and high-latitude distortion. |
| **Stage 8.15A-D6** | NORDRAD Weather Radar Composite | `REJECTED` | Beam overshooting (>2000m ASL), terrain blocking, hydrometeor mismatch. |
| **Stage 8.16A** | Causal NWP Uncertainty / Cloud Confidence Audit | `PROVISIONALLY FEASIBLE` | Audited 10 uncertainty signals across 6 families. Identified provisionally feasible, materially distinct physical signals ($\sigma_{low\_cloud}$, $\sigma_{LWP}$, $\Phi_{inconsist}$, $N_{cat} \times \sigma_{LWP}$). Stage 8.16B NOT AUTHORIZED in this stage. |
| **Stage 8.16B-1** | Causal LWP Ensemble Spread ($\sigma_{LWP}$) | `REJECTED` | Tested $\sigma_{LWP}$ on 174 EVEN origins under 5-fold CV. Failed Gate 3 (only 2/5 folds improved) and Gate 4 (worst-fold degradation $+1.3385\text{ W/m}^2$ exceeded $+0.50\text{ W/m}^2$ limit). Stage 8.1 champion remains frozen. |

---

## 4. Mandatory Reopening Protocol for Future Research

Before any future AI agent proposes or executes work on a candidate route:

1. **Check this Registry**: Verify that the proposed route is NOT listed as `CLOSED`, `BLOCKED`, `REJECTED`, or `NOT NOVEL`.
2. **Reopening Requirements for `CONDITIONAL` / `PROVISIONALLY FEASIBLE` Routes**:
   - Must provide a materially different, independently verified product identifier and access endpoint.
   - Must empirically demonstrate $\ge 90.0\%$ daylight optical coverage across the 347 benchmark origins.
   - Must provide explicit, auditable $T_{pub} \le t_0$ publication metadata for 100% of candidate swaths.
3. **Requirement for Unexplored Routes**:
   - Must explicitly demonstrate that the proposed route is materially different from every closed route in this registry BEFORE any data extraction or model training begins.
