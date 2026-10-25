# POLARIS STAGE 8.21A — 3D CLOUD SOLAR-RAY GEOMETRY FEASIBILITY & RESEARCH AUDIT

> [!IMPORTANT]
> **GOVERNANCE STATUS: FEASIBILITY RESEARCH AUDIT ONLY**  
> - **No model has been trained in this step.**  
> - **ODD benchmark dataset remains 100% untouched.**  
> - **Stage 8.1 37-feature HGB model remains the frozen operational champion (ODD daytime nMAE 28.0688%).**  
> - **No modifications to POLARIS_MASTER_HANDOFF.md or POLARIS_STAGE8_ROUTE_REGISTRY.**

---

## 1. Executive Summary

This feasibility and research audit evaluates the spatial cloud information axis: **3D Cloud–Solar-Ray Geometry (Stage 8.21A)**.

The research objective is to determine whether 3D liquid water mass fraction ($q_l$) and ice water mass fraction ($q_i$) from MET Norway MEPS deterministic forecasts (`meps_det_pl`) can be used to construct a causal, physically rigorous 3D slant-path ray integration operator along the actual solar vector $(x(s), y(s), z(s))$ from the Nuolja pyranometer site.

### Summary Verdict
The 3D Cloud Solar-Ray Geometry axis is **FEASIBLE AND PHYSICALLY DEFENSIBLE**, with verified causal availability, hydrostatically reconstructible 3D spatial geometry, and clear physical novelty over 1D vertical column LWP/IWP and Stage 7.5 DEM terrain features.

---

## 2. Quantitative Evaluation Across 10 Feasibility Dimensions

| Dimension | Evaluation Focus | Status | Empirical / Technical Evidence |
| :--- | :--- | :---: | :--- |
| **F1: Product & Variable Existence** | 3D Hydrometeor Fields | **PASS** | MET Norway MEPS `meps_det_pl` archive contains 3D $q_l$ (`mass_fraction_of_cloud_condensed_water_in_air_pl`) and $q_i$ (`mass_fraction_of_cloud_ice_in_air_pl`) on 13 pressure levels. |
| **F2: Causal Availability** | No Future Leakage | **PASS** | 100% causal availability across all 347 forecast origins. The $D-1$ 18:00 UTC MEPS run is published by $\sim 21:30$ UTC ($2.5\text{ hours}$ before $t_0=00:00$ UTC). |
| **F3: Spatial Coverage & Ray Geometry** | Domain Boundaries | **CONDITIONAL / PASS** | Nuolja grid index is $(y=760, x=486)$. $25 \times 25$ grid window ($30\text{ km}$ radius) covers zenith angles up to $80^\circ$ for clouds up to $5\text{ km}$. Zenith $85^\circ$ requires $57.15\text{ km}$ displacement $\implies$ expanded $47 \times 47$ grid window ($115\text{ km}$ span) or 23-ray column fallback. |
| **F4: Vertical Pressure-to-Height** | Hydrostatic Coordinate | **PASS** | 13 pressure levels ($1000$ to $50\text{ hPa}$). Geometric height $z(p)$ is hydrostatically reconstructed via $z(p) = \frac{R_d}{g} \int \frac{T_v}{p} dp$ using temperature $T$, specific humidity $q$, and surface pressure $P_{\text{sfc}}$. Below-ground pressure levels ($P > P_{\text{sfc}}$) are masked. |
| **F5: Phase Semantics** | Liquid / Ice Disambiguation | **PASS** | $q_l$ (cloud liquid) and $q_i$ (cloud ice) are separately provided in MEPS NetCDF fields in standard mass fractions ($\text{kg/kg}$). |
| **F6: Physical Meaning** | Optical Depth Proxy | **PASS** | Calculates 3D line integral of slant optical depth: $\tau_{\text{slant}} = \int \left( \frac{3 \text{LWC}}{2 \rho_w r_{e,\text{liq}}} + \frac{3 \text{IWC}}{2 \rho_i r_{e,\text{ice}}} \right) ds$ along the solar ray $(x(s), y(s), z(s))$, parameterizing $r_{e,\text{liq}}=10\,\mu\text{m}$ and $r_{e,\text{ice}}=30\,\mu\text{m}$. |
| **F7: Information Novelty** | Novelty vs 1D LWP/IWP & Stage 7.5 | **PASS** | Genuinely novel spatial 3D cloud-beam intersection operator. 1D LWP/IWP measures vertical clouds above Nuolja; Stage 7.5 DEM measures static terrain topography. 3D slant path measures dynamic cloud attenuation upwind/downwind up to $50\text{ km}$ along the Sun vector. |
| **F8: Computational Feasibility** | Data Retrieval & Slicing | **PASS** | NetCDF/OPeNDAP slicing across 347 origins requires $\sim 1.82\text{ GB}$ total payload for the $47 \times 47$ grid window, completing in $< 20\text{ minutes}$. |
| **F9: No Future Leakage** | Causal Timestamping | **PASS** | Ray tracing uses strictly causal solar zenith/azimuth geometry calculated at forecast valid times $t_0 + h$ ($h = 1 \dots 24$). |
| **F10: Benchmark Protocol** | Protocol Compatibility | **PASS** | Fully compatible with frozen 347-origin EVEN/ODD benchmark protocol without alteration. |

