# POLARIS GATE-02 — MILP INFEASIBILITY GOVERNANCE DECISION
## FORMAL HUMAN DECISION PACKAGE & SPECIFICATION CLOSURE

---

## 1. FORMAL GOVERNANCE RESOLUTION BLOCK

```text
GATE_ID =
    GATE-02

SUBJECT =
    MILP_INFEASIBILITY_OPERATIONAL_RESPONSE

CURRENT_SOFTWARE_BEHAVIOR =
    GOVERNED_DEGRADED_ZERO_DISPATCH_WITH_STATE_ADVANCEMENT

SELECTED_OPERATIONAL_OPTION =
    F

STATE_ADVANCEMENT_RULE =
    DEFINED

PHYSICAL_FALLBACK =
    UNDEFINED

OPERATOR_AUTHORITY =
    UNDEFINED

ECD_RELATIONSHIP =
    DEFINED

RECOVERY_POLICY =
    UNDEFINED

GATE02_STATUS =
    GOVERNANCE_DECISION_REQUIRED
```

---

## 2. RATIONALE & OPERATIONAL BOUNDARIES

### Rationale for Selecting Option F (REMAIN UNRESOLVED)
1. **Absence of Authorized Policy**: No formal operational policy exists governing constraint relaxation priorities (Option C), operator takeover protocols (Option E), or hardware fallback behavior (Option A).
2. **Rejection of Automatic Option D (Option D)**: Automatically invoking Option D on MILP infeasibility is governance-invalid. MILP infeasibility is a mathematical optimization status, not proof of a physical station emergency or ECD emergency state.
3. **Prevention of Un-Governed State Advancement**: Selecting Option F ensures that `MILP_INFEASIBILITY_STATE_ADVANCEMENT` remains strictly prohibited (`MUST_NOT_OCCUR`), preventing software blackout simulation and state drift.

---

## 3. SUMMARY OF DEFINED & FROZEN RULES

```text
+-------------------------------------------------------------------------------+
| RULE ID  | GOVERNANCE SPECIFICATION STATEMENT                                  |
+----------+--------------------------------------------------------------------+
| G02-R01  | MILP_INFEASIBILITY != UNKNOWN_INVALID                              |
| G02-R02  | MILP_INFEASIBILITY != EMERGENCY                                    |
| G02-R03  | MILP_INFEASIBILITY_STATE_ADVANCEMENT = MUST_NOT_OCCUR (NO)         |
| G02-R04  | NO_AUTOMATIC_OPTION_D_ROUTING = ENFORCED                           |
| G02-R05  | NO_AUTOMATIC_ECD_RERUN = ENFORCED                                  |
| G02-R06  | MILP_INFEASIBILITY_RUNTIME_INTERFACE = ENGINEERING_INTERFACE_BLOCKER|
+-------------------------------------------------------------------------------+
```

---

## 4. CONDITIONS REQUIRED FOR FUTURE RESOLUTION OF GATE-02

Before Gate-02 can be transitioned from `GOVERNANCE_DECISION_REQUIRED` to `RESOLVED`, operational governance must formally authorize:

1. **Physical Fallback Specification**: Define exact hardware dispatch behavior when automatic EMS optimization is unavailable.
2. **Constraint Relaxation Hierarchy (if Option C is chosen)**: Establish prioritized slack penalties, maximum allowable violations, and absolute critical-load protection bounds.
3. **Operator Transfer Interface (if Option E is chosen)**: Specify operator override API, control authority protocols, and manual recovery workflows.
4. **Implementation Authorization**: Grant explicit authorization to update `runner.py` to handle `OPTIMIZATION_INFEASIBLE` without un-governed state advancement.
