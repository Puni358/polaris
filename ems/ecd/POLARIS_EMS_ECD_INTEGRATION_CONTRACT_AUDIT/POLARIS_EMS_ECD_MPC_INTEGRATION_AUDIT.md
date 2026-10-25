# POLARIS EMS — ECD MPC INTEGRATION AUDIT

## 1. Executive Summary

This document audits the integration sequence of the Emergency Condition Detector (ECD) into the POLARIS receding horizon Model Predictive Control (MPC) loop.

---

## 2. Receding Horizon MPC Execution Sequence

The audited control flow sequence for each timestep $k$ within `PolarisLocalRunner.run_pipeline()` is defined as follows:

```
[Start Timestep k]
       │
       ▼
1. Observable Runtime State ──► StationState(t_k)
       │
       ▼
2. ForecastEngine.predict() ──► ForecastBundle(24h)
       │
       ▼
3. Construct CriticalLoadTrajectory ──► CriticalLoadTrajectory
       │
       ▼
4. ECD Evaluation ────────────► EmergencyConditionDetector.evaluate()
                                       │
                                       ▼
                             EmergencyAssessment
                                       │
                                       ▼
5. EMS Policy / Mode Manager ─► Configures NORMAL / EMERGENCY Mode
                                       │
                                       ▼
6. EnergyOptimizer.optimize() ─► DispatchPlan
       │
       ▼
7. DigitalTwinSimulator.step() ─► StationState(t_{k+1})
       │
       ▼
[Advance to Timestep k+1]
```

---

## 3. Required Control-Flow Integration Table

| Step | Existing Component | ECD Interaction | Required Change |
|------|--------------------|-----------------|-----------------|
| 1. State Observation | `LocalDataProvider` / SCADA | Provides SOC, fuel level, temperatures to `StationState` | None (Expose fuel if present) |
| 2. Forecast Generation | `ForecastEngine` | Generates solar/wind/demand forecast & critical demand | Pass `critical_demand_w` in `ForecastBundle` |
| 3. Critical Load Construction | Integration Adapter | Wraps `critical_demand_w` into `CriticalLoadTrajectory` | Add wrapper call |
| 4. ECD Evaluation | `EmergencyConditionDetector` | Evaluates $T_{\text{battery}}$, $T_{\text{diesel}}$, margins, and mode | Add `ecd.evaluate()` call |
| 5. Operating Mode Handling | EMS Mode Manager (NEW) | Selects optimizer objective/constraints based on `EmergencyAssessment` | Add Policy Router before optimizer |
| 6. Optimization | `EnergyOptimizer` | Solves dispatch for selected mode | Pass operating mode context to optimizer |
| 7. Dispatch Execution | `DigitalTwinSimulator` | Executes step 1 dispatch actions | None |
| 8. State Update | Simulator / Telemetry | Updates state for timestep $k+1$ | None |

---

## 4. Execution Frequency

- **Architecture-Supported Frequency**: **Once per MPC cycle** (every 1-hour or 5-minute timestep).
- **Rationale**: Survivability margins change as SOC, fuel levels, and load forecasts evolve. Evaluating ECD at every MPC step guarantees real-time emergency detection without operational lag.

Status: `ESTABLISHED`
