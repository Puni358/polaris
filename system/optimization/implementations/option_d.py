"""
POLARIS Energy Management System (EMS)
Option D Protected Critical-Load Fallback Solver Implementation

Governance:
- DEC-004 Final Selection / Option D Resolution
- Decisions D1-D6 Emergency Reserve Boundaries
- Proportional Protected Critical-Load Allocation

Priority Logic:
1. Protect Critical Load: P_critical(t) served at highest priority.
2. Direct Renewable First: Solar and wind generated directly to critical load.
3. Diesel Generator Support: Diesel run only when renewables are insufficient.
4. Emergency Battery Usage: Respect preserved_resource vs limiting_resource.
5. Exclude Non-Critical Load: Non-critical demand is shed.
6. Proportional Allocation: If total power < P_critical, allocate proportionally (alpha = P_avail / P_crit).
7. Excess Diesel Charging: Excess diesel power charges battery only when diesel is running for load.
8. No Diesel-Only Charging: Diesel is NEVER started solely to charge battery in emergency mode.
"""

import math
from typing import Dict, Any, List
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.control.ecd import EmergencyAssessment, ResourceSelection

class OptionDFallbackSolver:
    """
    Option D Protected Critical-Load Heuristic Fallback Solver.
    Generates valid DispatchPlan satisfying DEC-004 emergency rules.
    """

    def solve(
        self,
        assessment: EmergencyAssessment,
        bundle: ForecastBundle,
        current_state: StationState,
        configs: Dict[str, Any]
    ) -> DispatchPlan:
        """
        Generates 24-hour Option D emergency dispatch schedule.
        """
        horizon_steps = 24
        timestamps = bundle.timestamps[:horizon_steps]

        # Config parameters
        bat_cfg = configs.get("battery", {})
        capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
        min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))
        max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
        max_dis_w = float(bat_cfg.get("max_discharge_power_w", 50000.0))
        max_chg_w = float(bat_cfg.get("max_charge_power_w", 50000.0))
        eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
        eta_dis = float(bat_cfg.get("discharge_efficiency", 0.92))

        diesel_cfg = configs.get("diesel", {})
        min_diesel_w = float(diesel_cfg.get("min_power_w", 10000.0))
        max_diesel_w = float(diesel_cfg.get("max_power_w", 100000.0))
        current_fuel_l = current_state.diesel_fuel_remaining_liters
        if current_fuel_l is None:
            current_fuel_l = float(diesel_cfg.get("initial_fuel_l", 100.0))

        # Initial battery energy
        curr_e_wh = current_state.battery_energy_wh
        min_e_wh = capacity_wh * (min_soc_pct / 100.0)
        max_e_wh = capacity_wh * (max_soc_pct / 100.0)

        # Dispatch arrays
        solar_used: List[float] = []
        wind_used: List[float] = []
        battery_charge: List[float] = []
        battery_discharge: List[float] = []
        battery_soc: List[float] = []
        diesel_power: List[float] = []
        load_served: List[float] = []
        flexible_load_schedule: List[float] = [0.0] * horizon_steps
        renewable_curtailment: List[float] = []
        unmet_load: List[float] = []
        # Computed per-timestep below from the actual dispatch arrays (item
        # 2.6 of the RT-01 Option-D repair directive) instead of being
        # hardcoded to zero. Same sign convention and units as the
        # repository's own conservation audit
        # (system/tests/test_offline_runtime.py::test_per_timestep_conservation_audit):
        # bus_err = abs((sol_u + wind_u + dis + dies) - (serv + flex + chg)).
        # All quantities here are instantaneous power in Watts over a 1-hour
        # timestep, so the numeric residual is equivalently in Wh (no unit
        # conversion needed, consistent with how curr_e_wh is updated below).
        energy_balance_errors: List[float] = []

        # Track fuel state through forecast horizon
        available_fuel = current_fuel_l
        base_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
        marginal_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

        # Timestep contract: 1.0 hour timestep locked to simulator/evaluator contract
        dt_h = 1.0
        min_step_fuel_l = (base_lph + (marginal_lpwh * min_diesel_w)) * dt_h

        for t in range(horizon_steps):
            # 1. Total available renewable power
            p_solar_avail = float(bundle.solar_generation.point[t]) if t < len(bundle.solar_generation.point) else 0.0
            p_wind_avail = float(bundle.wind_generation.point[t]) if t < len(bundle.wind_generation.point) else 0.0
            p_ren_avail = p_solar_avail + p_wind_avail

            # 2. Protected critical demand (Synthetic fixture uses demand forecast)
            p_crit_demand = float(bundle.demand.point[t]) if t < len(bundle.demand.point) else 0.0

            # 3. Direct Renewable Dispatch to Protected Load
            p_ren_to_load = min(p_ren_avail, p_crit_demand)
            p_curtail_pre = max(0.0, p_ren_avail - p_ren_to_load)
            p_rem_demand = p_crit_demand - p_ren_to_load

            # 3b. Renewable-Surplus-to-Battery Charging
            # (ems/reports/diesel_and_loads/OPTION_D_RENEWABLE_CHARGING_SECTION6_REVIEW.md Section 3).
            # Fires only when there IS a renewable surplus (p_curtail_pre >
            # 0), which by the structural invariant p_curtail_pre > 0 =>
            # p_rem_demand == 0 means this branch can never be live in the
            # same step as the resource-preservation dispatch block below
            # that sets p_diesel/p_dis. The two charging paths (this one,
            # and the pre-existing excess-diesel path at "5. Excess Diesel
            # Generation Battery Charging" below) are therefore mutually
            # exclusive within a step by construction, not by an added
            # guard. Uses the same SOC-ceiling / charge-power / efficiency
            # expressions as that existing excess-diesel path.
            p_ren_to_chg = 0.0
            if p_curtail_pre > 0.0:
                headroom_dc_wh = max(0.0, max_e_wh - curr_e_wh)
                max_chg_avail_w = min(max_chg_w, (headroom_dc_wh / eta_chg) / dt_h)
                p_ren_to_chg = min(max_chg_avail_w, p_curtail_pre)
            p_curtail = p_curtail_pre - p_ren_to_chg

            # Track solar / wind split, EXTENDED to include the newly-
            # charged renewable energy so that renewable_utilization_pct's
            # numerator (solar_used + wind_used) reflects surplus that was
            # banked into the battery, not just surplus that served load
            # directly.
            p_ren_used_total = p_ren_to_load + p_ren_to_chg
            if p_ren_avail > 0:
                p_sol_used = p_ren_used_total * (p_solar_avail / p_ren_avail)
                p_win_used = p_ren_used_total * (p_wind_avail / p_ren_avail)
            else:
                p_sol_used = 0.0
                p_win_used = 0.0

            solar_used.append(p_sol_used)
            wind_used.append(p_win_used)
            renewable_curtailment.append(p_curtail)

            # Usable battery energy at step t
            usable_dc_wh = max(0.0, curr_e_wh - min_e_wh)
            max_dis_avail_w = min(max_dis_w, (usable_dc_wh * eta_dis) / dt_h)

            p_diesel = 0.0
            p_dis = 0.0
            # was: p_chg = 0.0 -- now defaults to the renewable-surplus
            # charge computed above. Per the mutual-exclusivity invariant
            # documented above, the pre-existing excess-diesel branch below
            # can never overwrite a nonzero p_ren_to_chg in the same step
            # (p_ren_to_chg > 0 implies p_diesel stays 0.0 this step).
            p_chg = p_ren_to_chg

            # Feasibility & Power Cap (can_run_diesel and eff_max_diesel_w)
            can_run_diesel = (available_fuel >= min_step_fuel_l) and (min_diesel_w <= max_diesel_w)
            if can_run_diesel:
                if marginal_lpwh > 0.0:
                    raw_fuel_power_w = ((available_fuel / dt_h) - base_lph) / marginal_lpwh
                    max_fuel_power_w = max(min_diesel_w, raw_fuel_power_w)
                    eff_max_diesel_w = min(max_diesel_w, max_fuel_power_w)
                    # Floating-point boundary guard: ensure required fuel does not exceed available_fuel
                    if (base_lph + (marginal_lpwh * eff_max_diesel_w)) * dt_h > available_fuel and eff_max_diesel_w > min_diesel_w:
                        eff_max_diesel_w = max(min_diesel_w, math.nextafter(eff_max_diesel_w, min_diesel_w))
                else:
                    eff_max_diesel_w = max_diesel_w
            else:
                eff_max_diesel_w = 0.0

            # 4. Resource Preservation Dispatch Logic (E3 Rules)
            if p_rem_demand > 0:
                if assessment.preserved_resource in (
                    ResourceSelection.BATTERY,
                    ResourceSelection.DIESEL,
                ):
                    # Unified discretionary battery-first policy:
                    # Usable battery power above the 20% floor is dispatched first
                    p_dis = min(max_dis_avail_w, p_rem_demand)
                    p_rem_after_bat = max(0.0, p_rem_demand - p_dis)

                    # Generator runs for remainder only if battery is insufficient and fuel available
                    if p_rem_after_bat > 0 and can_run_diesel:
                        p_diesel_req = max(min_diesel_w, p_rem_after_bat)
                        p_diesel = min(eff_max_diesel_w, p_diesel_req)
                        # Sequencing correction (RT-01 approach a'): diesel's
                        # mandatory minimum-power floor is non-negotiable once
                        # diesel is committed to run. If that floor forces
                        # p_diesel above the true remainder still owed after
                        # battery (p_rem_after_bat), the battery's
                        # discharge sized above must be reduced so it is never
                        # sized against demand diesel's floor already covers
                        # -- otherwise the same demand gets supplied twice
                        # (once by diesel's forced floor, once by the
                        # battery), producing an unaccounted bus-bar surplus.
                        # This accounts for diesel's floor BEFORE finalizing
                        # battery discharge, rather than reconciling after the
                        # fact. See ems/reports/diesel_and_loads/OPTION_D_DIESEL_FLOOR_REPAIR_PROPOSAL.md
                        # Section 3, approach (a'). Only applies when the
                        # floor actually binds (p_diesel exceeds what was
                        # needed); a diesel capacity (max_power_w) limit can
                        # only reduce p_diesel, never trigger this branch, so
                        # existing priority semantics are otherwise unchanged.
                        if p_diesel > p_rem_after_bat:
                            p_dis = max(0.0, min(max_dis_avail_w, p_rem_demand - p_diesel))

                    # Emergency battery release: if diesel is fuel-capped or power-capped and cannot cover remainder
                    p_rem_unmet = max(0.0, p_rem_demand - (p_dis + p_diesel))
                    if p_rem_unmet > 0:
                        p_dis = min(max_dis_avail_w, p_dis + p_rem_unmet)

                else:  # BOTH / TIE / NONE
                    # Guard: If diesel is eligible to run, but residual demand is below diesel
                    # minimum, committing diesel forces an unabsorbable surplus (min_diesel_w - p_rem_demand)
                    # whenever that surplus exceeds available battery charging headroom. If the battery
                    # has sufficient discharge capacity to serve p_rem_demand, route entirely to battery.
                    headroom_dc_wh = max(0.0, max_e_wh - curr_e_wh)
                    max_chg_avail_w = min(max_chg_w, (headroom_dc_wh / eta_chg) / dt_h)
                    if can_run_diesel and (0.0 < p_rem_demand < min_diesel_w) and ((min_diesel_w - p_rem_demand) > max_chg_avail_w) and (max_dis_avail_w >= p_rem_demand):
                        p_dis = p_rem_demand
                        p_diesel = 0.0
                        p_rem_after_bat = 0.0
                    else:
                        # Balanced dispatch: Use battery up to 50% max discharge, then diesel
                        half_dis_w = min(max_dis_avail_w, p_rem_demand * 0.5)
                        p_dis = half_dis_w
                        p_rem_after_bat = max(0.0, p_rem_demand - p_dis)

                    if p_rem_after_bat > 0 and can_run_diesel:
                        p_diesel_req = max(min_diesel_w, p_rem_after_bat)
                        p_diesel = min(eff_max_diesel_w, p_diesel_req)
                        # Same sequencing correction as the DIESEL-preserved
                        # branch above: if diesel's floor forces it above the
                        # true balanced remainder (p_rem_after_bat), resize
                        # the battery's 50% share down so the floor is
                        # accounted for before battery dispatch is finalized,
                        # never double-supplying the same demand.
                        if p_diesel > p_rem_after_bat:
                            p_dis = max(0.0, min(max_dis_avail_w, p_rem_demand - p_diesel))

                    # Release remaining usable battery if unserved demand remains
                    p_rem_unmet = max(0.0, p_rem_demand - (p_dis + p_diesel))
                    if p_rem_unmet > 0:
                        p_dis = min(max_dis_avail_w, p_dis + p_rem_unmet)

            # 5. Excess Diesel Generation Battery Charging
            # Excess diesel power can charge battery ONLY when diesel is running for load AND battery is not discharging
            if p_diesel > 0 and p_dis == 0:
                excess_diesel_w = max(0.0, p_diesel - p_rem_demand)
                if excess_diesel_w > 0:
                    headroom_dc_wh = max(0.0, max_e_wh - curr_e_wh)
                    max_chg_avail_w = min(max_chg_w, (headroom_dc_wh / eta_chg) / dt_h)
                    p_chg = min(max_chg_avail_w, excess_diesel_w)

            # Update fuel state if diesel ran
            if p_diesel > 0:
                fuel_step = (base_lph + (marginal_lpwh * p_diesel)) * dt_h
                available_fuel = max(0.0, available_fuel - fuel_step)

            # Update battery state
            curr_e_wh += (p_chg * eta_chg - (p_dis / eta_dis)) * dt_h
            curr_e_wh = max(min_e_wh, min(max_e_wh, curr_e_wh))
            soc_val = (curr_e_wh / capacity_wh) * 100.0

            battery_charge.append(p_chg)
            battery_discharge.append(p_dis)
            battery_soc.append(round(soc_val, 2))
            diesel_power.append(p_diesel)

            # 6. Served and Unmet Load Accounting
            p_total_served = p_ren_to_load + p_dis + min(p_diesel, p_rem_demand)
            p_served_actual = min(p_crit_demand, p_total_served)
            p_unmet = max(0.0, p_crit_demand - p_served_actual)

            # Proportional allocation scaling factor (alpha)
            if p_crit_demand > 0:
                alpha = min(1.0, p_total_served / p_crit_demand)
            else:
                alpha = 1.0

            load_served.append(p_served_actual)
            unmet_load.append(p_unmet)

            # Honest energy-balance audit trail: recompute the same bus-bar
            # residual the repository's own conservation test checks, from
            # this timestep's actual dispatch values, instead of claiming
            # zero unconditionally.
            bus_bar_err = abs(
                (p_sol_used + p_win_used + p_dis + p_diesel)
                - (p_served_actual + flexible_load_schedule[t] + p_chg)
            )
            energy_balance_errors.append(round(bus_bar_err, 6))

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
            objective_value=0.0,  # Option D is heuristic fallback, not MILP objective minimization
            constraint_status="OPTION_D_FALLBACK",
            energy_balance_errors=energy_balance_errors
        )
