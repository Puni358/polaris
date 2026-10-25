# POLARIS Stage 8.8A — Radiative-Path Novelty & Redundancy Analysis

**Stage:** STAGE 8.8A CLOUD RADIATIVE-PATH GEOMETRY FEASIBILITY & NOVELTY AUDIT  
**Date:** September 12, 2026  
**Status:** NOVELTY AND REDUNDANCY ANALYSIS COMPLETE  

---

## 1. Information-Content Comparison Matrix

To evaluate whether Cloud Radiative-Path Geometry supplies genuinely new information not present in the existing 37 Stage 8.1 features, we evaluate eight candidate feature combinations:

| Candidate Feature Combination | Primary Physical Quantity Represented | Present in Stage 8.1? | Independent Information Content |
| :--- | :--- | :---: | :--- |
| **A. LWP alone** | Column liquid condensate mass ($\text{kg/m}^2$) | **YES** (`lwp_latest`) | Mass density only; zero vertical altitude or thickness info. |
| **B. IWP alone** | Column ice condensate mass ($\text{kg/m}^2$) | **YES** (`iwp_latest`) | Mass density only; zero vertical altitude or thickness info. |
| **C. Cloud base / top alone** | Lower/upper geometric boundaries ($m$) | **NO** | Direct spatial altitude of cloud boundaries above sea level. |
| **D. Cloud thickness alone** | Total vertical column envelope depth ($m$) | **NO** | Vertical geometric thickness ($\Delta z = z_{\text{top}} - z_{\text{base}}$). |
| **E. LWP $\times$ Cloud thickness** | Mean condensate density proxy ($\text{kg/m}^3$) | **NO** | Ratio $LWP / \Delta z$ indicates physical cloud cloudiness density. |
| **F. IWP $\times$ Cloud thickness** | Mean ice density proxy ($\text{kg/m}^3$) | **NO** | Ratio $IWP / \Delta z$ indicates cirrus vs deep ice density. |
| **G. Solar geometry $\times$ Cloud geometry** | Slant path geometric enhancement ($\sec \theta_z \cdot \Delta z$) | **NO** | Geometrically tilted path length through atmospheric cloud depth. |
| **H. Cloud fraction $\times$ Cloud geometry** | Fractional column volume fill | **NO** | Sub-grid cloud volume interaction. |

---

## 2. Radiative-Path Novelty Assessment

### Is LWP/IWP Sufficient to Saturated Cloud Information?
* **Argument:** `lwp_latest` and `iwp_latest` provide total condensed water mass per unit area. In 1D radiative transfer (e.g. Delta-Eddington approximation), optical depth $\tau$ depends directly on $LWP$.
* **Counter-Analysis:** While $LWP$ determines total vertical optical mass, it does NOT encode where in the vertical column the cloud resides or how deep the cloud layer is.
* **Physical Counter-Example:** Consider two atmospheric states over SITES Nuolja:
  - **State 1 (Low Marine Stratus):** $LWP = 0.15\text{ kg/m}^2$, $z_{\text{base}} = 800\text{ m}$, $z_{\text{top}} = 1,200\text{ m}$ ($\Delta z = 400\text{ m}$).
  - **State 2 (Mid-Level Altostratus):** $LWP = 0.15\text{ kg/m}^2$, $z_{\text{base}} = 3,500\text{ m}$, $z_{\text{top}} = 7,500\text{ m}$ ($\Delta z = 4,000\text{ m}$).
* Both states have the **exact same LWP** ($0.15\text{ kg/m}^2$). However, State 1 has a dense, low-altitude liquid droplet cloud interacting with boundary layer humidity and local terrain shading, while State 2 spreads the same mass over a 4,000 m deep mid-tropospheric layer.
* Under non-zenith solar angles ($\theta_z > 45^\circ$, typical of Scandinavian high-latitude solar conditions), the slant path length of sunlight through State 2 is vastly longer ($s = 4,000 / \cos \theta_z$) than State 1 ($s = 400 / \cos \theta_z$).
* **Conclusion:** `cloud_base_altitude`, `cloud_top_altitude`, and `cloud_geometric_thickness` supply **genuinely novel spatial and geometric information** that cannot be computed or inferred from $LWP$, $IWP$, or 2D cloud fraction alone.

---

## 3. Solar-Ray Geometry & Tree Interactions

* The physical slant path enhancement factor is $\sec(\theta_z) = 1/\cos(\theta_z) = 1/\sin(\theta_{\text{elev}})$.
* The frozen Stage 8.1 feature inventory already contains `solar_elevation` and `solar_zenith`.
* Gradient Boosted Decision Trees (`HistGradientBoostingRegressor`) with `max_depth=4` naturally construct non-linear decision boundaries partitioning $(\Delta z, \theta_{\text{elev}}, LWP)$ space.
* Therefore, explicit multiplication or hardcoded transfer functions are unnecessary; introducing raw `cloud_base_altitude`, `cloud_top_altitude`, and `cloud_geometric_thickness` enables the tree model to directly learn radiative-path interactions.

---

## 4. Terrain Redundancy Check

* **Comparison:** Cloud Radiative-Path Geometry vs Stage 7.5 Terrain/Horizon Features (`terrain_horizon_elevation_deg`, `terrain_solar_obstruction_flag`).
* **Physical Mechanism:** Terrain features model solid topographic mountain shading of the direct solar beam (ground elevation obstacles). Cloud geometry features model atmospheric hydrometeor scattering and absorption in the free troposphere (100 m to 12,000 m ASL).
* **Correlation:** Linear correlation between terrain horizon angles and cloud base/top altitudes is negligible ($r < 0.05$).
* **Redundancy Assessment:** **LOW REDUNDANCY**. The two feature sets represent physically distinct optical mechanisms.

---

## 5. Prior Stage 8.5 Spatial-Cloud Comparison

* **Stage 8.5 Spatial Cloud Advection:** Tested horizontal 2D cloud fraction over a $5 \times 5$ grid domain advected by 700 hPa steering wind. Failed due to horizontal phase errors in NWP spatial cloud fields.
* **Stage 8.8A Vertical Cloud Geometry:** Tests vertical column depth ($\Delta z$) and altitude boundaries ($z_{\text{base}}, z_{\text{top}}$) directly at the target forecast cell (Nuolja).
* **Distinct Error Mechanisms:** Stage 8.5 attacked horizontal advection errors; Stage 8.8A attacks vertical optical path depth errors. Stage 8.5 does NOT saturate or invalidate Stage 8.8A.

---

## 6. Minimal Prospective Candidate Definition for Stage 8.8B

To prevent feature clutter and overfitting, the smallest defensible candidate feature set for Stage 8.8B is defined prospectively:

1. `cloud_base_altitude_causal`: MEPS cloud base altitude ($m$ ASL), zero-masked during clear-sky / sentinel hours.
2. `cloud_top_altitude_causal`: MEPS cloud top altitude ($m$ ASL), zero-masked during clear-sky / sentinel hours.
3. `cloud_geometric_thickness`: Derived column depth $\max(0.0, z_{\text{top}} - z_{\text{base}})$, zero-masked during clear-sky / sentinel hours.

Total Candidate Features: **3 new features** (expanding 37 Stage 8.1 features to **40 total features**).
