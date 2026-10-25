# MINIMUM IMPLEMENTATION BOUNDARY

## 1. PREREQUISITE IMPLEMENTATION BOUNDARY FOR CONTROLLED TEST AUTHORIZATION

Before any controlled runtime test (TEST-0, TEST-1, etc.) can be authorized, the following implementation work MUST be completed vs what can remain mocked.

### A. MUST IMPLEMENT (Implementation Blockers)
1. **`SyntheticFixtureProvider` / Adapter**: Ingests `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.csv`, filters by `scenario_id`, handles kW->W unit scaling, and exposes data interface for `runner.py`.
2. **`StationState` Additive Extension**: Add `fuel_remaining_liters: Optional[float] = None` and `operating_mode: Optional[str] = None` to `StationState`.
3. **`ForecastBundle` Additive Extension**: Add `critical_demand: Optional[TimeseriesForecast] = None` to `ForecastBundle`.
4. **ECD Runtime Wiring in `runner.py`**: Instantiate `EmergencyConditionDetector` and call `evaluate()` at each MPC iteration.
5. **Basic Policy Preprocessor / Router**: Intercept `EmergencyAssessment` from ECD and configure downstream optimizer mode.
6. **Digital Twin Fuel Decrement**: Update `DigitalTwinSimulator.step()` to decrement `fuel_remaining_liters` based on diesel power output.

---

### B. CAN REMAIN MOCKED (Not Blocking First Controlled Test)
1. **GAP19 Lexicographic Multi-Stage Solver**: First test can run with existing scalar HiGHS MILP solver using high penalty weights for critical unmet load.
2. **Operator Escalation UI / Hardware Alarms**: Operator notifications can be logged to runtime JSON report files.
3. **Complex State Recovery Machine**: MPC naturally re-evaluates state each timestep.

---

### C. ALREADY EXISTS (Fully Functional)
1. `EmergencyConditionDetector` core (`system/control/ecd.py`).
2. `LocalMILPEnergyOptimizer` HiGHS MILP core (`system/optimization/implementations/milp.py`).
3. `DigitalTwinSimulator` closed-loop state update simulator (`system/simulation/simulator.py`).
4. `EvaluationEngine` performance evaluator (`system/evaluation/evaluator.py`).
5. Truth firewall isolation in `runner.py`.

---

### D. NOT REQUIRED FOR FIRST CONTROLLED TEST
1. Live station telemetry connection.
2. Branch01 / Stage8.1 forecasting model retraining.
3. Real Nuolja physical site parameters.
