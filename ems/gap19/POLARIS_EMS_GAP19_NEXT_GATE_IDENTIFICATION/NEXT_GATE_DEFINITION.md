# Next-Gate Definition (`NEXT_GATE_DEFINITION.md`)

**GATE IDENTIFICATION CONTEXT**: POLARIS EMS GAP19 — Next-Gate Identification  
**VERDICT**: `PASS`

---

## Formal Next-Gate Specification

```text
NEXT_GATE_ID = GAP19_OPTION_B_24H_MPC_BASELINE_TEST

NEXT_GATE_NAME = Full 24-Hour Diurnal Rolling MPC Integration Test for Option B Native HiGHS

CURRENT_PRECONDITION =
    1. Option B Native HiGHS implementation COMPLETE and verified in single-cycle unit tests.
    2. Governed J2 maximum envelope formulation CLOSED.
    3. EBR 6-hour lookahead index semantics CONFIRMED ([t_now+1h, t_now+6h]).
    4. Controlled 8-cycle Digital Twin state continuity review PASSED.
    5. Protected source files frozen and verified.

PURPOSE =
    To evaluate whether GAP19 Option B native HiGHS multi-objective rolling MPC dispatch maintains physical state continuity, feasible dispatch trajectories, and reserve stability across a full 24-hour diurnal solar cycle (24 timesteps) under closed-loop DigitalTwinSimulator coupling.

CLAIMS_TO_ESTABLISH =
    1. Option B native HiGHS solver executes 24 consecutive MPC cycles cleanly (completed_steps = 24).
    2. Diurnal solar transition (daylight generation vs nocturnal zero-solar) is handled with ZERO solver infeasibilities or solver crashes.
    3. Battery SOC remains within configured bounds [20.0%, 95.0%] across the entire 24-hour simulation.
    4. EBR survivability reserve and terminal reserve constraints remain satisfied (j2_objective == 0.0) across all 24 cycles.
    5. In-loop state propagation operates continuously for 24 steps without state reset or memory leakage.

INPUT_ARTIFACTS =
    - system/data/scenarios/demo_scenario.json (24-hour baseline scenario)
    - system/config/*.yaml (station, battery, diesel, solar_pv, loads, optimizer)

RUNTIME_COMPONENTS_INVOLVED =
    - PolarisLocalRunner
    - LocalBaselineForecastEngine
    - GAP19HighsNativeOptimizer
    - DigitalTwinSimulator
    - LocalDataProvider

COMPONENTS_EXCLUDED =
    - EmergencyConditionDetector (ECD)
    - Decision Support / Option D Architecture
    - Stage 8.1 Solar Forecast Engine (s81_solar.py)
    - Multi-scenario stress suite
    - 168-hour endurance suite

TEST_OR_AUDIT_TYPE = Controlled Closed-Loop 24-Step MPC Integration Experiment

EXECUTION_AUTHORIZATION_REQUIRED = YES (Requires explicit human authorization to run)

GOVERNANCE_DEPENDENCIES = None (Uses governed J2 parameters: T_REQUIRED=6h, terminal reserve envelope)

ENGINEERING_DEPENDENCIES = 8-cycle state-continuity review CLOSED (Satisfied)

SUCCESS_CRITERIA =
    - execution_status == "SUCCESS_CLEAN"
    - completed_steps == 24
    - 24 result JSON files generated with continuous timestamps and state transitions
    - J1 (unmet load) == 0.0 across all 24 cycles
    - J2 (reserve shortfall) == 0.0 across all 24 cycles

FAILURE_CRITERIA =
    - execution_status == "FAILED_TERMINATED"
    - OPTIMIZATION_INFEASIBLE reported in any of the 24 cycles
    - FAILED_STATE_VIOLATION raised by DigitalTwinSimulator
    - Discontinuity or state reset in battery energy or diesel runtime hours

HARD_STOP_CONDITIONS =
    - Immediate halt if HiGHS solver fails to converge on any cycle
    - Immediate halt if state boundary [20%, 95%] is breached

REQUIRED_ARTIFACTS =
    POLARIS_EMS_GAP19_CONTROLLED_24_CYCLE_MPC_TEST/
    - README.md
    - CYCLE_01_RESULT.json ... CYCLE_24_RESULT.json
    - RUN_REPORT.json
    - HASH_AUDIT.json

SEALING_CRITERIA = Independent forensic state-continuity and energy-accounting audit of the 24-cycle output artifacts.
```
