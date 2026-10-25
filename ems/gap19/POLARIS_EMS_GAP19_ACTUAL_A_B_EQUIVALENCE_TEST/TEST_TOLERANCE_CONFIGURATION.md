# TEST TOLERANCE CONFIGURATION

## TEST-ONLY NUMERICAL COMPARISON PARAMETERS

> [!IMPORTANT]
> The tolerances listed below are **TEST_CONFIGURATION_ONLY** parameters used exclusively in this validation experiment harness. They are NOT promoted into POLARIS production governance.

- **Option A Explicit Lock Tolerances**:
  - `TEST_EPSILON_1` ($J_1$ lock): $1.0 \times 10^{-7}$
  - `TEST_EPSILON_2` ($J_2$ lock): $1.0 \times 10^{-7}$
  - `TEST_EPSILON_3` ($J_3$ lock): $1.0 \times 10^{-7}$
- **Option B Solver Tolerances**:
  - `abs_tolerance` ($J_{1..4}$): $0.0$
  - `rel_tolerance` ($J_{1..4}$): $0.0$
- **Equivalence Comparison Thresholds**:
  - Objective Equivalence Threshold: $1.0 \times 10^{-6}$
  - Decision Vector Equivalence Threshold: $1.0 \times 10^{-6}$
  - Constraint Residual Feasibility Threshold: $1.0 \times 10^{-6}$
