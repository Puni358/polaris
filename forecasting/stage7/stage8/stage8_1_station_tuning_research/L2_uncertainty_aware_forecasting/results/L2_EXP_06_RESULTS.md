# POLARIS L2-EXP-06 — Domain & Measurement Evidence Audit Results

**Date**: October 04, 2026  
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Target Station**: Mount Nuolja Middle Station AWS (`ANS_NMS`, 702 m a.s.l., `68.36207412° N, 18.73875158° E`)  
**Audit Purpose**: Determine whether authoritative project data and provenance contain sufficient direct measurement or metadata to justify a physically grounded solar upper-envelope formulation for L2 uncertainty-aware forecasting.

---

## 1. Executive Decision: **`DOMAIN-AUTHORITY-REQUIRED`**

A rigorous, exhaustive audit of all raw and processed station observations, metadata headers, acquisition manifests, instrument deployment logs, and terrain profiles in the POLARIS repository yields a definitive conclusion:

1. **Empirical Exceedance is Directly Observable (VERIFIED)**:
   Authoritative SITES Level 2 station data for `ANS_NMS` confirms that actual pyranometer irradiance routinely exceeds the geometric clear-sky bound ($1.25 \times \text{clearsky\_ghi}$) at low solar elevations ($\le 15^\circ$), with a $100.00\%$ violation rate at $0–1^\circ$ (mean actual $11.01\text{ W/m}^2$ vs mean clear sky $0.12\text{ W/m}^2$) and an invariant $29.8\% \pm 0.3\%$ violation rate across 2020, 2021, and 2022. The universal multiplicative clear-sky bound is structurally refuted.

2. **Component Decomposition is Entirely Absent (UNKNOWN)**:
   `ANS_NMS` is equipped with only a single upward-facing silicon photodiode pyranometer (Apogee SP110 at 2.86 m a.g.l.) recording total incoming hemispherical shortwave radiation ($SW_{IN}$). **No direct normal irradiance (DNI), no diffuse horizontal irradiance (DHI), no reflected shortwave ($SW_{OUT}$), no surface albedo, and no net radiometer measurements exist anywhere in the repository.**

3. **Sensor Calibration & Error Characteristics are Unrecorded (UNKNOWN)**:
   The repository contains **zero calibration certificates, zero calibration dates, zero sensor sensitivity multipliers, zero cosine response curves, and zero maintenance/cleaning logs** for the Nuolja pyranometer.

4. **Zero Production Authority for Numeric Limits**:
   While the structural *formulation* of a diffuse floor ($\max(k \cdot \text{cs}, F)$) or elevation-dependent envelope ($k \cdot \text{cs} + D(\theta_{\text{elev}})$) is physically motivated, setting any specific numerical production constant (such as $80\text{ W/m}^2$, $60\text{ W/m}^2$, or $100\text{ W/m}^2$) **cannot be justified from available physical evidence**.

**Conclusion**: The project cannot derive a defensible numeric production boundary from currently available repository data. Establishing an operational production bound requires either new sensor measurements (DHI/DNI) or formal operational boundary specification by the domain governing authority.

---

## 2. Radiation Measurements Available vs. Absent

| Radiation Variable | Status in Project | Exact Source / File Path | Authoritative for Production Envelope? |
|---|---|---|---|
| **Global Horizontal Irradiance ($SW_{IN}$)** | **VERIFIED PRESENT** | `data/raw_historical_sites_download/SITES_MET_ANS_NMS_20200101-20210101_L2_SH.csv` (and 2021–2023) | **Yes** for empirical envelope; **No** for component isolation |
| **Diffuse Horizontal Irradiance (DHI)** | **ABSENT** | None (`ANS_NMS` has no shaded pyranometer) | **No** (Unmeasured) |
| **Direct Normal Irradiance (DNI)** | **ABSENT** | None (`ANS_NMS` has no pyrheliometer) | **No** (Unmeasured) |
| **Direct / Diffuse Decomposition** | **ABSENT** | None | **No** (Unmeasured; diffuse interpretation is inferential) |
| **Reflected Shortwave ($SW_{OUT}$)** | **ABSENT** | None (`ANS_NMS` has no downward pyranometer) | **No** (Unmeasured) |
| **Surface Optical Albedo** | **ABSENT** | None (Acoustic snow depth `D_SNOW` exists, but not optical albedo) | **No** (Unmeasured) |
| **Surface Radiation Balance ($R_{\text{net}}$)** | **ABSENT** | None (No 4-component net radiometer) | **No** (Unmeasured) |
| **Dedicated Twilight Radiometer** | **ABSENT** | Standard SP110 logs 24/7 without low-light calibration | **No** (Unmeasured) |
| **Topographic Horizon Obstruction** | **VERIFIED PRESENT** | `stage7/stage7_5_terrain_horizon/nuolja_horizon_profile_360deg.csv` (DEM ray-marching) | **Yes** for geometric line-of-sight shading; **No** for diffuse flux |

---

## 3. Instrument Metadata & Quality Control Status

