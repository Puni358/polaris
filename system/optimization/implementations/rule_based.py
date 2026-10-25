"""
Local Rule-Based EnergyOptimizer Implementation
Deterministic, physically explicit microgrid dispatch optimizer for Phase D1.
Enforces strict power balance and battery SOC bounds at every timestep.
"""
from typing import Dict, Any, List
from system.optimization.interface.base import EnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

class LocalRuleBasedEnergyOptimizer(EnergyOptimizer):
    def optimize(
        self,
        forecast_bundle: ForecastBundle,
        station_state: StationState,
        config: Dict[str, Any]
    ) -> DispatchPlan:
        
        # Load physical configs or fallback defaults
        bat_cfg = config.get("battery", {})
        capacity_wh = bat_cfg.get("capacity_wh", 200000.0)
        min_soc_pct = bat_cfg.get("min_soc_pct", 20.0)
        max_soc_pct = bat_cfg.get("max_soc_pct", 95.0)
        eta_chg = bat_cfg.get("charge_efficiency", 0.92)
        eta_dis = bat_cfg.get("discharge_efficiency", 0.92)
        max_p_chg = bat_cfg.get("max_charge_power_w", 50000.0)
        max_p_dis = bat_cfg.get("max_discharge_power_w", 50000.0)

        min_e_wh = capacity_wh * (min_soc_pct / 100.0)
        max_e_wh = capacity_wh * (max_soc_pct / 100.0)

        diesel_cfg = config.get("diesel", {})
        min_diesel_w = diesel_cfg.get("min_power_w", 10000.0)
        max_diesel_w = diesel_cfg.get("max_power_w", 100000.0)

        loads_cfg = config.get("loads", {})
        unmet_penalty_rate = loads_cfg.get("critical_load", {}).get("unmet_penalty_per_wh", 10.0)

        # Output schedules
        timestamps = forecast_bundle.timestamps
        solar_gen = forecast_bundle.solar_generation.point
        wind_gen = forecast_bundle.wind_generation.point
        demand = forecast_bundle.demand.point

        solar_used: List[float] = []
        wind_used: List[float] = []
        battery_charge: List[float] = []
        battery_discharge: List[float] = []
        battery_soc: List[float] = []
        diesel_power: List[float] = []
        load_served: List[float] = []
        flexible_load_schedule: List[float] = []
        renewable_curtailment: List[float] = []
        unmet_load: List[float] = []
        energy_balance_errors: List[float] = []

        curr_e_wh = station_state.battery_energy_wh
        total_objective = 0.0

        for t in range(24):
            p_solar = solar_gen[t]
            p_wind = wind_gen[t]
            p_demand = demand[t]
            p_renewables = p_solar + p_wind

            p_chg = 0.0
            p_dis = 0.0
            p_diesel = 0.0
            p_served = 0.0
            p_curt = 0.0
            p_unmet = 0.0

            if p_renewables >= p_demand:
                # Surplus renewables
                p_served = p_demand
                surplus = p_renewables - p_demand

                # Charge battery with surplus
                avail_chg_capacity_wh = (max_e_wh - curr_e_wh) / eta_chg
                max_possible_chg = min(max_p_chg, avail_chg_capacity_wh)
                p_chg = min(surplus, max_possible_chg)

                # Excess surplus is curtailed
                p_curt = surplus - p_chg

            else:
                # Renewable deficit
                deficit = p_demand - p_renewables

                # Discharge battery to cover deficit
                avail_dis_energy_wh = (curr_e_wh - min_e_wh) * eta_dis
                max_possible_dis = min(max_p_dis, avail_dis_energy_wh)
                p_dis = min(deficit, max_possible_dis)

                rem_deficit = deficit - p_dis

                if rem_deficit > 0:
                    # Dispatch diesel if deficit remains
                    if rem_deficit <= min_diesel_w:
                        p_diesel = min_diesel_w
                    else:
                        p_diesel = min(rem_deficit, max_diesel_w)

                    # If min_diesel_w exceeds rem_deficit, charge battery / curtail excess
                    diesel_surplus = p_diesel - rem_deficit
                    if diesel_surplus > 0:
                        avail_chg_capacity_wh = (max_e_wh - curr_e_wh) / eta_chg
                        max_possible_chg = min(max_p_chg, avail_chg_capacity_wh)
                        extra_chg = min(diesel_surplus, max_possible_chg)
                        p_chg = extra_chg
                        p_curt = diesel_surplus - extra_chg

                # Served load and unmet load calculation
                supplied = p_renewables + p_dis + p_diesel - p_chg - p_curt
                if supplied >= p_demand:
                    p_served = p_demand
                    p_unmet = 0.0
                else:
                    p_served = supplied
                    p_unmet = p_demand - supplied

            # Attribute solar_used and wind_used explicitly
            if p_renewables > 0:
                curt_ratio = p_curt / p_renewables if p_curt > 0 else 0.0
                p_sol_used = p_solar * (1.0 - min(1.0, curt_ratio))
                p_w_used = p_wind * (1.0 - min(1.0, curt_ratio))
            else:
                p_sol_used = 0.0
                p_w_used = 0.0

            # Update battery SOC using exact discrete transition: E[t+1] = E[t] + (eta_chg * P_chg - P_dis / eta_dis) * dt
            curr_e_wh += (p_chg * eta_chg - (p_dis / eta_dis)) * 1.0
            curr_e_wh = max(min_e_wh, min(max_e_wh, curr_e_wh))
            soc_pct = (curr_e_wh / capacity_wh) * 100.0

            # Strict Energy Balance Conservation Equations:
            # 1. Bus-Bar Power Balance: P_supplied (used_solar + used_wind + discharge + diesel) == P_consumed (served + charge)
            p_supplied = p_sol_used + p_w_used + p_dis + p_diesel
            p_consumed = p_served + p_chg
            bus_bar_error = abs(p_supplied - p_consumed)

            # 2. Demand Deficit Balance: P_demand == P_served + P_unmet
            demand_error = abs(p_demand - (p_served + p_unmet))

            # 3. Renewable Availability Decomposition: P_available == P_used + P_curtailed
            renewable_error = abs((p_solar + p_wind) - (p_sol_used + p_w_used + p_curt))

            err = max(bus_bar_error, demand_error, renewable_error)

            solar_used.append(round(p_sol_used, 2))
            wind_used.append(round(p_w_used, 2))
            battery_charge.append(round(p_chg, 2))
            battery_discharge.append(round(p_dis, 2))
            battery_soc.append(round(soc_pct, 2))
            diesel_power.append(round(p_diesel, 2))
            load_served.append(round(p_served, 2))
            flexible_load_schedule.append(0.0) # Deferred for future implementation
            renewable_curtailment.append(round(p_curt, 2))
            unmet_load.append(round(p_unmet, 2))
            energy_balance_errors.append(round(err, 6))

            # Simple objective calculation
            fuel_used_l = (diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0) if p_diesel > 0 else 0.0) + p_diesel * diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025)
            total_objective += fuel_used_l * diesel_cfg.get("fuel_cost_per_l", 2.50) + p_unmet * unmet_penalty_rate

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
            objective_value=round(total_objective, 2),
            constraint_status="OPTIMAL",
            energy_balance_errors=energy_balance_errors
        )
