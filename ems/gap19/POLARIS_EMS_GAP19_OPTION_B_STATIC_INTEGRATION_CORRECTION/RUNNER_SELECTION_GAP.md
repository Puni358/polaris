# Runner Selection Gap & Governance Boundary

Inspection of `system/runtime/runner.py` confirms:
- `self.optimizer_type == "rule_based"` instantiates `LocalRuleBasedEnergyOptimizer()`
- Else defaults to `LocalMILPEnergyOptimizer()`
- Zero selection branch exists for `GAP19HighsNativeOptimizer`

```text
OPTION_B_CALL_PATH = DOES_NOT_EXIST
RUNNER_SELECTION_CHANGE_REQUIRED = YES
RUNNER_SELECTION_CHANGE_AUTHORIZED = NO
```

### Distinction Between Selection Path & Runtime Integration
Adding `"highs_native" -> GAP19HighsNativeOptimizer()` to `runner.py` will establish **ONLY** `OPTION_B_SELECTION_PATH = IMPLEMENTED`. It will **NOT** establish:
- ECD integration
- Option-D integration
- Critical-load policy integration
- Five-tier load integration
- Fuel-state integration
- Operator escalation
- Production deployment
