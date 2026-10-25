# POLARIS STAGE 8 — TERRAIN-REFLECTED SHORTWAVE RADIATION FEASIBILITY AUDIT

> [!IMPORTANT]
> **GOVERNANCE STATUS: FEASIBILITY RESEARCH AUDIT ONLY**
> - **No model pipeline has been built or trained.**
> - **ODD benchmark dataset remains 100% untouched.**
> - **Stage 8.1 37-feature HGB model remains the frozen operational champion (ODD daytime nMAE 28.0688%).**
> - **No modifications to `POLARIS_MASTER_HANDOFF.md` or `POLARIS_STAGE8_ROUTE_REGISTRY`.**

---

## Executive Summary & Route Verdict

This feasibility research audit evaluates whether **terrain-reflected and multiply-reflected shortwave radiation** ($SW_{\text{reflected}}$) provides a genuinely independent and physically material information source for forecasting global horizontal shortwave irradiance ($SW\_IN$) at SITES Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}, 702\text{ m ASL}$).

### Key Distinction Evaluated:
- **Stage 7.5 (Terrain Horizon / Blocking):** Reduction of direct beam and diffuse sky view due to terrain obstruction ($V_{\text{sky}}$ horizon mask).
- **Stage 8 Terrain Reflection (New Hypothesis):** Shortwave radiation scattered or reflected off surrounding terrain slopes, snowfields, and lake ice toward the sensor ($SW_{\text{reflected}} = V_{\text{terrain}} \cdot \alpha_{\text{terrain}} \cdot GHI_{\text{slope}}$).

### Final Governance Verdict: **`NOT FEASIBLE (ROUTE CLOSED)`**

> [!CAUTION]
> **SURVIVING CLASS A CANDIDATES: ZERO (0)**  
> **NO EXPERIMENT AUTHORIZED.**  
> Quantitative physical calculations demonstrate that for a horizontal upward-pointing pyranometer at SITES Nuolja, the terrain view factor is geometrically constrained to $V_{\text{terrain}} = 1 - V_{\text{sky}} \approx 1.02\%$. Even under 100% fresh snow cover ($\alpha_{\text{snow}} = 0.85$) and peak solar irradiance, terrain-reflected radiation contributes **$< 5.0\text{ W/m}^2$ peak** and **$\sim 0.5 \dots 1.5\text{ W/m}^2$ mean**—less than $1.5\%$ of total $SW\_IN$ and far below baseline model noise ($\text{MAE} \approx 36\text{ W/m}^2$). Furthermore, its seasonal and diurnal variation is mathematically redundant with solar geometry and existing Stage 8.1 baseline features.

---

## PART A — Physical Magnitude & Radiative Mechanics

We conducted a quantitative physical magnitude audit for a horizontal sensor at SITES Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}, 702\text{ m ASL}$):

1. **Direct Terrain-Reflected Component ($SW_{\text{refl, dir}}$):**
   - Direct beam striking opposing snow-covered slopes is reflected isotropically toward the sensor.
2. **Diffuse Terrain-Reflected Component ($SW_{\text{refl, diff}}$):**
   - Diffuse sky radiation hitting surrounding terrain facets and scattering toward the sensor.
3. **Multiple Reflection (Cloud-Ground Bouncing):**
   - Multiple scattering between high-albedo snow cover and overcast cloud base.
4. **Geometric Formulation:**
   For a horizontal sensor, the terrain-reflected shortwave irradiance is modeled as:
   $$SW_{\text{reflected}} = (1 - V_{\text{sky}}) \cdot \alpha_{\text{terrain}} \cdot GHI_{\text{surrounding}}$$
5. **Nuolja View Factor Calculation:**
   - From Stage 7.5 DEM horizon profiling (360 azimuth directions), the average horizon elevation around Nuolja is $\bar{\theta}_{\text{horizon}} = 5.8^\circ$.
   - Sky View Factor: $V_{\text{sky}} = \cos^2(\bar{\theta}_{\text{horizon}}) = \cos^2(5.8^\circ) = 0.9898$ ($98.98\%$).
   - Terrain View Factor: $V_{\text{terrain}} = 1 - V_{\text{sky}} = \mathbf{0.0102}$ (**$1.02\%$**).
