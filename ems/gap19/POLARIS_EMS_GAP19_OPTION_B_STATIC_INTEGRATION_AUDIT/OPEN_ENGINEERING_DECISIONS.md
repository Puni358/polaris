# Open Engineering Decisions

1. **Runner Optimizer Selection Branch:** Add `elif self.optimizer_type in ["highs_native", "gap19_highs_native"]:` to `PolarisLocalRunner.__init__`.
2. **ECD Runner Wiring:** Wire `system/control/ecd.py` into `PolarisLocalRunner` step 2.5 prior to optimizer invocation.
