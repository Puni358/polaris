# POLARIS Stage 5.3 — Forensics Evidence Validation & Scientific Audit Report

> **Document Type:** Scientific Audit & Evidence Validation  
> **System:** POLARIS Upstream Solar Irradiance Forecasting Module (SIH 2026)  
> **Subject:** Stage 5.3 Champion Forensics & Error Mechanism Analysis Audit  
> **Audited Baseline:** Stage 5.2 Architecture A Frozen Champion (**39.0848 W/m²** Daytime MAE, **30.32%** Daytime nMAE)  
> **Audit Date:** 2026-09-10  

---

## 1. Executive Summary

This report performs a rigorous scientific audit of the Stage 5.3 forensic findings. Every numerical metric, mechanism claim, interaction spread, and hard-error count reported in Stage 5.3 was cross-checked against the underlying CSV artifacts (`01_correction_distribution.csv` through `12_information_ceiling_summary.csv`), `POLARIS_MASTER_HANDOFF.md`, Stage 5.2 audit files, and previous negative controls (Stage 4.5 residual predictability and Stage 4.6 causal persistence).

### Key Audit Verdicts:
1. **Numerical Reconciliation:** All core metrics are reconciled with exact definitions. The apparent hard-error count discrepancy (124 vs 210 vs 180 hours) is fully resolved: 210 is the Stage 4 hard error count ($|e_4| > 150\text{ W/m}^2$), 158 is the number of those 210 hours remaining $>150\text{ W/m}^2$ under Arch A, 55 are converted below $150\text{ W/m}^2$, and 180 is the total Arch A hard error count ($|e_A| > 150\text{ W/m}^2$).
2. **Autocorrelation & Actionability Audit:** The interim claim that *"positive lag-1 residual ACF (+0.284) proves actionable structure remains"* is **REJECTED AS SCIENTIFICALLY OVERSTATED**. Following Stage 4.5/4.6 findings, residual autocorrelation indicates temporal persistence but does **not** prove operational exploitability at forecast origin $t_0$.
3. **Decision Gate Re-Evaluation:** The interim recommendation of **DECISION B** and proposal of a Stage 5.4 GBDT stacker is **REJECTED**. The correct, scientifically defensible gate is **DECISION C** (*Structure remains statistically detectable in specific high-flux regimes, but does NOT appear operationally exploitable using available 1D NWP and surface inputs without new physical observation sources*).
4. **Stage 5.4 Status:** Building another ML/GBDT model on existing features is **UNJUSTIFIED**. POLARIS upstream irradiance forecasting is frozen at Stage 5.2 Champion (39.0848 W/m² / 30.32% nMAE), and the project cleanly transitions to downstream **Stage 5 PV Digital Twin** development.

---

## 2. Numerical Reconciliation Matrix

| Metric / Quantity | Interim Stage 5.3 Summary Text | Exact Audited CSV Value | Status & Reconciliation Notes |
| :--- | :---: | :---: | :--- |
| **Stage 4 ODD Test Daytime MAE** | 43.45 W/m² | **43.4508 W/m²** | PASS (Exact match to frozen benchmark). |
| **Arch A ODD Test Daytime MAE** | 39.08 W/m² | **39.0848 W/m²** | PASS (Exact match to frozen champion). |
| **Absolute Daytime $\Delta\text{MAE}$** | -4.37 W/m² | **-4.3660 W/m²** | PASS (Exact match). |
| **Daytime nMAE Improvement** | -3.38 pp | **-3.38 pp** (33.70% $\to$ 30.32%) | PASS (Exact match). |
| **Arch A Daytime RMSE** | 68.99 W/m² | **68.9935 W/m²** | PASS (Exact match). |
| **Arch A Night MAE** | 0.32 W/m² | **0.3242 W/m²** | PASS (Exact match). |
| **Stage 4 Hard Errors ($>150\text{ W/m}^2$)** | 210 / 124 (ambiguous) | **210 hours** (Stage 4) | **RECONCILED**: Stage 4 had 210 daytime test hours with $|e_4| > 150\text{ W/m}^2$ (MAE = 213.87 W/m²). |
| **Arch A Remaining Hard Errors** | 124 (interim typo) | **180 hours** (Arch A) | **RECONCILED**: Arch A has 180 total daytime test hours with $|e_A| > 150\text{ W/m}^2$ (MAE = 210.52 W/m²). |
| **Stage 4 Hard Errors Converted** | Not explicitly reported | **55 hours** (26.2%) | **RECONCILED**: 55 of Stage 4's 210 hard error hours were reduced below $150\text{ W/m}^2$ by Arch A. |
| **Stage 4 Hard Errors Remaining** | Not explicitly reported | **158 hours** (75.2%) | **RECONCILED**: 158 of Stage 4's 210 hard error hours remained $>150\text{ W/m}^2$ after Arch A correction. |
| **New Hard Errors Created** | Not reported | **22 hours** | **RECONCILED**: 22 hours where $|e_4| \le 150\text{ W/m}^2$ were pushed to $|e_A| > 150\text{ W/m}^2$ by Arch A. |
| **Pct Daytime Rows Improved** | 64.2% (interim text) | **45.33%** (1,307 / 2,883) | **RECONCILED**: 45.33% improved ($g_i > 0$), 31.53% worsened ($g_i < 0$), 23.14% unchanged ($g_i = 0$). |
| **Top 5% Gain Contribution** | 44.2% / 73.0% | **73.04%** | **RECONCILED**: Top 5% of hours (144 hrs) account for 73.04% of total net MAE reduction ($\sum g_i$). |
| **Top 10% Gain Contribution** | 63.8% / 112.1% | **112.14%** | **RECONCILED**: Exceeds 100% of net gain because 31.5% of rows experience worsening that must be offset. |

