# STAGE 8.9A — SPATIAL REPRESENTATIVENESS & VIEWING GEOMETRY AUDIT

**Project:** POLARIS SIH Forecasting  
**Stage:** STAGE 8.9A INDEPENDENT CLOUD-STATE / CLOUD-MOTION AUDIT  
**Target Location:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, Elevation $\approx 702\text{ m ASL}$)  
**Date:** September 12, 2026  

---

## 1. Topographic & Microclimatic Context of SITES Nuolja

SITES Nuolja is situated on a steep north/northeast-facing mountain slope overlooking the Torneträsk lake basin in northern Swedish Lapland. The meteorological station is located at $702\text{ m ASL}$, positioned directly within the Scandinavian mountain range (Scandes).

### Key Topographic Factors Affecting Cloud Observation:
1. **Orographic Forcing & Lee-Side Dynamics:** Prevailing westerly winds carrying moist maritime air from the Norwegian Sea ($~80\text{ km}$ west) undergo forced uplift over the Scandes ridges, creating localized orographic cloud cap systems and mountain lee waves.
2. **Precipitation Shadow & Valley Cloud Inversions:** Abisko and Nuolja lie in a localized precipitation shadow (annual precipitation $< 300\text{ mm}$), while low-level cloud layers frequently form inside the Torneträsk valley basin ($388\text{ m ASL}$) below the mountain station ($702\text{ m ASL}$).
3. **Microscale Cloud Variability:** Cloud boundaries and cloud optical thickness over Nuolja exhibit high spatial gradients over distances as small as $500\text{ m}$ to $2\text{ km}$.

---

## 2. Geostationary Viewing Geometry at $68.36^\circ\text{N}$ (Theoretical Spherical Geometry Audit)

*Note: All values in this section are derived from theoretical spherical geometry calculations relative to geostationary sub-satellite point ($0^\circ\text{N}, 0^\circ\text{E}$), rather than empirical Level-2 pixel measurements.*

Geostationary satellites (EUMETSAT Meteosat Second Generation SEVIRI at $0^\circ\text{E}$ or $9.5^\circ\text{E}$, and Meteosat Third Generation MTG-I1) orbit over the equator ($0^\circ\text{N}$).

### Spherical Geometry Calculation:
For a target at latitude $\phi = 68.362074^\circ\text{N}$ and longitude $\lambda = 18.738752^\circ\text{E}$, assuming sub-satellite longitude $\lambda_0 = 0^\circ\text{E}$:

The Satellite Zenith Angle (VZA / $\theta_s$) is calculated via:

$$\cos(\theta_s) = \frac{R_E + H}{R} \cos(\psi) - \frac{R_E}{R}$$

where:
- $R_E = 6371\text{ km}$ (Earth radius)
- $H = 35786\text{ km}$ (Geostationary orbital height)
- $\cos(\psi) = \cos(\phi) \cos(\lambda - \lambda_0) = \cos(68.362^\circ) \cos(18.739^\circ) \approx 0.3687 \times 0.9470 = 0.3491$

Solving yields:

$$\theta_s \approx 76.54^\circ \text{ (Theoretical Satellite Zenith Angle)}$$

### Theoretical Viewing Distortions ($\theta_s \approx 76.54^\circ$):

1. **Calculated Horizontal Parallax Shift ($\Delta x$):**
   A cloud layer situated at cloud-top altitude $h_c = 5\text{ km ASL}$ suffers a theoretical horizontal displacement toward the north/northeast:

   $$\Delta x = h_c \cdot \tan(\theta_s) = 5\text{ km} \times \tan(76.54^\circ) \approx 5 \times 4.18 = 20.9\text{ km}$$

2. **Theoretical Pixel Footprint Expansion:**
   At nadir ($0^\circ\text{N}$), SEVIRI sampling is $3.0\text{ km} \times 3.0\text{ km}$. At $\theta_s = 76.54^\circ$, the footprint expands in the north-south direction by $1/\cos(76.54^\circ) \approx 4.3$:

   $$\text{Theoretical N-S Dimension} \approx 3.0\text{ km} \times 4.3 \approx 12.9\text{ km}$$

3. **EUMETSAT Scientific Specification Boundary:**
   Documented EUMETSAT NWC SAF GEO user manuals specify that cloud optical retrievals (COT, CTH) are degraded or non-recommended north of $65^\circ\text{N}$ due to extreme limb foreshortening.

*Conclusion on Geostationary Satellites:* **NOT FEASIBLE** based on documented polar viewing geometry constraints.

---

## 3. Polar Orbiting Viewing Geometry (VIIRS / AVHRR / NWC SAF PPS)

