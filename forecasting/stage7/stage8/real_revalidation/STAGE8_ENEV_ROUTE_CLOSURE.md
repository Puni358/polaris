# STAGE 8 — ENEV UPSTREAM METAR ROUTE CLOSURE REPORT

**Date:** 2026-09-13  
**Route:** `ENEV_UPSTREAM_METAR` (Harstad/Narvik Airport, Evenes METAR Cloud Observations)  
**Station Location:** 86 km WNW of Nuolja target station, coastal fjord entrance (68.4913° N, 16.6781° E, 26 m ASL)  
**Final Governance Verdict:** `REJECTED_BY_EVEN_GATES`  
**Operational Champion:** Stage 8.1 37-feature HGB control (`RETAINED_UNTOUCHED`)

---

## Executive Summary

The governed EVEN-only experiment for the **ENEV Upstream METAR** cloud observation route has been completed. The Candidate model evaluated Stage 8.1 37-feature HGB control augmented with exactly 3 ENEV features (`enev_cloud_cover_okta`, `enev_cloud_base_m`, `enev_is_missing`) using strictly matched exact 23:50 UTC ($t_0 - 10\text{ min}$) METAR reports across 174 EVEN origins.

While the route successfully satisfied all data integrity and protocol reproduction gates (**G5** and **G6**), it failed all four pre-registered predictive quality gates (**G1–G4**). Consequently, the ENEV upstream METAR route is **FORMALLY CLOSED AND REJECTED**.

> [!IMPORTANT]
> **ODD Firewall Integrity:** 100% intact. Zero ODD target data was accessed, zero ODD predictions were generated, and zero ODD evaluation metrics were calculated.

---

## 1. Candidate & Benchmark Definition

- **Locked Control:** Stage 8.1 37-feature HGB control
- **Candidate Features (exactly 3):**
  1. `enev_cloud_cover_okta`: Cloud cover amount in oktas (0–8 scale) derived from METAR cloud layers or CAVOK/NSC/NCD/SKC reports.
  2. `enev_cloud_base_m`: Cloud base height in meters ASL derived from METAR cloud layer heights or CAVOK ceiling defaults.
  3. `enev_is_missing`: Binary indicator (1 if exact 23:50 UTC report absent and causally forward-filled, 0 if observed).
- **Control Feature Count:** 37
- **Candidate Feature Count:** 40
- **Timestamp Matching Rule:** For every origin $t_0$, strictly require exact ENEV report at $t_0 - 10\text{ min} = 23:50\text{ UTC}$. Zero timestamp substitutions permitted.
- **Coverage Summary:**
  - Exact 23:50 Observed: **329 / 347 origins (94.81%)**
  - Exact 23:50 Missing: **18 / 347 origins (5.19%)**
  - Missing Imputation: Pre-declared causal forward-fill with `enev_is_missing = 1`

---

## 2. Gate Evaluation Results

| Gate | Description | Criteria | Observed Value | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **G1** | ΔMAE (Candidate - Control) | $\le -0.50\text{ W/m}^2$ | $+0.198852\text{ W/m}^2$ | **FAIL** |
| **G2** | Folds Improved | $\ge 4 / 5\text{ folds}$ | $3 / 5\text{ folds}$ (Folds 1, 2, 5) | **FAIL** |
| **G3** | Maximum Fold Degradation | $\le +0.50\text{ W/m}^2$ | $+1.392324\text{ W/m}^2$ (Fold 3) | **FAIL** |
| **G4** | Candidate RMSE & nMAE | $\le \text{Control}$ | RMSE $+0.516706\text{ W/m}^2$ ($60.68$ vs $60.16$) | **FAIL** |
| **G5** | 100% Causal Data Matching | Exact 23:50 UTC | $329/347$ observed, $18/347$ missing, $0$ substitutions | **PASS** |
| **G6** | Control Reproduction | Exact Match | Control EVEN MAE $37.620054\text{ W/m}^2$ reproduced | **PASS** |

### Per-Fold Performance Breakdown (EVEN 174 Origins)

