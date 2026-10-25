"""
ORACLE runner (EXP-PLANNER-CF-CONSISTENCY-2025, §6.2–6.3).

Diagnostic perfect-foresight bounds. NOT candidates. NOT deployable.

  ORACLE-PHYS (PRIMARY, used for NG7): reserve-free (Layer C and J2 removed), customer-first
      Planner-CF v1 MILP, perfect-foresight horizon (realized inputs), Arm A realization.
  ORACLE-CTRL (SECONDARY): as ORACLE-PHYS but with the Control governed EBR reserve (reserve on).

Future-input definitions (preregistration §6.3), exactly:
  calendar : origin = forecast_start, 00:00 UTC. Offset j counts hours from origin 00:00.
             Re-solve at step t (t = 0..23) uses horizon offsets j = t .. t+23 (max j = 46).
             Realized step s uses offset j = s (hour s of the origin day).
  solar    : S_pv(j) = min(max(0, SW_IN(T) * 300 * 0.20 * 0.85), 60000 W),
             T = origin + j hours, SW_IN from data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv
             (same conversion as executor.pv_from_sw_in).
  wind     : W(j) = max(0, round(4500 + 5000*sin((j+1)*pi/6), 2))
  demand   : D(j) = max(10000, round(15000 + 3000*cos((j+1)*pi/12), 2))
  critical : D_c(j) = min(11600, D(j))
  coverage : G12 — SITES file must contain every T used; otherwise the origin is BLOCKED.

Harness: reuses the executor (Arm A realization), the router and mode propagation
(system/control/router.py, system/research/route_mode_propagation.py), and the planned-
telemetry wrapper. No production file is modified.

This module defines the runner. It is NOT executed in this task.
"""

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import hashlib
import pandas as pd
import yaml

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from system.schemas.station_state import StationState  # noqa: E402
from system.control.router import EMSControlRouter  # noqa: E402
from system.research.route_mode_propagation import propagate_route_mode  # noqa: E402
from system.simulation.research_realization_executor import ResearchRealizationExecutor  # noqa: E402

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from research_numerical_extractor_planner_cf_v1 import PlannerCFV1Optimizer  # noqa: E402
from planned_telemetry_harness import PlannedTelemetryHarness  # noqa: E402
from planned_execution_telemetry import ExecutedHourRecorder  # noqa: E402

SITES_SW_IN_PATH = _REPO / "data" / "POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv"
SITES_SW_IN_SHA256 = "d457facdbeb57b9c582b623c524c0f50717306ca083ab93028f1bd700d1e7a2e"
WEATHER_2025_PATH = _REPO / "data" / "POLARIS_v0_1_future_weather_forecasts_2025.csv"
CONTROL_EBR_MODULE = _REPO / "experiments" / "stage4_sw_low_sun_2025_holdout" / "stage4_low_sun_adapter.py"

ORACLE_VARIANTS = ("ORACLE-PHYS", "ORACLE-CTRL")
PV_AREA_M2 = 300.0
PV_EFF = 0.20
PV_PR = 0.85
PV_MAX_W = 60000.0


class OracleInputError(RuntimeError):
    """Raised when an oracle input violates the preregistered definition (incl. G12)."""


def verify_solar_source() -> str:
    """Return the SHA-256 of the authoritative solar file; raise if it differs from the pin."""
    digest = hashlib.sha256(SITES_SW_IN_PATH.read_bytes()).hexdigest()
    if digest != SITES_SW_IN_SHA256:
        raise OracleInputError(f"solar source hash mismatch: {digest} != {SITES_SW_IN_SHA256}")
    return digest


def load_sw_in_lookup() -> Dict[str, float]:
    """Map 'YYYY-MM-DD HH:MM:SS' -> SW_IN (W/m^2) from the authoritative SITES file."""
    verify_solar_source()
    df = pd.read_csv(SITES_SW_IN_PATH)
    return {str(ts): float(v) for ts, v in zip(df["TIMESTAMP"], df["SW_IN"])}


def origins_2025_may_aug() -> List[pd.Timestamp]:
    """The 123 forecast_start origins of the preregistered population (2025-05-01..2025-08-31)."""
    w = pd.read_csv(WEATHER_2025_PATH, usecols=["forecast_start"])
    starts = sorted(set(pd.to_datetime(w["forecast_start"])))
    out = [s for s in starts
           if pd.Timestamp("2025-05-01") <= s <= pd.Timestamp("2025-08-31")]
    if len(out) != 123:
        raise OracleInputError(f"expected 123 origins, found {len(out)}")
    return out


def wind_w(j: int) -> float:
    return max(0.0, round(4500.0 + 5000.0 * math.sin((j + 1) * math.pi / 6.0), 2))


