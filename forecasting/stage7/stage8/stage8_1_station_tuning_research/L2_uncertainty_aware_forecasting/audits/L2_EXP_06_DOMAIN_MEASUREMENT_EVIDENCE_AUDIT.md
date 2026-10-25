# POLARIS L2 Uncertainty-Aware Forecasting — L2-EXP-06 Domain & Measurement Evidence Audit

**Date**: October 04, 2026  
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Target Station**: Mount Nuolja Middle Station AWS (`ANS_NMS`, 702 m a.s.l., `68.36207412° N, 18.73875158° E`)  
**Experiment ID**: `L2-EXP-06`  
**Audit Purpose**: Domain and measurement evidence audit for the solar physical uncertainty envelope.  
**Scientific Decision Category**: **`DOMAIN-AUTHORITY-REQUIRED`**  

---

## 1. Executive Summary & Audit Mandate

Following the findings of `L2-EXP-04` and `L2-EXP-05`:
1. The research physical upper bound $U = 1.25 \times \text{clearsky\_ghi}$ was proven empirically inadequate at low solar elevations ($\le 15^\circ$), causing severe prediction interval clipping and artificial coverage collapse.
2. An additive diffuse floor formulation ($U = \max(1.25 \times \text{cs}, F)$) and an elevation-dependent envelope ($U = 1.25 \times \text{cs} + D(\theta_{\text{elev}})$) were demonstrated to be physically motivated structural solutions.
3. However, the $80\text{ W/m}^2$ floor tested in L2-EXP-04 was strictly a research ablation assumption with zero production authority.
4. Physical mechanisms (diffuse twilight scattering, snow albedo reflections, silicon sensor cosine response) remained inferential.

**Audit Mandate**: Determine whether authoritative project data and provenance contain sufficient direct measurement or authoritative metadata to justify a physically grounded numeric solar upper-envelope for production.

**Audit Verdict: `DOMAIN-AUTHORITY-REQUIRED`**  
The project lacks direct measurements of diffuse horizontal irradiance (DHI), direct normal irradiance (DNI), reflected shortwave radiation, surface albedo, and sensor calibration/cosine curves. Therefore, while a diffuse-floor formulation is physically defensible, setting any specific numeric production boundary cannot be justified from current data and must be authorized by domain authorities.

---

## 2. Exhaustive Radiation Measurement Audit

| Radiation Variable | Authoritative Measurement in Repository? | Exact Repository Artifact | SHA256 Checksum | Authoritative Status |
|---|---|---|---|---|
| **Global Horizontal Irradiance ($SW_{IN}$)** | **YES** | `data/raw_historical_sites_download/SITES_MET_ANS_NMS_20200101-20210101_L2_SH.csv`<br>`SITES_MET_ANS_NMS_20210101-20220101_L2_SH.csv`<br>`SITES_MET_ANS_NMS_20220101-20221231_L2_SH.csv`<br>`SITES_MET_ANS_NMS_20230101-20231231_L2_SH.csv` | `0964f90c735c...`<br>`b7401e25c267...`<br>`85652531b70d...`<br>`38bee0f31503...` | **VERIFIED**. Continuous 10-minute Level 2 observations from Apogee SP110 at 2.86 m a.g.l. Fully validates empirical total GHI distribution, but cannot isolate components. |
| **Diffuse Horizontal Irradiance (DHI)** | **NO** | None | N/A | **ABSENT / UNKNOWN**. `ANS_NMS` has no shaded pyranometer or shadowband radiometer. |
| **Direct Normal Irradiance (DNI)** | **NO** | None | N/A | **ABSENT / UNKNOWN**. `ANS_NMS` has no sun-tracking pyrheliometer. |
| **Direct / Diffuse Decomposition** | **NO** | None | N/A | **ABSENT / UNKNOWN**. Direct/diffuse separation does not exist in any local dataset. |
| **Reflected Shortwave Radiation ($SW_{OUT}$)** | **NO** | None | N/A | **ABSENT / UNKNOWN**. `ANS_NMS` has no downward-facing pyranometer. |
| **Surface Optical Albedo** | **NO** | None | N/A | **ABSENT / UNKNOWN**. Snow depth (`D_SNOW`, acoustic SR50A) exists, but optical albedo is not measured. |
| **Surface Radiation Balance ($R_{\text{net}}$)** | **NO** | None | N/A | **ABSENT / UNKNOWN**. No 4-component net radiometer is installed at `ANS_NMS`. |
| **Dedicated Twilight Radiation Sensor** | **NO** | None | N/A | **ABSENT / UNKNOWN**. Standard SP110 logs continuously, but has no specialized low-irradiance calibration. |

---

## 3. Sensor & Instrument Metadata Audit

A forensic inspection of raw SITES CSV headers, acquisition manifests, and project documentation reveals:

