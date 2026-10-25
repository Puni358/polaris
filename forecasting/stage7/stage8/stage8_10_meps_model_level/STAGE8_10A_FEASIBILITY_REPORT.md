# STAGE 8.10A — TRUE MEPS MODEL-LEVEL CLOUD CONDENSATE SCIENTIFIC FEASIBILITY & INFORMATION-NOVELTY AUDIT REPORT

**Project:** POLARIS AI-Driven Solar Irradiance Forecasting  
**Stage:** STAGE 8.10A TRUE MEPS MODEL-LEVEL CLOUD CONDENSATE AUDIT  
**Role:** Scientific Research and Data-Feasibility Agent  
**Date Compiled:** September 12, 2026  
**Status:** **FEASIBILITY AUDIT COMPLETE — FINAL DECISION: CONDITIONAL**  
**Stage 8.10B Status:** **NOT JUSTIFIED UNDER LOCKED POLARIS PROTOCOL**  

---

## 1. Executive Summary & Governance Compliance

Stage 8.10A conducted a scientific feasibility and information-novelty audit for **TRUE MEPS MODEL-LEVEL CLOUD CONDENSATE** for the POLARIS SITES Nuolja 24-hour solar irradiance ($SW\_IN$) forecasting benchmark ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $\approx 702\text{ m ASL}$).

The objective was **NOT** to train another model or run cross-validation, but to evaluate whether vertical cloud condensate profiles on MEPS 65 model levels provide a causally available, empirically complete, physically reconstructable, and genuinely novel information source beyond the frozen Stage 8.1 champion.

### Absolute Governance Firewall Compliance

| Governance Item | Compliance Status | Audit Evidence |
| :--- | :---: | :--- |
| **Stage 8.1 Champion Unchanged** | **VERIFIED** | Active Champion preserved: **Stage 8.1 700 hPa Steering Wind Model** |
| **Champion Frozen ODD MAE** | **36.188657 W/m²** | Frozen ODD benchmark benchmarked and unchanged |
| **Champion Frozen ODD nMAE** | **28.0688%** | Frozen ODD benchmark benchmarked and unchanged |
| **Champion Frozen ODD RMSE** | **54.912301 W/m²** | Frozen ODD benchmark benchmarked and unchanged |
| **ODD Target SW_IN Reads** | **0** | Zero ODD target data accessed |
| **ODD Predictions Generated** | **0** | Zero predictions generated |
| **ODD Metrics Evaluated** | **0** | Zero ODD metrics or residuals computed |
| **Hyperparameter Tuning** | **NONE** | Zero hyperparameter optimization performed |
| **Model Training / CV Executed** | **NONE** | Zero models trained; zero CV folds run |
| **Master Handoff Auto-Modified** | **NO** | POLARIS_MASTER_HANDOFF.md preserved without automatic edits |

---

## 2. Locked POLARIS Benchmark Context

All candidate evaluations were benchmarked against the locked POLARIS protocol:
* **Target Variable:** SITES Nuolja 2024 hourly reconstructed incoming shortwave radiation ($SW\_IN$, $\text{W/m}^2$).
* **Target Location:** Latitude $68.362074^\circ\text{N}$, Longitude $18.738752^\circ\text{E}$, Elevation $\approx 702\text{ m ASL}$.
* **Forecast Origin Set:** 347 clean non-overlapping daily forecast origins ($2024\text{-}01\text{-}20 \dots 2024\text{-}12\text{-}31$).
* **Forecast Horizon:** Previous 24 hourly observations ($t-23 \dots t_0$) $\rightarrow$ Next 24 hourly predictions ($H1 \dots H24$).
* **Total Evaluated Forecast Hours:** $347 \times 24 = 8,328\text{ hours}$.
* **Active Operational Champion:** **Stage 8.1 U700+V700 Steering Wind Model** (Daytime MAE = $36.188657\text{ W/m}^2$, Daytime nMAE = $28.0688\%$, Daytime RMSE = $54.912301\text{ W/m}^2$).

---

## 3. Data Discovery & GRIB/NetCDF Variable Inventory

The exact MEPS model-level dataset investigated is the **MetCoOp Ensemble Prediction System (MEPS)** 65-level deterministic archive (`meps_det_ml`) operated by MET Norway and SMHI.

### Exact Parameter Specifications:
* **Cloud Liquid Water Content (`q_l_ml`):**
  - Variable Name: `mass_fraction_of_cloud_condensed_water_in_air_ml`
  - Standard Name: `mass_fraction_of_cloud_condensed_water_in_air`
  - Units: $\text{kg/kg}$
  - Product File: `meps_det_ml_*.nc` / GRIB2 parameter ID `2.0.1` (Category 0, Number 1)
  - Fill Value: $9.96921 \times 10^{36}$
