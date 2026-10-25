# POLARIS FRESH RESEARCH ROUND — OROGRAPHIC CLOUD-REGIME DYNAMICS REPORT

> [!IMPORTANT]
> **GOVERNANCE STATUS: RESEARCH FEASIBILITY SYNTHESIS ONLY**  
> - **No model has been trained or evaluated in cross-validation.**  
> - **ODD benchmark dataset remains 100% untouched.**  
> - **Stage 8.1 37-feature HGB model remains the frozen operational champion (ODD daytime nMAE 28.0688%).**  
> - **No modifications to POLARIS_MASTER_HANDOFF.md or POLARIS_STAGE8_ROUTE_REGISTRY.**  
> - **No experiment is authorized by this research task.**

---

## 1. Executive Summary

This fresh research round investigates a fundamental physical hypothesis:

> *"POLARIS is missing a physically meaningful description of the atmospheric flow regime controlling cloud formation, blocking, uplift, persistence, and propagation over Mount Nuolja."*

Rather than adding generic scalar wind or temperature features, this research evaluates whether compact, physically interpretable **Orographic Flow-Regime Descriptors**, **Causal Cloud Evolution Tendencies**, and **Diffuse Radiative Indicators** represent genuinely novel physical information axes relative to the frozen 37-feature Stage 8.1 champion.

---

## 2. Research Axis 1: Orographic Cloud-Regime Dynamics

### Physical Setting & Scandes Mountain Geometry
- **Location:** Mount Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)
- **Summit Elevation:** $1,169\text{ m a.s.l.}$
- **Pyranometer Site Elevation:** $675\text{ m a.s.l.}$
- **Torneträsk Valley Elevation:** $341\text{ m a.s.l.}$
- **Effective Local Mountain Relief ($h$):** $\approx 828\text{ m}$
- **Scandes Mountain Ridge Axis:** Orientation $\approx 200^\circ \text{ -- } 020^\circ$ (SSW $\leftrightarrow$ NNE)
- **Terrain-Normal Axis ($\theta_{\text{normal}}$):** $\approx 290^\circ \text{ / } 110^\circ$ (WNW $\leftrightarrow$ ESE)

---

### Candidate Quantities Evaluated Under Mandatory 12-Point Novelty Filter (A – L)

#### 1. Scandes Barrier-Normal Wind Component ($U_\perp$)
- **A. Physical Definition:** Projection of the 700 hPa wind vector $(u_{700}, v_{700})$ onto the axis perpendicular to the Scandes mountain ridge: $U_\perp = u_{700} \cdot \sin(200^\circ) + v_{700} \cdot \cos(200^\circ)$.
- **B. Required Input Variables:** MEPS $700\text{ hPa}$ $u$ and $v$ wind components (`u700`, `v700`).
- **C. Exact Causal Timestamp:** Forecast valid time $t_0 + h$ ($h = 1 \dots 24$).
- **D. MEPS/AROME Dataset Existence:** **YES.** Fully present in Stage 8.1 dataset.
- **E. Spatial Resolution:** Single point at Nuolja pyranometer grid cell ($2.5\text{ km}$).
- **F. Required Terrain Scale:** Scandes barrier ridge orientation ($200^\circ$).
- **G. Benchmark Computing (347 origins $\times$ 24 horizons):** 100% computable.
- **H. Genuinely Novel vs. Stage 8.1:** **YES.** Stage 8.1 contains raw Cartesian winds ($u_{700}, v_{700}$). Gradient boosted trees split on orthogonal hyperplanes ($u > c$ or $v > c$), which cannot cleanly reconstruct the rotated directional projection $U_\perp = u \cos\alpha + v \sin\alpha$ without deep interaction terms.
- **I. Closest Analogue:** Stage 8.1 (`u700`, `v700`).
- **J. Target Failure Mode:** Fails to distinguish mountain-perpendicular forced uplift ($U_\perp > 0$) from ridge-parallel along-valley flow ($U_\perp \approx 0$).
- **K. Representation Form:** Continuous scalar ($U_\perp$, $\text{m/s}$).
- **L. Justified for EVEN-Only Test:** **YES.**
- **Classification:** **`A. GENUINELY NOVEL + CAUSALLY FEASIBLE + BENCHMARK FEASIBLE`**

