"""
POLARIS Research-Only Hourly Closed-Loop Causal NWP Runner
Module: system.research.closed_loop_causal_nwp_runner

RESEARCH USE ONLY / CLOSED-LOOP REPLANNED EMS HARNESS:
Implements genuine hourly receding-horizon control:
    hour t
      ↓
    causal forecast (MEPS 18Z cloud trajectory + PVLIB clear-sky)
      ↓
    EMSControlRouter policy evaluation
      ↓
    GAP19 HiGHS Native Lexicographic Multi-Objective Optimization
      ↓
    extract ONLY dispatch_plan timestep 0 (discard remaining 23 steps)
      ↓
    realized environmental realization (actual solar, wind, demand)
      ↓
    ResearchRealizationExecutor (busbar balance, battery/diesel physical updates)
      ↓
    next StationState
      ↓
    hour t+1
      ↓
    repeat

Strict Causality & Governance:
- Zero actual observations passed to the forecast engine.
- Zero production simulator modifications (system/simulation/simulator.py untouched).
- Zero GAP19 or Stage 8.1 modifications.
- At every hour, a fresh optimization is performed from the current StationState.
- Every hour's energy balance, SOC bounds, and fuel non-negativity are verified with fail-closed safety assertions.
"""

import math
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Union

import pandas as pd

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.dispatch_plan import DispatchPlan
from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
from system.control.router import EMSControlRouter
from system.research.route_mode_propagation import propagate_route_mode
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.simulation.research_realization_executor import (
    ResearchRealizationExecutor,
    RealizationResult
)


@dataclass
class ClosedLoopStepRecord:
    step_index: int
    origin_timestamp: str
    target_timestamp: str
    route_mode: str
    optimizer_status: str
    j1_deficit_wh: float
    j2_shortfall_wh: float
    j3_fuel_l: float
    planned_battery_charge_w: float
    planned_battery_discharge_w: float
    planned_diesel_power_w: float
    realized_solar_w: float
    realized_wind_w: float
    realized_demand_w: float
    realized_diesel_w: float
    realized_battery_charge_w: float
    realized_battery_discharge_w: float
    served_load_w: float
    unmet_load_w: float
    curtailment_w: float
    realized_battery_energy_wh: float
    realized_soc_pct: float
    diesel_fuel_consumed_l: float
    diesel_fuel_remaining_l: float
    diesel_running: bool
    busbar_balance_error_w: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "origin_timestamp": self.origin_timestamp,
            "target_timestamp": self.target_timestamp,
            "route_mode": self.route_mode,
            "optimizer_status": self.optimizer_status,
            "j1_deficit_wh": self.j1_deficit_wh,
            "j2_shortfall_wh": self.j2_shortfall_wh,
            "j3_fuel_l": self.j3_fuel_l,
            "planned_battery_charge_w": self.planned_battery_charge_w,
            "planned_battery_discharge_w": self.planned_battery_discharge_w,
            "planned_diesel_power_w": self.planned_diesel_power_w,
            "realized_solar_w": self.realized_solar_w,
            "realized_wind_w": self.realized_wind_w,
            "realized_demand_w": self.realized_demand_w,
            "realized_diesel_w": self.realized_diesel_w,
            "realized_battery_charge_w": self.realized_battery_charge_w,
            "realized_battery_discharge_w": self.realized_battery_discharge_w,
            "served_load_w": self.served_load_w,
            "unmet_load_w": self.unmet_load_w,
            "curtailment_w": self.curtailment_w,
            "realized_battery_energy_wh": self.realized_battery_energy_wh,
            "realized_soc_pct": self.realized_soc_pct,
            "diesel_fuel_consumed_l": self.diesel_fuel_consumed_l,
            "diesel_fuel_remaining_l": self.diesel_fuel_remaining_l,
            "diesel_running": self.diesel_running,
            "busbar_balance_error_w": self.busbar_balance_error_w
        }


@dataclass
class ClosedLoopExecutionReport:
    execution_status: str
    total_hours_executed: int
    reoptimizations_count: int
    initial_state: StationState
    final_state: StationState
    step_records: List[ClosedLoopStepRecord] = field(default_factory=list)
    cumulative_served_load_wh: float = 0.0
    cumulative_unmet_load_wh: float = 0.0
    cumulative_curtailment_wh: float = 0.0
    cumulative_diesel_fuel_l: float = 0.0
    cumulative_diesel_energy_wh: float = 0.0
    cumulative_solar_realized_wh: float = 0.0
    cumulative_wind_realized_wh: float = 0.0


