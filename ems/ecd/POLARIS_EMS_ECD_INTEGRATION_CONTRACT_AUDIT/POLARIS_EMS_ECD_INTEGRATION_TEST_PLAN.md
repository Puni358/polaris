# POLARIS EMS — ECD INTEGRATION TEST PLAN

## 1. Executive Summary

This document specifies the 5-layer integration test plan for verifying the Emergency Condition Detector (ECD) integration into POLARIS EMS.

---

## 2. Five-Layer Testing Architecture

```
Layer 1: Isolated ECD Core Unit Tests ───────────────► [ALREADY PASSED - 7/7 PASS]
Layer 2: Schema / Interface Integration Tests ───────► [NOT EXECUTED - DESIGNED]
Layer 3: ECD + MPC Context Integration Tests ───────► [NOT EXECUTED - DESIGNED]
Layer 4: ECD + Optimizer Behavior Tests ─────────────► [NOT EXECUTED - DESIGNED]
Layer 5: Full Closed-Loop EMS Endurance Tests ──────► [NOT EXECUTED - DESIGNED]
```

---

## 3. Layer Specifications

### Layer 1: Isolated ECD Core Unit Tests
- **Status**: **PASSED** (`system/tests/test_ecd_core.py`, 7/7 tests passed in 0.08s).
- **Scope**: Canonical 5-case fixture, boundary states, fail-closed handling, tie epsilon, time-varying trajectory integration, 100-iteration determinism.

### Layer 2: Schema / Interface Integration Tests
- **Scope**: Verify `ForecastBundle` and `StationState` additive schema adapters feed `EmergencyConditionDetector` without breaking legacy code.

### Layer 3: ECD + MPC Context Integration Tests
- **Scope**: Verify `PolarisLocalRunner` invokes ECD once per timestep $k$ and attaches `EmergencyAssessment` to `DispatchPlan` metadata.

### Layer 4: ECD + Optimizer Behavior Tests
- **Scope**: Verify EMS Mode Manager correctly routes `EMERGENCY` operating mode to appropriate optimizer objective function.

### Layer 5: Full Closed-Loop EMS Endurance Tests
- **Scope**: 24h and 168h receding horizon MPC simulations verifying zero regressions on baseline cost metrics under `NORMAL` mode.

---

## 4. Regression Protection

- **Baseline Preserved**: When `operating_mode == NORMAL`, existing MILP optimizer dispatch, objective values, and simulator trajectories MUST be 100% identical to pre-integration benchmarks.

Status: `COMPLETE`
