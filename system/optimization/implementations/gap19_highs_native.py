"""
GAP19 Native HiGHS Lexicographic Multi-Objective EnergyOptimizer Implementation (Governed J2 Envelope Closure)
Formulates the governed 432-variable, 336-constraint POLARIS MILP model and executes Option B (Native HiGHS Lexicographic Multi-Objective Optimization) using highspy.

Governed J2 Specifications:
- Total Variables N = 432 (96 Binary, 336 Continuous)
- Total Constraints M = 336 Linear Constraints (NORMAL mode)
- Objective Hierarchy: J1 (Critical Deficit Wh) -> J1b (Non-Critical Unmet Load Wh) -> J2 (Governed Reserve
  Shortfall Wh) -> J3 (Diesel Fuel L) -> J4 (Curtailment Wh)
- Priorities: 5, 4, 3, 2, 1 with blend_multi_objectives = False
- Pointwise Maximum Reserve Envelope: E_stage2_target[t] = max(E_EBR_target[t], delta_{t,23} * E_term_target)

J1b (added): the original formulation only hard-constrained the critical demand
slice (P_unmet_crit) and left the non-critical slice of `demand` completely
unpenalized in every objective -- J1 only counts critical shortfall, so the
solver had zero incentive to ever serve non-critical load once J1 (critical)
and J2 (reserve) were satisfied, and would shed it for free rather than spend
one liter of diesel (J3) to cover it. J1b closes that gap: it measures
non-critical unmet load (= total unmet - critical unmet, via the existing
energy-balance variables p_unmet and P_unmet_crit) and places it strictly
between J1 and J2, so the solver sheds non-critical load only when physically
unavoidable, never merely to save fuel or curtailment.
"""

import math
import numpy as np
import highspy
from typing import Dict, Any, List, Tuple, Optional

from system.optimization.interface.base import EnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

