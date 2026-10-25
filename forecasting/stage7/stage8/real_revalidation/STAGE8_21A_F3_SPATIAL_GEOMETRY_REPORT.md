# POLARIS STAGE 8.21A — PART A: F3 SPATIAL GEOMETRY RESOLUTION REPORT

## 1. Benchmark Geometry & Target Location

- **Station Target:** Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, station elevation $\approx 702\text{ m}$ MSL)
- **MEPS Horizontal Grid Resolution:** $\Delta x = \Delta y = 2.5\text{ km}$
- **Nearest MEPS Grid Cell Index:** $y=760, x=486$
- **Target Observation:** Global Downwelling Shortwave Radiation ($SW_{\text{IN}}$) across 24 forecast horizons ($H1 \dots H24$, valid $00:00 \dots 23:00\text{ UTC}$).

---

## 2. Solar-Ray Geometry & Horizontal Displacement Across Heights

Horizontal ray displacement equation:
$$r(h, t) = h \cdot \tan(\theta_z(t))$$
where $h$ is geometric height above ground level (AGL) and $\theta_z(t)$ is solar zenith angle at valid forecast time $t$.

### Candidate Grid Window Evaluation Table

| Window Size | Grid Points | Cardinal Radius ($R_{\text{card}}$) | Corner Radius ($R_{\text{corner}}$) | Total Physical Span | Max Cloud $h$ at $\theta_z=80^\circ$ | Max Cloud $h$ at $\theta_z=85^\circ$ | Status for $85^\circ, 5\text{ km}$ Cloud |
|---|---|---|---|---|---|---|---|
| **$25 \times 25$** | $625$ | **$30.0\text{ km}$** | $42.43\text{ km}$ | $60.0\text{ km} \times 60.0\text{ km}$ | $5.29\text{ km}$ | $2.62\text{ km}$ | **INSUFFICIENT** |
| **$31 \times 31$** | $961$ | **$37.5\text{ km}$** | $53.03\text{ km}$ | $75.0\text{ km} \times 75.0\text{ km}$ | $6.61\text{ km}$ | $3.28\text{ km}$ | **INSUFFICIENT** |
| **$35 \times 35$** | $1,225$ | **$42.5\text{ km}$** | $60.10\text{ km}$ | $85.0\text{ km} \times 85.0\text{ km}$ | $7.49\text{ km}$ | $3.72\text{ km}$ | **INSUFFICIENT** (Cardinal) |
| **$41 \times 41$** | $1,681$ | **$50.0\text{ km}$** | $70.71\text{ km}$ | $100.0\text{ km} \times 100.0\text{ km}$ | $8.82\text{ km}$ | $4.37\text{ km}$ | **INSUFFICIENT** (Cardinal) |
| **$47 \times 47$** | **$2,209$** | **$57.5\text{ km}$** | **$81.32\text{ km}$** | **$115.0\text{ km} \times 115.0\text{ km}$** | **$10.14\text{ km}$** | **$5.03\text{ km}$** | **SUFFICIENT** |
| **$51 \times 51$** | $2,601$ | **$62.5\text{ km}$** | $88.39\text{ km}$ | $125.0\text{ km} \times 125.0\text{ km}$ | $11.02\text{ km}$ | $5.47\text{ km}$ | **SUFFICIENT** |

---

## 3. Azimuth, Grid Alignment & Directional Subsetting

- Solar azimuth $\phi_z(t)$ at Nuolja sweeps from East ($\approx 90^\circ$) through South ($\approx 180^\circ$) to West ($\approx 270^\circ$).
- Solar ray displacement vector:
  $$\Delta x = r(h, t) \sin\phi_z(t), \quad \Delta y = r(h, t) \cos\phi_z(t)$$
- Square bounding box vs Directional Subsetting: A square $47 \times 47$ grid window guarantees complete spatial coverage for all daytime solar azimuth angles up to $\theta_z = 85^\circ$ for cloud layers up to $h = 5.0\text{ km}$ AGL.

---

## 4. Distinction from Stage 7.5 Terrain Model

- **Stage 7.5 (Existing):** Evaluates 1D angular terrain horizon elevation obstruction angle at pyranometer location ($1\text{D}$ 360° DEM lookup).
- **Stage 8.21A (Proposed):** Evaluates 3D solar vector ray intersection with 3D DEM terrain surface AND 3D atmospheric MEPS hydrometeor condensate volumes ($q_l, q_i$).
- **Novelty Verification:** Genuinely NEW 3D spatial atmospheric ray operator.

---

## 5. F3 Gate Verdict & Resolution

- **Verdict:** **`CONDITIONAL — EXPANSION REQUIRED`**
- **Reasoning:** A $25 \times 25$ window ($30\text{ km}$ cardinal radius) is sufficient for zenith angles $\le 80^\circ$ or low clouds ($h \le 2.6\text{ km}$). To cover high zenith ($\theta_z > 80^\circ$) and mid/high cloud layers ($h > 3.0\text{ km}$), an expanded extraction window of **$47 \times 47$ grid points ($115.0\text{ km} \times 115.0\text{ km}$ physical span)** is required.
