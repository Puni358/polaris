# STAGE 8.5 — PRE-EXECUTION CONTROL BASELINE & GEOMETRY AUDIT REPORT

**Project:** POLARIS  
**Stage:** STAGE 8.5 MEPS SPATIAL CLOUD-ADVECTION EXPERIMENT  
**Audit Date:** September 12, 2026  
**Auditor:** POLARIS Lead Forensic Research Auditor  
**Status:** **AUDIT COMPLETE — CONTROL BASELINE RECONCILED & VERIFIED**  
**Action:** **STOPPED BEFORE STAGE 8.5 CV EXECUTION**

---

## 1. Executive Summary & Audit Conclusions

This pre-execution forensic audit resolved the control baseline discrepancy identified in the Stage 8.5 implementation plan, verified the MEPS spatial coordinate mapping, and established the authoritative control metrics and acceptance gates for Stage 8.5.

1. **Reconciled Control MAE:** The authoritative EVEN 5-fold CV MAE of the frozen Stage 8.1 37-feature Champion model is **`35.069059 W/m²`** (evaluated under the official frozen Stage 4 pipeline).
2. **Provenance of `37.620054 W/m²`:** Produced during Stage 8.1 development when Stage 4 parameters ($w, k$) were **dynamically refitted per fold**.
3. **Provenance of `38.280605 W/m²`:** The legacy Stage 6.6 31-feature baseline EVEN CV MAE.
4. **MEPS Grid Cell Verification:** MEPS grid cell $(y=760, x=486)$ corresponds to $68.355701^\circ\text{N}, 18.763666^\circ\text{E}$ ($\approx 1.2\text{ km}$ from SITES Nuolja $68.362074^\circ\text{N}, 18.738752^\circ\text{E}$), **100% verified** against MEPS NetCDF metadata.
5. **Corrected Candidate Gate 1 Threshold:** Candidate EVEN CV MAE must achieve $\le \mathbf{34.569059\text{ W/m}^2}$ ($\ge 0.500000\text{ W/m}^2$ improvement relative to Control $E_0 = 35.069059\text{ W/m}^2$).

---

## 2. Comprehensive Provenance Audit of Control Numbers

| Numerical Value | Model & Features | Stage 4 Parameter Pipeline | Provenance & Usage History | Status |
| :--- | :--- | :--- | :--- | :---: |
| **`38.280605 W/m²`** | Stage 6.6 Model (31 features) | Frozen Stage 4 parameters | Stage 6.6 5-fold EVEN CV baseline. Used as $E_0$ control in Stage 6.6, Stage 7.2–7.5, and Stage 8.1 initial development. | **LEGACY BASELINE** |
| **`37.620054 W/m²`** | Stage 8.1 Model (37 features) | Dynamic fold refitting ($w, k$) | Candidate $E_1$ result in Stage 8.1 (`run_stage8_1.py`) when Stage 4 parameters were re-optimized per fold during CV. | **DEVELOPMENT METRIC** |
| **`35.069059 W/m²`** | Stage 8.1 Champion (37 features) | **Frozen Stage 4 parameters** (`pred_ensemble`) | Official Stage 8.1 37-feature Champion evaluated under the frozen Stage 4 pipeline across the locked EVEN 5-fold CV (`run_stage8_3.py`). | **AUTHORITATIVE CONTROL ($E_0$)** |

### Methodological Explanation of Discrepancy
- In `run_stage8_1.py`, Stage 4 parameters $w$ and $k$ were refitted per CV fold via grid search (`Method B`), yielding an MAE of `37.620054 W/m²`.
- However, as mandated in `POLARIS_STAGE8_1_CHAMPION_MANIFEST.md` (Line 43: `Stage 4 Refit Executed: NO`), the official operational champion uses **frozen Stage 4 parameters** (`pred_ensemble` from Stage 4).
- When evaluated under the official frozen Stage 4 pipeline in Stage 8.3 (`run_stage8_3.py`), the Stage 8.1 37-feature Champion achieved an EVEN CV MAE of **`35.069059 W/m²`** (nMAE = `35.8331%`, RMSE = `56.691085 W/m²`).
- Therefore, **`35.069059 W/m²`** is the unique, mathematically authoritative Control Baseline $E_0$ for Stage 8.5.

---

## 3. Spatial Coordinate & Grid Mapping Verification

