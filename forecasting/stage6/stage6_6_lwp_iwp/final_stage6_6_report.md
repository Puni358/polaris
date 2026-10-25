# STAGE 6.6 LWP/IWP CLOUD MICROPHYSICS EXPERIMENT REPORT

**Status:** OFFICIAL ODD EVALUATION COMPLETE — **NEW CHAMPION CROWNED & FROZEN**  
**Date:** September 12, 2026  
**Target Station:** Nuolja ($68.355701^\circ\text{N}, 18.763666^\circ\text{E}$, Elev: $702\text{ m a.s.l.}$)  
**New Operational Champion:** Stage 6.6 LWP/IWP Model  

---

## EXECUTIVE SUMMARY & OFFICIAL DECISION

> [!IMPORTANT]
> **OFFICIAL ODD RESULT: NEW OPERATIONAL CHAMPION CROWNED**
> 
> Surface-aware Liquid Water Path (`lwp_latest`), Ice Water Path (`iwp_latest`), and cloud-liquid interaction (`lwp_x_cloud`) successfully outperformed the Stage 5.2 champion on the held-out 173 ODD test origins under the true frozen Stage 5.2 pipeline (`pred_stage4_full`).
> 
> * **Stage 5.2 ODD Control MAE:** $39.084821\text{ W/m}^2$ (nMAE: $30.3151\%$, RMSE: $68.993487\text{ W/m}^2$)
> * **Stage 6.6 Candidate ODD MAE:** **$37.005888\text{ W/m}^2$** (nMAE: **$28.7026\%$**, RMSE: **$65.671702\text{ W/m}^2$**)
> * **Absolute $\Delta\text{MAE}$:** **$-2.078933\text{ W/m}^2$** ($-1.6125\text{ pp}$ nMAE reduction)
> * **Absolute $\Delta\text{RMSE}$:** **$-3.321785\text{ W/m}^2$**
> * **Daytime Bias Improvement $(\text{pred}-\text{actual})$:** From $+1.934725\text{ W/m}^2$ to **$+1.144965\text{ W/m}^2$** ($-40.82\%$)
> * **10,000 Origin Bootstrap 95% CI:** $[-2.809838, -1.344760]\text{ W/m}^2$ (Statistically significant improvement, $100\%$ negative)
> 
> **FINAL DECISION:** **STAGE 6.6 FROZEN AS OFFICIAL OPERATIONAL CHAMPION**

---

## 1. OFFICIAL ODD TEST PERFORMANCE SUMMARY

Evaluated on all 173 ODD test origins ($4,152$ total hours, $2,883$ daytime validation hours):

| Metric | Stage 5.2 Control | Stage 6.6 Candidate | Absolute Delta ($\Delta$) | Relative Change |
| :--- | :---: | :---: | :---: | :---: |
| **Daytime MAE** | $39.084821\text{ W/m}^2$ | **$37.005888\text{ W/m}^2$** | **$-2.078933\text{ W/m}^2$** | **$-5.32\%$** |
| **Daytime nMAE** | $30.3151\%$ | **$28.7026\%$** | **$-1.6125\text{ pp}$** | **$-5.32\%$** |
| **Daytime RMSE** | $68.993487\text{ W/m}^2$ | **$65.671702\text{ W/m}^2$** | **$-3.321785\text{ W/m}^2$** | **$-4.81\%$** |
| **Daytime Bias $(\text{pred}-\text{actual})$** | $+1.934725\text{ W/m}^2$ | **$+1.144965\text{ W/m}^2$** | **$-0.789760\text{ W/m}^2$** | **$-40.82\%$** |
| **Night MAE** | $0.000000\text{ W/m}^2$ | $0.000000\text{ W/m}^2$ | $0.000000\text{ W/m}^2$ | $0.00\%$ |

---

## 2. BOOTSTRAP SIGNIFICANCE TEST

* **Method:** $10,000$ origin-level paired bootstrap resamples ($N=173$ origins, seed 42).
* **Mean Resampled $\Delta\text{MAE}$:** $-2.078277\text{ W/m}^2$
* **95% Confidence Interval:** $[-2.809838, -1.344760]\text{ W/m}^2$
* **Conclusion:** The 95% bootstrap confidence interval lies entirely below zero, providing strong evidence that the improvement is statistically significant under the specified resampling procedure.

---

## 3. ARTIFACT LOCATIONS

* `POLARIS_STAGE6_6_CHAMPION_MANIFEST.json` — Machine-readable manifest
* `POLARIS_STAGE6_6_CHAMPION_MANIFEST.md` — Detailed champion manifest
* `control_discrepancy_forensic_audit.json` — Forensic control reconstruction audit
* `odd_evaluation_results.json` — Authoritative numeric metrics and bootstrap stats
* `odd_predictions_comparison.csv` — Row-level predictions for control vs candidate on ODD set
* `gate_decision.json` — Complete audit and gate evaluation summary
