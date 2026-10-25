# POLARIS STAGE 8.7 — NEXT-ROUTE HANDOFF

## A. Stage 8.7 Final Outcome

- **Overall Stage 8.7 Status:** **CLOSED_REJECTED**
- **Stage 8.7A Feasibility & Proxy Freeze:** **PASS / APPROVED** (Proxy Hash: `a7f3e891c94b20d3671f845d098e21a44e5f7b88`)
- **Stage 8.7B Architecture Experiment:** **REJECTED**
- **EVEN CV Control MAE (Stage 8.1):** 37.620054 W/m² (Exact Match, G6 = PASS)
- **EVEN CV Candidate MAE (Stage 8.7B):** 49.445841 W/m²
- **EVEN CV Delta MAE:** **+11.825787 W/m²** (Severe Degradation)
- **EVEN CV Folds Improved:** 0 / 5 (G2 = FAIL)
- **Worst Fold Degradation:** +28.022026 W/m² (Fold 1, G3 = FAIL)
- **Control nMAE:** 37.97% | **Candidate nMAE:** 46.83% (G4 = FAIL)
- **Control RMSE:** 60.16 W/m² | **Candidate RMSE:** 81.33 W/m² (G4 = FAIL)
- **Causality Check:** 100% Causal (G5 = PASS)

---

## B. Why Stage 8.7 Was Rejected (Empirical Interpretation)

The two-head decomposition introduced separate prediction errors for the DirectProxy and DiffuseResidual components. When the two predicted components were recombined ($\widehat{\text{SW\_IN}} = \hat{y}_{\text{Direct}} + \hat{y}_{\text{Diffuse}}$), the resulting total $\text{SW\_IN}$ forecast performed substantially worse than the frozen Stage 8.1 control under the locked EVEN cross-validation protocol. 

The experiment therefore does not support this particular two-head decomposition as an improvement over the existing single-target residual-correction architecture.

---

## C. Information Learned & Mechanism Hypotheses

1. **Empirical Finding:** MEPS DNI was 100% causally available across all 347 origins ($8,328 / 8,328$ tuples) and was physically suitable for constructing the frozen DirectProxy. However, the Stage 8.7B direct/diffuse architecture produced severe degradation under the locked EVEN cross-validation protocol. The experiment does not uniquely identify the cause of that degradation.

2. **Mechanism Hypotheses (Unverified):** Potential contributors may include DirectProxy error propagation, target decomposition mismatch, or the difficulty of independently predicting the two derived components, but these mechanisms were not separately identified or established by the experiment.

---

## D. Scope of What Stage 8.7 Tested

### Distinction Between Stage 7.2 and Stage 8.7:
- **Stage 7.2:** MEPS native radiation variables, including DNI, were tested as additional scalar features and the route was rejected.
- **Stage 8.7:** The same causally available MEPS DNI information was tested in a fundamentally different architectural role: as a physical anchor for a DirectProxy / DiffuseResidual two-head target decomposition.

### Boundary of Conclusions:
- **Stage 8.7 DOES NOT establish that:**
  - DNI is physically useless,
  - MEPS radiation forecasts are useless,
  - direct/diffuse modeling is universally inferior,
  - all DNI-based architectures fail,
  - $L_1$ decomposition is mathematically invalid.
- **Stage 8.7 DOES establish that:**
  - this specific frozen DNI-anchored Direct/Diffuse two-head architecture failed the locked EVEN acceptance gates,
  - it degraded substantially relative to the frozen Stage 8.1 control (+11.83 W/m² MAE),
  - therefore this route is closed and rejected under the current POLARIS protocol.

---

## E. Authoritative POLARIS Stage 7 & 8 Route History Table

The following table summarizes the verified history of Stage 7 and Stage 8 research routes, reconciled directly against underlying stage artifacts:

| Stage | Route / Description | What Was Tested | Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Stage 7.1** | MEPS Radiation Verification | Causal availability & alignment of MEPS native shortwave, direct, and diffuse flux fields | Verified data pipelines & physical bounds | **PASS** |
| **Stage 7.2** | MEPS Native Radiation Features | Adding MEPS native shortwave and direct radiation variables as scalar features | Degraded EVEN CV MAE relative to baseline | **REJECTED** |
| **Stage 7.3** | $K_t$ Clearsky Index Reformulation | Target/feature reformulation using clearsky index $K_t = \text{SW\_IN} / \text{GHI}_{\text{clearsky}}$ | Increased variance and degraded EVEN CV MAE | **REJECTED** |
| **Stage 7.4** | Vertical Cloud Integration | Adding multi-layer cloud fraction, LWP, and IWP from MEPS pressure levels | Improved EVEN CV MAE (-0.42 W/m²) | **PASS / FROZEN** |
| **Stage 7.5** | Terrain Horizon & Shading | DEM 360° azimuth-resolved local horizon elevation & terrain shading flag | Improved EVEN CV & ODD test set (ODD MAE: 36.90 W/m²) | **PASS / FROZEN** |
| **Stage 8.0** | MEPS Model-Level Inventory | Audit of raw MEPS model-level pressure, wind, and humidity variables | Identified 700 hPa free-atmosphere steering wind candidate | **PASS** |
| **Stage 8.1** | 700 hPa Steering Wind | Adding $U_{700}, V_{700}$ free-atmosphere steering wind components | Improved EVEN CV & ODD test set (ODD MAE: 36.19 W/m²) | **PASS / CHAMPION** |
| **Stage 8.2** | Satellite Observability Feasibility | Data availability, latency, and spatial resolution audit for satellite cloud products | Verified operational latency constraints and data access | **PASS** |
| **Stage 8.3** | Abisko Direct/Diffuse Transfer | Incorporating Abisko station direct, diffuse, and transmissivity features | Degraded EVEN CV MAE (+0.63 W/m² relative to Stage 8.1) | **REJECTED** |
| **Stage 8.4** | VIIRS Feasibility & Operational Causality | Empirical coverage and operational latency investigation of NASA VIIRS L2 cloud optical properties | Verified 64.84% empirical coverage; standard L2 products require NRT feed | **VERIFIED / CONDITIONAL** |
| **Stage 8.5** | MEPS Spatial Cloud & Advection Experiment | Testing 14 spatial cloud-advection features extracted from 2D MEPS grid around Nuolja | Failed EVEN CV gates (Delta MAE: -0.19 W/m² vs required -0.50 W/m²) | **REJECTED** |
| **Stage 8.6** | CAMS AOD550 + TCWV Feasibility & Forecasting | Testing ECMWF/CAMS aerosol optical depth (`aod550`) and total column water vapour (`tcwv`) forecast features | Failed EVEN CV gates (Delta MAE: +0.25 W/m²; worst fold degradation: +1.31 W/m²) | **REJECTED** |
| **Stage 8.7** | Causal MEPS DNI-Anchored Direct/Diffuse Two-Head Architecture | Two-head target decomposition using frozen MEPS DNI DirectProxy anchor | Failed EVEN CV gates (Delta MAE: +11.83 W/m²; 0/5 folds improved) | **REJECTED** |

*Underlying stage artifacts and frozen benchmark records remain authoritative over this summary table.*

---

## F. Champion Status & Firewall Confirmation

- **Current Official Champion:** **Stage 8.1 700 hPa Steering Wind Model** ($U_{700}, V_{700}$).
- **Official ODD Test Set Metrics (Frozen):**
  - **ODD MAE:** **36.188657 W/m²**
  - **ODD nMAE:** **28.0688%**
  - **ODD RMSE:** **54.912301 W/m²**
- **ODD Dataset Status:** **100% UNTOUCHED** (0 target reads, 0 predictions, 0 metrics, 0 tuning).
- **Master Handoff Status:** `POLARIS_MASTER_HANDOFF.md` remains completely untouched.

---

## G. Historical Handoff Corrections

1. **Route Reconciliation:** The previous handoff contained stage-number and route-description mismatches (e.g., mislabeling VIIRS feasibility, MEPS spatial cloud advection, CAMS aerosol feasibility, and Stage 8.7 target architecture). The route history in Section E has been fully reconciled against the underlying authoritative stage artifacts.
2. **Empirical Narrowing:** The scientific interpretation of Stage 8.7 was narrowed to empirical findings supported directly by the experiment. Claims of mathematical superiority of Stage 8.1 and claims of uniquely identified DNI forecast noise were removed because they exceeded what the experiment established.
3. **Immutability of Historical Evidence:** All historical experimental measurements, fold records, gate decisions, and underlying stage artifacts remain 100% unchanged and preserved.

---

## H. Next Steps

- Stage 8.7 is officially **CLOSED_REJECTED**.
- Stage 8.1 $U_{700}/V_{700}$ steering wind model remains the active operational champion.
- ODD test dataset remains untouched by Stage 8.7.
- The next route must be selected from the verified Stage 8 research queue.
- No new experiment is authorized by this handoff document itself.
