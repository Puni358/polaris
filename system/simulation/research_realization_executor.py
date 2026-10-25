"""
POLARIS Research-Only Realized Energy-Balance Executor
Module: system.simulation.research_realization_executor

RESEARCH USE ONLY / CLOSED-LOOP HARNESS REALIZATION LAYER:
- Evaluates the physical outcome of a GAP19 dispatch plan against REALIZED hourly environmental inputs.
- Computes exact microgrid busbar energy balance:
    solar_realized + wind_realized + diesel_realized + battery_discharge - battery_charge - demand_realized
- Explicitly accounts for:
    served_load, unmet_load, curtailment, realized battery energy/SOC, and diesel fuel transitions.
- Enforces governed battery boundaries [min_soc_pct, max_soc_pct], efficiencies, and power ratings.
- Zero production simulator modification (system/simulation/simulator.py remains untouched).
- Distinguishes FORECAST SIDE (MEPS -> ForecastBundle -> GAP19) from REALIZATION SIDE (actual observations -> physical realization).
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan


@dataclass
class RealizationResult:
    """
    Physical realization result of executing one hourly dispatch step against realized environment.
    """
    next_state: StationState
    solar_realized_w: float
    wind_realized_w: float
    demand_realized_w: float
    diesel_realized_w: float
    battery_charge_realized_w: float
    battery_discharge_realized_w: float
    served_load_w: float
    unmet_load_w: float
    curtailment_w: float
    realized_battery_energy_wh: float
    realized_soc_pct: float
    diesel_fuel_consumed_l: float
    diesel_fuel_remaining_l: float
    diesel_running: bool
    diesel_hours_running: float
    busbar_energy_balance_error_w: float
    accounting: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.next_state.timestamp,
            "solar_realized_w": self.solar_realized_w,
            "wind_realized_w": self.wind_realized_w,
            "demand_realized_w": self.demand_realized_w,
            "diesel_realized_w": self.diesel_realized_w,
            "battery_charge_realized_w": self.battery_charge_realized_w,
            "battery_discharge_realized_w": self.battery_discharge_realized_w,
            "served_load_w": self.served_load_w,
            "unmet_load_w": self.unmet_load_w,
            "curtailment_w": self.curtailment_w,
            "realized_battery_energy_wh": self.realized_battery_energy_wh,
            "realized_soc_pct": self.realized_soc_pct,
            "diesel_fuel_consumed_l": self.diesel_fuel_consumed_l,
            "diesel_fuel_remaining_l": self.diesel_fuel_remaining_l,
            "diesel_running": self.diesel_running,
            "diesel_hours_running": self.diesel_hours_running,
            "busbar_energy_balance_error_w": self.busbar_energy_balance_error_w,
            "accounting": self.accounting
        }


class ResearchRealizationExecutor:
    """
    Research-only realization executor calculating realized microgrid energy balance.
    Respects existing governed parameters from system/config/ without modifying production simulator.
    """

    def __init__(self, configs: Dict[str, Any]):
        self.configs = configs

        # 1. Battery hardware parameters
        bat_cfg = configs.get("battery", {})
        self.capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
        self.min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))
        self.max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
        self.eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
        self.eta_dis = float(bat_cfg.get("discharge_efficiency", 0.92))
        self.max_charge_power_w = float(bat_cfg.get("max_charge_power_w", 50000.0))
        self.max_discharge_power_w = float(bat_cfg.get("max_discharge_power_w", 50000.0))

        self.min_e_wh = self.capacity_wh * (self.min_soc_pct / 100.0)
        self.max_e_wh = self.capacity_wh * (self.max_soc_pct / 100.0)

        # 2. Diesel hardware parameters
        diesel_cfg = configs.get("diesel", {})
        self.base_fuel_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
        self.marginal_fuel_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))
        self.min_diesel_w = float(diesel_cfg.get("min_power_w", 10000.0))
        self.max_diesel_w = float(diesel_cfg.get("max_power_w", 100000.0))
        self.initial_fuel_l = float(diesel_cfg.get("initial_fuel_l", 100.0))

        # 3. Solar PV transformation parameters (authorized D3 mapping)
        solar_cfg = configs.get("solar_pv", {})
        self.array_area_m2 = float(solar_cfg.get("array_area_m2", 300.0))
        self.panel_efficiency = float(solar_cfg.get("panel_efficiency", 0.20))
        self.performance_ratio = float(solar_cfg.get("performance_ratio", 0.85))
        self.max_inverter_power_w = float(solar_cfg.get("max_inverter_power_w", 60000.0))

    def pv_from_sw_in(self, sw_in_w_m2: float) -> float:
        """
        Authorized D3 transformation: SW_IN (W/m^2) -> Electrical Generation (W).
        min(SW_IN * 300 * 0.20 * 0.85, 60000.0 W)
        """
        raw_power = float(sw_in_w_m2) * self.array_area_m2 * self.panel_efficiency * self.performance_ratio
        return max(0.0, min(raw_power, self.max_inverter_power_w))

    def execute_step(
        self,
        current_state: StationState,
        dispatch_plan: DispatchPlan,
        realized_inputs: Dict[str, Any],
        step_index: int = 0
    ) -> RealizationResult:
        """
        Executes one hourly dispatch action against realized environmental inputs.
        
        Args:
            current_state: StationState at start of timestep
            dispatch_plan: DispatchPlan containing planned controllable actions
            realized_inputs: Dict with realized environmental conditions:
                - 'actual_SW_IN' (or 'actual_solar_w'): realized solar
                - 'actual_wind_generation' (or 'actual_wind_w'): realized wind
                - 'actual_demand' (or 'actual_demand_w'): realized demand
                - 'timestamp': next timestep ISO string
            step_index: index into dispatch_plan (default 0 for receding horizon MPC)
        """
        # 1. Planned controllable actions from dispatch plan
        p_chg_plan = float(dispatch_plan.battery_charge[step_index])
        p_dis_plan = float(dispatch_plan.battery_discharge[step_index])
        p_diesel_plan = float(dispatch_plan.diesel_power[step_index])

        # 2. Ingest realized environmental conditions
        if "actual_SW_IN" in realized_inputs:
            actual_sw_in = float(realized_inputs["actual_SW_IN"])
            solar_realized = self.pv_from_sw_in(actual_sw_in)
        elif "actual_solar_w" in realized_inputs:
            solar_realized = max(0.0, min(float(realized_inputs["actual_solar_w"]), self.max_inverter_power_w))
            # Backward compute equivalent irradiance for telemetry
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

        # 3. Diesel Generator Realization
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
                # Fuel starvation: produce what fuel permits
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

        # 4. Battery Discharge Realization with SOC Floor Protection
        curr_e_wh = float(current_state.battery_energy_wh)
        dc_energy_above_floor = max(0.0, curr_e_wh - self.min_e_wh)
        max_ac_discharge_allowed = dc_energy_above_floor * self.eta_dis

        # Limit planned discharge by hardware rating and available energy above min SOC
        p_dis_realized = min(p_dis_plan, self.max_discharge_power_w, max_ac_discharge_allowed)
        p_dis_realized = max(0.0, p_dis_realized)

        # 5. Busbar Supply and Demand Balance
        total_supply = solar_realized + wind_realized + diesel_realized + p_dis_realized
        served_load = min(demand_realized, total_supply)
        unmet_load = max(0.0, demand_realized - served_load)
        surplus_power = max(0.0, total_supply - demand_realized)

        # 6. Battery Charge Realization with SOC Ceiling Protection
        # Battery cannot charge if it is actively discharging in this timestep
        if surplus_power > 0.0 and p_dis_realized <= 1e-4:
            dc_energy_room = max(0.0, self.max_e_wh - curr_e_wh)
            max_ac_charge_allowed = dc_energy_room / self.eta_chg
            max_charge_capability = min(self.max_charge_power_w, max_ac_charge_allowed)

            # Charge up to surplus, bounded by battery charging capability
            p_chg_realized = min(surplus_power, max_charge_capability)
            p_chg_realized = max(0.0, p_chg_realized)
            curtailment = max(0.0, surplus_power - p_chg_realized)
        else:
            p_chg_realized = 0.0
            curtailment = surplus_power

        # 7. Realized Battery Energy & SOC Update
        delta_e_wh = (p_chg_realized * self.eta_chg - (p_dis_realized / self.eta_dis)) * 1.0
        next_e_wh = curr_e_wh + delta_e_wh

        # Guard numerical precision against bounds
        next_e_wh = max(self.min_e_wh, min(self.max_e_wh, next_e_wh))
        realized_soc_pct = (next_e_wh / self.capacity_wh) * 100.0

        # 8. Busbar Energy Accounting & Residual Check
        p_in = solar_realized + wind_realized + diesel_realized + p_dis_realized
        p_out = served_load + p_chg_realized + curtailment
        balance_error = abs(p_in - p_out)
        load_balance_error = abs(demand_realized - (served_load + unmet_load))

        if balance_error > 1e-3:
            raise RuntimeError(
                f"Busbar energy balance accounting error: P_in ({p_in:.4f} W) != P_out ({p_out:.4f} W), diff = {balance_error:.6f} W"
            )

        if load_balance_error > 1e-3:
            raise RuntimeError(
                f"Load balance error: demand ({demand_realized:.4f} W) != served ({served_load:.4f} W) + unmet ({unmet_load:.4f} W)"
            )

        accounting = {
            "p_in_total_w": round(p_in, 4),
            "p_out_total_w": round(p_out, 4),
            "solar_in_w": round(solar_realized, 4),
            "wind_in_w": round(wind_realized, 4),
            "diesel_in_w": round(diesel_realized, 4),
            "battery_dis_in_w": round(p_dis_realized, 4),
            "served_load_out_w": round(served_load, 4),
            "battery_chg_out_w": round(p_chg_realized, 4),
            "curtailment_out_w": round(curtailment, 4),
            "unmet_load_w": round(unmet_load, 4),
            "busbar_balance_error_w": round(balance_error, 8)
        }

        # 9. Next StationState Construction for Closed-Loop Receding Horizon
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
            battery_charge_realized_w=round(p_chg_realized, 2),
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
