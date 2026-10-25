# STAGE 8.10A — MEPS VERTICAL-COORDINATE & SURFACE TRUNCATION AUDIT

**Project:** POLARIS SIH Forecasting  
**Stage:** STAGE 8.10A TRUE MEPS MODEL-LEVEL CLOUD CONDENSATE AUDIT  
**Target Location:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, Elevation $\approx 702\text{ m ASL}$)  
**Date:** September 12, 2026  

---

## 1. MEPS Vertical Coordinate System Overview

The MetCoOp Ensemble Prediction System (MEPS), based on the HARMONIE-AROME atmospheric model, uses a **hybrid Arakawa $\eta$-coordinate (sigma-pressure) vertical grid** consisting of **65 model levels** indexed from $k = 0$ to $k = 64$.

* **Level Indexing Convention:**
  * $k = 0$: Top of the model domain ($\approx 10\text{ hPa} \approx 30,000\text{ m ASL}$).
  * $k = 64$: Lowest model layer closest to the Earth's surface ($\approx 12\text{ m}$ above ground level).
* **Hybrid Coordinate Formulation:**
  The full pressure $p(k)$ at model level $k$ is calculated as a function of the local surface pressure $p_{\text{sfc}}$:

  $$p(k) = a_p(k) + b(k) \cdot p_{\text{sfc}}$$

  where:
  - $a_p(k)$ is the hybrid pressure offset coefficient ($\text{Pa}$).
  - $b(k)$ is the non-dimensional sigma weighting coefficient ($0 \le b(k) \le 1$).
  - $p_{\text{sfc}}$ is the instantaneous surface air pressure ($\text{Pa}$) at the target location.

---

## 2. Hybrid Coefficient Distribution ($a_p$ and $b$)

1. **Upper Atmosphere ($k = 0 \dots 15$, Pure Pressure Coordinate):**
   - $b(k) = 0$, $a_p(k) = p_{\text{fixed}}$. Isobaric surfaces independent of terrain surface pressure.
2. **Mid Atmosphere ($k = 16 \dots 40$, Transition Hybrid Coordinate):**
   - Both $a_p(k) > 0$ and $b(k) > 0$. Smooth transition from isobaric to terrain-following coordinates.
3. **Lower Atmosphere ($k = 41 \dots 64$, Terrain-Following Sigma Coordinate):**
   - $a_p(k) \to 0$, $b(k) \to 1$. Model levels follow terrain topography directly.

---

## 3. Surface Truncation Physics at SITES Nuolja

SITES Nuolja is an elevated mountain station ($702\text{ m ASL}$). The mean sea-level pressure ($1013.25\text{ hPa}$) is invalid at Nuolja.

### Local Surface Pressure Profile:
- Average surface pressure at Nuolja ($702\text{ m ASL}$): $p_{\text{sfc, local}} \approx 925\text{ hPa} = 92500\text{ Pa}$.
- MEPS $2.5\text{ km}$ DEM surface elevation at Nuolja grid point: $~675\text{ m ASL}$ ($p_{\text{sfc, model}} \approx 928\text{ hPa}$).

### Sub-Surface Level Contamination Risk:
The 65 model levels in `meps_det_ml` are defined down to a standard sea-level reference ($1013.25\text{ hPa}$).
For a surface pressure of $p_{\text{sfc}} = 928\text{ hPa}$:
- Model levels $k = 52 \dots 64$ have calculated pressures $p(k) > 928\text{ hPa}$.
- These levels lie **physically below the Earth's surface at Nuolja**!

### Mandatory Surface Truncation & Boundary Handling Protocol:
To avoid creating physically impossible below-ground cloud columns:

$$\text{If } p(k) > p_{\text{sfc, local}} \implies q_l(k) = 0, \quad q_i(k) = 0$$

For the lowest valid atmospheric layer intersecting $p_{\text{sfc, local}}$, the layer thickness $\Delta p_{\text{bottom}}$ must be truncated at the surface pressure:

$$\Delta p_{\text{bottom}} = p_{\text{sfc, local}} - p(k_{\text{bottom\_valid}})$$

Any vertical profile summary or column integration that fails to enforce surface truncation will introduce gross unphysical errors by integrating fictitious below-ground cloud condensate.

---

## 4. Layer Mass Weighting & Column Integration

The hydrostatic mass of air per unit area within layer $k$ bounded by half-levels $k-1/2$ and $k+1/2$ is:

$$\Delta m(k) = \frac{\Delta p(k)}{g} = \frac{p(k+1/2) - p(k-1/2)}{g}$$

where $g = 9.80665\text{ m/s}^2$.

The truncated column Liquid Water Path ($LWP$) and Ice Water Path ($IWP$) are computed as:

$$LWP_{\text{truncated}} = \frac{1}{g} \sum_{k=k_{\text{top}}}^{k_{\text{surface}}} q_l(k) \Delta p(k)$$

$$IWP_{\text{truncated}} = \frac{1}{g} \sum_{k=k_{\text{top}}}^{k_{\text{surface}}} q_i(k) \Delta p(k)$$

---

## 5. Summary Verdict on Vertical Coordinates

The hybrid Arakawa coordinate system $p(k) = a_p(k) + b(k) p_{\text{sfc}}$ is **mathematically valid and physically reconstructable**.

However, because Nuolja is an elevated mountain site ($702\text{ m ASL}$), surface pressure truncation at $p_{\text{sfc}} \approx 928\text{ hPa}$ is **mandatory**. Levels $k=52 \dots 64$ must be zero-masked to prevent sub-surface cloud contamination.