### Documented Instrument Facts
- **Sensor Model**: Apogee SP110 Silicon-cell Pyranometer (documented in SITES file headers and acquisition manifests).
- **Deployment Height**: $2.86\text{ m}$ above ground level on the automatic weather station mast.
- **Station Location**: Mount Nuolja middle station, $702\text{ m}$ a.s.l., $68.36207412^\circ\text{ N}, 18.73875158^\circ\text{ E}$.
- **Logging Cadence**: 5-second sampling frequency, arithmetic mean logged every 10 minutes.

### Unrecorded / Missing Instrument Information
- **Calibration Records**: None. No factory sheet, recalibration date, or sensitivity factor ($\mu\text{V / (W/m}^2\text{)}$).
- **Measurement Uncertainty**: None documented locally.
- **Cosine Response**: No local cosine error curve or high-zenith angle correction is documented.
- **Sensor Leveling**: No spirit bubble inspection logs or orientation checks.
- **Maintenance Logs**: No records of rime, frost, snow, or dust removal from the optical diffuser.
- **Per-Row QC Flags**: Absent. SITES Level 2 files provide continuous numeric values (`0 NaNs`), but no row-level flags indicating sensor icing, twilight noise, or suspect data.

---

## 4. Assessment of Envelope Formulations

1. **Universal Multiplicative Bound ($U = k \times \text{clearsky\_ghi}$)**:
   - **REFUTED**. At $\theta_{\text{elev}} \le 1^\circ$, clear-sky GHI direct beam collapses to near zero ($0.12\text{ W/m}^2$), while pyranometer observations average $11.01\text{ W/m}^2$ (max $52.04\text{ W/m}^2$), resulting in a $100.00\%$ failure rate. No multiplier $k$ can overcome asymptotic horizon collapse.

2. **Clear-Sky + Positive Diffuse Floor ($U = \max(k \times \text{clearsky\_ghi}, F)$)**:
   - **FORMULATION-SUPPORTED, NUMERICALLY UNRESOLVED**. Decoupling the low-sun diffuse background from the geometric direct beam regime is physically sound. However, without local diffuse radiometers, any numeric value for $F$ cannot be derived from first principles.

3. **Elevation-Aware Continuous Envelope ($U = k \cdot \text{cs} + D(\theta_{\text{elev}})$)**:
   - **FORMULATION-SUPPORTED, NUMERICALLY UNRESOLVED**. Continuous variation of diffuse background avoids non-smooth derivative cliffs, but functional parameters cannot be identified from existing single-pyranometer data.

4. **Empirical Historical Regime Quantiles ($U = Q_{0.99}(y \mid \text{bin})$)**:
   - **REJECTED**. Pure statistical step functions lack physical radiative transfer grounding and risk overfitting the historical training sample.

5. **Specific $80\text{ W/m}^2$ Benchmark**:
   - **UNAUTHORIZED**. While $80\text{ W/m}^2$ satisfied empirical test gates in L2-EXP-04, it was selected strictly as a research ablation assumption. It has zero status as an established physical constant.

---

## 5. Strict Categorization of Physical Knowledge

### A. VERIFIED (Directly Supported by Authoritative Project Evidence)
- The Nuolja AWS pyranometer measures substantial positive shortwave radiation ($10–100\text{ W/m}^2$) during low-sun hours ($0–15^\circ$).
- The clear-sky GHI model collapses to zero as $\theta_{\text{elev}} \to 0^\circ$, causing a $100.00\%$ failure rate for $1.25 \times \text{cs}$ at $0–1^\circ$.
- The failure rate of $1.25 \times \text{cs}$ in low sun ($\le 15^\circ$) is invariant across independent years ($29.8\% \pm 0.3\%$ in 2020, 2021, and 2022).
- The station uses an Apogee SP110 silicon-cell pyranometer mounted at 2.86 m a.g.l. at 702 m elevation.

### B. INFERRED (Reasonable Physical Interpretation, Not Directly Measured)
- Low-sun positive irradiance is primarily atmospheric diffuse skylight, atmospheric refraction, and scattered light from snow-covered terrain.
- Silicon-cell pyranometers exhibit known cosine error increases at high solar zenith angles ($>80^\circ$), exaggerating relative sensitivity to diffuse light.
- Mountain ridge topography blocks direct sunlight while sky diffuse radiation continues to reach the sensor.
- *Diffuse interpretation is inferential; direct/diffuse decomposition unavailable.*

### C. UNKNOWN (Evidence Unavailable in Project Repository)
- The relative quantitative breakdown between atmospheric diffuse radiation, terrain reflection, snow albedo, and sensor cosine error.
- The true optical albedo of the surrounding terrain.
- The sensor's specific factory calibration constant, drift rate, and maintenance history.
- The exact numeric boundary required for operational production.

---

## 6. Recommended Governance Action

1. **Formalize Rejection of Multiplicative Bound**: Acknowledge that $U = 1.25 \times \text{clearsky\_ghi}$ is structurally invalid near the horizon.
2. **End Modeling Iterations for Physical Limits**: Cease attempting to "tune" or "discover" an optimal numerical floor through machine learning or conformal empirical metrics.
3. **Submit Evidence to Domain Governing Authority**: Present the empirical envelope statistics ($0–5^\circ$ p95 $= 74.09\text{ W/m}^2$, max $= 165.45\text{ W/m}^2$) to power grid/energy management system domain authorities to define an authorized operational safety envelope.
