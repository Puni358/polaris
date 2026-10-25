# STAGE 8 — RESEARCH-SPACE REDUCTION INVENTORY ENTRY: ENEV UPSTREAM METAR

**Timestamp:** 2026-09-13T19:47:00+05:30  
**Target Station:** Nuolja (WMO 02068)  
**Evaluated Route:** ENEV Upstream METAR Cloud Observations  

---

## Registered Inventory Entry

| Parameter | Recorded Value |
| :--- | :--- |
| **ROUTE** | `ENEV_UPSTREAM_METAR` |
| **STATUS** | `CLOSED_AFTER_GOVERNED_EVEN_REJECTION` |
| **REASON** | `FAILED_G1_G2_G3_G4` |
| **DATA_VALIDITY** | `PASSED_G5` |
| **CONTROL_VALIDITY** | `PASSED_G6` |
| **ODD_STATUS** | `FIREWALLED` |

---

## Route Summary

1. **Features Evaluated:** `enev_cloud_cover_okta`, `enev_cloud_base_m`, `enev_is_missing`
2. **Coverage & Causal Integrity:** 329 / 347 exact 23:50 UTC observed (94.81%), 18 / 347 missing (5.19%) causally forward-filled with `enev_is_missing = 1`. Passed **G5** (100% causal integrity).
3. **Control Benchmark:** Stage 8.1 37-feature HGB control ($37.620054\text{ W/m}^2$ EVEN MAE). Passed **G6** (exact control reproduction).
4. **Predictive Performance:** Candidate EVEN MAE $37.818906\text{ W/m}^2$ ($\Delta\text{MAE} = +0.198852\text{ W/m}^2$). Folds improved $3/5$. Max fold degradation $+1.392324\text{ W/m}^2$ (Fold 3). Candidate RMSE $60.677351\text{ W/m}^2$ vs Control RMSE $60.160645\text{ W/m}^2$. Failed **G1, G2, G3, G4**.
5. **ODD Status:** Absolute firewall maintained. Zero ODD reads, zero ODD predictions, zero ODD metric calculations.
6. **Operational Champion:** Stage 8.1 37-feature HGB control remains untouched as the operational champion ($36.188657\text{ W/m}^2$ ODD MAE).
