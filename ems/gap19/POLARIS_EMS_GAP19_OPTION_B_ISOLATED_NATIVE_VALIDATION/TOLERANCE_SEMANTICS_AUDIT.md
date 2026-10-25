# TOLERANCE SEMANTICS AUDIT

## Objective Tolerance Semantics Audit

This document details the audit of `abs_tolerance` and `rel_tolerance` fields in `HighsLinearObjective`.

---

## Technical Audit Findings

1. **Fields Exposed**: `abs_tolerance` (float) and `rel_tolerance` (float) are attributes of `HighsLinearObjective`.
2. **Default Values**: `abs_tolerance = 0.0`, `rel_tolerance = 0.0`.
3. **Semantics**: Tolerances allow lower-priority objectives to relax higher-priority objective optimality bounds by a specified absolute or relative amount:
   $$J_k(x) \le J_k^* + \text{abs\_tolerance}_k + \text{rel\_tolerance}_k \cdot |J_k^*|$$
4. **MILP Qualification**: In integer programming (MILP), tolerances must be specified carefully because discrete step sizes may make small continuous tolerances non-binding.

---

## Audit Verdict

```text
OBJECTIVE_TOLERANCE = QUALIFIED
```
Tolerance fields exist on `HighsLinearObjective` and are passed to C++, but discrete integer step sizes affect tolerance relaxation bounds.
