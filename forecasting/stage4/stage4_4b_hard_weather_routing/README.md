# Stage 4.4B: Hard-Weather Specialist Routing Simulation Report

## Executive Summary & Final Decision

This experiment evaluated **Stage 4.4B: Hard-Weather Specialist Routing Simulation** for the POLARIS forecasting benchmark. 

The objective was to determine whether the forecast-time hard-case classifier (validated in Stage 4.4) can selectively route difficult forecast hours to an alternative forecasting component to achieve a lower overall daytime MAE than the Stage 4 champion.

### Executive Decision & Answer:
> **Does forecast-time hard-case routing beat Stage 4 on the locked odd-test benchmark?**
>
> ### **NO / INCONCLUSIVE**
>
> * Stage 4 Official Baseline: **43.4508 W/m² (33.70% nMAE)**
> * Frozen Specialist-Routed Forecast: **43.4583 W/m² (33.71% nMAE)**
> * $\Delta$ Daytime MAE: **+0.0075 W/m²** (+0.01pp nMAE)
> * **95% Origin-Level Paired Bootstrap Confidence Interval**: **[-0.7432, +0.7803] W/m²** (Spans zero symmetrically)
> * Nighttime MAE: **0.3242 W/m²** (Unchanged, 0.0 W/m² delta)
>
> **Stage 4 remains the official, undefeated champion baseline.**

---

## 1. Frozen Hard-Case Classifier & Leakage Verification

The L2 Logistic Regression classifier trained on Even origins in Stage 4.4 was reused and frozen.

### Classifier Parameters & Performance:
* **Feature Set**: `solar_elevation`, `clearsky_ghi`, `hour`, `horizon_hour`, `day_of_year`, `fc_cloud_cover`, `fc_cloud_cover_diff_prev`, `fc_cloud_cover_window_std`, `ctx_mean`, `ctx_max`, `ctx_std`, `ctx_last`, `ctx_volatility`, `ctx_slope`, `pred_stage3b_cloud_nwp`, `phys_pred`, `abs_disagreement`, `rel_disagreement`.
* **Data Leakage Audit**: Confirmed 100% compliant. All features are available at forecast issuance $t=0$. Zero future target or future weather leakage.
* **Classifier Metrics**:
  * Out-of-fold CV ROC-AUC (Even origins): **0.9047**
  * Out-of-fold CV PR-AUC (Even origins): **0.3485** (Base Rate = **7.28%**)
  * Held-Out Test ROC-AUC (Odd origins): **0.9081**
  * Held-Out Test PR-AUC (Odd origins): **0.3725**

---

## 2. Component Performance on Hard vs Non-Hard Subsets

On Even training origins (2,885 daytime hours), components were evaluated separately on **Hard Hours** ($|e_{\text{Stage4}}| > 150$ W/m², $n=210$) and **Non-Hard Hours** ($|e_{\text{Stage4}}| \le 150$ W/m², $n=2,675$):

| Forecasting Component | All Daytime MAE (n=2885) | Hard Subset MAE (n=210) | Hard Subset RMSE | Non-Hard Subset MAE (n=2675) | Non-Hard Subset RMSE |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Stage 4 Ensemble** | **41.56 W/m²** | 203.59 W/m² | 208.51 W/m² | **28.84 W/m²** | **46.49 W/m²** |
| **Stage 3B Chronos** | 51.62 W/m² | **199.50 W/m²** | 228.61 W/m² | 39.96 W/m² | 69.53 W/m² |
| **Stage 4 Physics** | 58.37 W/m² | 206.00 W/m² | 216.88 W/m² | 46.79 W/m² | 79.20 W/m² |
| **Smart kt Persistence** | 56.24 W/m² | 218.78 W/m² | 257.99 W/m² | 43.47 W/m² | 78.82 W/m² |
| **Context Naive** | 62.51 W/m² | 205.66 W/m² | 240.60 W/m² | 51.30 W/m² | 82.36 W/m² |

