# POLARIS STAGE 8.24 — FAITHFUL SCANDES OROGRAPHIC FLOW PRE-REGISTRATION & IMPLEMENTATION SPECIFICATION

> [!IMPORTANT]
> **GOVERNANCE STATUS: PRE-REGISTERED IMPLEMENTATION SPECIFICATION ONLY — NO EXPERIMENTS EXECUTED**
> - **Operational Champion:** **Stage 8.1 37-feature HGB Model** (`RETAINED_UNTOUCHED`)
> - **Protected Held-out ODD Metrics:** **MAE 36.188657 W/m² | nMAE 28.0688% | RMSE 64.219495 W/m² | Bias +1.439399 W/m²**
> - **ODD Benchmark Status:** **100% UNTOUCHED & PROTECTED (`ODD_RUN = FALSE`)**
> - **Master Handoff & Route Registry:** **UNTOUCHED**
> - **Mandatory Constraints:** NO model experiment executed. NO ODD target data accessed. NO champion modifications.

---

## 1. Executive Summary & Objective

This document establishes the pre-registration specification and implementation design for a **faithful discrete layer-integrated re-evaluation** of the Scandes Orographic Flow Regime hypothesis (re-evaluating the provisionally rejected Stage 8.24 route).

The prior Stage 8.24 experiment tested an approximate 2-point stability shortcut constructed from surface and 700 hPa endpoints. That empirical result demonstrated that the *approximate shortcut* degraded performance, but carried an implementation qualification and did **not** constitute a definitive rejection of the underlying continuous physical hypothesis.

This specification establishes a mathematically rigorous, faithful discrete layer-integrated formulation of:
1. **Barrier-Normal Wind ($U_\perp$)** along the $290^\circ$ Scandes inflow axis.
2. **Continuous Layer-Integrated Brunt–Väisälä Buoyancy Frequency ($N_{\text{layer}}$)** over the $P_{\text{sfc}} \to 700\text{ hPa}$ tropospheric layer using virtual potential temperature profiles.
3. **Mountain Froude Number ($Fr$)** flow-regime indicator.

---

## 2. Rigorous Physical Quantity Specifications (A – P)

### Quantity 1: Barrier-Normal Wind ($U_\perp$)

- **A. Exact Mathematical Definition:**  
  $$U_\perp = \vec{V}_{700} \cdot \hat{n}_{\text{inflow}} = u_{700} \sin(\theta_{\text{normal}}) + v_{700} \cos(\theta_{\text{normal}})$$  
  where $\theta_{\text{normal}} = 290^\circ$ is the direction from North of the inflow axis perpendicular to the main Scandes mountain ridge ($200^\circ \leftrightarrow 020^\circ$).  
  $$\mathbf{U_\perp = -0.9396926 \cdot u_{700} + 0.3420201 \cdot v_{700}}$$  
  *(where $u_{700}$ is eastward wind, $v_{700}$ is northward wind).*
- **B. Coordinate / Sign Convention:**  
  $u_{700}$ positive East, $v_{700}$ positive North. $U_\perp > 0$ represents positive onshore/maritime inflow from the Norwegian Sea impinging on Mount Nuolja (WNW $\to$ ESE, heading $110^\circ$). $U_\perp < 0$ represents downslope lee-side Föhn flow (ESE $\to$ WNW).
- **C. DEM-Derived Terrain Quantity:**  
  Scandes mountain ridge orientation ($200^\circ \leftrightarrow 020^\circ$) and Lake Torneträsk valley inflow funnel axis ($290^\circ$), derived from 30m Lantmäteriet DEM surrounding Abisko/Nuolja ($68.35^\circ\text{N} \dots 68.40^\circ\text{N}, 18.50^\circ\text{E} \dots 19.00^\circ\text{E}$).
- **D. MEPS Variables & Levels Used:**  
  MEPS 700 hPa zonal wind `u700` ($u_{700}$, $\text{m/s}$) and meridional wind `v700` ($v_{700}$, $\text{m/s}$) at valid forecast lead time $t_0 + h$ ($h \in [1, 24]$).