1. **Documented Instrument Facts**:
   - **Instrument Model**: Apogee SP110 silicon-cell pyranometer.
   - **Deployment Height**: $2.86\text{ m}$ above ground level on the AWS mast.
   - **Sampling & Logging**: Sampled every 5 seconds, logged as 10-minute arithmetic mean.
   - **Station Elevation**: $702\text{ m}$ a.s.l. (treeline on Eastern slope of Mt. Nuolja).
   - **Provider**: SITES / Abisko Scientific Research Station (Swedish Polar Research Secretariat).

2. **Absent Instrument Documentation**:
   - **Calibration Certificates**: None found in the repository.
   - **Calibration Dates & Multipliers**: No sensor sensitivity constant ($\mu\text{V per W/m}^2$) or recalibration date recorded.
   - **Measurement Uncertainty Budget**: No locally certified measurement uncertainty.
   - **Cosine Response Curve**: No empirical directional response curve for the specific deployed unit.
   - **Leveling & Alignment Records**: No bubble-leveling or orientation logs available.
   - **Maintenance & Cleaning Records**: No records of optical dome cleaning, snow/rime wiping, or dome replacement.

---

## 4. Quality Control Protocol Audit

An audit of the SITES Level 2 format confirms:
- **No Per-Row Quality Flags**: The raw and processed CSV files contain purely numeric entries and standard deviations (`TA, RH, SW_IN, TS, PRECIP, D_SNOW, TA_STD, SW_IN_STD, TS_STD`).
- **No Snow/Ice Flags on Pyranometer**: While the `D_SNOW` metadata notes vegetation growth during summer, there is zero flagging or metadata regarding snow accumulation or rime frosting on the pyranometer optical dome.
- **No Shading / Low-Sun Flags**: There are no operational flags indicating when the sun is obstructed by local terrain or when the sensor operates at high zenith angles ($>80^\circ$).
- **Upstream Quality Screening**: SITES provides Level 2 data as "quality controlled", but the exact automated or manual screening rules applied upstream are not detailed in local repository records.

---

## 5. Physical Boundary Support Assessment

Based strictly on authoritative evidence:

1. **Universal Multiplicative Bound ($U = k \times \text{clearsky\_ghi}$)**:
   - **STATUS: REFUTED**.
   - Direct empirical data shows that at solar elevation $0–1^\circ$, clear-sky GHI direct beam approaches zero ($0.12\text{ W/m}^2$), while actual pyranometer observations average $11.01\text{ W/m}^2$ (max $52.04\text{ W/m}^2$). Consequently, $100.00\%$ of observations violate $1.25 \times \text{cs}$ at $0–1^\circ$. No scalar multiplier can solve this asymptotic failure.

2. **Clear-Sky + Positive Diffuse Floor ($U = \max(k \times \text{clearsky\_ghi}, F)$)**:
   - **STATUS: FORMULATION-SUPPORTED, NUMERICALLY UNRESOLVED**.
   - The formulation correctly decouples the direct geometric beam from the background diffuse sky radiation. However, because local diffuse radiation is unmeasured, the exact numerical floor $F$ cannot be derived from local physical evidence.

3. **Elevation-Aware Continuous Envelope ($U = k \cdot \text{cs} + D(\theta_{\text{elev}})$)**:
   - **STATUS: FORMULATION-SUPPORTED, NUMERICALLY UNRESOLVED**.
   - Physically superior because it models the gradual transition of diffuse radiation with atmospheric path length, avoiding sharp derivative discontinuities. However, functional parameters require DHI measurements that do not exist in the repository.

4. **Pure Empirical Historical Envelope ($U = Q_{0.99}(y \mid \text{bin})$)**:
   - **STATUS: REJECTED**.
   - Non-physical step-function table that risks empirical overfitting.

5. **Specific $80\text{ W/m}^2$ Constant**:
   - **STATUS: UNAUTHORIZED FOR PRODUCTION**.
   - $80\text{ W/m}^2$ was introduced purely as an ablation benchmark in L2-EXP-04. While the empirical 95th percentile in the $0–5^\circ$ bin happens to be $74.09\text{ W/m}^2$, selecting 80 vs 60 vs 100 has no authoritative physical backing from local sensors.

---

## 6. EXP-05 Follow-Up Questions Addressed

1. *Is low-sun exceedance directly observable in authoritative station data?*  
   **YES (VERIFIED)**. Across $12,206$ historical daytime observations, $61.09\%$ of observations in $0–5^\circ$ and $29.81\%$ in $\le 15^\circ$ strictly exceed $1.25 \times \text{clearsky\_ghi}$.

2. *Is there authoritative evidence explaining whether this is diffuse/twilight radiation, snow/albedo/reflection, cosine response, horizon effects, or another measurement phenomenon?*  
   **NO (INFERRED / UNKNOWN)**. These are plausible physical mechanisms, but none can be quantitatively isolated because `ANS_NMS` measures only total GHI via a single upward-looking pyranometer.

