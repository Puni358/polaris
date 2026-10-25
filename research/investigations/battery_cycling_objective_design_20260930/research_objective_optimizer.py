"""
POLARIS Battery Cycling Objective Design Research Optimizer Implementation
Strictly Isolated Research Implementation (Version 1.0.0)

Formulates exact Mixed-Integer Linear Program (MILP) with continuous power/energy decision variables
and binary commitment/startup variables for battery exclusivity and diesel generator operation,
parameterized to evaluate objective variants O0-O6 without modifying production source code.

FROZEN PRODUCTION FILE PRESERVATION:
- system/optimization/implementations/milp.py is UNTOUCHED.
- system/schemas/* are UNTOUCHED.
- system/config/* are UNTOUCHED.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from scipy.optimize import milp, LinearConstraint, Bounds

from system.optimization.interface.base import EnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan


class ResearchObjectiveOptimizer(EnergyOptimizer):
    def __init__(self, variant_id: str = "O0", custom_params: Dict[str, Any] = None):
        self.variant_id = variant_id
        self.custom_params = custom_params or {}

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

        # Degradation penalty determination per variant
        deg_penalty_default = float(bat_cfg.get("deg_penalty_per_wh", 0.00005))
        
        if "deg_penalty_per_wh" in self.custom_params:
            deg_penalty = float(self.custom_params["deg_penalty_per_wh"])
        elif self.variant_id == "O0":
            deg_penalty = 0.00005  # $0.05/kWh
        elif self.variant_id == "O1a":
            deg_penalty = 0.000025 # $0.025/kWh
        elif self.variant_id == "O1b":
            deg_penalty = 0.0000125 # $0.0125/kWh
        elif self.variant_id == "O1c":
            deg_penalty = 0.000000 # $0.00/kWh
        elif self.variant_id in ["O2", "O3", "O4", "O5", "O6"]:
            deg_penalty = float(self.custom_params.get("deg_penalty_per_wh", 0.0000125))
        else:
            deg_penalty = deg_penalty_default

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

        loads_cfg = config.get("loads", {})
        unmet_penalty_per_wh = float(loads_cfg.get("critical_load", {}).get("unmet_penalty_per_wh", 10.0))
        curt_penalty_per_wh = float(config.get("optimizer", {}).get("weights", {}).get("renewable_curtailment_penalty", 0.001))

        # Variant specific parameters
        diesel_avoidance_credit = float(self.custom_params.get("diesel_avoidance_credit_per_wh", 0.0))
        curtailment_absorption_credit = float(self.custom_params.get("curtailment_absorption_credit_per_wh", 0.0))
        opportunity_cost_weight = float(self.custom_params.get("opportunity_cost_weight", 0.0))

        if self.variant_id == "O2":
            diesel_avoidance_credit = self.custom_params.get("diesel_avoidance_credit_per_wh", 0.0003)
        elif self.variant_id == "O3":
            curtailment_absorption_credit = self.custom_params.get("curtailment_absorption_credit_per_wh", 0.0001)
        elif self.variant_id == "O4":
            opportunity_cost_weight = self.custom_params.get("opportunity_cost_weight", 0.00005)
        elif self.variant_id == "O5":
            pass
        elif self.variant_id == "O6":
            deg_penalty = 0.0000125
            diesel_avoidance_credit = 0.0002
            curtailment_absorption_credit = 0.00005

        timestamps = forecast_bundle.timestamps
        solar_gen = forecast_bundle.solar_generation.point
        wind_gen = forecast_bundle.wind_generation.point
        demand = forecast_bundle.demand.point

        H = 24
        K = 15

        num_vars = H * K
        c = np.zeros(num_vars)
        integrality = np.zeros(num_vars, dtype=int)
        lb = np.zeros(num_vars)
        ub = np.zeros(num_vars)

        for t in range(H):
            base = t * K
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_dem = max(0.0, demand[t])

            dt = float(config.get("optimizer", {}).get("timestep_hours", 1.0))
            gamma = float(config.get("optimizer", {}).get("horizon_discount_factor_gamma", 1.0))
            w_t = gamma ** t

            # Base Objective Coefficients
            c[base + 2] = curt_penalty_per_wh * dt * w_t  # p_curt_sol
            c[base + 3] = curt_penalty_per_wh * dt * w_t  # p_curt_wind
            
            # Charging cost: deg_penalty - curtailment_absorption_credit (if renewables exceed demand)
            chg_cost = deg_penalty
            if curtailment_absorption_credit > 0 and (p_sol_max + p_wind_max > p_dem):
                chg_cost -= curtailment_absorption_credit
            
            # Discharging cost: deg_penalty - diesel_avoidance_credit (if demand exceeds renewables)
            dis_cost = deg_penalty
            if diesel_avoidance_credit > 0 and (p_dem > p_sol_max + p_wind_max):
                dis_cost -= diesel_avoidance_credit

            # O5 Dynamic degradation cost scaling based on anticipated SOC
            if self.variant_id == "O5":
                estimated_soc = (initial_e_wh / capacity_wh)
                soc_factor = 1.0 + 2.0 * ((estimated_soc - 0.5) ** 2)
                chg_cost *= soc_factor
                dis_cost *= soc_factor

            c[base + 4] = chg_cost * dt * w_t         # p_chg
            c[base + 5] = dis_cost * dt * w_t         # p_dis
            c[base + 7] = fuel_cost_per_l * marg_fuel_l_wh * dt * w_t  # p_diesel
            c[base + 9] = unmet_penalty_per_wh * dt       # p_unmet
            c[base + 13] = fuel_cost_per_l * base_fuel_l_h * dt * w_t  # u_diesel
            c[base + 14] = startup_cost * w_t             # v_start

            if opportunity_cost_weight > 0 and p_dem > 20000.0:
                c[base + 6] = -opportunity_cost_weight * dt * w_t # E_next credit

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

        # Constraints construction
        A_rows = []
        lhs = []
        rhs = []

        for t in range(H):
            base = t * K
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_dem = max(0.0, demand[t])

            # 1. Solar Decomposition
            row = np.zeros(num_vars)
            row[base + 0] = 1.0
            row[base + 2] = 1.0
            A_rows.append(row)
            lhs.append(p_sol_max)
            rhs.append(p_sol_max)

            # 2. Wind Decomposition
            row = np.zeros(num_vars)
            row[base + 1] = 1.0
            row[base + 3] = 1.0
            A_rows.append(row)
            lhs.append(p_wind_max)
            rhs.append(p_wind_max)

            # 3. Bus-Bar Balance
            row = np.zeros(num_vars)
            row[base + 0] = 1.0
            row[base + 1] = 1.0
            row[base + 5] = 1.0
            row[base + 7] = 1.0
            row[base + 8] = -1.0
            row[base + 4] = -1.0
            row[base + 10] = -1.0
            A_rows.append(row)
            lhs.append(0.0)
            rhs.append(0.0)

            # 4. Demand Deficit Balance
            row = np.zeros(num_vars)
            row[base + 8] = 1.0
            row[base + 9] = 1.0
            A_rows.append(row)
            lhs.append(p_dem)
            rhs.append(p_dem)

            # 5. Charge Bound vs Binary
            row = np.zeros(num_vars)
            row[base + 4] = 1.0
            row[base + 11] = -max_p_chg
            A_rows.append(row)
            lhs.append(-np.inf)
            rhs.append(0.0)

            # 6. Discharge Bound vs Binary
            row = np.zeros(num_vars)
            row[base + 5] = 1.0
            row[base + 12] = -max_p_dis
            A_rows.append(row)
            lhs.append(-np.inf)
            rhs.append(0.0)

            # 7. Charge/Discharge Exclusivity
            row = np.zeros(num_vars)
            row[base + 11] = 1.0
            row[base + 12] = 1.0
            A_rows.append(row)
            lhs.append(-np.inf)
            rhs.append(1.0)

            # 8. Battery Energy Discrete Transition
            dt = float(config.get("optimizer", {}).get("timestep_hours", 1.0))
            row = np.zeros(num_vars)
            row[base + 6] = 1.0
            if t == 0:
                row[base + 4] = -eta_chg * dt
                row[base + 5] = dt / eta_dis
                A_rows.append(row)
                lhs.append(initial_e_wh)
                rhs.append(initial_e_wh)
            else:
                prev_base = (t - 1) * K
                row[prev_base + 6] = -1.0
                row[base + 4] = -eta_chg * dt
                row[base + 5] = dt / eta_dis
                A_rows.append(row)
                lhs.append(0.0)
                rhs.append(0.0)

            # 9. Diesel Min Output when Running
            row = np.zeros(num_vars)
            row[base + 7] = 1.0
            row[base + 13] = -min_diesel_w
            A_rows.append(row)
            lhs.append(0.0)
            rhs.append(np.inf)

            # 10. Diesel Max Output when Running
            row = np.zeros(num_vars)
            row[base + 7] = 1.0
            row[base + 13] = -max_diesel_w
            A_rows.append(row)
            lhs.append(-np.inf)
            rhs.append(0.0)

            # 11. Diesel Startup Tracking
            row = np.zeros(num_vars)
            row[base + 14] = 1.0
            row[base + 13] = -1.0
            if t == 0:
                A_rows.append(row)
                lhs.append(-initial_diesel_running)
                rhs.append(np.inf)
            else:
                prev_base = (t - 1) * K
                row[prev_base + 13] = 1.0
                A_rows.append(row)
                lhs.append(0.0)
                rhs.append(np.inf)

        A = np.array(A_rows)
        constraints = LinearConstraint(A, lhs, rhs)
        bounds = Bounds(lb, ub)

        try:
            res = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)
        except Exception as e:
            raise RuntimeError(f"RESEARCH_OPTIMIZATION_RUNTIME_FAILURE: {e}")

        if not res.success or res.x is None:
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
                energy_balance_errors=[0.0]*24
            )

        sol = res.x

        solar_used, wind_used = [], []
        battery_charge, battery_discharge, battery_soc = [], [], []
        diesel_power, load_served = [], []
        flexible_load_schedule, renewable_curtailment, unmet_load = [], [], []
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
            energy_balance_errors=energy_balance_errors
        )
