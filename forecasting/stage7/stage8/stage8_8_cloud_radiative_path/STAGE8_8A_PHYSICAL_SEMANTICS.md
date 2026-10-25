# POLARIS Stage 8.8A — Physical Semantics & Geometric Representation

**Stage:** STAGE 8.8A CLOUD RADIATIVE-PATH GEOMETRY FEASIBILITY & NOVELTY AUDIT  
**Date:** September 12, 2026  
**Status:** PHYSICAL SEMANTICS AUDIT COMPLETE  

---

## 1. Physical Definition of MEPS Cloud Base and Cloud Top

In the MEPS numerical weather prediction system (HARMONIE-AROME hydrostatic/non-hydrostatic model), cloud macro-structure is parameterized via diagnostic vertical boundaries in `meps_det_sfc`:

* `cloud_base_altitude`: Height above sea level ($m$) of the lowest atmospheric model layer where diagnosed cloud condensate (liquid + ice) exceeds the sub-grid cloud detection threshold ($q_c > 10^{-6}\text{ kg/kg}$) or where cloud fraction is non-zero.
* `cloud_top_altitude`: Height above sea level ($m$) of the highest atmospheric model layer containing diagnosed cloud condensate.
* `cloud_geometric_thickness`: Derived depth $\Delta z = \max(0.0, \text{cloud\_top\_altitude} - \text{cloud\_base\_altitude})$.

---

## 2. Geometric Cloud Thickness vs Radiative Optical Path Length

A critical physical distinction must be maintained between **geometric cloud thickness** ($\Delta z$) and **radiative optical path length** ($\tau_{slant}$):

$$\Delta z = z_{\text{top}} - z_{\text{base}} \quad [\text{meters}]$$

$$\tau = \int_{z_{\text{base}}}^{z_{\text{top}}} \beta_{\text{ext}}(z) dz \approx \frac{3}{2 \rho_w r_{\text{eff}}} \text{LWP} \quad [\text{dimensionless}]$$

$$\tau_{\text{slant}} = \frac{\tau}{\cos \theta_z} = \tau \cdot \sec \theta_z \quad [\text{dimensionless}]$$

### Key Distinctions:
1. **Physical Property:** Geometric thickness ($\Delta z$) measures the spatial extent of the cloud envelope in meters. Optical path length ($\tau$) measures the integrated extinction cross-section of water droplets and ice crystals encountering photons.
2. **Independence from Mass:** A cloud can be geometrically thick ($\Delta z = 6,000\text{ m}$, e.g. high Arctic cirrostratus) but optically thin ($\tau < 1.0$) if condensate density is very low ($LWP < 0.01\text{ kg/m}^2$). Conversely, a low stratus or fog layer can be geometrically thin ($\Delta z = 200\text{ m}$) but optically opaque ($\tau > 30$) due to high liquid water concentration ($LWP > 0.30\text{ kg/m}^2$).
3. **Slant Geometry:** When the sun is low on the horizon (high zenith angle $\theta_z$, low elevation $\theta_{\text{elev}}$), the slant path length of a solar ray passing through a cloud layer of thickness $\Delta z$ is $s = \Delta z / \sin(\theta_{\text{elev}})$.
4. **Conclusion:** $\Delta z = z_{\text{top}} - z_{\text{base}}$ is **NOT equivalent to optical thickness $\tau$**. It represents an independent geometric path variable.

---

## 3. Clear-Sky & Low Cloud Fraction Behavior

### Sentinel Value Behavior:
* In the MEPS archive NetCDF files, when total cloud cover is zero (`fc_cloud_cover == 0`), no cloud boundaries exist. The model outputs the NetCDF sentinel fill value:
  $$\text{Fill Value} = 9.96921 \times 10^{36}$$
* **Mandatory Preprocessing Guardrail:** In any feature extraction pipeline, clear-sky sentinel values MUST be explicitly zero-masked (`cloud_base = 0.0`, `cloud_top = 0.0`, `cloud_geometric_thickness = 0.0`) when `fc_cloud_cover == 0` or when sentinel values occur. Leaving sentinel values raw would corrupt decision tree splitting thresholds in gradient boosting algorithms.

### Sub-Grid Low Cloud Fraction:
* When total cloud cover is non-zero but small (e.g. 1–5% scattered sub-grid cumulus), MEPS diagnoses a base and top altitude for that sub-grid cloud layer.
* While the local cloud thickness $\Delta z$ may be several hundred meters, the column-averaged optical impact on Global Horizontal Irradiance (GHI) is modulated by `cloud_frac`. Interaction terms such as $\Delta z \times \text{cloud\_frac}$ prevent small sub-grid clouds from generating misleading column extinction signals.

---

## 4. Multi-Layer Cloud Representation & Envelope Collapse

A fundamental limitation of column-level surface diagnostics is the **multi-layer cloud problem**:

```
Model Column Profile:
---------------------------------------------
10,000 m  =================== Cloud Top (9,500 m)
 9,000 m  Thin Cirrus Layer
 8,000 m  =================== Layer Base (8,000 m)
 7,000 m  
 6,000 m  CLEAR AIR GAP (6,000 m empty)
 5,000 m  
 4,000 m  
 3,000 m  =================== Layer Top (2,000 m)
 2,000 m  Low Stratus Layer
 1,000 m  =================== Cloud Base (1,000 m)
     0 m  ------------------- Ground (702 m ASL)
---------------------------------------------
Diagnostic Result:
cloud_base_altitude = 1,000 m
cloud_top_altitude  = 9,500 m
cloud_geometric_thickness = 8,500 m  <-- OVERESTIMATED!
```

### Physical Evaluation:
* `cloud_base_altitude` reports the **lowest** cloud base in the atmospheric column.
* `cloud_top_altitude` reports the **highest** cloud top in the atmospheric column.
* When multiple distinct cloud layers coexist (e.g. high cirrus over low stratus), `cloud_top - cloud_base` collapses intermediate clear-sky gaps, producing a **total column envelope thickness**.
* **Layer Reconstruction Feasibility:** Surface diagnostic products do NOT separate multi-layer boundaries into discrete sub-layers. Reconstructing individual sub-layers from surface diagnostics alone is physically impossible without full 65-level model-level data (`meps_det_ml`), which was disproved at 18Z in Stage 8.0.
* **Impact:** Geometric thickness $\Delta z$ MUST be interpreted as a **total column envelope depth**, which serves as an upper bound on cloud geometric extent.
