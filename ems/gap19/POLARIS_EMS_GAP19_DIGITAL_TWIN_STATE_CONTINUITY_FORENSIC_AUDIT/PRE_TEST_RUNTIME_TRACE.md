# Pre-Test Runtime Trace (`PRE_TEST_RUNTIME_TRACE.md`)

**GATE CONTEXT**: POLARIS EMS GAP19 — Digital Twin State-Continuity Forensic Review  
**VERDICT**: `PASS`

---

## 1. Control Flow & Dataflow Architecture

Tracing [`system/runtime/runner.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/runtime/runner.py#L90-L204):

```python
# Initial Station State at t=0
first_step = self.data_provider.timesteps[0]
initial_state = StationState(
    timestamp=first_step["timestamp"],
    battery_soc_pct=self.configs.get("battery", {}).get("initial_soc_pct", 50.0), # (Overridden by scenario fixture to 80.0%)
    battery_energy_wh=...,
    diesel_running=False,
    diesel_hours_running=0.0,
    ...
)

current_state = initial_state

for step_idx in range(max_steps):
    # Step 1: Observable runtime state
    runtime_context = self.data_provider.get_runtime_state(step_idx)

    # Step 2: ForecastEngine predicts 24h horizon
    bundle = self.forecast_engine.predict(current_state, runtime_context)

    # Step 3: EnergyOptimizer optimizes 24h dispatch
    plan = self.optimizer.optimize(bundle, current_state, self.configs)

    # Step 4: Hidden ground truth for simulation
    future_actuals = self.data_provider.get_future_ground_truth(step_idx, horizon_hours=24)
    next_actual = future_actuals[0]

    # Step 5: Step simulator with step 1 dispatch decision
    current_state = self.simulator.step(current_state, plan, next_actual)
```

---

## 2. Key Dataflow Identifiers

1. **State Initialization ($t=0$)**: `current_state` begins at `2024-01-01T20:00:00Z` with $E_0 = 160,000$ Wh ($\text{SOC}_0 = 80.0\%$), `diesel_running = False`, `diesel_hours_running = 0.0`.
2. **First Action Isolation**: `self.simulator.step(current_state, plan, next_actual)` extracts `plan.battery_charge[0]`, `plan.battery_discharge[0]`, `plan.diesel_power[0]`.
3. **In-Loop Reassignment**: `current_state = self.simulator.step(...)` rebinds the local variable `current_state` to the newly instantiated `StationState` object returned by `DigitalTwinSimulator.step`.
4. **Subsequent Cycle Consumption**: In `step_idx + 1`, `current_state` is supplied to `predict()` and `optimize()`. No state reconstruction, cloning from fixture, or reset takes place.
