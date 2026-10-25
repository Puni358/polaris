# POLARIS STAGE 8 — OROGRAPHIC CANDIDATE PRE-EXPERIMENT AUDIT REPORT

> [!IMPORTANT]
> **GOVERNANCE STATUS: PRE-EXPERIMENT SCIENTIFIC AUDIT ONLY**  
> - **No EVEN cross-validation experiment has been executed.**  
> - **ODD benchmark dataset remains 100% untouched.**  
> - **Stage 8.1 37-feature HGB model remains the frozen operational champion (ODD daytime nMAE 28.0688%).**  
> - **No modifications to POLARIS_MASTER_HANDOFF.md or POLARIS_STAGE8_ROUTE_REGISTRY.**

---

## 1. Executive Summary

This report performs a scientific pre-experiment audit of the candidate information axes identified in the fresh research round:
1. **Scandes Barrier-Normal Wind ($U_\perp$) & Mountain Froude Number ($Fr$)**
2. **Kinematic Orographic Forced Uplift Rate ($w_{\text{kin}}$)**
3. **Causal Inter-Run MEPS Cloud Condensate Tendency ($\Delta \text{LWP}_{\text{run}}$)**

The objective is to verify mathematical definitions, causal lineage, physical defensibility, and true information novelty relative to the frozen 37-feature Stage 8.1 champion before any experiment is pre-registered.

---

## 2. Section 1: Scientific Audit of Orographic Flow Regime ($U_\perp$ & $Fr$)

### 1. Barrier Orientation & Inflow Axis
- **Scandes Mountain Ridge Axis:** Orientation $= 200^\circ \text{ -- } 020^\circ$ (SSW $\leftrightarrow$ NNE).
- **Terrain-Normal Axis ($\theta_{\text{normal}}$):** Direction from North $= \mathbf{290^\circ}$ (WNW $\leftrightarrow$ ESE).

### 2. Physical Defensibility of $290^\circ$ Axis
- **Finding:** Mount Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}$) is situated on the southern shore of Lake Torneträsk ($341\text{ m a.s.l.}$). The Lake Torneträsk valley aligns along the WNW $\to$ ESE axis ($290^\circ \to 110^\circ$).
- **Scientific Defense:** The $290^\circ$ axis is physically grounded because it aligns **both** with the regional Scandes barrier-normal axis ($290^\circ$) AND the local Torneträsk valley inflow funnel. It is not an arbitrary single-axis approximation.

### 3. MEPS Steering Wind Level
- **Level Selection:** **700 hPa level** ($\approx 2,900 \dots 3,100\text{ m a.s.l.}$).
- **Justification:** 700 hPa is located directly above the main Scandes ridge tops ($\sim 1,500 \dots 2,100\text{ m}$), capturing the un-blocked synoptic steering flow that impenges on the mountain barrier. 10m surface winds are heavily distorted by boundary-layer canopy friction and local valley turns.

### 4. Mathematical Definition of $U_\perp$
- Unit vector along the $290^\circ$ inflow axis (heading $110^\circ$ ESE):
  $$\hat{n} = (\sin 290^\circ, \cos 290^\circ) = (-0.9397, +0.3420)$$
- **Barrier-Normal Wind Component Formula:**
  $$\mathbf{U_\perp = -0.9397 \cdot u_{700} + 0.3420 \cdot v_{700}}$$
  *(Where $u_{700}$ is eastward wind, $v_{700}$ is northward wind).*
  - $U_\perp > 0 \implies$ Maritime inflow from Norwegian Sea (forced orographic uplift).
  - $U_\perp < 0 \implies$ Downslope lee-side Föhn flow (subsidence and cloud dissipation).

### 5. Brunt–Väisälä Static Stability Frequency ($N$)
- **Formula:** $N = \sqrt{\frac{g}{\theta_v} \frac{\partial \theta_v}{\partial z}}$ ($\text{s}^{-1}$).
- **Virtual Potential Temperature ($\theta_v$):** $\theta_v = T \cdot \left( \frac{1000}{P} \right)^{0.286} \cdot (1 + 0.61 q)$, incorporating low-level moisture buoyancy.

