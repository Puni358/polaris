# POLARIS STAGE 8 — POST-STAGE 8.22 RESEARCH STATE CHECKPOINT REPORT

> [!IMPORTANT]
> **PROJECT STATUS: REPRODUCIBLE OPERATIONAL BASELINE LOCKED**  
> - **Operational Champion:** Stage 8.1 (37 features)  
> - **Verified ODD Benchmark Performance:**  
>   - **ODD Daytime nMAE:** **`28.0688%`**  
>   - **ODD MAE:** **`36.188657 W/m²`**  
>   - **ODD RMSE:** **`64.219495 W/m²`**  
>   - **ODD Mean Bias:** **`+1.439399 W/m²`**  
> - **ODD Benchmark Protection:** The 174-origin ODD benchmark dataset remains **100% protected and untouched**. All ongoing research is strictly restricted to EVEN-only data.

---

## 1. Executive Summary

This checkpoint report formalizes the research state of Project POLARIS following the completion and closure of **Stage 8.21A (3D Cloud–Solar-Ray Geometry)** and **Stage 8.22 (Satellite Cloud-Motion / NRT Cloud State)**.

The POLARIS project has methodically compressed the feature research space over 23 governed iterative stages. This checkpoint establishes the frozen baseline champion, catalogues all 20 investigated information axes, details the closure evidence for Stages 8.21A and 8.22, defines the new research position, and establishes the novelty filter and governance rules for future research.

---

## 2. Complete Registry of Investigated Information Axes

Every information axis explored to date is catalogued with its official governance status. No route in this table may be casually re-proposed without new, extraordinary empirical evidence:

| Information Axis / Feature Area | Key Features / Operators | Governance Stage | Final Governance Status |
| :--- | :--- | :---: | :---: |
| **Historical $SW\_IN$ Context** | `ctx_last_obs`, `ctx_mean_24h`, `ctx_std_6h` | Stage 6.1 / 6.2 | **CLOSED / REJECTED** |
| **Solar Geometry** | `solar_elevation`, `solar_zenith`, `clearsky_ghi` | Stage 6.3 | **INCLUDED IN CHAMPION** |
| **MEPS Cloud Fraction** | `fc_cloud_cover`, `cloud_frac` | Stage 6.4 | **INCLUDED IN CHAMPION** |
| **MEPS LWP / IWP** | `lwp_latest`, `iwp_latest`, `lwp_x_cloud` | Stage 6.6 | **INCLUDED IN CHAMPION** |
| **Vertical Cloud Summaries** | Multi-layer cloud fraction profiles | Stage 7.1 | **REJECTED ON EVEN** |
| **Cloud Base / Top Geometry** | `cloud_base_height`, `cloud_top_height` | Stage 7.2 | **REJECTED ON EVEN** |
| **Terrain & Horizon Obstructivity** | `terrain_horizon_elevation_deg`, `clearsky_ghi_terrain_adjusted` | Stage 7.5 | **INCLUDED IN CHAMPION** |
| **MEPS 700 hPa Wind Field** | `u700`, `v700` | Stage 8.1 | **INCLUDED IN CHAMPION** |
| **MEPS Spatial Cloud Fields** | Regional spatial grid cloud metrics | Stage 8.2 | **REJECTED ON EVEN** |
| **MEPS Native Radiation** | Direct MEPS surface irradiance outputs | Stage 8.3 | **REJECTED ON EVEN** |
| **MEPS Ensemble Spread** | NWP ensemble variance / uncertainty | Stage 8.4 | **REJECTED ON EVEN** |
| **Deterministic Forecast Revisions** | $D-1$ vs $D-0$ forecast delta | Stage 8.5 | **REJECTED ON EVEN** |
| **Snow / Cloud Interaction** | Surface albedo & cloud interactions | Stage 8.6 | **REJECTED ON EVEN** |
| **CAMS AOD / TCWV** | Atmospheric optical depth & water vapor | Stage 8.7 / 8.8 | **REJECTED ON EVEN** |
| **Satellite Thermal IR** | EUMETSAT SEVIRI IR brightness temp | Stage 8.9 | **REJECTED ON EVEN** |
| **Abisko Direct / Diffuse Radiation** | Ground observations from ANS station | Stage 8.10 / 8.19 | **CLOSED / REVERTED** |
| **AROME Wind / LWP Disagreement** | Multi-model NWP structural delta | Stage 8.17A | **REJECTED ON EVEN** |
| **3D Cloud–Solar-Ray Geometry** | 3D slant-path hydrometeor ray integral | Stage 8.21A | **REJECTED ON EVEN (CLOSED)** |
| **Satellite Cloud-Motion / NRT State** | AMVs, Optical Flow, NWC SAF CTH | Stage 8.22 | **CLOSED (NOT FEASIBLE)** |
| **Local Boundary-Layer State** | Nuolja ground $T_A, RH, T_D$ observations | Stage 8.23 | **REJECTED ON EVEN** |

