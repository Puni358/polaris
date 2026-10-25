# 365D POLARIS TREATMENT CONTROL STRATEGY SPECIFICATION

## Exact Controller Identity & Implementation
- **Component File**: `system/optimization/implementations/gap19_highs_native.py`
- **Class Name**: `GAP19HighsNativeOptimizer`
- **SHA256 Hash**: `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737`
- **Solver Identity**: Native HiGHS C++ MILP Solver via `highspy` Python bindings.
- **Formulation Structure**: Governed 408-variable (96 binary, 312 continuous), 312-constraint MILP model.
- **Objective Hierarchy**: Multi-objective lexicographic hierarchy:
  $$\min J = \omega_1 J_1 + \omega_2 J_2 + \omega_3 J_3 + \omega_4 J_4$$
  where $J_1$ is Critical Deficit (Wh), $J_2$ is Reserve Shortfall (Wh), $J_3$ is Diesel Fuel (L), and $J_4$ is Curtailment (Wh).
- **Execution Semantics**: Receding horizon MPC committing ONLY $k=0$ dispatch action to `DigitalTwinSimulator`.
