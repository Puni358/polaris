# Runner Selection Implementation Diff Detail

The following changes were applied to `system/runtime/runner.py`:

```diff
--- system/runtime/runner.py
+++ system/runtime/runner.py
@@ -13,6 +13,7 @@
 from system.forecasting.implementations.s81_solar import Stage81ForecastEngine
 from system.optimization.implementations.rule_based import LocalRuleBasedEnergyOptimizer
 from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
+from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
 from system.simulation.simulator import DigitalTwinSimulator
 from system.evaluation.evaluator import EvaluationEngine
 
@@ -73,6 +73,8 @@
         self.optimizer_type = optimizer_type.lower()
         if self.optimizer_type == "rule_based":
             self.optimizer = LocalRuleBasedEnergyOptimizer()
+        elif self.optimizer_type in ("highs_native", "gap19_highs_native"):
+            self.optimizer = GAP19HighsNativeOptimizer()
         else:
             self.optimizer = LocalMILPEnergyOptimizer()
```
