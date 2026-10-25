# POLARIS EMS GAP19 — HIGHS NATIVE TRANSFER AUDIT
# Document 09: INTERFACE IMPACT ANALYSIS
# Audit Phase: GAP19_HIGHS_NATIVE_TRANSFER_AUDIT
# Generation Mode: READ-ONLY STATIC CODE ANALYSIS
# Execution Performed: FALSE

---

## SCOPE

This document audits the interface impact of transitioning from the current
single weighted-sum MILP objective to a 4-stage lexicographic objective under
either Option A (sequential MILP) or Option B (native HiGHS multi-objective).

Interfaces analyzed:
1. ForecastBundle → LocalMILPEnergyOptimizer
2. StationState → LocalMILPEnergyOptimizer
3. LocalMILPEnergyOptimizer → DispatchPlan
4. config dict → LocalMILPEnergyOptimizer
5. EnergyOptimizer base class interface

---

## 1. FORECASTBUNDLE INTERFACE

**Interface boundary:** `forecast_bundle: ForecastBundle` parameter to `optimize()`

| Field used | Lines in milp.py | Used by |
|---|---|---|
| `forecast_bundle.timestamps` | L67 | Output assignment (DispatchPlan.timestamps) |
| `forecast_bundle.solar_generation.point` | L68 | solar_gen variable, bounds C1, objective c[+2][+3] |
| `forecast_bundle.wind_generation.point` | L69 | wind_gen variable, bounds C2, objective c[+3] |
| `forecast_bundle.demand.point` | L70 | demand variable, bounds C3 C4 |

**Impact: NONE**

Neither Option A nor Option B requires any change to ForecastBundle structure,
fields, or access patterns. All four fields are used identically regardless of
objective architecture. ForecastBundle is an input to constraint construction,
not to objective construction (except indirectly via variable bounds).

---

## 2. STATIONSTATE INTERFACE

**Interface boundary:** `station_state: StationState` parameter to `optimize()`

| Field used | Lines in milp.py | Used by |
|---|---|---|
| `station_state.battery_energy_wh` | L37 | initial_e_wh → C8 t=0 constraint RHS |
| `station_state.diesel_running` | L46 | initial_diesel_running → C11 t=0 constraint LHS |

**Impact: NONE**

Both StationState fields are used only in constraint construction (not in objective
construction). Neither Option A nor Option B changes the constraint matrix. The
StationState interface is unaffected.

---

## 3. DISPATCHPLAN INTERFACE

**Interface boundary:** `return DispatchPlan(...)` from `optimize()`

| Field | Current source | Option A impact | Option B impact |
|---|---|---|---|
| `timestamps` | `forecast_bundle.timestamps` | NONE | NONE |
| `solar_used` | `sol[base+0]` per t | NONE | NONE |
| `wind_used` | `sol[base+1]` per t | NONE | NONE |
| `battery_charge` | `sol[base+4]` per t | NONE | NONE |
| `battery_discharge` | `sol[base+5]` per t | NONE | NONE |
| `battery_soc` | `(E_next/capacity_wh)*100` per t | NONE | NONE |
| `diesel_power` | `sol[base+7]` per t | NONE | NONE |
| `load_served` | `sol[base+8]` per t | NONE | NONE |
| `flexible_load_schedule` | `sol[base+10]` per t | NONE | NONE |
| `renewable_curtailment` | `p_c_sol+p_c_w` per t | NONE | NONE |
| `unmet_load` | `sol[base+9]` per t | NONE | NONE |
| `objective_value` | `res.fun` (scalar) | Returns Stage 4 final objective value OR governance may add per-stage reporting | Same as Option A |
| `constraint_status` | `"OPTIMAL"` or infeasibility string | May need: "LEX_OPTIMAL_STAGE_k" if partial lex solve | Same |
| `energy_balance_errors` | Post-solve verification | NONE | NONE |
| `schema_version` | `"1.0.0"` | NONE | NONE |

**Impact: MINOR (optional)**

The DispatchPlan schema does not require changes for either option. The only
potential change is to `objective_value` — currently a single scalar. If per-stage
objective values are desired for traceability, an optional `per_stage_objectives`
field could be added to DispatchPlan. This is a GOVERNANCE DECISION (OI-7), not
a technical requirement.

**The solution vectors** `sol[base+k]` are extracted identically in both options —
the final `res.x` (Option A, Stage 4 solve) or the final HiGHS solution (Option B)
are accessed in the same way.

