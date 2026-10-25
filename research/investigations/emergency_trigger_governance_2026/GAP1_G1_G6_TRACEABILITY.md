# POLARIS — GAP 1 (G1–G6) TRACEABILITY MATRIX

## Executive Overview

This document provides complete end-to-end traceability for the **provisional human decisions G1 through G6**, mapping each decision to **Approved Core Governance Rules**, **Mathematical Formalisms**, **POLARIS Codebase Parameters**, **Verification Test Cases (A–U)**, and **Downstream Gaps (GAP 2–5)**.

---

## 1. Complete G1–G6 Traceability Matrix

| Provisional Decision | Governed Policy Mapping | Formal Mathematical Equation | Codebase Location | Validating Test Cases | Downstream Gap Impact |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **G1: Generator Availability** (Option 1D) | Decision 4 (Resource Loss Assessment) | $A_{\text{cred\_k}}(t) = \mathbb{I}(\text{V} = \text{VALID} \land \text{Op} = \text{OK} \land \text{Disp} = \text{OK})$ | `station_state.diesel_running` | **Test H, I, J, K** | Impacts **GAP-03** (Generator exit requirement) and **GAP-05** (Exit path) |
| **G2: Fuel Sufficiency** (Options 2C + 2D) | Decision 4 + Telemetry Safeguard | $E_{\text{fuel\_credit}} = \text{usable} \text{ if } \text{V}=\text{VALID} \land E \ge \text{Req} \text{ else } 0$ | `station_state.diesel_fuel_remaining_liters` | **Test I, K** | Impacts **GAP-04** (Missing forecast reliance on diesel) |
| **G3: Startup Semantics** (Options 3B + 3D) | Survivability Margin Math | $P(t) = 0 \text{ for } t < \Delta t_{\text{start}} \text{ else } P_{\text{cred}}(t)$ | N/A (Assumed $0.0$ in code) | **Test F, P, U** | Impacts **GAP-05** (Exit delay during generator start) |
| **G4: Unknown Health** (Option 4D) | Telemetry Safeguard (`UNKNOWN_INVALID != EMERGENCY`) | $\text{Health} = \text{UNKNOWN} \implies E_{\text{gen\_credit}} = 0.0\text{ kWh}$ | N/A (Missing field) | **Test L** | Impacts **GAP-04** (Fallback when telemetry fails) |
| **G5: Time-Varying Energy** (Option 5E) | Decision 2 (Preemptive Survivability) | $E_{\text{gen\_credible}} = \int_0^6 P_{\text{gen\_credible}}(t) dt$ | `gap19_highs_native.py` ($P_{\text{diesel}}(t)$) | **Test A, B, R, S, T** | Impacts **GAP-02** (Renewable derating integration) |
| **G6: Strict Validation** (Option 6E) | Telemetry Validation ($\text{V}_{\text{telemetry}}$) | $\text{V}_{\text{telemetry}} = \text{INVALID} \implies \text{Credit} = 0.0$ | `gap19_highs_native.py` (Line 41) | **Test L** | Locks safe-harbor dispatch; prevents false credit |

---

## 2. Detailed Mapping to Core Governance Rules

1. **Rule 1 (Immediate Emergency on Critical Shortfall)**: G1–G6 evaluate $M_{\text{surv}}$ for *preemptive* emergency detection. If actual $P_{\text{crit\_srv}} < P_{\text{crit\_req}}$, Rule 1 immediately triggers Emergency regardless of G1–G6 values.
2. **Rule 2 (Preemptive Emergency when $M_{\text{surv}} < 0$)**: G5 defines the generator contribution term $E_{\text{gen\_credible}}$ in $M_{\text{surv}} = E_{\text{batt}} + E_{\text{gen}} + E_{\text{ren}} - 69.60\text{ kWh}$. If G1, G2, G3, or G4 set generator credit to $0.0$, $M_{\text{surv}}$ drops, enabling preemptive Emergency entry if battery is low.
3. **Rule 3 (Reserve Deficit $\neq$ Emergency)**: G1–G6 determine generator credit during `RESERVE_DEFICIT` mode ($SOC < 37.83\%$). If $E_{\text{gen\_credible}} \ge 69.60\text{ kWh}$, $M_{\text{surv}} \ge 0$, holding system strictly in `RESERVE_DEFICIT` (Test B, D, R).
4. **Rule 4 (Resource Loss Assessment)**: G1 + G2 define how diesel generator loss or fuel loss is evaluated dynamically without arbitrary static thresholds.
5. **Rule 5 (Automatic Return with Operator Override)**: G1 + G2 specify the generator availability required before automatic return to `NORMAL` mode can clear Emergency.
