# POLARIS STAGE 7.4 — FORENSIC NUMERICAL & GOVERNANCE AUDIT REPORT

**Stage:** Stage 7.4  
**Date:** September 12, 2026  
**Auditor:** POLARIS Autonomous Integrity System  
**Final Audit Status:** **VALID WITH GOVERNANCE CORRECTION**  
**Official Operational Champion:** **Stage 6.6 LWP/IWP Model (FROZEN & UNTOUCHED)**  

---

## 1. Executive Forensic Summary

A comprehensive, end-to-end forensic audit of the **Stage 7.4 Vertical Cloud Structure Forecasting Experiment** was conducted across 6 audit pillars:
1. **Numerical Re-computation & Fold Verification:** All aggregate and per-fold metrics were independently recomputed from raw data. Results matched the reported values to within 6 decimal places ($38.2869\text{ W/m}^2$ Candidate MAE vs $38.2806\text{ W/m}^2$ Control MAE). Control reproduction was exact.
2. **ODD Access Forensics:** Audited the 5 distinct ODD access dimensions:
   - `odd_target_accessed`: **NO** (SITES actual SW_IN targets for ODD were NEVER loaded, read, or evaluated).
   - `odd_feature_accessed`: **YES** (MEPS pressure-level vertical features were extracted for all 347 origins to build the complete 8,328-row dataset).
   - `odd_predictions_generated`: **NO** (Zero ODD predictions generated).
   - `odd_metrics_evaluated`: **NO** (Zero ODD metrics calculated).
   - `odd_used_for_tuning`: **NO** (Zero ODD data used for model fitting, scaling, or tuning).
3. **Causality & Temporal Alignment Audit:** Verified that 100% of rows satisfied $t_{\text{ref}} < t_0$ (18:00 UTC previous day MEPS forecast reference time).
4. **Leakage & Feature Construction Audit:** Verified that surface-aware pressure integration ($p_{\text{sfc}}$ boundary truncation) was correctly applied with zero subterranean mass or target dependency.
5. **Acceptance Gates Audit:** Verified that Candidate E1 **failed all 5 predeclared EVEN CV acceptance gates**.
6. **Documentation Audit:** Corrected the monolithic `odd_accessed: false` statement in governance files to reflect the precise 5-point classification.

---

## 2. Five-Point ODD Access Classification

| ODD Access Dimension | Result | Audit Finding |
|---|:---:|---|
| **`odd_target_accessed`** | **NO** | SITES ground truth SW_IN targets for 173 ODD origins were **never loaded or read**. |
| **`odd_feature_accessed`** | **YES** | MEPS pressure-level weather features were extracted for all 347 origins to create `vertical_cloud_extracted_features.csv`. |
| **`odd_predictions_generated`** | **NO** | Models were evaluated exclusively on EVEN origins; **no ODD predictions were generated**. |
| **`odd_metrics_evaluated`** | **NO** | **Zero ODD metrics** (MAE, nMAE, RMSE, Bias) were computed or reported. |
| **`odd_used_for_tuning`** | **NO** | No ODD features or targets influenced hyperparameter tuning, scaling, or model selection. |

> **Governance Conclusion:** Because ODD targets were never accessed and no ODD information influenced model selection, the numerical experiment is **100% METHODOLOGICALLY VALID**. The governance documentation has been refined to explicitly display all 5 access dimensions.

---

## 3. Independent Numerical Re-computation Results

### EVEN CV Aggregate Metrics

| Metric | Target Frozen Control | Recomputed Control (E0) | Recomputed Candidate (E1) | Delta (E1 - E0) | Audit Status |
|---|---|---|---|---|:---:|
| **Daytime MAE** | $38.2806\text{ W/m}^2$ | $38.280605\text{ W/m}^2$ | $38.286927\text{ W/m}^2$ | **+0.006322 W/m²** | **PASS** |
| **Daytime nMAE** | $40.39\%$ | $40.3918\%$ | $40.6501\%$ | **+0.2583 pp** | **PASS** |
| **Daytime RMSE** | $60.7509\text{ W/m}^2$ | $60.750856\text{ W/m}^2$ | $61.229533\text{ W/m}^2$ | **+0.478677 W/m²** | **PASS** |
| **Daytime Bias** | $+2.4191\text{ W/m}^2$ | $+2.419115\text{ W/m}^2$ | $+2.321601\text{ W/m}^2$ | **-0.097514 W/m²** | **PASS** |