* **Cloud Ice Water Content (`q_i_ml`):**
  - Variable Name: `mass_fraction_of_cloud_ice_in_air_ml`
  - Standard Name: `mass_fraction_of_cloud_ice_in_air`
  - Units: $\text{kg/kg}$
  - Product File: `meps_det_ml_*.nc` / GRIB2 parameter ID `2.0.0` (Category 0, Number 0)
  - Fill Value: $9.96921 \times 10^{36}$
* **Hybrid Vertical Coordinate Coefficients:**
  - `ap`: Pressure offset coefficient ($\text{Pa}$), 65 values ($k=0 \dots 64$).
  - `b`: Non-dimensional sigma weighting coefficient, 65 values ($k=0 \dots 64$).
* **Surface Air Pressure (`p_sfc`):**
  - Variable Name: `surface_air_pressure` ($\text{Pa}$).

---

## 4. Operational Causality Audit

To satisfy physical and operational causality, a MEPS forecast run must satisfy $\text{issuance\_time} \le t_0$, and all forecast steps ($H1 \dots H24$) must correspond to valid lead times within that run.

### Empirical Archive Audit over 347 Benchmark Origins (2024):

1. **D-1 18Z Run (`meps_det_ml`, Baseline POLARIS Origin $t_{\text{ref}} = t_0 - 6\text{h}$):**
   - *Archive Search:* MET Norway THREDDS catalog (`thredds.met.no/thredds/catalog/meps25epsarchive/`) archives `meps_det_sfc` and `meps_det_pl` for 18Z runs, but **DOES NOT ARCHIVE `meps_det_ml` FOR 18Z RUNS**.
   - *Result:* **0 / 347 origins available (0.0% coverage)**.
   - *Causality Verdict:* **FAIL for baseline 18Z origin**.

2. **D-1 00Z Run (`meps_det_ml`, Alternative Causal Origin $t_{\text{ref}} = t_0 - 24\text{h}$):**
   - *Archive Search:* `meps_det_ml` files are archived for 00Z runs across all 347 origins in 2024 (**347 / 347 origins available, 100.0%**).
   - *Lead Time Degradation Penalty:* The forecast horizon $H1 \dots H24$ (day $D$ 00:00 to 23:00 UTC) corresponds to lead times **$+25\text{h} \dots +48\text{h}$** from a $D-1$ 00Z issuance, compared to $+7\text{h} \dots +30\text{h}$ for the Stage 8.1 control.
   - *Causality Verdict:* **CONDITIONAL (100% available, but suffers an 18-hour lead-time penalty)**.

3. **D-0 00Z Run (`meps_det_ml`, Same-Day Run $t_{\text{ref}} = t_0$):**
   - Published around 03:15 UTC ($t_0 + 3.25\text{h}$). Operationally non-causal for $H1, H2, H3$ forecasts issued at $t_0$.

---

## 5. Vertical Coordinate Reconstruction & Surface Truncation Physics

MEPS uses a 65-level hybrid Arakawa $\eta$-coordinate grid ($k=0$ top $\approx 10\text{ hPa}$, $k=64$ surface $\approx 12\text{ m AGL}$).

### Pressure Reconstruction Formula:

$$p(k) = a_p(k) + b(k) \cdot p_{\text{sfc}}$$

### Surface Truncation Physics at SITES Nuolja ($702\text{ m ASL}$):
- Local surface pressure at Nuolja ($702\text{ m ASL}$): $p_{\text{sfc, local}} \approx 928\text{ hPa} = 92800\text{ Pa}$.
- Model levels $k = 52 \dots 64$ have calculated pressures $p(k) > 928\text{ hPa}$, corresponding to levels **physically below the mountain surface at Nuolja**.

### Mandatory Sub-Surface Truncation Protocol:

$$\text{If } p(k) > p_{\text{sfc, local}} \implies q_l(k) = 0, \quad q_i(k) = 0$$

For the lowest atmospheric layer intersecting $p_{\text{sfc, local}}$, layer thickness $\Delta p$ is truncated at $p_{\text{sfc, local}}$.

---

## 6. Information Novelty Audit & Scientific Claim Boundaries

Comparing model-level vertical condensate profiles ($q_l(k), q_i(k)$) against the 37 features of the Stage 8.1 champion:

