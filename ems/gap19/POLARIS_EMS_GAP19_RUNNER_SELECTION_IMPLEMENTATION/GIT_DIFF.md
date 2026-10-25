# Git Diff Output for `system/runtime/runner.py`

```diff
@@ -15,2 +15,3 @@
 from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
+from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
 
@@ -75,2 +76,4 @@
         if self.optimizer_type == "rule_based":
             self.optimizer = LocalRuleBasedEnergyOptimizer()
+        elif self.optimizer_type in ("highs_native", "gap19_highs_native"):
+            self.optimizer = GAP19HighsNativeOptimizer()
```
