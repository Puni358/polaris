# REFERENCE EQUIVALENCE TEST SPECIFICATION

## Test Specification for Future Reference Equivalence Audit

This document defines the formal test design for verifying native Option B against Option A reference implementation prior to production promotion.

---

## Test Design Specification

```text
FUTURE_EQUIVALENCE_TEST = DEFINED
```

### Test Procedure (To Be Executed Post-Implementation Authorization):
1. Construct the canonical POLARIS 24-hour horizon MILP model.
2. Execute **Option A Reference Pass**:
   - Solve 4 sequential passes using SciPy `milp()`.
   - Record decision vector $x_A$, objective vector $[J_{1,A}, J_{2,A}, J_{3,A}, J_{4,A}]$, and physical dispatch setpoints.
3. Execute **Option B Native Pass**:
   - Register 4 `HighsLinearObjective` structures in `highspy`. Set `blend_multi_objectives = False`.
   - Solve native multi-objective MILP.
   - Record decision vector $x_B$, objective vector $[J_{1,B}, J_{2,B}, J_{3,B}, J_{4,B}]$, and physical dispatch setpoints.
4. Evaluate Equivalence Criteria across decision vectors, objective vectors, and dispatch setpoints.
