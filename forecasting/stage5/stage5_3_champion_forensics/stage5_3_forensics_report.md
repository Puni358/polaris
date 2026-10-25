# POLARIS Stage 5.3 — Champion Forensics Research Findings

> **Executive Summary:** Stage 5.3 executed a quantitative forensic decomposition of the frozen Stage 5.2 champion (Architecture A: GBDT Non-Linear Residual Corrector). The analysis reveals that the **-4.37 W/m² MAE reduction** (33.70% -> 30.32% Daytime nMAE) is associated with three primary feature mechanisms: (1) pre-forecast ground volatility (`ctx_std_6h`), (2) clear-sky solar potential (`clearsky_ghi`), and (3) Stage-4 base forecast state (`pred_stage4_fold`).

---

## 1. Top 3 Feature Mechanisms Associated with Architecture A's Gain

1. **Clear-Sky Solar Potential Scaling (`clearsky_ghi`):**  
   Gains scale directly with solar potential. In high clear-sky regimes (>500 W/m²), Architecture A achieves a **-10.09 W/m² MAE reduction** (vs -2.22 W/m² in low-solar regimes). `clearsky_ghi` provides a physically interpretable measure of available solar potential and constrains the scale of physically plausible irradiance errors.
2. **Pre-Forecast Ground Volatility (`ctx_std_6h`):**  
   `ctx_std_6h` provides an observational indicator of recent irradiance variability and is strongly associated with regimes where Architecture A applies larger corrections (average MAE reduction of **-31.17 W/m²** in extreme volatility regimes `ctx_std_6h > 50` vs -3.75 W/m² in low volatility conditions). This pattern is compatible with, but does not directly measure, rapidly varying cloud conditions.
3. **Stage-3B / Physics Model Disagreement (`disagreement_fold`):**  
   `disagreement_fold` provides a model-state disagreement signal that is associated with regimes where Architecture A applies different residual corrections (-6.42 W/m² MAE drop in extreme disagreement regimes >100 W/m² vs -2.03 W/m² in low disagreement regimes <20 W/m²).

---

## 2. Quantitative Gain Contribution

* **Total Daytime MAE Reduction:** -4.3660 W/m² (-3.96 W/m² on ODD daytime test split).
* **Median Paired Gain:** 0.00 W/m²
* **Fraction of Daytime Hours Improved:** **45.33%** (1,307 / 2,883 daytime test hours)
* **Fraction Worsened:** **31.53%** (909 / 2,883 daytime test hours)
* **Fraction Unchanged:** **23.14%** (667 / 2,883 daytime test hours, night/zero solar)
* **Gain Concentration:**  
  * Top 1% of improved hours account for **23.81%** of total net MAE reduction.
  * Top 5% of improved hours account for **73.04%** of total net MAE reduction.
  * Top 10% of improved hours account for **112.14%** of total net MAE reduction (exceeding 100% because 31.53% of hours experience minor worsening that must be offset).

---

## 3. Subgroup Interaction Analysis

The systematic interaction audit evaluated candidate feature pairs and identified the largest observed subgroup gain spreads:
1. `ctx_std_6h` x `clearsky_ghi` (Cell Gain Spread = **32.62 W/m²**)
2. `ctx_std_6h` x `cloud_frac` (Cell Gain Spread = **28.45 W/m²**)
3. `pred_stage4_fold` x `clearsky_ghi` (Cell Gain Spread = **24.10 W/m²**)
4. `horizon_hour` x `ctx_std_6h` (Cell Gain Spread = **19.80 W/m²**)

*Sample Size Caveat:* The extreme cell (`ctx_std_6h > 50` and `clearsky_ghi > 500`) contains only **24 daytime test hours** (0.83% of daytime test hours). Therefore, this result represents evidence of a regime association rather than proof of a universal non-linear interaction.

---

## 4. Where Architecture A Improves Most vs Remaining Error Regimes

* **Largest Improvement Regimes:** High-irradiance, high-volatility midday horizons ($H8 ... H13$, clear-sky GHI >500 W/m², `ctx_std_6h > 30`), yielding MAE drops up to **-31.17 to -32.62 W/m²**.
* **Remaining Error Regimes:** 158 of Stage 4's 210 hard error hours (>150 W/m²) remained above 150 W/m² error after Architecture A correction, and Architecture A has **180 total daytime test hours** with absolute error >150 W/m² (averaging 210.52 W/m² MAE).

---

## 5. Residual Analysis & Actionability

* **Residual Autocorrelation:** Residual autocorrelation remains detectable after Architecture A ($r_A = y - \hat{y}_A$ exhibits positive lag-1 autocorrelation $r = +0.284 / +0.622$).
* **Actionability Audit:** Residual autocorrelation indicates temporal structure in the residual series; however, prior causal out-of-sample evaluations did not establish that this residual structure is operationally exploitable at forecast issuance time $t_0$.

---

## 6. Decision Gate & Scientific Recommendation

* **Selected Gate:** **DECISION C** — *Structure remains statistically detectable in specific high-flux regimes, but does NOT appear operationally exploitable using available surface and 1D NWP inputs without new physical observation sources.*
* **Stage 5.4 Recommendation:** Another GBDT stacker using the same 28-feature information set is not justified by the current evidence and would carry substantial risk of redundant modeling and overfitting. Future upstream forecasting research should prioritize genuinely new information sources, such as higher-resolution cloud observations, satellite-derived cloud motion, cloud optical depth, or higher-frequency radiometric observations, before attempting additional model stacking on the same information set.
