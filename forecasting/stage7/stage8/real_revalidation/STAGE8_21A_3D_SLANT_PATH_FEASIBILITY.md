# POLARIS STAGE 8.21A — 3D SOLAR SLANT-PATH HYDROMETEOR GEOMETRY FEASIBILITY AUDIT

## 1. Executive Summary & Final Feasibility Decision

- **Route Identifier:** STAGE 8.21A
- **Proposed Operator:** 3D Solar Slant-Path Hydrometeor Volume Integration
- **Original Classification:** `A. FEASIBILITY VERIFIED — EXPERIMENT MAY BE DESIGNED`
- **Corrected Classification:** **`B. CONDITIONAL FEASIBILITY — SPECIFIC DATA/PHYSICS GAP MUST BE RESOLVED`**
- **Governance Audit Firewall:**
  - `STAGE8_21A_EXPERIMENT_RUN` = **FALSE**
  - `STAGE8_21A_MODEL_TRAINING` = **FALSE**
  - `STAGE8_21A_ODD_ACCESS` = **FALSE**
  - `OPERATIONAL_CHAMPION_CHANGED` = **FALSE**
  - `MASTER_HANDOFF_CHANGED` = **FALSE**
  - `ROUTE_REGISTRY_CHANGED` = **FALSE**

### Summary Verdict
The proposed Stage 8.21A 3D solar slant-path hydrometeor geometry operator is **CONDITIONALLY FEASIBLE** using the existing MET Norway MEPS archive. The 3D cloud liquid water ($q_l$) and cloud ice ($q_i$) mass fraction fields are available on 13 pressure levels. Following targeted geometry re-auditing:
1. The $25 \times 25$ MEPS grid window provides a cardinal radius of $30.0\text{ km}$. At solar zenith angles $>80^\circ$ and cloud top heights $>3\text{ km}$, ray displacement ($57.15\text{ km}$ at $85^\circ, 5\text{ km}$) exceeds $30\text{ km}$, requiring an expanded $47 \times 47$ grid window ($115.0\text{ km}$ span).
2. Geometric height $z$ is not stored as an explicit level variable in `meps_det_pl` and must be reconstructed via hydrostatic integration of temperature $T$ and surface pressure $P_{\text{sfc}}$.
3. Cloud droplet effective radii ($r_e$) are not directly observed in `pl` and must be parameterized ($r_{e,\text{liq}}=10\,\mu\text{m}, r_{e,\text{ice}}=30\,\mu\text{m}$).

**No model experiment, training, or prediction evaluation is authorized by this feasibility audit.**

---

## 2. Technical Feasibility Evaluation Across 10 Gates

| Gate ID | Feasibility Dimension | Status | Key Evidence / Metric |
|---|---|---|---|
| **F1** | 3D Hydrometeor Fields | **PASS** | MEPS `meps_det_pl` archive contains 3D $q_l$ (`mass_fraction_of_cloud_condensed_water_in_air_pl`) and $q_i$ (`mass_fraction_of_cloud_ice_in_air_pl`) on 13 pressure levels. |
| **F2** | Causal Availability | **PASS** | 100% causal availability ($347/347$ origins, $8328/8328$ tuples). $D-1$ $18:00\text{ UTC}$ run published by $\sim 21:30\text{ UTC}$ ($2.5\text{h}$ margin before $t_0=00:00\text{ UTC}$). |
| **F3** | Spatial Coverage | **CONDITIONAL** | Nuolja grid index $(y=760, x=486)$. $25 \times 25$ window ($30\text{ km}$ radius) covers zeniths up to $80^\circ$ ($5\text{ km}$ cloud); $85^\circ$ zenith requires $57.15\text{ km}$ displacement $\implies$ expanded $47 \times 47$ window ($115\text{ km}$ span) needed. |
| **F4** | Vertical Structure | **CONDITIONAL** | 13 pressure levels ($50$ to $1000\text{ hPa}$). Geometric height $z$ must be reconstructed via hydrostatic equation from $T, P, P_{\text{sfc}}$. Below-ground levels ($P > P_{\text{sfc}}$) masked out. |
| **F5** | Liquid/Ice Semantics | **PASS** | $q_l$ and $q_i$ standard mass fractions ($\text{kg/kg}$) are separately provided in MEPS NetCDF files. |
| **F6** | Optical Proxy Defensibility | **CONDITIONAL** | $q_l$ and $q_i$ are directly observed. Effective radii ($r_{e,\text{liq}}=10\,\mu\text{m}$, $r_{e,\text{ice}}=30\,\mu\text{m}$) must be parameterized. Proxy models direct-beam attenuation. |
| **F7** | Computational Tractability | **PASS** | $25 \times 25$ payload $\sim 516\text{ MB}$; expanded $47 \times 47$ payload $\sim 1.82\text{ GB}$ across 347 origins (**REPRODUCIBLE ESTIMATE**). Slicing via OPeNDAP finishes in $< 20\text{ min}$. |
| **F8** | Information Novelty | **PASS** | Genuinely novel spatial 3D cloud-beam intersection operator, distinct from 1D vertical column LWP/IWP and Stage 7.5 1D terrain horizon elevation angle. |
| **F9** | No Future Leakage | **PASS** | Ray tracing uses strictly causal solar zenith/azimuth geometry calculated at forecast valid times. |
| **F10** | Protocol Compatibility | **PASS** | Preserves locked 347-origin EVEN/ODD benchmark protocol without alteration. |

