# POLARIS EMS GAP19 — NORMAL MPC DATA-BLOCKED BOUNDARY

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_DATA_BLOCKED_OPERATIONAL_ARCHITECTURE`  

---

## 1. Operational Scope of Normal MPC Under Data-Blocked Conditions

This document defines what normal MPC is allowed to execute and demonstrate while station-specific engineering inputs remain unavailable.

```text
NORMAL_MPC_ENGINEERING_DEMONSTRATION (ESTABLISHED)
        ≠
STATION_VALIDATED_NORMAL_OPERATION (NOT_ESTABLISHED)
        ≠
PRODUCTION_EMERGENCY_OPERATION (NOT_ESTABLISHED)
```

---

## 2. Legitimately Demonstrated Normal MPC Capabilities

The following capabilities have been empirically verified in the controlled synthetic engineering environment and may legitimately remain demonstrated:

1. **Forecast Refresh**: Regenerating fresh 24h point forecasts at the start of each cycle ($t \to t+1$).
2. **24-Hour Horizon Receding Control**: Solving a 24-step horizon and committing ONLY timestep $k=0$ to the simulator.
3. **Digital Twin State Continuity**: Consuming updated `StationState` from `DigitalTwinSimulator.step(...)` on cycle $N+1$.
4. **Option B Native HiGHS Optimization**: Executing native lexicographic multi-objective MILP via `highspy`.
5. **Lexicographic Priority Hierarchy ($J1 \succ J2 \succ J3 \succ J4$)**: Enforcing $J1$ critical reliability before $J2$ reserve shortfall, $J3$ fuel cost, and $J4$ curtailment within the synthetic fixture.
6. **Energy Balance & Physical Constraints**: Enforcing bus-bar power balance, battery charge/discharge bounds, and generator limits.
7. **Truth Firewall**: Ensuring the optimizer consumes strictly `StationState` and `ForecastBundle` without reading future ground truth.

---

## 3. Prohibited Operational Claims

Passing normal MPC tests in the controlled synthetic environment **MUST NOT** be used to claim:
* Real Nuolja station operational readiness or safety.
* Validated emergency reserve protection for actual station equipment.
* Proof of optimal real-world fuel savings.
