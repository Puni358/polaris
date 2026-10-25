# POLARIS STAGE 8.21A — FEASIBILITY AUDIT TARGETED CORRECTION REPORT

## 1. Executive Summary & Decision Corrections

- **Route Identifier:** STAGE 8.21A (3D Solar Slant-Path Hydrometeor Geometry)
- **Original Classification:** `A. FEASIBILITY VERIFIED — EXPERIMENT MAY BE DESIGNED`
- **Corrected Classification:** **`B. CONDITIONAL FEASIBILITY — SPECIFIC DATA/PHYSICS GAP MUST BE RESOLVED`**
- **Governance Verification:**
  - `FINAL_EXPERIMENT_RUN` = **FALSE**
  - `FINAL_MODEL_TRAINING` = **FALSE**
  - `FINAL_ODD_ACCESS` = **FALSE**
  - `OPERATIONAL_CHAMPION_CHANGED` = **FALSE**
  - `MASTER_HANDOFF_CHANGED` = **FALSE**
  - `ROUTE_REGISTRY_CHANGED` = **FALSE**

### Summary of Audit Re-Evaluations

| Feasibility Gate | Original Status | Corrected Status | Reason for Correction |
|---|---|---|---|
| **F3: Spatial Window Coverage** | `PASS` | **`CONDITIONAL`** | A $25 \times 25$ window provides a $30\text{ km}$ cardinal radius ($42.4\text{ km}$ diagonal). At $85^\circ$ zenith and $5\text{ km}$ cloud height, solar ray displacement is $57.15\text{ km}$, exceeding the $25 \times 25$ window. An expanded $47 \times 47$ window ($115\text{ km}$ span) is required. |
| **F4: Pressure-to-Height Geometry** | `PASS` | **`CONDITIONAL`** | MEPS pressure level dataset (`meps_det_pl`) provides pressure $P$, but geometric height $z$ is not stored directly on levels. Height must be defensibly reconstructed via hydrostatic integration of temperature $T$ and surface pressure $P_{\text{sfc}}$. |
| **F6: Optical Proxy Defensibility** | `CONDITIONAL` | **`CONDITIONAL`** | $q_l$ and $q_i$ are directly observed, but cloud droplet/ice effective radii $r_e$ are not stored and must be parameterized ($r_{e,\text{liq}}=10\,\mu\text{m}, r_{e,\text{ice}}=30\,\mu\text{m}$). Classified as **Physically Parameterized Attenuation Feasibility**. |

---

## 2. Section 1 — Exact Spatial Window Geometry Audit

### A. MEPS Grid Window Dimensions
- **Grid Spacing ($\Delta x, \Delta y$):** $2.5\text{ km}$
- **Proposed $25 \times 25$ Grid Window:**
  - Number of grid points: $25 \times 25$
  - Number of grid intervals: $24$
  - **Total Physical Span:** $24 \times 2.5\text{ km} = 60.0\text{ km} \times 60.0\text{ km}$
  - **Maximum Cardinal Radius (from Nuolja center):** $12 \text{ intervals} \times 2.5\text{ km} = 30.0\text{ km}$
  - **Maximum Diagonal Radius:** $\sqrt{30.0^2 + 30.0^2} = 42.43\text{ km}$

### B. Solar Zenith Angle & Ray Horizontal Displacement Matrix
Horizontal ray displacement $\Delta r(h, \theta_z) = h \cdot \tan(\theta_z)$:

| Cloud Height ($h$) | $\theta_z = 60^\circ$ | $\theta_z = 70^\circ$ | $\theta_z = 75^\circ$ | $\theta_z = 80^\circ$ | $\theta_z = 85^\circ$ | Fits $25 \times 25$ Cardinal ($30\text{ km}$)? |
|---|---|---|---|---|---|---|
| **1.0 km** | $1.73\text{ km}$ | $2.75\text{ km}$ | $3.73\text{ km}$ | $5.67\text{ km}$ | $11.43\text{ km}$ | **YES** for all zeniths |
| **2.0 km** | $3.46\text{ km}$ | $5.49\text{ km}$ | $7.46\text{ km}$ | $11.34\text{ km}$ | $22.86\text{ km}$ | **YES** for all zeniths |
| **3.0 km** | $5.20\text{ km}$ | $8.24\text{ km}$ | $11.20\text{ km}$ | $17.01\text{ km}$ | **$34.29\text{ km}$** | **NO** at $85^\circ$ |
| **5.0 km** | $8.66\text{ km}$ | $13.74\text{ km}$ | $18.66\text{ km}$ | **$28.36\text{ km}$** | **$57.15\text{ km}$** | **NO** at $85^\circ$ |
| **8.0 km** | $13.86\text{ km}$ | $21.98\text{ km}$ | $29.86\text{ km}$ | **$45.37\text{ km}$** | **$91.44\text{ km}$** | **NO** at $80^\circ, 85^\circ$ |
| **10.0 km** | $17.32\text{ km}$ | $27.47\text{ km}$ | **$37.32\text{ km}$** | **$56.71\text{ km}$** | **$114.30\text{ km}$** | **NO** at $\ge 75^\circ$ |
| **12.0 km** | $20.78\text{ km}$ | **$32.97\text{ km}$** | **$44.78\text{ km}$** | **$68.06\text{ km}$** | **$137.16\text{ km}$** | **NO** at $\ge 70^\circ$ |

### C. Minimum Required Window for $85^\circ$ Zenith at $5\text{ km}$ Cloud Height
- **Required Displacement:** $57.15\text{ km}$
- **Required Half-Width Grid Cells:** $\lceil 57.15 / 2.5 \rceil = 23\text{ cells}$
- **Minimum Grid Window:** $2 \times 23 + 1 = \mathbf{47 \times 47\text{ grid points}}$
- **Minimum Physical Span:** $(47-1) \times 2.5\text{ km} = \mathbf{115.0\text{ km} \times 115.0\text{ km}}$
- **Minimum Cardinal Radius:** $57.5\text{ km}$

---

## 3. Section 2 — Pressure-to-Height Geometry Audit

- **MEPS Archive Metadata:** Dataset `meps_det_pl` provides pressure levels ($50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000\text{ hPa}$) and surface pressure $P_{\text{sfc}}$. Geometric height $z$ is not stored as an explicit 3D level variable.
- **Defensible Height Reconstruction Method:**
  Geometric height $z(p)$ above ground must be reconstructed using the hypsometric equation:
  $$\Delta z = \frac{R_d \bar{T}_v}{g} \ln\left(\frac{P_1}{P_2}\right)$$
  integrating upward from surface pressure $P_{\text{sfc}}$ with virtual temperature $T_v = T (1 + 0.61 q_v)$.
- **Status:** **FEASIBLE RECONSTRUCTION (CONDITIONAL on implementing hydrostatic coordinate conversion)**.

---

## 4. Section 3 — Cloud-Layer Intersection & Interpolation

- **Horizontal Interpolation:** 2D bilinear spatial interpolation between neighboring 4 grid points.
- **Vertical Interpolation:** 1D log-linear pressure interpolation between adjacent pressure levels.
- **Below-Ground Masking:** Grid levels where pressure $P > P_{\text{sfc}}$ (e.g. $925, 1000\text{ hPa}$ at Nuolja $908.6\text{ hPa}$) are masked out.
- **Profile Resolution:** 13 pressure levels provide sufficient vertical resolution in the troposphere to resolve mid- and high-level cloud layers.

---

## 5. Section 4 — Terrain Intersection Distinction

- **Stage 7.5 (Existing):** Evaluates 1D angular terrain horizon obstruction angle at the pyranometer station location using a Digital Elevation Model (DEM).
- **Stage 8.21A (Proposed):** Computes a 3D solar vector ray tracing that tests for spatial intersection with both the 3D DEM terrain surface AND 3D atmospheric MEPS hydrometeor condensate volumes ($q_l, q_i$).
- **Distinction:** Stage 8.21A contains a **genuinely NEW 3D spatial atmospheric ray operator**.

