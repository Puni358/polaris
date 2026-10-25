# Experiment Scope

- **Model Specification**: Frozen 409-variable / 313-constraint Canonical GAP19 Target MILP.
- **Option A**: Independent 4-stage sequential MILP reference (`highspy` sequential locks).
- **Option B**: Native HiGHS multi-objective optimizer (`system/optimization/implementations/gap19_highs_native.py`).
- **Operating Mode**: `NORMAL` mode.
- **Boundaries Preserved**: Zero production source files modified. Zero integrated EMS/MPC/Digital Twin execution.
