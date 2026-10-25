# POLARIS STAGE 8.21A — EVEN-ONLY VALIDATION REPORT

**Execution Timestamp:** `2026-09-13T10:12:14.954522+00:00`
**Spatial Window:** 47×47 MEPS grid (57.5 km cardinal radius)
**Baseline Control:** Frozen Stage 8.1 37-feature Champion
**Candidate Feature Set:** 41 features (37 baseline + 4 Stage 8.21A 3D slant-path features)

---

## 1. EVEN 5-Fold Cross-Validation Summary

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) | Delta nMAE (%) | Control RMSE (W/m²) | Candidate RMSE (W/m²) | Delta RMSE (W/m²) | Improved |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | 49.3114 | 49.5655 | +0.2541 | 29.5265 | 29.6786 | +0.1521 | 81.3550 | 81.7334 | +0.3784 | NO |
| 2 | 70.5688 | 69.9989 | -0.5699 | 36.9196 | 36.6215 | -0.2981 | 103.7439 | 103.4081 | -0.3358 | YES |
| 3 | 40.3456 | 40.5233 | +0.1777 | 28.1423 | 28.2662 | +0.1240 | 67.2567 | 67.3239 | +0.0672 | NO |
| 4 | 25.7704 | 25.7721 | +0.0017 | 36.7313 | 36.7337 | +0.0024 | 44.6132 | 44.4596 | -0.1536 | NO |
| 5 | 2.1041 | 2.0979 | -0.0061 | 58.5528 | 58.3822 | -0.1706 | 3.8345 | 3.8687 | +0.0342 | YES |

**Mean EVEN Control MAE:** `37.6201 W/m²`
**Mean EVEN Candidate MAE:** `37.5916 W/m²`
**Mean EVEN Delta MAE:** `-0.0285 W/m²`

---

## 2. Predefined Acceptance Gate Evaluation

| Gate ID | Description | Requirement | Observed Value | Result |
| :--- | :--- | :--- | :--- | :---: |
| **G1** | MAE Improvement | `even_delta_mae < 0` | `-0.0285 W/m²` | **PASS** |
| **G2** | Fold Consistency | `improving_folds >= 4` | `2 / 5 folds` | **FAIL** |
| **G3** | Worst-Fold Tolerance | `worst_fold_degradation <= 0.50 W/m²` | `+0.2541 W/m²` | **PASS** |
| **G4** | nMAE / RMSE Non-Degradation | `delta_nmae <= 0` & `delta_rmse <= 0` | `nMAE: -0.0221%, RMSE: -0.0019` | **PASS** |
| **G5** | Causal Integrity | `causal_pass == True` | `VERIFIED` | **PASS** |
| **G6** | Control Reproduction | Matches Stage 8.1 baseline | `37.6201 W/m²` | **PASS** |

**EVEN GATES VERDICT:** **FAIL**

---

## 3. Governance Decision

> [!WARNING]
> **GATE FAILURE DETECTED ON G2 (Fold Consistency):** Only 2 out of 5 forward-chaining folds demonstrated MAE improvement. Protocol rules mandate a minimum of 4 improving folds to pass G2.
>
> Under locked governance rules:
> - **CANDIDATE FROZEN:** No tuning, no feature selection, no hyperparameter adjustment.
> - **ODD EVALUATION:** **HALTED (ODD_RUN = FALSE)**. ODD target data remained uninspected.
> - **CLASSIFICATION:** **REJECTED ON EVEN**
