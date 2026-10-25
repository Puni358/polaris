# 365D DETERMINISTIC REPRODUCIBILITY PLAN & ENVIRONMENT SPECIFICATION

## Stack & Environment Inventory
- **OS**: Linux x86_64
- **Python**: 3.10+
- **Key Libraries**: NumPy 1.24+, SciPy 1.10+, PyYAML 6.0+, highspy 1.5+
- **Mode**: 100% Offline Local PC Execution (`DISCONNECTED`).
- **Determinism**: Zero stochastic random seeds. Physics and HiGHS MILP equations are 100% deterministic. Repeated runs produce bitwise identical dispatch, state, and fuel results.