| Fold | Control MAE ($\text{W/m}^2$) | Candidate MAE ($\text{W/m}^2$) | $\Delta\text{MAE}$ ($\text{W/m}^2$) | Control RMSE ($\text{W/m}^2$) | Candidate RMSE ($\text{W/m}^2$) | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 49.311419 | 49.130659 | $-0.180760$ | 81.354967 | 81.298297 | Improved |
| **Fold 2** | 70.568800 | 70.320078 | $-0.248722$ | 103.743912 | 103.564529 | Improved |
| **Fold 3** | 40.345573 | 41.737897 | $+1.392324$ | 67.256670 | 69.678453 | **Degraded** |
| **Fold 4** | 25.770418 | 25.897717 | $+0.127298$ | 44.613169 | 45.196849 | **Degraded** |
| **Fold 5** | 2.104058 | 2.008177 | $-0.095881$ | 3.834508 | 3.648629 | Improved |
| **Overall** | **37.620054** | **37.818906** | **$+0.198852$** | **60.160645** | **60.677351** | **REJECTED** |

---

## 3. Physical & Scientific Interpretation

1. **Observational Validity:** ENEV was verified as a genuine, real-data, causally valid upstream observational station. The raw dataset, parser semantics, and timestamp alignment were validated under rigorous WMO METAR standards.
2. **Predictive Performance:** Adding coastal ENEV METAR cloud cover and cloud base height features increased overall EVEN MAE by $+0.198852\text{ W/m}^2$ and caused severe degradation on Fold 3 ($+1.392324\text{ W/m}^2$).
3. **Physical Decoupling Mechanism:** The 86 km WNW distance between Evenes and Nuolja traverses the Scandes mountain range (peak elevations $>1,500\text{ m}$). Coastal cloud layers at ENEV (sea level, $26\text{ m}$ ASL) undergo significant atmospheric transformation—including upwind mountain cloud blocking, forced orographic ascent, and lee-side Foehn wave dissipation—before reaching inland valleys at Nuolja. Consequently, point METAR cloud observations at ENEV do not provide reliable micro-scale cloud state information for Nuolja irradiance forecasting.
4. **Scope of Conclusion:** This closure applies specifically to this ENEV feature representation and route under the governed benchmark. It does **NOT** imply that all upstream METAR observations are physically void of information, but proves that ENEV METAR features fail to improve upon Stage 8.1.

---

## 4. Research-Space Reduction Inventory Entry

```json
{
  "ROUTE": "ENEV_UPSTREAM_METAR",
  "STATUS": "CLOSED_AFTER_GOVERNED_EVEN_REJECTION",
  "REASON": "FAILED_G1_G2_G3_G4",
  "DATA_VALIDITY": "PASSED_G5",
  "CONTROL_VALIDITY": "PASSED_G6",
  "ODD_STATUS": "FIREWALLED"
}
```

---

## 5. Provenance & Reproducibility Hashes

- **Execution Script SHA-256:** `8b0ce51d17429f4b0a6bfd2e23c880abf36eabccb1fcd777fdaa44e57921c3a0`
- **ENEV METAR CSV SHA-256:** `fca7069e029fe2c80b8972dc848fa9cbc540673f507ef84fe221d21812055a2d`
- **NWP Feature CSV SHA-256:** `8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16`
- **Results Artifacts:**
  - [`STAGE8_ENEV_GOVERNED_EVEN_RESULTS.json`](file:///home/punith-bs/.gemini/antigravity/brain/11d26e00-a045-428c-bdbb-e7c8fb7429cd/STAGE8_ENEV_GOVERNED_EVEN_RESULTS.json)
  - [`STAGE8_ENEV_GOVERNED_EVEN_RESULTS.md`](file:///home/punith-bs/.gemini/antigravity/brain/11d26e00-a045-428c-bdbb-e7c8fb7429cd/STAGE8_ENEV_GOVERNED_EVEN_RESULTS.md)
  - [`STAGE8_ENEV_REPRODUCIBILITY_MANIFEST.json`](file:///home/punith-bs/.gemini/antigravity/brain/11d26e00-a045-428c-bdbb-e7c8fb7429cd/STAGE8_ENEV_REPRODUCIBILITY_MANIFEST.json)

---

## 6. Champion Status Confirmation

- **Operational Champion:** Stage 8.1 37-feature HGB control
- **Master Handoff (`POLARIS_MASTER_HANDOFF.md`):** Untouched and unmodified.
- **Route Registry (`POLARIS_STAGE8_ROUTE_REGISTRY`):** Untouched and unmodified.
- **ODD Benchmark Metrics:**
  - ODD Daytime MAE: **$36.188657\text{ W/m}^2$**
  - ODD Daytime nMAE: **$28.0688\%$**
  - ODD Daytime RMSE: **$64.219495\text{ W/m}^2$**
  - ODD Daytime Bias: **$+1.439399\text{ W/m}^2$**
