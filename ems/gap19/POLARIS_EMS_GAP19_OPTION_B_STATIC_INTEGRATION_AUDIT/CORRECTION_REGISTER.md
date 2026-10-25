# Integration Gap & Correction Register

```text
INTEGRATION_GAP = Runner optimizer selection branch missing
SOURCE_FILE = system/runtime/runner.py
LINE = 75
CURRENT_BEHAVIOR = Defaults to LocalMILPEnergyOptimizer for non-rule_based
REQUIRED_CHANGE = Add elif self.optimizer_type in ["highs_native", "gap19_highs_native"]: self.optimizer = GAP19HighsNativeOptimizer()
AUTHORIZATION_STATUS = NOT_GRANTED
```