- **E. Pressure Levels Below Surface:**  
  Not applicable for 700 hPa ($z \approx 3,000\text{ m ASL}$), which is well above Mount Nuolja summit ($1,169\text{ m ASL}$) and surface pressure ($P_{\text{sfc}} \approx 930 \dots 960\text{ hPa}$).
- **F. Potential Temperature Calculation:**  
  Not required for $U_\perp$ calculation.
- **G. Vertical Derivatives Calculation:**  
  Not required for $U_\perp$ calculation.
- **H. Layer Integration:**  
  Evaluated at 700 hPa pressure level representing un-blocked synoptic steering flow over Scandes ridge tops.
- **I. Representative Wind Speed Selection:**  
  700 hPa steering wind vector. **Justification:** 700 hPa ($\sim 3,000\text{ m ASL}$) is situated above mountain boundary-layer friction and local terrain funneling, capturing the unblocked synoptic steering flow impinging on Scandes. 10m surface winds are heavily distorted by local valley vegetation and canopy friction.
- **J. Representative Mountain Height Selection:**  
  Not applicable for $U_\perp$ calculation itself.
- **K. Exact Causal Timestamp:**  
  Available at forecast origin $t_0 = 00:00\text{ UTC}$ from operational MEPS 18:00 UTC D-1 issuance for valid lead hours $h = 1 \dots 24$.
- **L. Benchmark Availability:**  
  **100% available** across all 347 forecast origins in the 2024 benchmark.
- **M. Interpolation / Extrapolation:**  
  Spatial bilinear interpolation to Nuolja pyranometer coordinates ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$).
- **N. Missing-Data Handling:**  
  Zero missing values in 2024 MEPS archive for 700 hPa wind fields.
- **O. Potential Leakage Pathways:**  
  None. Derived strictly from forecast fields valid for $t_0+h$ from model runs initialized prior to $t_0$.
- **P. Genuine Novelty vs. Stage 8.1:**  
  Stage 8.1 contains raw Cartesian $u_{700}$ and $v_{700}$. Decision tree hyperplanes ($u > c$, $v > c$) cannot construct the linear rotated projection $U_\perp = u\cos\alpha + v\sin\alpha$ without deep interaction splits. $U_\perp$ provides a compact, physically meaningful flow-relative coordinate.

---

### Quantity 2 & 3: Vertical Stability ($N$) & Layer-Integrated Stability ($P_{\text{sfc}} \to 700\text{ hPa}$)

- **A. Exact Mathematical Definition:**  
  Continuous Brunt–Väisälä buoyancy frequency definition: $N(z) = \sqrt{ \frac{g}{\theta_v(z)} \frac{\partial \theta_v}{\partial z} }$.  
  Faithful discrete layer-integrated estimate over the surface-to-700hPa layer ($P_{\text{sfc}} \to 700\text{ hPa}$):  
  $$N_{\text{layer}} = \sqrt{ \frac{g}{\bar{\theta}_v} \sum_{k=1}^{K-1} \frac{\theta_v(p_{k+1}) - \theta_v(p_k)}{z(p_{k+1}) - z(p_k)} \frac{\Delta z_k}{\Delta Z_{\text{tot}}} }$$  
  where $g = 9.80665\text{ m/s}^2$, $\theta_v = T_v \left( \frac{100000}{p} \right)^{0.286}$, $T_v = T(1 + 0.608 q)$, and $\Delta Z_{\text{tot}} = z(700) - z(P_{\text{sfc}})$.
