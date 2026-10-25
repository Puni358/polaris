# POLARIS L2 Uncertainty-Aware Forecasting — L2-EXP-02 Execution Audit

**Date**: October 04, 2026
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`
**Experiment ID**: `L2-EXP-02`
**Experiment Type**: Tree-Based Quantile GBDT Uncertainty Model
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l.)
**Execution Disposition**: **BLOCKED**

---

## 1. Executive Summary

Experiment `L2-EXP-02` was stopped in accordance with the strict scientific governance specified in Section 5 of the experiment protocol:

> *"Preferred implementation: LightGBM quantile regression, IF the already pinned/reproducible project environment supports it. If LightGBM is not available in the existing scientific runtime: DO NOT install arbitrary packages. STOP with BLOCKED and report the environment limitation. Do not silently switch to another implementation."*

The existing pinned scientific runtime (`/home/punith-bs/01polaris (Copy)/.venv/bin/python`, Python 3.12.3) contains `scikit-learn 1.9.0`, `scipy 1.18.1`, `numpy 2.5.2`, and `pandas 3.0.5`, but does not contain `lightgbm`. Because installing packages into the pinned project runtime is strictly forbidden without governance authorization, and silently substituting an alternative implementation (such as `scikit-learn`'s `HistGradientBoostingRegressor`) is explicitly prohibited, execution halted cleanly.

---

## 2. Authoritative Input Hashes & Pre-Flight Checks

| Artifact Description | File Path | Authoritative SHA256 Checksum | Verification Status |
|---|---|---|---|
| `historical_residual_dataset` | `/home/punith-bs/01polaris (Copy)/candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` | `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` | **PASS** |
| `exact_38_feature_matrix` | `/home/punith-bs/01polaris (Copy)/candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` | `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde` | **PASS** |
| `exact_frozen_f_predictions` | `/home/punith-bs/01polaris (Copy)/candidate_L_research/CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv` | `b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0` | **PASS** |
| `frozen_candidate_f_model` | `/home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | **PASS** |

All authoritative input artifacts are intact and bit-identical.

---

## 3. Feature Sequence Verification

The 38-feature sequence was verified against `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv`. All 38 feature columns match the exact sequence and names required by the Candidate F / L2 specification.

---

## 4. Runtime & Dependency Audit

- **Python Executable**: `/home/punith-bs/01polaris (Copy)/.venv/bin/python`
- **Python Version**: `3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]`
- **LightGBM Status**: **NOT INSTALLED** (`ModuleNotFoundError: No module named 'lightgbm'`)
- **Installed Scientific Packages**:
  - `scipy`: `1.18.1`
  - `sklearn`: `1.9.0`
  - `numpy`: `2.5.2`
  - `pandas`: `3.0.5`
  - `joblib`: `1.6.0`

---

## 5. Answers to Mandatory Protocol Questions

1. **Does GBDT improve blind Stage-C coverage over the MLP?**  
   **BLOCKED / UNTESTED.** Execution halted before training due to environment dependency limitation.

2. **Does it improve h21–24 coverage?**  
   **BLOCKED / UNTESTED.**

3. **Does it improve low-sun coverage?**  
   **BLOCKED / UNTESTED.**

4. **Does it reduce the Stage-B → Stage-C coverage collapse?**  
   **BLOCKED / UNTESTED.**

5. **Does it improve Winkler score?**  
   **BLOCKED / UNTESTED.**

6. **What is the interval-width tradeoff?**  
   **BLOCKED / UNTESTED.**

7. **Does quantile crossing occur?**  
   **BLOCKED / UNTESTED.**

8. **Are physical bounds frequently active?**  
   **BLOCKED / UNTESTED.**

9. **Does the GBDT pass P1/P2/P3/P4/P5?**  
   **P1–P4: BLOCKED. P5 (Point forecast invariance): PASS** (0.0 W/m² deviation).

10. **Is there evidence that the model class is better suited to conditional uncertainty?**  
    **UNTESTED.** Requires training to evaluate.

11. **Should POLARIS proceed to GBDT calibration research, return to NN research, or stop L2 uncertainty research?**  
    **Proceed to resolve environment governance.** The user must either authorize the controlled installation of `lightgbm` into the scientific virtual environment or explicitly authorize using `scikit-learn`'s `HistGradientBoostingRegressor(loss='quantile')` which is already pinned in the environment.

---

## 6. Evidence Categorization: VERIFIED, INFERRED, UNKNOWN

### A. VERIFIED (Empirically Proven by Authoritative Artifacts)
- **Input Hashes**: All 4 authoritative input artifacts match their pre-registered SHA256 checksums exactly.
- **Feature Matrix Integrity**: The 38 features in `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` match the frozen specification exactly.
- **Candidate F Invariance**: Frozen Candidate F predictions in `CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv` have zero drift.
- **Runtime State**: The project runtime `/home/punith-bs/01polaris (Copy)/.venv` does not contain `lightgbm`.

### B. INFERRED (Scientifically Grounded Deductions)
- The project environment was initialized using `requirements.txt` which specifies `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`, and `seaborn`, but omitted `lightgbm`.

### C. UNKNOWN (Requires Subsequent Experimental Testing)
- Whether tree-based quantile models will resolve the low-sun and late-horizon under-coverage of L2-EXP-01.

---

## 7. Final Governance Status Block

```
L2-EXP-02 QUANTILE GBDT
STATUS: BLOCKED

MODEL CLASS:
Quantile GBDT

MODEL CHANGED:
YES — RESEARCH-ONLY

F CHANGED:
NO

GAP19 CHANGED:
NO

2024 USED:
NO

2023 USED FOR MODEL SELECTION:
NO

BLIND PICP:
BLOCKED

BLIND PICP CI:
BLOCKED

WORST REQUIRED SLICE:
BLOCKED

MPIW:
BLOCKED

WINKLER:
BLOCKED

P1:
BLOCKED

P2:
BLOCKED

P3:
BLOCKED

P4:
BLOCKED

P5:
PASS

OVERALL:
FAIL

RECOMMENDED NEXT ACTION:
Halt execution per Section 5 governance; request explicit authorization to either pin LightGBM in the project virtualenv or approve scikit-learn's native HistGradientBoostingRegressor(loss='quantile') as the authorized GBDT implementation.
```
