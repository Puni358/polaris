# POLARIS — STAGE 8.17A REAL-DATA REBUILD FINAL REPORT

**Timestamp:** 2026-09-13T14:33:41Z  
**Repository:** `/home/punith-bs/01polaris (Copy)`  
**Target Location:** Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)  
**Final Status:** `REBUILD COMPLETE — STAGE 8.17A CLASSIFIED AS NOT REPRODUCED`

---

## 1. Executive Summary

This report documents the end-to-end real-data rebuild of **Stage 8.17A (AROME-Arctic Structural Disagreement)** following the discovery that prior experimental implementations utilized synthetic pseudo-random inputs (`seed 817`).

### Key Accomplishments
1. **Real Data Acquisition:** Extracted 100% real historical AROME-Arctic 2024 NWP data from MET Norway THREDDS via server-side OPeNDAP `.ascii` slicing across all 347 locked benchmark origins (8,328 forecast tuples, SHA256: `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298`).
2. **Variable Semantics & Surface-Aware Integration:** Verified $U_{700}$, $V_{700}$, and specific cloud liquid water mass fraction ($q_l$). Hydrostatic integration for Liquid Water Path ($LWP$) was truncated at surface air pressure ($908.61\text{ hPa}$ at Nuolja).
3. **40-Feature Pipeline Rebuild:** Reconstructed exact 40-feature architecture (`base_28` + Stage 6.6 + Stage 7.5 + Stage 8.1 + `wind_disagreement_700` + `LWP_disagreement`).
4. **EVEN 5-Fold Cross-Validation:** Verified baseline reproduction on EVEN origins (Control MAE = $44.718895\text{ W/m}^2$). Frozen candidate artifact saved prior to ODD testing.
5. **ODD Evaluation & Disk Persistence:** Evaluated 173 locked ODD origins ($4,152$ prediction rows) and persisted row-level output to disk (`STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv`, SHA256: `26bac202e3ce3cd851f1467a6a1c1b675b0409285058f895924d095eb8f0b908`).
6. **Independent Metric Verification:** Derived summary metrics directly from disk CSV without hardcoded literals.

---

## 2. Revalidation Performance Results

| Pipeline Stage | Control Model (38 Feats) | Real AROME Candidate (40 Feats) | Delta (Cand - Ctrl) | Result |
| :--- | :---: | :---: | :---: | :---: |
| **EVEN CV MAE (174 Origins)** | $44.718895\text{ W/m}^2$ | $44.553480\text{ W/m}^2$ | $-0.165414\text{ W/m}^2$ | Passed 5 EVEN Gates |
| **ODD Daytime MAE (173 Origins)** | **$36.211027\text{ W/m}^2$** | **$36.426418\text{ W/m}^2$** | **$+0.215391\text{ W/m}^2$** | **DEGRADED** |
| **ODD Daytime nMAE** | $28.0861\%$ | **$28.2532\%$** | $+0.1671\text{ pp}$ | **DEGRADED** |
| **ODD Daytime RMSE** | $64.230507\text{ W/m}^2$ | **$64.611649\text{ W/m}^2$** | $+0.381142\text{ W/m}^2$ | **DEGRADED** |
| **ODD Daytime Bias** | $+0.994557\text{ W/m}^2$ | **$+0.537993\text{ W/m}^2$** | $-0.456564\text{ W/m}^2$ | Lower Bias |
| **Night MAE** | $0.000000\text{ W/m}^2$ | **$0.000000\text{ W/m}^2$** | $0.000000\text{ W/m}^2$ | Causal Night Zero |
| **Bootstrap 95% CI** | $-$ | $-$ | $[-0.1127, +0.4749]\text{ W/m}^2$ | Spans Zero (11.8% Impr) |

---

## 3. Historical Comparison & Classification

- **Historically Claimed MAE (Synthetic Input):** $35.241085\text{ W/m}^2$
- **Revalidated Real-Data MAE:** $36.426418\text{ W/m}^2$
- **Discrepancy:** $+1.185333\text{ W/m}^2$ higher error on real data.
- **Classification:** **`C. NOT REPRODUCED / DEGRADED ON REAL AROME DATA`**

---

## 4. Operational Champion & Project Governance

1. **Official Champion Unchanged:**  
   The project champion remains **Stage 8.19 ABIS GNSS Model** (or baseline Stage 8.1 / Stage 7.5 depending on numerical provenance status of 8.19). Stage 8.17A is **NOT** promoted.
2. **Master Registry Integrity:**  
   `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY.json` remain untouched.
3. **Data Provenance:**  
   All 8,328 raw extraction tuples and 4,152 row-level ODD prediction records are permanently persisted with verifiable SHA256 checksums in `stage7/stage8/real_revalidation/`.

```
REBUILD COMPLETE — REAL AROME DATASET & PERSISTED PREDICTIONS VERIFIED.
```
