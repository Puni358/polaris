# POLARIS — GAP 1 (G1–G6) FINAL TRACEABILITY MATRIX

## Executive Overview

This traceability matrix maps the complete lineage of the **Authoritative GAP 1 Governance Decisions (G1–G6, G1.1, G1.2, G1.3-E, G1.4)** to **Formal Mathematical Equations**, **Codebase Locations**, **12 Edge Cases**, and **Governance Classification Categories**.

---

## 1. Complete Governance Traceability Matrix

| Decision ID | Human Policy Rule Summary | Formal Mathematical Expression | Codebase Location / Status | Validating Edge Cases | Classification |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **G1** | Availability requires operational + dispatchable + validated telemetry | $A_{\text{cred\_k}}(t) = \mathbb{I}(\text{V} \land \text{Op} \land \text{Disp})$ | `station_state.diesel_running` | **Case 1, 2** | `HUMAN POLICY` |
| **G2** | Sufficient fuel demonstrated; uncertainty $= 0.0\text{ kWh}$ credit | $E_{\text{fuel\_credit}} = \text{usable if } \text{V}=\text{VALID} \land \ge \text{Req} \text{ else } 0$ | `station_state.diesel_fuel_remaining_liters` | **Case 6** | `HUMAN POLICY` |
| **G3** | OFF generator counts ONLY after validated startup delay | $P(t) = 0 \text{ for } t < \Delta t_{\text{start}} \text{ else } P_{\text{cred}}(t)$ | N/A (Assumed $0.0$ in code) | **Case 4, 5** | `HUMAN POLICY` |
| **G4** | Unknown health $= 0.0\text{ kWh}$ credit; evaluate remaining resources | $\text{Health} = \text{UNKNOWN} \implies E_{\text{gen}} = 0.0\text{ kWh}$ | N/A (Missing field) | **Case 7, 8, 9** | `HUMAN POLICY` |
| **G5** | Time-varying power integral over 6 hours | $E_{\text{gen\_credible\_raw}} = \int_0^6 P_{\text{gen\_credible}}(t) dt$ | `gap19_highs_native.py` ($P_{\text{diesel}}(t)$) | **Case 1, 4, 10** | `HUMAN POLICY` |
| **G1.1** | Cap generator credit at net critical energy demand | $E_{\text{gen}} = \min(\int P dt, \, \max(0, 69.60 - E_{\text{batt}}))$ | `ecd.py` (Proposed Spec) | **Case 1** | `HUMAN POLICY` |
| **G1.2** | Dispatchable includes OFF generator ONLY with start-readiness | $\text{Disp}_{\text{OFF}} = \mathbb{I}(\text{StartReady} = \text{VALID})$ | N/A (Missing field) | **Case 4, 5** | `HUMAN POLICY` |
| **G1.3-E**| No universal numerical threshold; resource-specific research | $\text{FreshnessEligible}(\text{resource, measurement, } t, \text{ctx})$ | `EMERGENCY_TRIGGER_GOVERNANCE_RESEARCH.md` | **Case 1, 3, 8, 11, 12** | `HUMAN POLICY` |
| **G1.4** | Telemetry loss + $M_{\text{surv}} < 0 \implies \text{EMERGENCY}$ | $\text{V} = \text{INVALID} \land M_{\text{surv}} < 0 \implies \text{EMERGENCY}$ | `ecd.py` (Proposed Spec) | **Case 8, 9** | `HUMAN POLICY` |
| **G6** | Strict evidence threshold; missing evidence $= 0.0\text{ kWh}$ | $\text{Evidence} = \text{INVALID} \implies E_{\text{gen}} = 0.0\text{ kWh}$ | `gap19_highs_native.py` (Line 41) | **Case 2, 3, 5, 6, 7, 11** | `HUMAN POLICY` |

---

## 2. Traceability to Reconciled Survivability Equation

Every decision maps into the Critical Load Survivability Margin ($M_{\text{surv}}$):

$$M_{\text{surv}}(t) = E_{\text{batt\_deliverable}}(t) + E_{\text{gen\_credible\_total}}(t) + E_{\text{ren\_credible\_total}}(t) - 69.60\text{ kWh}$$

1. **G1, G1.2, G3, G4, G6** dictate whether $P_{\text{gen\_credible}}(t) > 0$. If any evidence check fails, $P_{\text{gen\_credible}}(t) = 0.0$.
2. **G2** dictates whether fuel depletion caps the time integral $\int_0^t \text{BSFC}(P) d\tau \le V_{\text{fuel}}$.
3. **G5** defines the continuous time integral $\int_0^{6} P_{\text{gen\_credible}}(t) dt$.
4. **G1.1** caps the resulting integral at $\max(0, 69.60 - E_{\text{batt\_deliverable}})$.
5. **G1.3-E** establishes that telemetry freshness must be evaluated via resource-specific rules rather than an arbitrary universal number.
6. **G1.4** directs system state determination based on the resulting $M_{\text{surv}}$ value.