---

#### 2. Non-Dimensional Mountain Froude Number ($Fr = \frac{U_\perp}{N \cdot h}$)
- **A. Physical Definition:** Ratio of kinetic energy to potential energy for air impinging on Mount Nuolja obstacle: $Fr = \frac{U_\perp}{N \cdot h}$, where $N = \sqrt{\frac{g}{\theta_v} \frac{\partial \theta_v}{\partial z}}$ is the dry Brunt–Väisälä static stability frequency.
- **B. Required Input Variables:** $U_\perp$, MEPS 2m temperature/pressure, and MEPS 700 hPa temperature/pressure.
- **C. Exact Causal Timestamp:** Forecast valid time $t_0 + h$.
- **D. MEPS/AROME Dataset Existence:** **YES.** Hydrostatically reconstructible from MEPS profile variables.
- **E. Spatial Resolution:** $2.5\text{ km}$ local grid cell.
- **F. Required Terrain Scale:** Local relief height $h = 828\text{ m}$.
- **G. Benchmark Computing:** 100% computable across all 8,328 forecast samples.
- **H. Genuinely Novel vs. Stage 8.1:** **YES.** Unites wind vector, static atmospheric stability, and terrain geometry into a non-linear non-dimensional flow regime index.
- **I. Closest Analogue:** None (no non-dimensional regime indices exist in Stage 8.1).
- **J. Target Failure Mode:** Flow-regime transitions between flow blocking ($Fr < 1$, trapped valley fog/cloud) and flow over-topping ($Fr \ge 1$, forced lee-side mountain wave cloudiness).
- **K. Representation Form:** Non-dimensional continuous scalar $Fr$ or binary regime class ($\text{Blocked} \le 1.0 < \text{Overtopping}$).
- **L. Justified for EVEN-Only Test:** **YES.**
- **Classification:** **`A. GENUINELY NOVEL + CAUSALLY FEASIBLE + BENCHMARK FEASIBLE`**

---

#### 3. Conditionally Unstable Moist Mountain Froude Number ($Fr_m = \frac{U_\perp}{N_m \cdot h}$)
- **A. Physical Definition:** Moist Froude number incorporating latent heat release during saturation: $N_m^2 = \frac{g}{\theta_v} \left( \frac{\partial \theta_v}{\partial z} - \frac{L_v}{c_p T} \frac{\partial q_s}{\partial z} \right)$.
- **B. Required Input Variables:** $U_\perp$, MEPS temperature, relative humidity, and pressure profiles.
- **C. Exact Causal Timestamp:** Forecast valid time $t_0 + h$.
- **D. MEPS/AROME Dataset Existence:** **YES.**
- **E–G. Resolution, Scale, Computing:** 100% benchmark feasible.
- **H. Genuinely Novel vs. Stage 8.1:** **YES.** Captures reduction in static stability during moisture-saturated orographic flow.
- **I. Closest Analogue:** Stage 8.1 `fc_relative_humidity_2m`.
- **J. Target Failure Mode:** Moist convective cloud formation over Nuolja slopes when dry $Fr < 1$ but moist $Fr_m \ge 1$.
- **K–L. Form & Testing:** Continuous scalar, justified for EVEN test.
- **Classification:** **`A. GENUINELY NOVEL + CAUSALLY FEASIBLE + BENCHMARK FEASIBLE`**

---

