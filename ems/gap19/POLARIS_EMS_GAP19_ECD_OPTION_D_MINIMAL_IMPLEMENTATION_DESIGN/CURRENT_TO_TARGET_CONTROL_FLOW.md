# Current to Target Control Flow Mapping

## 1. Single MPC Cycle Control Flow Mapping

```text
State_k (StationState)
   │
   ├──> 1. ForecastEngine.predict(State_k, context) ──> ForecastBundle_k
   │
   ├──> 2. ECD Evaluation Core
   │       Inputs: AuthorizedHorizon(6.0h), critical_load, State_k.battery_soc_pct, fuel, battery_params, diesel_params
   │       Output: EmergencyAssessment_k
   │
   ├──> 3. EMSControlRouter.route(Assessment_k, bundle_k, State_k, configs)
   │       │
   │       ├── operating_mode == NORMAL:
   │       │   └── GAP19HighsNativeOptimizer.optimize(bundle_k, State_k, configs) ──> DispatchPlan_k (Option B)
   │       │
   │       ├── operating_mode == EMERGENCY:
   │       │   └── OptionDFallbackSolver.solve(Assessment_k, bundle_k, State_k, configs) ──> DispatchPlan_k (Option D)
   │       │
   │       └── operating_mode == UNKNOWN_INVALID:
   │           └── UNKNOWN_INVALID_ROUTE (Action NOT_ESTABLISHED; halts path without silent solver execution)
   │
   ├──> 4. Extract Timestep k=0 First Action Only from DispatchPlan_k
   │       (solar_used[0], battery_charge[0], battery_discharge[0], diesel_power[0])
   │
   └──> 5. DigitalTwinSimulator.step(State_k, DispatchPlan_k, next_actual) ──> State_{k+1}
```

---

## 2. Control Edge Mapping & Status

| Edge # | Source | Destination | Data Object | Existing Interface | Missing Interface | Design Status |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | `StationState_k` | `ForecastEngine` | `StationState` | `predict(state, context)` | None | `ESTABLISHED` |
| **E2** | `StationState_k` & `Config` | `ECD Core` | `StationState`, `ECDConfig` | `evaluate(...)` | Direct Parameter Passing | `PROPOSED_DESIGN` |
| **E3** | `ECD Core` | `EMSControlRouter` | `EmergencyAssessment` | New Function Call | `EMSControlRouter.route(...)` | `PROPOSED_DESIGN` |
| **E4a** | `EMSControlRouter` (NORMAL) | `Option B HiGHS` | `ForecastBundle`, `State_k` | `optimize(...)` | None | `ESTABLISHED` |
| **E4b** | `EMSControlRouter` (EMERGENCY) | `Option D Fallback` | `Assessment`, `Bundle`, `State` | New Function Call | `OptionDFallbackSolver.solve(...)` | `PROPOSED_DESIGN` |
| **E4c** | `EMSControlRouter` (INVALID) | Invalid Path Handler | `EmergencyAssessment` | None | `UNKNOWN_INVALID_ROUTE` | `NOT_ESTABLISHED` |
| **E5** | Optimizer / Option D | `DispatchPlan` | `DispatchPlan` | `DispatchPlan.__init__` | None (Reuse schema) | `ESTABLISHED` |
| **E6** | `DispatchPlan` ($k=0$) | `DigitalTwinSimulator` | `DispatchPlan`, `next_actual` | `step(state, plan, actual)` | None | `ESTABLISHED` |
