"""
POLARIS Research-Only Numerical Boundary Extractor & Optimizer
Module: experiments.candidate_s_sw_campaign_2024.research_numerical_extractor

Implements the governance-approved numerical boundary resolution protocol
specified in ADDENDUM-NUMERICAL-BOUNDARY-RESIDUE-01:
- HiGHS default tolerances:
    eps_integrality = 1e-6
    eps_primal = 1e-7
- Battery flow capacity M = 50,000 W
- Derived theoretical residue bound:
    tau = M * (eps_integrality + eps_primal) = 50,000 * (1e-6 + 1e-7) = 0.055 W

Extraction Protocol:
- Operates on raw, UNROUNDED solver solution values before DispatchPlan construction.
- If raw_p_chg > 0 and raw_p_dis > 0:
    - If min(raw_p_chg, raw_p_dis) <= 0.055 W: zero the smaller flow (non-physical residue).
    - If min(raw_p_chg, raw_p_dis) > 0.055 W: raise genuine simultaneous charge/discharge violation.
- Otherwise: no change.
- Never normalizes binaries (u_chg, u_dis remain raw unrounded floats).
- Never modifies solver tolerances, options, or MILP formulations.
- Captures full raw solver diagnostics per reoptimization cycle.
"""

import math
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.dispatch_plan import DispatchPlan
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer

TAU_RESIDUE_W: float = 0.055
BIG_M_W: float = 50000.0
EPS_INTEGRALITY: float = 1e-6
EPS_PRIMAL: float = 1e-7


def extract_and_correct_flows(
    raw_chg: float,
    raw_dis: float,
    tau: float = TAU_RESIDUE_W
) -> Tuple[float, float, bool, float]:
    """
    Applies the approved residue correction protocol on unrounded continuous flows.

    Returns:
        (corrected_chg, corrected_dis, correction_fired, zeroed_magnitude)

    Raises:
        ValueError if genuine simultaneous flow exceeds tau.
    """
    chg = float(raw_chg)
    dis = float(raw_dis)

    if chg > 0.0 and dis > 0.0:
        min_flow = min(chg, dis)
        if min_flow <= tau:
            if chg <= dis:
                return 0.0, dis, True, chg
            else:
                return chg, 0.0, True, dis
        else:
            raise ValueError(
                f"GENUINE_SIMULTANEOUS_FLOW_VIOLATION: charge={chg:.6f} W, "
                f"discharge={dis:.6f} W strictly exceeds numerical residue threshold tau={tau} W."
            )

    return chg, dis, False, 0.0


