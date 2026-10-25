"""
DigitalTwinSimulator Module
Offline microgrid simulator enforcing closed-loop simulation and MPC receding-horizon control.
"""
from typing import Dict, Any, List
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

class DigitalTwinSimulator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        bat_cfg = config.get("battery", {})
        self.capacity_wh = bat_cfg.get("capacity_wh", 200000.0)
        self.min_soc_pct = bat_cfg.get("min_soc_pct", 20.0)
        self.max_soc_pct = bat_cfg.get("max_soc_pct", 95.0)
        self.eta_chg = bat_cfg.get("charge_efficiency", 0.92)
        self.eta_dis = bat_cfg.get("discharge_efficiency", 0.92)

        self.min_e_wh = self.capacity_wh * (self.min_soc_pct / 100.0)
        self.max_e_wh = self.capacity_wh * (self.max_soc_pct / 100.0)

        diesel_cfg = config.get("diesel", {})
        self.base_fuel_lph = diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0)
        self.marginal_fuel_lpwh = diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025)
        self.initial_fuel_l = diesel_cfg.get("initial_fuel_l", 100.0)

    def step(
        self,
        current_state: StationState,
        dispatch_plan: DispatchPlan,
        actuals_next_step: Dict[str, Any]
    ) -> StationState:
        """
        Executes the FIRST timestep of the DispatchPlan against actual ground truth.
        Returns the updated StationState for the next timestep.
        """
        # First timestep dispatch decisions
        p_chg = dispatch_plan.battery_charge[0]
        p_dis = dispatch_plan.battery_discharge[0]
        p_diesel = dispatch_plan.diesel_power[0]

        # Actual environmental conditions
        actual_sw_in = actuals_next_step["actual_SW_IN"]
        actual_demand = actuals_next_step["actual_demand"]
        actual_wind = actuals_next_step["actual_wind_generation"]
        next_ts = actuals_next_step["timestamp"]

        # Update true physical battery state
        curr_e_wh = current_state.battery_energy_wh
        curr_e_wh += (p_chg * self.eta_chg - (p_dis / self.eta_dis)) * 1.0
        soc_pct = (curr_e_wh / self.capacity_wh) * 100.0

        if soc_pct < (self.min_soc_pct - 1e-4) or soc_pct > (self.max_soc_pct + 1e-4):
            raise RuntimeError(
                f"FAILED_STATE_VIOLATION: Physical SOC_next {soc_pct:.4f}% exceeded configured boundaries "
                f"[{self.min_soc_pct}%, {self.max_soc_pct}%]"
            )

        diesel_running = p_diesel > 0
        diesel_hours = (current_state.diesel_hours_running + 1.0) if diesel_running else 0.0

        # Physical fuel consumption calculation for committed first action (k=0)
        required_fuel = ((self.base_fuel_lph if diesel_running else 0.0) + (self.marginal_fuel_lpwh * p_diesel)) * 1.0
        available_fuel = current_state.diesel_fuel_remaining_liters
        if available_fuel is None:
            available_fuel = self.initial_fuel_l
        next_fuel = max(0.0, available_fuel - required_fuel)

        return StationState(
            timestamp=next_ts,
            battery_soc_pct=round(soc_pct, 2),
            battery_energy_wh=round(curr_e_wh, 2),
            diesel_running=diesel_running,
            diesel_hours_running=diesel_hours,
            last_observed_solar_irradiance=actual_sw_in,
            last_observed_demand=actual_demand,
            last_observed_wind_generation=actual_wind,
            operating_mode=current_state.operating_mode,
            diesel_fuel_remaining_liters=round(next_fuel, 4)
        )
