# POLARIS EMS GAP19 — Implementation Change Manifest

## File Change Summary

### Modified Allowed Files
1. [`system/simulation/simulator.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py)
   - **Type**: Modified (Narrow line refinement)
   - **Description**: Explicitly separated fuel variables into `available_fuel`, `required_fuel`, and `next_fuel = max(0.0, available_fuel - required_fuel)` for committed first action $k=0$ (`dispatch_plan.diesel_power[0]`) ONLY.

### Created Allowed Files
2. [`system/control/router.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/router.py)
   - **Type**: New File
   - **Description**: `EMSControlRouter` pure policy router wrapping ECD evaluator. Passes current fuel into ECD and routes NORMAL → Option B, EMERGENCY → Option D, UNKNOWN_INVALID → Blocked.

3. [`system/optimization/implementations/option_d.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/option_d.py)
   - **Type**: New File
   - **Description**: `OptionDFallbackSolver` emergency heuristic solver satisfying DEC-004 / D1–D6 governance.

4. [`tests/test_gap19_ecd_option_d.py`](file:///home/punith-bs/01polaris%20%28Copy%29/tests/test_gap19_ecd_option_d.py)
   - **Type**: New File
   - **Description**: Unit test suite covering authorized items A through R (18 tests).

5. [`tests/test_isolated_components.py`](file:///home/punith-bs/01polaris%20%28Copy%29/tests/test_isolated_components.py)
   - **Type**: New File
   - **Description**: Isolated synthetic component tests (4 tests).

### Protected Baseline Files (0 Modifications)
- `system/control/ecd.py` (UNTOUCHED)
- `system/optimization/implementations/gap19_highs_native.py` (UNTOUCHED)
- `system/optimization/implementations/milp.py` (UNTOUCHED)
- `system/schemas/station_state.py` (UNTOUCHED)
- `system/runtime/runner.py` (UNTOUCHED)