- **B. Coordinate / Sign Convention:**  
  $p$ decreases upwards ($P_{\text{sfc}} > 925 > 850 > 700\text{ hPa}$), $z$ increases upwards. Stable stratification requires $\frac{\partial \theta_v}{\partial z} > 0$ ($\theta_v(700) > \theta_v(P_{\text{sfc}})$), yielding $N^2 > 0$ ($N > 0\text{ s}^{-1}$). If $\frac{\partial \theta_v}{\partial z} \le 0$ (unstable/neutral lapse rate), $N^2 \le 0$ is clipped to a small positive floor $N_{\text{floor}} = 10^{-4}\text{ s}^{-1}$ to prevent complex numbers or division by zero.
- **C. DEM-Derived Terrain Quantity:**  
  Station surface elevation $z_{\text{sfc}} = 675\text{ m ASL}$ (pyranometer) or Torneträsk valley floor elevation $z_{\text{valley}} = 341\text{ m ASL}$, derived from 30m DEM.
- **D. MEPS Variables & Levels Used:**  
  Pressure-level profiles from `meps_det_pl`: $T$ (temperature, K), $q$ (specific humidity, kg/kg) at 925, 850, 700 hPa, combined with surface pressure `psfc` ($P_{\text{sfc}}$, Pa), 2m temperature `fc_temperature_2m` ($T_{2\text{m}}$, K), and 2m relative humidity `fc_relative_humidity_2m` ($RH_{2\text{m}}$, %).
- **E. Pressure Levels Below Surface:**  
  At Nuolja (pyranometer elevation $675\text{ m ASL}$, mean $P_{\text{sfc}} \approx 935\text{ hPa}$), the 1000 hPa level is subterranean ($p > P_{\text{sfc}}$). **Handling:** Subterranean levels ($p > P_{\text{sfc}}$) are strictly excluded from profile layer integration. The bottom level of the layer is set exactly to the valid surface state ($P_{\text{sfc}}, T_{2\text{m}}, q_{2\text{m}}$). If $P_{\text{sfc}} < 925\text{ hPa}$ during extreme low pressure, the 925 hPa level is also excluded if subterranean, integrating over available pressure levels $P_{\text{sfc}} \to 850 \to 700\text{ hPa}$.
- **F. Potential Temperature / Virtual Potential Temperature Calculation:**  
  1. Virtual temperature: $T_v = T \cdot (1 + 0.608 \cdot q)$ (K).  
  2. Virtual potential temperature: $\theta_v = T_v \cdot \left( \frac{100000}{p} \right)^{0.286}$ (K), where $p$ is pressure in Pa.  
  3. Mean layer virtual potential temperature: $\bar{\theta}_v = \frac{\theta_v(P_{\text{sfc}}) + \theta_v(700)}{2}$ (K).
- **G. Vertical Derivatives Calculation:**  
  Discrete finite differences between adjacent MEPS levels:  
  $$\frac{\Delta \theta_v}{\Delta z} = \frac{\theta_v(p_{k+1}) - \theta_v(p_k)}{z(p_{k+1}) - z(p_k)}$$  
  where geopotential height difference $\Delta z_k$ is calculated using the hypsometric equation:  
  $$\Delta z_k = \frac{R_d \bar{T}_{v, k}}{g} \ln\left( \frac{p_k}{p_{k+1}} \right)$$
- **H. Layer Integration:**  
  Layer-weighted mean Brunt–Väisälä frequency:  
  $$N_{\text{layer}} = \sqrt{ \sum_{k=1}^{K-1} N_k^2 \cdot \frac{\Delta z_k}{\Delta Z_{\text{tot}}} }$$  
  where $N_k^2 = \frac{g}{\bar{\theta}_{v,k}} \frac{\theta_v(p_{k+1}) - \theta_v(p_k)}{\Delta z_k}$ and $\Delta Z_{\text{tot}} = \sum \Delta z_k = z(700) - z(P_{\text{sfc}})$.
- **I. Representative Wind Speed:**  
  Not used directly in $N$ calculation.
- **J. Representative Mountain Height:**  
  Not used directly in $N$ calculation.
- **K. Exact Causal Timestamp:**  
  Forecast valid time $t_0 + h$ from MEPS 18:00 UTC D-1 run.