---

## 3. Stage 8.21A Closure Summary

Stage 8.21A evaluated a 3D solar slant-path hydrometeor integration operator ($\tau_{\text{slant}}$) along the direct Sun $\to$ Nuolja vector using MEPS 3D liquid/ice condensate fields (`meps_det_pl`).

- **Technical Verdict:** The 3D cloud-ray geometry operator was **genuinely novel** and **technically feasible** ( hydrostatically reconstructed $z(p)$ over a $47 \times 47$ grid window).
- **EVEN Validation Results:**
  - **EVEN Control MAE:** $37.6201\text{ W/m}^2$ (Stage 8.1 37-feature champion)
  - **EVEN Candidate MAE:** $37.5916\text{ W/m}^2$
  - **EVEN Delta MAE:** **$-0.0285\text{ W/m}^2$**
  - **Fold Consistency (Gate G2):** **FAIL** (Improved in only **2 of 5 folds**, required $\ge 4/5$).
- **Closure Reason:** Failed pre-declared consistency Gate G2 due to spatial resolution smearing in the MEPS $2.5\text{ km}$ grid. It was **NOT** physically invalid or useless, but failed the strict governed cross-fold consistency criterion.
- **Status:** **`REJECTED_ON_EVEN` (Closed)**. ODD dataset remained 100% untouched.

---

## 4. Stage 8.22 Closure Summary

Stage 8.22 evaluated satellite cloud-motion, cloud-displacement, and real-time cloud-state observations for SITES Nuolja in 2024.

- **Audit Findings:** No candidate satellite product satisfied all operational requirements simultaneously:
  1. **GEO MSG SEVIRI AMVs / HRW:** Severely degraded by extreme View Zenith Angle ($\text{VZA} = 78.07^\circ$) over Nuolja ($68.36^\circ\text{N}$), causing a **$>21\text{ km}$ northward parallax shift** and **$>14.5\text{ km}$ pixel elongation** over the Scandes mountain ridge (**`OPERATIONALLY INFEASIBLE`**).
  2. **LEO Polar Orbiter AMVs:** Derivation latency ($1.5 \dots 3.0\text{ hours}$) causes published vectors to arrive after forecast origin $t_0 = 00:00\text{ UTC}$ ($t_{\text{pub}} > t_0$), with usable empirical coverage $<14\%$ (**`NOT CAUSALLY AVAILABLE`**).
  3. **LEO Algorithmic Optical Flow:** Processing pipeline exceeds $t_0$ cutoff; winter polar night darkness ($SZA > 84^\circ$) eliminates visible tracking; orographic mountain cloud non-stationarity ($\frac{D q_c}{D t} \ne 0$) breaks passive tracer advection (**`NOT CAUSALLY AVAILABLE`**).
  4. **LEO NWC SAF PPS Cloud Top Height (CTH):** Static cloud snapshot supplies spatial position but **zero motion velocity vectors**. When advected using MEPS 700 hPa winds, it is functionally redundant with Stage 8.1 MEPS liquid/ice cloud fields (`lwp_latest`, `iwp_latest`, `u700`, `v700`) (**`FEASIBLE BUT NOT NOVEL`**).
- **Status:** **`CLOSED (NOT FEASIBLE)`**. No experiment was authorized. ODD dataset remained 100% untouched. Stage 8.1 champion remains unchanged.

---

## 5. New Research Position

> [!IMPORTANT]
> **"We are no longer in a generic feature-addition phase."**

All basic scalar NWP additions, ground weather observations, 1D/3D model cloud variables, satellite thermal snapshots, and local ground state features have been thoroughly tested and closed.

The next research phase must search exclusively for a **GENUINELY MISSING PHYSICAL MECHANISM** or **INDEPENDENT INFORMATION AXIS** that directly affects future shortwave irradiance ($SW\_IN$).