class ClosedLoopCausalNwpRunner:
    """
    Orchestrates hourly receding-horizon closed-loop execution.
    """

    def __init__(self, configs: Dict[str, Any]):
        self.configs = configs
        self.forecast_engine = CausalNwpPhysicsForecastEngine()
        self.router = EMSControlRouter()
        self.optimizer = GAP19HighsNativeOptimizer()
        self.executor = ResearchRealizationExecutor(configs)

    def _parse_iso(self, ts_str: str) -> datetime:
        clean = ts_str.replace("Z", "+00:00") if ts_str.endswith("Z") else ts_str
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

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
        """
        Executes hours_to_run cycles of receding-horizon control.

        Args:
            initial_state: Governed starting StationState at t0.
            hours_to_run: Number of hourly control cycles to execute.
            weather_dataset: DataFrame containing 'timestamp' and 'fc_cloud_cover'.
            realized_solar: List of actual SW_IN (W/m^2) for each executed hour.
            realized_wind: List of actual wind generation (W) for each executed hour.
            realized_demand: List of actual demand (W) for each executed hour.
            realized_timestamps: List of timestamp strings for each executed hour (t+1, t+2, ...).
        """
        if hours_to_run <= 0:
            raise ValueError(f"hours_to_run must be positive, got {hours_to_run}.")

        if len(realized_solar) < hours_to_run or len(realized_wind) < hours_to_run or len(realized_demand) < hours_to_run or len(realized_timestamps) < hours_to_run:
            raise ValueError(
                f"Realized trajectory lengths (solar={len(realized_solar)}, wind={len(realized_wind)}, "
                f"demand={len(realized_demand)}, ts={len(realized_timestamps)}) must be >= hours_to_run ({hours_to_run})."
            )

        # Build fast lookup for causal weather forecasts
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

            # 1. Extract exactly 24 future hourly target timestamps for current origin
            target_dts = [origin_dt + timedelta(hours=h) for h in range(1, 25)]
            cloud_trajectory: List[float] = []

            for h_dt in target_dts:
                # Lookup in weather dataset
                if h_dt in weather_lookup:
                    c_val = weather_lookup[h_dt]
                    if math.isnan(c_val) or math.isinf(c_val):
                        raise ValueError(f"NaN/Inf causal cloud value at timestamp {h_dt}.")
                    cloud_trajectory.append(float(c_val))
                else:
                    raise ValueError(
                        f"CAUSAL_DATA_UNAVAILABLE: Timestamp {h_dt} not found in causal weather dataset. "
                        "Cannot construct causal 24h horizon."
                    )

            # 2. Causal Forecaster generates new 24h ForecastBundle
            # STRICT FIREWALL: Pass ONLY fc_cloud_cover. Actuals are forbidden.
            forecast_context = {"fc_cloud_cover": cloud_trajectory}
            bundle = self.forecast_engine.predict(current_state, forecast_context)

            # 3. EMS Control Router Policy Assessment
            assessment, route_mode = self.router.evaluate_and_route(current_state, bundle, self.configs)
            planning_state = propagate_route_mode(current_state, route_mode)

            # 4. Fresh GAP19 Multi-Objective Optimization
            reoptimizations_count += 1
            plan = self.optimizer.optimize(bundle, planning_state, self.configs)

            if plan.constraint_status not in ("OPTIMAL", "FEASIBLE"):
                raise RuntimeError(
                    f"GAP19 optimization failed at step {step} (origin {current_state.timestamp}): "
                    f"status={plan.constraint_status}"
                )

            # 5. Extract ONLY timestep 0 from the 24-hour plan
            p_chg_0 = float(plan.battery_charge[0])
            p_dis_0 = float(plan.battery_discharge[0])
            p_diesel_0 = float(plan.diesel_power[0])

            # 6. Execute timestep 0 through ResearchRealizationExecutor using REALIZED inputs
            realized_inputs = {
                "timestamp": target_ts_str,
                "actual_SW_IN": float(realized_solar[step]),
                "actual_wind_generation": float(realized_wind[step]),
                "actual_demand": float(realized_demand[step])
            }
            realization_res = self.executor.execute_step(current_state, plan, realized_inputs, step_index=0)

            # 7. Safety & Accounting Invariants Check
            if realization_res.busbar_energy_balance_error_w > 1e-3:
                raise RuntimeError(
                    f"Safety invariant breach at step {step}: Busbar balance error {realization_res.busbar_energy_balance_error_w} W."
                )

            if realization_res.realized_soc_pct < 19.999 or realization_res.realized_soc_pct > 95.001:
                raise RuntimeError(
                    f"Safety invariant breach at step {step}: SOC {realization_res.realized_soc_pct}% out of bounds [20, 95]."
                )

            if realization_res.diesel_fuel_remaining_l < -1e-6:
                raise RuntimeError(
                    f"Safety invariant breach at step {step}: Negative fuel {realization_res.diesel_fuel_remaining_l} L."
                )

            if p_chg_0 > 1e-3 and p_dis_0 > 1e-3:
                raise RuntimeError(
                    f"Safety invariant breach at step {step}: Simultaneous planned charge ({p_chg_0}) and discharge ({p_dis_0})."
                )

            # Record step metrics
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

            # 8. State update: next_state becomes state for next hour
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
