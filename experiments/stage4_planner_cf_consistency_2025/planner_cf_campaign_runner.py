"""
Planner-CF v1 campaign runner (EXP-PLANNER-CF-CONSISTENCY-2025, §4, §5, §7, §9).

Research-only. Runs the five preregistered closed-loop arms on the 2025 holdout population:

  PC-Control, PC-S, PC-SW, PC-S-L, PC-SW-L

Every arm uses the same Planner-CF v1 optimizer, the same Arm A realization executor, the same
causal NWP forecaster, router and mode propagation, and the same realized inputs as the corrected
reproduction. Only the EBR reserve equation differs by arm (frozen equations, §4 and §5 of the
corrected preregistration, via stage4_low_sun_adapter).

Campaign execution is gated: `run_campaign` refuses to run unless `authorized=True` is passed,
and verifies the §9 hash guards before any origin is run. This module is not run by this change.

Harness-only outputs: hourly telemetry (realized values), executed-hour planned records
(planned_execution_telemetry), and per-step solver status and EMERGENCY row counts for G4/G10.
"""

import importlib.util
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
for _p in (str(REPO), str(_HERE), str(REPO / "experiments" / "stage4_sw_low_sun_2025_holdout")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import stage4_low_sun_adapter as s4a  # noqa: E402
from system.research.research_critical_demand_adapter import (  # noqa: E402
    AdaptedClosedLoopRunner,
    adapt_critical_demand_vector,
)
from system.research.route_mode_propagation import propagate_route_mode  # noqa: E402
from research_numerical_extractor_planner_cf_v1 import PlannerCFV1Optimizer  # noqa: E402
from planned_execution_telemetry import ExecutedHourRecorder  # noqa: E402
from planner_cf_hash_guards import CORRECTED_RESULTS_PATH, verify_protected_hashes  # noqa: E402
import planner_cf_statistics as stat  # noqa: E402
import planner_cf_audit_gates as gates  # noqa: E402

WEATHER_2025_PATH = REPO / "data" / "POLARIS_v0_1_future_weather_forecasts_2025.csv"
DECOMPOSITION_2025_PATH = REPO / "data" / "POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv"
OUT_DIR = _HERE
CRITICAL_CEILING_W = 11600.0
TERMINAL_TARGET_WH = 100000.0
ARMS = ("PC-Control", "PC-S", "PC-SW", "PC-S-L", "PC-SW-L")

# Arm -> (renewable credit, low-sun protection)
ARM_SPEC = {
    "PC-Control": ("none", False),
    "PC-S": ("solar", False),
    "PC-SW": ("solar+wind", False),
    "PC-S-L": ("solar", True),
    "PC-SW-L": ("solar+wind", True),
}


def arm_ebr(arm: str, crit_w: List[float], solar_w: List[float], wind_w: List[float],
            elevations_deg: List[float]) -> List[float]:
    """EBR trajectory for an arm, using the frozen stage4 adapter equations."""
    if arm == "PC-Control":
        return s4a.compute_governed_ebr(crit_w)
    if arm == "PC-S":
        return s4a.compute_variant_s_ebr(crit_w, solar_w)
    if arm == "PC-SW":
        return s4a.compute_variant_sw_ebr(crit_w, solar_w, wind_w)
    if arm == "PC-S-L":
        return s4a.compute_variant_sl_ebr(crit_w, solar_w, elevations_deg, threshold_deg=15.0, protection_enabled=True)
    if arm == "PC-SW-L":
        return s4a.compute_variant_swl_ebr(crit_w, solar_w, wind_w, elevations_deg, threshold_deg=15.0,
                                           protection_enabled=True)
    raise ValueError(f"unknown arm {arm}")


def _load_canonical_configs():
    spec = importlib.util.spec_from_file_location("camp", REPO / "experiments" / "run_diesel_reduction_campaign.py")
    camp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(camp)
    return camp.load_canonical_configs(), camp.make_initial_state


class PlannerCFArmRunner(AdaptedClosedLoopRunner):
    """Closed-loop runner for one preregistered arm. Replaces the optimizer with Planner-CF v1."""

    def __init__(self, configs: Dict[str, Any], arm: str, solar_provider: Any):
        if arm not in ARMS:
            raise ValueError(f"unknown arm {arm}")
        super().__init__(configs)
        self.arm = arm
        self.solar_provider = solar_provider
        self.optimizer = PlannerCFV1Optimizer(reserve_enabled=True)
        self.bat = configs["battery"]
        self.e_min_wh = float(self.bat.get("capacity_wh", 200000.0)) * float(self.bat.get("min_soc_pct", 20.0)) / 100.0
        self.eta_dis = float(self.bat.get("discharge_efficiency", 0.92))

    def run_origin(self, origin_index: int, initial_state: Any, weather_df: pd.DataFrame,
                   realized_solar: List[float], realized_wind: List[float],
                   realized_demand: List[float], realized_timestamps: List[str]):
        if "dt" not in weather_df.columns:
            weather_df = weather_df.copy()
            weather_df["dt"] = pd.to_datetime(weather_df["timestamp"], utc=True)
        weather_lookup = weather_df.set_index("dt")["fc_cloud_cover"].to_dict()

        recorder = ExecutedHourRecorder()
        hourly: List[Dict[str, Any]] = []
        state = initial_state
        for step in range(24):
            origin_dt = self._parse_iso(state.timestamp)
            target_dts = [origin_dt + pd.Timedelta(hours=h) for h in range(1, 25)]
            cloud = [float(weather_lookup[d]) for d in target_dts]
            bundle = self.forecast_engine.predict(state, {"fc_cloud_cover": cloud})

            _, route = self.router.evaluate_and_route(state, bundle, self.configs)
            planning_state = propagate_route_mode(state, route)

            crit_w = adapt_critical_demand_vector(CRITICAL_CEILING_W, bundle.demand.point)
            sol_w = list(bundle.solar_generation.point)
            wnd_w = list(bundle.wind_generation.point)
            elev = self.solar_provider.get_elevation_vector(bundle.timestamps)
            ebr = arm_ebr(self.arm, crit_w, sol_w, wnd_w, elev)

            step_cfg = dict(self.configs)
            step_cfg["critical_demand_w"] = crit_w
            step_cfg["ebr_target_wh"] = ebr
            step_cfg["terminal_target_wh"] = TERMINAL_TARGET_WH

            e_start_wh = state.battery_energy_wh
            soc_before = state.battery_soc_pct
            plan = self.optimizer.optimize(bundle, planning_state, step_cfg)
            if plan.constraint_status not in ("OPTIMAL", "FEASIBLE"):
                raise RuntimeError(f"{self.arm} optimizer failed at step {step}: {plan.constraint_status}")
            diag0 = self.optimizer.last_diagnostics[0] if self.optimizer.last_diagnostics else {}

            realized_inputs = {
                "timestamp": realized_timestamps[step],
                "actual_SW_IN": float(realized_solar[step]),
                "actual_wind_generation": float(realized_wind[step]),
                "actual_demand": float(realized_demand[step]),
            }
            res = self.executor.execute_step(state, plan, realized_inputs, step_index=0)
            if res.busbar_energy_balance_error_w > 1e-3:
                raise RuntimeError(f"{self.arm} busbar error {res.busbar_energy_balance_error_w} W at step {step}")

            d_real = res.demand_realized_w
            d_crit = min(CRITICAL_CEILING_W, d_real)
            s_tot = res.served_load_w
            s_crit_first = min(d_crit, s_tot)
            s_crit_prop = s_tot * (d_crit / d_real) if d_real > 0 else 0.0

            recorder.record_resolve(
                origin_id=origin_index, arm=self.arm, step=step, planned_rows=self.optimizer.last_planned,
                e_start_wh=e_start_wh, pv_real_w=res.solar_realized_w, wind_real_w=res.wind_realized_w,
                d_c_real_w=d_crit, e_min_wh=self.e_min_wh, eta_dis=self.eta_dis,
            )
            hourly.append({
                "origin_id": origin_index, "hour": step, "timestamp": realized_timestamps[step],
                "arm": self.arm, "route": route, "optimizer_received_mode": planning_state.operating_mode,
                "solver_status": str(diag0.get("solver_status", plan.constraint_status)),
                "em_rows_built": int(self.optimizer.last_em_rows_built),
                "actual_solar": res.solar_realized_w, "actual_wind": res.wind_realized_w,
                "actual_demand": d_real, "critical_demand": d_crit,
                "served_load": s_tot, "unmet_load": res.unmet_load_w,
                "critical_served_first": s_crit_first, "critical_served_prop": s_crit_prop,
                "diesel_power": res.diesel_realized_w, "diesel_fuel": res.diesel_fuel_consumed_l,
                "battery_charge": res.battery_charge_realized_w,
                "battery_discharge": res.battery_discharge_realized_w,
                "soc_before": soc_before, "soc_after": res.realized_soc_pct,
                "curtailment": res.curtailment_w, "busbar_balance_error_w": res.busbar_energy_balance_error_w,
                "ebr_target_wh": ebr[0], "j2_shortfall_wh": diag0.get("j2_shortfall_wh", 0.0),
            })
            state = res.next_state
        return hourly, recorder.as_dicts()


def origin_population(weather_df: pd.DataFrame) -> List[str]:
    """123 forecast_start strings, 2025-05-01 00:00:00 .. 2025-08-31 00:00:00 inclusive (preregistered)."""
    starts = sorted(weather_df[
        (weather_df["forecast_start"] >= "2025-05-01 00:00:00")
        & (weather_df["forecast_start"] <= "2025-08-31 00:00:00")
    ]["forecast_start"].unique())
    if len(starts) != 123:
        raise RuntimeError(f"expected 123 origins, found {len(starts)}")
    return list(starts)


def realized_inputs_for(weather_df: pd.DataFrame, forecast_start: str) -> Tuple[List[float], List[float], List[float], List[str]]:
    """Realized solar (from the 2025 weather file), wind and demand (synthetic formulas, h = 1..24)."""
    sub = weather_df[weather_df["forecast_start"] == forecast_start]
    if len(sub) != 24:
        raise RuntimeError(f"origin {forecast_start} has {len(sub)} rows, expected 24")
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]
    return rs, rw, rd, rts