---

## 3. Scientific Audit of Mechanism Claims

### A. Ground Volatility Mechanism (`ctx_std_6h`)
* **Claim:** *"Pre-forecast ground volatility (`ctx_std_6h`) is a primary mechanism driving rapid cloud transmission corrections."*
* **Audit Finding:** **ASSOCIATIVE ONLY (INTERPRETATION CAVEAT)**. `ctx_std_6h` correlates with solar elevation ($r \approx 0.52$) and clear-sky GHI ($r \approx 0.58$) because absolute irradiance fluctuations naturally scale with total available irradiance. Labeling high volatility as "rapid cloud movement" is an unmeasured physical inference. `ctx_std_6h` is an **observational indicator of high flux variance**, not direct proof of cloud dynamics.

### B. Clear-Sky Solar Potential Scaling (`clearsky_ghi`)
* **Claim:** *"Clear-sky solar potential scales MAE reductions directly."*
* **Audit Finding:** **SUPPORTED (AMPLITUDE SCALER)**. `clearsky_ghi` provides a physically interpretable measure of available solar potential and constrains the scale of physically plausible irradiance errors. In high clear-sky conditions ($>500\text{ W/m}^2$), absolute errors are naturally larger, providing greater absolute room for GBDT correction ($\Delta\text{MAE} = -10.09\text{ W/m}^2$).

### C. Stage 3B vs Physics Disagreement (`disagreement_fold`)
* **Claim:** *"Architecture A acts as a non-linear state-dependent arbiter when neural and physics models diverge."*
* **Audit Finding:** **ASSOCIATIVE**. Disagreement between Stage 3B (neural) and PVLIB clear-sky physics correlates strongly with broken cloud fraction ($0.5\text{--}0.8$) and high clear-sky potential. It serves as a proxy for atmospheric state uncertainty rather than a unique causal arbiter.

---

## 4. Interaction Claims & Cell Gain Spread Audit

In `08_interaction_analysis.csv`, 10 candidate pairwise interactions were evaluated. The top interaction (`ctx_std_6h` $\times$ `clearsky_ghi`) showed a cell gain spread of **32.62 W/m²**.

* **Audit Finding:** **CELL-SIZE SENSITIVE**. The extreme interaction cell (`ctx_std_6h > 50` and `clearsky_ghi > 500`) contains only **24 daytime test hours** (0.83% of daytime hours). 
* **Scientific Caution:** Large cell gain spreads in sparse subgroup cells do **not** constitute proof of a multi-variable physical interaction. The effect is heavily dominated by a small cluster of high-flux summer days.

---

## 5. Residual Autocorrelation & Actionability Audit (Stage 4.5/4.6 Cross-Check)

The interim Stage 5.3 report asserted: *"positive lag-1 residual ACF of +0.284 demonstrates actionable structure remains."*