### 6. Layer for $N$ Calculation
- Spans from **surface ($P_{\text{sfc}}$, $2\text{ m}$)** to **700 hPa ($z \approx 3,000\text{ m}$)**, representing the complete valley-to-free-troposphere atmospheric stability layer.

### 7. Mountain Relief Height ($h$) Definition
- **Definition:** Effective mountain relief height:
  $$\mathbf{h = z_{\text{summit}} - z_{\text{valley}} = 1,169\text{ m} - 341\text{ m} = 828\text{ m}}$$
- **Justification:** Represents the actual vertical obstacle height that air parcels must ascend to cross Mount Nuolja from Torneträsk valley.

### 8. Mountain Froude Number ($Fr$) Formula
- **Formula:**
  $$\mathbf{Fr = \frac{U_\perp}{N \cdot h}}$$
- **Physical Interpretation:**
  - $Fr < 1.0 \implies$ **Flow Blocking Regime:** Air lacks kinetic energy to cross Mount Nuolja; flow stagnates in Torneträsk valley, forming trapped low-level stratocumulus/fog.
  - $Fr \ge 1.0 \implies$ **Over-Topping Regime:** Flow easily over-tops the ridge, creating lee-side mountain wave clouds and cap cloud dynamics.

### 9. Novelty vs. Stage 8.1 (`u700`, `v700`) & Stage 7.5 Terrain
- **Stage 8.1 (`u700`, `v700`):** Raw Cartesian wind components relative to East/North axes.
- **Stage 7.5 Terrain:** Static DEM horizon elevation obstruction angles (topography).
- **$U_\perp$ & $Fr$ Novelty:** Represents **FLOW RELATIVE TO THE MOUNTAIN BARRIER**. It combines wind vector, static stability, and mountain geometry into a non-linear physical regime descriptor that decision trees cannot construct from raw Cartesian inputs.

---

## 3. Section 2: Scientific Audit of Orographic Uplift Proxy ($w_{\text{kin}}$)

- **Formula:** $w_{\text{kin}} = U_\perp \cdot \left| \nabla z_{\text{terrain}} \right|$, using Nuolja DEM slope ($\approx 0.15\text{ m/m}$).
- **Nomenclature Audit:** Must **NOT** be called "actual vertical velocity" ($w$ or $\omega$). Real $w$ requires non-hydrostatic pressure gradient and buoyancy terms.
- **Correct Scientific Definition:** **Kinematic Orographic Forced Ascent Proxy ($w_{\text{kin}}$)** ($\text{m/s}$).
- **Physical Value:** Directly quantifies the rate of forced adiabatic cooling and moisture condensation along Mount Nuolja's slopes.

---

## 4. Section 3: Timeline & Causal Audit of Inter-Run Cloud Tendencies ($\Delta \text{LWP}_{\text{run}}$)

### Timeline Audit across Forecast Issuances:
- **Run A:** $D-1$ $12:00\text{ UTC}$ MEPS run $\to$ published at $\sim 15:30\text{ UTC}$ ($D-1$).
- **Run B:** $D-1$ $18:00\text{ UTC}$ MEPS run $\to$ published at $\sim 21:30\text{ UTC}$ ($D-1$).
- **Run C:** $D-0$ $00:00\text{ UTC}$ MEPS run $\to$ published at $\sim 02:30\text{ UTC}$ ($D-0$).
- **Forecast Origin ($t_0$):** $D-0$ $00:00\text{ UTC}$.

