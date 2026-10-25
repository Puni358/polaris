# Minimal Runtime Implementation Boundary Specification

## Minimal Adapter Architecture for Integration

To enable controlled synthetic ECD $\to$ Option D integration in `runner.py`, the following minimal software components are required:

1. **`EMSControlRouter` (`system/control/router.py`)**:
   - Encapsulates `EmergencyConditionDetector`.
   - Accepts `StationState`, `ForecastBundle`, and `configs`.
   - Evaluates `EmergencyAssessment`.
   - Directs execution to `OptionB` (HiGHS native MILP) or `OptionD` (Fallback heuristic/solver).

2. **`OptionDFallbackSolver` (`system/optimization/implementations/option_d.py`)**:
   - Implements 24h dispatch plan generator for EMERGENCY mode.
   - Enforces Option D priority hierarchy (Protected Critical Load first, renewable direct, diesel support, battery emergency rules).

3. **`PolarisLocalRunner` Integration (`system/runtime/runner.py`)**:
   - Insert `EMSControlRouter` call between `ForecastEngine.predict()` and `optimizer.optimize()`.

---

## Protected Source Files (Must Remain Untouched)
- `system/optimization/implementations/gap19_highs_native.py` (Option B Native HiGHS solver)
- `system/optimization/implementations/milp.py`
- `system/simulation/simulator.py` (Digital Twin)
- `system/control/ecd.py` (ECD Core)

## Verdict
The runtime implementation boundary is clean, decoupled, and strictly additive.
