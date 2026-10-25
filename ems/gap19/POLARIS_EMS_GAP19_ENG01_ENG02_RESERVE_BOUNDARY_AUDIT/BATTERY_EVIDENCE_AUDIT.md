# POLARIS EMS GAP19 — BATTERY EVIDENCE AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_ENG01_ENG02_RESERVE_BOUNDARY_AUDIT`  
**Focus**: **BATTERY ENERGY STORAGE SYSTEM (BESS) PARAMETER PROVENANCE**  

---

## 1. Audit of Battery Engineering Inputs

| Battery Parameter | Value in `system/config/battery.yaml` | Evidence Classification | Production Status |
| :--- | :--- | :--- | :---: |
| **Nominal Capacity ($C_{\text{bat}}$)** | $200,000.0\text{ Wh}$ ($200\text{ kWh}$) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **NOT_ESTABLISHED** for real site |
| **Minimum Operational SOC ($SOC_{\min}$)** | $20.0\%$ ($40\text{ kWh}$) | `IMPLEMENTATION_FACT` | **NOT_ESTABLISHED** for real site |
| **Maximum Operational SOC ($SOC_{\max}$)** | $95.0\%$ ($190\text{ kWh}$) | `IMPLEMENTATION_FACT` | **NOT_ESTABLISHED** for real site |
| **Usable Energy Window** | $150,000.0\text{ Wh}$ ($150\text{ kWh}$) | `IMPLEMENTATION_FACT` | **NOT_ESTABLISHED** for real site |
| **Discharge Efficiency ($\eta_{\text{dis}}$)** | $0.92$ ($92\%$) | `IMPLEMENTATION_FACT` | **NOT_ESTABLISHED** for real site |
| **Charge Efficiency ($\eta_{\text{chg}}$)** | $0.92$ ($92\%$) | `IMPLEMENTATION_FACT` | **NOT_ESTABLISHED** for real site |
| **Max Discharge Power ($P_{\text{dis,max}}$)** | $50,000.0\text{ W}$ ($50\text{ kW}$) | `IMPLEMENTATION_FACT` | **NOT_ESTABLISHED** for real site |
| **Max Charge Power ($P_{\text{chg,max}}$)** | $50,000.0\text{ W}$ ($50\text{ kW}$) | `IMPLEMENTATION_FACT` | **NOT_ESTABLISHED** for real site |
| **Thermal / Temperature Limits** | Unspecified in config | `NOT_ESTABLISHED` | **NOT_ESTABLISHED** |
| **BMS Telemetry & Derating** | Unspecified in config | `NOT_ESTABLISHED` | **NOT_ESTABLISHED** |

---

## 2. Evidence Findings

1. **Synthetic Origin**: All values in `battery.yaml` represent prototype defaults chosen during initial software development.
2. **Missing Real-Station Evidence**: No certified manufacturer spec sheet, BMS telemetry map, or temperature derating curve for Nuolja station BESS hardware exists in the evidence base (Item **EVID-ST-03**).
3. **Firewall Requirement**: The $200\text{ kWh}$ capacity and $20\%\dots95\%$ SOC window MUST NOT be assumed to represent real Nuolja station hardware.
