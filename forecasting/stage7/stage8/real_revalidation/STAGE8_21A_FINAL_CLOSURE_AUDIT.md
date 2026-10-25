# STAGE 8.21A FINAL CLOSURE & NUMERICAL PROVENANCE AUDIT

**Audit Timestamp:** `2026-09-13T10:16:39.466431+00:00`  
**Audit Target:** Stage 8.21A EVEN-Only Validation Artifacts  
**Final Conclusion:** **`VERIFIED_REJECTED_ON_EVEN`**  

---

## 1. G4 Proof (nMAE & RMSE Recomputation)

| Metric | Control | Candidate | Recomputed Delta | Locked Rule | Result |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Daytime nMAE (%)** | `29.2063%` | `29.1841%` | `-0.0222%` | `delta_nmae <= 0` | **PASS** |
| **Daytime RMSE (W/m²)** | `60.1606` | `60.1587` | `-0.0019` | `delta_rmse <= 0` | **PASS** |

**G4 Rule Verification:** Derived directly from persisted EVEN validation predictions/metrics. Gate G4 passed (`delta_nmae <= 0` and `delta_rmse <= 0`).

---

## 2. Fallback Provenance Audit

- **Relevant Solar Rays (>= 5° elevation):** `3,285`
- **Direct 3D Spatial Window Rays (47x47):** `3,262` (99.30%)
- **Outside-Window Deterministic Fallback Rays:** `23` (0.70%)
- **Evaluation Population:** All 23 fallback rays were retained inside the EVEN metric population without dropping, filtering, or NaN assignment.
- **Fallback Implementation:** Uses the locked 1D station-column vertical path length (ds = dz_cloud).

---

## 3. Feature Integrity Audit

- **Frozen Stage 8.1 Baseline Features:** `37`
- **Added Stage 8.21A 3D Slant-Path Features:** `4`
  1. `slant_path_optical_depth_proxy`
  2. `slant_path_direct_transmittance`
  3. `slant_path_liquid_water_path`
  4. `slant_path_ice_water_path`
- **Total Candidate Features:** `41`
- **Hidden / Altered Features:** `NONE`

---

## 4. Fold Provenance Audit

| Fold | Observed Delta MAE (W/m²) | Expected Delta MAE (W/m²) | Improved |
| :--- | :--- | :--- | :---: |
| **Fold 1** | `+0.2541` | `+0.2541` | NO |
| **Fold 2** | `-0.5699` | `-0.5699` | **YES** |
| **Fold 3** | `+0.1777` | `+0.1777` | NO |
| **Fold 4** | `+0.0017` | `+0.0017` | NO |
| **Fold 5** | `-0.0061` | `-0.0061` | **YES** |

- **Improving Folds:** `2 / 5` (Fold 2 & Fold 5)
- **Gate G2 Requirement:** `improving_folds >= 4` => **G2 FAILED**
- **Worst Fold Degradation:** `+0.2541 W/m²` (<= 0.50 W/m², G3 Passed)

---

## 5. Control Reproduction Audit

- **Observed EVEN Control MAE:** `37.6201 W/m²`
- **Expected Stage 8.1 Champion Baseline:** `37.6201 W/m²`
- **Exact Match:** `PASS` (Corresponds to locked Stage 8.1 37-feature HGB architecture).

---

## 6. Governance Audit

- **ODD Target Access:** `FALSE` (ODD targets were never read or evaluated).
- **ODD Run Status:** `ODD_RUN = FALSE`
- **ODD Prediction / Metric Artifacts:** `NONE`
- **Operational Champion:** Stage 8.1 37-feature champion remains frozen and operational.
- **System Governance Files:** `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY` remain untouched.

---

## 7. Official Statement of Final Closure

> [!IMPORTANT]
> **Stage 8.21A is formally closed as REJECTED ON EVEN without ODD evaluation.**
>
> The 4-feature 3D solar slant-path hydrometeor geometry failed acceptance gate G2 (improving in only 2 of 5 forward-chaining folds, whereas >= 4 folds are required).
>
> In accordance with strict governance rules:
> 1. ODD target data was never accessed.
> 2. No model tuning or feature subsetting was performed.
> 3. The Stage 8.1 37-feature HGB model remains the operational champion.
