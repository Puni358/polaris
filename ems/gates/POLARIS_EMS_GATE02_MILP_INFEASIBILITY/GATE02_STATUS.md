# POLARIS GATE-02 — MILP INFEASIBILITY OPERATIONAL RESPONSE
## GATEWAY STATUS AND GOVERNANCE SUMMARY

```yaml
GATE_ID: GATE-02
SUBJECT: MILP_INFEASIBILITY_OPERATIONAL_RESPONSE
GATE02_HUMAN_DECISION: OPTION_C
CRITICAL_LOAD_RULE: HARD_NEVER_RELAX
NONCRITICAL_LOAD_CONSTRAINTS: GOVERNED_RELAXATION_ALLOWED
RELAXATION_HIERARCHY: DEFINED_ONLY_WHERE_GOVERNED
OPERATOR_NOTIFICATION: MANDATORY_ON_RELAXATION
STATE_ADVANCEMENT_RULE: DEFINED (STATE_ADVANCES = NO_BEFORE_VALID_DISPATCH)
PHYSICAL_FALLBACK: UNDEFINED
OPERATOR_AUTHORITY: UNDEFINED
ECD_RELATIONSHIP: DEFINED (NO_AUTOMATIC_ECD_RERUN)
RECOVERY_POLICY: GOVERNANCE_REQUIRED
GATE02_POLICY_STATUS: PARTIALLY_RESOLVED
GATE02_IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
SOURCE_MODIFICATIONS: 0
GATE02_STATUS: GOVERNANCE_DECISION_REQUIRED_UNTIL_RELAXATION_HIERARCHY_IS_SUFFICIENTLY_DEFINED
```

---

## 1. GATEWAY PURPOSE & AUTHORITATIVE HUMAN DECISION

This governance package addresses **POLARIS GATE-02 — MILP INFEASIBILITY OPERATIONAL RESPONSE**.

The project-owner / human governance decision is explicitly:
> **`MILP_INFEASIBILITY_OPERATIONAL_POLICY = OPTION_C_GOVERNED_CONSTRAINT_RELAXATION`**

### Authoritative Human Decision Principles
1. **Critical Load is Compulsory**: Critical load service is a **HARD constraint** that **MUST NEVER be relaxed**.
2. **Governed Relaxation of Non-Critical Load**: Flexible and non-critical loads may be constrained/shed only when required to restore mathematical feasibility under an explicit governed hierarchy.
3. **No Arbitrary Solver Relaxation**: The optimizer MUST NOT arbitrarily relax physical constraints.
4. **Mandatory Operator Notification**: Every occurrence of governed constraint relaxation MUST generate an operator-visible notification/event.
5. **Separation from Emergency & Unknown Invalid**: `MILP_INFEASIBLE` does NOT equal `EMERGENCY` or `UNKNOWN_INVALID`.
6. **No Un-Governed State Advancement**: No Digital Twin state advancement, fuel consumption, or battery SOC update occurs before a valid governed dispatch is obtained.

---

## 2. CURRENT GATEWAY STATUS

While Option C is the authorized operational response policy, Gate-02 status is recorded as:
```text
GATE02_STATUS = GOVERNANCE_DECISION_REQUIRED UNTIL RELAXATION HIERARCHY IS SUFFICIENTLY DEFINED
GATE02_IMPLEMENTATION_STATUS = NOT_IMPLEMENTED
SOURCE_MODIFICATIONS = 0
```
No code implementation of Option C is authorized until the numerical hierarchy, penalty weights, and solver interfaces pass formal engineering governance.
