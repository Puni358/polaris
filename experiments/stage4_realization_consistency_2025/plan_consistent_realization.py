"""
Plan-Consistent Diagnostic Realization Semantics (Arm B)
Module: experiments.stage4_realization_consistency_2025.plan_consistent_realization

Governing Contract:
  experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md (§2.2, §14.1)
  experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.json

Realization order per step:
  1. Critical load served from realized supply: s_c = min(D_c, S_avail)
  2. Planned battery charge realized:
     C = min(P_c, max(0, S_avail - s_c), 50,000 W, max(0, max_e - E) / eta_c) (if not discharging)
  3. Planned flexible load realized as sink:
     F = min(P_f, max(0, S_avail - s_c - C))
  4. Non-critical load served from residual supply:
     n = min(D - D_c, max(0, S_avail - s_c - C - F))
  5. Served = s_c + n; Unmet = D - served
  6. Curtailment = S_avail - served - C - F
  7. Stored energy update: E' = clamp(E + eta_c * C - p_dis / eta_d, min_e, max_e)
"""

from typing import Dict, Any, Optional
from system.schemas.dispatch_plan import DispatchPlan
from system.schemas.station_state import StationState
from system.simulation.research_realization_executor import (
    ResearchRealizationExecutor,
    RealizationResult
)