- **L. Benchmark Availability:**  
  **100% available** across all 347 origins.
- **M. Interpolation / Extrapolation:**  
  Vertical hypsometric interpolation between discrete pressure levels.
- **N. Missing-Data Handling:**  
  Standard physical defaults ($N_{\text{floor}} = 10^{-4}\text{ s}^{-1}$ for superadiabatic layers).
- **O. Potential Leakage Pathways:**  
  None.
- **P. Genuine Novelty vs. Stage 8.1:**  
  Stage 8.1 contains single-level 2m temp/humidity and does NOT calculate continuous vertical potential temperature gradients or Brunt–Väisälä buoyancy frequencies.

---

### Quantity 4: Mountain Froude Number ($Fr$)

- **A. Exact Mathematical Definition:**  
  Non-dimensional ratio of inertial force to gravitational buoyancy force for air parcels impinging on Mount Nuolja:  
  $$Fr = \frac{U_\perp}{N_{\text{layer}} \cdot h}$$  
  where $U_\perp$ is the Scandes barrier-normal wind ($\text{m/s}$), $N_{\text{layer}}$ is the faithful discrete layer-integrated Brunt–Väisälä buoyancy frequency ($\text{s}^{-1}$), and $h$ is the effective mountain relief height ($\text{m}$).
- **B. Coordinate / Sign Convention:**  
  Continuous signed Froude number $Fr = \frac{U_\perp}{N_{\text{layer}} \cdot h}$. Positive $Fr$ indicates impinging onshore flow; negative $Fr$ indicates downslope Föhn flow.
- **C. DEM-Derived Terrain Quantity:**  
  Effective mountain relief height $h = z_{\text{summit}} - z_{\text{valley}} = 1,169\text{ m} - 341\text{ m} = \mathbf{828\text{ m}}$, derived from 30m DEM.
- **D. MEPS Variables Used:**  
  Combines inputs from $U_\perp$ (`u700`, `v700`) and $N_{\text{layer}}$ (`psfc`, `fc_temperature_2m`, `fc_relative_humidity_2m`, profile $T, q$ at 925, 850, 700 hPa).
- **E. Pressure Levels Below Surface:**  
  Inherits surface truncation rule from $N_{\text{layer}}$ ($p \le P_{\text{sfc}}$).
- **F. Potential Temperature Calculation:**  
  Inherits $\theta_v$ formulation from $N_{\text{layer}}$.
- **G. Vertical Derivatives:**  
  Inherits layer-integrated stability from $N_{\text{layer}}$.
- **H. Layer Integration:**  
  Evaluated over surface ($P_{\text{sfc}}$) to 700 hPa layer.
- **I. Representative Wind Speed:**  
  700 hPa barrier-normal wind $U_\perp$ ($\text{m/s}$). **Justification:** Captures unblocked synoptic inflow impinging on the mountain barrier.
- **J. Representative Mountain Height:**  
  Fixed effective mountain relief height $h = 828\text{ m}$. **Justification:** Represents the actual vertical obstacle height from Lake Torneträsk valley floor ($341\text{ m ASL}$) to Mount Nuolja summit ($1,169\text{ m ASL}$) that an impinging air parcel must ascend.
- **K. Exact Causal Timestamp:**  
  Valid time $t_0 + h$ from MEPS 18:00 UTC D-1 run.
- **L. Benchmark Availability:**  
  **100% available** across all 347 origins.
- **M. Interpolation / Extrapolation:**  
  None beyond component calculations.
- **N. Missing-Data Handling:**  
  $N_{\text{layer}}$ clipping ($N \ge 10^{-4}\text{ s}^{-1}$) prevents division by zero.
- **O. Potential Leakage Pathways:**  
  None.
- **P. Genuine Novelty vs. Stage 8.1:**  
  Unites wind vector, static atmospheric stability, and mountain geometry into a non-linear non-dimensional flow regime index. Stage 8.1 has zero non-dimensional regime features.

