# POLARIS — EMERGENCY TRIGGER RESERVE DEFICIT SEMANTICS

## Executive Governance Definition

This artifact provides the formal, binding definition of **RESERVE DEFICIT / RECOVERY STATE SEMANTICS** for POLARIS Energy Management System governance.

---

## 1. Binding Reserve Deficit Definition

```yaml
STATE_NAME: RESERVE_DEFICIT
GOVERNANCE_STATUS: BINDING_GOVERNANCE_RULE
PRIMARY_CONDITION: SOC < 37.83% (E_batt_stored < 75.652 kWh) AND M_surv >= 0 AND P_crit_srv == 11.6 kW
EMERGENCY_STATUS: STRICTLY_NOT_AN_EMERGENCY
LOAD_SHEDDING_PERMITTED: FALSE
AUTOMATIC_OPTIMIZATION_PERMITTED: TRUE (With reserve recovery objective penalty)
```

### Formal Statement
> "A reserve deficit ($SOC < 37.83\%$) does **NOT** mean the battery can independently sustain six hours of critical load. It **ONLY** means the microgrid is operating below its normal-mode stored-energy reserve target while the complete resource-adequacy assessment ($M_{\text{surv}} \ge 0$) still indicates sufficient critical-load survivability."

---

## 2. Distinction Between Target Deficit and Survivability Failure

```
+-----------------------------------------------------------------------------------+
|                        RESERVE TARGET DEFICIT (S2)                                |
| - State of Charge: SOC < 37.83% (E_batt_stored < 75.652 kWh)                      |
| - Net Resource Margin: M_surv >= 0.0 kWh (Generator/Renewables cover gap)         |
| - Critical Load: 100% Served (11.6 kW)                                            |
| - Operational Action: Economic dispatch active; replenishment prioritized when    |
|   excess generation exists.                                                       |
| - GOVERNANCE: LOAD SHEDDING PROHIBITED. NOT AN EMERGENCY.                         |
+-----------------------------------------------------------------------------------+
                                          VS
+-----------------------------------------------------------------------------------+
|                     SURVIVABILITY FAILURE (S3 EMERGENCY)                          |
| - State of Charge: Any SOC (e.g. SOC < 37.83% or SOC = 50.0%)                     |
| - Net Resource Margin: M_surv < 0.0 kWh (Generation insufficient to cover gap)    |
| - Critical Load: Served right now, but cannot be sustained for 6 hours            |
| - Operational Action: Activate Option C governed load shedding hierarchy.        |
| - GOVERNANCE: EMERGENCY MODE ACTIVE.                                              |
+-----------------------------------------------------------------------------------+
```

---

## 3. Mapping Across Governance Artifacts

This definition is consistently embedded across all POLARIS governance documents:

| Artifact Name | Governance Mapping | Core Requirement Enforced |
| :--- | :--- | :--- |
| [`EMERGENCY_STATE_MACHINE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/investigations/emergency_trigger_governance_2026/EMERGENCY_STATE_MACHINE.md) | State `S2: RESERVE_DEFICIT` | Transition $T_{12}$ occurs at $SOC < 37.83\%$; requires $M_{\text{surv}} \ge 0$. |
| [`EMERGENCY_TRIGGER_IMPLEMENTATION_SPEC.md`](file:///home/punith-bs/01polaris%20%28Copy%29/investigations/emergency_trigger_governance_2026/EMERGENCY_TRIGGER_IMPLEMENTATION_SPEC.md) | Section 3 Trigger Logic | Reserve check occurs *after* verifying $M_{\text{surv}} \ge 0$. |
| [`EMERGENCY_TRIGGER_GOVERNANCE_DECISION_RECORD.md`](file:///home/punith-bs/01polaris%20%28Copy%29/investigations/emergency_trigger_governance_2026/EMERGENCY_TRIGGER_GOVERNANCE_DECISION_RECORD.md) | Approved Decision 3 | $37.83\%\text{ SOC}$ ($75.65\text{ kWh}$) is a target, never an emergency floor. |
| [`EMERGENCY_TRIGGER_CORRECTED_TEST_PLAN.md`](file:///home/punith-bs/01polaris%20%28Copy%29/investigations/emergency_trigger_governance_2026/EMERGENCY_TRIGGER_CORRECTED_TEST_PLAN.md) | Test Cases B, D, R | Explicitly test low SOC with active generation ($M_{\text{surv}} \ge 0 \implies \text{RESERVE\_DEFICIT}$). |
| `EMERGENCY_TRIGGER_IMPLEMENTATION_SPEC.json` | `governance_decisions` | Machine-readable rule `reserve_deficit_alone_never_triggers_emergency: true`. |

---

## 4. Implementation Safeguards

To prevent future software engineers from accidentally implementing naive `SOC < 37.83% => Emergency` logic, the following code comment header MUST be placed in `ecd.py` when implementation is authorized:

```python
# ==============================================================================
# POLARIS GOVERNANCE MANDATE: RESERVE DEFICIT SEMANTICS
# ------------------------------------------------------------------------------
# SOC < 37.83% (75.65 kWh) is a NORMAL-MODE RESERVE TARGET, NOT AN EMERGENCY FLOOR.
# Under NO circumstance shall SOC < 37.83% alone trigger EMERGENCY mode.
# EMERGENCY mode requires either:
#   1. Validated P_critical_served < P_critical_required (Hard Failure), OR
#   2. M_surv < 0.0 kWh (Resource-Adequacy Survivability Failure).
# ==============================================================================
```