3. *Can any of those mechanisms be quantitatively bounded from existing evidence?*  
   **NO (UNKNOWN)**. Bounding them requires separate DHI, DNI, and upwelling shortwave measurements, which are absent.

4. *Can the existing evidence justify a forecast-time physical upper bound?*  
   **NO (UNKNOWN / INSUFFICIENT)**. The evidence justifies rejecting multiplicative bounds, but cannot justify an operational numeric boundary.

5. *What additional measurement/documentation is required?*  
   - Dedicated direct/diffuse radiation measurements (DNI from tracking pyrheliometer, DHI from shaded pyranometer).  
   - Reflected shortwave radiation ($SW_{OUT}$) to quantify snow albedo feedback.  
   - Factory calibration certificates, cosine error response curves, and maintenance logs for the Apogee SP110 sensor.  
   - Formal operational risk specifications from energy management/grid domain authorities.

---

## 7. Strict Categorization: VERIFIED / INFERRED / UNKNOWN

### VERIFIED (Directly Supported by Authoritative Project Evidence)
- Empirical GHI observations from Apogee SP110 at Nuolja AWS (`ANS_NMS`, 702 m a.s.l.) across 2020–2023.
- Clear-sky GHI direct beam approaches zero at $\theta_{\text{elev}} \to 0^\circ$ ($0.12\text{ W/m}^2$ at $0–1^\circ$), leading to a $100.00\%$ failure rate for $1.25 \times \text{cs}$ at $0–1^\circ$.
- Low-sun failure rate of $1.25 \times \text{cs}$ is structurally invariant across independent years ($29.8\% \pm 0.3\%$).
- DEM 360° terrain horizon ray-marching profile computes geometric terrain obstruction up to $29.8^\circ$ (azimuth $252^\circ$).

### INFERRED (Supported Interpretation but Not Directly Measured)
- Low-sun positive irradiance is primarily atmospheric diffuse skylight and twilight scattering, amplified by surrounding snow cover albedo.
- Silicon-cell pyranometer cosine response characteristics at high zenith angles ($>80^\circ$) contribute to elevated relative diffuse sensitivity.
- Direct sunlight is blocked by western mountain ridges during evening hours while diffuse skylight continues to reach the horizontal pyranometer.
- *“Diffuse interpretation is inferential; direct/diffuse decomposition unavailable.”*

### UNKNOWN (Evidence Unavailable in Project Repository)
- Quantitative split between atmospheric diffuse radiation, snow albedo backscatter, and sensor cosine error.
- Apogee SP110 factory calibration constant, serial number, calibration date, and cosine error curve.
- Maintenance history regarding pyranometer dome cleaning or rime/frost clearing.
- Authoritative operational numeric boundary for production forecasting.

---

## 8. Final Governance Status Block

```
L2-EXP-06 DOMAIN / MEASUREMENT EVIDENCE AUDIT
STATUS: PASS

SCIENTIFIC CAUSAL CONCLUSION:
DOMAIN-AUTHORITY-REQUIRED

EVIDENCE AUDIT VERDICT:
Existing authoritative project evidence is insufficient to justify a numeric production boundary for the solar physical upper envelope. While multiplicative clear-sky bounding is structurally refuted and diffuse-floor formulations are physically supported, local radiation decomposition (DHI/DNI), surface albedo, and sensor calibration curves are absent. Specification of an operational upper boundary requires formal domain authority determination.

MODEL CLASS:
Frozen SKGBDT + Global Conformal (CQR)

MODEL CHANGED:
NO

F CHANGED:
NO

GAP19 CHANGED:
NO

2024 USED:
NO

2023 BLIND EVALUATION USED:
NO (Quarantined from model evaluation)

Q_HAT VERIFIED:
+9.8962 W/m² (MATCH)

GHI / SW_IN MEASUREMENTS:
VERIFIED PRESENT (Apogee SP110 @ 2.86 m a.g.l., 2020-2023 SITES Level 2)

DHI / DNI MEASUREMENTS:
ABSENT (0 datasets)

REFLECTED SW / ALBEDO MEASUREMENTS:
ABSENT (0 datasets)

SENSOR CALIBRATION / COSINE RECORDS:
ABSENT (0 certificates / 0 curves)

IS 80 W/m² AN AUTHORIZED PHYSICAL CONSTANT:
NO (Research ablation reference only; zero production authority)

IS 1.25*CLEARSKY PHYSICALLY DEFENSIBLE AT LOW SUN:
NO (Structurally refuted; 100% violation at 0-1° elevation)

RECOMMENDED NEXT ACTION:
Cease empirical modeling iterations for physical boundaries. Retain Candidate F, Stage 8.1, and SKGBDT+CQR frozen. Submit the low-sun empirical envelope evidence (p95 = 74.09 W/m², max = 165.45 W/m² in 0-5°) to domain and energy management system authorities to define a formal operational boundary policy.
```