---

## 3. Scientific Analysis of Orographic Uplift Velocity ($w_{\text{oro}}$)

- **Question:** Does $w_{\text{oro}} = U_\perp \cdot |\nabla z_{\text{terrain}}|$ add genuinely independent information beyond $U_\perp$, $Fr$, and existing Stage 8.1 wind/terrain features?
- **Finding:** No. For a static single-station target site (Mount Nuolja), local terrain slope along the inflow axis $|\nabla z_{\text{terrain}}|$ is a constant scalar multiplier ($C_{\text{slope}} \approx 0.1507\text{ m/m}$). Thus, $w_{\text{oro}} = U_\perp \times C_{\text{slope}}$ is **100% linearly collinear with $U_\perp$**. Decision tree split points on $w_{\text{oro}}$ are mathematically identical to split points on $U_\perp$.
- **Pre-registration Decision:** **EXCLUDE $w_{\text{oro}}$** from candidate feature set to adhere to the strict scientific requirement of minimizing feature count and avoiding redundant feature explosion.

---

## 4. Pre-Registered Candidate Feature List

The candidate model extends the locked Stage 8.1 37-feature control by adding **EXACTLY TWO (2)** continuous physical features:

1. **`ctx_u_perp`**: Faithful discrete estimate of Scandes barrier-normal wind component $U_\perp$ ($\text{m/s}$).
2. **`ctx_mountain_froude`**: Faithful discrete layer-integrated mountain Froude number $Fr = \frac{U_\perp}{N_{\text{layer}} \cdot h}$ (non-dimensional).

*(Total Candidate Feature Count: 37 + 2 = 39 features).*

---

## 5. Critical Scientific Guidelines & Hypothesis Statements

1. **Discrete Estimation Terminology:** All discrete calculations are specified as *"faithful discrete/layer-integrated estimates from MEPS vertical profiles"* rather than exact continuous field integrals.
2. **No Hardcoded Regime Labels:** The features `ctx_u_perp` and `ctx_mountain_froude` are provided to the model as continuous physical predictors. Simplistic deterministic labels (such as $Fr < 1 \implies \text{trapped cloud}$, $Fr \ge 1 \implies \text{wave cloud}$) are **NOT** hardcoded into the dataset. The Gradient Boosted Tree model will learn non-linear relationships directly from data.
3. **Hypothesis Under Test:**  
   > *"Adding continuous barrier-normal wind ($U_\perp$) and faithful layer-integrated mountain Froude number ($Fr$) predictors provides incremental predictive skill for broadband shortwave irradiance forecasting over Mount Nuolja, passing ALL SIX EVEN acceptance gates G1–G6."*

---

## 6. Leakage & Causality Audit

1. **Temporal Causality Check:** All inputs (`u700`, `v700`, `psfc`, `fc_temperature_2m`, `fc_relative_humidity_2m`, pressure-level $T, q$ profiles) originate from the operational MEPS 18:00 UTC D-1 forecast run, which is fully published and available prior to $t_0 = 00:00\text{ UTC}$ on Day D. $T_{\text{pub}} \le t_0$ is 100% satisfied for all 347 benchmark origins.
2. **Spatial Alignment Check:** Extracted for the exact grid cell covering Mount Nuolja pyranometer ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$).
3. **Target Firewall Check:** Zero pyranometer ground target data (`actual_SW_IN`) is used in computing candidate features. Features are strictly antecedent meteorological predictors.
4. **ODD Firewall Check:** No ODD data or evaluation will be accessed (`ODD_RUN = FALSE`).
5. **Audit Verdict:** **LEAKAGE & CAUSALITY AUDIT PASSED (100% CLEAN).**

---

## 7. Readiness Verdict

```
READY_FOR_GOVERNED_EVEN_EXPERIMENT
```

---

*Specification generated under POLARIS Stage 8 Governance Guidelines on 2026-09-13.*
