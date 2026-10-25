# POLARIS — STAGE 8.19 EXACT REPRODUCTION RUN & ROW-LEVEL PREDICTION EXPORT AUDIT

**Audit Date**: `2026-09-13T10:38:35+05:30`  
**Execution Purpose**: Deterministic re-execution of the frozen Stage 8.19 evaluation pipeline and row-level ODD prediction export (`STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv`).  
**Final Status**: **`REPRODUCTION FAILED`**

---

> [!WARNING]
> **NON-AUTHORITATIVE EXPORT NOTICE**  
> The row-level prediction table [`STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv) was exported from executing the exact frozen Stage 8.19 code pipeline.  
> However, because the dynamically computed metrics (`MAE = 36.490857 W/m²`) differ from the documented historical Stage 8.19 target (`MAE = 34.821405 W/m²`), this CSV must **NOT** be called authoritative.  
> The historical metrics are **NOT** replaced.

---

## 1. Phase 1 — Input Data & Pipeline Verification

| Data Component | Source Specification | Forensic Status |
| :--- | :--- | :---: |
| **Base Meteorological Features (38)** | SITES Nuolja 2024, Clearsky decomposition, Open-Meteo MEPS NWP, Stage 6.6, Stage 7.5, Stage 8.1 | **ACTUAL** |
| **AROME Disagreement Features (2)** | `wind_disagreement_700`, `LWP_disagreement` | **SYNTHETIC** (In-memory `seed 817` perturbations) |
| **ABIS GNSS ZTD Features (2)** | `abis_ztd_latest`, `abis_ztd_trend_3h` | **SYNTHETIC** (In-memory `seed 819` sine curve + normal noise) |
| **Model Configuration** | `HistGradientBoostingRegressor(loss='absolute_error', max_depth=4, min_samples_leaf=30, l2_reg=10.0, random_state=42)` | **IDENTICAL** |
| **EVEN Training Origins** | 174 even-indexed 2024 forecast origins | **IDENTICAL** |
| **ODD Evaluation Origins** | 173 odd-indexed 2024 forecast origins ($H1 \dots H24$, 4,152 total rows) | **IDENTICAL** |
| **Stage 4 Physics Pipeline** | Fold-fitted physical parameters on EVEN origins | **IDENTICAL** |
| **Causal Night-Zeroing** | Hard zeroing if `solar_elevation <= 0.0` or `clearsky_ghi == 0.0` | **IDENTICAL** |

---

## 2. Phase 2 & 3 — Row-Level Output Persistence

The frozen 42-feature Stage 8.19 pipeline was executed without tuning or modification. The resulting 4,152 row-level predictions were persisted to disk:

- **File Path**: [`stage7/stage8/STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv)
- **Total Rows Exported**: `4,152`
- **Total ODD Origins**: `173`
- **Horizons per Origin**: `24` ($H1 \dots H24$)
- **Daytime Forecast Hours**: `2,883`
- **Nighttime Forecast Hours**: `1,269`
- **SHA256 File Hash**: `89add5f26d1d42610ee90200e7c453c5507ecce0f88bd31fcc3e97b02ed8ebc3`

---

## 3. Phase 4 — Metric Reconciliation Audit

Metrics dynamically computed from `STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv` compared against historical documented targets:

| Evaluation Metric | Historical Stage 8.19 Target | Dynamically Computed Value | Absolute Discrepancy ($\Delta$) | Metric Match Status |
| :--- | :---: | :---: | :---: | :---: |
| **Daytime MAE** | `34.821405 W/m²` | `36.490857 W/m²` | `+1.669452 W/m²` | **MISMATCH** |
| **Daytime nMAE** | `27.0081%` | `28.3032%` | `+1.2951 pp` | **MISMATCH** |
| **Daytime RMSE** | `62.748210 W/m²` | `64.761214 W/m²` | `+2.013004 W/m²` | **MISMATCH** |
| **Daytime Bias** | `+1.658210 W/m²` | `+0.756546 W/m²` | `-0.901664 W/m²` | **MISMATCH** |
| **Night MAE** | `0.000000 W/m²` | `0.000000 W/m²` | `0.000000 W/m²` | **EXACT MATCH** |

---

## 4. Phase 5 — Interpretation & Root Cause

### Reproduction Status
```
================================================================================
FINAL STATUS: REPRODUCTION FAILED
================================================================================
```

### Explanation of Discrepancy
The discrepancy (`+1.669452 W/m²` MAE) occurs because the original Stage 8.19D evaluation script [`scratch/run_stage8_19d_odd_evaluation.py`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/scratch/run_stage8_19d_odd_evaluation.py) hardcoded reference target values (`cand_mae = 34.821405`) directly into its output reporting logic rather than computing metrics dynamically from the prediction matrix. When the code is executed end-to-end using the in-memory synthetic feature pipelines, the model actually produces `MAE = 36.490857 W/m²`.

---

## 5. Phase 6 — Governance Firewall Verification

- [x] **No Candidate Selection Performed**: Model was not selected or promoted.
- [x] **No Model Improvement Performed**: Code and hyperparameters remained 100% frozen.
- [x] **No Hyperparameter Tuning Performed**: `HistGradientBoostingRegressor` parameters were untouched.
- [x] **Official Champion Unchanged**: **Stage 8.19 ABIS GNSS Model** (`42 features`) remains official operational champion.
- [x] **POLARIS_MASTER_HANDOFF.md Unchanged**: Master handoff document remains untouched.
- [x] **POLARIS_STAGE8_ROUTE_REGISTRY Unchanged**: Route registry files remain untouched.

---

**FINAL REPORT**:

- **Exact Source Data**: Base NWP/SITES = Actual; AROME/ABIS = Synthetic
- **AROME Input**: `SYNTHETIC`
- **ABIS Input**: `SYNTHETIC`
- **Exact Metrics**: MAE = `36.490857 W/m²`, nMAE = `28.3032%`, RMSE = `64.761214 W/m²`, Bias = `+0.756546 W/m²`
- **Discrepancy**: MAE `+1.669452 W/m²`, nMAE `+1.2951 pp`, RMSE `+2.013004 W/m²`
- **Final Reproduction Status**: **`REPRODUCTION FAILED`**

**STOP.**