> [!CAUTION]
> **CAUSALITY FIREWALL AUDIT:**  
> Using $(D-0 \text{ 00:00z} - D-1 \text{ 18:00z})$ at $t_0 = 00:00\text{ UTC}$ **VIOLATES CAUSALITY** because the $D-0$ 00:00z run is published at $02:30\text{ UTC}$ ($02:30 > 00:00$).  
> To remain 100% causal before $t_0 = 00:00\text{ UTC}$, the inter-run tendency MUST use:
> $$\Delta \text{LWP}_{\text{run}} = \text{LWP}_{D-1 \text{ 18:00z}}(t) - \text{LWP}_{D-1 \text{ 12:00z}}(t)$$
> Both runs are published prior to $21:30\text{ UTC}$ ($D-1$), well before $t_0 = 00:00\text{ UTC}$.

### Novelty vs. Stage 8.5 (Forecast Revisions):
- Stage 8.5 evaluated inter-run revisions for scalar $SW\_IN$ predictions and failed validation because inter-run deltas were dominated by cycle-to-cycle numerical noise.
- **Verdict:** Classify as **`B. USEFUL BUT MOSTLY REPACKAGED EXISTING INFORMATION`**.

---

## 5. Section 4: Comprehensive Classification Summary Matrix

| Candidate Feature / Operator | Causal Status | Novelty vs Stage 8.1 & Past Routes | Final Classification Verdict |
| :--- | :---: | :---: | :---: |
| **1. Barrier-Normal Wind ($U_\perp$) & Froude Number ($Fr$)** | **100% PASS** | **GENUINELY NOVEL** (Flow-relative-to-barrier representation) | **A. GENUINELY NOVEL + CAUSAL + BENCHMARK FEASIBLE** |
| **2. Kinematic Orographic Uplift Proxy ($w_{\text{kin}}$)** | **100% PASS** | **GENUINELY NOVEL** (Forced slope ascent proxy) | **A. GENUINELY NOVEL + CAUSAL + BENCHMARK FEASIBLE** |
| **3. Causal Inter-Run LWP Tendency ($\Delta \text{LWP}_{18z-12z}$)** | **PASS** | **REPACKAGED** (Overlaps Stage 8.5 forecast revisions) | **B. USEFUL BUT MOSTLY REPACKAGED EXISTING INFO** |
| **4. Non-Causal Inter-Run LWP Tendency ($\Delta \text{LWP}_{00z-18z}$)** | **FAIL** ($02:30 > t_0$) | N/A | **C. NOVEL BUT CAUSALLY INFEASIBLE** |
| **5. Vector Wind Shear ($\Delta \vec{V}_{\text{shear}}$)** | **PASS** | **REPACKAGED** (Approximated by tree splits on $u_{700}, v_{700}, v_{10m}$) | **B. USEFUL BUT MOSTLY REPACKAGED EXISTING INFO** |

---

## 6. Recommendation for Governed Experiment Pre-Registration

The scientific audit supports **ONE CANDIDATE PACKAGE** for governed pre-registration:

$$\mathbf{\text{RECOMMENDED PACKAGE: OROGRAPHIC FLOW REGIME (Candidate 1: } U_\perp \text{ and } Fr\text{)}}$$

### Pre-Registration Feature Definitions:
1. `ctx_u_perp`: $U_\perp = -0.9397 \cdot u_{700} + 0.3420 \cdot v_{700}$ (barrier-normal inflow at $290^\circ$).
2. `ctx_mountain_froude`: $Fr = \frac{U_\perp}{N \cdot h}$, using hydrostatically derived $N$ ($P_{\text{sfc}} \to 700\text{ hPa}$) and $h = 828\text{ m}$.

---

## Final Governance Statement

- **Pre-Experiment Scientific Audit Completed.**
- **One Candidate Package ($U_\perp$ & $Fr$) PASSED scientific audit.**
- **No EVEN cross-validation experiment has been executed yet.**
- **ODD benchmark dataset remains 100% untouched.**
- **Stage 8.1 37-feature model remains operational champion (ODD daytime nMAE 28.0688%).**
- **No model changes, master handoff changes, or route registry changes.**
