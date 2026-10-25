# POLARIS — STAGE 8 REAL-DATA REBUILD ARTIFACT MANIFEST

**Timestamp:** 2026-09-13T14:33:41Z  
**Directory:** `/home/punith-bs/01polaris (Copy)/stage7/stage8/real_revalidation/`

---

## 1. Primary Data & Prediction Artifacts

| Artifact Name | File Path | Size | SHA256 Checksum | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Real AROME Extraction CSV** | [`arome_arctic_347_origins_real_subset.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/arome_arctic_347_origins_real_subset.csv) | $1.03\text{ MB}$ | `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298` | 347 origins $\times$ 24 lead hours = 8,328 real AROME tuples ($U_{700}, V_{700}, \text{LWP}$). |
| **Persisted ODD Predictions CSV** | [`STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv) | $760.3\text{ KB}$ | `26bac202e3ce3cd851f1467a6a1c1b675b0409285058f895924d095eb8f0b908` | Row-level predictions for all 173 ODD origins (4,152 rows). |
| **Candidate Freeze JSON** | [`STAGE8_17A_REAL_AROME_FREEZE.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_FREEZE.json) | $2.45\text{ KB}$ | `a67cd426e84cfb92d6e326aa6bc7d62fb6a76ddc5ea5d0df8ff4fa127a5d3f2c` | Frozen feature list, model parameters, fold metrics, and dataset hash. |
| **Single-Origin Test CSV** | [`arome_arctic_nuolja_20240119T18Z_real_subset.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/arome_arctic_nuolja_20240119T18Z_real_subset.csv) | $3.16\text{ KB}$ | `fdb42f63ebc37223774eba65c21dd0b9cef837ac16217b385eef8ff413a73d94` | Test point extraction for `2024-01-19 18Z`. |

---

## 2. Pipeline Scripts & Logs

| File Name | Location | Description |
| :--- | :--- | :--- |
| [`extract_arome_opendap_subset.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/extract_arome_opendap_subset.py) | `real_revalidation/` | Parallel OPeNDAP `.ascii` point-subset extraction script. |
| [`run_stage8_17a_real_revalidation.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/run_stage8_17a_real_revalidation.py) | `real_revalidation/` | Main revalidation pipeline (data validation, EVEN 5-fold CV, freeze, prediction persistence). |
| [`verify_stage8_17a_real_arome_metrics.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/verify_stage8_17a_real_arome_metrics.py) | `real_revalidation/` | Independent metric verifier reading predictions from disk CSV. |
| [`STAGE8_17A_REAL_AROME_RERUN.log`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_RERUN.log) | `real_revalidation/` | Timestamped live execution log. |

---

## 3. Governance Summary

- **Real Data Status:** `100% REAL HISTORICAL NWP DATA`
- **Missing / Padded / Synthetic Values:** `0`
- **Historical Comparison:** Reported $35.241085\text{ W/m}^2$ vs Real AROME $36.426418\text{ W/m}^2$
- **Final Verdict:** `CLASSIFICATION C. NOT REPRODUCED / DEGRADED ON REAL AROME DATA`