def demand_w(j: int) -> float:
    return max(10000.0, round(15000.0 + 3000.0 * math.cos((j + 1) * math.pi / 12.0), 2))


def critical_w(j: int) -> float:
    return min(11600.0, demand_w(j))


def pv_from_sw_in(sw_in: float) -> float:
    raw = float(sw_in) * PV_AREA_M2 * PV_EFF * PV_PR
    return max(0.0, min(raw, PV_MAX_W))


def solar_w(lookup: Dict[str, float], origin: pd.Timestamp, j: int) -> float:
    key = (origin + pd.Timedelta(hours=j)).strftime("%Y-%m-%d %H:%M:%S")
    if key not in lookup:
        raise OracleInputError(f"G12: SITES SW_IN missing for {key}")
    return pv_from_sw_in(lookup[key])


def ts_label(origin: pd.Timestamp, j: int) -> str:
    return (origin + pd.Timedelta(hours=j)).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class HorizonBundle:
    """Minimal bundle exposing the attributes the optimizer and router read."""
    timestamps: List[str]
    solar_generation: Any
    wind_generation: Any
    demand: Any
    demand_critical: Any = None
    origin_timestamp: str = ""


@dataclass
class _Series:
    point: List[float]


def build_horizon(origin: pd.Timestamp, step: int, lookup: Dict[str, float]) -> HorizonBundle:
    js = list(range(step, step + 24))
    solar = [solar_w(lookup, origin, j) for j in js]
    wind = [wind_w(j) for j in js]
    dem = [demand_w(j) for j in js]
    return HorizonBundle(
        timestamps=[ts_label(origin, j) for j in js],
        solar_generation=_Series(solar),
        wind_generation=_Series(wind),
        demand=_Series(dem),
        demand_critical=None,
        origin_timestamp=ts_label(origin, step),
    )


def _initial_state(origin: pd.Timestamp) -> StationState:
    return StationState(
        timestamp=ts_label(origin, -1),
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=4500.0,
        diesel_fuel_remaining_liters=100.0,
        operating_mode="NORMAL",
    )


def canonical_configs() -> Dict[str, Any]:
    def rd(p: str) -> Dict[str, Any]:
        with open(_REPO / p) as f:
            return yaml.safe_load(f)
    return {
        "battery": rd("system/config/battery.yaml"),
        "diesel": rd("system/config/diesel.yaml"),
        "solar_pv": rd("system/config/solar_pv.yaml"),
        "loads": rd("system/config/loads.yaml"),
        "critical_demand_baseline_w": 11600.0,
        "terminal_target_wh": 100000.0,
    }


