# POLARIS STAGE 8 — ENEV METAR GOVERNED EVEN EXPERIMENT RESULTS

**Date:** 2026-09-13T14:13:32.893190+00:00  
**Final Verdict:** **`REJECTED_BY_EVEN_GATES`**  
**ODD Firewall Status:** **INTACT (0 Reads / 0 Predictions / 0 Metrics)**  
**Candidate Features:** `enev_cloud_cover_okta`, `enev_cloud_base_m`, `enev_is_missing`  
**Control Feature Inventory:** 37 features (Stage 8.1 Champion)  

---

## 1. Executive Summary & Gate Decision

| Gate | Description | Threshold | Observed | Result |
| :--- | :--- | :--- | :--- | :---: |
| **G1** | Aggregated Delta MAE | <= -0.50 W/m2 | +0.198852 W/m2 | **FAIL** |
| **G2** | Folds Improved | >= 4/5 folds | 3/5 | **FAIL** |
| **G3** | Max Fold Degradation | <= +0.50 W/m2 | +1.392324 W/m2 | **FAIL** |
| **G4** | nMAE & RMSE <= Control | Both <= Control | nMAE: 37.6237% vs 37.9745%, RMSE: 60.677351 vs 60.160645 | **FAIL** |
| **G5** | Causal Data Integrity | 329 observed / 18 missing | 329 observed / 18 missing | **PASS** |
| **G6** | Exact Control Reproduction | Matched | Control EVEN MAE = 37.620054 W/m2 | **PASS** |

**Final Verdict:** **`REJECTED_BY_EVEN_GATES`**

---

## 2. Quantitative Metric Comparison (EVEN Benchmark, 174 Origins)

| Metric | Stage 8.1 Control (37 Feat) | ENEV Candidate (40 Feat) | Delta | Threshold / Goal |
| :--- | :---: | :---: | :---: | :---: |
| **EVEN MAE (W/m2)** | 37.620054 | 37.818906 | **+0.198852** | <= -0.50 W/m2 |
| **EVEN nMAE (%)** | 37.9745 | 37.6237 | **-0.3508** | <= 0.00% |
| **EVEN RMSE (W/m2)** | 60.160645 | 60.677351 | **+0.516706** | <= 0.00 W/m2 |
| **EVEN Bias (W/m2)** | 4.218739 | 3.390700 | -0.828040 | — |

---

## 3. 5-Fold Forward-Chaining EVEN CV Breakdown

| Fold | Control MAE (W/m2) | Candidate MAE (W/m2) | Delta MAE (W/m2) | Improved? | Max Degradation Check |
| :---: | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | 49.311419 | 49.130659 | -0.180760 | YES | PASS |
| Fold 2 | 70.568800 | 70.320078 | -0.248722 | YES | PASS |
| Fold 3 | 40.345573 | 41.737897 | +1.392324 | NO | FAIL |
| Fold 4 | 25.770418 | 25.897717 | +0.127298 | NO | PASS |
| Fold 5 | 2.104058 | 2.008177 | -0.095881 | YES | PASS |

---

## 4. ENEV Observed vs. Missing Coverage

- **Exact 23:50 UTC Observed:** 329 / 347 origins (94.81%)
- **Exact 23:50 UTC Missing (Imputed):** 18 / 347 origins (5.19%)
- **Substitute Timestamp Reports Used:** 0 (Strict exact 23:50 matching)

### List of 18 Missing Exact-23:50 Origins:
- `2024-04-06 00:00:00+00:00`
- `2024-04-07 00:00:00+00:00`
- `2024-04-12 00:00:00+00:00`
- `2024-04-23 00:00:00+00:00`
- `2024-04-28 00:00:00+00:00`
- `2024-05-07 00:00:00+00:00`
- `2024-05-19 00:00:00+00:00`
- `2024-06-03 00:00:00+00:00`
- `2024-07-03 00:00:00+00:00`
- `2024-08-24 00:00:00+00:00`
- `2024-08-25 00:00:00+00:00`
- `2024-09-20 00:00:00+00:00`
- `2024-10-10 00:00:00+00:00`
- `2024-10-18 00:00:00+00:00`
- `2024-11-06 00:00:00+00:00`
- `2024-12-03 00:00:00+00:00`
- `2024-12-19 00:00:00+00:00`
- `2024-12-26 00:00:00+00:00`

---

## 5. Candidate Feature Importance

| Feature Name | Mean Permutation Importance (W/m2) |
| :--- | :---: |
| `enev_cloud_cover_okta` | -0.012748 |
| `enev_cloud_base_m` | -0.010543 |
| `enev_is_missing` | 0.001017 |

---

## 6. Provenance & Reproducibility Hashes

- **Script SHA256:** `8b0ce51d17429f4b0a6bfd2e23c880abf36eabccb1fcd777fdaa44e57921c3a0`
- **ENEV METAR CSV SHA256:** `fca7069e029fe2c80b8972dc848fa9cbc540673f507ef84fe221d21812055a2d`
- **NWP Forecast CSV SHA256:** `8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16`

---

## 7. ODD Firewall Status

- **ODD Access:** `FALSE`
- **ODD Target Reads:** `0`
- **ODD Predictions Generated:** `0`
- **ODD Metrics Evaluated:** `0`
- **Status:** Firewalled under EVEN gate failure protocol. Champion remains untouched.

---
*Report compiled & verified by POLARIS Governed Execution Engine | 2026-09-13T14:13:32.893287+00:00*
