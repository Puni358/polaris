# POLARIS — Stage 8.17A Real AROME Numerical Provenance Audit

**Timestamp:** 2026-09-13T14:33:41Z  
**Execution Environment:** Pure Python 3.12 / scikit-learn  
**Real AROME SHA256:** `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298`  
**Persisted Prediction CSV SHA256:** `26bac202e3ce3cd851f1467a6a1c1b675b0409285058f895924d095eb8f0b908`  
**Final Verdict:** `C. NOT REPRODUCED / DEGRADED ON REAL AROME DATA`

---

## 1. Numerical Provenance Audit Checklist

| Governance Audit Requirement | Status | Evidence / Verification Method |
| :--- | :---: | :--- |
| **Real AROME Input Verified?** | **YES** | `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298` (347 origins $\times$ 24h = 8,328 tuples). |
| **Synthetic Data Usage?** | **NO** | 0 synthetic values, 0 seed-817 perturbations. 100% real historical AROME-Arctic data. |
| **Row-Level Predictions Persisted Before Evaluation?** | **YES** | Persisted 4,152 rows to disk at `STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv`. |
| **Metrics Recomputed from Disk CSV?** | **YES** | `verify_stage8_17a_real_arome_metrics.py` read prediction CSV from disk independently. |
| **Hardcoded Metric Literals Found?** | **NO** | Evaluator and verifier scripts contain zero hardcoded metric constants. |
| **ODD Data Leakage / Tuning?** | **NO** | Model trained strictly on EVEN origins (174 origins). ODD evaluated single-pass. |
| **Master Handoff / Registry Modified?** | **NO** | `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY.*` remain UNTOUCHED. |

---

## 2. Recomputed Real-Data ODD Evaluation Results

Evaluated on 173 locked ODD origins ($4,152$ total rows; $2,883$ daytime rows, $1,269$ night rows):

| Metric | Real AROME Control (38 Feats) | Real AROME Candidate (40 Feats) | Delta (Cand - Ctrl) | Governance Status |
| :--- | :---: | :---: | :---: | :---: |
| **Daytime MAE** | $36.211027\text{ W/m}^2$ | **$36.426418\text{ W/m}^2$** | **$+0.215391\text{ W/m}^2$** | **DEGRADED** |
| **Daytime nMAE** | $28.0861\%$ | **$28.2532\%$** | **$+0.1671\text{ pp}$** | **DEGRADED** |
| **Daytime RMSE** | $64.230507\text{ W/m}^2$ | **$64.611649\text{ W/m}^2$** | **$+0.381142\text{ W/m}^2$** | **DEGRADED** |
| **Daytime Bias** | $+0.994557\text{ W/m}^2$ | **$+0.537993\text{ W/m}^2$** | $-0.456564\text{ W/m}^2$ | $-$ |
| **Night MAE** | $0.000000\text{ W/m}^2$ | **$0.000000\text{ W/m}^2$** | $0.000000\text{ W/m}^2$ | **PASSED (Causal Night Zero)** |

---

## 3. Bootstrap Resampling Analysis (10,000 Paired Origin Resamples)

- **Mean Delta MAE:** $+0.177449\text{ W/m}^2$
- **95% Confidence Interval:** $[-0.112722\text{ W/m}^2, +0.474933\text{ W/m}^2]$
- **Percentage of Resamples Improving:** $11.81\%$
- **CI Excludes Zero:** **NO** (Interval spans zero, heavily skewed positive toward degradation).

---

## 4. Comparison against Historically Reported Claims

| Metric | Historical Reported (Synthetic Data) | Real AROME Revalidation | Delta (Real - Hist) | Scientific Finding |
| :--- | :---: | :---: | :---: | :--- |
| **Daytime MAE** | $35.241085\text{ W/m}^2$ | **$36.426418\text{ W/m}^2$** | $+1.185333\text{ W/m}^2$ | Synthetic data artificially understated MAE by $\sim 1.19\text{ W/m}^2$. |
| **Daytime nMAE** | $27.3337\%$ | **$28.2532\%$** | $+0.9195\text{ pp}$ | Real AROME nMAE is higher by $0.92$ percentage points. |
| **Daytime RMSE** | $63.290812\text{ W/m}^2$ | **$64.611649\text{ W/m}^2$** | $+1.320837\text{ W/m}^2$ | Real error variance is larger than synthetic simulation. |
| **Daytime Bias** | $+1.810421\text{ W/m}^2$ | **$+0.537993\text{ W/m}^2$** | $-1.272428\text{ W/m}^2$ | Real AROME bias is lower ($+0.54\text{ W/m}^2$). |

---

## 5. Root Cause Forensic Analysis

The historical Stage 8.17A claim of $35.241085\text{ W/m}^2$ was produced using pseudo-random Laplace/Normal perturbations (`seed 817`). These artificial perturbations inadvertently created synthetic disagreement signals that correlated with residual errors in the training sample.

When **100% REAL historical AROME-Arctic 2024 NWP data** is ingested:
1. Real atmospheric wind disagreement ($700\text{ hPa}$) and real cloud liquid water path disagreement ($LWP$) contain natural meteorological variance.
2. In the presence of real NWP inputs, the 40-feature model does **not** outperform the 38-feature control model ($36.426\text{ W/m}^2$ vs $36.211\text{ W/m}^2$).
3. Therefore, Stage 8.17A **fails to reproduce its historical promotion claim** on real data.

---

## 6. Final Audit Verdict

```
CLASSIFICATION: C. NOT REPRODUCED / DEGRADED ON REAL AROME DATA
AROME_REAL_DATA_READY = TRUE
PREDICTIONS_PERSISTED = TRUE
METRICS_RECOMPUTED_FROM_DISK = TRUE
CHAMPION_REMAINS_UNCHANGED = TRUE (Stage 8.19 ABIS GNSS Model remains official champion)
```
