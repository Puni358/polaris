# POLARIS EMS GAP19 — ENGINEERING INPUT REGISTER

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_ENG01_ENG02_RESERVE_BOUNDARY_AUDIT`  
**Classification System**: **8 MANDATORY EVIDENCE CATEGORIES**  

---

## 1. Master Engineering Input Register

| Ref ID | Candidate Engineering Input | Required Role in Reserve Model | Current Value in Project / Code | Evidence Classification | Evidence Source / Provenance | Production Readiness |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **INP-01** | **$P_{\text{critical}}(t)$ Load Trajectory** | Defines baseline AC critical load energy $W_{\text{crit\_required}}$. | Synthetic array ($30\text{ kW}$ / scenario profiles) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | Scenario JSON test fixtures | **NOT_READY** |
| **INP-02** | **Essential Heating Load** | Sub-component of protected critical load. | Unspecified | `NOT_ESTABLISHED` | Zero measured site data | **NOT_READY** |
| **INP-03** | **Water Treatment / Filtration** | Sub-component of protected critical load. | Unspecified | `NOT_ESTABLISHED` | Zero measured site data | **NOT_READY** |
| **INP-04** | **Emergency Communications** | Sub-component of protected critical load. | Unspecified | `NOT_ESTABLISHED` | Zero measured site data | **NOT_READY** |
| **INP-05** | **$T_{\text{required\_baseline}} = 6\text{h}$ Semantics** | Defines lookahead window length for EBR reserve. | $6.0\text{ hours}$ | `GOVERNANCE_VALUE` | Governed Decision Record | **SEALED_SEMANTICS** |
| **INP-06** | **$T_{\text{required}}$ Station Validation** | Validates $6\text{h}$ against Nuolja weather logistics. | Un-validated | `NOT_ESTABLISHED` | EVID-ST-06 / EVID-ST-05 missing | **NOT_READY** |
| **INP-07** | **Nominal Battery Capacity ($C_{\text{bat}}$)** | Converts SOC percentage to Wh energy. | $200,000.0\text{ Wh}$ ($200\text{ kWh}$) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | `battery.yaml` prototype config | **NOT_READY** |
| **INP-08** | **Minimum Operational SOC ($SOC_{\min}$)** | Defines physical battery reserve floor $E_{\min}$. | $20.0\%$ ($40\text{ kWh}$) | `IMPLEMENTATION_FACT` | `battery.yaml` prototype config | **NOT_READY** |
| **INP-09** | **Maximum Operational SOC ($SOC_{\max}$)** | Defines physical battery energy ceiling $E_{\max}$. | $95.0\%$ ($190\text{ kWh}$) | `IMPLEMENTATION_FACT` | `battery.yaml` prototype config | **NOT_READY** |
| **INP-10** | **Discharge Efficiency ($\eta_{\text{dis}}$)** | Converts AC critical energy to battery stored energy. | $0.92$ ($92\%$) | `IMPLEMENTATION_FACT` | `battery.yaml` prototype config | **NOT_READY** |
| **INP-11** | **Max Discharge Power ($P_{\text{dis,max}}$)** | Bounds instantaneous battery discharge rate. | $50,000.0\text{ W}$ ($50\text{ kW}$) | `IMPLEMENTATION_FACT` | `battery.yaml` prototype config | **NOT_READY** |
| **INP-12** | **Diesel Generator Rating** | Backup generation upper bound $P_{\text{D,max}}$. | $100,000.0\text{ W}$ ($100\text{ kW}$) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | `diesel.yaml` prototype config | **NOT_READY** |
| **INP-13** | **Diesel Minimum Stable Output** | Generator low-load operating limit $P_{\text{D,min}}$. | $10,000.0\text{ W}$ ($10\text{ kW}$) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | `diesel.yaml` prototype config | **NOT_READY** |
| **INP-14** | **Diesel Fuel Consumption Curve** | Relates diesel electrical output to fuel burn rate. | $5.0\text{ L/h} + 0.00025\text{ L/Wh}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | `diesel.yaml` prototype config | **NOT_READY** |
| **INP-15** | **Real Station Fuel Inventory** | Available fuel for backup generator operation. | Unspecified ($100\text{L}$ test default) | `NOT_ESTABLISHED` | EVID-ST-01 missing | **NOT_READY** |
| **INP-16** | **Station Fuel Resupply Interval** | Logistics window for fuel tank replenishment. | Unspecified | `NOT_ESTABLISHED` | EVID-ST-05 missing | **NOT_READY** |
| **INP-17** | **Renewable Availability Assumption** | Generation profile assumed during reserve lookahead. | Full forecast point generation | `GOVERNANCE_REQUIRED` | Pending policy decision | **NOT_READY** |

---

## 2. Summary Breakdown by Category

* `STATION_SPECIFIC_ESTABLISHED`: **0**
* `STATION_SPECIFIC_REPORTED_BUT_UNVERIFIED`: **0**
* `REGIONAL_PROXY`: **0**
* `SYNTHETIC_ENGINEERING_ASSUMPTION`: **6**
* `IMPLEMENTATION_FACT`: **4**
* `GOVERNANCE_VALUE`: **1**
* `GOVERNANCE_REQUIRED`: **1**
* `NOT_ESTABLISHED`: **5**
* `NOT_REQUIRED`: **0**
