# POLARIS STAGE 8.1 CHAMPION MANIFEST

**Status:** OFFICIAL FROZEN OPERATIONAL CHAMPION  
**Date:** September 12, 2026  
**Target Station:** Nuolja ($68.355701^\circ\text{N}, 18.763666^\circ\text{E}$, Elev: $702\text{ m a.s.l.}$)  
**Champion ID:** `STAGE_8_1_U700_V700`  
**Audit Status:** `FINAL_CHAMPION_FREEZE_PASSED`  

---

## 1. AUTHORITATIVE ODD TEST METRICS

Evaluated under the **True Frozen Stage 4 / Stage 7.5 Pipeline** (`pred_ensemble` from `ensemble_predictions.csv`) on all 173 held-out ODD test origins ($4,152$ total hours, $2,883$ daytime validation hours):

| Metric | Stage 7.5 Champion | Stage 8.1 Champion | Absolute Delta ($\Delta$) | Relative Change |
| :--- | :---: | :---: | :---: | :---: |
| **Daytime MAE** | $36.613571\text{ W/m}^2$ | **$36.188657\text{ W/m}^2$** | **$-0.424913\text{ W/m}^2$** | **$-1.16\%$** |
| **Daytime nMAE** | $28.3983\%$ | **$28.0688\%$** | **$-0.3296\text{ pp}$** | **$-1.16\%$** |
| **Daytime RMSE** | $65.347064\text{ W/m}^2$ | **$64.219495\text{ W/m}^2$** | **$-1.127569\text{ W/m}^2$** | **$-1.73\%$** |
| **Daytime Bias $(\text{pred}-\text{actual})$** | $+1.307778\text{ W/m}^2$ | **$+1.439399\text{ W/m}^2$** | **$+0.131622\text{ W/m}^2$** | $+10.06\%$ |
| **Night MAE** | $0.000000\text{ W/m}^2$ | $0.000000\text{ W/m}^2$ | $0.000000\text{ W/m}^2$ | $0.00\%$ |

---

## 2. STATISTICAL BOOTSTRAP (10,000 RESAMPLES)

* **Resampling Protocol:** $10,000$ paired origin-level bootstrap resamples ($N=173$ origins).
* **Random Seed:** 42
* **Mean Bootstrapped $\Delta\text{MAE}$:** **$-0.424222\text{ W/m}^2$**
* **95% Confidence Interval:** **$[-0.887999, +0.026372]\text{ W/m}^2$**
* **Fraction of Resamples $< 0$:** **$0.9665$** ($96.65\%$ of resamples show candidate improvement).
* **Statistical Wording Standard**: Stage 8.1 achieved an observed held-out improvement over Stage 7.5, reducing ODD nMAE from 28.3983% to 28.0688%. The paired bootstrap distribution was strongly shifted toward improvement, with 96.65% of resamples showing lower MAE, but the 95% confidence interval [-0.887999, +0.026372] narrowly includes zero. Therefore the gain should be described as an observed held-out improvement rather than a statistically significant improvement under the specified bootstrap procedure.

---

## 3. FEATURE SPECIFICATION & MODEL CONFIGURATION

* **Feature Set Count:** 37 features (35 frozen Stage 7.5 features + $U_{700} + V_{700}$).
* **New Features:**
  1. `u700`: Zonal wind component ($U$) at 700 hPa from MEPS pressure-level forecast (`meps_det_pl`).
  2. `v700`: Meridional wind component ($V$) at 700 hPa from MEPS pressure-level forecast (`meps_det_pl`).
* **Model:** `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`
* **Stage 4 Refit Executed:** NO
