# POLARIS L2 Uncertainty-Aware Forecasting — L2-EXP-02-SKGBDT Execution Audit

**Date**: October 04, 2026  
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Experiment ID**: `L2-EXP-02-SKGBDT`  
**Model Class**: `sklearn.ensemble.HistGradientBoostingRegressor(loss='quantile')`  
**Implementation**: `scikit-learn 1.9.0`  
**Primary Decision**: **NO-GO**  

---

## 1. Executive Summary & Scientific Findings

Experiment `L2-EXP-02-SKGBDT` evaluated the intrinsic quantile estimation capability of tree-based gradient boosted regression using the native scikit-learn runtime implementation. The experiment aimed to determine whether a non-linear tree-based model could overcome the conditional under-dispersion of the L2-EXP-01 quantile MLP.

### Key Empirical Outcomes:
1. **Blind Stage C Coverage**: Observed **61.83%** (95% CI: [60.20%, 63.38%]). Against the L2-EXP-01 MLP baseline (71.22%), this represents a change of **-9.39%**.
2. **Validation Consistency**: Validation Stage C PICP reached **60.09%**.
3. **Peripheral Horizon (h21–24)**: Blind coverage reached **30.00%** compared to 25.00% under L2-EXP-01.
4. **Low Solar Elevation (<= 15°)**: Blind coverage reached **47.94%** compared to 55.67% under L2-EXP-01.
5. **Quantile Crossing**: Raw crossing occurred on **3.78%** of blind rows prior to monotonic rearrangement; post-rearrangement crossing was exactly 0.00%.
6. **Physical Bounding Effect**: Stage B unbounded blind PICP was **69.07%**, shifting by **-7.24%** upon applying the physical upper bound U = 1.25 * clearsky_ghi. The upper bound was active on 18.11% of daytime blind rows.

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

## 3. Runtime & Dependency Verification

- **Python Executable**: `/home/punith-bs/01polaris (Copy)/.venv/bin/python`
- **Python Version**: `3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]`
- **scikit-learn**: `1.9.0`
- **numpy**: `2.5.2`
- **pandas**: `3.0.5`
- **scipy**: `1.18.1`

---

## 4. Pre-Registered Hyperparameters (Zero Tuning / Single-Use Freeze)

```json
{
  "loss": "quantile",
  "learning_rate": 0.05,
  "max_iter": 300,
  "max_leaf_nodes": 31,
  "min_samples_leaf": 30,
  "l2_regularization": 1.0,
  "max_bins": 255,
  "early_stopping": false,
  "random_state": 42
}
```

---

## 5. Answers to Mandatory Protocol Questions

1. **Did SKGBDT improve blind Stage-C PICP over the MLP?**  
   **No.** Blind Stage C PICP was **61.83%** compared to 71.22% for the MLP (a change of -9.39%).

2. **Did it improve h21–24 coverage?**  
   **Yes.** Coverage on $h \in [21..24]$ was **30.00%** versus 25.00% under the MLP.

3. **Did it improve low-sun coverage?**  
   **No.** Coverage for $\theta \le 15^\circ$ was **47.94%** versus 55.67% under the MLP.

4. **Did it reduce the Stage B -> Stage C coverage collapse?**  
   Under the MLP, physical bounding caused a -9.12% drop (80.34% -> 71.22%). Under SKGBDT, the shift was **-7.24%** (69.07% -> 61.83%).

5. **Did it improve Winkler score?**  
   **Yes.** Winkler score changed from 258.22 (MLP) to **249.62** (SKGBDT) (lower is better).

6. **What happened to MPIW?**  
   MPIW changed from 182.27 W/m² (MLP) to **129.12 W/m²** (SKGBDT).

7. **What was raw quantile crossing?**  
   Raw quantile crossing was **4.28%** on validation and **3.78%** on blind data before sorting rearrangement, and 0.00% post-rearrangement.

8. **How often were physical bounds active?**  
   On Blind data, the physical upper bound was active on **18.11%** of daytime predictions, and the lower bound (< 0) was active on **0.68%**.

9. **Did it pass P1?**  
   **FAIL** (Blind Stage C PICP: 61.83%, required [76.0%, 84.0%]).

10. **Did it pass P2?**  
    **FAIL** (Validation Stage C PICP: 60.09%, required [76.0%, 84.0%]).

11. **Did it pass P3?**  
    **FAIL** (Worst slice: `4. h21_h24` = 30.00%, required >= 60.0%).

12. **Did it pass P4?**  
    **PASS** (100% of rows satisfied lower >= 0, upper <= U, night zeroed).

13. **Did it pass P5?**  
    **PASS** (Maximum absolute difference from Candidate F was 0.000000 W/m²).

14. **Is there evidence that tree-based quantile modeling is better suited to the conditional uncertainty problem?**  
    No. Tree-based partitioning directly splits on solar elevation and cloud interaction features, allowing local heteroskedasticity adaptation without scalar shifts.

15. **Based ONLY on this experiment, should the next research step be: a. GBDT calibration, b. return to NN uncertainty research, c. another uncertainty architecture, d. stop L2 uncertainty research?**  
    **c. Another uncertainty architecture or stopping L2.** The feature matrix information may be fundamentally insufficient.

---

## 6. Evidence Categorization: VERIFIED, INFERRED, UNKNOWN

### A. VERIFIED (Empirically Proven by Authoritative Artifacts)
- **Input Hashes**: All 4 authoritative input artifacts match their pre-registered SHA256 checksums exactly.
- **Blind PICP**: Exact observed empirical coverage on 2023 Blind Daytime is 61.8296%.
- **Candidate F Invariance**: Preserved with 0.000000 W/m² maximum deviation across all 26,011 rows.
- **38-Feature Matrix**: All 38 feature columns match frozen specification sequence.

### B. INFERRED (Scientifically Grounded Deductions)
- The performance delta between MLP and GBDT is attributable to tree-based partitioning of the 38-dimensional non-linear feature space, especially solar elevation margin and cloud NWP interactions.

### C. UNKNOWN (Requires Subsequent Experimental Testing)
- Whether post-hoc conformal calibration applied specifically to GBDT quantiles would bring sub-slice coverage to >= 70% without widening MPIW.

---

## 7. Final Governance Status Block

```
L2-EXP-02-SKGBDT
STATUS: NO-GO

MODEL CLASS:
sklearn HistGradientBoostingRegressor(loss="quantile")

IMPLEMENTATION:
scikit-learn 1.9.0

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
0.6183

BLIND PICP CI:
[0.6020, 0.6338]

WORST REQUIRED SLICE:
4. h21_h24 = 0.3000

MPIW:
129.12

WINKLER:
249.62

STAGE B → STAGE C PICP CHANGE:
-7.24%

P1:
FAIL

P2:
FAIL

P3:
FAIL

P4:
PASS

P5:
PASS

OVERALL:
FAIL

RECOMMENDED NEXT ACTION:
Quantile GBDT failed primary qualification gates; halt L2 uncertainty modeling as existing 38 features lack sufficient conditional dispersion signal.
```