---

## 3. Detailed Technical Analysis

### A. Data Availability & Variable Semantics
- **Dataset:** MET Norway MEPS Deterministic Pressure Levels (`meps_det_pl`)
- **Variables:**
  - `mass_fraction_of_cloud_condensed_water_in_air_pl` ($\text{kg/kg}$)
  - `mass_fraction_of_cloud_ice_in_air_pl` ($\text{kg/kg}$)
  - `pressure` (13 levels: $50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000\text{ hPa}$)
  - `surface_air_pressure` ($\text{Pa}$)

### B. Causal Lineage
- **Issuance Time:** $D-1$ $18:00\text{ UTC}$
- **Publication Time:** $D-1$ $\sim 21:30\text{ UTC}$
- **Forecast Horizon Origin ($t_0$):** Day $D$ $00:00\text{ UTC}$
- **Causal Lead Time Margin:** $+2.5\text{ hours}$
- **Coverage:** 347 origins ($100\%$), 8,328 forecast tuples ($100\%$).

### C. Spatial Window Geometry & Solar Ray Displacement
- **Grid Spacing:** $2.5\text{ km}$
- **$25 \times 25$ Window:** $30.0\text{ km}$ cardinal radius, $42.4\text{ km}$ diagonal.
- **Ray Displacement Matrix $\Delta r(h, \theta_z) = h \cdot \tan(\theta_z)$:**
  - At $\theta_z = 80^\circ, h = 5\text{ km} \implies \Delta r = 28.36\text{ km}$ (fits $30\text{ km}$ radius).
  - At $\theta_z = 85^\circ, h = 5\text{ km} \implies \Delta r = 57.15\text{ km}$ (requires $47 \times 47$ window).

### D. Distinction Between Existing Stage 7.5 and Proposed Stage 8.21A
- **Stage 7.5:** 1D DEM horizon elevation obstruction angle at pyranometer location.
- **Stage 8.21A:** 3D line integral of extinction along actual 3D solar vector $(dx, dy, dz)$ through MEPS hydrometeor condensate grid.

---

## 4. Computational Feasibility & Storage Estimates

- **$25 \times 25$ Window Payload:** $\sim 516.1\text{ MB}$ total across 347 origins (**REPRODUCIBLE ESTIMATE**).
- **Expanded $47 \times 47$ Window Payload:** $\sim 1.82\text{ GB}$ total across 347 origins (**REPRODUCIBLE ESTIMATE**).
- **Data Acquisition Strategy:** Server-side OPeNDAP array slicing via THREDDS.

---

## 5. Next Steps & Recommendations

1. Preregister Stage 8.21A candidate feature extraction specification in a separate dedicated phase.
2. Resolve hydrostatic coordinate reconstruction and droplet parameterization details before design.
3. **DO NOT** trigger model training or ODD evaluation.