class GAP19HighsNativeOptimizer(EnergyOptimizer):
    def optimize(
        self,
        forecast_bundle: ForecastBundle,
        station_state: StationState,
        config: Dict[str, Any]
    ) -> DispatchPlan:
        
        # 1. Ingest Operating Mode and Config
        opt_cfg = config.get("optimizer", {})
        operating_mode = str(getattr(station_state, "operating_mode", config.get("operating_mode", "NORMAL"))).upper()
        
        timestamps = forecast_bundle.timestamps
        solar_gen = forecast_bundle.solar_generation.point
        wind_gen = forecast_bundle.wind_generation.point
        demand = forecast_bundle.demand.point
        
        # Handle fail-safe UNKNOWN_INVALID mode
        if operating_mode == "UNKNOWN_INVALID":
            return DispatchPlan(
                schema_version="1.0.0",
                timestamps=timestamps,
                solar_used=[0.0]*24,
                wind_used=[0.0]*24,
                battery_charge=[0.0]*24,
                battery_discharge=[0.0]*24,
                battery_soc=[(station_state.battery_energy_wh / float(config.get("battery", {}).get("capacity_wh", 200000.0))) * 100.0]*24,
                diesel_power=[0.0]*24,
                load_served=[0.0]*24,
                flexible_load_schedule=[0.0]*24,
                renewable_curtailment=[(s + w) for s, w in zip(solar_gen, wind_gen)],
                unmet_load=demand,
                objective_value=1e9,
                constraint_status="DEGRADED_FAILSAFE_UNKNOWN_INVALID",
                energy_balance_errors=[0.0]*24,
                j1_objective=1e9,
                j2_objective=0.0,
                j3_objective=0.0,
                j4_objective=0.0,
                reserve_shortfall=[0.0]*24
            )

        # 2. Ingest Physical Asset Parameters
        bat_cfg = config.get("battery", {})
        capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
        min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))
        max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
        eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
        eta_dis = float(bat_cfg.get("discharge_efficiency", 0.92))
        max_p_chg = float(bat_cfg.get("max_charge_power_w", 50000.0))
        max_p_dis = float(bat_cfg.get("max_discharge_power_w", 50000.0))
        
        min_e_wh = capacity_wh * (min_soc_pct / 100.0)
        max_e_wh = capacity_wh * (max_soc_pct / 100.0)
        initial_e_wh = max(min_e_wh, min(max_e_wh, station_state.battery_energy_wh))

        diesel_cfg = config.get("diesel", {})
        min_diesel_w = float(diesel_cfg.get("min_power_w", 10000.0))
        max_diesel_w = float(diesel_cfg.get("max_power_w", 100000.0))
        base_fuel_l_h = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
        marg_fuel_l_wh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))
        startup_fuel_l = float(diesel_cfg.get("startup_fuel_l", 2.0))
        initial_diesel_running = 1 if station_state.diesel_running else 0

        # 3. Ingest Protected Critical Load Trajectory (Explicit Data Semantics)
        if forecast_bundle.demand_critical is not None:
            critical_demand = forecast_bundle.demand_critical.point
        elif "critical_demand_w" in config and config["critical_demand_w"] is not None:
            cd_cfg = config["critical_demand_w"]
            if not isinstance(cd_cfg, (list, tuple)) or len(cd_cfg) != 24:
                raise ValueError(f"Invalid critical_demand_w configuration array length ({len(cd_cfg) if isinstance(cd_cfg, (list, tuple)) else type(cd_cfg)}); expected 24.")
            critical_demand = [float(v) for v in cd_cfg]
        elif "critical_demand_ratio" in config and config["critical_demand_ratio"] is not None:
            ratio = float(config["critical_demand_ratio"])
            if not (0.0 <= ratio <= 1.0):
                raise ValueError(f"Invalid critical_demand_ratio ({ratio}); expected ratio in [0.0, 1.0].")
            critical_demand = [p * ratio for p in demand]
        else:
            raise ValueError("MISSING_GOVERNED_INPUT: Protected critical load trajectory (demand_critical) is missing or unspecified.")

        for idx, (cp, dp) in enumerate(zip(critical_demand, demand)):
            if math.isnan(cp) or math.isinf(cp) or cp < 0.0:
                raise ValueError(f"Invalid protected critical load value at index {idx}: {cp}.")
            if cp > dp + 1e-4:
                raise ValueError(f"Protected critical load ({cp}W) exceeds total demand ({dp}W) at index {idx}.")

        dt = float(opt_cfg.get("timestep_hours", 1.0))

        # 4. Calculate Governed EBR 6-Hour Lookahead Target Trajectory E_EBR_target[t]
        # Governed survivability window T_REQUIRED = 6 hours (6 timesteps)
        ebr_target_wh_list = []
        if getattr(station_state, "ebr_target_wh_override", None) is not None:
            override_val = float(station_state.ebr_target_wh_override)
            ebr_target_wh_list = [override_val] * 24
        elif "ebr_target_wh" in config and config["ebr_target_wh"] is not None:
            ebr_cfg = config["ebr_target_wh"]
            if isinstance(ebr_cfg, (list, tuple)) and len(ebr_cfg) == 24:
                ebr_target_wh_list = [float(v) for v in ebr_cfg]
            elif isinstance(ebr_cfg, (int, float)):
                ebr_target_wh_list = [float(ebr_cfg)] * 24
            else:
                raise ValueError("Invalid ebr_target_wh configuration format; expected scalar or 24-element list.")
        else:
            # Governed formula over 6h lookahead window W(t) = [t, min(t+5, 23)]
            for t in range(24):
                end_k = min(t + 6, 24)
                w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, end_k))
                ebr_req_wh = (1.0 / eta_dis) * w_crit_sum_wh
                ebr_target_wh_list.append(ebr_req_wh)

        # 5. Ingest / Calculate Governed Terminal Reserve Target E_term_target
        if getattr(station_state, "terminal_target_wh_override", None) is not None:
            terminal_target_wh = float(station_state.terminal_target_wh_override)
        elif "terminal_target_wh" in config and config["terminal_target_wh"] is not None:
            terminal_target_wh = float(config["terminal_target_wh"])
        elif config.get("terminal_reserve_model") == "INITIAL_STATE":
            terminal_target_wh = initial_e_wh
        elif config.get("terminal_reserve_model") == "CAPACITY_RATIO":
            alpha_term = float(config.get("terminal_capacity_ratio", 0.5))
            terminal_target_wh = min_e_wh + alpha_term * (max_e_wh - min_e_wh)
        else:
            raise ValueError("MISSING_GOVERNED_INPUT: Terminal reserve target (terminal_target_wh) is missing or unspecified.")

        # 6. Construct Pointwise Maximum Reserve Envelope Trajectory E_stage2_target[t]
        e_stage2_target = [0.0] * 24
        for t in range(23):
            e_stage2_target[t] = ebr_target_wh_list[t]
        # Horizon edge (t=23): pointwise maximum envelope of EBR and Terminal Reserve
        e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)

        # 6b. Optional Reserve Deadband (hysteresis): relaxes the J2 target line by a
        # flat Wh amount so shortfalls within the deadband register as zero J2 cost
        # and never pressure the solver to commit the diesel generator's 10kW floor
        # to chase them. Purely additive/soft -- read defensively, defaults to 0.0
        # (fully inert/backward-compatible) if absent, matching the reserve_shortfall_penalty
        # convention in optimizer.yaml. Does NOT touch the hard physical SOC floor
        # (min_e_wh), which remains enforced unconditionally below.
        reserve_deadband_wh = float(config.get("reserve_deadband_wh", 0.0))
        if reserve_deadband_wh > 0.0:
            e_stage2_target = [max(0.0, v - reserve_deadband_wh) for v in e_stage2_target]

        H = 24
        K = 15

        # Variable Index Layout (Unified N = 432):
        # Base 360 variables: 0 .. 359 (15 per timestep)
        # 360 .. 383: P_unmet_crit[t] (24 continuous)
        # 384 .. 407: s_J2[t] (24 continuous)
        # 408 .. 431: P_unmet_noncrit[t] (24 continuous) -- J1b penalty variable
        # Total: 432 variables (96 binary, 336 continuous)

        num_base_vars = H * K # 360
        idx_unmet_crit_start = num_base_vars # 360
        idx_s_j2_start = idx_unmet_crit_start + H # 384
        idx_unmet_noncrit_start = idx_s_j2_start + H # 408
        num_total_vars = idx_unmet_noncrit_start + H # 432

        lb = np.zeros(num_total_vars)
        ub = np.zeros(num_total_vars)
        integrality = np.zeros(num_total_vars, dtype=int)

        for t in range(H):
            base = t * K
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_dem = max(0.0, demand[t])
            p_crit_dem = max(0.0, critical_demand[t])

            # Base variables
            lb[base + 0], ub[base + 0] = 0.0, p_sol_max     # p_sol_used
            lb[base + 1], ub[base + 1] = 0.0, p_wind_max    # p_wind_used
            lb[base + 2], ub[base + 2] = 0.0, p_sol_max     # p_curt_sol
            lb[base + 3], ub[base + 3] = 0.0, p_wind_max    # p_curt_wind
            lb[base + 4], ub[base + 4] = 0.0, max_p_chg     # p_chg
            lb[base + 5], ub[base + 5] = 0.0, max_p_dis     # p_dis
            lb[base + 6], ub[base + 6] = min_e_wh, max_e_wh # E_next
            lb[base + 7], ub[base + 7] = 0.0, max_diesel_w  # p_diesel
            lb[base + 8], ub[base + 8] = 0.0, p_dem         # p_served
            lb[base + 9], ub[base + 9] = 0.0, p_dem         # p_unmet
            lb[base + 10], ub[base + 10] = 0.0, 500.0       # p_flex
            
            # Binary variables (96 total)
            lb[base + 11], ub[base + 11] = 0.0, 1.0; integrality[base + 11] = 1 # u_chg
            lb[base + 12], ub[base + 12] = 0.0, 1.0; integrality[base + 12] = 1 # u_dis
            lb[base + 13], ub[base + 13] = 0.0, 1.0; integrality[base + 13] = 1 # u_diesel
            lb[base + 14], ub[base + 14] = 0.0, 1.0; integrality[base + 14] = 1 # v_start

            # Optional what-if hook (inert when absent): config["diesel_step_overrides"] maps a
            # planning step to "off" (generator banned that step) or "on" (generator forced
            # running that step). Used only by the decision what-if analysis.
            _ovr = (config.get("diesel_step_overrides") or {}).get(t)
            if _ovr is None:
                _ovr = (config.get("diesel_step_overrides") or {}).get(str(t))
            if _ovr == "off":
                ub[base + 7] = 0.0; ub[base + 13] = 0.0
            elif _ovr == "on":
                lb[base + 13] = 1.0

            # Layer B: P_unmet_crit[t]
            lb[idx_unmet_crit_start + t] = 0.0
            ub[idx_unmet_crit_start + t] = p_crit_dem

            # Layer C: s_J2[t]
            lb[idx_s_j2_start + t] = 0.0
            ub[idx_s_j2_start + t] = capacity_wh

            # J1b: P_unmet_noncrit[t] -- bounded by the non-critical slice of demand
            lb[idx_unmet_noncrit_start + t] = 0.0
            ub[idx_unmet_noncrit_start + t] = max(0.0, p_dem - p_crit_dem)

        # 7. Construct Linear Constraints Matrix (M = 312 total constraints in NORMAL mode)
        A_rows = []
        lhs_list = []
        rhs_list = []

        for t in range(H):
            base = t * K
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_dem = max(0.0, demand[t])
            p_crit_dem = max(0.0, critical_demand[t])

            # 1. Solar Decomposition
            row = np.zeros(num_total_vars)
            row[base + 0] = 1.0; row[base + 2] = 1.0
            A_rows.append(row); lhs_list.append(p_sol_max); rhs_list.append(p_sol_max)

            # 2. Wind Decomposition
            row = np.zeros(num_total_vars)
            row[base + 1] = 1.0; row[base + 3] = 1.0
            A_rows.append(row); lhs_list.append(p_wind_max); rhs_list.append(p_wind_max)

            # 3. Bus-Bar Balance
            row = np.zeros(num_total_vars)
            row[base + 0] = 1.0; row[base + 1] = 1.0; row[base + 5] = 1.0; row[base + 7] = 1.0
            row[base + 8] = -1.0; row[base + 4] = -1.0; row[base + 10] = -1.0
            A_rows.append(row); lhs_list.append(0.0); rhs_list.append(0.0)

            # 4. Total Demand Deficit Balance
            row = np.zeros(num_total_vars)
            row[base + 8] = 1.0; row[base + 9] = 1.0
            A_rows.append(row); lhs_list.append(p_dem); rhs_list.append(p_dem)

            # 5. Charge Bound vs Binary
            row = np.zeros(num_total_vars)
            row[base + 4] = 1.0; row[base + 11] = -max_p_chg
            A_rows.append(row); lhs_list.append(-np.inf); rhs_list.append(0.0)

            # 6. Discharge Bound vs Binary
            row = np.zeros(num_total_vars)
            row[base + 5] = 1.0; row[base + 12] = -max_p_dis
            A_rows.append(row); lhs_list.append(-np.inf); rhs_list.append(0.0)

            # 7. Exclusivity Bound
            row = np.zeros(num_total_vars)
            row[base + 11] = 1.0; row[base + 12] = 1.0
            A_rows.append(row); lhs_list.append(-np.inf); rhs_list.append(1.0)

            # 8. Battery Energy Discrete Transition
            row = np.zeros(num_total_vars)
            row[base + 6] = 1.0
            if t == 0:
                row[base + 4] = -eta_chg * dt
                row[base + 5] = dt / eta_dis
                A_rows.append(row); lhs_list.append(initial_e_wh); rhs_list.append(initial_e_wh)
            else:
                prev_base = (t - 1) * K
                row[prev_base + 6] = -1.0
                row[base + 4] = -eta_chg * dt
                row[base + 5] = dt / eta_dis
                A_rows.append(row); lhs_list.append(0.0); rhs_list.append(0.0)

            # 9. Diesel Min Output
            row = np.zeros(num_total_vars)
            row[base + 7] = 1.0; row[base + 13] = -min_diesel_w
            A_rows.append(row); lhs_list.append(0.0); rhs_list.append(np.inf)

            # 10. Diesel Max Output
            row = np.zeros(num_total_vars)
            row[base + 7] = 1.0; row[base + 13] = -max_diesel_w
            A_rows.append(row); lhs_list.append(-np.inf); rhs_list.append(0.0)

            # 11. Diesel Startup Tracking
            row = np.zeros(num_total_vars)
            row[base + 14] = 1.0; row[base + 13] = -1.0
            if t == 0:
                A_rows.append(row); lhs_list.append(-initial_diesel_running); rhs_list.append(np.inf)
            else:
                prev_base = (t - 1) * K
                row[prev_base + 13] = 1.0
                A_rows.append(row); lhs_list.append(0.0); rhs_list.append(np.inf)

        # Layer B: 24 Critical Demand Protection Constraints (264 .. 287)
        # Served load + unmet critical load >= critical demand (a FLOOR, not a
        # ceiling, on p_served). The original formulation used an EQUALITY here
        # (p_served + P_unmet_crit == p_crit_dem), which algebraically pinned
        # p_served to never exceed the critical slice -- making it structurally
        # impossible for the solver to ever serve non-critical demand, no matter
        # what any objective (including the new J1b below) wanted. The inequality
        # lets p_served range freely up to the full p_dem[t] while J1's
        # minimization of P_unmet_crit still drives it to exactly
        # max(0, p_crit_dem[t] - p_served[t]), so critical-load protection is
        # unchanged -- only the artificial ceiling on serving the rest is removed.
        for t in range(H):
            base = t * K
            p_crit_dem = max(0.0, critical_demand[t])
            row = np.zeros(num_total_vars)
            row[base + 8] = 1.0 # p_served
            row[idx_unmet_crit_start + t] = 1.0 # P_unmet_crit
            A_rows.append(row); lhs_list.append(p_crit_dem); rhs_list.append(np.inf)

        # Layer C: 24 Stage 2 Unified Reserve Envelope Constraints (288 .. 311)
        # E_next[t] + s_J2[t] >= E_stage2_target[t] + min_e_wh
        for t in range(H):
            base = t * K
            row = np.zeros(num_total_vars)
            row[base + 6] = 1.0 # E_next[t]
            row[idx_s_j2_start + t] = 1.0 # s_J2[t]
            req_lhs = e_stage2_target[t] + min_e_wh
            A_rows.append(row); lhs_list.append(req_lhs); rhs_list.append(np.inf)

        # Layer E: 24 Non-Critical Unmet Load Definition Constraints (J1b)
        # P_unmet_noncrit[t] == p_unmet[t] - P_unmet_crit[t]
        for t in range(H):
            base = t * K
            row = np.zeros(num_total_vars)
            row[idx_unmet_noncrit_start + t] = 1.0   # P_unmet_noncrit
            row[base + 9] = -1.0                      # p_unmet (total)
            row[idx_unmet_crit_start + t] = 1.0       # P_unmet_crit
            A_rows.append(row); lhs_list.append(0.0); rhs_list.append(0.0)

        # Layer D: Option D Emergency Mode Constraints if active
        if operating_mode == "EMERGENCY":
            for t in range(H):
                base = t * K
                # Critical-only discharge: p_dis[t] <= p_served[t]
                row = np.zeros(num_total_vars)
                row[base + 5] = 1.0 # p_dis
                row[base + 8] = -1.0 # p_served
                A_rows.append(row); lhs_list.append(-np.inf); rhs_list.append(0.0)

        A_mat = np.array(A_rows)
        lhs_arr = np.array(lhs_list)
        rhs_arr = np.array(rhs_list)
        num_constraints = A_mat.shape[0]

        # 8. Construct Objective Vectors J1, J1b, J2, J3, J4 (Length N = 432)
        c1 = np.zeros(num_total_vars)
        c1b = np.zeros(num_total_vars)
        c2 = np.zeros(num_total_vars)
        c3 = np.zeros(num_total_vars)
        c4 = np.zeros(num_total_vars)

        for t in range(H):
            base = t * K
            # J1: Critical Deficit Wh
            c1[idx_unmet_crit_start + t] = 1.0 * dt

            # J1b: Non-Critical Unmet Load Wh (shed only if physically unavoidable)
            c1b[idx_unmet_noncrit_start + t] = 1.0 * dt

            # J2: Governed Reserve Shortfall Wh (Pointwise Envelope)
            c2[idx_s_j2_start + t] = 1.0

            # J3: Diesel Fuel Liters (marg_fuel * p_diesel + base_fuel * u_diesel + startup_fuel * v_start) * dt
            c3[base + 7] = marg_fuel_l_wh * dt
            c3[base + 13] = base_fuel_l_h * dt
            c3[base + 14] = startup_fuel_l

            # J4: Renewable Curtailment Wh
            c4[base + 2] = 1.0 * dt
            c4[base + 3] = 1.0 * dt

        # 9. Initialize HiGHS C++ Solver via highspy
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("threads", 1)
        h.setOptionValue("blend_multi_objectives", False)

        # Add Variables
        h.addVars(num_total_vars, lb, ub)
        for j in range(num_total_vars):
            if integrality[j] == 1:
                h.changeColIntegrality(j, highspy.HighsVarType.kInteger)

        # Add Constraints
        for i in range(num_constraints):
            row_vals = A_mat[i]
            nonzeros = np.where(row_vals != 0.0)[0]
            indices = nonzeros.astype(np.int32)
            coeffs = row_vals[nonzeros].astype(np.float64)
            h.addRow(lhs_arr[i], rhs_arr[i], len(indices), indices, coeffs)

        # Add Objectives (Option B Priority Mapping: J1 > J1b > J2 > J3 > J4)
        obj1 = highspy.HighsLinearObjective()
        obj1.priority = 5; obj1.weight = 1.0; obj1.offset = 0.0; obj1.abs_tolerance = 0.0; obj1.rel_tolerance = 0.0
        obj1.coefficients = c1.tolist()

        obj1b = highspy.HighsLinearObjective()
        obj1b.priority = 4; obj1b.weight = 1.0; obj1b.offset = 0.0; obj1b.abs_tolerance = 0.0; obj1b.rel_tolerance = 0.0
        obj1b.coefficients = c1b.tolist()

        obj2 = highspy.HighsLinearObjective()
        obj2.priority = 3; obj2.weight = 1.0; obj2.offset = 0.0; obj2.abs_tolerance = 0.0; obj2.rel_tolerance = 0.0
        obj2.coefficients = c2.tolist()

        obj3 = highspy.HighsLinearObjective()
        obj3.priority = 2; obj3.weight = 1.0; obj3.offset = 0.0; obj3.abs_tolerance = 0.0; obj3.rel_tolerance = 0.0
        obj3.coefficients = c3.tolist()

        obj4 = highspy.HighsLinearObjective()
        obj4.priority = 1; obj4.weight = 1.0; obj4.offset = 0.0; obj4.abs_tolerance = 0.0; obj4.rel_tolerance = 0.0
        obj4.coefficients = c4.tolist()

        h.addLinearObjective(obj1)
        h.addLinearObjective(obj1b)
        h.addLinearObjective(obj2)
        h.addLinearObjective(obj3)
        h.addLinearObjective(obj4)

        # Run Solver
        h.run()
        model_status = h.getModelStatus()

        if model_status != highspy.HighsModelStatus.kOptimal:
            return DispatchPlan(
                schema_version="1.0.0",
                timestamps=timestamps,
                solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
                battery_soc=[min_soc_pct]*24, diesel_power=[0.0]*24, load_served=[0.0]*24,
                flexible_load_schedule=[0.0]*24, renewable_curtailment=[(s + w) for s, w in zip(solar_gen, wind_gen)],
                unmet_load=demand, objective_value=1e9,
                constraint_status=f"OPTIMIZATION_INFEASIBLE: {model_status}",
                energy_balance_errors=[0.0]*24,
                j1_objective=1e9, j2_objective=1e9, j3_objective=1e9, j4_objective=1e9,
                reserve_shortfall=[capacity_wh]*24
            )

        sol = h.getSolution()
        col_vals = np.array(sol.col_value)

        # 10. Extract Dispatch Outputs & Stage Objectives
        solar_used, wind_used, battery_charge, battery_discharge, battery_soc = [], [], [], [], []
        diesel_power, load_served, flexible_load_schedule, renewable_curtailment, unmet_load = [], [], [], [], []
        energy_balance_errors = []
        reserve_shortfall = []
        unmet_noncritical_load = []

        for t in range(H):
            base = t * K
            p_sol_u = max(0.0, float(col_vals[base + 0]))
            p_w_u = max(0.0, float(col_vals[base + 1]))
            p_c_sol = max(0.0, float(col_vals[base + 2]))
            p_c_w = max(0.0, float(col_vals[base + 3]))
            p_chg = max(0.0, float(col_vals[base + 4]))
            p_dis = max(0.0, float(col_vals[base + 5]))
            e_next = float(col_vals[base + 6])
            p_dies = max(0.0, float(col_vals[base + 7]))
            p_serv = max(0.0, float(col_vals[base + 8]))
            p_unm = max(0.0, float(col_vals[base + 9]))
            p_flx = max(0.0, float(col_vals[base + 10]))
            s_j2_val = max(0.0, float(col_vals[idx_s_j2_start + t]))
            p_unm_noncrit = max(0.0, float(col_vals[idx_unmet_noncrit_start + t]))

            soc_pct = (e_next / capacity_wh) * 100.0
            p_curt_tot = p_c_sol + p_c_w
            err = max(
                abs((p_sol_u + p_w_u + p_dis + p_dies) - (p_serv + p_chg + p_flx)),
                abs(demand[t] - (p_serv + p_unm))
            )

            solar_used.append(round(p_sol_u, 2))
            wind_used.append(round(p_w_u, 2))
            battery_charge.append(round(p_chg, 2))
            battery_discharge.append(round(p_dis, 2))
            battery_soc.append(round(soc_pct, 2))
            diesel_power.append(round(p_dies, 2))
            load_served.append(round(p_serv, 2))
            flexible_load_schedule.append(round(p_flx, 2))
            renewable_curtailment.append(round(p_curt_tot, 2))
            unmet_load.append(round(p_unm, 2))
            energy_balance_errors.append(round(err, 6))
            reserve_shortfall.append(round(s_j2_val, 4))
            unmet_noncritical_load.append(round(p_unm_noncrit, 2))

        J1_val = float(np.dot(c1, col_vals))
        J1b_val = float(np.dot(c1b, col_vals))
        J2_val = float(np.dot(c2, col_vals))
        J3_val = float(np.dot(c3, col_vals))
        J4_val = float(np.dot(c4, col_vals))

        return DispatchPlan(
            schema_version="1.0.0",
            timestamps=timestamps,
            solar_used=solar_used,
            wind_used=wind_used,
            battery_charge=battery_charge,
            battery_discharge=battery_discharge,
            battery_soc=battery_soc,
            diesel_power=diesel_power,
            load_served=load_served,
            flexible_load_schedule=flexible_load_schedule,
            renewable_curtailment=renewable_curtailment,
            unmet_load=unmet_load,
            objective_value=round(J3_val, 4), # Primary operational fuel cost reported
            constraint_status="OPTIMAL",
            energy_balance_errors=energy_balance_errors,
            j1_objective=round(J1_val, 4),
            j2_objective=round(J2_val, 4),
            j3_objective=round(J3_val, 4),
            j4_objective=round(J4_val, 4),
            reserve_shortfall=reserve_shortfall,
            unmet_noncritical_load=unmet_noncritical_load,
            j1b_objective=round(J1b_val, 4)
        )
