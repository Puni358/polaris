# POLARIS STAGE 8.21A — F3/F4/F6 FEASIBILITY RESOLUTION AUDIT REPORT

## 1. Executive Summary & Gate Resolutions

- **Route Identifier:** STAGE 8.21A (3D Solar Slant-Path Hydrometeor Geometry)
- **Final Route Classification:** **`B. CONDITIONAL FEASIBILITY — SPECIFIC DATA/PHYSICS GAP MUST BE RESOLVED`**
- **Governance Audit Firewall Verification:**
  - `EXPERIMENT_RUN` = **FALSE**
  - `MODEL_TRAINING` = **FALSE**
  - `ODD_ACCESS` = **FALSE**
  - `ODD_PREDICTIONS_CREATED` = **FALSE**
  - `CHAMPION_CHANGED` = **FALSE**
  - `MASTER_HANDOFF_CHANGED` = **FALSE**
  - `ROUTE_REGISTRY_CHANGED` = **FALSE**

---

## 2. Gate Resolution Matrix

| Gate ID | Technical Dimension | Resolution Verdict | Key Findings & Evidence |
|---|---|---|---|
| **F3** | Spatial Geometry & Window | **`CONDITIONAL`** | **CONDITIONAL — EXPANSION REQUIRED.** $25 \times 25$ window ($30\text{ km}$ cardinal radius) covers zeniths $\le 80^\circ$; $\theta_z = 85^\circ$ at $h=5\text{ km}$ requires $57.15\text{ km}$ displacement $\implies$ **$47 \times 47$ grid window ($115.0\text{ km} \times 115.0\text{ km}$ physical span)** is required. |
| **F4** | Vertical Coordinate & Height | **`PASS`** | **PASS.** Hydrostatic pressure-to-height coordinate reconstruction $\Delta z = \frac{R_d \bar{T}_v}{g_0} \ln(P_1/P_2)$ is physically rigorous, verified with MEPS variables ($T, q_v, P, P_{\text{sfc}}$), and demonstrated on real MEPS columns. |
| **F6** | Optical Attenuation Proxy | **`CONDITIONAL`** | **CONDITIONAL — PARAMETERIZED ATTENUATION PROXY.** $q_l, q_i$ are directly observed, but microphysical effective radii ($r_{e,\text{liq}}=10\,\mu\text{m}, r_{e,\text{ice}}=30\,\mu\text{m}$) are parameterized modeling assumptions. Feature models direct-beam extinction proxy, not full diffuse $SW_{\text{IN}}$. |
| **COMP** | Computational Feasibility | **`PASS`** | **PASS.** Expanded $47 \times 47$ window payload for 13 levels, 24 horizons, 4 variables across 347 origins is $\mathbf{3.82\text{ GB}}$, fully operationally tractable via OPeNDAP slicing ($< 25\text{ min}$). |

---

## 3. Computational Feasibility Re-Calculation Summary

- **Extracted Window:** $47 \times 47$ grid points ($2,209$ horizontal columns per horizon)
- **Vertical Levels:** 13 pressure levels ($50 \dots 1000\text{ hPa}$)
- **Forecast Horizons:** 24 horizons per origin ($H1 \dots H24$)
- **Required Variables:** $q_l, q_i, T, q_v$ ($4$ float32 variables)
- **Per-Origin Data Payload:** $\sim 11.02\text{ MB}$
- **Total Batch Payload (347 Origins):** $\mathbf{3.82\text{ GB}}$ (**REPRODUCIBLE ESTIMATE**)
- **Storage & Acquisition Strategy:** Targeted server-side OPeNDAP slicing via THREDDS. Highly tractable.

---

## 4. Final Route Classification & Next Steps

Stage 8.21A is classified as **`B. CONDITIONAL FEASIBILITY — SPECIFIC DATA/PHYSICS GAP MUST BE RESOLVED`**.

- **Prerequisites Before Design Phase:**
  1. Preregister extraction using the expanded $47 \times 47$ grid window.
  2. Implement hydrostatic $z(p)$ coordinate reconstruction and below-ground pressure level masking ($P > P_{\text{sfc}}$).
  3. Frame the candidate feature explicitly as a **parameterized direct-beam extinction proxy** $T_{\text{dir}} = \exp(-\tau_{\text{slant}})$.
- **DO NOT** launch model training or ODD evaluation.
