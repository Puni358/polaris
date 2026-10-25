# IMPLEMENTATION DEPENDENCY ORDER

## 1. PHASED IMPLEMENTATION DEPENDENCY BLUEPRINT (PHASE 0 THROUGH PHASE 7)

The audit constructed a strict dependency-ordered implementation roadmap for the coding agent.

```text
[PHASE 0: Additive Schemas] ──► [PHASE 1: Fixture Adapter] ──► [PHASE 2: ECD Runner Wiring]
                                                                        │
                                                                        ▼
[PHASE 5: Dispatch Reporting] ◄── [PHASE 4: Option D MILP] ◄── [PHASE 3: Policy Router]
             │
             ▼
[PHASE 6: Static Integration Tests] ──► [PHASE 7: GAP19 Solver Integration]
```

---

## 2. PHASE SPECIFICATIONS

### PHASE 0: Additive Schema Extensions
- **Prerequisites**: Governance authorization.
- **Files Affected**: `system/schemas/station_state.py`, `system/schemas/forecast_bundle.py`, `system/schemas/dispatch_plan.py`.
- **Delivers**: `fuel_remaining_liters`, `operating_mode`, `critical_demand` optional fields.

### PHASE 1: Synthetic Fixture Adapter
- **Prerequisites**: Phase 0.
- **Files Affected**: `system/adapters/synthetic_fixture_adapter.py`.
- **Delivers**: `SyntheticFixtureProvider` class parsing `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.csv`.

### PHASE 2: ECD Runtime Wiring
- **Prerequisites**: Phase 0, Phase 1.
- **Files Affected**: `system/runtime/runner.py`.
- **Delivers**: Invocation of `EmergencyConditionDetector.evaluate()` inside `runner.py` MPC loop.

### PHASE 3: Option D Policy Router & Mode Contract
- **Prerequisites**: Phase 2.
- **Files Affected**: `system/control/option_d_policy.py`.
- **Delivers**: `OptionDPolicyLayer` producing `ModeConstraintSet`.

### PHASE 4: Option D Constraint Model in MILP
- **Prerequisites**: Phase 3.
- **Files Affected**: `system/optimization/implementations/milp.py`.
- **Delivers**: Extended 19-variable MILP formulation with Option D linear constraints.

### PHASE 5: DispatchPlan Reporting & Simulator Update
- **Prerequisites**: Phase 4.
- **Files Affected**: `system/simulation/simulator.py`, `system/schemas/dispatch_plan.py`.
- **Delivers**: Diesel fuel decrementing in simulator and critical load reporting in `DispatchPlan`.

### PHASE 6: Controlled Static Integration Tests
- **Prerequisites**: Phase 5.
- **Files Affected**: `system/tests/test_option_d_integration.py`.
- **Delivers**: Test suite execution (TEST-A through TEST-M).

### PHASE 7: GAP19 Multi-Stage Solver Integration
- **Prerequisites**: Phase 6, GAP19 C++ solver package release.
- **Files Affected**: `system/optimization/implementations/gap19_solver.py`.
- **Delivers**: Native HiGHS multi-stage lexicographic optimization.
