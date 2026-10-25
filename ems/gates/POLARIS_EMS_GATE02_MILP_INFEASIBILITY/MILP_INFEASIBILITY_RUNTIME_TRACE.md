# POLARIS GATE-02 — MILP INFEASIBILITY RUNTIME TRACE
## FORENSIC TRACE OF MILP INFEASIBILITY EXECUTION PATH

---

## 1. RUNTIME EXECUTION PATH

The runtime path of the POLARIS EMS from input forecasting to state advancement is traced below:

```text
ForecastBundle
    ↓
StationState
    ↓
EnergyOptimizer / Option B (gap19_highs_native.py)
    ↓
HiGHS Solver (highspy.Highs.solve())
    ↓
solver status evaluation (model_status != kOptimal)
    ↓
DispatchPlan generation (dummy zero-dispatch plan)
    ↓
PolarisLocalRunner.run_pipeline() (runner.py)
    ↓
FaultEvent logging (GOVERNED_DEGRADED / GOVERNED_ZERO_DISPATCH)
    ↓
DigitalTwinSimulator.step(action_k0) [Pre-existing behavior]
    ↓
next StationState
```

---

## 2. DETAILED STEP-BY-STEP FORENSIC ANALYSIS

### Step 1: Input Assembly & Optimizer Invocation
- `ForecastBundle` and current `StationState` are provided to `EnergyOptimizer.optimize_dispatch()` in `system/optimization/implementations/gap19_highs_native.py`.

### Step 2: Solver Execution & Status Detection
- The HiGHS native C++ wrapper is invoked.
- If the optimizer cannot satisfy all hard constraints (e.g. power balance, battery C-rate, generator bounds, min up/down time, terminal SOC reserve), HiGHS returns a model status such as `kInfeasible`, `kUnboundedOrInfeasible`, or `kModelError`.
- In `gap19_highs_native.py` (lines 391–403), status detection occurs immediately after `highs.solve()`:
  ```python
  if model_status != highspy.HighsModelStatus.kOptimal:
      return DispatchPlan(
          timestamp=current_state.timestamp,
          horizon_hours=24,
          diesel_power=[0.0] * 24,
          battery_charge=[0.0] * 24,
          battery_discharge=[0.0] * 24,
          load_served=[0.0] * 24,
          unmet_load=demand_forecast,
          objective_value=1e9,
          constraint_status=f"OPTIMIZATION_INFEASIBLE: {model_status}",
          solver_wall_time_ms=wall_time,
      )
  ```

### Step 3: DispatchPlan Construction on Infeasibility
- Rather than throwing an exception or returning `None`, `gap19_highs_native.py` constructs a synthetic `DispatchPlan`.
- `constraint_status` is explicitly set to `"OPTIMIZATION_INFEASIBLE: <HighsModelStatus>"` (e.g. `"OPTIMIZATION_INFEASIBLE: HighsModelStatus.kInfeasible"`).
- `objective_value` is set to `1e9`.
- All control vectors (`diesel_power`, `battery_charge`, `battery_discharge`, `load_served`) are populated with `0.0` for all 24 horizon hours.
- `unmet_load` is set equal to the full `demand_forecast`.

### Step 4: Runner Infeasibility Handling (runner.py)
- `PolarisLocalRunner.run_pipeline()` receives the `DispatchPlan`.
- Lines 184–195 inspect `plan.constraint_status`:
  ```python
  if plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"):
      fault_event = FaultEvent(
          timestamp=current_state.timestamp,
          fault_class="OPTIMIZATION_INFEASIBLE",
          severity="GOVERNED_DEGRADED",
          response="GOVERNED_ZERO_DISPATCH",
          state_advanced=True,
      )
  ```
- A `FaultEvent` is instantiated with `severity="GOVERNED_DEGRADED"` and `response="GOVERNED_ZERO_DISPATCH"`.

### Step 5: Pre-Existing State Advancement vs. Frozen Policy Boundary
- **Pre-existing Code Behavior**: In `runner.py`, `state_advanced` is set to `True`. The runner extracts `action_k0` (`diesel_power[0]=0.0`, `battery_power[0]=0.0`) and calls `DigitalTwinSimulator.step(action_k0)`. The simulator advances the state by 1 timestep with zero generation, dropping load and applying self-discharge to the battery. The runner loop then continues to the next cycle.
- **Frozen Policy Boundary**:
  ```text
  MILP_INFEASIBILITY_STATE_ADVANCEMENT = MUST_NOT_OCCUR
  MILP_INFEASIBILITY_OPERATIONAL_RESPONSE = NOT_IMPLEMENTED
  MILP_INFEASIBILITY_RUNTIME_INTERFACE = ENGINEERING_INTERFACE_BLOCKER
  ```
- **Conflict**: The pre-existing runner behavior (`state_advanced=True`, zero dispatch commitment) violates the frozen policy boundary (`MUST_NOT_OCCUR`).

---

## 3. IDENTIFICATION OF SPECIFIC RUNTIME METRICS

| Metric / Action | Observed Runtime Behavior |
| :--- | :--- |
| **Solver Status Representation** | `f"OPTIMIZATION_INFEASIBLE: {model_status}"` string in `plan.constraint_status`. |
| **Detection Location** | `gap19_highs_native.py` line 391 (post-solve check) and `runner.py` line 184. |
| **DispatchPlan Produced?** | **YES** — A placeholder plan with 0.0 dispatch vectors and `objective_value = 1e9`. |
| **First Action Committed?** | **Pre-existing**: YES (`diesel_power=0.0`, `battery_power=0.0`). **Frozen Policy**: NO. |
| **Fuel Consumed?** | **NO** — Zero diesel generation yields 0.0 liters fuel burn. |
| **Battery SOC Changed?** | **Pre-existing**: Small decrease via simulator self-discharge model. **Frozen Policy**: NO. |
| **Digital Twin Advanced?** | **Pre-existing**: YES. **Frozen Policy**: NO (`MUST_NOT_OCCUR`). |
| **Execution Status Changed?** | Recorded `FaultEvent(severity="GOVERNED_DEGRADED")`. |
| **FaultEvent Generated?** | **YES** — `fault_class="OPTIMIZATION_INFEASIBLE"`. |
| **Loop Execution Continues?** | **Pre-existing**: YES (runner proceeds to next step). **Frozen Policy**: NO (blocked). |
| **Runner Retries?** | **NO** — No retry loop exists in `runner.py`. |
| **Fallback Optimizer Called?** | **NO** — Neither Option D nor any alternative solver is invoked. |
| **Option D Called?** | **NO** — Option D is not triggered by `OPTIMIZATION_INFEASIBLE`. |
| **ECD Called Again?** | **NO** — ECD is evaluated once per cycle prior to optimization; not re-invoked. |
| **System Terminates?** | **NO** — Unlike `UNKNOWN_INVALID` (which raises `CRITICAL_TERMINATION`), `OPTIMIZATION_INFEASIBLE` in pre-existing code does NOT break the loop or terminate process execution. |
