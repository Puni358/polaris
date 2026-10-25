# STAGE 8 — ENEV METAR IMPLEMENTATION PROVENANCE & PROTOCOL AUDIT

**Audit Date:** 2026-09-13  
**Audit Status:** **IMPLEMENTATION-QUALIFIED / NOT YET SEALED**  
**ODD Firewall Status:** **INTACT (0 Reads / 0 Predictions / 0 Metrics)**  

---

## 1. Executive Summary & Audit Decision

A forensic provenance audit of the executed ENEV METAR EVEN experiment parser revealed **two protocol deviations** relative to the pre-registered experiment specification:

1. **Timestamp Substitutions (18 / 347 origins, 5.19%):** The parser used a 2-hour lookback window fallback (`sub.iloc[-1]`), substituting 23:20 UTC (16 origins) or 22:50 UTC (2 origins) reports when the exact 23:50 UTC report was absent in the IEM archive, rather than enforcing exact 23:50 UTC matching.
2. **Silent Clear Fallback (1 / 347 origins, 0.29%):** On `2024-10-22 00:00:00`, the report contained `skyc1 = ///` with rain `-RA` and cloud base `skyl1 = 3000.0` ft. Because `///` was not in the parsed layer list, it fell through to the `else` default branch, silently assigning `0.0` oktas (clear sky) and `5000.0` m base.

### Audit Decision: **`IMPLEMENTATION-QUALIFIED / NOT YET SEALED`**

The historical EVEN experiment result (+0.067 W/m² MAE degradation) is **implementation-qualified**. The rejection cannot be formally sealed until the protocol deviations are rectified.

---

## 2. Origin Timestamp Breakdown (347 Benchmark Origins)

| Category | Count | Percentage | Description / Action |
| :--- | :---: | :---: | :--- |
| **Exact 23:50 UTC Report** | **329** | **94.81%** | Strict causal match (10 min before t0) |
| **Earlier Report (23:20 UTC)** | **16** | **4.61%** | Substituted 23:20 report via parser lookback fallback |
| **Earlier Report (22:50 UTC)** | **2** | **0.58%** | Substituted 22:50 report via parser lookback fallback |
| **Other Timestamp (> 23:50 UTC)** | **0** | **0.00%** | None |
| **Genuinely Missing (No 2h report)** | **0** | **0.00%** | None |

---

## 3. Parser Fallback & Unparsed Branch Audit

### Unparsed Silent Clear Fallback Detail (1 Origin)

* **Forecast Start:** `2024-10-22 00:00:00+00:00`
* **Report Timestamp:** `2024-10-21 23:50:00+00:00`
* **Raw METAR:** `ENEV 212350Z AUTO 25017G34KT 220V310 9999 -RA ///030/// 10/08 Q0989 RERA RMK WIND 1400FT 24034G47KT`
* **Raw Fields:** `skyc1 = ///`, `skyl1 = 3000.0` ft, `wxcodes = -RA`
* **Erroneous Executed Value:** `enev_cloud_cover_okta = 0.0`, `enev_cloud_base_m = 5000.0` m
* **Physical Reality:** Active light rain (`-RA`) with automated cloud sensor code (`///`) and cloud base at 3000 ft (914.4 m). Silently converting this into clear sky (0 oktas, 5000 m) violated the mandate not to invent clear sky.

---

## 4. Pre-Registered Feature Inventory Verification

* **Control Features:** 37 Stage 8.1 champion features
* **Candidate Features:** 39 features (Control + `enev_cloud_cover_okta` + `enev_cloud_base_m`)
* **Feature Names Matched:** `VERIFIED`

---

## 5. Minimal Required Corrections

Before any re-execution, the parser must be updated with the following minimal corrections:
1. **Strict Timestamp Matching:** Strictly require exact 23:50 UTC matching. Flag absent 23:50 UTC origins explicitly as missing rather than silently substituting earlier 23:20/22:50 reports.
2. **Sensor Code & Whitespace Handling:** Strip whitespace from `skyc1` (handling `VV `) and parse `///` sensor cloud layer code when `skyl1` height is present (e.g. `///030` with rain).

---

## 6. Firewall & Governance Status

* [x] **ODD Firewall Intact:** 0 ODD reads, 0 ODD predictions, 0 ODD metrics evaluated.
* [x] **Historical EVEN Metrics Preserved:** Control EVEN MAE: 37.620054 W/m², Candidate EVEN MAE: 37.687360 W/m².
* [x] **No Rerun Triggered Automatically:** Pending minimal correction alignment.
* [x] **Spatial Decoupling:** Stated as a plausible interpretation, not a proven fact.
* [x] **Master Handoff & Route Registry:** Untouched.

---
*Audit completed by POLARIS Provenance Firewall System | 2026-09-13*
