# OPTION B NATIVE RUN REPORT

## NATIVE HIGHS LEXICOGRAPHIC MULTI-OBJECTIVE MILP

Option B was executed using `highspy==1.15.1` with native multi-objective linear objectives added via `HighsLinearObjective`:

- **HiGHS Version**: 1.15.1
- **Solver Options**: `output_flag=False`, `threads=1`
- **Objective Priority Mapping**:
  - $J_1$: `priority = 1`, `weight = 1.0`, `abs_tolerance = 0.0`, `rel_tolerance = 0.0`
  - $J_2$: `priority = 2`, `weight = 1.0`, `abs_tolerance = 0.0`, `rel_tolerance = 0.0`
  - $J_3$: `priority = 3`, `weight = 1.0`, `abs_tolerance = 0.0`, `rel_tolerance = 0.0`
  - $J_4$: `priority = 4`, `weight = 1.0`, `abs_tolerance = 0.0`, `rel_tolerance = 0.0`
- **Model Termination Status**: `HighsModelStatus.kOptimal`
- **Returned Recalculated Objectives**:
  - $J_{1,B} = 0.00000000$
  - $J_{2,B} = 0.00000000$
  - $J_{3,B} = -0.00000000$
  - $J_{4,B} = -0.00000000$

Option B produced a fully feasible solution $x_B$ with maximum constraint residual $6.6613381478e-12$.