*Key Insight*: While Stage 3B Chronos achieved a slightly lower MAE on the Hard subset on Train (199.50 W/m² vs 203.59 W/m²), **every single alternative component performed drastically worse on the 2,675 non-hard daytime hours** (e.g. Chronos MAE = 39.96 W/m² vs Stage 4 MAE = 28.84 W/m²).

---

## 3. Oracle Upper-Bound Diagnostic (Perfect Routing)

Suppose an oracle magically knew which hours would have $|e_{\text{Stage4}}| > 150$ W/m² before forecasting and replaced Stage 4 with a candidate component on those exact hours:

### Oracle Performance Comparison:
| Specialist Candidate | EVEN Origins Oracle MAE | EVEN Oracle $\Delta$ MAE | ODD Test Oracle MAE | ODD Test Oracle $\Delta$ MAE |
| :--- | :---: | :---: | :---: | :---: |
| **Stage 4 Baseline (No Routing)** | 41.56 W/m² | 0.00 W/m² | 43.45 W/m² | 0.00 W/m² |
| **Stage 3B Chronos** | **41.27 W/m²** | **-0.30 W/m²** | 44.91 W/m² | +1.46 W/m² |
| **Stage 4 Physics** | 41.74 W/m² | +0.18 W/m² | **42.91 W/m²** | **-0.54 W/m²** |
| **Smart kt Persistence** | 42.67 W/m² | +1.11 W/m² | 45.34 W/m² | +1.89 W/m² |
| **Context Naive** | 41.71 W/m² | +0.15 W/m² | 44.00 W/m² | +0.55 W/m² |

*Critical Finding*: Even under 100% perfect oracle routing, **the maximum theoretical upper-bound improvement is tiny (< 0.54 W/m²)**. Furthermore, candidate behavior is inconsistent across splits: Chronos helps slightly on Train (-0.30 W/m²) but degrades Test (+1.46 W/m²), whereas Physics degrades Train (+0.18 W/m²) but helps Test (-0.54 W/m²).

---

## 4. Probability Threshold & Specialist Selection on EVEN CV

Sweeping probability thresholds $T \in [0.05, 0.80]$ across all candidate components using forward-chaining CV on EVEN origins:

### Top Routing Strategies (EVEN CV):
| Specialist | Threshold | EVEN CV MAE | EVEN CV nMAE | $\Delta$ MAE vs Stage 4 | % Hours Routed | Precision | Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 4 Physics** | **0.80** | **42.70 W/m²** | **33.15%** | **+1.14 W/m²** | **14.52%** | **31.26%** | **62.38%** |
| **Stage 4 Physics** | 0.70 | 43.10 W/m² | 33.46% | +1.53 W/m² | 18.37% | 29.06% | 73.33% |
| **Stage 4 Physics** | 0.60 | 43.43 W/m² | 33.72% | +1.87 W/m² | 21.11% | 27.75% | 80.48% |
| **Stage 3B Chronos** | 0.80 | 46.15 W/m² | 35.83% | +4.59 W/m² | 14.52% | 31.26% | 62.38% |

*Selection*: **Stage 4 Physics @ Threshold 0.80** was selected as the optimal CV candidate on EVEN origins (since it minimized CV daytime MAE among all non-trivial thresholds), and frozen for test evaluation.

---

## 5. Final Official Test Set Evaluation

Applying the frozen strategy (**Stage 4 Physics @ Threshold 0.80**) to the 173 odd test origins:

### Official Test Benchmark Metrics:
* **Stage 4 Baseline Daytime MAE**: **43.4508 W/m²**
* **Stage 4 Baseline Daytime nMAE**: **33.70%**
* **Routed Forecast Daytime MAE**: **43.4583 W/m²**
* **Routed Forecast Daytime nMAE**: **33.71%**
* **$\Delta$ Daytime MAE**: **+0.0075 W/m²**
* **$\Delta$ Daytime nMAE**: **+0.01 percentage points**
* **95% Origin-Level Paired Bootstrap CI**: **[-0.7432, +0.7803] W/m²**
* **Nighttime MAE**: **0.3242 W/m²** (Exact 0.0 W/m² change)