class ResearchNumericalGAP19Optimizer(GAP19HighsNativeOptimizer):
    """
    Research-only optimizer that inherits GAP19HighsNativeOptimizer,
    preserves 100% of its MILP constraints, objective hierarchy, and solver settings,
    and applies the governance-approved numerical extraction protocol on raw unrounded
    solver solutions before DispatchPlan construction.
    """

    def __init__(self, tau: float = TAU_RESIDUE_W):
        super().__init__()
        self.tau: float = tau
        self.last_diagnostics: List[Dict[str, Any]] = []

    def optimize(
        self,
        forecast_bundle: ForecastBundle,
        station_state: StationState,
        config: Dict[str, Any]
    ) -> DispatchPlan:
        import highspy

        # 1. Ingest Operating Mode and Config
        opt_cfg = config.get("optimizer", {})
        operating_mode = str(getattr(station_state, "operating_mode", config.get("operating_mode", "NORMAL"))).upper()

        timestamps = forecast_bundle.timestamps
        solar_gen = forecast_bundle.solar_generation.point
        wind_gen = forecast_bundle.wind_generation.point
        demand = forecast_bundle.demand.point

        # Handle fail-safe UNKNOWN_INVALID mode
        if operating_mode == "UNKNOWN_INVALID":
            self.last_diagnostics = []
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
        e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)

        H = 24
        K = 15

        num_base_vars = H * K # 360
        idx_unmet_crit_start = num_base_vars # 360
        idx_s_j2_start = idx_unmet_crit_start + H # 384
        num_total_vars = idx_s_j2_start + H # 408

        lb = np.zeros(num_total_vars)
        ub = np.zeros(num_total_vars)
        integrality = np.zeros(num_total_vars, dtype=int)

        for t in range(H):
            base = t * K
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_dem = max(0.0, demand[t])
            p_crit_dem = max(0.0, critical_demand[t])

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

            lb[base + 11], ub[base + 11] = 0.0, 1.0; integrality[base + 11] = 1 # u_chg
            lb[base + 12], ub[base + 12] = 0.0, 1.0; integrality[base + 12] = 1 # u_dis
            lb[base + 13], ub[base + 13] = 0.0, 1.0; integrality[base + 13] = 1 # u_diesel
            lb[base + 14], ub[base + 14] = 0.0, 1.0; integrality[base + 14] = 1 # v_start

            lb[idx_unmet_crit_start + t] = 0.0
            ub[idx_unmet_crit_start + t] = p_crit_dem

            lb[idx_s_j2_start + t] = 0.0
            ub[idx_s_j2_start + t] = capacity_wh

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

        # Layer B: 24 Critical Demand Balance Constraints
        for t in range(H):
            base = t * K
            p_crit_dem = max(0.0, critical_demand[t])
            row = np.zeros(num_total_vars)
            row[base + 8] = 1.0
            row[idx_unmet_crit_start + t] = 1.0
            A_rows.append(row); lhs_list.append(p_crit_dem); rhs_list.append(p_crit_dem)

        # Layer C: 24 Stage 2 Unified Reserve Envelope Constraints
        for t in range(H):
            base = t * K
            row = np.zeros(num_total_vars)
            row[base + 6] = 1.0
            row[idx_s_j2_start + t] = 1.0
            req_lhs = e_stage2_target[t] + min_e_wh
            A_rows.append(row); lhs_list.append(req_lhs); rhs_list.append(np.inf)

        if operating_mode == "EMERGENCY":
            for t in range(H):
                base = t * K
                row = np.zeros(num_total_vars)
                row[base + 5] = 1.0
                row[base + 8] = -1.0
                A_rows.append(row); lhs_list.append(-np.inf); rhs_list.append(0.0)

        A_mat = np.array(A_rows)
        lhs_arr = np.array(lhs_list)
        rhs_arr = np.array(rhs_list)
        num_constraints = A_mat.shape[0]

        # 8. Objectives J1..J4
        c1 = np.zeros(num_total_vars)
        c2 = np.zeros(num_total_vars)
        c3 = np.zeros(num_total_vars)
        c4 = np.zeros(num_total_vars)

        for t in range(H):
            base = t * K
            c1[idx_unmet_crit_start + t] = 1.0 * dt
            c2[idx_s_j2_start + t] = 1.0
            c3[base + 7] = marg_fuel_l_wh * dt
            c3[base + 13] = base_fuel_l_h * dt
            c3[base + 14] = startup_fuel_l
            c4[base + 2] = 1.0 * dt
            c4[base + 3] = 1.0 * dt

        # 9. Solve via HiGHS
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("threads", 1)
        h.setOptionValue("blend_multi_objectives", False)

        h.addVars(num_total_vars, lb, ub)
        for j in range(num_total_vars):
            if integrality[j] == 1:
                h.changeColIntegrality(j, highspy.HighsVarType.kInteger)

        for i in range(num_constraints):
            row_vals = A_mat[i]
            nonzeros = np.where(row_vals != 0.0)[0]
            indices = nonzeros.astype(np.int32)
            coeffs = row_vals[nonzeros].astype(np.float64)
            h.addRow(lhs_arr[i], rhs_arr[i], len(indices), indices, coeffs)

        obj1 = highspy.HighsLinearObjective()
        obj1.priority = 4; obj1.weight = 1.0; obj1.offset = 0.0; obj1.abs_tolerance = 0.0; obj1.rel_tolerance = 0.0
        obj1.coefficients = c1.tolist()

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
        h.addLinearObjective(obj2)
        h.addLinearObjective(obj3)
        h.addLinearObjective(obj4)

        h.run()
        model_status = h.getModelStatus()

        if model_status != highspy.HighsModelStatus.kOptimal:
            self.last_diagnostics = []
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

        # 10. Extract Dispatch Outputs with Research Numerical Boundary Extraction
        solar_used, wind_used, battery_charge, battery_discharge, battery_soc = [], [], [], [], []
        diesel_power, load_served, flexible_load_schedule, renewable_curtailment, unmet_load = [], [], [], [], []
        energy_balance_errors = []
        reserve_shortfall = []
        diagnostics = []

        # HiGHS mip gap / status
        info = h.getInfo()
        mip_gap = getattr(info, "mip_gap", 0.0)

        for t in range(H):
            base = t * K
            p_sol_u = max(0.0, float(col_vals[base + 0]))
            p_w_u = max(0.0, float(col_vals[base + 1]))
            p_c_sol = max(0.0, float(col_vals[base + 2]))
            p_c_w = max(0.0, float(col_vals[base + 3]))

            # Raw unrounded flow extraction
            raw_p_chg = max(0.0, float(col_vals[base + 4]))
            raw_p_dis = max(0.0, float(col_vals[base + 5]))
            e_next = float(col_vals[base + 6])
            p_dies = max(0.0, float(col_vals[base + 7]))
            p_serv = max(0.0, float(col_vals[base + 8]))
            p_unm = max(0.0, float(col_vals[base + 9]))
            p_flx = max(0.0, float(col_vals[base + 10]))

            # Raw unrounded binary extraction (NO NORMALIZATION)
            u_chg = float(col_vals[base + 11])
            u_dis = float(col_vals[base + 12])
            u_diesel = float(col_vals[base + 13])
            v_start = float(col_vals[base + 14])

            s_j2_val = max(0.0, float(col_vals[idx_s_j2_start + t]))

            # Apply Research Numerical Boundary Extraction Protocol
            p_chg, p_dis, residue_corrected, zeroed_mag = extract_and_correct_flows(
                raw_p_chg, raw_p_dis, tau=self.tau
            )

            diag = {
                "t": t,
                "raw_p_chg": raw_p_chg,
                "raw_p_dis": raw_p_dis,
                "corrected_p_chg": p_chg,
                "corrected_p_dis": p_dis,
                "u_chg": u_chg,
                "u_dis": u_dis,
                "p_diesel": p_dies,
                "u_diesel": u_diesel,
                "v_start": v_start,
                "solver_status": str(model_status),
                "mip_gap": float(mip_gap),
                "residue_corrected": residue_corrected,
                "zeroed_magnitude_w": zeroed_mag,
            }
            diagnostics.append(diag)

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

        self.last_diagnostics = diagnostics

        J1_val = float(np.dot(c1, col_vals))
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
            objective_value=round(J3_val, 4),
            constraint_status="OPTIMAL",
            energy_balance_errors=energy_balance_errors,
            j1_objective=round(J1_val, 4),
            j2_objective=round(J2_val, 4),
            j3_objective=round(J3_val, 4),
            j4_objective=round(J4_val, 4),
            reserve_shortfall=reserve_shortfall
        )