Research must prioritize the following four physical domains (without assuming usefulness):
1. **Orographic Cloud Formation & Atmospheric Flow Regime:** Mountain-wave dynamics, Föhn wind subsidence, and forced moist ascent over the Scandes ridge.
2. **Cloud Growth / Decay / Evolution Mechanisms:** Microphysical phase change rate proxies and thermodynamic cloud lifetime dynamics.
3. **Diffuse & Broken-Cloud Radiative-Transfer Information:** Non-linear cloud fraction geometry, 3D cloud side-scattering, and diffuse irradiance fraction physics.
4. **Genuinely Independent Physical Observations:** Remote sensing or atmospheric boundary layer measurements that provide un-modelled physical state feedback.

---

## 6. Mandatory Novelty Filter for Future Candidates

Every proposed candidate feature or information axis must explicitly answer all 10 mandatory filter questions before an audit script or experiment specification can be authored:

1. **Physical Quantity/Process:** What exact physical quantity or atmospheric process does it measure?
2. **Difference from Stage 8.1:** Why is it not already represented by the 37 Stage 8.1 features (e.g. `lwp_latest`, `u700`, `v700`, `cloud_frac`)?
3. **Information Dimension:** Is it spatial, temporal, dynamical, microphysical, or radiative information?
4. **Target Failure Mode:** Which specific known POLARIS error regime (e.g. afternoon convective cloudiness, low-elevation winter errors) does it address?
5. **Causal Availability:** Is it guaranteed to be published and accessible prior to $t_0 = 00:00\text{ UTC}$ ($t_{\text{pub}} < t_0$)?
6. **Benchmark Coverage:** Can it cover $\ge 95\%$ of all 347 benchmark forecast origins in 2024?
7. **Authoritative Data Source:** What exact public or institutional dataset/archive provides it?
8. **Closest Tested Analogue:** What previously tested Stage 6–8 route is its closest analogue?
9. **Genuinely Different:** Why is it structurally and physically different from that analogue?
10. **EVEN-Only Testability:** Can it be evaluated strictly using the locked EVEN 5-fold cross-validation split without touching ODD data?

---

## 7. Permanent Governance Firewall Rules

The following 8 governance rules are locked and strictly enforced across all future POLARIS research:

1. **Strict ODD Protection:** Zero access to ODD target values during feasibility research or candidate selection.
2. **EVEN Gate Requirement:** No ODD evaluation is permitted unless an EVEN experiment passes all pre-declared acceptance gates (G1–G6).
3. **Frozen Benchmark:** The 347 forecast origin benchmark (173 EVEN / 174 ODD) is frozen and unchangeable.
4. **Frozen Champion:** The Stage 8.1 37-feature HGB model remains the operational champion during all research.
5. **No Retroactive Reopening:** Closed routes (Stages 6.1–8.23) cannot be reopened without new primary-source empirical evidence.
6. **No File Mutation without Approval:** System files (`POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY`) cannot be modified until an experiment produces a justified, promoted result.
7. **Empirical Coverage Requirement:** Theoretical overpass or coverage estimates cannot be substituted for empirical line-by-line file verification.
8. **Supported Claims Only:** All claims of novelty, causality, or physical skill must be supported by primary source derivations or empirical logs.

---

## 8. Final Research Handoff & Lists

### DO NOT RESEARCH AGAIN (Closed / Redundant Axes):
- Historical $SW\_IN$ lag context (`ctx_last_obs`, `ctx_mean_24h`)
- Single-point scalar ground weather observations ($T_A, RH, T_D$ at $t_0$)
- Basic 1D/2D NWP cloud fraction, LWP, IWP, or CTH fields
- Single-point static terrain elevation angles (Stage 7.5 terrain)
- Geostationary satellite imagery over Lapland ($\text{VZA} > 78^\circ$)
- LEO Atmospheric Motion Vectors with publication latency $> t_0$
- Static cloud snapshots advected by MEPS 700 hPa winds
- Multi-model NWP scalar disagreement features

### GENUINELY OPEN RESEARCH SPACE:
- Orographic mountain-flow stability indices (Froude number $Fr$, moist Brunt-Väisälä frequency $N_m$)
- Scandes ridge wind-perpendicular component & mountain-wave cloud formation
- Clear-sky vs. diffuse sky radiative transfer decomposition
- Boundary-layer thermodynamic moisture flux divergence

---

> **NEXT ACTION:** Conduct a fresh research synthesis for genuinely independent physical mechanisms affecting future $SW\_IN$, prioritizing orographic cloud formation/flow regime, cloud evolution, and diffuse/broken-cloud radiative transfer. Research only first. No experiment is authorized at this stage.
