# D4 HUMAN DECISION RECORD

## IMMUTABLE GOVERNANCE RECORD

```text
DATE: 2026-09-24
DECISION_ID: DEC-004-D4
DECISION_NAME: CRITICAL_LOAD_ALLOCATION_UNDER_INSUFFICIENT_POWER
DECISION_STATUS: HUMAN_SELECTED_AND_SEALED

HUMAN_DECISION:
1. WHEN SUFFICIENT POWER EXISTS:
   Maintain each protected critical system at or above its engineering-defined
   minimum viable operating level whenever physically feasible.

2. WHEN AVAILABLE POWER IS INSUFFICIENT TO SATISFY ALL PROTECTED CRITICAL MINIMUMS:
   Proportionally allocate the available protected-critical power according to each
   protected critical system's minimum viable requirement (P_i,min).

ALLOCATION_BASIS: PROPORTIONAL_TO_MINIMUM_VIABLE_CRITICAL_REQUIREMENTS
MATHEMATICAL_FORMULA: P_i,served(t) = alpha(t) * P_i,min(t), where alpha(t) = P_crit,avail(t) / sum_k(P_k,min(t))

RATIONALE_SUMMARY:
Preserves the Option D intent of keeping all protected critical systems operating
as far as physically possible without assigning an unauthorized priority among
protected categories. Using minimum viable requirements (P_i,min) focuses scarce
emergency power on preserving minimum viable operation rather than proportionally
distributing normal requested demand.

ALTERNATIVE_NOT_SELECTED: PROPORTIONAL_TO_REQUESTED_DEMAND (REJECTED)
CATEGORY_PRIORITY: NONE (No category receives an authorized priority over another)

SYNTHETIC_VALUES: FIXTURE_ONLY (15 kW / 10 kW / 5 kW are synthetic fixture values only)
PRODUCTION_STATUS: NOT_ESTABLISHED (Real Nuolja critical-load values require engineering inputs)
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
IMPLEMENTATION_AUTHORIZATION: NOT_GRANTED
EXECUTION_STATUS: NOT_EXECUTED
```