def _control_governed_ebr(critical: List[float]) -> List[float]:
    import importlib.util
    spec = importlib.util.spec_from_file_location("stage4_low_sun_adapter_readonly", CONTROL_EBR_MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.compute_governed_ebr(critical)


@dataclass
class OracleOriginResult:
    origin: str
    variant: str
    hourly: List[Dict[str, Any]] = field(default_factory=list)
    planned: List[Dict[str, Any]] = field(default_factory=list)
    executed: List[Dict[str, Any]] = field(default_factory=list)
    audit: List[Dict[str, Any]] = field(default_factory=list)  # A2 audit records (additive; no realization effect)
    route_by_step: List[str] = field(default_factory=list)
    optimizer_status: List[str] = field(default_factory=list)


def audit_row(origin_index: int, step: int, bundle: Any, plan: Any, optimizer: Any,
              state_before: Any, res: Any) -> Dict[str, Any]:
    """A2 audit record for one executed hour: planned hour-0 values, the planned 24-hour horizon,
    the pre-step state, and the realized values. Pure read of existing objects; changes nothing."""
    lp = optimizer.last_planned[0]
    horizon = {
        "forecast_solar": [float(v) for v in bundle.solar_generation.point],
        "forecast_wind": [float(v) for v in bundle.wind_generation.point],
        "P_discharge": [float(v) for v in plan.battery_discharge],
        "P_diesel": [float(v) for v in plan.diesel_power],
        "P_served": [float(v) for v in plan.load_served],
        "P_unmet": [float(v) for v in plan.unmet_load],
        "P_curt": [float(v) for v in plan.renewable_curtailment],
    }
    return {
        "origin_id": int(origin_index), "step": int(step),
        "P_charge_w": float(lp["charge"]), "R_charge_w": float(res.battery_charge_realized_w),
        "P_discharge_w": float(plan.battery_discharge[0]), "R_discharge_w": float(res.battery_discharge_realized_w),
        "P_diesel_w": float(plan.diesel_power[0]), "R_diesel_w": float(res.diesel_realized_w),
        "P_served_w": float(plan.load_served[0]), "R_served_w": float(res.served_load_w),
        "P_unmet_w": float(plan.unmet_load[0]), "R_unmet_w": float(res.unmet_load_w),
        "P_curt_w": float(plan.renewable_curtailment[0]),
        "P_solar_used_w": float(plan.solar_used[0]), "P_wind_used_w": float(plan.wind_used[0]),
        "solar_w": float(res.solar_realized_w), "wind_w": float(res.wind_realized_w),
        "demand_w": float(res.demand_realized_w),
        "forecast_solar_w": float(bundle.solar_generation.point[0]),
        "forecast_wind_w": float(bundle.wind_generation.point[0]),
        "E_before_wh": float(state_before.battery_energy_wh),
        "fuel_before_l": float(state_before.diesel_fuel_remaining_liters),
        "horizon": horizon,
    }


def run_oracle_origin(origin: pd.Timestamp, variant: str, origin_index: int,
                      lookup: Optional[Dict[str, float]] = None,
                      configs: Optional[Dict[str, Any]] = None) -> OracleOriginResult:
    """Run one origin of one oracle variant: 24 perfect-foresight re-solves with Arm A realization.
    Not invoked in this task."""
    if variant not in ORACLE_VARIANTS:
        raise ValueError(f"unknown oracle variant {variant}")
    lookup = lookup if lookup is not None else load_sw_in_lookup()
    cfg = dict(configs if configs is not None else canonical_configs())

    reserve_enabled = variant == "ORACLE-CTRL"
    optimizer = PlannerCFV1Optimizer(reserve_enabled=reserve_enabled)
    harness = PlannedTelemetryHarness(optimizer)
    exec_recorder = ExecutedHourRecorder()
    bat = cfg["battery"]
    e_min_wh = float(bat.get("capacity_wh", 200000.0)) * float(bat.get("min_soc_pct", 20.0)) / 100.0
    eta_dis = float(bat.get("discharge_efficiency", 0.92))
    router = EMSControlRouter()
    executor = ResearchRealizationExecutor(cfg)

    state = _initial_state(origin)
    result = OracleOriginResult(origin=str(origin.date()), variant=variant)

    for step in range(24):
        bundle = build_horizon(origin, step, lookup)
        crit = [critical_w(j) for j in range(step, step + 24)]
        _, route = router.evaluate_and_route(state, bundle, cfg)
        planning_state = propagate_route_mode(state, route)

        step_cfg = dict(cfg)
        step_cfg["critical_demand_w"] = crit
        if reserve_enabled:
            step_cfg["ebr_target_wh"] = _control_governed_ebr(crit)

        plan = harness.optimize(bundle, planning_state, step_cfg,
                                origin_id=origin_index, arm=variant, step=step)
        status = optimizer.last_diagnostics[0]["solver_status"] if optimizer.last_diagnostics else str(plan.constraint_status)
        result.optimizer_status.append(status)
        result.route_by_step.append(route)

        realized = {
            "timestamp": ts_label(origin, step),
            "actual_SW_IN": lookup[(origin + pd.Timedelta(hours=step)).strftime("%Y-%m-%d %H:%M:%S")],
            "actual_wind_generation": wind_w(step),
            "actual_demand": demand_w(step),
        }
        e_start_wh = state.battery_energy_wh  # realized start-of-hour energy E_t (before execution)
        res = executor.execute_step(state, plan, realized, step_index=0)
        if res.busbar_energy_balance_error_w > 1e-3:
            raise RuntimeError(f"busbar error {res.busbar_energy_balance_error_w} W at step {step}")
        exec_recorder.record_resolve(
            origin_id=origin_index, arm=variant, step=step, planned_rows=optimizer.last_planned,
            e_start_wh=e_start_wh, pv_real_w=res.solar_realized_w, wind_real_w=res.wind_realized_w,
            d_c_real_w=critical_w(step), e_min_wh=e_min_wh, eta_dis=eta_dis)
        result.hourly.append({
            "step": step, "route": route, "solar_w": res.solar_realized_w, "wind_w": res.wind_realized_w,
            "demand_w": res.demand_realized_w, "served_w": res.served_load_w, "unmet_w": res.unmet_load_w,
            "charge_w": res.battery_charge_realized_w, "discharge_w": res.battery_discharge_realized_w,
            "diesel_w": plan.diesel_power[0], "fuel_l": res.diesel_fuel_consumed_l,
            "soc_pct": res.realized_soc_pct,
        })
        result.audit.append(audit_row(origin_index, step, bundle, plan, optimizer, state, res))
        state = res.next_state

    result.planned = harness.as_dicts()
    result.executed = exec_recorder.as_dicts()
    return result
