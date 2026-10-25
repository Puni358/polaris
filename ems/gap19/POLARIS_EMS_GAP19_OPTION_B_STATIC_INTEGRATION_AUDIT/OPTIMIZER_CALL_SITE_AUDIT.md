# Optimizer Call-Site Audit

- **Callers Traced:**
  1. `PolarisLocalRunner` (`system/runtime/runner.py`): Lines 75-78 instantiate `LocalRuleBasedEnergyOptimizer()` or `LocalMILPEnergyOptimizer()`.
  2. `D5Runner` (`system/robustness/orchestrator.py`): Instantiates `LocalMILPEnergyOptimizer()`.
  3. Test suites (`system/tests/`): Instantiate `LocalMILPEnergyOptimizer()`.

- **Finding:** No caller currently instantiates `GAP19HighsNativeOptimizer()`.
- **Classification:** `OPTION_B_CALL_PATH = DOES_NOT_EXIST`.
