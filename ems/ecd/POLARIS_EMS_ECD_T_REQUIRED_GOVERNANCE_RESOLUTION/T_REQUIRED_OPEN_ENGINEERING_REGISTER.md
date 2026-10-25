# POLARIS EMS — T_REQUIRED OPEN ENGINEERING REGISTER

## Executive Statement

This register tracks physical station engineering parameters required before $T_{\text{required}}$ and ECD resource survivability calculations can be deployed to production.

These parameters are **TECHNICAL ENGINEERING DEFINITIONS** and **STATION DATA INPUTS**. They do NOT require serial human policy selection and must be resolved through empirical station engineering, single-line diagrams, and equipment specification sheets.

---

## Master Open Engineering Register

| Parameter / Engineering Input | Current Status | Impact on ECD $T_{\text{required}}$ Evaluation | Required Engineering Resolution Step |
| :--- | :--- | :--- | :--- |
| **Protected Equipment Inventory** | `ENGINEERING_REQUIRED` | Identifies specific station loads comprising $P_{\text{critical}}$. | Station electrical engineering equipment audit. |
| **Critical Circuit Mapping** | `ENGINEERING_REQUIRED` | Maps breaker control actuators to physical load circuits. | Single-line diagram & breaker panel wiring audit. |
| **Dynamic Critical Load $P_{\text{critical}}(t)$** | `ENGINEERING_REQUIRED` | Integral trajectory evaluation of critical power demand over time. | Critical load profiling & time-series modeling. |
| **Minimum Viable Operating Levels** | `ENGINEERING_REQUIRED` | Defines lower power bounds for proportional shortfall allocation. | Equipment minimum power operational specification. |
| **Usable Battery Capacity $C_{\text{usable}}$** | `PROTOTYPE_ESTABLISHED` | Determines stored electrical energy horizon ($T_{\text{battery}}$). | Battery spec sheet & state-of-health calibration. |
| **Battery Discharge Limits & $\eta_{\text{dis}}$** | `PROTOTYPE_ESTABLISHED` | Determines net power delivery efficiency to critical loads. | Battery inverter & discharge curve calibration. |
| **Battery SOC Bounds ($\text{SOC}_{\text{min}}, \text{SOC}_{\text{max}}$)** | `PROTOTYPE_ESTABLISHED` | Sets physical discharge floor and charging ceiling. | Battery management system (BMS) config verification. |
| **Battery Thermal Constraints** | `NOT_ESTABLISHED` | Derates capacity or disconnects battery in extreme cold/heat. | BMS thermal protection spec sheet review. |
| **Generator Minimum Load $P_{\text{gen,min}}$** | `PROTOTYPE_ESTABLISHED` | Sets lower bound for generator operation (prototype uses 10 kW). | Diesel generator mechanical spec review. |
| **Generator Fuel Curve $f_{\text{rate}}(P)$** | `PROTOTYPE_ESTABLISHED` | Determines fuel consumption rate ($L/h$) vs load ($kW$). | Engine fuel curve calibration / test bench data. |
| **Usable Diesel Inventory** | `INTERFACE_ESTABLISHED` | Ingress telemetry signal `StationState.fuel_remaining_liters`. | Fuel tank level sensor calibration & verification. |
| **Fuel Tank Usable Volume $V_{\text{tank}}$** | `NOT_ESTABLISHED` | Physical capacity bound for fuel storage endurance. | Site fuel tank mechanical specification sheet. |
| **Renewable Survivability Assumption** | `DECISION_REQUIRED` | Governs whether $P_{\text{renewable}}=0$ baseline or P10 quantile is used. | Station meteorological risk assessment. |

---

## Firewall Confirmation

Zero values in this register have been assumed or invented. All 13 items remain open for empirical station engineering resolution.
