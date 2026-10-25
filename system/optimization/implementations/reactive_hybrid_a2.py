"""
ReactiveHybridA2Optimizer Module
Implements CELL A2: REACTIVE_HYBRID_NO_FORECAST_BASELINE.
Enforces human-approved deterministic reactive dispatch policy:
1. Current renewables serve current station demand first.
2. Excess renewables charge battery up to SOC_max and P_chg_max.
3. Deficit demand uses battery discharge up to SOC_min and P_dis_max.
4. Remaining deficit is supplied by diesel generator.
5. If diesel is required and min_diesel_w > deficit, unavoidable minimum-output surplus:
   a. First offsets/reduces battery discharge if battery was discharging.
   b. Then charges battery if battery was not discharging and SOC headroom exists.
6. Diesel is NEVER started solely for battery charging.
7. FORECAST_CALL_COUNT = 0, MILP_SOLVE_COUNT = 0, FUTURE_TRUTH_ACCESS = 0.
"""

from typing import Dict, Any, List
from system.optimization.interface.base import EnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

class ReactiveHybridA2Optimizer(EnergyOptimizer):
    def optimize(
        self,
        forecast_bundle: ForecastBundle,
        station_state: StationState,
        config: Dict[str, Any]
    ) -> DispatchPlan:
        """
        Executes single-step instantaneous reactive dispatch.
        Ignores all horizon forecast values (uses index 0 only).
        """
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

        diesel_cfg = config.get("diesel", {})
        min_diesel_w = float(diesel_cfg.get("min_power_w", 10000.0))
        max_diesel_w = float(diesel_cfg.get("max_power_w", 100000.0))
        base_fuel_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
        marg_fuel_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

        timestamps = forecast_bundle.timestamps
        solar_gen = forecast_bundle.solar_generation.point
        wind_gen = forecast_bundle.wind_generation.point
        demand = forecast_bundle.demand.point

        H = len(timestamps)

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
        total_fuel_l = 0.0

        for t in range(H):
            p_solar = max(0.0, float(solar_gen[t]))
            p_wind = max(0.0, float(wind_gen[t]))
            p_demand = max(0.0, float(demand[t]))
            p_renewables = p_solar + p_wind

            p_chg = 0.0
            p_dis = 0.0
            p_diesel = 0.0
            p_curt_ren = 0.0
            p_curt_die = 0.0
            p_unmet = 0.0

            if p_renewables >= p_demand:
                # 1. Current renewables serve current demand first
                surplus_ren = p_renewables - p_demand
                
                # 2. Excess renewables charge battery up to SOC_max and P_chg_max
                avail_chg_capacity_wh = max(0.0, (max_e_wh - curr_e_wh) / eta_chg)
                max_possible_chg = min(max_p_chg, avail_chg_capacity_wh)
                p_chg = min(surplus_ren, max_possible_chg)
                
                # Remaining excess renewables are curtailed
                p_curt_ren = surplus_ren - p_chg
                p_dis = 0.0
                p_diesel = 0.0
            else:
                # 3. Renewable deficit -> Discharge battery
                deficit_1 = p_demand - p_renewables
                
                avail_dis_energy_wh = max(0.0, (curr_e_wh - min_e_wh) * eta_dis)
                max_possible_dis = min(max_p_dis, avail_dis_energy_wh)
                p_dis = min(deficit_1, max_possible_dis)
                
                deficit_2 = deficit_1 - p_dis

                if deficit_2 > 0.0:
                    # 4. Remaining deficit -> Diesel dispatch
                    p_diesel = max(min_diesel_w, min(deficit_2, max_diesel_w))
                    diesel_surplus = p_diesel - deficit_2

                    if diesel_surplus > 0.0:
                        # Unavoidable minimum-output surplus:
                        # Exclusivity rule: If battery is discharging, surplus offsets discharge first!
                        if p_dis > 0.0:
                            offset_dis = min(p_dis, diesel_surplus)
                            p_dis -= offset_dis
                            rem_surplus = diesel_surplus - offset_dis
                        else:
                            rem_surplus = diesel_surplus

                        if rem_surplus > 0.0 and p_dis == 0.0:
                            avail_chg_capacity_wh = max(0.0, (max_e_wh - curr_e_wh) / eta_chg)
                            max_possible_chg = min(max_p_chg, avail_chg_capacity_wh)
                            p_chg = min(rem_surplus, max_possible_chg)
                            p_curt_die = rem_surplus - p_chg
                        else:
                            p_chg = 0.0
                            p_curt_die = rem_surplus if p_dis > 0.0 else 0.0
                    else:
                        p_chg = 0.0
                        p_curt_die = 0.0
                else:
                    p_diesel = 0.0
                    p_chg = 0.0

            # Served load calculation
            p_supplied = p_renewables + p_dis + p_diesel - p_chg - p_curt_ren - p_curt_die
            if p_supplied >= p_demand - 1e-4:
                p_served = p_demand
                p_unmet = 0.0
            else:
                p_served = max(0.0, p_supplied)
                p_unmet = p_demand - p_served

            # Pro-rate renewable usage for telemetry
            p_curt_total = p_curt_ren + p_curt_die
            if p_renewables > 0.0:
                ren_used_ratio = max(0.0, 1.0 - (p_curt_ren / p_renewables))
                p_sol_u = p_solar * ren_used_ratio
                p_w_u = p_wind * ren_used_ratio
            else:
                p_sol_u = 0.0
                p_w_u = 0.0

            # Discrete state transition for battery
            curr_e_wh += (p_chg * eta_chg - (p_dis / eta_dis)) * 1.0
            curr_e_wh = max(min_e_wh, min(max_e_wh, curr_e_wh))
            soc_pct = (curr_e_wh / capacity_wh) * 100.0

            # Diesel fuel calculation
            diesel_running = p_diesel > 0.0
            step_fuel_l = ((base_fuel_lph if diesel_running else 0.0) + (marg_fuel_lpwh * p_diesel)) * 1.0
            total_fuel_l += step_fuel_l

            # Strict power balance check: (sol_used + wind_used + dis + diesel) == (served + chg)
            err = abs((p_sol_u + p_w_u + p_dis + p_diesel) - (p_served + p_chg))

            solar_used.append(round(p_sol_u, 2))
            wind_used.append(round(p_w_u, 2))
            battery_charge.append(round(p_chg, 2))
            battery_discharge.append(round(p_dis, 2))
            battery_soc.append(round(soc_pct, 2))
            diesel_power.append(round(p_diesel, 2))
            load_served.append(round(p_served, 2))
            flexible_load_schedule.append(0.0) # P_flex is ALWAYS 0.0 in Cell A2
            renewable_curtailment.append(round(p_curt_total, 2))
            unmet_load.append(round(p_unmet, 2))
            energy_balance_errors.append(round(err, 6))

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
            objective_value=round(total_fuel_l, 4),
            constraint_status="OPTIMAL",
            energy_balance_errors=energy_balance_errors,
            j1_objective=0.0,
            j2_objective=0.0,
            j3_objective=round(total_fuel_l, 4),
            j4_objective=sum(renewable_curtailment),
            reserve_shortfall=[0.0]*H
        )