* **Audit Finding:** **REJECTED AS SCIENTIFICALLY OVERSTATED**.
* **Cross-Check with Stage 4.5 & Stage 4.6:**
  - Stage 4.5 (Residual Predictability) and Stage 4.6 (Causal Residual Persistence) explicitly established that **statistically detectable residual autocorrelation DOES NOT imply operational exploitability at forecast issuance time $t_0$**.
  - In Stage 4.6, autoregressive residual feedback models ($r_{t+h} = \alpha_h r_t$) failed on held-out test data because historical residual persistence observed over $[t_0-24\text{h}, t_0)$ decays rapidly and un-predictably across forecast horizons $H1\dots H24$ during polar cloud transitions.
  - Therefore, residual autocorrelation ($r = +0.284$ or $+0.622$) indicates temporal structure in the residual series; however, prior causal out-of-sample evaluations did not establish that this residual structure is operationally exploitable at forecast issuance time $t_0$.

---

## 6. Re-Evaluation of Decision Gate & Stage 5.4 Status

### Rejection of Interim DECISION B:
The interim report selected **DECISION B** ("Meaningful actionable nonlinear structure remains; targeted architecture justified") and proposed building a "Volatility-Conditioned Spatiotemporal GBDT Stacker" (Stage 5.4).

* **Why DECISION B is Unjustified:**
  1. Architecture A (Stage 5.2) already incorporated `ctx_std_6h`, `clearsky_ghi`, `cloud_frac`, `solar_elevation`, and Stage 4 predictions into a non-linear GBDT.
  2. Building another GBDT stacker on the exact same 28 surface and 1D NWP features is not justified by the current evidence and would carry substantial risk of redundant modeling and overfitting, repeating the failed patterns of Stages 4.1, 4.2, 4.3, 4.4, 4.4B, 4.5, 4.6, and 5.1.
  3. The remaining daytime MAE (**39.0848 W/m²**, 30.32% nMAE) is consistent with representation limits associated with the spatial-temporal resolution of the available 1D NWP cloud forecasts.

### Formal Selection of DECISION C:

```
================================================================================
FINAL SCIENTIFIC DECISION GATE: DECISION C
================================================================================
Label: "Structure remains statistically detectable in specific high-flux regimes, 
       but does NOT appear operationally exploitable using available surface 
       and 1D NWP inputs without new physical observation sources."

Justification:
1. Representation Limits: Stage 5.2 Architecture A successfully extracted the 
   predictive signal available in 24h ground context, PVLIB solar geometry, and 
   1D MET Nordic NWP cloud fraction.
2. Diminishing Returns: Further post-hoc ML stackers on the same feature set 
   cannot resolve the spatial-temporal mismatch of 1D NWP cloud forecasts.
3. Clean Hand-off: Upstream irradiance forecasting is officially LOCKED at Stage 5.2 
   Champion (39.0848 W/m² Daytime MAE / 30.32% Daytime nMAE).
================================================================================
```

---

## 7. Guidelines for Future Upstream Research

Future upstream forecasting research should prioritize genuinely new information sources, such as higher-resolution cloud observations, satellite-derived cloud motion, cloud optical depth, or higher-frequency radiometric observations, before attempting additional model stacking on the same information set. Any future attempt must adhere to:
1. **EVEN CV Validation First:** Any new model idea must be proven strictly on 5-fold EVEN forward-chaining CV before touching ODD held-out data.
2. **Out-of-Sample Holdout Preservation:** The ODD held-out test result (**39.0848 W/m²**) must remain completely un-contaminated by hyperparameter tuning or feature selection.

---

## 8. Immediate Downstream Action: Stage 5 PV Digital Twin Handoff

With Stage 5.3 forensics validated and frozen:
* **Upstream Irradiance Forecast Champion:** Stage 5.2 Architecture A predictions (`stage5_2_test_results.csv`) are locked as the primary irradiance driver.
* **Next Action:** POLARIS cleanly transitions to downstream **Stage 5 PV Digital Twin & Power Forecast Modeling**, converting forecasted `SW_IN` ($\text{W/m}^2$) into AC/DC photovoltaic electrical power output ($\text{kW}$) for Maitri/Bharati microgrid simulation.

---
*End of Stage 5.3 Forensics Evidence Validation Report.*
