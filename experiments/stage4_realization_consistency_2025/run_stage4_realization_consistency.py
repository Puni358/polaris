"""
POLARIS Stage 4: Realization Consistency Experiment (2025 Holdout)
Module: experiments.stage4_realization_consistency_2025.run_stage4_realization_consistency

Governing Contract:
  experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md
  experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.json

Factorial Design:
  123 Origins x 5 Arms (Control_B, S, SW, S-L, SW-L) x 2 Realizations (A, B)
  = 1,230 Runs, 29,520 Arm-Hours.

Realization Semantics:
  A: Current realization semantics (ResearchRealizationExecutor, unmodified).
  B: Plan-consistent diagnostic realization semantics (PlanConsistentRealizationExecutor, §2.2).
"""

import copy
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
import scipy.stats as stats

REPO = Path("/home/punith-bs/01polaris (Copy)")
os.chdir(REPO)
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments/candidate_s_sw_campaign_2024"))
sys.path.insert(0, str(REPO / "experiments/stage4_sw_low_sun_2025_holdout"))
sys.path.insert(0, str(REPO / "experiments/stage4_realization_consistency_2025"))

import highspy
import stage4_low_sun_adapter as s4a
from research_numerical_extractor import ResearchNumericalGAP19Optimizer, TAU_RESIDUE_W
from system.research.research_critical_demand_adapter import (
    AdaptedClosedLoopRunner,
    adapt_critical_demand_vector
)
from system.research.route_mode_propagation import propagate_route_mode
from system.simulation.research_realization_executor import ResearchRealizationExecutor
from plan_consistent_realization import PlanConsistentRealizationExecutor

OUT_DIR = REPO / "experiments/stage4_realization_consistency_2025"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_PATH = OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_CHECKPOINT.jsonl"
FAILURES_PATH = OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_FAILURES.jsonl"

WEATHER_2025_PATH = REPO / "data/POLARIS_v0_1_future_weather_forecasts_2025.csv"
WEATHER_2025_DF = pd.read_csv(WEATHER_2025_PATH)

DECOMPOSITION_2025_PATH = REPO / "data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv"
SOLAR_PROVIDER = s4a.SolarElevationProvider(DECOMPOSITION_2025_PATH)

REPRO_TELEMETRY_PATH = REPO / "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv"
REPRO_TELEMETRY_DF = pd.read_csv(REPRO_TELEMETRY_PATH)

# Load canonical configs
spec_camp = importlib.util.spec_from_file_location("camp", REPO / "experiments/run_diesel_reduction_campaign.py")
camp = importlib.util.module_from_spec(spec_camp)
spec_camp.loader.exec_module(camp)
BASE_CONFIG = camp.load_canonical_configs()


class SpyHighs(highspy.Highs):
    """
    Subclass of highspy.Highs that observes every addRow call to count EMERGENCY rows.
    Verifies Gate G5 without changing any model formulation or solver options.
    """
    _active_instance = None

    def __init__(self):
        super().__init__()
        self.emergency_rows = 0
        SpyHighs._active_instance = self

    def addRow(self, lhs, rhs, n, idx, coef):
        # Emergency constraint form: p_dis(t) - p_served(t) <= 0 (lhs = -inf, rhs = 0.0, n = 2)
        if n == 2 and rhs == 0.0 and math.isinf(lhs) and lhs < 0:
            idx_list = list(idx)
            coef_list = list(coef)
            pairs = dict(zip(idx_list, coef_list))
            for t in range(24):
                base = t * 15
                if pairs.get(base + 5) == 1.0 and pairs.get(base + 8) == -1.0:
                    self.emergency_rows += 1
                    break
        return super().addRow(lhs, rhs, n, idx, coef)


# Install SpyHighs into highspy module namespace
highspy.Highs = SpyHighs


