# Option B Source Implementation Trace

- **Module Path:** `system/optimization/implementations/gap19_highs_native.py`
- **Class:** `GAP19HighsNativeOptimizer`
- **Inheritance:** `from system.optimization.interface.base import EnergyOptimizer`
- **Method Signature:** `optimize(self, forecast_bundle: ForecastBundle, station_state: StationState, config: Dict[str, Any]) -> DispatchPlan`
- **Internal Model Dimensions:** N = 409 Variables (96 Binary, 313 Continuous), M = 313 Linear Constraints.
- **Solver Backend:** Native `highspy.Highs()` with `blend_multi_objectives = False`.
- **Objectives & Priorities:**
  - J1 (Critical Deficit Wh): priority = 4, weight = 1.0, abs_tolerance = 0.0, rel_tolerance = 0.0
  - J2 (Reserve Shortfall Wh): priority = 3, weight = 1.0, abs_tolerance = 0.0, rel_tolerance = 0.0
  - J3 (Diesel Fuel Liters): priority = 2, weight = 1.0, abs_tolerance = 0.0, rel_tolerance = 0.0
  - J4 (Curtailment Wh): priority = 1, weight = 1.0, abs_tolerance = 0.0, rel_tolerance = 0.0
