# POLARIS Stage 7.3 — Clear-Sky Index ($k_t$) Target Reformulation Experiment

## Executive Summary
* **Status**: **CLOSED — REJECTED**
* **Decision**: **STAGE 7.3 = NO IMPROVEMENT**
* **Official Operational Champion**: **Stage 6.6 LWP/IWP Model (FROZEN & UNTOUCHED)**
* **ODD Test Set**: **100% UNTOUCHED & LOCKED** (0 ODD predictions or evaluations generated)

Stage 7.3 evaluated a target reformulation hypothesis: whether reformulating the prediction target from surface shortwave irradiance ($	ext{SW\_IN}$) to the clear-sky index ($k_t = 	ext{SW\_IN\_actual} / 	ext{clearsky\_ghi}$) improves out-of-sample forecasting performance using the exact frozen 31-feature representation and hyperparameter setup of the Stage 6.6 LWP/IWP champion.

While $k_t$ target reformulation reduced overall daytime MAE to $36.3828	ext{ W/m}^2$ (passing Gate 1), it failed three out of five predeclared EVEN cross-validation acceptance gates due to severe fold instability (Fold 3 degraded by $+1.7020	ext{ W/m}^2$), failing fold count (only $3/5$ folds improved), and higher overall nMAE ($40.46\%$ vs $40.39\%$). Consequently, Stage 7.3 was rejected, and Stage 6.6 LWP/IWP remains the unbeaten operational champion.

---

## Experimental Setup & Methodology

### Locked Baseline & Champion (Stage 6.6 LWP/IWP)
* **Features (31 Total)**: 28 Stage 5.2 base features + `lwp_latest` + `iwp_latest` + `lwp_x_cloud`.
* **Model**: `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`
* **EVEN CV Baseline (Control E0)**: MAE = $38.2806	ext{ W/m}^2$, nMAE = $40.39\%$, RMSE = $60.7509	ext{ W/m}^2$ (100.000% exact reproduction verified).
* **Held-out ODD Baseline (Champion)**: MAE = $37.005888	ext{ W/m}^2$, nMAE = $28.7026\%$, RMSE = $65.671702	ext{ W/m}^2$.

### Target Reformulation Definition
For all daytime training hours ($	ext{SW\_IN\_actual} > 0$), $k_t$ is defined as:
$$k_t = rac{	ext{SW\_IN\_actual}}{	ext{clearsky\_ghi}}$$
At validation/prediction time:
$$\widehat{	ext{SW\_IN}} = \hat{k}_t 	imes 	ext{clearsky\_ghi}$$
Night hours ($	ext{solar\_elevation} \le 0$ or $	ext{clearsky\_ghi} == 0$) are causally forced to $0.0	ext{ W/m}^2$. Evaluation is strictly performed in original $	ext{SW\_IN}$ units ($	ext{W/m}^2$).

---

## $k_t$ Distribution Inspection (No Arbitrary Clipping Rule)
Inspecting the unclipped EVEN training distribution of $k_t$ for causal daytime hours ($	ext{clearsky\_ghi} > 0$):
* **Min**: $0.031366$
* **Max**: $63.450884$
* **Mean**: $1.267390$
* **Median**: $0.609977$
* **Std**: $3.479202$
* **Percentiles**: P1 = $0.0858$, P5 = $0.1546$, P25 = $0.3767$, P50 = $0.6100$, P75 = $0.9944$, P95 = $3.9957$, P99 = $14.2874$

*Physical Regime Findings*: $k_t > 1.0$ occurs in $42.22\%$ of daytime target rows ($1,218$ rows), concentrated around low solar elevation ($< 2.0^\circ$) near sunrise/sunset and in transitional cloud regimes where diffuse/scattered solar radiation produces non-zero surface measurements while direct clear-sky GHI is small.

---

## 5-Fold EVEN CV & Acceptance Gate Audit

| Fold | E0 Control MAE ($	ext{W/m}^2$) | E1 $k_t$ MAE ($	ext{W/m}^2$) | $\Delta	ext{MAE}$ ($	ext{W/m}^2$) | Fold Improved? | Max Degradation Pass? |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | $49.8174$ | $44.5888$ | $-5.2286$ | **YES** | **PASS** |
| **Fold 2** | $71.0775$ | $66.8321$ | $-4.2454$ | **YES** | **PASS** |
| **Fold 3** | $41.2620$ | $42.9639$ | $+1.7020$ | **NO** | **FAIL (+1.7020)** |
| **Fold 4** | $26.8042$ | $24.8237$ | $-1.9805$ | **YES** | **PASS** |
| **Fold 5** | $2.4420$ | $2.7053$ | $+0.2633$ | **NO** | **FAIL (+0.2633)** |
| **Aggregate Mean** | **$38.2806$** | **$36.3828$** | **$-1.8978$** | **3 / 5 Folds** | **FAILED GATE 3** |

### Predeclared Acceptance Gates Evaluation
1. **Gate 1 (Aggregate MAE $\le 38.0806	ext{ W/m}^2$)**: **PASS** ($36.3828	ext{ W/m}^2$)
2. **Gate 2 (Improve in $\ge 4/5$ folds)**: **FAIL** ($3/5$ folds improved)
3. **Gate 3 (Max single-fold degradation $\le +0.15	ext{ W/m}^2$)**: **FAIL** (Fold 3 degraded by $+1.7020	ext{ W/m}^2$)
4. **Gate 4 (Aggregate nMAE $\le 40.39\%$)**: **FAIL** ($40.46\%$)
5. **Gate 5 (Aggregate RMSE $\le 60.7509	ext{ W/m}^2$)**: **PASS** ($58.8212	ext{ W/m}^2$)

**Final Stage 7.3 Decision**: **REJECTED (NO IMPROVEMENT)**

---

## Artifact Inventory
* [`README.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/README.md)
* [`run_stage7_3.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/run_stage7_3.py)
* [`stage7_3_even_cv_results.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/stage7_3_even_cv_results.csv)
* [`stage7_3_fold_results.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/stage7_3_fold_results.csv)
* [`kt_distribution_even.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/kt_distribution_even.csv)
* [`stage7_3_temporal_alignment_audit.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/stage7_3_temporal_alignment_audit.csv)
* [`stage7_3_decision.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/stage7_3_decision.json)
* [`stage7_3_report.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/stage7_3_report.md)
* [`reproducibility_notes.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_3_kt_reformulation/reproducibility_notes.md)