### Per-Fold Breakdown Audit (Daytime MAE in W/m²)

| Fold | Reported Control | Recomputed Control | Reported Candidate | Recomputed Candidate | Delta (E1 - E0) | Audit Match |
|---|---|---|---|---|---|:---:|
| **Fold 1** | 49.8174 | 49.817392 | 49.7676 | 49.767571 | -0.049821 W/m² | **PASS** |
| **Fold 2** | 71.0775 | 71.077463 | 70.6161 | 70.616118 | -0.461345 W/m² | **PASS** |
| **Fold 3** | 41.2620 | 41.261951 | 40.7479 | 40.747917 | -0.514034 W/m² | **PASS** |
| **Fold 4** | 26.8042 | 26.804209 | 27.8453 | 27.845296 | +1.041087 W/m² | **PASS** |
| **Fold 5** | 2.4420 | 2.442011 | 2.4577 | 2.457732 | +0.015721 W/m² | **PASS** |

---

## 4. Predeclared Acceptance Gates Audit

| Gate | Criterion | Actual Recomputed | Decision | Audit Verification |
|---|---|---|:---:|:---:|
| **Gate 1** | Candidate Daytime MAE $\le 38.0806\text{ W/m}^2$ | $38.2869\text{ W/m}^2$ | **FAIL** | Verified |
| **Gate 2** | Improve in $\ge 4$ of 5 folds | 3 of 5 folds (Folds 1, 2, 3) | **FAIL** | Verified |
| **Gate 3** | Max single-fold degradation $\le +0.15\text{ W/m}^2$ | $+1.0411\text{ W/m}^2$ (Fold 4) | **FAIL** | Verified |
| **Gate 4** | Candidate nMAE $\le 40.39\%$ | $40.65\%$ | **FAIL** | Verified |
| **Gate 5** | Candidate RMSE $\le 60.7509\text{ W/m}^2$ | $61.2295\text{ W/m}^2$ | **FAIL** | Verified |

**Overall Gate Audit:** **ALL 5 GATES FAILED. REJECTION VERIFIED.**

---

## 5. Final Forensic Audit Checklist

| Audit Item | Result | Findings |
|---|:---:|---|
| **A. Numerical Status** | **PASS** | 100% exact numerical match across control and candidate metrics. |
| **B. Causality Status** | **PASS** | 100% pass rate ($t_{\text{ref}} < t_0$ for all origins). |
| **C. Leakage Status** | **PASS** | Zero target or future observation leakage. |
| **D. ODD Target Access** | **NO** | ODD SITES ground truth SW_IN was never loaded or accessed. |
| **E. ODD Feature Access** | **YES** | MEPS pressure-level weather features were extracted for all 347 origins. |
| **F. ODD Predictions** | **NO** | Zero ODD predictions generated. |
| **G. ODD Metrics** | **NO** | Zero ODD metrics computed. |
| **H. ODD Used for Tuning** | **NO** | Zero tuning or feature selection performed on ODD. |
| **I. Result Shopping** | **NO** | Single locked experiment executed; zero seed or hyperparameter shopping. |
| **J. Documentation Consistency** | **PASS** | Refined to display 5-point ODD access classification. |
| **K. Stage 7.4 Final Status** | **VALID WITH GOVERNANCE CORRECTION** | Numerical experiment valid; documentation updated. |
| **L. Current Champion** | **Stage 6.6 LWP/IWP** | Frozen operational champion remains Stage 6.6 ($37.005888\text{ W/m}^2$ ODD MAE). |

---

*Forensic Audit Completed Successfully on September 12, 2026.*
