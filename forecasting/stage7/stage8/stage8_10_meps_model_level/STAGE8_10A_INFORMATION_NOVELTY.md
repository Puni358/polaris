# STAGE 8.10A — INFORMATION NOVELTY AUDIT

**Project:** POLARIS SIH Forecasting  
**Stage:** STAGE 8.10A TRUE MEPS MODEL-LEVEL CLOUD CONDENSATE AUDIT  
**Baseline Inventory:** Stage 8.1 Champion Feature Set (37 Features)  
**Date:** September 12, 2026  

---

## 1. Baseline Feature Set Context (Stage 8.1 Champion)

The active frozen champion is the **Stage 8.1 700 hPa Steering Wind Model** (ODD Daytime MAE = $36.188657\text{ W/m}^2$, nMAE = $28.0688\%$, RMSE = $54.912301\text{ W/m}^2$).

The 37 features in Stage 8.1 cover:
1. **Target History ($t-23 \dots t_0$):** Past 24 hourly observations of SITES Nuolja `SW_IN`.
2. **Solar & Clearsky Reference ($H1 \dots H24$):** Solar Zenith Angle ($SZA$), Solar Azimuth Angle ($SAA$), Ineichen/Perez Clearsky GHI ($GHI_{\text{clearsky}}$).
3. **MEPS Column Microphysics ($H1 \dots H24$):** Total Cloud Cover (`TCC`), Low Cloud Cover (`LCC`), Mid Cloud Cover (`MCC`), High Cloud Cover (`HCC`), Liquid Water Path (`LWP`), Ice Water Path (`IWP`).
4. **Terrain Horizon Shading (Stage 7.5):** $30\text{ m}$ DEM horizon masking profile ($360^\circ$ azimuth).
5. **Steering Winds (Stage 8.1):** Zonal wind ($U_{700}$) and Meridional wind ($V_{700}$) at $700\text{ hPa}$.

---

## 2. Information Redundancy vs Novelty Classification

To evaluate true MEPS model-level cloud condensate ($q_l(k), q_i(k)$ on 65 levels), we classify its physical information into two categories:

### A. Information Already Represented in Baseline (Redundant)

1. **Total Column Liquid Water Path ($LWP$) and Ice Water Path ($IWP$):**
   - Stage 6.6 already extracted integrated column $LWP$ and $IWP$ from MEPS.
   - Summing $q_l(k)$ and $q_i(k)$ across the 65 model levels reproduces the exact scalar $LWP$ and $IWP$ features already present in Stage 8.1.
   - *Redundancy:* **100% Redundant for Column Integrals**.

2. **Cloud Base Altitude, Cloud Top Altitude, Geometric Thickness:**
   - Stage 8.8 extracted `cloud_base_altitude`, `cloud_top_altitude`, and `cloud_thickness` from MEPS.
   - Stage 8.8 was evaluated and **REJECTED** (failed to beat Stage 8.1 champion).
   - *Redundancy:* **Already Tested & Rejected**.

3. **Atmospheric Steering Wind Layer ($U_{700}, V_{700}$):**
   - Stage 8.1 extracted $700\text{ hPa}$ steering winds. Model-level winds $x\_wind\_ml(k), y\_wind\_ml(k)$ at $\approx 700\text{ hPa}$ ($k \approx 42$) are identical to pressure-level $U_{700}, V_{700}$.
   - *Redundancy:* **100% Redundant**.

---

### B. Potentially Novel Information (Vertical Condensate Profile Shape)

Vertical condensate profile shape represents potentially novel information relative to total-column $LWP/IWP$, but Stage 8.10A did not demonstrate that this information is predictively irrelevant to $SW\_IN$. The route remains experimentally untested because the required causally aligned D-1 18Z model-level archive is unavailable.

Potential profile shape summary metrics include:
- **Condensate Vertical Centroid Altitude ($z_{\text{centroid}}$):**

  $$z_{\text{centroid}} = \frac{\sum_{k} z(k) q_l(k)}{\sum_k q_l(k)}$$

- **Vertical Profile Spread ($\sigma_z^2$):** Variance of condensate altitude distribution.
- **Multilayer Separation Indicator:** Binary indicator if condensate profile has multiple vertical peaks separated by clear layers.
- **Liquid-to-Ice Vertical Detachment:** Altitude gap between liquid water peak and ice water peak.

---

## 3. Scientific Claim Boundaries

Stage 8.10A explicitly distinguishes what it **DOES** establish from what it **DOES NOT** establish:

### Stage 8.10A DOES Establish:
- The intended causally aligned D-1 18Z model-level archive (`meps_det_ml`) is **unavailable** ($0/347$ origins) for the locked benchmark.
- The alternative D-1 00Z archive is available ($347/347$ origins) but introduces a severe 18-hour lead-time penalty ($+25\text{h} \dots +48\text{h}$ vs $+7\text{h} \dots +30\text{h}$).

### Stage 8.10A DOES NOT Establish:
- Vertical cloud structure has no predictive value.
- Vertical cloud condensate is physically redundant with $LWP/IWP$.
- Model-level condensate cannot improve forecasting.
- Radiative transfer makes vertical structure irrelevant.
- A different operational archive could never be useful.

---

## 4. Summary Matrix of Information Novelty

| Feature / Information Channel | Source Variable | Baseline Equivalent (Stage 8.1) | Physical Novelty Status | Experimental Status |
| :--- | :--- | :--- | :--- | :--- |
| **Integrated Liquid Water Path** | $\sum q_l(k) \Delta p / g$ | `LWP` (Stage 6.6) | **100% Redundant** | Fully Represented in Stage 8.1 |
| **Integrated Ice Water Path** | $\sum q_i(k) \Delta p / g$ | `IWP` (Stage 6.6) | **100% Redundant** | Fully Represented in Stage 8.1 |
| **Cloud Base / Top Altitude** | Level thresholds | `cloud_base` / `cloud_top` (Stage 8.8) | **Already Rejected (Stage 8.8)** | Evaluated & Rejected |
| **Steering Wind** | $x\_wind\_ml(k)$ at $700\text{ hPa}$ | $U_{700}, V_{700}$ (Stage 8.1) | **100% Redundant** | Fully Represented in Stage 8.1 |
| **Condensate Vertical Centroid ($z_{\text{cen}}$)** | $z_{\text{centroid}}$ equation | None | **Potentially Novel** | Untested (18Z Archive Missing) |
| **Multilayer Cloud Indicator** | Profile peak count | None | **Potentially Novel** | Untested (18Z Archive Missing) |

---

## 5. Summary Conclusion on Information Novelty

Vertical condensate profile shape represents potentially novel information relative to total-column $LWP/IWP$, but Stage 8.10A did not demonstrate that this information is predictively irrelevant to $SW\_IN$. The route remains experimentally untested because the required causally aligned D-1 18Z model-level archive is unavailable ($0/347$ empirical coverage).

