# Next-Gate Definition (`NEXT_GATE_DEFINITION.md`)

**GATE IDENTIFICATION CONTEXT**: POLARIS EMS GAP19 — Post-24H Baseline Next-Gate Identification  
**VERDICT**: `PASS`

---

## Formal Next-Gate Specification

```text
NEXT_GATE_ID = GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST

NEXT_GATE_NAME = Multi-Scenario Closed-Loop Stress Validation for Option B Native HiGHS

CURRENT_PRECONDITION =
    1. GAP19_OPTION_B_24H_MPC_BASELINE_TEST is CLOSED (24/24 cycles OPTIMAL, zero fallbacks).
    2. Option B Native HiGHS implementation COMPLETE and verified.
    3. Governed J2 maximum envelope formulation CLOSED.
    4. EBR 6-hour lookahead index semantics CONFIRMED ([t_now+1h, t_now+6h]).
    5. 24-cycle Digital Twin state continuity and energy accounting PASSED.
    6. Protected source files frozen and verified.

PURPOSE =
    To evaluate whether GAP19 Option B native HiGHS multi-objective rolling MPC dispatch maintains solver feasibility (zero fallbacks), physical state continuity, and reserve compliance under four distinct synthetic stress scenarios:
    1. Normal Baseline (normal_demo)
    2. Renewable Stress (renewable_stress — zero/low solar generation)
    3. Demand Stress (demand_stress — high peak load demand)
    4. Battery Stress (battery_stress — restricted SOC bounds & capacity)

CLAIMS_TO_ESTABLISH =
    1. Option B native HiGHS solver executes 24 consecutive MPC cycles cleanly across all 4 scenarios (4 x 24 = 96 total steps).
    2. Zero solver fallbacks to legacy MILP or rule-based optimizers across all 4 stress scenarios.
    3. Zero solver retries or solver infeasibilities across all 4 stress scenarios.
    4. Physical battery SOC remains strictly within configured operational bounds [20.0%, 95.0%] across all 4 scenarios.
    5. EBR survivability reserve and terminal reserve constraints remain satisfied without J2 shortfall in stress conditions.

INPUT_ARTIFACTS =
    - system/data/scenarios/demo_scenario.json
    - system/data/scenarios/renewable_stress_scenario.json
    - system/data/scenarios/demand_stress_scenario.json
    - system/data/scenarios/battery_stress_scenario.json
    - system/config/*.yaml

RUNTIME_COMPONENTS_INVOLVED =
    - PolarisLocalRunner (run_multi_scenario_suite)
    - LocalBaselineForecastEngine
    - GAP19HighsNativeOptimizer
    - DigitalTwinSimulator
    - LocalDataProvider

COMPONENTS_EXCLUDED =
    - EmergencyConditionDetector (ECD)
    - Decision Support / Option D Architecture
    - Stage 8.1 Solar Forecast Engine (s81_solar.py)
    - 168-hour endurance suite

TEST_OR_AUDIT_TYPE = Controlled Closed-Loop Multi-Scenario 24-Step MPC Integration Experiment

EXECUTION_AUTHORIZATION_REQUIRED = YES (Requires explicit human authorization to run)

GOVERNANCE_DEPENDENCIES = None (Uses governed J2 parameters: T_REQUIRED=6h, terminal reserve envelope)

ENGINEERING_DEPENDENCIES = GAP19_OPTION_B_24H_MPC_BASELINE_TEST CLOSED (Satisfied)

SUCCESS_CRITERIA =
    - execution_status == "SUCCESS_CLEAN" across all 4 scenarios
    - 96 / 96 total MPC steps completed cleanly
    - 4 scenario result JSONs / reports generated with continuous state transitions
    - J1 (unmet load) == 0.0 across all 96 cycles
    - J2 (reserve shortfall) == 0.0 across all 96 cycles

FAILURE_CRITERIA =
    - OPTIMIZATION_INFEASIBLE reported in any of the 96 cycles
    - FAILED_STATE_VIOLATION raised by DigitalTwinSimulator in any scenario
    - Solver fallback or retry triggered in any scenario

HARD_STOP_CONDITIONS =
    - Immediate halt if HiGHS solver fails to converge on any scenario cycle
    - Immediate halt if physical state boundaries are breached

REQUIRED_ARTIFACTS =
    POLARIS_EMS_GAP19_CONTROLLED_MULTI_SCENARIO_STRESS_TEST/
    - README.md
    - NORMAL_DEMO_RESULT.json
    - RENEWABLE_STRESS_RESULT.json
    - DEMAND_STRESS_RESULT.json
    - BATTERY_STRESS_RESULT.json
    - MULTI_SCENARIO_EVALUATION_REPORT.json
    - HASH_AUDIT.json

SEALING_CRITERIA = Independent forensic audit of multi-scenario dispatch performance, energy balance, and state continuity.
```