#### 4. Orographic Kinematic Uplift Rate ($w_{\text{oro}} = U_\perp \cdot \left| \nabla z_{\text{terrain}} \right|$)
- **A. Physical Definition:** Forced vertical velocity at terrain surface: $w_{\text{oro}} = u \frac{\partial z}{\partial x} + v \frac{\partial z}{\partial y}$.
- **B. Required Input Variables:** $u_{700}, v_{700}$ and high-resolution DEM terrain gradients ($\frac{\partial z}{\partial x}, \frac{\partial z}{\partial y}$).
- **C. Exact Causal Timestamp:** Forecast valid time $t_0 + h$.
- **D. MEPS/AROME Dataset Existence:** **YES.**
- **E–G. Resolution, Scale, Computing:** 100% benchmark feasible.
- **H. Genuinely Novel vs. Stage 8.1:** **YES.** Directly couples terrain slope vector with 3D wind field to compute forced adiabatic cooling and moisture condensation rate ($\text{g/m}^3/\text{s}$).
- **I. Closest Analogue:** Stage 7.5 (terrain horizon elevation angle).
- **J. Target Failure Mode:** Slope forced condensation vs clear-sky downslope Föhn subsidence.
- **Classification:** **`A. GENUINELY NOVEL + CAUSALLY FEASIBLE + BENCHMARK FEASIBLE`**

---

#### 5. Low-Level Vector Wind Shear ($\Delta \vec{V}_{\text{shear}} = \left| \vec{V}_{700} - \vec{V}_{10m} \right|$)
- **A. Physical Definition:** Magnitude of vector wind shear between $700\text{ hPa}$ ridge top and $10\text{ m}$ surface level: $\sqrt{(u_{700} - u_{10m})^2 + (v_{700} - v_{10m})^2}$.
- **B. Required Input Variables:** `u700`, `v700`, `fc_wind_speed_10m`.
- **H. Genuinely Novel vs. Stage 8.1:** **PARTIALLY.** Tree interactions between `u700`, `v700`, and `fc_wind_speed_10m` can approximate magnitude difference.
- **Classification:** **`B. SCIENTIFICALLY INTERESTING BUT NOT SUFFICIENTLY NOVEL`**

---

## 3. Research Axis 2: Cloud Evolution & Growth/Decay Dynamics

### 1. Causal Inter-Run MEPS Cloud Condensate Tendency ($\Delta \text{LWP}_{\text{run}}$)
- **A. Physical Definition:** Difference in predicted liquid water path for matching valid time $t$ between the $D-0$ 00:00 UTC MEPS issuance and the prior $D-1$ 18:00 UTC MEPS issuance: $\Delta \text{LWP}_{\text{run}}(t) = \text{LWP}_{D-0}(t) - \text{LWP}_{D-1}(t)$.
- **B. Required Input Variables:** `lwp_latest` from consecutive MEPS runs.
- **C. Exact Causal Timestamp:** Available prior to morning daytime hours.
- **D. MEPS Dataset Existence:** **YES.**
- **H. Genuinely Novel vs. Stage 8.1:** **YES.** Captures the NWP physics engine's cloud build-up or dissipation rate between consecutive model issuances prior to $t_0$.
- **I. Closest Analogue:** Stage 8.5 (deterministic forecast revisions).
- **J. Target Failure Mode:** Model cloud generation/decay dynamics.
- **Classification:** **`A. GENUINELY NOVEL + CAUSALLY FEASIBLE + BENCHMARK FEASIBLE`**

---

### 2. Pre-$t_0$ Observational Transmissivity Rate ($\frac{d k_t}{dt}$)
- **A. Physical Definition:** Rate of change of observed clear-sky transmissivity in the 3 hours prior to $t_0$.
- **C. Causal & Operational Limitation:** **FAILS CAUSALLY.** At $t_0 = 00:00\text{ UTC}$ in sub-Arctic Lapland, pre-$t_0$ hours ($21:00 \dots 00:00\text{ UTC}$) are dark throughout spring, autumn, and winter, yielding zero solar radiation observations.
- **Classification:** **`C. NOVEL BUT OPERATIONALLY INFEASIBLE`**

---

## 4. Research Axis 3: Diffuse & Broken-Cloud Radiative Regime

