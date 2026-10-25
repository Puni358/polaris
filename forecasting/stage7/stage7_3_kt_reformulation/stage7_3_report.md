# POLARIS Stage 7.3 Experiment Report: Clear-Sky Index ($k_t$) Target Reformulation

## 1. Executive Summary & Objective
Stage 7.3 tested a pure target reformulation hypothesis for shortwave solar irradiance forecasting at the POLARIS Nuolja site ($68.36^\circ	ext{N}$). The experiment evaluated whether changing the prediction target from raw surface shortwave irradiance ($	ext{SW\_IN}$) to the clear-sky-normalized ratio ($k_t = 	ext{SW\_IN} / 	ext{clearsky\_ghi}$) improves out-of-sample performance when using the frozen 31-feature Stage 6.6 LWP/IWP champion representation.

* **Result**: **NO IMPROVEMENT / REJECTED**
* **Official Champion**: Stage 6.6 LWP/IWP Model remains frozen and active.
* **ODD Status**: 100% UNTOUCHED & LOCKED.

---

## 2. Background & Target Reformulation Mechanics

In standard irradiance forecasting, predicting absolute irradiance ($	ext{W/m}^2$) requires the model to simultaneously learn the diurnal/seasonal solar geometry cycle and atmospheric cloud attenuation. Normalizing by clear-sky GHI ($k_t$) converts the target into a dimensionless clearness index bounded in theory between $0$ (overcast) and $pprox 1$ (clear sky).

For daytime target hours ($	ext{SW\_IN} > 0$):
$$k_t = rac{	ext{SW\_IN\_actual}}{	ext{clearsky\_ghi}}$$

At inference time, the model predicts $\hat{k}_t$, and physical irradiance is reconstructed via:
$$\widehat{	ext{SW\_IN}} = \hat{k}_t 	imes 	ext{clearsky\_ghi}$$

For causal night hours ($	ext{solar\_elevation} \le 0$ or $	ext{clearsky\_ghi} == 0$), predictions are forced to $0.0	ext{ W/m}^2$ following POLARIS causal night-masking rules.

---

## 3. Data & $k_t$ Distribution Analysis

Per experiment design, $k_t$ was evaluated without arbitrary clipping or Winsorizing. Distribution inspection across the 2,218 causal daytime EVEN training rows revealed:

* **Mean**: $1.267390$
* **Median**: $0.609977$
* **Std**: $3.479202$
* **P1 / P5 / P25 / P50 / P75 / P95 / P99**: $0.0858$ / $0.1546$ / $0.3767$ / $0.6100$ / $0.9944$ / $3.9957$ / $14.2874$
* **Maximum $k_t$**: $63.450884$

### Physical Diagnostic of High $k_t$ Values
At high latitude ($68.36^\circ	ext{N}$), near sunrise/sunset transitions (solar elevation $< 2^\circ$), actual surface shortwave sensors detect diffuse and terrain-reflected radiation ($2 \dots 30	ext{ W/m}^2$) while the direct clear-sky model approaches small values ($0.1 \dots 1.0	ext{ W/m}^2$). This small-denominator effect produces high $k_t$ ratios up to $>60$.

---

## 4. Experimental Results (5-Fold EVEN CV)

### Control E0 Reproduction
The Stage 6.6 EVEN CV control baseline was reproduced to 100.000% exact numerical precision:
* **MAE**: $38.2806	ext{ W/m}^2$
* **nMAE**: $40.39\%$
* **RMSE**: $60.7509	ext{ W/m}^2$

### Candidate E1 Performance
* **Aggregate MAE**: $36.3828	ext{ W/m}^2$ ($\Delta	ext{MAE} = -1.8978	ext{ W/m}^2$)
* **Aggregate nMAE**: $40.46\%$ ($\Delta	ext{nMAE} = +0.07	ext{ pp}$)
* **Aggregate RMSE**: $58.8212	ext{ W/m}^2$ ($\Delta	ext{RMSE} = -1.9297	ext{ W/m}^2$)
* **Aggregate Bias**: $+4.7858	ext{ W/m}^2$ (vs Control $+2.4191	ext{ W/m}^2$)

### Per-Fold Breakdown

| Fold | Control MAE ($	ext{W/m}^2$) | E1 Candidate MAE ($	ext{W/m}^2$) | Delta MAE ($	ext{W/m}^2$) | Fold Pass? | Degradation Pass? |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | $49.8174$ | $44.5888$ | $-5.2286$ | PASS | PASS |
| 2 | $71.0775$ | $66.8321$ | $-4.2454$ | PASS | PASS |
| 3 | $41.2620$ | $42.9639$ | $+1.7020$ | FAIL | FAIL (+1.7020) |
| 4 | $26.8042$ | $24.8237$ | $-1.9805$ | PASS | PASS |
| 5 | $2.4420$ | $2.7053$ | $+0.2633$ | FAIL | FAIL (+0.2633) |

---

## 5. Acceptance Gate Evaluation & Failure Forensic Analysis

### Gate Audit Summary
1. **Gate 1 (MAE $\le 38.0806	ext{ W/m}^2$)**: **PASS** ($36.3828	ext{ W/m}^2$)
2. **Gate 2 ($\ge 4/5$ folds improve)**: **FAIL** ($3/5$ folds improved)
3. **Gate 3 (Max single-fold degradation $\le +0.15	ext{ W/m}^2$)**: **FAIL** (Fold 3 degraded by $+1.7020	ext{ W/m}^2$)
4. **Gate 4 (nMAE $\le 40.39\%$)**: **FAIL** ($40.46\%$)
5. **Gate 5 (RMSE $\le 60.7509	ext{ W/m}^2$)**: **PASS** ($58.8212	ext{ W/m}^2$)

### Failure Diagnostics & Scientific Interpretation
Why did $k_t$ target reformulation fail acceptance gates despite lowering aggregate MAE?
1. **Target Instability near Sunrise/Sunset**: Small clear-sky GHI values near sunrise/sunset make the $k_t$ target numerically unstable because $k_t = \text{SW\_IN} / \text{GHI\_clear}$ divides the observed irradiance by a very small denominator. This produces a highly skewed and heavy-tailed target distribution, with extreme $k_t$ values even when absolute $\text{SW\_IN}$ is modest. The resulting target instability is a plausible contributor to the fold-specific degradation observed in Fold 3 and should be treated as a diagnostic interpretation rather than a proven causal mechanism.
2. **Elevated Prediction Bias**: $k_t$ targeting increased overall prediction bias from $+2.42\text{ W/m}^2$ to $+4.79\text{ W/m}^2$, consistent with skewed target distribution tails during low-sun transitions.
3. **Redundancy with Direct GBDT Representation**: The GBDT model with 31 features (including `clearsky_ghi`, `cloud_frac`, `lwp_latest`, `iwp_latest`, `solar_elevation`) already models non-linear clear-sky attenuation directly and with greater temporal stability than ratio-based target normalization.

## 6. Official Decision & Next Steps
Per POLARIS experiment protocol, because candidate E1 failed Gates 2, 3, and 4:

* **FINAL DECISION**: **STAGE 7.3 = NO IMPROVEMENT**
* **Active Operational Champion**: **Stage 6.6 LWP/IWP Model (FROZEN)**
* **ODD Test Set**: **100% UNTOUCHED & LOCKED**
