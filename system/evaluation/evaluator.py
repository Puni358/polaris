"""
EvaluationEngine Module
Decouples statistical forecasting evaluation from physical microgrid energy management evaluation.
"""
import math
import numpy as np
from typing import Dict, Any, List

from system.safety import reserve_policy_guard

class EvaluationEngine:
    @staticmethod
    def evaluate_forecasts(
        forecast_bundles: List[Dict[str, Any]],
        actual_scenarios: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Computes forecast accuracy metrics (MAE, RMSE, nMAE, Bias) for SW_IN irradiance and demand.
        NO MAPE used for solar irradiance.
        """
        sw_in_errors = []
        demand_errors = []
        sw_in_trues = []
        demand_trues = []

        for bundle, actuals in zip(forecast_bundles, actual_scenarios):
            pred_sw = bundle["solar_irradiance"]["point"]
            pred_dem = bundle["demand"]["point"]

            for p_sw, p_dem, act in zip(pred_sw, pred_dem, actuals):
                act_sw = act["actual_SW_IN"]
                act_dem = act["actual_demand"]

                sw_in_errors.append(p_sw - act_sw)
                demand_errors.append(p_dem - act_dem)
                sw_in_trues.append(act_sw)
                demand_trues.append(act_dem)

        sw_errs = np.array(sw_in_errors)
        dem_errs = np.array(demand_errors)
        sw_trues = np.array(sw_in_trues)
        dem_trues = np.array(demand_trues)

        sw_mae = float(np.mean(np.abs(sw_errs))) if len(sw_errs) > 0 else 0.0
        sw_rmse = float(np.sqrt(np.mean(sw_errs ** 2))) if len(sw_errs) > 0 else 0.0
        sw_nmae = float(sw_mae / np.max(sw_trues)) if np.max(sw_trues) > 0 else 0.0
        sw_bias = float(np.mean(sw_errs)) if len(sw_errs) > 0 else 0.0

        dem_mae = float(np.mean(np.abs(dem_errs))) if len(dem_errs) > 0 else 0.0
        dem_rmse = float(np.sqrt(np.mean(dem_errs ** 2))) if len(dem_errs) > 0 else 0.0
        dem_nmae = float(dem_mae / np.mean(dem_trues)) if np.mean(dem_trues) > 0 else 0.0
        dem_bias = float(np.mean(dem_errs)) if len(dem_errs) > 0 else 0.0

        return {
            "solar_irradiance_metrics": {
                "unit": "W/m^2",
                "mae": round(sw_mae, 4),
                "rmse": round(sw_rmse, 4),
                "nmae": round(sw_nmae, 4),
                "bias": round(sw_bias, 4)
            },
            "demand_metrics": {
                "unit": "W",
                "mae": round(dem_mae, 4),
                "rmse": round(dem_rmse, 4),
                "nmae": round(dem_nmae, 4),
                "bias": round(dem_bias, 4)
            }
        }

    @staticmethod
    def evaluate_ems_performance(
        dispatch_plans: List[Dict[str, Any]],
        station_configs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Computes physical microgrid performance metrics (fuel, renewable utilization, curtailment, battery throughput).
        """
        total_diesel_energy_wh = 0.0
        total_solar_used_wh = 0.0
        total_wind_used_wh = 0.0
        total_curtailment_wh = 0.0
        total_unmet_wh = 0.0
        total_demand_wh = 0.0
        total_battery_dis_wh = 0.0
        constraint_violations = 0

        diesel_cfg = station_configs.get("diesel", {})
        base_fuel_l_h = diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0)
        marg_fuel_l_wh = diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025)
        fuel_cost_per_l = diesel_cfg.get("fuel_cost_per_l", 2.50)
        startup_cost = diesel_cfg.get("startup_cost", 15.0)
        startup_fuel_l = startup_cost / fuel_cost_per_l if fuel_cost_per_l > 0 else 0.0

        total_fuel_l = 0.0
        battery_cap_wh = station_configs.get("battery", {}).get("capacity_wh", 200000.0)
        min_soc_pct_cfg = float(station_configs.get("battery", {}).get("min_soc_pct", 20.0))
        min_e_wh = battery_cap_wh * (min_soc_pct_cfg / 100.0)

        is_closed_loop_mpc = len(dispatch_plans) > 1
        was_running = False

        # --- Dispatch-safety guard aggregation (system/safety/reserve_policy_guard.py) ---
        # Additive, out-of-band. Does NOT change the computations above or the governed
        # reserve/GAP19 formulation. Evaluated over the SAME executed slice (H1-only for
        # closed-loop MPC, full 24h for a standalone plan) as the physical aggregation
        # above, so the safety totals below are on the same basis as total_unmet_wh etc.
        critical_unmet_total_wh = 0.0
        critical_unmet_sources = set()
        reserve_shortfall_total_wh = 0.0
        reserve_shortfall_present_any = False
        hard_soc_violation_any = False
        hard_soc_violation_details: List[str] = []
        solver_infeasible_step_count = 0
        optimal_but_unsafe_step_count = 0
        safety_failure_reasons_all: List[str] = []
        safety_notes_all: List[str] = []

        for plan in dispatch_plans:
            status = plan.get("constraint_status", "OPTIMAL")
            if status != "OPTIMAL":
                constraint_violations += 1

            s_used = plan["solar_used"]
            w_used = plan["wind_used"]
            d_pow = plan["diesel_power"]
            curt = plan["renewable_curtailment"]
            unmet = plan["unmet_load"]
            served = plan["load_served"]
            flex = plan.get("flexible_load_schedule", [0.0]*len(served))
            dis = plan["battery_discharge"]

            if is_closed_loop_mpc:
                # Closed-loop MPC: Evaluate ONLY the physically executed H1 action (index 0)
                time_slice = [(s_used[0], w_used[0], d_pow[0], curt[0], unmet[0], served[0], flex[0], dis[0])]
                exec_indices = [0]
            else:
                # Single standalone horizon plan: Evaluate all 24 planned hours
                time_slice = list(zip(s_used, w_used, d_pow, curt, unmet, served, flex, dis))
                exec_indices = list(range(len(unmet)))

            for s, w, d, c, u, l, f_load, b_dis in time_slice:
                total_solar_used_wh += s
                total_wind_used_wh += w
                total_diesel_energy_wh += d
                total_curtailment_wh += c
                total_unmet_wh += u
                total_demand_wh += (l + f_load + u)
                total_battery_dis_wh += b_dis

                if d > 0:
                    total_fuel_l += base_fuel_l_h + d * marg_fuel_l_wh
                    if not was_running:
                        total_fuel_l += startup_fuel_l
                    was_running = True
                else:
                    was_running = False

            # --- Per-plan dispatch-safety evaluation (same exec_indices slice) ---
            unmet_essential_full = plan.get("unmet_essential")
            reserve_shortfall_full = plan.get("reserve_shortfall")
            # NOTE: DispatchPlan.battery_soc is stored as a PERCENT (0-100), not Wh, (see
            # GAP19HighsNativeOptimizer: `soc_pct = (e_next / capacity_wh) * 100.0`).
            # reserve_policy_guard.validate_hard_soc_floor expects Wh (same unit as
            # min_e_wh), so it is converted here using the same battery.yaml
            # capacity_wh/min_soc_pct GAP19 itself reads -- never a new/invented value.
            battery_soc_full = plan.get("battery_soc")

            safety_plan = {
                "constraint_status": status,
                "unmet_load": [unmet[i] for i in exec_indices],
                "unmet_essential": (
                    [unmet_essential_full[i] for i in exec_indices]
                    if unmet_essential_full is not None else None
                ),
                "reserve_shortfall": (
                    [reserve_shortfall_full[i] for i in exec_indices]
                    if reserve_shortfall_full is not None else None
                ),
                "battery_soc": (
                    [(battery_soc_full[i] / 100.0) * battery_cap_wh for i in exec_indices]
                    if battery_soc_full is not None else None
                ),
            }

            safety_result = None
            try:
                safety_result = reserve_policy_guard.evaluate_dispatch_safety(
                    safety_plan,
                    min_e_wh=min_e_wh,
                    # AUTHORIZATION_REQUIRED: no numeric reserve-shortfall ceiling has
                    # been authorized by the project owner. Passing None here means the
                    # guard reports the shortfall for visibility without claiming a
                    # pass/fail verdict against an invented threshold.
                    reserve_shortfall_authorization_wh=None,
                )
            except reserve_policy_guard.ReservePolicyViolation as exc:
                # Hard SOC floor violated. The guard raises unconditionally for this
                # case (it is a physical constraint, not a policy judgment call); this
                # evaluator converts it into a visible, structured safety finding
                # instead of letting it crash the whole evaluation pass, per the
                # "do not suppress, reset, or overwrite findings" requirement.
                hard_soc_violation_any = True
                hard_soc_violation_details.append(str(exc))
                safety_failure_reasons_all.append(str(exc))

            if unmet_essential_full is not None:
                critical_unmet_sources.add("unmet_essential")
            elif plan.get("unmet_load") is not None:
                critical_unmet_sources.add("fallback_total_unmet_load")
            else:
                critical_unmet_sources.add("unavailable")

            if safety_result is not None:
                if safety_result.critical_unmet_total_wh is not None:
                    critical_unmet_total_wh += safety_result.critical_unmet_total_wh
                if reserve_shortfall_full is not None:
                    reserve_shortfall_present_any = True
                    reserve_shortfall_total_wh += safety_result.reserve_shortfall_total_wh
                if safety_result.solver_infeasible:
                    solver_infeasible_step_count += 1
                if safety_result.hard_soc_violation:
                    hard_soc_violation_any = True
                safety_failure_reasons_all.extend(safety_result.failure_reasons)
                safety_notes_all.extend(safety_result.notes)
                if status == "OPTIMAL" and safety_result.failure_reasons:
                    # Protocol item 6: OPTIMAL alone must never be read as safe/successful
                    # when critical load was unmet, reserve was short, or SOC floor broke.
                    optimal_but_unsafe_step_count += 1

        total_renewables_used_wh = total_solar_used_wh + total_wind_used_wh
        total_renewables_avail_wh = total_renewables_used_wh + total_curtailment_wh
        renewable_utilization_pct = (total_renewables_used_wh / total_renewables_avail_wh * 100.0) if total_renewables_avail_wh > 0 else 0.0
        renewable_curtailment_pct = (total_curtailment_wh / total_renewables_avail_wh * 100.0) if total_renewables_avail_wh > 0 else 0.0

        reliability_pct = ((total_demand_wh - total_unmet_wh) / total_demand_wh * 100.0) if total_demand_wh > 0 else 100.0
        battery_equivalent_cycles = total_battery_dis_wh / battery_cap_wh

        # --- Resolve the critical-vs-total unmet-load labeling (protocol item 3) ---
        if critical_unmet_sources == {"unavailable"}:
            critical_unmet_total_wh_reported = "UNKNOWN_NOT_VERIFIED"
            critical_unmet_source_label = (
                "UNAVAILABLE: neither 'unmet_essential' nor 'unmet_load' present on any dispatch plan."
            )
        elif critical_unmet_sources == {"unmet_essential"}:
            critical_unmet_total_wh_reported = round(critical_unmet_total_wh, 2)
            critical_unmet_source_label = "unmet_essential (critical-specific field, verified)."
        else:
            # At least one plan lacked 'unmet_essential' and fell back to total unmet_load.
            critical_unmet_total_wh_reported = round(critical_unmet_total_wh, 2)
            critical_unmet_source_label = (
                "FALLBACK_TO_TOTAL_UNMET_LOAD: 'unmet_essential' was not present on one or more "
                "dispatch plans. This value OVER-COUNTS non-critical shortfall and must NOT be read "
                "as critical-only. See forecasting/n6/reports/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md Section 4 / "
                "SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md."
            )

        reserve_shortfall_total_wh_reported = (
            round(reserve_shortfall_total_wh, 2) if reserve_shortfall_present_any else "UNKNOWN_NOT_VERIFIED"
        )

        dispatch_safety = {
            "min_e_wh_used_for_hard_soc_check": round(min_e_wh, 2),
            "min_soc_pct_used_for_hard_soc_check": min_soc_pct_cfg,
            "hard_soc_violation": hard_soc_violation_any,
            "hard_soc_violation_details": hard_soc_violation_details,
            "solver_infeasible_step_count": solver_infeasible_step_count,
            "critical_unmet_total_wh": critical_unmet_total_wh_reported,
            "critical_unmet_source": critical_unmet_source_label,
            "reserve_shortfall_total_wh": reserve_shortfall_total_wh_reported,
            "reserve_shortfall_authorization_wh": None,
            "reserve_shortfall_authorization_status": (
                "AUTHORIZATION_REQUIRED: no numeric reserve-shortfall ceiling has been authorized by "
                "the project owner. The measured shortfall above is reported for visibility only and "
                "must not be read as a pass/fail verdict."
            ),
            "optimal_but_unsafe_step_count": optimal_but_unsafe_step_count,
            "failure_reasons": safety_failure_reasons_all,
            "notes": safety_notes_all,
            "proposed_safety_gate_would_pass": not safety_failure_reasons_all,
            "safety_gate_formally_authorized": False,
        }

        return {
            "total_diesel_fuel_liters": round(total_fuel_l, 2),
            "total_diesel_energy_kwh": round(total_diesel_energy_wh / 1000.0, 2),
            "total_renewable_energy_used_kwh": round(total_renewables_used_wh / 1000.0, 2),
            "total_renewable_curtailment_kwh": round(total_curtailment_wh / 1000.0, 2),
            "renewable_utilization_pct": round(renewable_utilization_pct, 2),
            "renewable_curtailment_pct": round(renewable_curtailment_pct, 2),
            "battery_throughput_kwh": round(total_battery_dis_wh / 1000.0, 2),
            "battery_equivalent_cycles": round(battery_equivalent_cycles, 4),
            # DEPRECATED LABEL (kept unchanged for backward compatibility): this field is
            # actually computed from TOTAL unmet_load, not critical-specific unmet load.
            # Use "total_unmet_load_kwh" (same value, correctly named) and
            # "dispatch_safety.critical_unmet_total_wh" / "critical_unmet_source" for the
            # correctly-scoped, source-tagged critical-load metric.
            "unmet_critical_load_kwh": round(total_unmet_wh / 1000.0, 2),
            "unmet_critical_load_kwh_label_warning": (
                "This field name is historically mislabeled: it is TOTAL unmet load (unmet_load), "
                "not critical-specific unmet load. Retained unchanged for backward compatibility. "
                "See 'dispatch_safety.critical_unmet_total_wh' / 'critical_unmet_source' instead."
            ),
            "total_unmet_load_kwh": round(total_unmet_wh / 1000.0, 2),
            "system_reliability_pct": round(reliability_pct, 2),
            "constraint_violations_count": constraint_violations,
            "dispatch_safety": dispatch_safety
        }