class PlanConsistentRealizationExecutor(ResearchRealizationExecutor):
    """
    Research diagnostic realization executor that honours the optimizer's
    planned battery charge from available supply after critical load service.
    """

    def __init__(self, configs: Dict[str, Any]):
        super().__init__(configs)
        self.critical_ceiling_w = float(configs.get("critical_demand_baseline_w", 11600.0))

    def execute_step(
        self,
        current_state: StationState,
        dispatch_plan: DispatchPlan,
        realized_inputs: Dict[str, Any],
        step_index: int = 0
    ) -> RealizationResult:
        # 1. Planned controllable actions from dispatch plan
        p_chg_plan = float(dispatch_plan.battery_charge[step_index])
        p_dis_plan = float(dispatch_plan.battery_discharge[step_index])
        p_diesel_plan = float(dispatch_plan.diesel_power[step_index])
        p_flx_plan = float(dispatch_plan.flexible_load_schedule[step_index]) if dispatch_plan.flexible_load_schedule else 0.0

        # 2. Ingest realized environmental conditions (identical to Arm A)
        if "actual_SW_IN" in realized_inputs:
            actual_sw_in = float(realized_inputs["actual_SW_IN"])
            solar_realized = self.pv_from_sw_in(actual_sw_in)
        elif "actual_solar_w" in realized_inputs:
            solar_realized = max(0.0, min(float(realized_inputs["actual_solar_w"]), self.max_inverter_power_w))
            actual_sw_in = solar_realized / (self.array_area_m2 * self.panel_efficiency * self.performance_ratio)
        else:
            raise ValueError("Missing realized solar input ('actual_SW_IN' or 'actual_solar_w').")

        if "actual_wind_generation" in realized_inputs:
            wind_realized = max(0.0, float(realized_inputs["actual_wind_generation"]))
        elif "actual_wind_w" in realized_inputs:
            wind_realized = max(0.0, float(realized_inputs["actual_wind_w"]))
        else:
            raise ValueError("Missing realized wind input ('actual_wind_generation' or 'actual_wind_w').")

        if "actual_demand" in realized_inputs:
            demand_realized = max(0.0, float(realized_inputs["actual_demand"]))
        elif "actual_demand_w" in realized_inputs:
            demand_realized = max(0.0, float(realized_inputs["actual_demand_w"]))
        else:
            raise ValueError("Missing realized demand input ('actual_demand' or 'actual_demand_w').")

        next_timestamp = str(realized_inputs["timestamp"])

        # 3. Diesel Generator Realization (identical to Arm A)
        avail_fuel = current_state.diesel_fuel_remaining_liters
        if avail_fuel is None:
            avail_fuel = self.initial_fuel_l

        if p_diesel_plan > 0.0 and avail_fuel > 0.0:
            fuel_req = (self.base_fuel_lph + self.marginal_fuel_lpwh * p_diesel_plan) * 1.0
            if avail_fuel >= fuel_req:
                diesel_realized = p_diesel_plan
                fuel_consumed = fuel_req
                fuel_remaining = max(0.0, avail_fuel - fuel_consumed)
                diesel_running = True
                diesel_hours = current_state.diesel_hours_running + 1.0
            else:
                max_p = max(0.0, (avail_fuel - self.base_fuel_lph) / self.marginal_fuel_lpwh) if avail_fuel > self.base_fuel_lph else 0.0
                diesel_realized = min(p_diesel_plan, max_p)
                fuel_consumed = avail_fuel
                fuel_remaining = 0.0
                diesel_running = diesel_realized > 0.0
                diesel_hours = (current_state.diesel_hours_running + 1.0) if diesel_running else 0.0
        else:
            diesel_realized = 0.0
            fuel_consumed = 0.0
            fuel_remaining = avail_fuel
            diesel_running = False
            diesel_hours = 0.0

        # 4. Battery Discharge Realization with SOC Floor Protection (identical to Arm A)
        curr_e_wh = float(current_state.battery_energy_wh)
        dc_energy_above_floor = max(0.0, curr_e_wh - self.min_e_wh)
        max_ac_discharge_allowed = dc_energy_above_floor * self.eta_dis

        p_dis_realized = min(p_dis_plan, self.max_discharge_power_w, max_ac_discharge_allowed)
        p_dis_realized = max(0.0, p_dis_realized)

        # 5. Realized Available Supply (S_avail)
        S_avail = solar_realized + wind_realized + diesel_realized + p_dis_realized

        # 6. Critical Load Service: s_c = min(D_c, S_avail)
        D = demand_realized
        D_c = min(self.critical_ceiling_w, D)
        s_c = min(D_c, S_avail)

        # 7. Planned Charge Realization (honours plan subject to limits & remaining supply)
        if p_dis_realized > 1e-4:
            C = 0.0
        else:
            dc_energy_room = max(0.0, self.max_e_wh - curr_e_wh)
            max_ac_charge_allowed = dc_energy_room / self.eta_chg
            max_charge_capability = min(self.max_charge_power_w, max_ac_charge_allowed)

            rem_supply_after_crit = max(0.0, S_avail - s_c)
            C = min(p_chg_plan, rem_supply_after_crit, max_charge_capability)
            C = max(0.0, C)

        # 8. Planned Flexible Load (Sink)
        rem_after_chg = max(0.0, S_avail - s_c - C)
        F = min(p_flx_plan, rem_after_chg)
        F = max(0.0, F)

        # 9. Non-Critical Service
        rem_after_flx = max(0.0, S_avail - s_c - C - F)
        non_crit_dem = max(0.0, D - D_c)
        n = min(non_crit_dem, rem_after_flx)
        n = max(0.0, n)

        # 10. Served and Unmet Load
        served_load = s_c + n
        unmet_load = max(0.0, D - served_load)

        # 11. Curtailment
        curtailment = max(0.0, S_avail - served_load - C - F)

        # 12. Realized Battery Energy & SOC Update
        delta_e_wh = (C * self.eta_chg - (p_dis_realized / self.eta_dis)) * 1.0
        next_e_wh = curr_e_wh + delta_e_wh
        next_e_wh = max(self.min_e_wh, min(self.max_e_wh, next_e_wh))
        realized_soc_pct = (next_e_wh / self.capacity_wh) * 100.0

        # 13. Busbar Energy Accounting & Residual Check
        p_in = S_avail
        p_out = served_load + C + F + curtailment
        balance_error = abs(p_in - p_out)
        load_balance_error = abs(D - (served_load + unmet_load))

        if balance_error > 1e-3:
            raise RuntimeError(
                f"Busbar energy balance accounting error in Arm B: P_in ({p_in:.4f} W) != P_out ({p_out:.4f} W), diff = {balance_error:.6f} W"
            )

        if load_balance_error > 1e-3:
            raise RuntimeError(
                f"Load balance error in Arm B: demand ({D:.4f} W) != served ({served_load:.4f} W) + unmet ({unmet_load:.4f} W)"
            )

        accounting = {
            "p_in_total_w": round(p_in, 4),
            "p_out_total_w": round(p_out, 4),
            "solar_in_w": round(solar_realized, 4),
            "wind_in_w": round(wind_realized, 4),
            "diesel_in_w": round(diesel_realized, 4),
            "battery_dis_in_w": round(p_dis_realized, 4),
            "served_load_out_w": round(served_load, 4),
            "battery_chg_out_w": round(C, 4),
            "flexible_load_out_w": round(F, 4),
            "curtailment_out_w": round(curtailment, 4),
            "unmet_load_w": round(unmet_load, 4),
            "busbar_balance_error_w": round(balance_error, 8),
            "p_chg_plan_w": round(p_chg_plan, 4),
            "delta_c_w": round(p_chg_plan - C, 4)
        }

        next_state = StationState(
            timestamp=next_timestamp,
            battery_soc_pct=round(realized_soc_pct, 2),
            battery_energy_wh=round(next_e_wh, 2),
            diesel_running=diesel_running,
            diesel_hours_running=round(diesel_hours, 2),
            last_observed_solar_irradiance=round(actual_sw_in, 4),
            last_observed_demand=round(demand_realized, 2),
            last_observed_wind_generation=round(wind_realized, 2),
            operating_mode=current_state.operating_mode,
            diesel_fuel_remaining_liters=round(fuel_remaining, 4)
        )

        return RealizationResult(
            next_state=next_state,
            solar_realized_w=round(solar_realized, 2),
            wind_realized_w=round(wind_realized, 2),
            demand_realized_w=round(demand_realized, 2),
            diesel_realized_w=round(diesel_realized, 2),
            battery_charge_realized_w=round(C, 2),
            battery_discharge_realized_w=round(p_dis_realized, 2),
            served_load_w=round(served_load, 2),
            unmet_load_w=round(unmet_load, 2),
            curtailment_w=round(curtailment, 2),
            realized_battery_energy_wh=round(next_e_wh, 2),
            realized_soc_pct=round(realized_soc_pct, 2),
            diesel_fuel_consumed_l=round(fuel_consumed, 4),
            diesel_fuel_remaining_l=round(fuel_remaining, 4),
            diesel_running=diesel_running,
            diesel_hours_running=round(diesel_hours, 2),
            busbar_energy_balance_error_w=round(balance_error, 6),
            accounting=accounting
        )
