# POLARIS EMS GAP19 — AUTHORITATIVE SOURCE REGISTER

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY`  
**Quality Rule**: **AUTHORITATIVE SOURCE METADATA & REASON FOR CLASSIFICATION**  

---

## 1. Master Authoritative Source Register

| Source ID | Source Title / Document | Organization | Source Type | Target Station | Location | Claim / Information | Classification | Can Support Production Claim? | Reason for Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **SRC-ST-01** | SITES Meteorological Station Metadata | SITES / ANS | Scientific Infrastructure Registry | SITES Nuolja Station | Abisko, Sweden | Solar shortwave ($SW\_IN$), Clearsky GHI, Wind speed time-series | `STATION_SPECIFIC_ESTABLISHED` | **YES** *(Meteorology only)* | Direct measured open-access meteorological data streams for Nuolja site. |
| **SRC-ST-02** | DEC-004 Option D Selection Record | POLARIS Governance Authority | Governed Decision Record | POLARIS System Architecture | Governed | Option D Protected Critical-Load Fallback (D1–D6) selected | `GOVERNANCE_VALUE` | **YES** *(Policy only)* | Human governance decision sealing emergency response policy. |
| **SRC-ST-03** | `battery.yaml` Prototype Config | POLARIS Software Engineering | Prototype Software Config | Synthetic Test Model | Local Repository | $200\text{kWh}$ BESS, $20\%\dots95\%$ SOC, $92\%$ efficiency, $50\text{kW}$ power | `SYNTHETIC_ENGINEERING_ASSUMPTION` / `IMPLEMENTATION_FACT` | **NO** | Created as software prototype default; not tied to site hardware datasheet. |
| **SRC-ST-04** | `diesel.yaml` Prototype Config | POLARIS Software Engineering | Prototype Software Config | Synthetic Test Model | Local Repository | $100\text{kW}$ max power, $10\text{kW}$ min power, $5\text{L/h}+0.25\text{L/kWh}$ fuel model | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **NO** | Created as software prototype default; un-verified on engine bench. |
| **SRC-ST-05** | Synthetic Scenario JSON Fixtures | POLARIS Software Engineering | Prototype Software Fixtures | Synthetic Test Model | Local Repository | $30\text{kW}$ baseline critical load, $500\text{L}/100\text{L}/50\text{L}$ fuel levels | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **NO** | Created for deterministic software cycle testing; explicit claim firewall applied. |

---

## 2. Un-sourced & Generic Source Disqualification

* Generic blogs, forum posts, scraped aggregators, and un-linked product marketing specs were **disqualified** and excluded from the register.
* Regional proxy data from non-Nuolja stations (e.g., SANAE IV, Princess Elisabeth) are logged as proxy leads but strictly disqualified from supporting production claims for Nuolja (`CAN_SUPPORT_PRODUCTION_CLAIM = NO`).