---

## 6. Section 5 — Optical Proxy Classification & Clarification

- **MEPS Variable Audit:** `meps_det_pl` contains $q_l$ and $q_i$. Effective droplet radius $r_e$, cloud optical depth $\tau$, and extinction coefficients are NOT stored in the pressure-level archive.
- **Classification:** **B. PHYSICALLY PARAMETERIZED ATTENUATION FEASIBILITY**.
- **Parameterization Assumptions:** $r_{e,\text{liq}} = 10\,\mu\text{m}$, $r_{e,\text{ice}} = 30\,\mu\text{m}$. These are explicit modeling assumptions, NOT directly observed MEPS fields.
- **F6 Status:** Remains **`CONDITIONAL`**.

---

## 7. Section 6 — Direct vs Global Shortwave Semantics

- **Target Observation:** Nuolja pyranometer measures **global downwelling shortwave radiation ($SW_{\text{IN}}$)** (direct beam + diffuse horizontal).
- **Proposed 3D Ray Operator:** Calculates direct-beam extinction optical thickness $\tau_{\text{slant}} = \int \beta_{\text{ext}}(s) \, ds$ and direct transmittance $T_{\text{dir}} = \exp(-\tau_{\text{slant}})$.
- **Radiative Transfer Semantics:** The operator is a **physical proxy for direct beam attenuation**, not a complete multi-stream diffuse scattering radiative transfer model.

---

## 8. Section 7 — Causality Recheck

- **Benchmark Origin Origin ($t_0$):** $00:00\text{ UTC}$ Day $D$
- **Issuance Time:** $D-1$ $18:00\text{ UTC}$
- **Publication Time:** $D-1$ $\sim 21:30\text{ UTC}$
- **Causal Lead Margin:** $+2.5\text{ hours}$ before $t_0$
- **Causal Coverage:** 347 / 347 origins ($100.0\%$), 8,328 / 8,328 tuples ($100.0\%$).

---

## 9. Section 8 — Computational Feasibility Estimates

- **$25 \times 25$ Grid Window Payload:** $\sim 1.56\text{ MB}$ per origin $\implies \mathbf{516.1\text{ MB}}$ total across 347 origins (**REPRODUCIBLE ESTIMATE**).
- **Expanded $47 \times 47$ Grid Window Payload:** $\sim 5.51\text{ MB}$ per origin $\implies \mathbf{1.82\text{ GB}}$ total across 347 origins (**REPRODUCIBLE ESTIMATE**).
- **Extraction Strategy:** Targeted OPeNDAP server-side array slicing via THREDDS. Highly operationally tractable ($<20\text{ min}$ download).

---

## 10. Section 9 & 10 — Final Audit Summary & Governance

```
ORIGINAL_DECISION = A. FEASIBILITY VERIFIED — EXPERIMENT MAY BE DESIGNED
CORRECTED_DECISION = B. CONDITIONAL FEASIBILITY — SPECIFIC DATA/PHYSICS GAP MUST BE RESOLVED

F3_ORIGINAL = PASS
F3_CORRECTED = CONDITIONAL (25x25 window provides 30km cardinal radius; 85° zenith at 5km cloud height requires 57.15km displacement -> 47x47 window needed)

F4_ORIGINAL = PASS
F4_CORRECTED = CONDITIONAL (meps_det_pl provides pressure levels; height z must be defensibly reconstructed via hydrostatic equation)

F6_ORIGINAL = CONDITIONAL
F6_CORRECTED = CONDITIONAL (q_l/q_i directly observed, but droplet effective radii r_e must be parameterized)

FINAL_EXPERIMENT_RUN = FALSE
FINAL_MODEL_TRAINING = FALSE
FINAL_ODD_ACCESS = FALSE
OPERATIONAL_CHAMPION_CHANGED = FALSE
MASTER_HANDOFF_CHANGED = FALSE
ROUTE_REGISTRY_CHANGED = FALSE
```
