# STAGE 8 — ENEV METAR PARSER SEMANTICS CORRECTION REPORT

**Date:** 2026-09-13  
**Status:** **READY_FOR_GOVERNED_EVEN_RERUN**  
**ODD Firewall Status:** **INTACT (0 Reads / 0 Predictions / 0 Metrics)**  

---

## 1. Executive Summary & Readiness Assessment

The scientific parser semantics audit and correction for ENEV METAR observations has been completed. All timestamp, sensor-code, and missing-data policies have been rigorously aligned with authoritative meteorological standards and POLARIS governance:

1. **Authoritative Decoding of `///` Sensor Code:** Under WMO Manual on Codes (WMO-No. 306) and ICAO Annex 3, `///` in AUTO METAR specifies that cloud amount/type is unidentifiable by the automated optical sensor. For the single affected report (`2024-10-21 23:50 UTC`, forecast start `2024-10-22 00:00 UTC`), the ceilometer-measured cloud base of 3000 ft ($914.4	ext<re.Match object; span=(32, 37), match='VV011'>$) is **preserved directly as an observed measurement**, while cloud amount is treated as unknown and causally imputed without inventing 6 or 0 oktas.
2. **Exact 23:50 UTC Coverage:** Exactly **329 / 347 origins (94.81%)** have an exact 23:50 UTC report present. Exactly **18 / 347 origins (5.19%)** are missing exact 23:50 UTC reports. Zero substitute reports (23:20 or 22:50 UTC) are loaded.
3. **Causal Missing-Data Policy & Explicit Indicator:** Missing origins are causally forward-filled from the previous valid 23:50 UTC report. An explicit binary feature `enev_is_missing` (0 = observed, 1 = missing) is added to the candidate feature set.
4. **Zero Silent-Clear Defaults Remaining:** Unparsed count = `0`, silent clear fallbacks = `0`.

### Status Verdict: **`READY_FOR_GOVERNED_EVEN_RERUN`**

---

## 2. Authoritative Interpretation of Sensor Code `///`

* **WMO / ICAO Standard:** In automated METAR reports, `///` indicates cloud type/amount is below sensor reporting threshold or unidentifiable due to environmental interference (e.g., active precipitation `-RA`).
* **Height Field (`030`):** The height field in `///030///` represents a valid laser-ceilometer ground-to-cloud-base measurement at 3000 ft ($914.4	ext<re.Match object; span=(32, 37), match='VV011'>$).
* **Correct Handling:**
  - `enev_cloud_base_m` = `914.4` m (`OBSERVED_HEIGHT_SLASHES`)
  - `enev_cloud_cover_okta` = causally imputed from previous valid 23:50 UTC okta (`IMPUTED_UNKNOWN_AMOUNT_SLASHES`)
  - Arbitrary assumption of 6 oktas or 0 oktas is completely eliminated.

---

## 3. Observed vs. Imputed Origin Coverage Summary

| Coverage Category | Origin Count | Percentage | Description & Governance Rule |
| :--- | :---: | :---: | :--- |
| **Exact 23:50 UTC Observed** | **329** | **94.81%** | Direct instrument measurement at 23:50 UTC (10 min before t0) |
| **Exact 23:50 UTC Missing (Imputed)** | **18** | **5.19%** | Absent 23:50 UTC report; causally forward-filled with `enev_is_missing = 1` |
| **Substitute Timestamp Reports Used** | **0** | **0.00%** | Strictly zero earlier reports (23:20/22:50 UTC) substituted |
| **Total Benchmark Origins** | **347** | **100.00%** | Benchmark origin set preserved exactly |

---

## 4. Detailed Okta & Base Status Breakdown

| Status Code | Okta Count | Base Count | Explanation |
| :--- | :---: | :---: | :--- |
| **OBSERVED_CLEAR / CLEAR_SENTINEL** | 106 | 106 | Explicit CAVOK/NSC/NCD/SKC/CLR code in raw METAR (0.0 oktas, 5000m sentinel) |
| **OBSERVED_FEW / HEIGHT** | 89 | 89 | FEW layer reported (1.5 oktas, `skyl1` $	imes 0.3048$ m base) |
| **OBSERVED_BKN / HEIGHT** | 68 | 68 | BKN layer reported (6.0 oktas, `skyl1` $	imes 0.3048$ m base) |
| **OBSERVED_SCT / HEIGHT** | 39 | 39 | SCT layer reported (3.5 oktas, `skyl1` $	imes 0.3048$ m base) |
| **IMPUTED_MISSING_ORIGIN** | 18 | 18 | Absent 23:50 UTC report (forward-filled, `enev_is_missing = 1`) |
| **OBSERVED_VV / VV_HEIGHT** | 16 | 16 | Vertical Visibility reported (8.0 oktas, `VV` height / `skyl1` base) |
| **OBSERVED_OVC / HEIGHT** | 10 | 10 | OVC layer reported (8.0 oktas, `skyl1` $	imes 0.3048$ m base) |
| **IMPUTED_SLASHES / OBSERVED_SLASHES** | 1 | 1 | `///` sensor code: amount imputed, height observed at 914.4m (3000 ft) |

---

## 5. Candidate Feature Inventory for Governed Rerun

The candidate feature set consists of the frozen Stage 8.1 37 control features plus exactly **3 ENEV features**:

1. `enev_cloud_cover_okta` (numeric okta: 0, 1.5, 3.5, 6, 8, or causally imputed)
2. `enev_cloud_base_m` (numeric cloud base height in meters AGL, 5000m clear sentinel, or causally imputed)
3. `enev_is_missing` (explicit binary indicator: 0 = observed exact 23:50 UTC, 1 = missing exact 23:50 UTC)

---

## 6. Firewall & Governance Status

* [x] **ODD Firewall Intact:** 0 ODD reads, 0 ODD predictions, 0 ODD metrics computed.
* [x] **No Rerun Triggered Automatically:** Pending explicit authorization.
* [x] **Master Handoff & Route Registry:** Untouched.
* [x] **Champion Status:** Stage 8.1 700 hPa Steering Wind Model preserved unchanged.

---
*Report compiled & verified by POLARIS Scientific Audit Engine | 2026-09-13*
