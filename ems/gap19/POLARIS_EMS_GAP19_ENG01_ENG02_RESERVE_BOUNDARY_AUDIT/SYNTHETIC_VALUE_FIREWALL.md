# POLARIS EMS GAP19 — SYNTHETIC VALUE FIREWALL

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_ENG01_ENG02_RESERVE_BOUNDARY_AUDIT`  
**Firewall Objective**: **PREVENT PROMOTION OF SYNTHETIC/PROTOTYPE PARAMETERS TO PRODUCTION EVIDENCE**  

---

## 1. Master Synthetic Value Firewall Matrix

To ensure rigorous scientific integrity, all 13 known synthetic/prototype parameters in the POLARIS repository are cataloged and bound by explicit firewall classifications:

| Ref # | Parameter Description | Prototype Value | True Evidence Classification | Firewall Directive |
| :-: | :--- | :--- | :--- | :--- |
| **1** | Synthetic Critical Load | $30.0\text{ kW}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **MUST NOT** be cited as Nuolja station load. |
| **2** | Battery Nominal Capacity | $200.0\text{ kWh}$ ($200\text{ kWh}$) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **MUST NOT** be cited as Nuolja BESS hardware size. |
| **3** | Operational SOC Range | $20.0\% \dots 95.0\%$ | `IMPLEMENTATION_FACT` | **MUST NOT** be cited as manufacturer cell bounds. |
| **4** | Battery Roundtrip/Discharge Efficiency | $92.0\%$ ($\eta_{\text{dis}}=0.92$) | `IMPLEMENTATION_FACT` | **MUST NOT** be cited as inverter test bench result. |
| **5** | Battery Max Power | $50.0\text{ kW}$ ($50\text{ kW}$) | `IMPLEMENTATION_FACT` | **MUST NOT** be cited as inverter thermal limit. |
| **6** | Diesel Fuel Consumption Curve | $5.0\text{ L/h} + 0.25\text{ L/kWh}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **MUST NOT** be cited as diesel generator test sheet. |
| **7** | Generator Operating Bounds | $10.0\text{ kW} \dots 100.0\text{ kW}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **MUST NOT** be cited as nameplate generator limits. |
| **8** | Prototype $T_{\text{required}}$ Baseline | $6.0\text{ Hours}$ | `GOVERNANCE_VALUE` | **MUST NOT** claim empirical site validation. |
| **9** | Prototype Endurance Test Window | $72.0\text{ Hours}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **MUST NOT** be cited as station autonomy requirement. |
| **10** | Unit Test Rapid Window | $2.0\text{ Hours}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **MUST NOT** be cited as physical survivability floor. |
| **11** | Initial Test SOC States | $80.0\% / 50\% / 30\%$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **MUST NOT** be cited as site initial condition. |
| **12** | Test Fuel Inventory Levels | $500\text{L} / 100\text{L} / 50\text{L} / 12.5\text{L}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **MUST NOT** be cited as site fuel tank volume. |
| **13** | Ad-Hoc MILP $s_{\text{J2}}$ Cap | $200.0\text{ kWh}$ ($200\text{ kWh}$) | `IMPLEMENTATION_FACT` | **MUST NOT** be cited as governed policy bound. |

---

## 2. Firewall Enforcement Declaration

None of the 13 items above may become a production station requirement merely because it appeared repeatedly in past experiments or configuration files.