Polar-orbiting satellites (Suomi-NPP, NOAA-20, NOAA-21, MetOp-B/C, Sentinel-3) operate in near-polar sun-synchronous orbits ($i \approx 98.7^\circ$) at altitudes of $\approx 820\text{ km}$.

### Spatial Footprint & Distance Analysis:
- **Nadir Resolution:** $750\text{ m}$ for VIIRS M-band ($375\text{ m}$ I-band); $1.0\text{ km}$ for MetOp AVHRR; $300\text{ m}$ for Sentinel-3 OLCI.
- **Off-Nadir Swath Width:** $3000\text{ km}$ for VIIRS. At swath edge, VZA reaches $\approx 70^\circ$, causing pixel enlargement to $\approx 1.6\text{ km} \times 1.6\text{ km}$.
- **Target Cell Alignment:** In Stage 8.4 empirical granule enumeration, nearest pixel center distance to Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}$) was $< 2.5\text{ km}$ for overpasses.

### Terrain Obstruction & Slope Geometry:
Nuolja's steep slope ($~20^\circ$ incline to the northeast) creates local shadowing. Solar optical retrievals (COT, CER) from polar orbiters assume flat horizontal surfaces, introducing retrieval uncertainties when solar azimuth angles align with mountain ridge shadows.

*Conclusion on Polar Orbiters:* Spatially representative ($< 2.5\text{ km}$ distance), but bounded by operational dissemination latency and polar night fill values.

---

## 4. Ground-Based Observational Networks (Kiruna ESNQ vs Abisko ANS)

### Candidate 1: Kiruna Airport Ceilometer & METAR (ESNQ)
- **Location:** $67.822^\circ\text{N}, 20.336^\circ\text{E}$, Elevation $460\text{ m ASL}$.
- **Geodesic Distance to Nuolja:** **88.4 km ESE**.
- **Topographic Separation:** Kiruna lies on the interior Lapland plateau east of the Scandes range. Nuolja is inside the high Scandes mountain corridor.
- **Spatial Representativeness Analysis:**
  Kiruna Airport is separated from Nuolja by $88.4\text{ km}$ of mountainous terrain across the Scandes ridge barrier. Frontal clouds arriving from the Norwegian Sea deposit precipitation and cloudiness over Nuolja while Kiruna remains clear under lee-side subsidence. Due to this extreme spatial separation and microclimate mismatch (interior plateau vs mountain valley), Kiruna observations are spatially non-representative of localized mountain cloudiness over Nuolja. No colocated paired correlation calculation was performed or claimed.

*Conclusion on Kiruna METAR:* **NOT FEASIBLE** due to spatial separation ($88.4\text{ km}$) and mountain barrier microclimate mismatch.

### Candidate 2: Abisko Scientific Research Station (SITES ANS)
- **Location:** $68.353^\circ\text{N}, 18.816^\circ\text{E}$, Elevation $388\text{ m ASL}$.
- **Geodesic Distance to Nuolja:** **3.23 km ESE**.
- **Elevation Difference:** $314\text{ m}$ lower than Nuolja ($702\text{ m}$).
- **Spatial Status:** Evaluated in Stage 8.3 and **REJECTED** due to inability of past surface transmissivity to beat the Stage 8.1 champion over $H1 \dots H24$.

---

## 5. Summary Matrix of Spatial Representativeness

| Candidate Source | Distance to Nuolja | Spatial Resolution / Footprint | Elevation Match | Topographic Obstruction Effect | Spatial Representativeness Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Meteosat SEVIRI / MTG FCI** | $\approx 20.9\text{ km}$ (Theoretical Parallax) | Theoretical N-S $12.9\text{ km} \times 3.0\text{ km}$ | N/A (Satellite column) | Severe limb foreshortening ($\theta_s \approx 76.54^\circ$) | **UNUSABLE (Polar Geometry Boundary)** |
| **NASA VIIRS Cloud Properties** | $< 2.5\text{ km}$ (Nadir pixel) | $750\text{ m} \times 750\text{ m}$ | Column average | Minor slope shadow distortion | **SPATIAL REPRESENTATIVE** |
| **EUMETSAT NWC SAF PPS** | $< 2.5\text{ km}$ | $1.0\text{ km} \times 1.0\text{ km}$ | Column average | Minor polar stereographic distortion | **SPATIAL REPRESENTATIVE** |
| **Kiruna Airport Ceilometer** | $88.4\text{ km}$ ESE | Point observation ($460\text{ m}$) | $242\text{ m}$ lower | Separated by Scandes mountain barrier | **UNUSABLE (88.4 km Separation)** |
| **Abisko ANS Pyrheliometer** | $3.23\text{ km}$ ESE | Point observation ($388\text{ m}$) | $314\text{ m}$ lower | Valley floor vs mountain slope | **HIGH (Already Rejected Stage 8.3)** |

