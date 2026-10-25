# POLARIS EMS GAP19 — EVIDENCE CLASSIFICATION MATRIX

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY`  
**Classification System**: **7 MANDATORY EVIDENCE CATEGORIES (A through G)**  

---

## 1. Master Evidence Classification Matrix

| Evidence Category Code | Category Description | Production Claim Eligibility | Active Items in POLARIS System |
| :-: | :--- | :---: | :--- |
| **A** | **`STATION_SPECIFIC_ESTABLISHED`** | **ELIGIBLE** | Target station identity (SITES Nuolja) & solar/wind meteorological time-series. |
| **B** | **`STATION_SPECIFIC_REPORTED_BUT_UNVERIFIED`** | **INELIGIBLE** | Un-verified custodian data dispatches (SANAP, IPF, ACEP). |
| **C** | **`REGIONAL_PROXY`** | **INELIGIBLE** | Non-Nuolja Antarctic/Arctic research station publications. |
| **D** | **`SYNTHETIC_ENGINEERING_ASSUMPTION`** | **INELIGIBLE** | $30\text{kW}$ critical load, $200\text{kWh}$ BESS, $100\text{kW}$ diesel, fuel levels ($100\text{L}, 50\text{L}$). |
| **E** | **`IMPLEMENTATION_FACT`** | **INELIGIBLE** | $20\%\dots95\%$ SOC window, $92\%$ efficiency, $50\text{kW}$ inverter power limit, $200\text{kWh}$ $s_{\text{J2}}$ cap. |
| **F** | **`GOVERNANCE_VALUE`** | **ELIGIBLE (Policy)** | DEC-004 Option D selection, $T_{\text{required\_baseline}} = 6\text{h}$ semantics, D1 conceptual categories. |
| **G** | **`NOT_ESTABLISHED`** | **INELIGIBLE** | Real site electrical load, BESS datasheets, engine fuel curves, fuel tank inspection sheets, single-line diagrams. |

---

## 2. Firewall Rule Summary

Only Category **A** (`STATION_SPECIFIC_ESTABLISHED`) and Category **F** (`GOVERNANCE_VALUE`) can support production claims. All items in Categories B, C, D, E, and G are strictly firewall-blocked.