---

## 3. Physical Disambiguation & Novelty Analysis

### A. Novelty vs. Existing 1D LWP/IWP (`lwp_latest`, `iwp_latest`)
- **1D Vertical Column (Stage 6.6):** Integrates cloud condensate vertically directly above Nuolja $(x_0, y_0, z=0 \dots z_{\text{top}})$. When the Sun is at a low elevation angle ($\theta_z = 60^\circ \dots 85^\circ$), clouds directly overhead do not block the direct solar beam; clouds $10\text{ km} \dots 50\text{ km}$ upwind/downwind block the beam.
- **3D Slant Path (Stage 8.21A):** Integrates cloud condensate along the actual 3D vector $\vec{S} = (\sin\theta_z \sin\phi_a, \sin\theta_z \cos\phi_a, \cos\theta_z)$ passing through the 3D MEPS grid volume, capturing off-zenith cloud shadows and slant optical depth.

### B. Novelty vs. Stage 7.5 Terrain Features
- **Stage 7.5 (Terrain Obstructivity):** Computes static 1D horizon elevation angles ($\theta_{\text{terrain}}(\phi_a)$) from high-resolution DEM to determine whether solid topographic mountains block the Sun.
- **Stage 8.21A (3D Hydrometeor Obstructivity):** Computes dynamic, time-varying 3D atmospheric cloud extinction along un-obstructed solar vectors through the troposphere.

---

## 4. Historical Stage 8.21A Experiment Results & Closure Provenance Audit

For full technical completeness, previous governed execution of the Stage 8.21A candidate (3D Slant-Path Hydrometeor Geometry) yielded the following EVEN validation results:

### EVEN Validation Results
- **EVEN Control MAE:** $37.6201\text{ W/m}^2$ (Stage 8.1 37-feature champion)
- **EVEN Candidate MAE:** $37.5916\text{ W/m}^2$ (Stage 8.21A 41-feature candidate)
- **EVEN Delta MAE:** $-0.0285\text{ W/m}^2$

### Governed Gate Evaluation
- **G1 (MAE Margin):** PASS ($\Delta = -0.0285 < 0$)
- **G2 (Fold Consistency $\ge 4/5$ folds):** **FAIL** (Improved in only **2 of 5 folds**)
- **G3 (Worst-Fold Tolerance):** PASS ($+0.2541 \le +0.50\text{ W/m}^2$)
- **G4 (nMAE/RMSE Non-Degradation):** PASS
- **G5 (Causal Integrity):** PASS
- **G6 (Exact Control Reproduction):** PASS

### Protocol Closure Action
Because acceptance gate **G2 (Fold Consistency)** failed (improving in only 2 of 5 folds due to spatial resolution smearing in MEPS 2.5 km grid), **candidate freeze protocol took effect**:
1. Official ODD evaluation was **NOT** executed (`ODD_RUN = FALSE`).
2. ODD target data remained strictly uninspected (`ODD_TARGET_ACCESS = FALSE`).
3. Final Verdict: **`REJECTED_ON_EVEN`**.
4. The Stage 8.1 37-feature model remains the operational champion.

---

## 5. Recommendation of Next Genuinely Independent Information Axis

With 3D cloud-solar ray geometry (Stage 8.21A) and local ground boundary-layer state (Stage 8.23) fully audited and closed under strict governance, the recommended next genuinely independent information axis for POLARIS research is:

$$\mathbf{\text{SATELLITE CLOUD-MOTION / SATELLITE NRT CLOUD STATE (Stage 8.22)}}$$

### Rationale:
Direct geostationary/polar-orbiting satellite cloud optical depth, cloud-top height, and optical-flow advection vectors provide observational cloud-state feedback causally available before $t_0$, bypassing NWP cloud location initialization errors.

---

## Final Governance Statement

- **Stage 8.21A Feasibility Audit Completed.**
- **Route Status: REJECTED ON EVEN (Closed).**
- **ODD dataset remains 100% untouched.**
- **Stage 8.1 37-feature model remains operational champion (ODD daytime nMAE 28.0688%).**
- **No model changes, master handoff changes, or route registry changes.**
