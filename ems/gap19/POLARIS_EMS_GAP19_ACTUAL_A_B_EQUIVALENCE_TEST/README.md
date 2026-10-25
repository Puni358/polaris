# POLARIS EMS GAP19 — ACTUAL OPTION A vs OPTION B EQUIVALENCE TEST PACKAGE

## EXECUTIVE SUMMARY

This validation experiment package establishes the empirical mathematical equivalence between Option A (`SEQUENTIAL_LEXICOGRAPHIC_MILP_WITH_EXPLICIT_LOCKS`) and Option B (`NATIVE_HIGHS_LEXICOGRAPHIC_MULTI_OBJECTIVE_MILP`) for the POLARIS EMS GAP19 solver architecture.

Human governance has selected:
```text
GAP19_SOLVER_ARCHITECTURE = OPTION_B
```

Option A was retained as the independent mathematical reference implementation. This experiment was conducted in full accordance with the absolute safety boundary: zero production code was modified, zero dependencies were changed in POLARIS, and `OPTION_B_IMPLEMENTATION_AUTHORIZATION` remains `NOT_GRANTED`.

## EXPERIMENTAL VERDICT SUMMARY

```text
GAP19_ACTUAL_A_B_TEST_STATUS = PASS
FROZEN_MODEL_VALID = YES
MODEL_IDENTITY_A_B = PASS
FEASIBLE_REGION_IDENTITY = PASS
OBJECTIVE_IDENTITY = PASS
PRIORITY_IDENTITY = PASS
LEXICOGRAPHIC_BEHAVIOR = PASS
J1_EQUIVALENCE = PASS
J2_EQUIVALENCE = PASS
J3_EQUIVALENCE = PASS
J4_EQUIVALENCE = PASS
CONSTRAINT_FEASIBILITY = PASS
DECISION_VECTOR_RESULT = MATCH
OBJECTIVE_VECTOR_RESULT = EQUIVALENT
REPRODUCIBILITY = PASS
ACTUAL_POLARIS_A_B_EQUIVALENCE = ESTABLISHED
OPTION_B_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
PRODUCTION_EXECUTION = NOT_AUTHORIZED
```

## KEY EMPIRICAL FINDINGS

- **Model Dimensions**: 385 variables (265 continuous, 120 binary), 265 linear constraints, $H=24\text{h}$ horizon.
- **Canonical Model Hash**: `9c740dc5de2a0cf28e17748dd12466e7f5ca00e733b93cfb34b148c60cfc779c`
- **Objective Equivalence**:
  - $\Delta J_1 = |J_{1,A} - J_{1,B}| = 0.0000000000e+00$ (PASS)
  - $\Delta J_2 = |J_{2,A} - J_{2,B}| = 0.0000000000e+00$ (PASS)
  - $\Delta J_3 = |J_{3,A} - J_{3,B}| = 5.6843418861e-17$ (PASS)
  - $\Delta J_4 = |J_{4,A} - J_{4,B}| = 9.0949470177e-13$ (PASS)
- **Decision Vector Comparison**: Max elementwise difference $\max |x_A - x_B| = 1.8189894035e-12 \le 10^{-6}$ (`MATCH`).
- **Constraint Feasibility**: Max constraint residual across all 265 constraints: Option A = $9.0949470177e-13$, Option B = $6.6613381478e-12$ (`PASS`).
- **Process Replay**: Deterministic multi-process replay confirmed ($0.0$ variance across independent executions).

## PACKAGE CONTENTS

1. `README.md` - Overview and executive summary.
2. `MODEL_SOURCE_AUDIT.md` - Source mapping to POLARIS equations.
3. `FROZEN_MODEL_SPEC.md` - Detailed mathematical specification of frozen model.
4. `FROZEN_MODEL_HASH.json` - JSON canonical representation and hash.
5. `VARIABLE_AUDIT.md` - Audit of all 385 variables.
6. `BOUND_AUDIT.md` - Lower and upper bounds audit.
7. `INTEGRALITY_AUDIT.md` - Integrality classification of variables.
8. `CONSTRAINT_AUDIT.md` - Audit of 265 physical constraints.
9. `OBJECTIVE_VECTOR_AUDIT.md` - Comparison of objective coefficient vectors $c_1, c_2, c_3, c_4$.
10. `J1_REFERENCE.md` - Critical load reliability objective reference.
11. `J2_REFERENCE.md` - Emergency battery reserve objective reference.
12. `J3_REFERENCE.md` - Diesel fuel consumption objective reference.
13. `J4_REFERENCE.md` - Renewable curtailment objective reference.
14. `TEST_TOLERANCE_CONFIGURATION.md` - Numerical comparison thresholds ($\epsilon_{1..3} = 10^{-7}$).
15. `OPTION_A_REFERENCE_RUN.md` - Details of 4-pass sequential SciPy solve.
16. `OPTION_A_LOCK_FORENSICS.md` - Lock constraint satisfaction analysis for Option A.
17. `OPTION_B_NATIVE_RUN.md` - Details of native `highspy` multi-objective solve.
18. `OPTION_B_PRIORITY_FORENSICS.md` - HiGHS priority and tolerance configuration forensics.
19. `MODEL_IDENTITY_AUDIT.md` - Verification that Model A identity equals Model B identity.
20. `OBJECTIVE_COMPARISON.md` - Comparative analysis of $[J_{1..4,A}]$ vs $[J_{1..4,B}]$.
21. `DECISION_VECTOR_COMPARISON.md` - Elementwise $x_A$ vs $x_B$ evaluation.
22. `DISPATCH_COMPARISON.md` - Physical energy dispatch comparison (diesel, battery, renewables).
23. `CONSTRAINT_FORENSICS.md` - Residual violation analysis for all 265 constraints.
24. `PRIMAL_DEGENERACY_ANALYSIS.md` - Degeneracy analysis.
25. `REPRODUCIBILITY_AUDIT.md` - Threading and environment reproducibility audit.
26. `FRESH_PROCESS_REPLAY.md` - Fresh process replay results.
27. `PERFORMANCE_OBSERVATION.md` - Non-claim runtime observations.
28. `SCIENTIFIC_CLAIM_BOUNDARY.md` - Strict boundaries of scientific claims.
29. `EQUIVALENCE_VERDICT.md` - Official mathematical verdict and authorization status.
30. `HASH_AUDIT.json` - Complete manifest of artifact checksums.