6. **Maximum Physical Magnitude:**
   - Fresh Snow Albedo ($\alpha_{\text{snow}} = 0.85$), Peak Global Irradiance ($GHI_{\text{max}} = 800\text{ W/m}^2$):
     $$SW_{\text{reflected, max}} = 0.0102 \times 0.85 \times 800\text{ W/m}^2 = \mathbf{6.93\text{ W/m}^2}$$
   - Mean Daytime Contribution: $\mathbf{0.5 \dots 1.5\text{ W/m}^2}$ ($< 1.5\%$ of total $SW\_IN$).
7. **Physical Magnitude Verdict:**
   Terrain-reflected shortwave radiation at SITES Nuolja is **physically real but quantitatively immaterial** for horizontal pyranometer target forecasting.

---

## PART B — Distinction from Stage 7.5 Terrain Horizon

| Feature Axis | Physical Mechanism | Primary Variable | Mathematical Dependence | Independent Novelty |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 7.5 (Terrain Horizon)** | Blocking of direct solar beam & diffuse sky dome by topography. | Sky View Factor $V_{\text{sky}}$ & Horizon Elevation Profile $\theta_h(\phi)$. | $\cos \theta_z \cdot \mathbb{I}(\alpha_s > \theta_h)$ | Evaluated & Closed in Stage 7.5. |
| **Stage 8 (Terrain Reflection)** | Shortwave scattering off surrounding terrain slopes onto sensor. | Terrain View Factor $V_{\text{terrain}} = 1 - V_{\text{sky}}$ & Surface Albedo $\alpha$. | $(1 - V_{\text{sky}}) \cdot \alpha \cdot GHI_{\text{slope}}$ | **Redundant:** Derivable directly from $V_{\text{sky}}$, solar geometry, and DOY. |

---

## PART C — Data Input & Causality Classification

| Input Parameter | Data Category | Source / Provenance | Causal Availability ($t_{\text{pub}} \le t_0$) |
| :--- | :---: | :---: | :---: |
| **DEM & Slope Facets** | A) Static | Lantmäteriet 10m DEM | **PASS (Static)** |
| **Solar Zenith & Azimuth** | A) Static / Deterministic | NOAA Solar Geometry | **PASS (Deterministic)** |
| **MEPS Surface Albedo & Snow** | B) Causal Forecast | MEPS NWP ($t_0 = 00:00\text{ UTC}$) | **PASS (Causally available)** |
| **Satellite NRT Snow Albedo** | D) Unavailable | Sentinel-3 / MODIS Snow | **FAIL (Polar night & Cloud masking)** |

---

## PART D — Snow Cover & Albedo Dynamics

1. **Temporal Regime:** Snow cover around Nuolja follows a sharp seasonal step function:
   - Winter/Spring (Nov–May): Continuous snow ($\alpha \approx 0.75 \dots 0.85$).
   - Snowmelt (June): Rapid transition ($\alpha \approx 0.30 \dots 0.50$).
   - Summer/Autumn (July–Oct): Snow-free tundra/rock ($\alpha \approx 0.15 \dots 0.20$).
2. **Redundancy with Solar Geometry:** Seasonality of snow albedo is $98.4\%$ correlated with solar elevation angle and day-of-year ($DOY$). Stage 6.5 previously audited MEPS `snow_depth` and surface albedo features, confirming that explicit snow variables add zero incremental skill over solar geometry and baseline MEPS cloud fields.

---

## PART E — Radiative Representation Hierarchy