class StepExecutionError(Exception):
    def __init__(
        self,
        arm: str,
        realization: str,
        hour: int,
        error_type: str,
        error_message: str,
        raw_solver_diagnostics: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(f"[{arm}-{realization} h={hour}] {error_type}: {error_message}")
        self.arm = arm
        self.realization = realization
        self.hour = hour
        self.error_type = error_type
        self.error_message = error_message
        self.raw_solver_diagnostics = raw_solver_diagnostics or []


class RealizationConsistencyRunner(AdaptedClosedLoopRunner):
    """
    Research runner supporting both Arm A (current executor) and Arm B (plan-consistent executor),
    with full instrumentation for G1-G11 audit gates.
    """
    def __init__(self, configs: Dict[str, Any], variant: str, realization_mode: str):
        super().__init__(configs)
        self.variant = variant
        self.realization_mode = realization_mode  # 'A' or 'B'

        # Select appropriate realization executor
        if realization_mode == "A":
            self.executor = ResearchRealizationExecutor(configs)
        elif realization_mode == "B":
            self.executor = PlanConsistentRealizationExecutor(configs)
        else:
            raise ValueError(f"Unknown realization_mode '{realization_mode}'")

        self.optimizer = ResearchNumericalGAP19Optimizer(tau=TAU_RESIDUE_W)
        self.step_telemetry: List[Dict[str, Any]] = []

        inner_opt = self.optimizer
        runner_ref = self

        class InterceptingOptimizer:
            def optimize(self, bundle, station_state, config):
                crit_w = config.get("critical_demand_w")
                if crit_w is None:
                    crit_w = adapt_critical_demand_vector(runner_ref.critical_ceiling_w, bundle.demand.point)
                    config["critical_demand_w"] = crit_w

                sol_w = list(bundle.solar_generation.point)
                wnd_w = list(bundle.wind_generation.point)

                # Look up solar elevations for the 24 horizon timestamps
                elevations = SOLAR_PROVIDER.get_elevation_vector(bundle.timestamps)

                cfg_copy = dict(config)
                ebr_used = None
                if runner_ref.variant == "FROZEN_B":
                    ebr_used = s4a.compute_governed_ebr(crit_w)
                    cfg_copy.pop("ebr_target_wh", None)
                elif runner_ref.variant == "S":
                    ebr_used = s4a.compute_variant_s_ebr(crit_w, sol_w)
                    cfg_copy["ebr_target_wh"] = ebr_used
                elif runner_ref.variant == "SW":
                    ebr_used = s4a.compute_variant_sw_ebr(crit_w, sol_w, wnd_w)
                    cfg_copy["ebr_target_wh"] = ebr_used
                elif runner_ref.variant in ("SL", "S-L"):
                    ebr_used = s4a.compute_variant_sl_ebr(
                        crit_w, sol_w, elevations, threshold_deg=15.0, protection_enabled=True
                    )
                    cfg_copy["ebr_target_wh"] = ebr_used
                elif runner_ref.variant in ("SWL", "SW-L"):
                    ebr_used = s4a.compute_variant_swl_ebr(
                        crit_w, sol_w, wnd_w, elevations, threshold_deg=15.0, protection_enabled=True
                    )
                    cfg_copy["ebr_target_wh"] = ebr_used
                else:
                    raise ValueError(f"Unknown variant '{runner_ref.variant}'")

                stage2_vector = s4a.compute_stage2_target_vector(ebr_used, terminal_target_wh=100000.0)

                # Reset spy row counter before solve
                if SpyHighs._active_instance is not None:
                    SpyHighs._active_instance.emergency_rows = 0

                plan = inner_opt.optimize(bundle, station_state, cfg_copy)

                step0_diag = inner_opt.last_diagnostics[0] if inner_opt.last_diagnostics else {}
                low_sun_0 = int(elevations[0] < 15.0)

                # Emergency row count observed by SpyHighs
                em_rows_built = SpyHighs._active_instance.emergency_rows if SpyHighs._active_instance else 0

                runner_ref.current_snapshot = {
                    "forecast_solar_step0": sol_w[0],
                    "forecast_wind_step0": wnd_w[0],
                    "forecast_demand_step0": bundle.demand.point[0],
                    "critical_demand_step0": crit_w[0],
                    "solar_elevation_step0": elevations[0],
                    "low_sun_indicator_step0": low_sun_0,
                    "ebr_target_wh_step0": ebr_used[0],
                    "stage2_target_wh_step0": stage2_vector[0],
                    "j1_objective": plan.j1_objective if plan.j1_objective is not None else 0.0,
                    "j2_shortfall_wh": plan.j2_objective if plan.j2_objective is not None else 0.0,
                    "j3_objective": plan.objective_value if plan.objective_value is not None else 0.0,
                    "j4_objective": plan.j4_objective if plan.j4_objective is not None else 0.0,
                    "emergency_rows_built": em_rows_built,
                    "solver_status": step0_diag.get("solver_status", plan.constraint_status),
                    "raw_p_chg": step0_diag.get("raw_p_chg", 0.0),
                    "raw_p_dis": step0_diag.get("raw_p_dis", 0.0),
                    "corrected_p_chg": step0_diag.get("corrected_p_chg", 0.0),
                    "corrected_p_dis": step0_diag.get("corrected_p_dis", 0.0),
                    "u_chg": step0_diag.get("u_chg", 0.0),
                    "u_dis": step0_diag.get("u_dis", 0.0),
                    "p_diesel": step0_diag.get("p_diesel", 0.0),
                    "u_diesel": step0_diag.get("u_diesel", 0.0),
                    "v_start": step0_diag.get("v_start", 0.0),
                    "mip_gap": step0_diag.get("mip_gap", 0.0),
                    "residue_corrected": step0_diag.get("residue_corrected", False),
                    "zeroed_magnitude_w": step0_diag.get("zeroed_magnitude_w", 0.0),
                    "plan": plan,
                    "full_plan_diagnostics": inner_opt.last_diagnostics
                }
                return plan

            def __getattr__(self, name):
                return getattr(inner_opt, name)

        self.optimizer = InterceptingOptimizer()
        self.current_snapshot = {}

    def run_closed_loop_robust(
        self,
        origin_idx: int,
        initial_state: Any,
        weather_df: pd.DataFrame,
        realized_solar: List[float],
        realized_wind: List[float],
        realized_demand: List[float],
        realized_timestamps: List[str]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        if "dt" not in weather_df.columns:
            weather_df["dt"] = pd.to_datetime(weather_df["timestamp"], utc=True)
        weather_lookup = weather_df.set_index("dt")["fc_cloud_cover"].to_dict()

        current_state = initial_state
        hourly_rows = []

        cum_served = 0.0
        cum_unmet = 0.0
        cum_curtail = 0.0
        cum_fuel = 0.0
        cum_diesel_e = 0.0
        cum_solar = 0.0
        cum_wind = 0.0

        arm_name = f"Control_Frozen_B" if self.variant == "FROZEN_B" else f"Candidate_{self.variant}"
        real_mode = self.realization_mode

        for step in range(24):
            origin_dt = self._parse_iso(current_state.timestamp)
            target_ts_str = realized_timestamps[step]

            target_dts = [origin_dt + pd.Timedelta(hours=h) for h in range(1, 25)]
            cloud_trajectory = [float(weather_lookup[h_dt]) for h_dt in target_dts]

            forecast_context = {"fc_cloud_cover": cloud_trajectory}
            bundle = self.forecast_engine.predict(current_state, forecast_context)

            # 1. Router policy evaluation
            assessment, route_mode = self.router.evaluate_and_route(current_state, bundle, self.configs)

            # 2. PROVENANCE FIX: Propagate evaluated route_mode into planning state
            planning_state = propagate_route_mode(current_state, route_mode)

            step_configs = dict(self.configs)
            step_configs["critical_demand_w"] = adapt_critical_demand_vector(
                self.critical_ceiling_w, bundle.demand.point
            )

            soc_before = current_state.battery_soc_pct

            try:
                # 3. Optimize using planning_state (receives route_mode)
                plan = self.optimizer.optimize(bundle, planning_state, step_configs)
                if plan.constraint_status not in ("OPTIMAL", "FEASIBLE"):
                    raise RuntimeError(f"Optimizer failed at step {step}: status={plan.constraint_status}")

                # G5 Gate: EMERGENCY rows built assertion
                snap = self.current_snapshot
                em_rows = snap["emergency_rows_built"]
                if route_mode == "EMERGENCY" and em_rows != 24:
                    raise RuntimeError(f"G5 Violation: EMERGENCY mode expected 24 rows, got {em_rows}")
                if route_mode == "NORMAL" and em_rows != 0:
                    raise RuntimeError(f"G5 Violation: NORMAL mode expected 0 rows, got {em_rows}")

                realized_inputs = {
                    "timestamp": target_ts_str,
                    "actual_SW_IN": float(realized_solar[step]),
                    "actual_wind_generation": float(realized_wind[step]),
                    "actual_demand": float(realized_demand[step])
                }

                # 4. Executor receives current_state (unmutated execution state)
                realization_res = self.executor.execute_step(current_state, plan, realized_inputs, step_index=0)

                # G6 Gate: Busbar balance
                if realization_res.busbar_energy_balance_error_w > 1e-3:
                    raise RuntimeError(f"G6 Violation: Busbar error {realization_res.busbar_energy_balance_error_w} W at step {step}")

                # G7 Gate: SOC bounds
                if realization_res.realized_soc_pct < 19.999 or realization_res.realized_soc_pct > 95.001:
                    raise RuntimeError(f"G7 Violation: SOC {realization_res.realized_soc_pct}% out of bounds at step {step}")

            except Exception as e:
                diag = self.current_snapshot.get("full_plan_diagnostics") or getattr(self.optimizer, "last_diagnostics", [])
                raise StepExecutionError(
                    arm=arm_name,
                    realization=real_mode,
                    hour=step,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    raw_solver_diagnostics=diag
                ) from e

            d_real = realization_res.demand_realized_w
            d_crit = min(11600.0, d_real)
            s_tot = realization_res.served_load_w
            u_tot = realization_res.unmet_load_w

            # Critical-first
            s_crit_first = min(d_crit, s_tot)
            u_crit_first = d_crit - s_crit_first

            # Proportional
            s_crit_prop = s_tot * (d_crit / d_real)
            u_crit_prop = d_crit - s_crit_prop

            step_fuel = realization_res.diesel_fuel_consumed_l
            soc_after = realization_res.realized_soc_pct

            p_chg_plan = float(plan.battery_charge[0])
            p_dis_plan = float(plan.battery_discharge[0])
            p_flx_plan = float(plan.flexible_load_schedule[0]) if plan.flexible_load_schedule else 0.0
            p_served_plan = float(plan.load_served[0])
            p_unmet_plan = float(plan.unmet_load[0])

            c_realized = float(realization_res.battery_charge_realized_w)
            delta_c = p_chg_plan - c_realized
            f_realized = float(realization_res.accounting.get("flexible_load_out_w", 0.0))

            row = {
                "origin_id": origin_idx,
                "hour": step,
                "timestamp": target_ts_str,
                "arm": arm_name,
                "realization": real_mode,
                "route": route_mode,
                "optimizer_received_mode": planning_state.operating_mode,
                "emergency_constraint_active": bool(route_mode == "EMERGENCY"),
                "emergency_rows_built": snap["emergency_rows_built"],
                "solver_status": snap["solver_status"],
                "solar_elevation_deg": snap["solar_elevation_step0"],
                "low_sun_indicator_L": snap["low_sun_indicator_step0"],
                "forecast_solar": snap["forecast_solar_step0"],
                "actual_solar": realization_res.solar_realized_w,
                "forecast_wind": snap["forecast_wind_step0"],
                "actual_wind": realization_res.wind_realized_w,
                "forecast_demand": snap["forecast_demand_step0"],
                "actual_demand": d_real,
                "critical_demand": d_crit,
                "served_load": s_tot,
                "unmet_load": u_tot,
                "critical_served_first": s_crit_first,
                "critical_unmet_first": u_crit_first,
                "critical_served_prop": s_crit_prop,
                "critical_unmet_prop": u_crit_prop,
                "diesel_power": realization_res.diesel_realized_w,
                "diesel_fuel": step_fuel,
                "battery_charge": c_realized,
                "battery_discharge": realization_res.battery_discharge_realized_w,
                "soc_before": soc_before,
                "soc_after": soc_after,
                "curtailment": realization_res.curtailment_w,
                "ebr_target_wh": snap["ebr_target_wh_step0"],
                "stage2_target_wh": snap["stage2_target_wh_step0"],
                "j1_objective": snap["j1_objective"],
                "j2_shortfall_wh": snap["j2_shortfall_wh"],
                "j3_objective": snap["j3_objective"],
                "j4_objective": snap["j4_objective"],
                "busbar_balance_error_w": realization_res.busbar_energy_balance_error_w,
                "p_chg_plan": p_chg_plan,
                "battery_charge_realized": c_realized,
                "delta_c_w": delta_c,
                "p_flx_plan": p_flx_plan,
                "flexible_load_realized": f_realized,
                "p_served_plan": p_served_plan,
                "realized_served": s_tot,
                "p_unmet_plan": p_unmet_plan,
                "realized_unmet": u_tot,
                "raw_p_chg": snap["raw_p_chg"],
                "raw_p_dis": snap["raw_p_dis"],
                "corrected_p_chg": snap["corrected_p_chg"],
                "corrected_p_dis": snap["corrected_p_dis"],
                "u_chg": snap["u_chg"],
                "u_dis": snap["u_dis"],
                "p_diesel": snap["p_diesel"],
                "u_diesel": snap["u_diesel"],
                "v_start": snap["v_start"],
                "mip_gap": snap["mip_gap"],
                "residue_corrected": snap["residue_corrected"],
                "zeroed_magnitude_w": snap["zeroed_magnitude_w"]
            }
            hourly_rows.append(row)

            cum_served += s_tot
            cum_unmet += u_tot
            cum_curtail += realization_res.curtailment_w
            cum_fuel += step_fuel
            cum_diesel_e += realization_res.diesel_realized_w
            cum_solar += realization_res.solar_realized_w
            cum_wind += realization_res.wind_realized_w

            current_state = realization_res.next_state

        arm_summary = {
            "origin_id": origin_idx,
            "arm": arm_name,
            "realization": real_mode,
            "diesel_fuel_liters": cum_fuel,
            "served_load_wh": cum_served,
            "unmet_load_wh": cum_unmet,
            "curtailment_wh": cum_curtail,
            "diesel_energy_wh": cum_diesel_e,
            "min_soc_pct": min(r["soc_after"] for r in hourly_rows),
            "max_soc_pct": max(r["soc_after"] for r in hourly_rows),
            "soc_violations_below_20": sum(1 for r in hourly_rows if r["soc_after"] < 19.999),
            "served_crit_first_wh": sum(r["critical_served_first"] for r in hourly_rows),
            "unmet_crit_first_wh": sum(r["critical_unmet_first"] for r in hourly_rows),
            "served_crit_prop_wh": sum(r["critical_served_prop"] for r in hourly_rows),
            "unmet_crit_prop_wh": sum(r["critical_unmet_prop"] for r in hourly_rows),
            "diesel_on_hours": sum(1 for r in hourly_rows if r["diesel_power"] > 1e-3),
            "diesel_startups": sum(
                1 for step_i in range(24)
                if hourly_rows[step_i]["diesel_power"] > 1e-3 and (step_i == 0 or hourly_rows[step_i - 1]["diesel_power"] <= 1e-3)
            ),
            "battery_throughput_wh": sum(r["battery_charge"] + r["battery_discharge"] for r in hourly_rows),
            "efc": sum(r["battery_charge"] + r["battery_discharge"] for r in hourly_rows) / (2.0 * 200000.0),
            "total_delta_c_wh": sum(r["delta_c_w"] for r in hourly_rows),
            "mean_delta_c_w": sum(r["delta_c_w"] for r in hourly_rows) / 24.0,
            "residue_corrections_count": sum(1 for r in hourly_rows if r["residue_corrected"]),
            "max_residue_zeroed_w": max((r["zeroed_magnitude_w"] for r in hourly_rows), default=0.0)
        }

        return arm_summary, hourly_rows


def run_single_origin_decuple(origin_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes all 5 arms under Realization A and all 5 arms under Realization B
    for a single origin (10 runs, 240 arm-hours).
    Performs real-time verification of G1 (determinism) and G11 (hour-0 identity).
    """
    oi = origin_info["origin_index"]
    fs = origin_info["forecast_start"]
    t0 = origin_info["t0_timestamp"]

    sub = WEATHER_2025_DF[WEATHER_2025_DF["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]

    variants = [
        ("FROZEN_B", "Control_Frozen_B"),
        ("S", "Candidate_S"),
        ("SW", "Candidate_SW"),
        ("SL", "Candidate_SL"),
        ("SWL", "Candidate_SWL")
    ]

    arm_summaries = {}
    hourly_rows_all = {}
    hour0_plans = {}

    current_arm = ""
    current_real = ""
    current_runner = None

    try:
        # Run pairs of (A, B) for each variant
        for var_code, arm_name in variants:
            # 1. Realization A
            current_arm = arm_name
            current_real = "A"
            runner_a = RealizationConsistencyRunner(BASE_CONFIG, variant=var_code, realization_mode="A")
            current_runner = runner_a
            init_a = camp.make_initial_state(t0)
            sum_a, rows_a = runner_a.run_closed_loop_robust(oi, init_a, WEATHER_2025_DF, rs, rw, rd, rts)

            arm_summaries[(arm_name, "A")] = sum_a
            hourly_rows_all[(arm_name, "A")] = rows_a
            hour0_plans[(arm_name, "A")] = rows_a[0]

            # G1 Gate Check: Compare Arm A rows against reference corrected reproduction telemetry
            ref_sub = REPRO_TELEMETRY_DF[
                (REPRO_TELEMETRY_DF["origin_id"] == oi) &
                (REPRO_TELEMETRY_DF["arm"] == arm_name)
            ].sort_values("hour").to_dict("records")

            assert len(ref_sub) == 24, f"Reference telemetry missing rows for origin {oi}, arm {arm_name}"
            for step_h in range(24):
                calc_r = rows_a[step_h]
                ref_r = ref_sub[step_h]

                err_diesel = abs(calc_r["diesel_power"] - ref_r["diesel_power"])
                err_chg = abs(calc_r["battery_charge"] - ref_r["battery_charge"])
                err_dis = abs(calc_r["battery_discharge"] - ref_r["battery_discharge"])
                err_soc = abs(calc_r["soc_after"] - ref_r["soc_after"])
                err_unmet = abs(calc_r["unmet_load"] - ref_r["unmet_load"])

                if err_diesel > 1e-5:
                    raise RuntimeError(f"G1 Determinism Mismatch [Origin {oi}, {arm_name}, h={step_h}]: diesel diff = {err_diesel:.6f} W")
                if err_chg > 1e-5:
                    raise RuntimeError(f"G1 Determinism Mismatch [Origin {oi}, {arm_name}, h={step_h}]: chg diff = {err_chg:.6f} W")
                if err_dis > 1e-5:
                    raise RuntimeError(f"G1 Determinism Mismatch [Origin {oi}, {arm_name}, h={step_h}]: dis diff = {err_dis:.6f} W")
                if err_soc > 1e-4:
                    raise RuntimeError(f"G1 Determinism Mismatch [Origin {oi}, {arm_name}, h={step_h}]: soc diff = {err_soc:.6f} %")
                if err_unmet > 1e-5:
                    raise RuntimeError(f"G1 Determinism Mismatch [Origin {oi}, {arm_name}, h={step_h}]: unmet diff = {err_unmet:.6f} W")

            # 2. Realization B
            current_arm = arm_name
            current_real = "B"
            runner_b = RealizationConsistencyRunner(BASE_CONFIG, variant=var_code, realization_mode="B")
            current_runner = runner_b
            init_b = camp.make_initial_state(t0)
            sum_b, rows_b = runner_b.run_closed_loop_robust(oi, init_b, WEATHER_2025_DF, rs, rw, rd, rts)

            arm_summaries[(arm_name, "B")] = sum_b
            hourly_rows_all[(arm_name, "B")] = rows_b
            hour0_plans[(arm_name, "B")] = rows_b[0]

            # G11 Gate Check: Hour 0 optimizer inputs and outputs MUST be identical between A and B
            h0_a = rows_a[0]
            h0_b = rows_b[0]

            diff_p_diesel = abs(h0_a["p_diesel"] - h0_b["p_diesel"])
            diff_p_chg = abs(h0_a["p_chg_plan"] - h0_b["p_chg_plan"])
            diff_p_dis = abs(h0_a["raw_p_dis"] - h0_b["raw_p_dis"])
            diff_p_serv = abs(h0_a["p_served_plan"] - h0_b["p_served_plan"])
            diff_p_unm = abs(h0_a["p_unmet_plan"] - h0_b["p_unmet_plan"])
            diff_p_flx = abs(h0_a["p_flx_plan"] - h0_b["p_flx_plan"])
            diff_v_start = abs(h0_a["v_start"] - h0_b["v_start"])
            diff_j1 = abs(h0_a["j1_objective"] - h0_b["j1_objective"])
            diff_j2 = abs(h0_a["j2_shortfall_wh"] - h0_b["j2_shortfall_wh"])
            diff_j3 = abs(h0_a["j3_objective"] - h0_b["j3_objective"])
            diff_j4 = abs(h0_a["j4_objective"] - h0_b["j4_objective"])

            if max(diff_p_diesel, diff_p_chg, diff_p_dis, diff_p_serv, diff_p_unm, diff_p_flx) > 1e-4:
                raise RuntimeError(
                    f"G11 Violation [Origin {oi}, {arm_name}, h=0]: optimizer dispatch mismatch between A and B: "
                    f"diesel={diff_p_diesel:.4f}, chg={diff_p_chg:.4f}, dis={diff_p_dis:.4f}, "
                    f"serv={diff_p_serv:.4f}, unm={diff_p_unm:.4f}, flx={diff_p_flx:.4f}"
                )
            if max(diff_v_start, diff_j1, diff_j2, diff_j3, diff_j4) > 1e-4:
                raise RuntimeError(
                    f"G11 Violation [Origin {oi}, {arm_name}, h=0]: optimizer objectives mismatch between A and B: "
                    f"v_start={diff_v_start:.4f}, J1={diff_j1:.4f}, J2={diff_j2:.4f}, J3={diff_j3:.4f}, J4={diff_j4:.4f}"
                )

        return {
            "success": True,
            "origin_id": oi,
            "forecast_start": fs,
            "t0_timestamp": t0,
            "summaries": {f"{a}_{r}": arm_summaries[(a, r)] for a, r in arm_summaries},
            "hourly_rows": [r for pair in hourly_rows_all.values() for r in pair]
        }

    except StepExecutionError as see:
        return {
            "success": False,
            "origin_id": oi,
            "forecast_start": fs,
            "t0_timestamp": t0,
            "arm": see.arm,
            "realization": see.realization,
            "hour": see.hour,
            "error_type": see.error_type,
            "error_message": see.error_message,
            "raw_solver_diagnostics": see.raw_solver_diagnostics
        }
    except Exception as e:
        diag = getattr(current_runner.optimizer, "last_diagnostics", []) if current_runner else []
        return {
            "success": False,
            "origin_id": oi,
            "forecast_start": fs,
            "t0_timestamp": t0,
            "arm": current_arm,
            "realization": current_real,
            "hour": -1,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "raw_solver_diagnostics": diag
        }


def compute_guard_hashes() -> Dict[str, str]:
    expected = {
        "system/simulation/research_realization_executor.py": "c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b",
        "system/optimization/implementations/gap19_highs_native.py": "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737",
        "system/schemas/dispatch_plan.py": "21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b",
        "system/forecasting/implementations/causal_nwp_physics.py": "14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710",
        "system/control/router.py": "041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f",
        "system/schemas/station_state.py": "e763439a6ddecbbadb9287f99258e595ab7f23f0eb9a7377f5a54beb7661df88",
        "system/research/route_mode_propagation.py": "80456f8776925860ad20c407ec92f3ac78dbd387f4863ea48dc1917490e89376",
        "experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py": "95b2f3b53609a6e420a18692b4b0e3927cb47841d9e1200cce04677094a5950e",
        "experiments/stage4_corrected_reproduction_2025/run_stage4_corrected_reproduction.py": "770cb61b0a73f3f8c66fd3918419ef31768dd88b47306a47bd60d1e3b06d3ecc",
        "experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md": "4f438f466a285d2d230edda168075f883919317922de3a5866dbb7ca5cdac14b",
        "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv": "6b3636d7ae4d596016f4e7b3b5fc63e9a26e374041b586b619b49afc2eec7d2e",
        "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_RESULTS.csv": "8c13b904e286e25167a8eca5144e545627b6c598f36716e93fcf9ee95a2ab57e",
        "experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md": "e73558cfd03acd35fc55d24a055f7ccc6a31d0d973a3cc2e4443a8665ac21cd7",
        "experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.json": "6b0bb6f7af44ef06731180d50239de222f301fa571c5862d115f7644d3be7b87",
        "experiments/stage4_sw_low_sun_2025_holdout/STAGE4_123_ORIGIN_RESULTS.csv": "18d13dec71eab82919c900da52b5248699e4b5b8fa4c4ed8499aff494f4fa62b",
        "experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md": "1e9077d4bb3f3828f7040a9fbd39a31e46308c547ce648a80c7579099124cf0b",
        "experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.json": "076279c227be7c8f866e90226adc719042c3ad7f9977161e5dad4b006a14bb8b",
        "experiments/stage4_realization_consistency_2025/plan_consistent_realization.py": "dea4b46b623e83fd7bc5428ef013a3b57b58af756f3397099a5863f6d59cbadd"
    }
    actual = {}
    for rel_path, exp_hash in expected.items():
        h = hashlib.sha256((REPO / rel_path).read_bytes()).hexdigest()
        if h != exp_hash:
            raise ValueError(f"GUARD_HASH_MISMATCH for {rel_path}: expected {exp_hash}, got {h}")
        actual[rel_path] = h
    return actual


def read_existing_checkpoints() -> Dict[int, Dict[str, Any]]:
    completed = {}
    if not CHECKPOINT_PATH.exists():
        return completed

    with open(CHECKPOINT_PATH, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            origin_id = rec["origin_id"]
            completed[origin_id] = rec
    return completed


def append_checkpoint(result_dict: Dict[str, Any]):
    with open(CHECKPOINT_PATH, "a") as f:
        f.write(json.dumps(result_dict) + "\n")


def compute_bca_confidence_interval(
    data: np.ndarray,
    confidence_level: float = 0.95,
    n_resamples: int = 10000,
    seed: int = 42
) -> Tuple[float, float]:
    """Computes BCa 95% bootstrap confidence interval with seed 42."""
    rng = np.random.default_rng(seed)
    try:
        res = stats.bootstrap(
            (data,),
            np.mean,
            method="BCa",
            confidence_level=confidence_level,
            n_resamples=n_resamples,
            random_state=rng
        )
        return float(res.confidence_interval.low), float(res.confidence_interval.high)
    except Exception:
        res = stats.bootstrap(
            (data,),
            np.mean,
            method="percentile",
            confidence_level=confidence_level,
            n_resamples=n_resamples,
            random_state=rng
        )
        return float(res.confidence_interval.low), float(res.confidence_interval.high)


def holm_adjust_pvalues(pvalues: List[float]) -> List[float]:
    """Applies standard Holm-Bonferroni step-down correction to a list of p-values."""
    m = len(pvalues)
    indexed_p = sorted(enumerate(pvalues), key=lambda x: x[1])
    adjusted = [0.0] * m
    running_max = 0.0
    for rank, (orig_idx, p_val) in enumerate(indexed_p):
        k = rank + 1
        adj_p = min(1.0, (m - k + 1) * p_val)
        running_max = max(running_max, adj_p)
        adjusted[orig_idx] = min(1.0, running_max)
    return adjusted


def main():
    print("=" * 80)
    print("POLARIS STAGE 4: REALIZATION CONSISTENCY EXPERIMENT (2025 HOLDOUT)")
    print("Governing Contract: EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md")
    print("=" * 80)
    t0_start = time.time()

    startup_guards = compute_guard_hashes()
    print(f"Startup Cryptographic Guards Verified. All {len(startup_guards)} reference hashes intact.")

    # 1. Build Population (strictly calendar rule: 2025-05-01 through 2025-08-31)
    summer_starts = sorted(
        WEATHER_2025_DF[
            (WEATHER_2025_DF["forecast_start"] >= "2025-05-01 00:00:00") &
            (WEATHER_2025_DF["forecast_start"] <= "2025-08-31 00:00:00")
        ]["forecast_start"].unique()
    )
    assert len(summer_starts) == 123, f"Expected 123 origins, got {len(summer_starts)}"

    origins_list = []
    for idx, fs in enumerate(summer_starts, 1):
        dt_start = pd.to_datetime(fs)
        t0_dt = dt_start - pd.Timedelta(hours=1)
        t0_str = t0_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        origins_list.append({
            "origin_index": idx,
            "forecast_start": fs,
            "t0_timestamp": t0_str
        })

    print(f"Total Confirmatory Origins to Execute: {len(origins_list)} (2,952 origin-hours per arm-realization, 29,520 total arm-hours).")

    completed_checkpoints = read_existing_checkpoints()
    print(f"Read {len(completed_checkpoints)} completed origin decuples from checkpoint.")

    remaining_origins = [o for o in origins_list if o["origin_index"] not in completed_checkpoints]
    print(f"Remaining origins to execute: {len(remaining_origins)} of {len(origins_list)}.")

    all_decuple_results = list(completed_checkpoints.values())
    failures = []

    if remaining_origins:
        print("Launching parallel evaluation across 4 worker processes...")
        with Pool(processes=4) as pool:
            for i, res in enumerate(pool.imap_unordered(run_single_origin_decuple, remaining_origins, chunksize=1), 1):
                if res["success"]:
                    append_checkpoint(res)
                    all_decuple_results.append(res)
                    elapsed = time.time() - t0_start
                    pct = (len(all_decuple_results) / 123.0) * 100.0
                    rate = len(all_decuple_results) / (elapsed + 1e-6)
                    eta_sec = (123 - len(all_decuple_results)) / (rate + 1e-6)
                    print(
                        f"[{len(all_decuple_results)}/123] ({pct:.1f}%) Completed origin {res['origin_id']} | "
                        f"Elapsed: {elapsed/60.0:.1f}m | ETA: {eta_sec/60.0:.1f}m"
                    )
                else:
                    failures.append(res)
                    print(f"FAILED Origin {res['origin_id']} [{res.get('arm')}-{res.get('realization')}]: {res['error_type']} - {res['error_message']}")
                    with open(FAILURES_PATH, "a") as f:
                        f.write(json.dumps(res) + "\n")
                    raise RuntimeError(f"Campaign execution aborted due to origin failure: {res}")

    print("All 123 origin decuples completed successfully.")
    all_decuple_results.sort(key=lambda r: r["origin_id"])

    # Flatten hourly rows & per-origin rows
    all_hourly_rows = []
    per_origin_records = []

    for r in all_decuple_results:
        oi = r["origin_id"]
        fs = r["forecast_start"]
        t0 = r["t0_timestamp"]
        sums = r["summaries"]
        rows = r["hourly_rows"]
        all_hourly_rows.extend(rows)

        rec = {
            "origin_id": oi,
            "forecast_start": fs,
            "t0_timestamp": t0,
        }
        for arm_key, s_data in sums.items():
            for metric, val in s_data.items():
                if metric not in ("origin_id", "arm", "realization"):
                    rec[f"{arm_key}_{metric}"] = val
        per_origin_records.append(rec)

    total_expected_hourly = 123 * 24 * 5 * 2
    assert len(all_hourly_rows) == total_expected_hourly, f"Expected {total_expected_hourly} rows, got {len(all_hourly_rows)}"

    print("Saving telemetry and per-origin CSV and JSON...")
    hourly_df = pd.DataFrame(all_hourly_rows)
    hourly_csv_path = OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_TELEMETRY.csv"
    hourly_df.to_csv(hourly_csv_path, index=False)

    hourly_json_path = OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_TELEMETRY.json"
    with open(hourly_json_path, "w") as f:
        json.dump(all_hourly_rows, f, indent=2)

    per_origin_df = pd.DataFrame(per_origin_records)
    per_origin_csv_path = OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_RESULTS.csv"
    per_origin_df.to_csv(per_origin_csv_path, index=False)

    per_origin_json_path = OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_RESULTS.json"
    with open(per_origin_json_path, "w") as f:
        json.dump(per_origin_records, f, indent=2)

    # ==============================================================================
    # 10-POINT AUDIT GATES (G1 - G11)
    # ==============================================================================
    print("Running 10-Point Pre-Outcome Audit (G1 - G11)...")
    audit_results = {}

    # G1 Determinism: Arm A vs corrected reproduction telemetry
    max_diff_diesel = 0.0
    max_diff_chg = 0.0
    max_diff_dis = 0.0
    max_diff_soc = 0.0
    max_diff_unmet = 0.0

    arm_a_rows = hourly_df[hourly_df["realization"] == "A"].sort_values(["origin_id", "arm", "hour"])
    ref_rows = REPRO_TELEMETRY_DF.sort_values(["origin_id", "arm", "hour"])

    assert len(arm_a_rows) == len(ref_rows) == 14760, f"Row count mismatch for G1: {len(arm_a_rows)} vs {len(ref_rows)}"

    diff_diesel_series = np.abs(arm_a_rows["diesel_power"].values - ref_rows["diesel_power"].values)
    diff_chg_series = np.abs(arm_a_rows["battery_charge"].values - ref_rows["battery_charge"].values)
    diff_dis_series = np.abs(arm_a_rows["battery_discharge"].values - ref_rows["battery_discharge"].values)
    diff_soc_series = np.abs(arm_a_rows["soc_after"].values - ref_rows["soc_after"].values)
    diff_unmet_series = np.abs(arm_a_rows["unmet_load"].values - ref_rows["unmet_load"].values)

    max_diff_diesel = float(np.max(diff_diesel_series))
    max_diff_chg = float(np.max(diff_chg_series))
    max_diff_dis = float(np.max(diff_dis_series))
    max_diff_soc = float(np.max(diff_soc_series))
    max_diff_unmet = float(np.max(diff_unmet_series))

    g1_pass = (
        max_diff_diesel <= 1e-5 and
        max_diff_chg <= 1e-5 and
        max_diff_dis <= 1e-5 and
        max_diff_soc <= 1e-4 and
        max_diff_unmet <= 1e-5
    )
    audit_results["G1_Determinism"] = {
        "pass": g1_pass,
        "max_diff_diesel_w": max_diff_diesel,
        "max_diff_battery_charge_w": max_diff_chg,
        "max_diff_battery_discharge_w": max_diff_dis,
        "max_diff_soc_after_pct": max_diff_soc,
        "max_diff_unmet_load_w": max_diff_unmet
    }

    # G2 Accounting
    unique_origins_a = hourly_df[hourly_df["realization"] == "A"]["origin_id"].nunique()
    unique_origins_b = hourly_df[hourly_df["realization"] == "B"]["origin_id"].nunique()
    hours_per_arm_a = [len(hourly_df[(hourly_df["realization"] == "A") & (hourly_df["arm"] == arm)]) for arm in hourly_df["arm"].unique()]
    hours_per_arm_b = [len(hourly_df[(hourly_df["realization"] == "B") & (hourly_df["arm"] == arm)]) for arm in hourly_df["arm"].unique()]
    g2_pass = (
        unique_origins_a == 123 and
        unique_origins_b == 123 and
        all(h == 2952 for h in hours_per_arm_a) and
        all(h == 2952 for h in hours_per_arm_b) and
        len(hourly_df) == 29520
    )
    audit_results["G2_Accounting"] = {
        "pass": g2_pass,
        "unique_origins_a": unique_origins_a,
        "unique_origins_b": unique_origins_b,
        "total_rows": len(hourly_df),
        "expected_rows": 29520
    }

    # G3 Optimizer Status (preregistration §9: every step HighsModelStatus.kOptimal)
    non_optimal = hourly_df[~hourly_df["solver_status"].isin(["OPTIMAL", "kOptimal", "HighsModelStatus.kOptimal"])]
    g3_pass = len(non_optimal) == 0
    audit_results["G3_Optimizer_Status"] = {
        "pass": g3_pass,
        "non_optimal_count": len(non_optimal)
    }

    # G4 Route Propagation
    route_mismatch = hourly_df[hourly_df["optimizer_received_mode"] != hourly_df["route"]]
    g4_pass = len(route_mismatch) == 0
    audit_results["G4_Route_Propagation"] = {
        "pass": g4_pass,
        "mismatches_count": len(route_mismatch)
    }

    # G5 EMERGENCY Rows Built
    g5_violations = hourly_df[
        ((hourly_df["route"] == "EMERGENCY") & (hourly_df["emergency_rows_built"] != 24)) |
        ((hourly_df["route"] == "NORMAL") & (hourly_df["emergency_rows_built"] != 0))
    ]
    g5_pass = len(g5_violations) == 0
    audit_results["G5_EMERGENCY_Rows"] = {
        "pass": g5_pass,
        "violations_count": len(g5_violations)
    }

    # G6 Busbar Balance
    max_busbar_err = float(hourly_df["busbar_balance_error_w"].max())
    g6_pass = max_busbar_err <= 1e-3
    audit_results["G6_Busbar_Balance"] = {
        "pass": g6_pass,
        "max_busbar_balance_error_w": max_busbar_err
    }

    # G7 SOC Accounting & Bounds
    min_soc_overall = float(hourly_df["soc_after"].min())
    max_soc_overall = float(hourly_df["soc_after"].max())
    soc_floor_violations = int((hourly_df["soc_after"] < 19.999).sum())
    g7_pass = (min_soc_overall >= 19.999) and (max_soc_overall <= 95.001) and (soc_floor_violations == 0)
    audit_results["G7_SOC_Accounting"] = {
        "pass": g7_pass,
        "min_soc_pct": min_soc_overall,
        "max_soc_pct": max_soc_overall,
        "soc_floor_violations_count": soc_floor_violations
    }

    # G8 Fuel Accounting (preregistration §9: accounted fuel equals 5*on + 0.25*kWh on every row except recorded starvation rows, which are listed and counted)
    on_mask = hourly_df["diesel_power"] > 1e-3
    expected_fuel = 5.0 * on_mask.astype(float) + 0.00025 * hourly_df["diesel_power"]
    fuel_err = np.abs(hourly_df["diesel_fuel"].values - expected_fuel.values)
    starvation_mask = (hourly_df["diesel_fuel"] > 0) & (~on_mask) & (hourly_df["diesel_fuel"] < 5.0)
    non_starvation_fuel_err = fuel_err[~starvation_mask]
    max_fuel_err = float(np.max(non_starvation_fuel_err)) if len(non_starvation_fuel_err) > 0 else 0.0
    starvation_rows = hourly_df[starvation_mask][["origin_id", "arm", "realization", "hour", "diesel_power", "diesel_fuel"]].to_dict("records")
    g8_pass = max_fuel_err <= 1e-4
    audit_results["G8_Fuel_Accounting"] = {
        "pass": g8_pass,
        "max_fuel_accounting_error_l": max_fuel_err,
        "starvation_rows_count": len(starvation_rows),
        "starvation_rows": starvation_rows
    }

    # G9 Planned/Realized Reconciliation
    g9_fields = ["p_chg_plan", "battery_charge_realized", "delta_c_w", "p_served_plan", "realized_served", "p_unmet_plan", "realized_unmet"]
    missing_g9 = [col for col in g9_fields if col not in hourly_df.columns or hourly_df[col].isna().any()]
    g9_pass = len(missing_g9) == 0
    audit_results["G9_Reconciliation"] = {
        "pass": g9_pass,
        "missing_or_nan_fields": missing_g9
    }

    # G11 Hour-0 Optimizer Identity
    h0_a = hourly_df[(hourly_df["realization"] == "A") & (hourly_df["hour"] == 0)].sort_values(["origin_id", "arm"])
    h0_b = hourly_df[(hourly_df["realization"] == "B") & (hourly_df["hour"] == 0)].sort_values(["origin_id", "arm"])
    assert len(h0_a) == len(h0_b) == 123 * 5, f"Hour 0 row count mismatch: {len(h0_a)} vs {len(h0_b)}"

    h0_diff_diesel = np.max(np.abs(h0_a["p_diesel"].values - h0_b["p_diesel"].values))
    h0_diff_chg = np.max(np.abs(h0_a["p_chg_plan"].values - h0_b["p_chg_plan"].values))
    h0_diff_dis = np.max(np.abs(h0_a["raw_p_dis"].values - h0_b["raw_p_dis"].values))
    h0_diff_serv = np.max(np.abs(h0_a["p_served_plan"].values - h0_b["p_served_plan"].values))
    h0_diff_unm = np.max(np.abs(h0_a["p_unmet_plan"].values - h0_b["p_unmet_plan"].values))
    h0_diff_flx = np.max(np.abs(h0_a["p_flx_plan"].values - h0_b["p_flx_plan"].values))
    h0_diff_vstart = np.max(np.abs(h0_a["v_start"].values - h0_b["v_start"].values))
    h0_diff_j1 = np.max(np.abs(h0_a["j1_objective"].values - h0_b["j1_objective"].values))
    h0_diff_j2 = np.max(np.abs(h0_a["j2_shortfall_wh"].values - h0_b["j2_shortfall_wh"].values))
    h0_diff_j3 = np.max(np.abs(h0_a["j3_objective"].values - h0_b["j3_objective"].values))
    h0_diff_j4 = np.max(np.abs(h0_a["j4_objective"].values - h0_b["j4_objective"].values))

    g11_pass = max(
        h0_diff_diesel, h0_diff_chg, h0_diff_dis, h0_diff_serv, h0_diff_unm,
        h0_diff_flx, h0_diff_vstart, h0_diff_j1, h0_diff_j2, h0_diff_j3, h0_diff_j4
    ) <= 1e-4

    audit_results["G11_Hour0_Identity"] = {
        "pass": bool(g11_pass),
        "max_h0_diff_diesel_w": float(h0_diff_diesel),
        "max_h0_diff_charge_plan_w": float(h0_diff_chg),
        "max_h0_diff_discharge_plan_w": float(h0_diff_dis),
        "max_h0_diff_served_plan_w": float(h0_diff_serv),
        "max_h0_diff_unmet_plan_w": float(h0_diff_unm),
        "max_h0_diff_flex_plan_w": float(h0_diff_flx),
        "max_h0_diff_v_start": float(h0_diff_vstart),
        "max_h0_diff_j1": float(h0_diff_j1),
        "max_h0_diff_j2": float(h0_diff_j2),
        "max_h0_diff_j3": float(h0_diff_j3),
        "max_h0_diff_j4": float(h0_diff_j4)
    }

    # G10 Hash Guards Check
    shutdown_guards = compute_guard_hashes()
    g10_pass = len(shutdown_guards) == 18
    audit_results["G10_Hash_Guards"] = {
        "pass": g10_pass,
        "verified_hashes_count": len(shutdown_guards)
    }

    all_audit_pass = all(item["pass"] for item in audit_results.values())
    print(f"Audit Gates G1-G11: {'ALL PASS' if all_audit_pass else 'FAIL'}")

    with open(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_AUDIT.json", "w") as f:
        json.dump(audit_results, f, indent=2)

    # ==============================================================================
    # COMPUTE OUTCOMES AND STATISTICS PER REALIZATION
    # ==============================================================================
    total_crit_demand_wh = 123 * 24 * 11600.0

    def compute_arm_real_metrics(arm_name: str, real_mode: str) -> Dict[str, Any]:
        rows = [r for r in all_hourly_rows if r["arm"] == arm_name and r["realization"] == real_mode]
        assert len(rows) == 2952, f"Expected 2952 rows for {arm_name}-{real_mode}, got {len(rows)}"

        fuel_tot = sum(r["diesel_fuel"] for r in rows)
        served_tot = sum(r["served_load"] for r in rows)
        unmet_tot = sum(r["unmet_load"] for r in rows)
        curtail_tot = sum(r["curtailment"] for r in rows)

        served_crit_first = sum(r["critical_served_first"] for r in rows)
        unmet_crit_first = sum(r["critical_unmet_first"] for r in rows)
        rel_crit_first = (served_crit_first / total_crit_demand_wh) * 100.0

        served_crit_prop = sum(r["critical_served_prop"] for r in rows)
        unmet_crit_prop = sum(r["critical_unmet_prop"] for r in rows)
        rel_prop = (served_crit_prop / total_crit_demand_wh) * 100.0

        socs = [r["soc_after"] for r in rows]
        min_soc = min(socs)
        max_soc = max(socs)
        soc_violations = sum(1 for s in socs if s < 19.999)

        diesel_on_hours = sum(1 for r in rows if r["diesel_power"] > 1e-3)
        startups = 0
        for oi in range(1, 124):
            o_rows = [r for r in rows if r["origin_id"] == oi]
            for step_i in range(24):
                if o_rows[step_i]["diesel_power"] > 1e-3 and (step_i == 0 or o_rows[step_i - 1]["diesel_power"] <= 1e-3):
                    startups += 1

        bat_throughput = sum(r["battery_charge"] + r["battery_discharge"] for r in rows)
        efc = bat_throughput / (2.0 * 200000.0)

        delta_c_tot = sum(r["delta_c_w"] for r in rows)
        mean_delta_c = delta_c_tot / 2952.0

        return {
            "arm": arm_name,
            "realization": real_mode,
            "diesel_fuel_l": fuel_tot,
            "critical_first_reliability_pct": rel_crit_first,
            "proportional_reliability_pct": rel_prop,
            "min_soc_pct": min_soc,
            "max_soc_pct": max_soc,
            "soc_violations_count": soc_violations,
            "unmet_load_kwh": unmet_tot / 1000.0,
            "curtailment_kwh": curtail_tot / 1000.0,
            "diesel_on_hours": diesel_on_hours,
            "diesel_startups": startups,
            "efc": efc,
            "mean_delta_c_w": mean_delta_c,
            "total_delta_c_kwh": delta_c_tot / 1000.0
        }

    arms = ["Control_Frozen_B", "Candidate_S", "Candidate_SW", "Candidate_SL", "Candidate_SWL"]
    metrics_by_arm_real = {}
    for r_mode in ("A", "B"):
        for a_name in arms:
            metrics_by_arm_real[(a_name, r_mode)] = compute_arm_real_metrics(a_name, r_mode)

    # Compute safety gates per realization
    def eval_safety(cand_m: Dict[str, Any], ctrl_m: Dict[str, Any]) -> Dict[str, Any]:
        d_cf = cand_m["critical_first_reliability_pct"] - ctrl_m["critical_first_reliability_pct"]
        d_prop = cand_m["proportional_reliability_pct"] - ctrl_m["proportional_reliability_pct"]
        min_s = cand_m["min_soc_pct"]
        soc_v = cand_m["soc_violations_count"]

        g1 = d_cf >= -1e-9
        g2 = d_prop >= -1e-9
        g3 = (soc_v == 0) and (min_s >= 20.00 - 1e-3)
        return {
            "delta_cf_pp": d_cf,
            "gate1_pass": bool(g1),
            "delta_prop_pp": d_prop,
            "gate2_pass": bool(g2),
            "min_soc_pct": min_s,
            "soc_violations": soc_v,
            "gate3_pass": bool(g3),
            "all_gates_pass": bool(g1 and g2 and g3)
        }

    safety_by_real = {}
    for r_mode in ("A", "B"):
        ctrl = metrics_by_arm_real[("Control_Frozen_B", r_mode)]
        safety_by_real[r_mode] = {
            "Candidate_S": eval_safety(metrics_by_arm_real[("Candidate_S", r_mode)], ctrl),
            "Candidate_SW": eval_safety(metrics_by_arm_real[("Candidate_SW", r_mode)], ctrl),
            "Candidate_SL": eval_safety(metrics_by_arm_real[("Candidate_SL", r_mode)], ctrl),
            "Candidate_SWL": eval_safety(metrics_by_arm_real[("Candidate_SWL", r_mode)], ctrl)
        }

    # Statistical Tests per Realization (Wilcoxon + Holm across 4 candidates)
    statistical_by_real = {}
    candidates = ["Candidate_S", "Candidate_SW", "Candidate_SL", "Candidate_SWL"]

    for r_mode in ("A", "B"):
        ctrl_fuel_arr = np.array([r[f"Control_Frozen_B_{r_mode}_diesel_fuel_liters"] for r in per_origin_records])
        ctrl_total_fuel = metrics_by_arm_real[("Control_Frozen_B", r_mode)]["diesel_fuel_l"]

        raw_pvals = []
        stats_list = []
        deltas_by_cand = {}

        for cand in candidates:
            cand_fuel_arr = np.array([r[f"{cand}_{r_mode}_diesel_fuel_liters"] for r in per_origin_records])
            delta_arr = ctrl_fuel_arr - cand_fuel_arr
            deltas_by_cand[cand] = delta_arr

            w_res = stats.wilcoxon(delta_arr, alternative="two-sided")
            raw_pvals.append(float(w_res.pvalue))
            stats_list.append(float(w_res.statistic))

        holm_pvals = holm_adjust_pvalues(raw_pvals)

        cand_stats = {}
        for idx, cand in enumerate(candidates):
            delta_arr = deltas_by_cand[cand]
            cand_total_fuel = metrics_by_arm_real[(cand, r_mode)]["diesel_fuel_l"]
            saving_l = ctrl_total_fuel - cand_total_fuel
            saving_pct = (saving_l / ctrl_total_fuel) * 100.0

            ci_low, ci_high = compute_bca_confidence_interval(delta_arr, confidence_level=0.95, n_resamples=10000, seed=42)
            sig = bool(holm_pvals[idx] < 0.05)
            diesel_gate_pass = bool(safety_by_real[r_mode][cand]["all_gates_pass"] and sig and (ci_low > 0.0))

            cand_stats[cand] = {
                "total_saving_l": saving_l,
                "saving_pct": saving_pct,
                "mean_paired_saving_l": float(np.mean(delta_arr)),
                "median_paired_saving_l": float(np.median(delta_arr)),
                "bca_95_ci_low_l": ci_low,
                "bca_95_ci_high_l": ci_high,
                "ci_strictly_positive": bool(ci_low > 0.0),
                "wilcoxon_stat": stats_list[idx],
                "wilcoxon_raw_p": raw_pvals[idx],
                "holm_adjusted_p": holm_pvals[idx],
                "holm_significant_at_005": sig,
                "diesel_gate_pass": diesel_gate_pass,
                "target_40pct_achieved": bool(saving_pct >= 40.0)
            }
        statistical_by_real[r_mode] = cand_stats

    # Pairwise A vs B Deltas per arm (B_o - A_o)
    a_vs_b_by_arm = {}
    fuel_diff_pvals = []
    arm_list = ["Control_Frozen_B", "Candidate_S", "Candidate_SW", "Candidate_SL", "Candidate_SWL"]

    for arm in arm_list:
        fuel_a = np.array([r[f"{arm}_A_diesel_fuel_liters"] for r in per_origin_records])
        fuel_b = np.array([r[f"{arm}_B_diesel_fuel_liters"] for r in per_origin_records])
        diff_fuel = fuel_b - fuel_a
        w_f = stats.wilcoxon(diff_fuel, alternative="two-sided")
        fuel_diff_pvals.append(float(w_f.pvalue))

    holm_fuel_diff_pvals = holm_adjust_pvalues(fuel_diff_pvals)

    for idx, arm in enumerate(arm_list):
        fuel_a = np.array([r[f"{arm}_A_diesel_fuel_liters"] for r in per_origin_records])
        fuel_b = np.array([r[f"{arm}_B_diesel_fuel_liters"] for r in per_origin_records])
        diff_fuel = fuel_b - fuel_a
        ci_fuel_low, ci_fuel_high = compute_bca_confidence_interval(diff_fuel, seed=42)

        # Reliability differences
        rcf_a = np.array([r[f"{arm}_A_served_crit_first_wh"] / (24 * 11600.0) * 100.0 for r in per_origin_records])
        rcf_b = np.array([r[f"{arm}_B_served_crit_first_wh"] / (24 * 11600.0) * 100.0 for r in per_origin_records])
        diff_rcf = rcf_b - rcf_a
        ci_rcf_low, ci_rcf_high = compute_bca_confidence_interval(diff_rcf, seed=42)

        rp_a = np.array([r[f"{arm}_A_served_crit_prop_wh"] / (24 * 11600.0) * 100.0 for r in per_origin_records])
        rp_b = np.array([r[f"{arm}_B_served_crit_prop_wh"] / (24 * 11600.0) * 100.0 for r in per_origin_records])
        diff_rp = rp_b - rp_a
        ci_rp_low, ci_rp_high = compute_bca_confidence_interval(diff_rp, seed=42)

        # Min SOC
        soc_a = np.array([r[f"{arm}_A_min_soc_pct"] for r in per_origin_records])
        soc_b = np.array([r[f"{arm}_B_min_soc_pct"] for r in per_origin_records])
        diff_soc = soc_b - soc_a

        # Delta C
        dc_a = np.array([r[f"{arm}_A_total_delta_c_wh"] for r in per_origin_records])
        dc_b = np.array([r[f"{arm}_B_total_delta_c_wh"] for r in per_origin_records])

        a_vs_b_by_arm[arm] = {
            "diff_fuel_total_l": float(np.sum(diff_fuel)),
            "diff_fuel_mean_l": float(np.mean(diff_fuel)),
            "diff_fuel_bca_95_ci": [ci_fuel_low, ci_fuel_high],
            "diff_fuel_raw_p": fuel_diff_pvals[idx],
            "diff_fuel_holm_p": holm_fuel_diff_pvals[idx],
            "diff_rcf_mean_pp": float(np.mean(diff_rcf)),
            "diff_rcf_bca_95_ci": [ci_rcf_low, ci_rcf_high],
            "diff_rp_mean_pp": float(np.mean(diff_rp)),
            "diff_rp_bca_95_ci": [ci_rp_low, ci_rp_high],
            "mean_min_soc_a": float(np.mean(soc_a)),
            "mean_min_soc_b": float(np.mean(soc_b)),
            "diff_min_soc_mean_pp": float(np.mean(diff_soc)),
            "mean_delta_c_a_wh": float(np.mean(dc_a)),
            "mean_delta_c_b_wh": float(np.mean(dc_b))
        }

    # ==============================================================================
    # WINNER DETERMINATION AND CLASSIFICATION
    # ==============================================================================
    def determine_winner(r_mode: str) -> Tuple[Optional[str], float]:
        qualified = []
        for cand in candidates:
            if statistical_by_real[r_mode][cand]["diesel_gate_pass"]:
                qualified.append((cand, statistical_by_real[r_mode][cand]["saving_pct"]))
        if not qualified:
            return None, 0.0
        qualified.sort(key=lambda x: x[1], reverse=True)
        return qualified[0][0], qualified[0][1]

    winner_a, win_saving_a = determine_winner("A")
    winner_b, win_saving_b = determine_winner("B")

    # Classification Precedence:
    # 1. BLOCKED
    # 2. SAFETY-CHANGING
    # 3. RANKING-CHANGING
    # 4. SENSITIVE
    # 5. ROBUST

    classification = "UNKNOWN"
    classification_reason = ""

    if not all_audit_pass:
        classification = "BLOCKED"
        classification_reason = "One or more audit gates G1-G11 failed."
    else:
        # Check safety changing
        safety_status_a = {c: safety_by_real["A"][c]["all_gates_pass"] for c in candidates}
        safety_status_b = {c: safety_by_real["B"][c]["all_gates_pass"] for c in candidates}
        safety_changed = any(safety_status_a[c] != safety_status_b[c] for c in candidates)

        # Check ranking changing
        # Compare qualified ordering
        qual_a = [c for c in candidates if statistical_by_real["A"][c]["diesel_gate_pass"]]
        qual_b = [c for c in candidates if statistical_by_real["B"][c]["diesel_gate_pass"]]
        winner_changed = (winner_a != winner_b)

        ranking_flipped = False
        # Pairwise ordering between safety-qualified candidates
        common_qual = [c for c in qual_a if c in qual_b]
        for i in range(len(common_qual)):
            for j in range(i + 1, len(common_qual)):
                c1, c2 = common_qual[i], common_qual[j]
                s1_a = statistical_by_real["A"][c1]["saving_pct"]
                s2_a = statistical_by_real["A"][c2]["saving_pct"]
                s1_b = statistical_by_real["B"][c1]["saving_pct"]
                s2_b = statistical_by_real["B"][c2]["saving_pct"]
                if (s1_a - s2_a) * (s1_b - s2_b) < 0:
                    ranking_flipped = True

        # Check sensitive thresholds: |Δ saving| >= 1.0 pp with CI excluding zero
        # or |ΔR_CF| >= 0.10 pp or |ΔR_P| >= 0.10 pp with CI excluding zero
        has_material_diff = False
        material_reasons = []

        for cand in candidates:
            sav_a = statistical_by_real["A"][cand]["saving_pct"]
            sav_b = statistical_by_real["B"][cand]["saving_pct"]
            delta_sav_pp = abs(sav_b - sav_a)

            ci_f_low, ci_f_high = a_vs_b_by_arm[cand]["diff_fuel_bca_95_ci"]
            ci_f_excludes_zero = (ci_f_low > 0 and ci_f_high > 0) or (ci_f_low < 0 and ci_f_high < 0)

            if delta_sav_pp >= 1.0 and ci_f_excludes_zero:
                has_material_diff = True
                material_reasons.append(f"{cand} saving diff {delta_sav_pp:.2f} pp >= 1.0 pp (CI: [{ci_f_low:.2f}, {ci_f_high:.2f}] L)")

            # Check reliability
            diff_rcf = abs(a_vs_b_by_arm[cand]["diff_rcf_mean_pp"])
            ci_rcf_low, ci_rcf_high = a_vs_b_by_arm[cand]["diff_rcf_bca_95_ci"]
            ci_rcf_excludes_zero = (ci_rcf_low > 0 and ci_rcf_high > 0) or (ci_rcf_low < 0 and ci_rcf_high < 0)

            if diff_rcf >= 0.10 and ci_rcf_excludes_zero:
                has_material_diff = True
                material_reasons.append(f"{cand} critical-first reliability diff {diff_rcf:.3f} pp >= 0.10 pp")

            diff_rp = abs(a_vs_b_by_arm[cand]["diff_rp_mean_pp"])
            ci_rp_low, ci_rp_high = a_vs_b_by_arm[cand]["diff_rp_bca_95_ci"]
            ci_rp_excludes_zero = (ci_rp_low > 0 and ci_rp_high > 0) or (ci_rp_low < 0 and ci_rp_high < 0)

            if diff_rp >= 0.10 and ci_rp_excludes_zero:
                has_material_diff = True
                material_reasons.append(f"{cand} proportional reliability diff {diff_rp:.3f} pp >= 0.10 pp")

        if safety_changed:
            classification = "SAFETY-CHANGING"
            classification_reason = f"Candidate safety gate status changed between A and B: A={safety_status_a}, B={safety_status_b}"
        elif winner_changed or ranking_flipped:
            classification = "RANKING-CHANGING"
            classification_reason = f"Winner or pairwise candidate ordering changed: Winner A={winner_a} vs Winner B={winner_b}"
        elif has_material_diff:
            classification = "SENSITIVE"
            classification_reason = f"Safety and winner invariant, but material differences detected: {'; '.join(material_reasons)}"
        else:
            classification = "ROBUST"
            classification_reason = "Safety gates, winner, and ranking are invariant; no material differences exceed preregistered thresholds."

    print(f"Classification: {classification}")
    print(f"Reason: {classification_reason}")
    print(f"Winner A: {winner_a} ({win_saving_a:.2f}%) | Winner B: {winner_b} ({win_saving_b:.2f}%)")

    # ==============================================================================
    # WRITE ALL REPORTS (MD and JSON)
    # ==============================================================================
    comparison_data = {
        "classification": classification,
        "classification_reason": classification_reason,
        "winner_arm_a": winner_a,
        "winner_saving_pct_a": win_saving_a,
        "winner_arm_b": winner_b,
        "winner_saving_pct_b": win_saving_b,
        "winner_retained": bool(winner_a == winner_b == "Candidate_S"),
        "metrics_by_arm_real": {f"{a}_{r}": metrics_by_arm_real[(a, r)] for a, r in metrics_by_arm_real},
        "safety_by_real": safety_by_real,
        "statistical_by_real": statistical_by_real,
        "a_vs_b_paired_deltas": a_vs_b_by_arm,
        "audit_gates": audit_results
    }

    with open(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_COMPARISON.json", "w") as f:
        json.dump(comparison_data, f, indent=2)

    with open(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_SAFETY_REPORT.json", "w") as f:
        json.dump(safety_by_real, f, indent=2)

    with open(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_STATISTICAL_REPORT.json", "w") as f:
        json.dump(statistical_by_real, f, indent=2)

    # Manifest
    manifest = {
        "experiment_id": "EXP-STAGE4-REALIZATION-CONSISTENCY-2025",
        "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "classification": classification,
        "winner_a": winner_a,
        "winner_b": winner_b,
        "winner_s_retained": bool(winner_a == winner_b == "Candidate_S"),
        "production_promotion_authorized": False,
        "total_origins": 123,
        "total_runs": 1230,
        "total_arm_hours": 29520,
        "audit_gates_pass": all_audit_pass,
        "cryptographic_guards": shutdown_guards,
        "artifacts": {
            "telemetry_csv": str(hourly_csv_path),
            "telemetry_json": str(hourly_json_path),
            "results_csv": str(per_origin_csv_path),
            "results_json": str(per_origin_json_path),
            "checkpoint_jsonl": str(CHECKPOINT_PATH),
            "comparison_json": str(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_COMPARISON.json"),
            "safety_report_json": str(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_SAFETY_REPORT.json"),
            "statistical_report_json": str(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_STATISTICAL_REPORT.json"),
            "audit_json": str(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_AUDIT.json")
        }
    }

    with open(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_EXECUTION_MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Markdown Reports
    # 1. Comparison MD
    comp_md = f"""# POLARIS Stage 4: Realization Consistency Experiment Comparison Report

**Experiment ID:** EXP-STAGE4-REALIZATION-CONSISTENCY-2025  
**Governing Preregistration:** `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md`  
**Classification:** **{classification}**  
**Classification Reason:** {classification_reason}  
**Winner Under Arm A:** {winner_a} ({win_saving_a:.2f}% saving)  
**Winner Under Arm B:** {winner_b} ({win_saving_b:.2f}% saving)  
**Candidate S Remains Winner:** {'YES' if winner_a == winner_b == 'Candidate_S' else 'NO'}  
**Production Promotion Authorized:** **NO** (Research findings only; operational policy not established)

---

## 1. Summary Metrics Comparison (Arm A vs Arm B)

| Arm | Realization | Fuel (L) | Saving (%) | R_CF (%) | R_P (%) | Min SOC (%) | SOC Violations | Unmet (kWh) | Curtail (kWh) | On Hours | Starts | EFC | Mean $\\delta_c$ (W) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
    for a_name in arms:
        mA = metrics_by_arm_real[(a_name, "A")]
        mB = metrics_by_arm_real[(a_name, "B")]
        savA = statistical_by_real["A"][a_name]["saving_pct"] if a_name != "Control_Frozen_B" else 0.0
        savB = statistical_by_real["B"][a_name]["saving_pct"] if a_name != "Control_Frozen_B" else 0.0
        comp_md += f"| {a_name} | A (Current) | {mA['diesel_fuel_l']:.2f} | {savA:.2f}% | {mA['critical_first_reliability_pct']:.4f}% | {mA['proportional_reliability_pct']:.4f}% | {mA['min_soc_pct']:.2f}% | {mA['soc_violations_count']} | {mA['unmet_load_kwh']:.2f} | {mA['curtailment_kwh']:.2f} | {mA['diesel_on_hours']} | {mA['diesel_startups']} | {mA['efc']:.2f} | {mA['mean_delta_c_w']:.2f} |\n"
        comp_md += f"| {a_name} | B (Plan-Consistent) | {mB['diesel_fuel_l']:.2f} | {savB:.2f}% | {mB['critical_first_reliability_pct']:.4f}% | {mB['proportional_reliability_pct']:.4f}% | {mB['min_soc_pct']:.2f}% | {mB['soc_violations_count']} | {mB['unmet_load_kwh']:.2f} | {mB['curtailment_kwh']:.2f} | {mB['diesel_on_hours']} | {mB['diesel_startups']} | {mB['efc']:.2f} | {mB['mean_delta_c_w']:.2f} |\n"

    comp_md += """
---

## 2. Safety Gates Status (Arm A vs Arm B)

| Candidate | Realization | Gate 1 (R_CF $\\ge$ Ctrl) | Gate 2 (R_P $\\ge$ Ctrl) | Gate 3 (SOC $\\ge$ 20%) | Safety Verdict |
|---|---|---|---|---|---|
"""
    for cand in candidates:
        sA = safety_by_real["A"][cand]
        sB = safety_by_real["B"][cand]
        comp_md += f"| {cand} | A | {'PASS' if sA['gate1_pass'] else 'FAIL'} ({sA['delta_cf_pp']:+.4f} pp) | {'PASS' if sA['gate2_pass'] else 'FAIL'} ({sA['delta_prop_pp']:+.4f} pp) | {'PASS' if sA['gate3_pass'] else 'FAIL'} (min {sA['min_soc_pct']:.2f}%) | **{'PASS' if sA['all_gates_pass'] else 'FAIL'}** |\n"
        comp_md += f"| {cand} | B | {'PASS' if sB['gate1_pass'] else 'FAIL'} ({sB['delta_cf_pp']:+.4f} pp) | {'PASS' if sB['gate2_pass'] else 'FAIL'} ({sB['delta_prop_pp']:+.4f} pp) | {'PASS' if sB['gate3_pass'] else 'FAIL'} (min {sB['min_soc_pct']:.2f}%) | **{'PASS' if sB['all_gates_pass'] else 'FAIL'}** |\n"

    comp_md += """
---

## 3. Statistical Diesel Saving Gates (Arm A vs Arm B)

| Candidate | Realization | Diesel Saving (L) | Saving (%) | Mean Paired Saving (L) | BCa 95% CI (L) | Wilcoxon Raw $p$ | Holm Adjusted $p$ | Diesel Gate |
|---|---|---|---|---|---|---|---|---|
"""
    for cand in candidates:
        stA = statistical_by_real["A"][cand]
        stB = statistical_by_real["B"][cand]
        comp_md += f"| {cand} | A | {stA['total_saving_l']:.2f} | {stA['saving_pct']:.2f}% | {stA['mean_paired_saving_l']:.2f} | [{stA['bca_95_ci_low_l']:.2f}, {stA['bca_95_ci_high_l']:.2f}] | {stA['wilcoxon_raw_p']:.4e} | {stA['holm_adjusted_p']:.4e} | **{'PASS' if stA['diesel_gate_pass'] else 'FAIL'}** |\n"
        comp_md += f"| {cand} | B | {stB['total_saving_l']:.2f} | {stB['saving_pct']:.2f}% | {stB['mean_paired_saving_l']:.2f} | [{stB['bca_95_ci_low_l']:.2f}, {stB['bca_95_ci_high_l']:.2f}] | {stB['wilcoxon_raw_p']:.4e} | {stB['holm_adjusted_p']:.4e} | **{'PASS' if stB['diesel_gate_pass'] else 'FAIL'}** |\n"

    comp_md += """
---

## 4. Paired A vs B Differences ($B_o - A_o$) per Arm

| Arm | Fuel Diff (L) | BCa 95% CI (L) | Holm $p$ | $\\Delta R_{CF}$ (pp) | BCa 95% CI (pp) | $\\Delta R_P$ (pp) | BCa 95% CI (pp) | $\\Delta$ Min SOC (pp) | Mean $\\delta_c$ Diff (W) |
|---|---|---|---|---|---|---|---|---|---|
"""
    for a_name in arms:
        d = a_vs_b_by_arm[a_name]
        comp_md += f"| {a_name} | {d['diff_fuel_total_l']:+.2f} | [{d['diff_fuel_bca_95_ci'][0]:+.2f}, {d['diff_fuel_bca_95_ci'][1]:+.2f}] | {d['diff_fuel_holm_p']:.4e} | {d['diff_rcf_mean_pp']:+.4f} | [{d['diff_rcf_bca_95_ci'][0]:+.4f}, {d['diff_rcf_bca_95_ci'][1]:+.4f}] | {d['diff_rp_mean_pp']:+.4f} | [{d['diff_rp_bca_95_ci'][0]:+.4f}, {d['diff_rp_bca_95_ci'][1]:+.4f}] | {d['diff_min_soc_mean_pp']:+.2f} | {d['mean_delta_c_b_wh'] - d['mean_delta_c_a_wh']:+.2f} |\n"

    comp_md += f"""
---

## 5. Audit Gates Summary (G1 - G11)

| Gate | Description | Status | Diagnostics |
|---|---|---|---|
| **G1** | Determinism (Arm A == Corrected Repro Telemetry) | **{'PASS' if audit_results['G1_Determinism']['pass'] else 'FAIL'}** | Max diff: diesel {audit_results['G1_Determinism']['max_diff_diesel_w']:.6f} W, chg {audit_results['G1_Determinism']['max_diff_battery_charge_w']:.6f} W |
| **G2** | Population Accounting (123 origins, 29,520 rows) | **{'PASS' if audit_results['G2_Accounting']['pass'] else 'FAIL'}** | Total rows: {audit_results['G2_Accounting']['total_rows']} |
| **G3** | Optimizer Status (All OPTIMAL) | **{'PASS' if audit_results['G3_Optimizer_Status']['pass'] else 'FAIL'}** | Non-optimal: {audit_results['G3_Optimizer_Status']['non_optimal_count']} |
| **G4** | Route Mode Propagation | **{'PASS' if audit_results['G4_Route_Propagation']['pass'] else 'FAIL'}** | Mismatches: {audit_results['G4_Route_Propagation']['mismatches_count']} |
| **G5** | EMERGENCY Rows Built (24 on EM, 0 on NORM) | **{'PASS' if audit_results['G5_EMERGENCY_Rows']['pass'] else 'FAIL'}** | Violations: {audit_results['G5_EMERGENCY_Rows']['violations_count']} |
| **G6** | Busbar Energy Balance (|error| $\\le$ 1e-3 W) | **{'PASS' if audit_results['G6_Busbar_Balance']['pass'] else 'FAIL'}** | Max error: {audit_results['G6_Busbar_Balance']['max_busbar_balance_error_w']:.6f} W |
| **G7** | SOC Floor Bounds & Continuity | **{'PASS' if audit_results['G7_SOC_Accounting']['pass'] else 'FAIL'}** | Min SOC: {audit_results['G7_SOC_Accounting']['min_soc_pct']:.2f}%, Violations: {audit_results['G7_SOC_Accounting']['soc_floor_violations_count']} |
| **G8** | Fuel Accounting & Starvation Check | **{'PASS' if audit_results['G8_Fuel_Accounting']['pass'] else 'FAIL'}** | Max diff: {audit_results['G8_Fuel_Accounting']['max_fuel_accounting_error_l']:.6f} L |
| **G9** | Planned vs Realized Reconciliation ($P_c, C, \\delta_c$) | **{'PASS' if audit_results['G9_Reconciliation']['pass'] else 'FAIL'}** | Missing: {len(audit_results['G9_Reconciliation']['missing_or_nan_fields'])} |
| **G11** | Hour-0 Optimizer Identity (A == B) | **{'PASS' if audit_results['G11_Hour0_Identity']['pass'] else 'FAIL'}** | Max diff: diesel {audit_results['G11_Hour0_Identity']['max_h0_diff_diesel_w']:.6f} W |
| **G10** | Cryptographic Hash Guards Before & After | **{'PASS' if audit_results['G10_Hash_Guards']['pass'] else 'FAIL'}** | Verified: {audit_results['G10_Hash_Guards']['verified_hashes_count']} files |
"""

    with open(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_COMPARISON.md", "w") as f:
        f.write(comp_md)

    with open(OUT_DIR / "STAGE4_REALIZATION_CONSISTENCY_SUMMARY.md", "w") as f:
        f.write(comp_md)

    print("Execution complete. All artifacts generated successfully.")


if __name__ == "__main__":
    main()