---

## 4. CONFIG DICT INTERFACE

**Interface boundary:** `config: Dict[str, Any]` parameter to `optimize()`

Current config keys used in milp.py (from optimizer.yaml and runtime config):

| Key path | Used for | Change required |
|---|---|---|
| `battery.capacity_wh` | capacity_wh | NONE |
| `battery.min_soc_pct` | min_e_wh bound | NONE |
| `battery.max_soc_pct` | max_e_wh bound | NONE |
| `battery.charge_efficiency` | eta_chg | NONE |
| `battery.discharge_efficiency` | eta_dis | NONE |
| `battery.max_charge_power_w` | max_p_chg | NONE |
| `battery.max_discharge_power_w` | max_p_dis | NONE |
| `battery.deg_penalty_per_wh` | deg_penalty | NONE |
| `diesel.min_power_w` | min_diesel_w | NONE |
| `diesel.max_power_w` | max_diesel_w | NONE |
| `diesel.base_fuel_consumption_l_per_h` | base_fuel_l_h | NONE |
| `diesel.marginal_fuel_consumption_l_per_wh` | marg_fuel_l_wh | NONE |
| `diesel.fuel_cost_per_l` | fuel_cost_per_l | NONE |
| `diesel.startup_cost` | startup_cost | NONE |
| `loads.critical_load.unmet_penalty_per_wh` | unmet_penalty_per_wh | NONE |
| `loads.deferrable_loads` | flex load config | NONE |
| `optimizer.timestep_hours` | dt | NONE |
| `optimizer.weights.renewable_curtailment_penalty` | curt_penalty_per_wh | NONE |
| `optimizer.horizon_discount_factor_gamma` | w_t computation | NONE |
| `optimizer.custom_weight_vector` | w_t computation | NONE |
| `optimizer.v4g_single_horizon_mode` | w_t computation | NONE |

**New config keys REQUIRED for lexicographic implementation:**

| New key path | Purpose | Applies to | Notes |
|---|---|---|---|
| `optimizer.E_EBR_target_pct` or `battery.terminal_reserve_pct` | Stage 2 terminal reserve target | BOTH options | BLOCKING (OI-2). No current value defined. |
| `optimizer.lex_tolerance.stage1_eps` | Option A Stage 1 epsilon lock | Option A | OI-3. Could default to 0.0. |
| `optimizer.lex_tolerance.stage2_eps` | Option A Stage 2 epsilon lock | Option A | OI-3. Could default to 0.0. |
| `optimizer.lex_tolerance.stage3_eps` | Option A Stage 3 epsilon lock | Option A | OI-3. Could default to 0.0. |

**Impact: MINOR extension** — optimizer.yaml requires 1-4 new keys. Existing keys unchanged.

---

## 5. ENERGYOPTIMIZER BASE CLASS INTERFACE

**Interface boundary:** `class LocalMILPEnergyOptimizer(EnergyOptimizer)` with `def optimize(self, forecast_bundle, station_state, config) -> DispatchPlan`

The base class interface signature is:
```
optimize(forecast_bundle: ForecastBundle, station_state: StationState, config: Dict[str, Any]) -> DispatchPlan
```

**Impact: NONE**

Neither Option A nor Option B changes the `optimize()` method signature. The
lexicographic solve is entirely internal to `LocalMILPEnergyOptimizer.optimize()`.
All callers of this method (MPC controller, Digital Twin, test harness) are unaffected.

---

## INTERFACE IMPACT SUMMARY

| Interface | Option A Impact | Option B Impact |
|---|---|---|
| ForecastBundle | NONE | NONE |
| StationState | NONE | NONE |
| DispatchPlan schema | NONE (optional per-stage reporting) | NONE (optional per-stage reporting) |
| config dict (optimizer.yaml) | MINOR: add E_EBR_target + lex_tolerance keys | MINOR: same additions |
| EnergyOptimizer base class | NONE | NONE |
| Python solver library | NONE (stays scipy) | HIGH: add highspy dependency |
| MPC/Digital Twin callers | NONE | NONE |

**Conclusion:** The governed lexicographic objective transition does NOT require schema
changes to ForecastBundle, StationState, or the DispatchPlan output. The impact is
confined to: (1) internal milp.py `optimize()` method refactoring, (2) minor
optimizer.yaml config additions, and (3) for Option B only, the addition of the
highspy library dependency.
