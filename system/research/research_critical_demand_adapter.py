"""
POLARIS Research-Only Critical Demand Governance Adapter
Module: system.research.research_critical_demand_adapter

Implements the canonical POLARIS worker critical-demand adaptation formula:
    critical_demand[t] = min(critical_load_baseline_w, total_demand[t])
as established in:
    - system/orchestration/worker.py:244 (Cell B production orchestration path)
    - system/tests/test_demand_critical_config_path.py (regression specification)

PHYSICAL & GOVERNANCE INVARIANT:
In microgrid busbar balance, critical load cannot exceed total demand (cp <= dp).
The governed baseline power (11,600.0 W in system/config/loads.yaml:5) represents
the governed critical-load ceiling, not a mandatory minimum total demand floor.
When total forecast demand drops below 11.6 kW, critical demand is clipped down
to total demand, ensuring 100% of demand is treated as critical without violating
the physical invariant cp <= dp.

ZERO PRODUCTION CODE MODIFIED:
- GAP19 (system/optimization/implementations/gap19_highs_native.py) is untouched.
- EMSControlRouter (system/control/router.py) is untouched.
- Canonical configs (system/config/*.yaml) are untouched.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from system.schemas.station_state import StationState
from system.research.route_mode_propagation import propagate_route_mode
from system.schemas.forecast_bundle import ForecastBundle
from system.research.closed_loop_causal_nwp_runner import (
    ClosedLoopCausalNwpRunner,
    ClosedLoopExecutionReport,
    ClosedLoopStepRecord
)


def adapt_critical_demand_vector(baseline_power_w: float, demand_points: List[float]) -> List[float]:
    """
    Canonical POLARIS worker critical-load clipping formula.
    Matches system/orchestration/worker.py:244 and test_demand_critical_config_path.py.
    """
    return [min(float(baseline_power_w), float(d)) for d in demand_points]


class AdaptedClosedLoopRunner(ClosedLoopCausalNwpRunner):
    """
    Research-only closed-loop receding-horizon runner with canonical
    critical-demand adaptation enabled.
    Inherits ClosedLoopCausalNwpRunner and ensures GAP19 receives
    the canonical clipped critical-load vector at every hourly cycle.
    """

    def __init__(self, configs: Dict[str, Any]):
        super().__init__(configs)
        self.critical_ceiling_w = float(
            self.configs.get("loads", {}).get("critical_load", {}).get(
                "baseline_power_w",
                self.configs.get("critical_demand_baseline_w", 11600.0)
            )
        )

    def run_closed_loop(
        self,
        initial_state: StationState,
        hours_to_run: int,
        weather_dataset: pd.DataFrame,
        realized_solar: List[float],
        realized_wind: List[float],
        realized_demand: List[float],
        realized_timestamps: List[str]
    ) -> ClosedLoopExecutionReport:
        if hours_to_run <= 0:
            raise ValueError(f"hours_to_run must be positive, got {hours_to_run}.")

        if (len(realized_solar) < hours_to_run or len(realized_wind) < hours_to_run or
                len(realized_demand) < hours_to_run or len(realized_timestamps) < hours_to_run):
            raise ValueError(
                f"Realized trajectory lengths must be >= hours_to_run ({hours_to_run})."
            )

        weather_df = weather_dataset.copy()
        if "dt" not in weather_df.columns:
            weather_df["dt"] = pd.to_datetime(weather_df["timestamp"], utc=True)
        weather_lookup = weather_df.set_index("dt")["fc_cloud_cover"].to_dict()

        current_state = initial_state
        step_records: List[ClosedLoopStepRecord] = []
        reoptimizations_count = 0

        cum_served = 0.0
        cum_unmet = 0.0
        cum_curtail = 0.0
        cum_fuel = 0.0
        cum_diesel_e = 0.0
        cum_solar = 0.0
        cum_wind = 0.0

        for step in range(hours_to_run):
            origin_dt = self._parse_iso(current_state.timestamp)
            target_ts_str = realized_timestamps[step]

            # 1. Extract 24 future hourly target timestamps for current origin
            target_dts = [origin_dt + pd.Timedelta(hours=h) for h in range(1, 25)]
            cloud_trajectory: List[float] = []

            for h_dt in target_dts:
                if h_dt in weather_lookup:
                    c_val = weather_lookup[h_dt]
                    cloud_trajectory.append(float(c_val))
                else:
                    raise ValueError(
                        f"CAUSAL_DATA_UNAVAILABLE: Timestamp {h_dt} not found in causal weather dataset."
                    )

            # 2. Forecaster generates 24h ForecastBundle
            forecast_context = {"fc_cloud_cover": cloud_trajectory}
            bundle = self.forecast_engine.predict(current_state, forecast_context)

            # 3. Router policy evaluation
            assessment, route_mode = self.router.evaluate_and_route(current_state, bundle, self.configs)
            planning_state = propagate_route_mode(current_state, route_mode)

            # 4. Canonical Critical Demand Adaptation (worker.py:244 pattern)
            step_configs = dict(self.configs)
            step_configs["critical_demand_w"] = adapt_critical_demand_vector(
                self.critical_ceiling_w, bundle.demand.point
            )

            # 5. Fresh GAP19 Multi-Objective Optimization
            reoptimizations_count += 1
            plan = self.optimizer.optimize(bundle, planning_state, step_configs)

            if plan.constraint_status not in ("OPTIMAL", "FEASIBLE"):
                raise RuntimeError(
                    f"GAP19 optimization failed at step {step}: status={plan.constraint_status}"
                )

            # 6. Extract ONLY timestep 0 from the 24-hour plan
            p_chg_0 = float(plan.battery_charge[0])
            p_dis_0 = float(plan.battery_discharge[0])
            p_diesel_0 = float(plan.diesel_power[0])

            # 7. Execute timestep 0 through ResearchRealizationExecutor
            realized_inputs = {
                "timestamp": target_ts_str,
                "actual_SW_IN": float(realized_solar[step]),
                "actual_wind_generation": float(realized_wind[step]),
                "actual_demand": float(realized_demand[step])
            }
            realization_res = self.executor.execute_step(current_state, plan, realized_inputs, step_index=0)

            # 8. Physical and accounting invariant checks
            if realization_res.busbar_energy_balance_error_w > 1e-3:
                raise RuntimeError(f"Busbar balance error {realization_res.busbar_energy_balance_error_w} W.")
            if realization_res.realized_soc_pct < 19.999 or realization_res.realized_soc_pct > 95.001:
                raise RuntimeError(f"SOC {realization_res.realized_soc_pct}% out of bounds [20, 95].")
            if realization_res.diesel_fuel_remaining_l < -1e-6:
                raise RuntimeError(f"Negative fuel {realization_res.diesel_fuel_remaining_l} L.")
            if p_chg_0 > 1e-3 and p_dis_0 > 1e-3:
                raise RuntimeError(f"Simultaneous charge and discharge.")

            rec = ClosedLoopStepRecord(
                step_index=step,
                origin_timestamp=current_state.timestamp,
                target_timestamp=target_ts_str,
                route_mode=route_mode,
                optimizer_status=plan.constraint_status,
                j1_deficit_wh=plan.j1_objective if plan.j1_objective is not None else 0.0,
                j2_shortfall_wh=plan.j2_objective if plan.j2_objective is not None else 0.0,
                j3_fuel_l=plan.j3_objective if plan.j3_objective is not None else 0.0,
                planned_battery_charge_w=p_chg_0,
                planned_battery_discharge_w=p_dis_0,
                planned_diesel_power_w=p_diesel_0,
                realized_solar_w=realization_res.solar_realized_w,
                realized_wind_w=realization_res.wind_realized_w,
                realized_demand_w=realization_res.demand_realized_w,
                realized_diesel_w=realization_res.diesel_realized_w,
                realized_battery_charge_w=realization_res.battery_charge_realized_w,
                realized_battery_discharge_w=realization_res.battery_discharge_realized_w,
                served_load_w=realization_res.served_load_w,
                unmet_load_w=realization_res.unmet_load_w,
                curtailment_w=realization_res.curtailment_w,
                realized_battery_energy_wh=realization_res.realized_battery_energy_wh,
                realized_soc_pct=realization_res.realized_soc_pct,
                diesel_fuel_consumed_l=realization_res.diesel_fuel_consumed_l,
                diesel_fuel_remaining_l=realization_res.diesel_fuel_remaining_l,
                diesel_running=realization_res.diesel_running,
                busbar_balance_error_w=realization_res.busbar_energy_balance_error_w
            )
            step_records.append(rec)

            cum_served += realization_res.served_load_w
            cum_unmet += realization_res.unmet_load_w
            cum_curtail += realization_res.curtailment_w
            cum_fuel += realization_res.diesel_fuel_consumed_l
            cum_diesel_e += realization_res.diesel_realized_w
            cum_solar += realization_res.solar_realized_w
            cum_wind += realization_res.wind_realized_w

            current_state = realization_res.next_state

        return ClosedLoopExecutionReport(
            execution_status="SUCCESS",
            total_hours_executed=hours_to_run,
            reoptimizations_count=reoptimizations_count,
            initial_state=initial_state,
            final_state=current_state,
            step_records=step_records,
            cumulative_served_load_wh=round(cum_served, 2),
            cumulative_unmet_load_wh=round(cum_unmet, 2),
            cumulative_curtailment_wh=round(cum_curtail, 2),
            cumulative_diesel_fuel_l=round(cum_fuel, 4),
            cumulative_diesel_energy_wh=round(cum_diesel_e, 2),
            cumulative_solar_realized_wh=round(cum_solar, 2),
            cumulative_wind_realized_wh=round(cum_wind, 2)
        )
