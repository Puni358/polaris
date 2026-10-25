"""
Local MILP EnergyOptimizer Implementation for POLARIS Phase D2
Receding-horizon mathematical optimization using Scipy HiGHS solver.
Formulates exact Mixed-Integer Linear Program (MILP) with continuous power/energy decision variables
and binary commitment/startup variables for battery exclusivity and diesel generator operation.
"""
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy.optimize import milp, LinearConstraint, Bounds

from system.optimization.interface.base import EnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

class LocalMILPEnergyOptimizer(EnergyOptimizer):
    def optimize(
        self,
        forecast_bundle: ForecastBundle,
        station_state: StationState,
        config: Dict[str, Any]
    ) -> DispatchPlan:
        
        # Load physical configurations
        bat_cfg = config.get("battery", {})
        capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
        min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))
        max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
        eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
        eta_dis = float(bat_cfg.get("discharge_efficiency", 0.92))
        max_p_chg = float(bat_cfg.get("max_charge_power_w", 50000.0))
        max_p_dis = float(bat_cfg.get("max_discharge_power_w", 50000.0))
        deg_penalty = float(bat_cfg.get("deg_penalty_per_wh", 0.00005))

        min_e_wh = capacity_wh * (min_soc_pct / 100.0)
        max_e_wh = capacity_wh * (max_soc_pct / 100.0)
        initial_e_wh = max(min_e_wh, min(max_e_wh, station_state.battery_energy_wh))

        diesel_cfg = config.get("diesel", {})
        min_diesel_w = float(diesel_cfg.get("min_power_w", 10000.0))
        max_diesel_w = float(diesel_cfg.get("max_power_w", 100000.0))
        base_fuel_l_h = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
        marg_fuel_l_wh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))
        fuel_cost_per_l = float(diesel_cfg.get("fuel_cost_per_l", 2.50))
        startup_cost = float(diesel_cfg.get("startup_cost", 15.0))
        initial_diesel_running = 1 if station_state.diesel_running else 0

        current_fuel_l = station_state.diesel_fuel_remaining_liters
        if current_fuel_l is None:
            current_fuel_l = float(diesel_cfg.get("initial_fuel_l", 100.0))

        loads_cfg = config.get("loads", {})
        unmet_penalty_per_wh = float(loads_cfg.get("critical_load", {}).get("unmet_penalty_per_wh", 10.0))
        curt_penalty_per_wh = float(config.get("optimizer", {}).get("weights", {}).get("renewable_curtailment_penalty", 0.001))

        # Check flexible loads configuration
        deferrable_list = loads_cfg.get("deferrable_loads", [])
        has_flexible_load = len(deferrable_list) > 0
        flex_power_w = 0.0
        flex_total_wh = 0.0
        flex_start_h = 0
        flex_finish_h = 24
        if has_flexible_load:
            def_item = deferrable_list[0]
            flex_power_w = float(def_item.get("power_w", 10000.0))
            flex_duration_h = float(def_item.get("duration_hours", 4))
            flex_total_wh = flex_power_w * flex_duration_h
            flex_start_h = int(def_item.get("earliest_start_h", 8))
            flex_finish_h = int(def_item.get("latest_finish_h", 18))

        timestamps = forecast_bundle.timestamps
        solar_gen = forecast_bundle.solar_generation.point
        wind_gen = forecast_bundle.wind_generation.point
        demand = forecast_bundle.demand.point

        H = 24 # Horizon hours
        K = 15 # Number of decision variables per timestep

        # Index mapping per timestep t:
        # 0: p_sol_used, 1: p_wind_used, 2: p_curt_sol, 3: p_curt_wind
        # 4: p_chg, 5: p_dis, 6: E_next, 7: p_diesel, 8: p_served, 9: p_unmet, 10: p_flex
        # 11: u_chg (bin), 12: u_dis (bin), 13: u_diesel (bin), 14: v_start (bin)

        # --- RT-01 Stage 1: cross-horizon soft reservation mechanism ---------------
        # Two additional CONTINUOUS slack variables are appended after the existing
        # H*K=360 base block (num_base_vars..num_base_vars+1). Per
        # ems/reports/rt01_runtime_fixes/RT01_CROSS_HORIZON_RESERVATION_DESIGN_MEMO.md Sec.2 (Candidate 4, Stage 1
        # only -- the static, config-driven skeleton; Stage 2's forecast-outlook
        # trigger via ForecastBundle.metadata is explicitly NOT implemented here):
        #   idx_s_term -> s_term (Wh): soft shortfall slack for a terminal
        #                 battery-energy reservation target on E[H-1].
        #   idx_s_fuel -> s_fuel (L):  soft shortfall slack for a horizon-
        #                 cumulative fuel-reserve preference.
        # Both terms are purely additive/soft: every existing hard constraint
        # (including the hard SOC floor lb[E]=min_e_wh and the hard cumulative
        # fuel-budget cap <= current_fuel_l, both unmodified below) keeps exactly
        # today's feasible region. A trivial all-slack solution always exists
        # whenever today's problem is feasible, so this mechanism can never, by
        # itself, cause OPTIMIZATION_INFEASIBLE.
        num_base_vars = H * K
        idx_s_term = num_base_vars       # s_term (Wh), continuous, >= 0
        idx_s_fuel = num_base_vars + 1   # s_fuel (L), continuous, >= 0
        num_vars = num_base_vars + 2

        opt_cfg_top = config.get("optimizer", {})
        reservation_cfg = opt_cfg_top.get("reservation", {})
        opt_weights_cfg = opt_cfg_top.get("weights", {})
        reserve_shortfall_penalty = float(opt_weights_cfg.get("reserve_shortfall_penalty", 0.0))
        terminal_target_soc_pct = float(reservation_cfg.get("terminal_target_soc_pct", min_soc_pct))
        fuel_reserve_target_l = float(reservation_cfg.get("fuel_reserve_target_l", 0.0))
        # Static Stage-1 terminal-energy target, capped to [min_e_wh, max_e_wh]
        # exactly like every other battery-energy bound in this formulation.
        # Stage 1 computes this ONCE, identically on every receding-horizon call
        # (no forecast-outlook signal is read).
        e_term_target_wh_static = min(max_e_wh, max(min_e_wh, capacity_wh * (terminal_target_soc_pct / 100.0)))
        fuel_reserve_target_l_static = max(0.0, fuel_reserve_target_l)

        # --- RT-01 Stage 2: genuine forecast-outlook trigger ----------------
        # Per ems/reports/rt01_runtime_fixes/RT01_CROSS_HORIZON_RESERVATION_DESIGN_MEMO.md Sec.2 (Candidate 4,
        # Stage 2). Read `forecast_bundle.metadata["extended_outlook"]`
        # DEFENSIVELY (getattr/.get chains, default None) -- fully
        # backward-compatible with every existing test, the rule-based/
        # reactive-A2 optimizers, and any ForecastBundle that never populates
        # this free-form, unvalidated metadata key. When absent or disabled,
        # this entire block is a no-op and Stage 1's static behavior (above)
        # is exactly preserved.
        #
        # The resulting target is the ELEMENTWISE MAXIMUM of the static Stage-1
        # target and the outlook-driven target -- never a reduction below
        # whatever static floor the operator configured. Both are still soft
        # (slack-penalized via s_term/s_fuel below); the hard SOC floor/ceiling
        # and hard fuel cap are completely unaffected by this block.
        outlook_cfg = reservation_cfg.get("outlook_trigger", {})
        outlook_enabled = bool(outlook_cfg.get("enabled", False))
        outlook_min_confidence = float(outlook_cfg.get("min_confidence", 0.3))
        outlook_max_lookahead_h = float(outlook_cfg.get("max_lookahead_h", 72.0))
        outlook_deficit_threshold_wh = abs(float(outlook_cfg.get("deficit_threshold_wh", 0.0)))
        outlook_term_target_scale = float(outlook_cfg.get("term_target_scale", 1.0))
        outlook_fuel_target_scale_l_per_wh = float(
            outlook_cfg.get("fuel_target_scale_l_per_wh", marg_fuel_l_wh)
        )

        extended_outlook = None
        try:
            md = getattr(forecast_bundle, "metadata", None)
            if isinstance(md, dict):
                extended_outlook = md.get("extended_outlook")
        except Exception:
            extended_outlook = None

        outlook_triggered = False
        e_term_target_wh_outlook = min_e_wh
        fuel_reserve_target_l_outlook = 0.0
        if outlook_enabled and isinstance(extended_outlook, dict):
            try:
                outlook_lookahead_h = float(extended_outlook.get("lookahead_h", 0.0))
                outlook_confidence = float(extended_outlook.get("confidence", 0.0))
                outlook_projected_margin_wh = float(
                    extended_outlook.get("projected_min_net_renewable_margin_wh", 0.0)
                )
            except (TypeError, ValueError):
                outlook_lookahead_h, outlook_confidence, outlook_projected_margin_wh = 0.0, 0.0, 0.0

            if (
                outlook_lookahead_h > 0.0
                and outlook_lookahead_h <= outlook_max_lookahead_h
                and outlook_confidence >= outlook_min_confidence
                and outlook_projected_margin_wh < -outlook_deficit_threshold_wh
            ):
                outlook_triggered = True
                deficit_wh = -outlook_projected_margin_wh
                confidence_discounted_deficit_wh = deficit_wh * outlook_confidence
                e_term_target_wh_outlook = min(
                    max_e_wh,
                    max(min_e_wh, min_e_wh + confidence_discounted_deficit_wh * outlook_term_target_scale),
                )
                fuel_reserve_target_l_outlook = max(
                    0.0, confidence_discounted_deficit_wh * outlook_fuel_target_scale_l_per_wh
                )

        e_term_target_wh = max(e_term_target_wh_static, e_term_target_wh_outlook)
        fuel_reserve_target_l = max(fuel_reserve_target_l_static, fuel_reserve_target_l_outlook)
        # --- END RT-01 Stage 2 forecast-outlook trigger -----------------------

        c = np.zeros(num_vars)
        integrality = np.zeros(num_vars, dtype=int)
        lb = np.zeros(num_vars)
        ub = np.zeros(num_vars)

        for t in range(H):
            base = t * K
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_dem = max(0.0, demand[t])

            # Objective coefficients accumulated over timestep dt
            dt = float(config.get("optimizer", {}).get("timestep_hours", 1.0))

            # Horizon Weighting: Baseline (gamma=1.0), Class F (gamma=0.95), V4.G Single-Horizon Mode (t=13 -> w_13=0.5133), or Custom Weight Vector (OFAT)
            opt_cfg = config.get("optimizer", {})
            if "custom_weight_vector" in opt_cfg and opt_cfg["custom_weight_vector"] is not None:
                w_t = float(opt_cfg["custom_weight_vector"][t])
            elif opt_cfg.get("v4g_single_horizon_mode", False):
                t_target = int(opt_cfg.get("v4g_target_index", 13))
                w_target = float(opt_cfg.get("v4g_weight", 0.5133))
                w_t = w_target if t == t_target else 1.0
            else:
                gamma = float(opt_cfg.get("horizon_discount_factor_gamma", 1.0))
                w_t = gamma ** t

            c[base + 2] = curt_penalty_per_wh * dt * w_t  # p_curt_sol ($/Wh * W * h)
            c[base + 3] = curt_penalty_per_wh * dt * w_t  # p_curt_wind ($/Wh * W * h)
            c[base + 4] = deg_penalty * dt * w_t         # p_chg ($/Wh * W * h)
            c[base + 5] = deg_penalty * dt * w_t         # p_dis ($/Wh * W * h)
            c[base + 7] = fuel_cost_per_l * marg_fuel_l_wh * dt * w_t  # p_diesel ($/L * L/Wh * W * h)
            # p_unmet ($/Wh * W * h) -- base rate UNWEIGHTED (gamma^t does
            # NOT apply here; this intentionally stays dominant and uniform
            # in order of magnitude). A strictly-decreasing-in-t epsilon tie-
            # break is layered on top (ems/reports/rt01_runtime_fixes/S81_24H_REGRESSION_FIX_REPORT.md):
            # without it, this horizon-wide MILP is cost-indifferent to
            # WHICH relative timestep bears an otherwise-unavoidable unmet
            # amount within a single 24-step solve (u_chg/u_dis themselves
            # carry no objective cost, and gamma=1.0 by default here), so
            # HiGHS can legally park unmet at rel_t=0 -- the one relative
            # step runner.py actually executes each receding-horizon call
            # (system/simulation/simulator.py only consumes index 0) -- even
            # though resources to serve it exist, because an equally-optimal
            # solution leaves the same total unmet at a later, never-
            # executed relative step instead. near_term_priority_eps is set
            # far below the smallest real cost ratio in this objective
            # (curtailment/diesel/degradation vs. unmet_penalty_per_wh), so
            # it cannot change which TOTAL unmet amount is optimal or
            # relax/weaken the unmet penalty anywhere -- it only breaks ties
            # among equal-total-unmet optima toward serving the step that is
            # actually executed first.
            near_term_priority_eps = 1e-6
            c[base + 9] = unmet_penalty_per_wh * dt * (1.0 + near_term_priority_eps * (H - 1 - t))
            c[base + 13] = fuel_cost_per_l * base_fuel_l_h * dt * w_t  # u_diesel ($/L * L/h * 1 * h)
            c[base + 14] = startup_cost * w_t             # v_start ($ * 1)

            # Bounds
            lb[base + 0], ub[base + 0] = 0.0, p_sol_max
            lb[base + 1], ub[base + 1] = 0.0, p_wind_max
            lb[base + 2], ub[base + 2] = 0.0, p_sol_max
            lb[base + 3], ub[base + 3] = 0.0, p_wind_max
            lb[base + 4], ub[base + 4] = 0.0, max_p_chg
            lb[base + 5], ub[base + 5] = 0.0, max_p_dis
            lb[base + 6], ub[base + 6] = min_e_wh, max_e_wh
            lb[base + 7], ub[base + 7] = 0.0, max_diesel_w
            lb[base + 8], ub[base + 8] = 0.0, p_dem
            lb[base + 9], ub[base + 9] = 0.0, p_dem
            
            if has_flexible_load and flex_start_h <= t < flex_finish_h:
                lb[base + 10], ub[base + 10] = 0.0, flex_power_w
            else:
                lb[base + 10], ub[base + 10] = 0.0, 0.0

            # Binary variables
            lb[base + 11], ub[base + 11] = 0.0, 1.0
            lb[base + 12], ub[base + 12] = 0.0, 1.0
            lb[base + 13], ub[base + 13] = 0.0, 1.0
            lb[base + 14], ub[base + 14] = 0.0, 1.0

            integrality[base + 11] = 1 # u_chg
            integrality[base + 12] = 1 # u_dis
            integrality[base + 13] = 1 # u_diesel
            integrality[base + 14] = 1 # v_start

        # RT-01 Stage 1 reservation slack variable bounds/objective coefficients.
        # Continuous, non-negative, unbounded above (no upper bound restricts how
        # large a priced shortfall can be -- these are SOFT terms, never hard
        # bounds, so they can never themselves restrict feasibility).
        lb[idx_s_term], ub[idx_s_term] = 0.0, np.inf
        lb[idx_s_fuel], ub[idx_s_fuel] = 0.0, np.inf
        # integrality[idx_s_term]/[idx_s_fuel] already 0 (continuous) -- the
        # integrality array is zero-initialized above and never set for these.
        c[idx_s_term] = reserve_shortfall_penalty  # $ per Wh terminal-energy shortfall
        # s_fuel is denominated in liters; translate the same per-Wh price into a
        # per-liter price via the diesel marginal fuel-to-energy ratio so both
        # slacks are priced on a consistent, explainable basis (documented in
        # ems/reports/rt01_runtime_fixes/RT01_CROSS_HORIZON_RESERVATION_DESIGN_MEMO.md Sec.2: "priced similarly").
        fuel_shortfall_price_per_l = (
            reserve_shortfall_penalty / marg_fuel_l_wh if marg_fuel_l_wh > 1e-12 else reserve_shortfall_penalty
        )
        c[idx_s_fuel] = fuel_shortfall_price_per_l
        # Neither new term is weighted by the per-timestep horizon-discount w_t:
        # both rows are horizon-level (one terminal state, one cumulative-fuel
        # aggregate), not per-timestep flows, so a per-t decay factor does not
        # apply to them.

        # Constraints construction
        A_rows = []
        lhs = []
        rhs = []

        for t in range(H):
            base = t * K
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_dem = max(0.0, demand[t])

            # 1. Solar Decomposition: p_sol_used + p_curt_sol == p_solar_gen
            row = np.zeros(num_vars)
            row[base + 0] = 1.0
            row[base + 2] = 1.0
            A_rows.append(row)
            lhs.append(p_sol_max)
            rhs.append(p_sol_max)

            # 2. Wind Decomposition: p_wind_used + p_curt_wind == p_wind_gen
            row = np.zeros(num_vars)
            row[base + 1] = 1.0
            row[base + 3] = 1.0
            A_rows.append(row)
            lhs.append(p_wind_max)
            rhs.append(p_wind_max)

            # 3. Bus-Bar Balance: p_sol_used + p_wind_used + p_dis + p_diesel - p_served - p_chg - p_flex == 0
            row = np.zeros(num_vars)
            row[base + 0] = 1.0
            row[base + 1] = 1.0
            row[base + 5] = 1.0 # p_dis
            row[base + 7] = 1.0 # p_diesel
            row[base + 8] = -1.0 # p_served
            row[base + 4] = -1.0 # p_chg
            row[base + 10] = -1.0 # p_flex
            A_rows.append(row)
            lhs.append(0.0)
            rhs.append(0.0)

            # 4. Demand Deficit Balance: p_served + p_unmet == p_demand
            row = np.zeros(num_vars)
            row[base + 8] = 1.0
            row[base + 9] = 1.0
            A_rows.append(row)
            lhs.append(p_dem)
            rhs.append(p_dem)

            # 5. Charge Bound vs Binary: p_chg - max_p_chg * u_chg <= 0
            row = np.zeros(num_vars)
            row[base + 4] = 1.0
            row[base + 11] = -max_p_chg
            A_rows.append(row)
            lhs.append(-np.inf)
            rhs.append(0.0)

            # 6. Discharge Bound vs Binary: p_dis - max_p_dis * u_dis <= 0
            row = np.zeros(num_vars)
            row[base + 5] = 1.0
            row[base + 12] = -max_p_dis
            A_rows.append(row)
            lhs.append(-np.inf)
            rhs.append(0.0)

            # 7. Charge/Discharge Exclusivity: u_chg + u_dis <= 1
            row = np.zeros(num_vars)
            row[base + 11] = 1.0
            row[base + 12] = 1.0
            A_rows.append(row)
            lhs.append(-np.inf)
            rhs.append(1.0)

            # 8. Battery Energy Discrete Transition: E[t+1] - E[t] - eta_chg * p_chg * dt + (p_dis / eta_dis) * dt == 0
            dt = float(config.get("optimizer", {}).get("timestep_hours", 1.0))
            row = np.zeros(num_vars)
            row[base + 6] = 1.0 # E[t+1]
            if t == 0:
                row[base + 4] = -eta_chg * dt
                row[base + 5] = dt / eta_dis
                A_rows.append(row)
                lhs.append(initial_e_wh)
                rhs.append(initial_e_wh)
            else:
                prev_base = (t - 1) * K
                row[prev_base + 6] = -1.0 # E[t]
                row[base + 4] = -eta_chg * dt
                row[base + 5] = dt / eta_dis
                A_rows.append(row)
                lhs.append(0.0)
                rhs.append(0.0)

            # 9. Diesel Min Output when Running: p_diesel - min_diesel_w * u_diesel >= 0
            row = np.zeros(num_vars)
            row[base + 7] = 1.0
            row[base + 13] = -min_diesel_w
            A_rows.append(row)
            lhs.append(0.0)
            rhs.append(np.inf)

            # 10. Diesel Max Output when Running: p_diesel - max_diesel_w * u_diesel <= 0
            row = np.zeros(num_vars)
            row[base + 7] = 1.0
            row[base + 13] = -max_diesel_w
            A_rows.append(row)
            lhs.append(-np.inf)
            rhs.append(0.0)

            # 11. Diesel Startup Tracking: v_start[t] - u_diesel[t] + u_diesel[t-1] >= 0
            row = np.zeros(num_vars)
            row[base + 14] = 1.0 # v_start[t]
            row[base + 13] = -1.0 # u_diesel[t]
            if t == 0:
                A_rows.append(row)
                lhs.append(-initial_diesel_running)
                rhs.append(np.inf)
            else:
                prev_base = (t - 1) * K
                row[prev_base + 13] = 1.0 # u_diesel[t-1]
                A_rows.append(row)
                lhs.append(0.0)
                rhs.append(np.inf)

        # Diesel Cumulative Fuel Budget Constraint: sum(marg_fuel_l_wh*dt*p_diesel[t] + base_fuel_l_h*dt*u_diesel[t]) <= current_fuel_l
        row = np.zeros(num_vars)
        dt = float(config.get("optimizer", {}).get("timestep_hours", 1.0))
        for t in range(H):
            base = t * K
            row[base + 7] = marg_fuel_l_wh * dt   # p_diesel
            row[base + 13] = base_fuel_l_h * dt   # u_diesel
        A_rows.append(row)
        lhs.append(-np.inf)
        rhs.append(current_fuel_l)
        # --- END hard cumulative fuel-budget constraint (UNMODIFIED above) ---

        # --- RT-01 Stage 1 soft row A: terminal battery-energy reservation ---
        # E[H-1] + s_term >= e_term_target_wh (soft -- shortfall priced via
        # s_term's objective coefficient above, never forbidden). The existing
        # hard SOC floor lb[E]=min_e_wh (applied to every E[t] including
        # E[H-1] via the bounds array set earlier) is completely unmodified;
        # this is a strictly additive row with its own new column.
        last_base = (H - 1) * K
        row = np.zeros(num_vars)
        row[last_base + 6] = 1.0   # E[H-1] (terminal battery energy this horizon)
        row[idx_s_term] = 1.0
        A_rows.append(row)
        lhs.append(e_term_target_wh)
        rhs.append(np.inf)

        # --- RT-01 Stage 1 soft row B: fuel-reserve preference ---
        # Prefers cumulative diesel use stay below (current_fuel_l -
        # fuel_reserve_target_l); soft via s_fuel. Uses the SAME marg/base fuel
        # coefficients as the hard row above, but is an independent additional
        # row with a reduced RHS and its own slack column -- the hard row
        # itself (<= current_fuel_l) is untouched.
        row = np.zeros(num_vars)
        for t in range(H):
            base = t * K
            row[base + 7] = marg_fuel_l_wh * dt   # p_diesel
            row[base + 13] = base_fuel_l_h * dt   # u_diesel
        row[idx_s_fuel] = -1.0
        A_rows.append(row)
        lhs.append(-np.inf)
        rhs.append(current_fuel_l - fuel_reserve_target_l)

        # 12. Flexible Load Total Requirement Constraint (if active)
        if has_flexible_load and flex_total_wh > 0:
            row = np.zeros(num_vars)
            for t in range(flex_start_h, flex_finish_h):
                base = t * K
                row[base + 10] = 1.0 # p_flex
            A_rows.append(row)
            lhs.append(flex_total_wh)
            rhs.append(flex_total_wh)

        A = np.array(A_rows)
        constraints = LinearConstraint(A, lhs, rhs)
        bounds = Bounds(lb, ub)

        # Solve MILP using HiGHS C++ solver.
        # mip_rel_gap is tightened from scipy's default (1e-4) to 1e-9
        # (ems/reports/rt01_runtime_fixes/S81_24H_REGRESSION_FIX_REPORT.md root cause). At the default gap,
        # HiGHS is permitted to report "Optimal" on any incumbent within
        # 0.01% of the dual bound; on this objective's scale (critical-load
        # unmet priced at unmet_penalty_per_wh -- tens to hundreds of
        # thousands across a 24-step horizon), that 0.01% slack is large
        # enough in absolute terms to leave an entire real unmet-load event
        # unaddressed at rel_t=0 -- the one relative timestep this
        # receding-horizon call's output actually executes
        # (system/simulation/simulator.py only consumes index 0 each call)
        # -- while reporting constraint_status="OPTIMAL". This was verified
        # directly: re-solving the identical problem with unmet[0] forced to
        # 0 remains feasible and yields a strictly lower true objective than
        # the default-gap "optimal" result. Tightening the gap makes HiGHS
        # prove genuine near-global optimality instead, which removes the
        # false OPTIMAL-with-avoidable-unmet outcome without touching any
        # cost weight, constraint, or the unmet penalty itself.
        try:
            res = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints,
                       options={"mip_rel_gap": 1e-9})
        except Exception as e:
            raise RuntimeError(f"OPTIMIZATION_RUNTIME_FAILURE: Solver exception encountered during optimization: {e}")

        if not res.success or res.x is None:
            # Check if genuine mathematical infeasibility vs solver runtime failure
            # status == 2 in scipy.optimize.milp / HiGHS represents INFEASIBLE
            # If status indicates infeasibility, return governed zero-dispatch degraded plan
            if res.status == 2 or "infeasible" in str(res.message).lower() or res.status != 0:
                return DispatchPlan(
                    schema_version="1.0.0",
                    timestamps=timestamps,
                    solar_used=[0.0]*24,
                    wind_used=[0.0]*24,
                    battery_charge=[0.0]*24,
                    battery_discharge=[0.0]*24,
                    battery_soc=[0.0]*24,
                    diesel_power=[0.0]*24,
                    load_served=[0.0]*24,
                    flexible_load_schedule=[0.0]*24,
                    renewable_curtailment=[0.0]*24,
                    unmet_load=demand,
                    objective_value=1e9,
                    constraint_status=f"OPTIMIZATION_INFEASIBLE: {res.message}",
                    energy_balance_errors=[0.0]*24,
                    reserve_shortfall=[0.0]*24,
                    reservation_target_wh=[0.0]*24,
                    outlook_triggered_flag=[0.0]*24
                )
            else:
                raise RuntimeError(f"OPTIMIZATION_RUNTIME_FAILURE: Solver failed with status code {res.status}: {res.message}")

        sol = res.x

        # Post-solve binary snapping: HiGHS returns binary decision variables
        # (u_chg, u_dis, u_diesel, v_start) within its integrality tolerance of
        # 0/1 (e.g. 7.8e-7), not exactly 0/1. Left as-is, a near-zero u_chg still
        # satisfies constraint 5 (p_chg <= max_p_chg * u_chg) with a tiny nonzero
        # p_chg (e.g. 0.039W), which can trip DispatchPlan's charge/discharge
        # exclusivity check if p_dis is simultaneously nonzero. Snap each binary
        # to the nearest of {0, 1} and, when it snaps to 0, zero its continuous
        # companion exactly so the bound it governs is actually enforced.
        for t in range(H):
            base = t * K
            u_chg = 1.0 if sol[base + 11] >= 0.5 else 0.0
            u_dis = 1.0 if sol[base + 12] >= 0.5 else 0.0
            u_diesel = 1.0 if sol[base + 13] >= 0.5 else 0.0
            v_start = 1.0 if sol[base + 14] >= 0.5 else 0.0
            sol[base + 11] = u_chg
            sol[base + 12] = u_dis
            sol[base + 13] = u_diesel
            sol[base + 14] = v_start
            if u_chg == 0.0:
                sol[base + 4] = 0.0  # p_chg
            if u_dis == 0.0:
                sol[base + 5] = 0.0  # p_dis
            if u_diesel == 0.0:
                sol[base + 7] = 0.0  # p_diesel

        # Extract output vectors
        solar_used = []
        wind_used = []
        battery_charge = []
        battery_discharge = []
        battery_soc = []
        diesel_power = []
        load_served = []
        flexible_load_schedule = []
        renewable_curtailment = []
        unmet_load = []
        energy_balance_errors = []

        for t in range(H):
            base = t * K
            p_sol_u = max(0.0, float(sol[base + 0]))
            p_w_u = max(0.0, float(sol[base + 1]))
            p_c_sol = max(0.0, float(sol[base + 2]))
            p_c_w = max(0.0, float(sol[base + 3]))
            p_chg = max(0.0, float(sol[base + 4]))
            p_dis = max(0.0, float(sol[base + 5]))
            e_next = float(sol[base + 6])
            p_dies = max(0.0, float(sol[base + 7]))
            p_serv = max(0.0, float(sol[base + 8]))
            p_unm = max(0.0, float(sol[base + 9]))
            p_flx = max(0.0, float(sol[base + 10]))

            soc_pct = (e_next / capacity_wh) * 100.0
            p_curt_tot = p_c_sol + p_c_w

            # Verification of exact energy balance
            bus_err = abs((p_sol_u + p_w_u + p_dis + p_dies) - (p_serv + p_chg + p_flx))
            dem_err = abs(demand[t] - (p_serv + p_unm))
            ren_err = abs((solar_gen[t] + wind_gen[t]) - (p_sol_u + p_w_u + p_curt_tot))
            err = max(bus_err, dem_err, ren_err)

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

        # RT-01 Stage 1: surface the reservation shortfall explicitly, never
        # silently absorb it. s_term (terminal-energy shortfall, Wh) and s_fuel
        # (fuel-reserve shortfall, L -- converted to a Wh-equivalent using the
        # same marg_fuel_l_wh ratio used to price it above) are summed into a
        # single horizon-level figure, surfaced at index H-1 (the terminal
        # index both soft rows are about). All other indices are 0.0, which is
        # correct (neither soft row is per-timestep) -- not a hidden omission.
        s_term_val = max(0.0, float(sol[idx_s_term]))
        s_fuel_val_l = max(0.0, float(sol[idx_s_fuel]))
        s_fuel_val_wh_equiv = (s_fuel_val_l / marg_fuel_l_wh) if marg_fuel_l_wh > 1e-12 else s_fuel_val_l
        reserve_shortfall = [0.0] * 24
        reserve_shortfall[H - 1] = round(s_term_val + s_fuel_val_wh_equiv, 2)

        # RT-01 Stage 2 diagnostics -- surfaced the same way reserve_shortfall
        # is (index H-1 only; both terms are horizon-level, not per-timestep).
        # Research-only, additive, optional; never consumed by any protected
        # file or existing production logic.
        reservation_target_wh = [0.0] * 24
        reservation_target_wh[H - 1] = round(e_term_target_wh, 2)
        outlook_triggered_flag = [0.0] * 24
        outlook_triggered_flag[H - 1] = 1.0 if outlook_triggered else 0.0

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
            objective_value=round(float(res.fun), 2),
            constraint_status="OPTIMAL",
            energy_balance_errors=energy_balance_errors,
            reserve_shortfall=reserve_shortfall,
            reservation_target_wh=reservation_target_wh,
            outlook_triggered_flag=outlook_triggered_flag
        )
