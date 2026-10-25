# Runtime Horizon & Dataflow Trace

## 1. Architectural Code Trace: `PolarisLocalRunner`

The active execution loop for POLARIS local system orchestration is implemented in:
`system/runtime/runner.py` (`PolarisLocalRunner.run_pipeline`).

### 1.1 Receding Horizon Execution Loop (`runner.py` lines 116–264)

```python
for step_idx in range(max_steps):
    # 1. Fetch observable historical runtime context (STRICTLY Causal)
    runtime_context = self.data_provider.get_runtime_state(step_idx)

    # 2. ForecastEngine predicts 24h horizon relative to current_state.timestamp
    bundle = self.forecast_engine.predict(current_state, runtime_context)

    # 3. EnergyOptimizer optimizes 24h dispatch horizon (H=24)
    plan = self.optimizer.optimize(bundle, current_state, self.configs)

    # 4. Extract hidden future actual observation for the FIRST step only (simulation truth)
    future_actuals = self.data_provider.get_future_ground_truth(step_idx, horizon_hours=24)
    next_actual = future_actuals[0]

    # 5. Step DigitalTwinSimulator using STEP 1 DISPATCH DECISION ONLY
    current_state = self.simulator.step(current_state, plan, next_actual)
```

---

## 2. Answers to Specific Runtime Questions

### Question 3: What timestamps are supplied to `EnergyOptimizer.optimize()`?
- **Finding**: The `EnergyOptimizer.optimize()` method receives two primary data structures:
  1. `station_state`: Contains `station_state.timestamp` representing the current observation origin time $t_{\text{now}}$ (e.g., `"2024-01-01T00:00:00Z"`).
  2. `forecast_bundle`: Contains `forecast_bundle.timestamps`, which is a list of exactly 24 ISO-8601 strings covering hours $t_{\text{now}} + 1\text{h}$ through $t_{\text{now}} + 24\text{h}$.
- **Code Reference**: `system/optimization/implementations/milp.py` (lines 67-70):
  ```python
  timestamps = forecast_bundle.timestamps  # Exactly 24 entries
  demand = forecast_bundle.demand.point     # Exactly 24 entries
  ```

### Question 4: What timestamps are supplied to the MPC/runner at each cycle?
- **Finding**: At cycle `step_idx`, `PolarisLocalRunner` supplies `current_state.timestamp` to the forecast engine and optimizer.
- **Trace across timesteps**:
  - `step_idx = 0`: $t_{\text{now}} = \text{"2024-01-01T00:00:00Z"}$. Forecast covers `01:00` to `24:00` (Jan 2 00:00).
  - `step_idx = 1`: $t_{\text{now}} = \text{"2024-01-01T01:00:00Z"}$. Forecast covers `02:00` to Jan 2 `01:00`.
  - `step_idx = 18`: $t_{\text{now}} = \text{"2024-01-01T18:00:00Z"}$. Forecast covers `19:00` to Jan 2 `18:00`.
  - `step_idx = 23`: $t_{\text{now}} = \text{"2024-01-01T23:00:00Z"}$. Forecast covers Jan 2 `00:00` to Jan 2 `23:00`.

### Question 5: Does `PolarisLocalRunner` advance the current state and timestamp after each control interval?
- **Finding**: `YES. ABSOLUTELY.`
- **Code Reference**: `system/runtime/runner.py` (line 199) and `system/simulation/simulator.py`:
  ```python
  current_state = self.simulator.step(current_state, plan, next_actual)
  ```
- After step `step_idx`, `DigitalTwinSimulator.step()`:
  1. Reads `plan.battery_charge[0]`, `plan.battery_discharge[0]`, `plan.diesel_power[0]`.
  2. Applies efficiency losses and physical dynamics to compute $E_{\text{bat}}[t+1]$ and new SOC.
  3. Updates `current_state.timestamp` to `next_actual["timestamp"]` (which is $t_{\text{now}} + 1\text{h}$).
  4. Advances the simulation state to the next control interval.

---

## 3. Summary Verdict

The `PolarisLocalRunner` strictly implements a **Receding Horizon Model Predictive Control (MPC)** loop:
- **Optimization Horizon**: 24 hours ($H = 24$).
- **Control Execution Interval**: 1 hour (step 0 only).
- **State Advancement & Re-Observation**: 1 hour.
- **Re-Forecasting Frequency**: Every 1 hour.
