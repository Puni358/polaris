# Pre-Test Digital Twin Trace Audit (`PRE_TEST_DIGITAL_TWIN_TRACE.md`)

**GATE CONTEXT**: POLARIS EMS GAP19 — Controlled Digital-Twin 8-Cycle MPC Integration Test  
**AUTHORITATIVE TARGET**: `system/simulation/simulator.py` (`DigitalTwinSimulator`)  
**AUDIT DATE**: 2026-09-25  
**PRE-TEST VERDICT**: `PASS`

---

## 1. Overview & Objectives

Before executing the controlled 8-cycle simulation loop, a read-only source-code inspection of `DigitalTwinSimulator` was performed to verify its interface contracts, state propagation equations, and truth firewall boundaries.

---

## 2. Source-Level Class Inspection (`DigitalTwinSimulator`)

### 2.1 Constructor (`__init__`)
- **Signature**: `DigitalTwinSimulator(config: Dict[str, Any])`
- **Config Parameters Extracted**:
  - `capacity_wh`: $200,000.0\text{ Wh}$ (default)
  - `min_soc_pct`: $20.0\%$ (default)
  - `max_soc_pct`: $95.0\%$ (default)
  - `charge_efficiency` ($\eta_{\text{ch}}$): $0.92$ (default)
  - `discharge_efficiency` ($\eta_{\text{dis}}$): $0.92$ (default)
- **Derived Boundary Limits**:
  - `min_e_wh`: $40,000.0\text{ Wh}$
  - `max_e_wh`: $190,000.0\text{ Wh}$

### 2.2 Execution Method (`step`)
- **Signature**: `step(self, current_state: StationState, dispatch_plan: DispatchPlan, actuals_next_step: Dict[str, Any]) -> StationState`
- **Inputs**:
  1. `current_state`: `StationState` object representing physical state at observation origin $t_n$.
  2. `dispatch_plan`: `DispatchPlan` output from `GAP19HighsNativeOptimizer`.
  3. `actuals_next_step`: `Dict[str, Any]` containing ground-truth actuals for step $t_{n} \to t_{n+1}$ (`actual_SW_IN`, `actual_demand`, `actual_wind_generation`, `timestamp`).

---

## 3. Physical State Transition Mechanics

### 3.1 First-Action Extraction
```python
p_chg = dispatch_plan.battery_charge[0]
p_dis = dispatch_plan.battery_discharge[0]
p_diesel = dispatch_plan.diesel_power[0]
```
The simulator extracts and commits **ONLY** timestep index 0 of the 24-hour horizon plan. Timesteps $1 \dots 23$ are ignored by the simulator.

### 3.2 Battery Energy & SOC Governing Equations
```python
curr_e_wh = current_state.battery_energy_wh
curr_e_wh += (p_chg * self.eta_chg - (p_dis / self.eta_dis)) * 1.0
soc_pct = (curr_e_wh / self.capacity_wh) * 100.0
```
- **Charge Efficiency**: $\eta_{\text{ch}} = 0.92$
- **Discharge Efficiency**: $\eta_{\text{dis}} = 0.92$
- **Timestep**: $\Delta t = 1.0\text{ h}$

### 3.3 Boundary Enforcement
```python
if soc_pct < (self.min_soc_pct - 1e-4) or soc_pct > (self.max_soc_pct + 1e-4):
    raise RuntimeError(f"FAILED_STATE_VIOLATION: Physical SOC_next {soc_pct:.4f}% exceeded configured boundaries...")
```
If the physical state breaches $[20.0\%, 95.0\%]$, `DigitalTwinSimulator` raises a critical termination exception.

### 3.4 Diesel Running State & Hour Counter
```python
diesel_running = p_diesel > 0
diesel_hours = (current_state.diesel_hours_running + 1.0) if diesel_running else 0.0
```

### 3.5 Next StationState Construction
Returns a fresh immutable `StationState`:
```python
return StationState(
    timestamp=next_ts,
    battery_soc_pct=round(soc_pct, 2),
    battery_energy_wh=round(curr_e_wh, 2),
    diesel_running=diesel_running,
    diesel_hours_running=diesel_hours,
    last_observed_solar_irradiance=actual_sw_in,
    last_observed_demand=actual_demand,
    last_observed_wind_generation=actual_wind
)
```

---

## 4. Pre-Test Runtime Dataflow Trace

```text
StationState(t_n)
      ↓
24h ForecastBundle(t_n)
      ↓
GAP19HighsNativeOptimizer.optimize(...)
      ↓
DispatchPlan(t_n ... t_{n+23})
      ↓
First Control Action Only (p_chg[0], p_dis[0], p_diesel[0])
      ↓
DigitalTwinSimulator.step(StationState(t_n), DispatchPlan, actuals_next_step)
      ↓
Physical State Advancement (Energy balance & SOC update)
      ↓
StationState(t_{n+1})
```

---

## 5. Audit Conclusion

The existing `DigitalTwinSimulator` implementation requires **ZERO source-code changes** to participate in the controlled 8-cycle rolling MPC loop.

```text
DIGITAL_TWIN_PRETEST_TRACE = PASS
DIGITAL_TWIN_SOURCE_MODIFICATION_REQUIRED = NO
```
