# REPRODUCIBILITY REQUIREMENTS

## Mandatory Execution Logging Parameters for 100% Reproducible Solves

This document establishes the mandatory reproducibility logging specification for future Option B executions.

---

## Mandatory Execution Capture Register

For every future Option B optimization call, the runtime system MUST record:

1. `python_version`: Python runtime version string.
2. `highspy_version`: `highspy` PyPI package version (`1.15.1`).
3. `highs_engine_version`: Underlying HiGHS C++ engine version (`1.15.1`).
4. `solver_options`: Complete dictionary of active solver options (`blend_multi_objectives: False`, `threads: 1`, `mip_rel_tolerance: 1e-4`).
5. `objective_definitions`: Priority index, weight, and coefficients for $J_1, J_2, J_3, J_4$.
6. `model_hash`: SHA-256 hash of matrix $A$, vector $b$, bounds $lb, ub$.
7. `result_hash`: SHA-256 hash of returned decision vector $x^*$.
8. `solver_status`: HiGHS model status string (`HighsModelStatus.kOptimal`).