### 1. Non-Linear Broken-Cloud Diffuse Enhancement Index ($I_{\text{diffuse}}$)
- **A. Physical Definition:** Non-linear cloud-edge perimeter proxy: $I_{\text{diffuse}} = \text{cloud\_frac} \times (1 - \text{cloud\_frac}) \times \text{clearsky\_ghi}$.
- **H. Genuinely Novel vs. Stage 8.1:** **NO.** Deep decision tree splits on existing features `cloud_frac` and `clearsky_ghi` can easily capture this non-linear interaction product.
- **Classification:** **`B. SCIENTIFICALLY INTERESTING BUT NOT SUFFICIENTLY NOVEL`**

---

## 5. Comprehensive Classification Summary Matrix

| Research Axis | Candidate Feature / Operator | Novelty vs Stage 8.1 | Causal & Benchmark Feasible? | Final Governance Classification |
| :--- | :--- | :---: | :---: | :---: |
| **Axis 1: Orographic** | **Scandes Barrier-Normal Wind ($U_\perp$)** | **HIGH** | **YES** | **A. NOVEL + FEASIBLE** |
| **Axis 1: Orographic** | **Mountain Froude Number ($Fr = \frac{U_\perp}{N h}$)** | **HIGH** | **YES** | **A. NOVEL + FEASIBLE** |
| **Axis 1: Orographic** | **Moist Mountain Froude Number ($Fr_m$)** | **HIGH** | **YES** | **A. NOVEL + FEASIBLE** |
| **Axis 1: Orographic** | **Kinematic Uplift Rate ($w_{\text{oro}}$)** | **HIGH** | **YES** | **A. NOVEL + FEASIBLE** |
| **Axis 1: Orographic** | Vector Wind Shear ($\Delta \vec{V}_{\text{shear}}$) | LOW | YES | **B. NOT SUFFICIENTLY NOVEL** |
| **Axis 2: Evolution** | **Inter-Run Cloud Tendency ($\Delta \text{LWP}_{\text{run}}$)** | **HIGH** | **YES** | **A. NOVEL + FEASIBLE** |
| **Axis 2: Evolution** | Pre-$t_0$ Transmissivity Rate ($\frac{d k_t}{dt}$) | HIGH | **NO** (Darkness) | **C. OPERATIONALLY INFEASIBLE** |
| **Axis 3: Diffuse** | Diffuse Enhancement Index ($I_{\text{diffuse}}$) | LOW | YES | **B. NOT SUFFICIENTLY NOVEL** |
| **Generic** | Generic Wind/Temp Gradients | NONE | YES | **D. ALREADY REPRESENTED** |

---

## 6. Ranked Top Candidates

The three strongest Class A candidates surviving all novelty and feasibility filters are:

1. **Rank 1: Scandes Barrier-Normal Wind Component ($U_\perp$) & Mountain Froude Number ($Fr$)**
   - *Rationale:* Directly resolves Scandes mountain flow-regime control (flow blocking vs over-topping) using hydrostatically derived stability $N$ and terrain-normal 700 hPa wind. Fully novel relative to Stage 8.1 Cartesian winds (`u700`, `v700`).
2. **Rank 2: Orographic Kinematic Uplift Rate ($w_{\text{oro}}$)**
   - *Rationale:* Couples DEM slope vectors with 3D wind fields to compute forced adiabatic cooling and moisture condensation rates along Mount Nuolja slopes.
3. **Rank 3: Inter-Run MEPS Cloud Condensate Tendency ($\Delta \text{LWP}_{\text{run}}$)**
   - *Rationale:* Captures the NWP physics engine cloud build-up / dissipation rate between consecutive causal MEPS model runs prior to $t_0$.

---

## Final Governance Statement & Recommendation

- **Fresh Research Round Completed.**
- **Three Class A candidates have demonstrated physical novelty, causal availability, and benchmark feasibility.**
- **NO EXPERIMENT IS AUTHORIZED BY THIS RESEARCH TASK.**
- **ODD dataset remains 100% untouched.**
- **Stage 8.1 37-feature HGB model remains operational champion (ODD daytime nMAE 28.0688%).**
- **No model changes, master handoff changes, or route registry changes.**