### Test Set Routing Classification Metrics:
* **Total Daytime Hours Routed**: 340 / 2,883 (11.79%)
* **Actual Hard Hours (>150 W/m²)**: 210 (7.28%)
* **Captured Hard Hours (True Positives)**: 119
* **False Positive Routed Hours**: 221
* **Precision**: **35.00%**
* **Recall**: **56.67%**

---

## 6. Targeted NWP Cloud-Miss Diagnostic

Testing a deterministic rule for high-risk cloud misforecasts (`solar_elevation > 20°`, `clearsky_ghi > 300 W/m²`, `fc_cloud_cover > 70%`):
* **Matching Daytime Hours**: 524 hours (18.16% of daytime)
* **Hard Hours Captured**: 126 out of 210 hard hours (**60.00% of all hard cases**)
* **Sub-Regime Hard Rate**: 24.05%
* **Stage 4 MAE in Sub-Regime**: **94.43 W/m²**
* **Chronos MAE in Sub-Regime**: 121.10 W/m²
* **Physics MAE in Sub-Regime**: 120.93 W/m²

*Diagnostic Finding*: Even when isolating the exact regime where hard errors cluster (NWP predicting cloud cover under high sun potential), **Stage 4 Ensemble (94.43 W/m²) still outperforms both raw Chronos (121.10 W/m²) and raw Physics (120.93 W/m²)**. The ensemble blend is already superior to its individual constituent parts in this regime.

---

## 7. Answers to 9 Core Report Questions

1. **Which existing component is best on Stage-4 hard cases?**
   * *Answer*: Stage 3B Chronos achieves slightly lower MAE on hard hours on Train (199.50 W/m² vs 203.59 W/m²), but no single candidate consistently dominates Stage 4 across both splits.
2. **How much improvement is theoretically available from perfect hard-case routing?**
   * *Answer*: Oracle upper bound is only **~0.30 to 0.54 W/m²**.
3. **How much improvement is obtained by the frozen classifier?**
   * *Answer*: **+0.0075 W/m²** (a tiny shift on Test set).
4. **What specialist and threshold were selected using EVEN-origin CV?**
   * *Answer*: **Stage 4 Physics @ Threshold 0.80**.
5. **Does that frozen routing strategy improve the 173-origin held-out test?**
   * *Answer*: **No**. Daytime MAE changes by +0.0075 W/m² (+0.01pp nMAE).
6. **What is the exact Stage4 MAE $\rightarrow$ Routed MAE and nMAE $\rightarrow$ Routed nMAE?**
   * *Answer*: MAE **43.4508 W/m² $\rightarrow$ 43.4583 W/m²**; nMAE **33.70% $\rightarrow$ 33.71%**.
7. **What is the 95% paired bootstrap CI for $\Delta$ MAE?**
   * *Answer*: **[-0.7432, +0.7803] W/m²** (origin-level paired bootstrap).
8. **Did nighttime performance change?**
   * *Answer*: **No**. Night MAE remains exactly **0.3242 W/m²** (0.0 W/m² delta).
9. **Does the evidence justify proceeding to a genuinely new hard-weather specialist model?**
   * *Answer*: **NO**.

---

## 8. Decision Tree Outcome & Final Verdict

* **Case 2 & Case 5 Apply**:
  1. Oracle improvement potential is negligible (<0.54 W/m²).
  2. Classifier routing produces no meaningful improvement on the test set (+0.0075 W/m²), with 95% paired origin-level bootstrap CI [-0.7432, +0.7803] spanning zero.
  3. Classifier precision is ~35%, causing 221 false-positive hours to be routed to inferior component forecasts, cancelling any small benefit on hard hours.

> **FINAL VERDICT:**
> **"Does forecast-time hard-case routing beat Stage 4 on the locked odd-test benchmark? NO / INCONCLUSIVE"**
>
> **Stage 4 remains the official, undefeated champion baseline.**