### MEPS Projection & Grid Coordinates
- **Target Location:** SITES Nuolja Middle Station ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, Elev: $675\text{ m a.s.l.}$).
- **MEPS Projection:** Lambert Conformal Conic, $2.5\text{ km} \times 2.5\text{ km}$ projected grid spacing ($\Delta x = \Delta y = 2500\text{ m}$).
- **Metadata Inspection:** Queried `latitude` and `longitude` at grid indices $(y=760, x=486)$ from `meps_det_sfc_20240119T18Z.ncml` via THREDDS:
  - `latitude[760][486]` = **$68.355701^\circ\text{N}$**
  - `longitude[760][486]` = **$18.763666^\circ\text{E}$**
  - `y` coordinate = $567,482.1\text{ m}$
  - `x` coordinate = $154,915.94\text{ m}$
- **Euclidean Distance:** The spatial offset between grid cell center $(y=760, x=486)$ and SITES Nuolja is $\approx 1.2\text{ km}$, strictly within the $2.5\text{ km}$ grid cell boundary. **Mapping is 100% VERIFIED**.

### Steering Vector & Spatial Derivatives
- MEPS variables `x_wind_pl` ($U_{700}$) and `y_wind_pl` ($V_{700}$) are expressed in m/s along the projected $x$ (column) and $y$ (row) grid axes.
- Spatial gradients $\frac{\partial N}{\partial x}$ and $\frac{\partial N}{\partial y}$ are computed using physical grid spacing in metres ($\Delta x = 2500\text{ m}$ for 3x3 stencil, $5000\text{ m}$ for 5x5 stencil).
- Advection proxy $-\mathbf{v} \cdot \nabla N = -\left(U_{700} \frac{\partial N}{\partial x} + V_{700} \frac{\partial N}{\partial y}\right)$ is fully consistent with the projected coordinate frame.

---

## 4. Causality & Temporal Tendency Verification

1. **Issuance Policy:** For every origin $t_0$, spatial cloud features are extracted exclusively from the D-1 18Z MEPS run ($t_{\text{issuance}} = t_0 - 6\text{h} \le t_0$).
2. **Temporal Tendency Rule:** $dN/dt = [N_{\text{MEPS}}(t_0 + H) - N_{\text{MEPS}}(t_0 + H - 1\text{h})] / 1\text{h}$ uses forecast cloud fractions from the SAME D-1 18Z run.
3. **Causality Assertion:** Code explicitly asserts `issuance_time <= t0` and `valid_time == t0 + H` for all 347 origins $\times$ 24 horizons.
4. **Zero Hindsight:** No future observations (actuals, SITES SW_IN, Abisko obs, VIIRS obs, or ODD data) are used.

---

## 5. Corrected Stage 8.5 Acceptance Gates

Evaluating Candidate $E_1$ (Stage 8.1 37 features + 14 causal spatial cloud/advection features = 51 features) against Control $E_0$ (Stage 8.1 Champion = `35.069059 W/m²`):

| Gate | Description | Predeclared Acceptance Threshold |
| :--- | :--- | :---: |
| **Gate 1** | Mean Daytime MAE | $\le \mathbf{34.569059\text{ W/m}^2}$ ($\Delta\text{MAE} \le -0.500000\text{ W/m}^2$) |
| **Gate 2** | Fold Consistency | $\ge 4 / 5$ EVEN CV folds improved |
| **Gate 3** | Worst-Fold Degradation | $\max(\text{cand\_mae}_{\text{fold}} - \text{ctrl\_mae}_{\text{fold}}) \le +0.500000\text{ W/m}^2$ |
| **Gate 4** | nMAE & RMSE Consistency | Candidate nMAE $\le 35.8331\%$ AND RMSE $\le 56.691085\text{ W/m}^2$ |
| **Gate 5** | Absolute Causality | $t_{\text{issuance}} \le t_0$ for 100% of 347 origins |
| **Gate 6** | Control Reproduction | Reproduced $E_0$ MAE == `35.069059 W/m²` ($\text{tolerance} < 1 \times 10^{-4}$) |

---

## 6. Audit Confirmation & Stop Status

- **Control Reconciliation:** **100% PASSED** (`35.069059 W/m²` established as authoritative).
- **Spatial Grid Mapping:** **100% PASSED** (Cell $760, 486$ verified to $68.3557^\circ\text{N}, 18.7637^\circ\text{E}$).
- **Causality Policy:** **100% PASSED** (D-1 18Z run verified for all 347 origins).
- **ODD Governance:** **100% PASSED** (Zero ODD access, zero tuning).
- **Execution Status:** **STOPPED AS DIRECTED**. Model training for Stage 8.5 candidate CV has NOT been executed.

---
*Audit completed: September 12, 2026 | Verified against MEPS metadata, stage manifests, and codebase logs.*
