# CONTROLLED TEST SEQUENCE

## 1. RECOMMENDED FUTURE RUNTIME TEST SEQUENCE

The audit defines the smallest safe sequence of runtime tests to execute **ONLY AFTER** the prerequisite implementation boundary is cleared.

```text
[TEST-0: Static Data & Contract Validation]
                     │
                     ▼
[TEST-1: Single Scenario Execution (SC-01 NORMAL)]
                     │
                     ▼
[TEST-2: All 5 Scenarios Execution (SC-01 .. SC-05)]
                     │
                     ▼
[TEST-3: 24h Closed-Loop Receding Horizon MPC Demonstration]
```

---

## 2. DETAILED TEST SPECIFICATIONS

### TEST-0: Static Data Contract & Interface Test
- **Scope**: Single timestep static instantiation.
- **Objective**: Verify that `SyntheticFixtureProvider` successfully parses `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.csv`, constructs `StationState`, `ForecastBundle`, and `ECD` inputs without throwing schema or unit errors.
- **Duration**: Static 1-step call (zero simulation).

### TEST-1: Single Scenario Static Integration Test (SC-01)
- **Scope**: SC-01 (`NORMAL_OPERATION`), 24 timesteps.
- **Objective**: Verify end-to-end pipeline execution from Data Provider → StationState → ForecastEngine → ForecastBundle → ECD → Optimizer → DispatchPlan → Digital Twin.
- **Verification**: Verify zero crashes, energy balance closure, and ECD classification = `NORMAL`.

### TEST-2: Multi-Scenario Stress Test (SC-01 to SC-05)
- **Scope**: All 5 scenarios (120 timesteps).
- **Objective**: Verify that ECD correctly classifies `NORMAL` (SC-01), `EMERGENCY` (SC-02, SC-03, SC-04), and `UNKNOWN_INVALID` (SC-05), and that the runner handles all failure modes cleanly.

### TEST-3: 24h Closed-Loop Demonstration
- **Scope**: 24-step receding-horizon MPC simulation across SC-01 and SC-02.
- **Objective**: Verify closed-loop state transitions, fuel decrementing, battery SOC tracking, and truth firewall survival over 24 simulation hours.

---

## 3. EXECUTION DIRECTIVE
- **DO NOT EXECUTE NOW**.
- This sequence is defined for future test authorization after code interface gaps are closed.