def run_campaign(*, authorized: bool = False, out_dir: Optional[Path] = None,
                 weather_path: Path = WEATHER_2025_PATH) -> Dict[str, Any]:
    """Runs all 123 origins x 5 arms (615 closed-loop runs). Requires explicit authorization."""
    if not authorized:
        raise PermissionError("campaign execution requires explicit authorization (preregistration §14)")
    mismatches = verify_protected_hashes(REPO)
    if mismatches:
        raise RuntimeError(f"hash guards failed before execution: {mismatches}")

    configs, make_initial_state = _load_canonical_configs()
    weather_df = pd.read_csv(weather_path)
    solar_provider = s4a.SolarElevationProvider(DECOMPOSITION_2025_PATH)
    origins = origin_population(weather_df)

    hourly_all: List[Dict[str, Any]] = []
    executed_all: List[Dict[str, Any]] = []
    for oi, fs in enumerate(origins, start=1):
        t0 = (pd.to_datetime(fs) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rs, rw, rd, rts = realized_inputs_for(weather_df, fs)
        for arm in ARMS:
            runner = PlannerCFArmRunner(configs, arm, solar_provider)
            hourly, executed = runner.run_origin(oi, make_initial_state(t0), weather_df, rs, rw, rd, rts)
            hourly_all.extend(hourly)
            executed_all.extend(executed)

    # G7 repeat: one repeated PC-Control run on origin index 1 (declared in preregistration §16.2).
    fs1 = origins[0]
    t0_1 = (pd.to_datetime(fs1) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rs1, rw1, rd1, rts1 = realized_inputs_for(weather_df, fs1)
    repeat_hourly, _ = PlannerCFArmRunner(configs, "PC-Control", solar_provider).run_origin(
        1, make_initial_state(t0_1), weather_df, rs1, rw1, rd1, rts1)

    hourly_df = pd.DataFrame(hourly_all)
    executed_df = pd.DataFrame(executed_all)
    target = Path(out_dir) if out_dir is not None else OUT_DIR
    target.mkdir(parents=True, exist_ok=True)
    hourly_df.to_csv(target / "PC_HOURLY_TELEMETRY.csv", index=False)
    executed_df.to_csv(target / "PC_EXECUTED_HOUR_TELEMETRY.csv", index=False)

    report = build_post_run_report(hourly_df, executed_df, pd.DataFrame(repeat_hourly),
                                   pd.read_csv(REPO / CORRECTED_RESULTS_PATH), REPO)
    import json
    with open(target / "PC_POST_RUN_REPORT.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    stat.write_summary_markdown(report["statistics"], target / "PC_RESULT_SUMMARY.md")
    return {"hourly_rows": len(hourly_df), "executed_rows": len(executed_df), "origins": len(origins),
            "winner": report["statistics"]["winner"], "gates_pass": report["all_gates_pass"]}


def build_post_run_report(hourly_df: pd.DataFrame, executed_df: pd.DataFrame, repeat_pc_control: pd.DataFrame,
                          corrected_results: pd.DataFrame, repo: Path) -> Dict[str, Any]:
    """Gates G2, G3, G4, G6, G7, G9, G10, G11 and the statistical decision, from campaign frames only."""
    g7_ref = hourly_df[(hourly_df["arm"] == "PC-Control") & (hourly_df["origin_id"] == 1)]
    gate_results = {
        "G2": gates.g2_priority_inversion(executed_df),
        "G3": gates.g3_critical_infeasibility(executed_df),
        "G4": gates.g4_optimizer_status(hourly_df),
        "G6": gates.g6_busbar_soc_fuel(hourly_df),
        "G7": gates.g7_determinism(g7_ref, repeat_pc_control),
        "G9": gates.g9_accounting(hourly_df, runner_arms()),
        "G10": gates.g10_route_propagation(hourly_df),
        "G11": gates.g11_old_telemetry_unmodified(repo),
    }
    stat_res = stat.evaluate(hourly_df)
    d_res = stat.d_comparisons(hourly_df, corrected_results)
    all_pass = all(v["PASS"] for v in gate_results.values())
    return {
        "gates": gate_results,
        "all_gates_pass": bool(all_pass),
        "statistics": stat_res,
        "d_comparisons": d_res,
        "note": "G1 and G12 are evaluated on oracle outputs by the oracle audit, not in the campaign.",
    }


def runner_arms() -> Tuple[str, ...]:
    return ARMS
