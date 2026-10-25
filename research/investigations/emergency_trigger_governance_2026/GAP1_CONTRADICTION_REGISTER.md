# POLARIS — GAP 1 CONTRADICTION REGISTER

## Executive Summary

This formal register audits potential mathematical, logical, and operational contradictions across provisional human decisions **G1 through G6** and the locked core governance decisions.

---

## Formal Contradiction Register

| Contradiction ID | Decision Pair / Area | Potential Contradiction | Evidence & Analysis | Severity | Human Decision Required? |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **CONTR-01** | **G2 (Fuel Uncertainty) vs. Telemetry Governance** | Does fuel telemetry failure ($\text{V}_{\text{fuel}} = \text{INVALID}$) trigger `EMERGENCY` or `UNKNOWN_INVALID`? | G2 specifies `UNKNOWN_INVALID != EMERGENCY`. Setting generator credit $= 0.0\text{ kWh}$ correctly leaves state evaluation to remaining verified resources. Zero contradiction if decoupled. | `LOW` | **NO** (Decoupled in Audit 4) |
| **CONTR-02** | **G3 (Startup Delay) vs. Codebase Implementation** | Current synthetic code assumes $\Delta t_{\text{startup}} = 0.0\text{ h}$ (instant startup). G3 requires validating non-zero startup delay. | `gap19_highs_native.py` permits instant unit commitment $u(t) \in \{0, 1\}$. Real polar generators require preheating. Discrepancy between synthetic model and real specification. | `MEDIUM` | **YES** (Define synthetic $\Delta t_{\text{start}}$ parameter) |
| **CONTR-03** | **G5 (Time-Varying Energy) vs. Constant 6h Power Assumption** | Preliminary spec used $E_{\text{gen}} = P_{\text{max}} \times 6.0\text{ h}$. G5 requires dynamic integral $E_{\text{gen}} = \int_0^6 P(t) dt$. | Draft spec used $600\text{ kWh}$ constant potential. G5 correctly replaces constant potential with dynamic integral. Specification inconsistency resolved by G5. | `RESOLVED` | **NO** (Resolved by G5) |
| **CONTR-04** | **G4 (Unknown Health) vs. G6 (Strict Validation)** | Does setting generator credit $= 0.0$ on unknown health force Emergency entry when battery is at $50\%$ SOC? | At $50\%\text{ SOC}$, battery deliverable energy is $55.20\text{ kWh}$. Required is $69.60\text{ kWh}$. Net margin $M_{\text{surv}} = 55.20 - 69.60 = -14.40\text{ kWh} < 0$. G4 + G6 WILL trigger Emergency at $50\%$ SOC if generator health is unknown and renewables $= 0$. | `HIGH` | **YES** (Human must accept or modify Option C fallback) |
| **CONTR-05** | **G1 (Dispatchable) vs. G3 (OFF Generator)** | Is an OFF generator ($u=0$) considered "dispatchable" under G1? | G1 requires generator to be "dispatchable" for safety credit. If OFF generator is classified as non-dispatchable, G3 startup credit is blocked. | `HIGH` | **YES** (Clarify definition of "dispatchable" for OFF assets) |
| **CONTR-06** | **G5 (Integral) vs. Critical Load Demand** | Does $E_{\text{gen\_credible}} = \int_0^6 P(t) dt$ credit unserved generator energy above $11.6\text{ kW}$? | A $100\text{ kW}$ generator produces $600\text{ kWh}$ in 6 hours. Critical load requires $69.6\text{ kWh}$. Unserved excess ($530.4\text{ kWh}$) cannot be stored. If un-capped, $M_{\text{surv}}$ is artificially inflated. | `HIGH` | **YES** (Confirm Model D demand capping rule) |
| **CONTR-07** | **G6 (Strict Validation) vs. Telemetry Freshness** | Specification requires "validated telemetry" but defines no numerical max age ($\Delta t_{\text{max}}$). | Without explicit $\Delta t_{\text{max}}$, code cannot determine whether 5-minute-old fuel telemetry is "valid" or "stale". | `MEDIUM` | **YES** (Assign numerical $\Delta t_{\text{max}}$ parameter) |

---

## Detailed Analysis of Critical Contradictions

### CONTR-04: High SOC Emergency Entry Under Unknown Generator Health
- **Scenario**: Battery is at $SOC = 50.0\%$ ($100.0\text{ kWh}$ stored / $55.20\text{ kWh}$ deliverable). Generator health telemetry drops ($\text{Health} = \text{UNKNOWN}$). Renewables $= 0.0\text{ kW}$.
- **Execution Path**:
  1. G6 sets Generator Safety Credit $= 0.0\text{ kWh}$ due to UNKNOWN health.
  2. G4 evaluates remaining verified resources: $M_{\text{surv}} = 55.20 + 0.0 + 0.0 - 69.60 = -14.40\text{ kWh} < 0$.
  3. Preemptive Emergency trigger fires, transitioning system to `EMERGENCY` mode and enforcing Option C load shedding.
- **Analysis**: This is mathematically consistent with Decision 2 ($M_{\text{surv}} < 0 \implies \text{EMERGENCY}$), but the human project owner must explicitly confirm whether triggering Emergency Mode at $50.0\%\text{ SOC}$ when generator telemetry drops is the intended policy.

### CONTR-05: Dispatchability Ambiguity for OFF Generators
- **Ambiguity**: G1 requires a generator to be "dispatchable" to receive safety credit. G3 allows an OFF generator to receive safety credit after startup delay $\Delta t_{\text{startup}}$.
- **Conflict**: If "dispatchable" is defined as *currently running and synchronized*, an OFF generator is NOT dispatchable, rendering G3 startup credit impossible.
- **Resolution**: "Dispatchable" must be formally defined to include *start-ready OFF units capable of automated remote start*.