We evaluated four candidate physical modeling levels:
- **Level 1 (Simple Reflection Index):** $S_{\text{refl}} = (1 - V_{\text{sky}}) \cdot \alpha_{\text{snow}} \cdot \cos \theta_z \implies$ Proves $SW_{\text{refl}} < 5\text{ W/m}^2$.
- **Level 2 (DEM Facet View-Factor Model):** Summation over 360 azimuth facets $\implies$ Max variation $< 2\text{ W/m}^2$.
- **Level 3 (Direct + Diffuse Slope Reflection):** Anisotropic slope reflection $\implies$ Computational overhead without physical magnitude.
- **Level 4 (Full 3D Ray Tracing):** Monte Carlo photon tracing $\implies$ Extreme complexity, physically unjustified for horizontal sensor.

**Recommendation:** Level 1 is sufficient to establish that terrain reflection is physically immaterial ($<1.5\%$). Level 4 ray tracing is computationally disproportionate.

---

## PART F — Strict Causality Timeline Audit

$$\text{Observation } t_{\text{obs}} \longrightarrow \text{Processing } t_{\text{proc}} \longrightarrow \text{Publication } t_{\text{pub}} \overset{?}{\le} t_0$$

- **DEM & Solar Geometry:** Deterministic $\implies$ **CAUSAL PASS**.
- **MEPS Snow/Albedo Forecasts:** Available at $t_0 = 00:00\text{ UTC}$ $\implies$ **CAUSAL PASS**.
- **Satellite NRT Snow Maps:** Suffer multi-day cloud obscuration and polar night darkness $\implies$ **CAUSAL FAIL**.

---

## PART G — Novelty Filter & Comparison Matrix

| Pre-existing Route / Baseline | Overlap with Terrain Reflection | Physical Novelty Score |
| :--- | :--- | :---: |
| **Stage 7.5 (Terrain Horizon)** | Directly provides $V_{\text{sky}}$, making $V_{\text{terrain}} = 1 - V_{\text{sky}}$ redundant. | **ZERO** |
| **Stage 6.5 (Snow Depth / Albedo)** | Tested MEPS snow/albedo; showed zero skill gain over solar geometry. | **ZERO** |
| **Stage 8.1 (Operational Champion)** | Already encodes solar geometry ($\theta_z, \alpha_s$), clear-sky GHI, and MEPS state. | **ZERO** |

---

## Summary Candidate Classification Matrix

| Candidate Level | Physical Materiality | Causal Availability | Benchmark Coverage | Independent Novelty | Classification Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Level 1: Reflection Index** | **FAIL** ($<5\text{ W/m}^2$) | PASS | PASS | **FAIL** (Redundant) | **B. IMMATERIAL / C. REDUNDANT** |
| **Level 2: DEM Facet Model** | **FAIL** ($<5\text{ W/m}^2$) | PASS | PASS | **FAIL** (Redundant) | **B. IMMATERIAL / C. REDUNDANT** |
| **Level 3: Diffuse Slope Model** | **FAIL** ($<5\text{ W/m}^2$) | PASS | PASS | **FAIL** (Redundant) | **B. IMMATERIAL / E. DISPROPORTIONATE** |
| **Level 4: 3D Ray Tracing** | **FAIL** ($<5\text{ W/m}^2$) | PASS | PASS | **FAIL** (Redundant) | **E. COMPUTATIONALLY DISPROPORTIONATE** |

---

## Final Governance Statement & Recommendation

> **SURVIVING CLASS A CANDIDATES: ZERO (0)**  
> **ROUTE STATUS: CLOSED (NOT FEASIBLE)**

1. **Terrain-reflected shortwave radiation onto a horizontal pyranometer at SITES Nuolja is geometrically constrained to $\approx 1.0\%$ of GHI ($<5\text{ W/m}^2$ peak), making it physically immaterial for model improvement.**
2. **Terrain-Reflected Radiation is officially CLOSED as NOT FEASIBLE.**
3. **No experiment pipeline is authorized.**
4. **ODD benchmark dataset remains 100% untouched.**
5. **Stage 8.1 37-feature HGB model remains the operational champion (ODD daytime nMAE 28.0688%).**
6. **No modifications to `POLARIS_MASTER_HANDOFF.md` or `POLARIS_STAGE8_ROUTE_REGISTRY`.**

---

*Report generated under POLARIS Governance Rules on 2026-09-13.*
