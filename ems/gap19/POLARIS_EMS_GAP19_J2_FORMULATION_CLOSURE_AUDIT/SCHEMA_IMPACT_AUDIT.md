# Schema and Interface Impact Audit

## 1. Audit of Current GAP19 Variables and Constraints

Static inspection of the active POLARIS codebase (`system/schemas/` and `system/optimization/implementations/milp.py`) reveals the following current state:

### 1.1 `LocalMILPEnergyOptimizer` (`milp.py`)
- **Variable Vector Index**: $K = 15$ variables per timestep $t \in [0, 23]$ (total $N_{\text{vars}} = 360$).
- **Current Variable Vector per timestep $t$**:
  - `0: p_sol_used`, `1: p_wind_used`, `2: p_curt_sol`, `3: p_curt_wind`
  - `4: p_chg`, `5: p_dis`, `6: E_next`, `7: p_diesel`, `8: p_served`, `9: p_unmet`, `10: p_flex`
  - `11: u_chg (bin)`, `12: u_dis (bin)`, `13: u_diesel (bin)`, `14: v_start (bin)`
- **Current Objective Formulation**: Single scalar composite objective $c_{\text{total}} = \sum w_k c_k$.
- **Deficit**: `milp.py` does NOT contain explicit decision variables for Stage 2 EBR shortfall ($s_{\text{EBR}}[t]$), unified reserve shortfall ($s_{J2}[t]$), or Terminal Reserve shortfall ($s_{\text{term}}$).

### 1.2 `ForecastBundle` (`system/schemas/forecast_bundle.py`)
- **Current Fields**: `solar_irradiance`, `solar_generation`, `wind_generation`, `demand`.
- **Deficit**: `demand` represents total station demand as a single timeseries (`point`, `lower`, `upper`). There is NO separate field or array for protected critical demand ($P_{\text{crit}}[t]$).

### 1.3 `StationState` (`system/schemas/station_state.py`)
- **Current Fields**: `timestamp`, `battery_soc_pct`, `battery_energy_wh`, `diesel_running`, `diesel_hours_running`, `last_observed_solar_irradiance`, `last_observed_demand`, `last_observed_wind_generation`.
- **Deficit**: Does NOT contain operating mode (`operating_mode`: `NORMAL` / `EMERGENCY`) or explicit target parameters (`ebr_target_wh`, `terminal_target_wh`).

### 1.4 `DispatchPlan` (`system/schemas/dispatch_plan.py`)
- **Current Fields**: `timestamps`, `solar_used`, `wind_used`, `battery_charge`, `battery_discharge`, `battery_soc`, `diesel_power`, `load_served`, `flexible_load_schedule`, `renewable_curtailment`, `unmet_load`, `objective_value` (single scalar float), `constraint_status`, `energy_balance_errors`.
- **Deficit**: Does NOT report individual stage objective values ($J_1^*, J_2^*, J_3^*, J_4^*$) or Stage 2 reserve shortfall vectors ($s_{J2}[t]$).

---

## 2. Capability Audit: Can Current Variables Represent Governed Semantics?

```text
CURRENT_GAP19_REPRESENTABILITY = INSUFFICIENT
```

**Finding**: The current GAP19 variable vector ($K=15$) and composite cost vector ($c$) CANNOT represent the governed Stage 2 semantics.
Specifically:
1. Critical load is not isolated from total demand in `ForecastBundle`.
2. The optimizer lacks decision variables $s_{J2}[t]$ to measure reserve shortfall below the governed 6-hour EBR lookahead target.
3. The optimizer lacks a terminal decision variable $s_{\text{term}}$ or state constraint for $E_{\text{bat}}[24]$.
4. The solver interface (`scipy.optimize.milp`) receives a single 1D cost array $c$ rather than the multi-pass stage locking loop required for sequential lexicographic optimization (Option A).

---

## 3. Required Additive Schema & Interface Extensions

All required extensions are **ADDITIVE** (zero breaking changes to existing 1.0.0 interfaces):

### 3.1 `ForecastBundle` Additive Extension
- Add optional field `demand_critical: Optional[TimeseriesForecast] = None` to `ForecastBundle` class.
- When `demand_critical` is `None`, default to a governed fallback ratio (e.g. $P_{\text{crit}}[t] = \gamma_{\text{crit}} \cdot P_{\text{demand}}[t]$) to preserve backward compatibility.

### 3.2 `StationState` Additive Extension
- Add optional field `operating_mode: str = "NORMAL"` (values: `"NORMAL"`, `"EMERGENCY"`).
- Add optional field `ebr_target_wh_override: Optional[float] = None`.
- Add optional field `terminal_target_wh_override: Optional[float] = None`.

### 3.3 `DispatchPlan` Additive Extension
- Add optional fields for lexicographic stage results:
  - `j1_objective: Optional[float] = None` (Critical load shedding Wh)
  - `j2_objective: Optional[float] = None` (Reserve shortfall Wh)
  - `j3_objective: Optional[float] = None` (Fuel consumption Liters)
  - `j4_objective: Optional[float] = None` (Renewable curtailment Wh)
  - `reserve_shortfall: Optional[List[float]] = None` (24h array of $s_{J2}[t]$)

### 3.4 Optimizer Variable Vector Expansion ($K = 17$)
Expand decision variable vector per timestep $t$ from $K=15$ to $K=17$:
- Index `15`: `s_ebr` (Continuous, $s_{\text{EBR}}[t] \ge 0$, Stage 2 EBR shortfall slack variable).
- Index `16`: `s_term` (Continuous, $s_{\text{term}} \ge 0$, Stage 2 Terminal Reserve shortfall slack variable at $t=23$).

---

## 4. Summary Verdict

```text
SCHEMA_IMPACT = ADDITIVE_EXTENSION_REQUIRED
BREAKING_CHANGES = NONE
INTERFACE_COMPATIBILITY = PRESERVED
```