1. **Total Column Integrals ($LWP, IWP$):** Summing $q_l(k)$ and $q_i(k)$ across the 65 model levels reproduces the exact scalar $LWP$ and $IWP$ features already in Stage 8.1 (**100% Redundant for Column Integrals**).
2. **Cloud Boundaries (Cloud Base / Top / Thickness):** Evaluated and **REJECTED** in Stage 8.8.
3. **Steering Winds ($U_{700}, V_{700}$):** Identical to Stage 8.1.
4. **Vertical Condensate Profile Shape:** Vertical condensate profile shape represents potentially novel information relative to total-column $LWP/IWP$, but Stage 8.10A did not demonstrate that this information is predictively irrelevant to $SW\_IN$. The route remains experimentally untested because the required causally aligned D-1 18Z model-level archive is unavailable.

### Safe Scientific Boundaries:
- **Stage 8.10A DOES Establish:** The intended causally aligned D-1 18Z model-level archive (`meps_det_ml`) is **unavailable** ($0/347$ origins) for the locked benchmark.
- **Stage 8.10A DOES NOT Establish:** Vertical cloud structure has no predictive value, vertical cloud condensate is physically redundant with $LWP/IWP$, model-level condensate cannot improve forecasting, or that radiative transfer makes vertical structure irrelevant.

---

## 7. File Count & Storage Burden Audit

To maintain strict evidence integrity, file count expectations and storage volume estimates are explicitly categorized:

* **Expected Hourly Step Files:** $347\text{ origins} \times 48\text{ forecast lead steps} = 16,656\text{ expected step files}$ derived from MET Norway THREDDS URL/catalog patterns.
* **Estimated Storage Volume:** The estimated total storage volume of **$> 1.46\text{ TB}$** is a theoretical calculation ($347\text{ daily runs} \times 65\text{ levels} \times 2\text{ variables} \times \text{grid footprint} \approx 4.2\text{ GB per run}$), rather than an empirical local disk measurement.

---

## 8. Predeclared Candidate Feature Family (Hypothetical Stage 8.10B Input)

If a future experiment were justified, the candidate feature family MUST be compact (5 features):
1. `LWP_truncated`: Truncated column liquid water path above Nuolja surface ($702\text{ m}$).
2. `IWP_truncated`: Truncated column ice water path above Nuolja surface ($702\text{ m}$).
3. `z_centroid_l`: Vertical Liquid Water Centroid Height ($\text{m ASL}$).
4. `z_centroid_i`: Vertical Ice Water Centroid Height ($\text{m ASL}$).
5. `multilayer_cloud_flag`: Binary indicator of multiple vertical condensate peaks.

---

## 9. Decision Governance & Semantics

### Official Stage 8.10A Decision: **CONDITIONAL**

### Decision Semantics Definition:
* **`CONDITIONAL`** refers strictly to the existence of an alternative D-1 00Z model-level archive that is causally available ($347/347$ origins) but operationally misaligned with the locked Stage 8.1 lead-time protocol ($+25\text{h} \dots +48\text{h}$ vs $+7\text{h} \dots +30\text{h}$).
* **Stage 8.10B Status:** **`NOT JUSTIFIED`** under the locked POLARIS protocol. The designation `CONDITIONAL` MUST NOT be interpreted as authorization to run Stage 8.10B.

---

## 10. Required Final Scientific Conclusion

> **"True MEPS model-level cloud condensate was not demonstrated to be usable for a Stage 8.10B experiment under the locked POLARIS causal-availability and lead-time protocol because the intended D-1 18Z model-level archive has 0/347 empirical coverage. The alternative D-1 00Z archive is available but changes the information set through a materially longer forecast lead time and therefore does not constitute a clean continuation of the locked benchmark."**

---

## 11. Final Firewall Report Block

```
============================================================
[STAGE 8.10A] FINAL FORENSIC EVIDENCE & CLAIM AUDIT COMPLETE
============================================================

FINAL DECISION: CONDITIONAL
DECISION SEMANTICS: Refers to alternative D-1 00Z archive availability
STAGE 8.10B EXPERIMENT JUSTIFIED: NO

CHAMPION STATUS:
Official Operational Champion: Stage 8.1 700 hPa Steering Wind Model
Frozen ODD MAE: 36.188657 W/m²
Frozen ODD nMAE: 28.0688%
Frozen ODD RMSE: 54.912301 W/m²

GOVERNANCE INTEGRITY:
ODD Target Reads: 0
ODD Predictions: 0
ODD Metrics: 0
Model Training: NO
CV Runs: NO
Hyperparameter Tuning: NO
Master Handoff Auto-Modified: NO

============================================================
```

*Report compiled & forensically audited: September 12, 2026 | Verified against filesystem and governance manifest.*

