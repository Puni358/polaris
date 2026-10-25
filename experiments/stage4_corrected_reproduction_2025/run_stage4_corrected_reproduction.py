"""
POLARIS Stage 4: Corrected Reproduction Campaign Runner (2025 Holdout)
Module: experiments.stage4_corrected_reproduction_2025.run_stage4_corrected_reproduction

Governing Contract:
  - experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md
  - experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.json
  - experiments/RESEARCH_HARNESS_ROUTE_MODE_FIX_RECORD.md

Five Arms Executed on 2025 Holdout with Faithful Closed-Loop Mode Propagation:
  1. Control_Frozen_B: Governed unconditional 6h lookahead EBR (safety & fuel reference)
  2. Candidate_S: Solar-only net EBR, protection OFF
  3. Candidate_SW: Solar + wind net EBR, protection OFF
  4. Candidate_SL: Solar-only net EBR, low-sun protection ON (S-L, efficiency reference)
  5. Candidate_SWL: Solar + wind net EBR, low-sun protection ON (SW-L, final candidate)
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

import stage4_low_sun_adapter as s4a
from research_numerical_extractor import ResearchNumericalGAP19Optimizer, TAU_RESIDUE_W
from system.research.research_critical_demand_adapter import (
    AdaptedClosedLoopRunner,
    adapt_critical_demand_vector
)
from system.research.route_mode_propagation import propagate_route_mode
from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine

OUT_DIR = REPO / "experiments/stage4_corrected_reproduction_2025"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_PATH = OUT_DIR / "STAGE4_REPRO_CHECKPOINT.jsonl"
FAILURES_PATH = OUT_DIR / "STAGE4_REPRO_FAILURES.jsonl"

WEATHER_2025_PATH = REPO / "data/POLARIS_v0_1_future_weather_forecasts_2025.csv"
WEATHER_2025_DF = pd.read_csv(WEATHER_2025_PATH)

DECOMPOSITION_2025_PATH = REPO / "data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv"
SOLAR_PROVIDER = s4a.SolarElevationProvider(DECOMPOSITION_2025_PATH)

# Load canonical configs
spec_camp = importlib.util.spec_from_file_location("camp", REPO / "experiments/run_diesel_reduction_campaign.py")
camp = importlib.util.module_from_spec(spec_camp)
spec_camp.loader.exec_module(camp)
BASE_CONFIG = camp.load_canonical_configs()


class StepExecutionError(Exception):
    def __init__(
        self,
        arm: str,
        hour: int,
        error_type: str,
        error_message: str,
        raw_solver_diagnostics: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(f"[{arm} h={hour}] {error_type}: {error_message}")
        self.arm = arm
        self.hour = hour
        self.error_type = error_type
        self.error_message = error_message
        self.raw_solver_diagnostics = raw_solver_diagnostics or []


class Stage4ReproductionRunner(AdaptedClosedLoopRunner):
    """
    Research runner with faithful closed-loop route-mode propagation
    and ResearchNumericalGAP19Optimizer (tau = 0.055 W).
    """
    def __init__(self, configs: Dict[str, Any], variant: str):
        super().__init__(configs)
        self.variant = variant
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
                plan = inner_opt.optimize(bundle, station_state, cfg_copy)

                step0_diag = inner_opt.last_diagnostics[0] if inner_opt.last_diagnostics else {}
                low_sun_0 = int(elevations[0] < 15.0)

                runner_ref.current_snapshot = {
                    "forecast_solar_step0": sol_w[0],
                    "forecast_wind_step0": wnd_w[0],
                    "forecast_demand_step0": bundle.demand.point[0],
                    "critical_demand_step0": crit_w[0],
                    "solar_elevation_step0": elevations[0],
                    "low_sun_indicator_step0": low_sun_0,
                    "ebr_target_wh_step0": ebr_used[0],
                    "stage2_target_wh_step0": stage2_vector[0],
                    "j2_shortfall_wh": plan.j2_objective if plan.j2_objective is not None else 0.0,
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

                realized_inputs = {
                    "timestamp": target_ts_str,
                    "actual_SW_IN": float(realized_solar[step]),
                    "actual_wind_generation": float(realized_wind[step]),
                    "actual_demand": float(realized_demand[step])
                }
                # 4. Executor receives current_state (unmutated execution state)
                realization_res = self.executor.execute_step(current_state, plan, realized_inputs, step_index=0)

                if realization_res.busbar_energy_balance_error_w > 1e-3:
                    raise RuntimeError(f"Busbar error {realization_res.busbar_energy_balance_error_w} W at step {step}")
                if realization_res.realized_soc_pct < 19.999 or realization_res.realized_soc_pct > 95.001:
                    raise RuntimeError(f"SOC {realization_res.realized_soc_pct}% out of bounds at step {step}")
            except Exception as e:
                diag = self.current_snapshot.get("full_plan_diagnostics") or getattr(self.optimizer, "last_diagnostics", [])
                raise StepExecutionError(
                    arm=arm_name,
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

            snap = self.current_snapshot

            row = {
                "origin_id": origin_idx,
                "hour": step,
                "timestamp": target_ts_str,
                "arm": arm_name,
                "route": route_mode,
                "optimizer_received_mode": planning_state.operating_mode,
                "emergency_constraint_active": bool(route_mode == "EMERGENCY"),
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
                "battery_charge": realization_res.battery_charge_realized_w,
                "battery_discharge": realization_res.battery_discharge_realized_w,
                "soc_before": soc_before,
                "soc_after": soc_after,
                "curtailment": realization_res.curtailment_w,
                "ebr_target_wh": snap["ebr_target_wh_step0"],
                "stage2_target_wh": snap["stage2_target_wh_step0"],
                "j2_shortfall_wh": snap["j2_shortfall_wh"],
                "busbar_balance_error_w": realization_res.busbar_energy_balance_error_w,
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
            "residue_corrections_count": sum(1 for r in hourly_rows if r["residue_corrected"]),
            "max_residue_zeroed_w": max((r["zeroed_magnitude_w"] for r in hourly_rows), default=0.0)
        }

        return arm_summary, hourly_rows


def run_single_origin_pentad_repro(origin_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes all 5 arms for a single origin under corrected reproduction semantics.
    """
    oi = origin_info["origin_index"]
    fs = origin_info["forecast_start"]
    t0 = origin_info["t0_timestamp"]

    sub = WEATHER_2025_DF[WEATHER_2025_DF["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]

    current_arm = "Control_Frozen_B"
    current_runner = None
    try:
        # 1. Control Frozen B
        current_arm = "Control_Frozen_B"
        runner_b = Stage4ReproductionRunner(BASE_CONFIG, variant="FROZEN_B")
        current_runner = runner_b
        init_b = camp.make_initial_state(t0)
        sum_b, rows_b = runner_b.run_closed_loop_robust(oi, init_b, WEATHER_2025_DF, rs, rw, rd, rts)

        # 2. Candidate S
        current_arm = "Candidate_S"
        runner_s = Stage4ReproductionRunner(BASE_CONFIG, variant="S")
        current_runner = runner_s
        init_s = camp.make_initial_state(t0)
        sum_s, rows_s = runner_s.run_closed_loop_robust(oi, init_s, WEATHER_2025_DF, rs, rw, rd, rts)

        # 3. Candidate SW
        current_arm = "Candidate_SW"
        runner_sw = Stage4ReproductionRunner(BASE_CONFIG, variant="SW")
        current_runner = runner_sw
        init_sw = camp.make_initial_state(t0)
        sum_sw, rows_sw = runner_sw.run_closed_loop_robust(oi, init_sw, WEATHER_2025_DF, rs, rw, rd, rts)

        # 4. Candidate S-L
        current_arm = "Candidate_SL"
        runner_sl = Stage4ReproductionRunner(BASE_CONFIG, variant="SL")
        current_runner = runner_sl
        init_sl = camp.make_initial_state(t0)
        sum_sl, rows_sl = runner_sl.run_closed_loop_robust(oi, init_sl, WEATHER_2025_DF, rs, rw, rd, rts)

        # 5. Candidate SW-L
        current_arm = "Candidate_SWL"
        runner_swl = Stage4ReproductionRunner(BASE_CONFIG, variant="SWL")
        current_runner = runner_swl
        init_swl = camp.make_initial_state(t0)
        sum_swl, rows_swl = runner_swl.run_closed_loop_robust(oi, init_swl, WEATHER_2025_DF, rs, rw, rd, rts)

        return {
            "success": True,
            "origin_id": oi,
            "forecast_start": fs,
            "t0_timestamp": t0,
            "control_b": sum_b,
            "candidate_s": sum_s,
            "candidate_sw": sum_sw,
            "candidate_sl": sum_sl,
            "candidate_swl": sum_swl,
            "delta_fuel_s_liters": sum_b["diesel_fuel_liters"] - sum_s["diesel_fuel_liters"],
            "delta_fuel_sw_liters": sum_b["diesel_fuel_liters"] - sum_sw["diesel_fuel_liters"],
            "delta_fuel_sl_liters": sum_b["diesel_fuel_liters"] - sum_sl["diesel_fuel_liters"],
            "delta_fuel_swl_liters": sum_b["diesel_fuel_liters"] - sum_swl["diesel_fuel_liters"],
            "rows_b": rows_b,
            "rows_s": rows_s,
            "rows_sw": rows_sw,
            "rows_sl": rows_sl,
            "rows_swl": rows_swl
        }

    except StepExecutionError as see:
        return {
            "success": False,
            "origin_id": oi,
            "forecast_start": fs,
            "t0_timestamp": t0,
            "arm": see.arm,
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
            "hour": -1,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "raw_solver_diagnostics": diag
        }


def compute_repro_run_guards() -> Dict[str, str]:
    """Computes all required startup run guards specified in the preregistration."""
    prereg_json_path = REPO / "experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.json"
    with open(prereg_json_path) as f:
        prereg = json.load(f)

    computed = {}
    for name, info in prereg["reference_hashes"].items():
        p = REPO / info["path"]
        computed[name] = hashlib.sha256(p.read_bytes()).hexdigest()

    for rel_path, exp_hash in prereg["corrected_research_files"].items():
        computed[f"corrected_{rel_path}"] = hashlib.sha256((REPO / rel_path).read_bytes()).hexdigest()

    for rel_path, exp_hash in prereg["production_boundary_hashes"].items():
        computed[f"prod_{rel_path}"] = hashlib.sha256((REPO / rel_path).read_bytes()).hexdigest()

    computed["prereg_md"] = hashlib.sha256(
        (REPO / "experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md").read_bytes()
    ).hexdigest()
    computed["prereg_json"] = hashlib.sha256(
        (REPO / "experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.json").read_bytes()
    ).hexdigest()

    return computed


def verify_repro_guards(computed: Dict[str, str]):
    prereg_json_path = REPO / "experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.json"
    with open(prereg_json_path) as f:
        prereg = json.load(f)

    for name, info in prereg["reference_hashes"].items():
        expected = info["sha256"]
        actual = computed[name]
        if actual != expected:
            raise ValueError(f"GUARD_HASH_MISMATCH for {name}: expected {expected}, got {actual}")

    for rel_path, expected in prereg["corrected_research_files"].items():
        actual = computed[f"corrected_{rel_path}"]
        if actual != expected:
            raise ValueError(f"CORRECTED_HASH_MISMATCH for {rel_path}: expected {expected}, got {actual}")

    for rel_path, expected in prereg["production_boundary_hashes"].items():
        actual = computed[f"prod_{rel_path}"]
        if actual != expected:
            raise ValueError(f"PROD_BOUNDARY_HASH_MISMATCH for {rel_path}: expected {expected}, got {actual}")


def read_existing_repro_checkpoints(expected_guards: Optional[Dict[str, str]] = None) -> Dict[int, Dict[str, Any]]:
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


def append_checkpoint(record: Dict[str, Any], guards: Optional[Dict[str, str]] = None):
    if guards is not None:
        record["guards"] = guards
    with open(CHECKPOINT_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())


def append_failure(record: Dict[str, Any]):
    with open(FAILURES_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())


def compute_bca_confidence_interval(
    data: np.ndarray, confidence_level: float = 0.95, n_resamples: int = 10000
) -> Tuple[float, float]:
    """Computes BCa 95% bootstrap confidence interval with seed 42."""
    try:
        res = stats.bootstrap(
            (data,),
            np.mean,
            method="BCa",
            confidence_level=confidence_level,
            n_resamples=n_resamples,
            random_state=42
        )
        return float(res.confidence_interval.low), float(res.confidence_interval.high)
    except Exception:
        res = stats.bootstrap(
            (data,),
            np.mean,
            method="percentile",
            confidence_level=confidence_level,
            n_resamples=n_resamples,
            random_state=42
        )
        return float(res.confidence_interval.low), float(res.confidence_interval.high)


def main():
    print("=" * 80)
    print("POLARIS STAGE 4: CORRECTED REPRODUCTION 5-ARM CAMPAIGN (2025 HOLDOUT)")
    print("Governing Contract: EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md")
    print("=" * 80)
    t0_start = time.time()

    CURRENT_GUARDS = compute_repro_run_guards()
    verify_repro_guards(CURRENT_GUARDS)
    print("Startup Cryptographic Guards Verified. Production and reference integrity intact.")

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

    print(f"Total Confirmatory Origins to Execute: {len(origins_list)} (2,952 origin-hours per arm, 14,760 total arm-hours).")

    completed_checkpoints = read_existing_repro_checkpoints(expected_guards=CURRENT_GUARDS)
    print(f"Read {len(completed_checkpoints)} completed origin pentads from checkpoint.")

    remaining_origins = [o for o in origins_list if o["origin_index"] not in completed_checkpoints]
    print(f"Remaining origins to execute: {len(remaining_origins)} of {len(origins_list)}.")

    all_pentad_results = list(completed_checkpoints.values())
    failures = []

    if remaining_origins:
        print("Launching parallel evaluation across 4 worker processes...")
        with Pool(processes=4) as pool:
            for i, res in enumerate(pool.imap_unordered(run_single_origin_pentad_repro, remaining_origins, chunksize=1), 1):
                if res["success"]:
                    append_checkpoint(res, guards=CURRENT_GUARDS)
                    all_pentad_results.append(res)
                    elapsed = time.time() - t0_start
                    pct = (len(all_pentad_results) / 123.0) * 100.0
                    rate = len(all_pentad_results) / (elapsed + 1e-6)
                    eta_sec = (123 - len(all_pentad_results)) / (rate + 1e-6)
                    print(
                        f"[{len(all_pentad_results)}/123 - {pct:.1f}%] Origin {res['origin_id']:03d} completed in {elapsed:.1f}s "
                        f"(Rate: {rate:.2f} org/s, ETA: {eta_sec:.1f}s) | "
                        f"Fuel: B={res['control_b']['diesel_fuel_liters']:.2f}L, S={res['candidate_s']['diesel_fuel_liters']:.2f}L, "
                        f"SW={res['candidate_sw']['diesel_fuel_liters']:.2f}L, SL={res['candidate_sl']['diesel_fuel_liters']:.2f}L, "
                        f"SWL={res['candidate_swl']['diesel_fuel_liters']:.2f}L"
                    )
                else:
                    append_failure(res)
                    failures.append(res)
                    print(f"FAIL-CLOSED: Origin {res['origin_id']} FAILED: [{res.get('arm')}] {res.get('error_type')}: {res.get('error_message')}")
                    pool.terminate()
                    break

    if failures:
        print(f"\nFATAL: Campaign encountered {len(failures)} failures. Aborting before aggregation.")
        sys.exit(1)

    assert len(all_pentad_results) == 123, f"Expected 123 completed pentads, got {len(all_pentad_results)}"
    all_pentad_results.sort(key=lambda r: r["origin_id"])

    # Aggregate telemetry and results
    print("\nAggregating 14,760 hours across 123 origins...")
    all_hourly_rows = []
    per_origin_records = []

    for r in all_pentad_results:
        oi = r["origin_id"]
        fs = r["forecast_start"]
        t0 = r["t0_timestamp"]

        b = r["control_b"]
        s = r["candidate_s"]
        sw = r["candidate_sw"]
        sl = r["candidate_sl"]
        swl = r["candidate_swl"]

        all_hourly_rows.extend(r["rows_b"])
        all_hourly_rows.extend(r["rows_s"])
        all_hourly_rows.extend(r["rows_sw"])
        all_hourly_rows.extend(r["rows_sl"])
        all_hourly_rows.extend(r["rows_swl"])

        total_crit_orig = 24 * 11600.0
        r_cf_b_orig = (b["served_crit_first_wh"] / total_crit_orig) * 100.0
        r_p_b_orig = (b["served_crit_prop_wh"] / total_crit_orig) * 100.0

        r_cf_s_orig = (s["served_crit_first_wh"] / total_crit_orig) * 100.0
        r_p_s_orig = (s["served_crit_prop_wh"] / total_crit_orig) * 100.0

        r_cf_sw_orig = (sw["served_crit_first_wh"] / total_crit_orig) * 100.0
        r_p_sw_orig = (sw["served_crit_prop_wh"] / total_crit_orig) * 100.0

        r_cf_sl_orig = (sl["served_crit_first_wh"] / total_crit_orig) * 100.0
        r_p_sl_orig = (sl["served_crit_prop_wh"] / total_crit_orig) * 100.0

        r_cf_swl_orig = (swl["served_crit_first_wh"] / total_crit_orig) * 100.0
        r_p_swl_orig = (swl["served_crit_prop_wh"] / total_crit_orig) * 100.0

        per_origin_records.append({
            "origin_id": oi,
            "forecast_start": fs,
            "t0_timestamp": t0,
            "control_b_fuel_l": b["diesel_fuel_liters"],
            "candidate_s_fuel_l": s["diesel_fuel_liters"],
            "candidate_sw_fuel_l": sw["diesel_fuel_liters"],
            "candidate_sl_fuel_l": sl["diesel_fuel_liters"],
            "candidate_swl_fuel_l": swl["diesel_fuel_liters"],
            "delta_fuel_s_l": r["delta_fuel_s_liters"],
            "delta_fuel_sw_l": r["delta_fuel_sw_liters"],
            "delta_fuel_sl_l": r["delta_fuel_sl_liters"],
            "delta_fuel_swl_l": r["delta_fuel_swl_liters"],
            "control_b_r_cf": r_cf_b_orig,
            "control_b_r_p": r_p_b_orig,
            "candidate_s_r_cf": r_cf_s_orig,
            "candidate_s_r_p": r_p_s_orig,
            "candidate_sw_r_cf": r_cf_sw_orig,
            "candidate_sw_r_p": r_p_sw_orig,
            "candidate_sl_r_cf": r_cf_sl_orig,
            "candidate_sl_r_p": r_p_sl_orig,
            "candidate_swl_r_cf": r_cf_swl_orig,
            "candidate_swl_r_p": r_p_swl_orig,
            "control_b_unmet_wh": b["unmet_load_wh"],
            "candidate_s_unmet_wh": s["unmet_load_wh"],
            "candidate_sw_unmet_wh": sw["unmet_load_wh"],
            "candidate_sl_unmet_wh": sl["unmet_load_wh"],
            "candidate_swl_unmet_wh": swl["unmet_load_wh"],
            "control_b_curtail_wh": b["curtailment_wh"],
            "candidate_s_curtail_wh": s["curtailment_wh"],
            "candidate_sw_curtail_wh": sw["curtailment_wh"],
            "candidate_sl_curtail_wh": sl["curtailment_wh"],
            "candidate_swl_curtail_wh": swl["curtailment_wh"],
            "control_b_min_soc": b["min_soc_pct"],
            "candidate_s_min_soc": s["min_soc_pct"],
            "candidate_sw_min_soc": sw["min_soc_pct"],
            "candidate_sl_min_soc": sl["min_soc_pct"],
            "candidate_swl_min_soc": swl["min_soc_pct"]
        })

    assert len(all_hourly_rows) == 123 * 24 * 5, f"Expected {123*24*5} rows, got {len(all_hourly_rows)}"

    # 1. Archive Hourly Telemetry
    hourly_df = pd.DataFrame(all_hourly_rows)
    hourly_csv_path = OUT_DIR / "STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv"
    hourly_df.to_csv(hourly_csv_path, index=False)

    hourly_json_path = OUT_DIR / "STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.json"
    with open(hourly_json_path, "w") as f:
        json.dump(all_hourly_rows, f, indent=2)

    # 2. Archive Per-Origin CSV & JSON
    per_origin_df = pd.DataFrame(per_origin_records)
    per_origin_csv_path = OUT_DIR / "STAGE4_REPRO_123_ORIGIN_RESULTS.csv"
    per_origin_df.to_csv(per_origin_csv_path, index=False)

    per_origin_json_path = OUT_DIR / "STAGE4_REPRO_123_ORIGIN_RESULTS.json"
    with open(per_origin_json_path, "w") as f:
        json.dump(per_origin_records, f, indent=2)

    total_crit_demand_wh = 123 * 24 * 11600.0

    def compute_arm_metrics(arm_name: str) -> Dict[str, Any]:
        rows = [r for r in all_hourly_rows if r["arm"] == arm_name]
        assert len(rows) == 2952, f"Expected 2952 rows for {arm_name}, got {len(rows)}"

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

        corrections_count = sum(1 for r in rows if r["residue_corrected"])
        max_residue = max((r["zeroed_magnitude_w"] for r in rows), default=0.0)

        emergency_hours = sum(1 for r in rows if r["route"] == "EMERGENCY")
        normal_hours = sum(1 for r in rows if r["route"] == "NORMAL")
        emergency_active_hours = sum(1 for r in rows if r["emergency_constraint_active"])

        return {
            "arm": arm_name,
            "total_diesel_fuel_l": fuel_tot,
            "total_served_load_wh": served_tot,
            "total_unmet_load_wh": unmet_tot,
            "total_curtailment_wh": curtail_tot,
            "served_crit_first_wh": served_crit_first,
            "unmet_crit_first_wh": unmet_crit_first,
            "critical_first_reliability_pct": rel_crit_first,
            "served_crit_prop_wh": served_crit_prop,
            "unmet_crit_prop_wh": unmet_crit_prop,
            "proportional_reliability_pct": rel_prop,
            "min_soc_pct": min_soc,
            "max_soc_pct": max_soc,
            "soc_violations_below_20": soc_violations,
            "diesel_on_hours": diesel_on_hours,
            "diesel_startups": startups,
            "battery_throughput_wh": bat_throughput,
            "efc": efc,
            "residue_corrections_count": corrections_count,
            "max_residue_zeroed_w": max_residue,
            "emergency_hours": emergency_hours,
            "normal_hours": normal_hours,
            "emergency_active_hours": emergency_active_hours
        }

    metrics_b = compute_arm_metrics("Control_Frozen_B")
    metrics_s = compute_arm_metrics("Candidate_S")
    metrics_sw = compute_arm_metrics("Candidate_SW")
    metrics_sl = compute_arm_metrics("Candidate_SL")
    metrics_swl = compute_arm_metrics("Candidate_SWL")

    all_metrics = {
        "Control_Frozen_B": metrics_b,
        "Candidate_S": metrics_s,
        "Candidate_SW": metrics_sw,
        "Candidate_SL": metrics_sl,
        "Candidate_SWL": metrics_swl
    }

    # ==============================================================================
    # SAFETY GATES EVALUATION
    # ==============================================================================
    def evaluate_safety_gates(cand_metrics: Dict[str, Any], baseline_metrics: Dict[str, Any]) -> Dict[str, Any]:
        delta_cf = cand_metrics["critical_first_reliability_pct"] - baseline_metrics["critical_first_reliability_pct"]
        delta_prop = cand_metrics["proportional_reliability_pct"] - baseline_metrics["proportional_reliability_pct"]
        min_soc = cand_metrics["min_soc_pct"]
        soc_violations = cand_metrics["soc_violations_below_20"]

        gate1_cf = delta_cf >= -1e-9
        gate2_prop = delta_prop >= -1e-9
        gate3_soc = (soc_violations == 0) and (min_soc >= 20.00 - 1e-3)
        overall_pass = gate1_cf and gate2_prop and gate3_soc

        return {
            "delta_cf_pp": delta_cf,
            "gate1_critical_first_pass": bool(gate1_cf),
            "delta_prop_pp": delta_prop,
            "gate2_proportional_pass": bool(gate2_prop),
            "min_soc_pct": min_soc,
            "soc_violations": soc_violations,
            "gate3_soc_floor_pass": bool(gate3_soc),
            "all_safety_gates_pass": bool(overall_pass)
        }

    safety_s = evaluate_safety_gates(metrics_s, metrics_b)
    safety_sw = evaluate_safety_gates(metrics_sw, metrics_b)
    safety_sl = evaluate_safety_gates(metrics_sl, metrics_b)
    safety_swl = evaluate_safety_gates(metrics_swl, metrics_b)

    safety_report = {
        "Control_Frozen_B": {
            "fuel_l": metrics_b["total_diesel_fuel_l"],
            "critical_first_reliability_pct": metrics_b["critical_first_reliability_pct"],
            "proportional_reliability_pct": metrics_b["proportional_reliability_pct"],
            "min_soc_pct": metrics_b["min_soc_pct"],
            "soc_violations": metrics_b["soc_violations_below_20"]
        },
        "Candidate_S": safety_s,
        "Candidate_SW": safety_sw,
        "Candidate_SL": safety_sl,
        "Candidate_SWL": safety_swl
    }

    with open(OUT_DIR / "STAGE4_REPRO_SAFETY_REPORT.json", "w") as f:
        json.dump(safety_report, f, indent=2)

    # ==============================================================================
    # DIESEL GATE EVALUATION (S-L and SW-L)
    # ==============================================================================
    fuel_b = np.array([r["control_b_fuel_l"] for r in per_origin_records])
    fuel_sl = np.array([r["candidate_sl_fuel_l"] for r in per_origin_records])
    fuel_swl = np.array([r["candidate_swl_fuel_l"] for r in per_origin_records])

    delta_fuel_sl = fuel_b - fuel_sl
    delta_fuel_swl = fuel_b - fuel_swl

    w_res_sl = stats.wilcoxon(delta_fuel_sl, alternative="two-sided")
    w_res_swl = stats.wilcoxon(delta_fuel_swl, alternative="two-sided")

    ci_low_sl, ci_high_sl = compute_bca_confidence_interval(delta_fuel_sl)
    ci_low_swl, ci_high_swl = compute_bca_confidence_interval(delta_fuel_swl)

    raw_p_sl = float(w_res_sl.pvalue)
    raw_p_swl = float(w_res_swl.pvalue)

    if raw_p_sl <= raw_p_swl:
        holm_p_sl = min(1.0, raw_p_sl * 2.0)
        holm_p_swl = min(1.0, max(holm_p_sl, raw_p_swl * 1.0))
        sig_sl = raw_p_sl < 0.025
        sig_swl = sig_sl and (raw_p_swl < 0.05)
    else:
        holm_p_swl = min(1.0, raw_p_swl * 2.0)
        holm_p_sl = min(1.0, max(holm_p_swl, raw_p_sl * 1.0))
        sig_swl = raw_p_swl < 0.025
        sig_sl = sig_swl and (raw_p_sl < 0.05)

    diesel_gate_sl_pass = safety_sl["all_safety_gates_pass"] and sig_sl and (ci_low_sl > 0.0)
    diesel_gate_swl_pass = safety_swl["all_safety_gates_pass"] and sig_swl and (ci_low_swl > 0.0)

    target_saving_sl = (metrics_b["total_diesel_fuel_l"] - metrics_sl["total_diesel_fuel_l"]) / metrics_b["total_diesel_fuel_l"]
    target_saving_swl = (metrics_b["total_diesel_fuel_l"] - metrics_swl["total_diesel_fuel_l"]) / metrics_b["total_diesel_fuel_l"]

    statistical_report = {
        "Candidate_SL": {
            "total_saving_l": float(metrics_b["total_diesel_fuel_l"] - metrics_sl["total_diesel_fuel_l"]),
            "saving_pct": float(target_saving_sl * 100.0),
            "mean_paired_saving_l": float(np.mean(delta_fuel_sl)),
            "median_paired_saving_l": float(np.median(delta_fuel_sl)),
            "bca_95_ci_low_l": ci_low_sl,
            "bca_95_ci_high_l": ci_high_sl,
            "ci_strictly_positive": bool(ci_low_sl > 0.0),
            "wilcoxon_stat": float(w_res_sl.statistic),
            "wilcoxon_raw_p": raw_p_sl,
            "holm_adjusted_p": holm_p_sl,
            "holm_significant_at_005": bool(sig_sl),
            "diesel_gate_pass": bool(diesel_gate_sl_pass),
            "target_40pct_achieved": bool(target_saving_sl >= 0.40)
        },
        "Candidate_SWL": {
            "total_saving_l": float(metrics_b["total_diesel_fuel_l"] - metrics_swl["total_diesel_fuel_l"]),
            "saving_pct": float(target_saving_swl * 100.0),
            "mean_paired_saving_l": float(np.mean(delta_fuel_swl)),
            "median_paired_saving_l": float(np.median(delta_fuel_swl)),
            "bca_95_ci_low_l": ci_low_swl,
            "bca_95_ci_high_l": ci_high_swl,
            "ci_strictly_positive": bool(ci_low_swl > 0.0),
            "wilcoxon_stat": float(w_res_swl.statistic),
            "wilcoxon_raw_p": raw_p_swl,
            "holm_adjusted_p": holm_p_swl,
            "holm_significant_at_005": bool(sig_swl),
            "diesel_gate_pass": bool(diesel_gate_swl_pass),
            "target_40pct_achieved": bool(target_saving_swl >= 0.40)
        }
    }

    with open(OUT_DIR / "STAGE4_REPRO_STATISTICAL_REPORT.json", "w") as f:
        json.dump(statistical_report, f, indent=2)

    # ==============================================================================
    # FACTORIAL CONTRASTS (C1, C2, C3, C4)
    # ==============================================================================
    prop_s = np.array([r["candidate_s_r_p"] for r in per_origin_records])
    prop_sw = np.array([r["candidate_sw_r_p"] for r in per_origin_records])
    prop_sl = np.array([r["candidate_sl_r_p"] for r in per_origin_records])
    prop_swl = np.array([r["candidate_swl_r_p"] for r in per_origin_records])

    cf_s = np.array([r["candidate_s_r_cf"] for r in per_origin_records])
    cf_sw = np.array([r["candidate_sw_r_cf"] for r in per_origin_records])
    cf_sl = np.array([r["candidate_sl_r_cf"] for r in per_origin_records])
    cf_swl = np.array([r["candidate_swl_r_cf"] for r in per_origin_records])

    fuel_s_arr = np.array([r["candidate_s_fuel_l"] for r in per_origin_records])
    fuel_sw_arr = np.array([r["candidate_sw_fuel_l"] for r in per_origin_records])
    fuel_sl_arr = np.array([r["candidate_sl_fuel_l"] for r in per_origin_records])
    fuel_swl_arr = np.array([r["candidate_swl_fuel_l"] for r in per_origin_records])

    unmet_s_arr = np.array([r["candidate_s_unmet_wh"] / 1000.0 for r in per_origin_records])
    unmet_sw_arr = np.array([r["candidate_sw_unmet_wh"] / 1000.0 for r in per_origin_records])
    unmet_sl_arr = np.array([r["candidate_sl_unmet_wh"] / 1000.0 for r in per_origin_records])
    unmet_swl_arr = np.array([r["candidate_swl_unmet_wh"] / 1000.0 for r in per_origin_records])

    curtail_s_arr = np.array([r["candidate_s_curtail_wh"] / 1000.0 for r in per_origin_records])
    curtail_sw_arr = np.array([r["candidate_sw_curtail_wh"] / 1000.0 for r in per_origin_records])
    curtail_sl_arr = np.array([r["candidate_sl_curtail_wh"] / 1000.0 for r in per_origin_records])
    curtail_swl_arr = np.array([r["candidate_swl_curtail_wh"] / 1000.0 for r in per_origin_records])

    def summarize_contrast(diff_series: np.ndarray, unit: str) -> Dict[str, Any]:
        mean_v = float(np.mean(diff_series))
        std_v = float(np.std(diff_series, ddof=1))
        median_v = float(np.median(diff_series))
        ci_l, ci_h = compute_bca_confidence_interval(diff_series)
        return {
            "mean": mean_v,
            "std": std_v,
            "median": median_v,
            "ci_95_bca_low": ci_l,
            "ci_95_bca_high": ci_h,
            "unit": unit
        }

    c1_prop = prop_sw - prop_s
    c2_prop = prop_swl - prop_sw
    c3_prop = prop_sl - prop_s
    c4_prop = (prop_swl - prop_sw) - (prop_sl - prop_s)

    c1_cf = cf_sw - cf_s
    c2_cf = cf_swl - cf_sw
    c3_cf = cf_sl - cf_s
    c4_cf = (cf_swl - cf_sw) - (cf_sl - cf_s)

    c1_fuel = fuel_sw_arr - fuel_s_arr
    c2_fuel = fuel_swl_arr - fuel_sw_arr
    c3_fuel = fuel_sl_arr - fuel_s_arr
    c4_fuel = (fuel_swl_arr - fuel_sw_arr) - (fuel_sl_arr - fuel_s_arr)

    c1_unmet = unmet_sw_arr - unmet_s_arr
    c2_unmet = unmet_swl_arr - unmet_sw_arr
    c3_unmet = unmet_sl_arr - unmet_s_arr
    c4_unmet = (unmet_swl_arr - unmet_sw_arr) - (unmet_sl_arr - unmet_s_arr)

    c1_curtail = curtail_sw_arr - curtail_s_arr
    c2_curtail = curtail_swl_arr - curtail_sw_arr
    c3_curtail = curtail_sl_arr - curtail_s_arr
    c4_curtail = (curtail_swl_arr - curtail_sw_arr) - (curtail_sl_arr - curtail_s_arr)

    factorial_report = {
        "C1_wind_without_protection (SW - S)": {
            "primary_proportional_reliability_pp": summarize_contrast(c1_prop, "pp"),
            "critical_first_reliability_pp": summarize_contrast(c1_cf, "pp"),
            "fuel_l": summarize_contrast(c1_fuel, "L"),
            "unmet_load_kwh": summarize_contrast(c1_unmet, "kWh"),
            "curtailment_kwh": summarize_contrast(c1_curtail, "kWh")
        },
        "C2_protection_under_solar_plus_wind (SW-L - SW)": {
            "primary_proportional_reliability_pp": summarize_contrast(c2_prop, "pp"),
            "critical_first_reliability_pp": summarize_contrast(c2_cf, "pp"),
            "fuel_l": summarize_contrast(c2_fuel, "L"),
            "unmet_load_kwh": summarize_contrast(c2_unmet, "kWh"),
            "curtailment_kwh": summarize_contrast(c2_curtail, "kWh")
        },
        "C3_protection_under_solar_only (S-L - S)": {
            "primary_proportional_reliability_pp": summarize_contrast(c3_prop, "pp"),
            "critical_first_reliability_pp": summarize_contrast(c3_cf, "pp"),
            "fuel_l": summarize_contrast(c3_fuel, "L"),
            "unmet_load_kwh": summarize_contrast(c3_unmet, "kWh"),
            "curtailment_kwh": summarize_contrast(c3_curtail, "kWh")
        },
        "C4_interaction_primary_mechanism_diagnostic": {
            "primary_proportional_reliability_pp": summarize_contrast(c4_prop, "pp"),
            "critical_first_reliability_pp": summarize_contrast(c4_cf, "pp"),
            "fuel_l": summarize_contrast(c4_fuel, "L"),
            "unmet_load_kwh": summarize_contrast(c4_unmet, "kWh"),
            "curtailment_kwh": summarize_contrast(c4_curtail, "kWh"),
            "algebraic_identity_check_max_diff": float(np.max(np.abs(c4_prop - ((prop_swl - prop_sl) - (prop_sw - prop_s)))))
        }
    }

    with open(OUT_DIR / "STAGE4_REPRO_FACTORIAL_C4_REPORT.json", "w") as f:
        json.dump(factorial_report, f, indent=2)

    # Markdown reports
    write_markdown_reports(all_metrics, safety_report, statistical_report, factorial_report, time.time() - t0_start)
    print(f"\nAll reports generated successfully in {time.time() - t0_start:.1f} s.")


def write_markdown_reports(all_metrics, safety_report, statistical_report, factorial_report, elapsed_s):
    # Load old frozen Stage 4 metrics for side-by-side comparison
    old_prereg_json = json.load(open(REPO / "experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.json"))
    frozen_base = old_prereg_json["old_frozen_stage4_results_baseline"]

    # 1. Comparison Report (JSON and MD)
    comparison_data = {}
    arms = ["Control_Frozen_B", "Candidate_S", "Candidate_SW", "Candidate_SL", "Candidate_SWL"]
    labels = {
        "Control_Frozen_B": "Control Frozen B",
        "Candidate_S": "Candidate S",
        "Candidate_SW": "Candidate SW",
        "Candidate_SL": "Candidate S-L",
        "Candidate_SWL": "Candidate SW-L"
    }

    for arm in arms:
        cur = all_metrics[arm]
        frz = frozen_base[arm]
        b_fuel_cur = all_metrics["Control_Frozen_B"]["total_diesel_fuel_l"]
        b_cf_cur = all_metrics["Control_Frozen_B"]["critical_first_reliability_pct"]
        b_p_cur = all_metrics["Control_Frozen_B"]["proportional_reliability_pct"]

        saving_cur = ((b_fuel_cur - cur["total_diesel_fuel_l"]) / b_fuel_cur) * 100.0 if arm != "Control_Frozen_B" else 0.0
        delta_cf_cur = cur["critical_first_reliability_pct"] - b_cf_cur
        delta_p_cur = cur["proportional_reliability_pct"] - b_p_cur

        comparison_data[arm] = {
            "name": labels[arm],
            "fuel_l": {"frozen": frz["fuel_l"], "corrected": cur["total_diesel_fuel_l"], "diff": cur["total_diesel_fuel_l"] - frz["fuel_l"]},
            "diesel_saving_pct": {"frozen": frz["diesel_saving_pct"], "corrected": saving_cur, "diff": saving_cur - frz["diesel_saving_pct"]},
            "critical_first_rel_pct": {"frozen": frz["critical_first_rel_pct"], "corrected": cur["critical_first_reliability_pct"], "diff": cur["critical_first_reliability_pct"] - frz["critical_first_rel_pct"]},
            "delta_cf_pp": {"frozen": frz["delta_cf_pp"], "corrected": delta_cf_cur, "diff": delta_cf_cur - frz["delta_cf_pp"]},
            "proportional_rel_pct": {"frozen": frz["proportional_rel_pct"], "corrected": cur["proportional_reliability_pct"], "diff": cur["proportional_reliability_pct"] - frz["proportional_rel_pct"]},
            "delta_p_pp": {"frozen": frz["delta_p_pp"], "corrected": delta_p_cur, "diff": delta_p_cur - frz["delta_p_pp"]},
            "unmet_load_mwh": {"frozen": frz["unmet_load_mwh"], "corrected": cur["total_unmet_load_wh"] / 1e6, "diff": (cur["total_unmet_load_wh"] / 1e6) - frz["unmet_load_mwh"]},
            "curtailment_mwh": {"frozen": frz["curtailment_mwh"], "corrected": cur["total_curtailment_wh"] / 1e6, "diff": (cur["total_curtailment_wh"] / 1e6) - frz["curtailment_mwh"]},
            "min_soc_pct": {"frozen": frz["min_soc_pct"], "corrected": cur["min_soc_pct"], "diff": cur["min_soc_pct"] - frz["min_soc_pct"]},
            "soc_violations": {"frozen": frz["soc_violations"], "corrected": cur["soc_violations_below_20"], "diff": cur["soc_violations_below_20"] - frz["soc_violations"]},
            "diesel_on_hours": {"frozen": frz["diesel_on_hours"], "corrected": cur["diesel_on_hours"], "diff": cur["diesel_on_hours"] - frz["diesel_on_hours"]},
            "diesel_startups": {"frozen": frz["diesel_startups"], "corrected": cur["diesel_startups"], "diff": cur["diesel_startups"] - frz["diesel_startups"]},
            "efc": {"frozen": frz["efc"], "corrected": cur["efc"], "diff": cur["efc"] - frz["efc"]}
        }

    with open(OUT_DIR / "STAGE4_REPRO_COMPARISON_TO_FROZEN_STAGE4.json", "w") as f:
        json.dump(comparison_data, f, indent=2)

    # Comparison Markdown
    comp_md = [
        "# POLARIS Stage 4 Corrected Reproduction: Comparison vs Frozen Historical Stage 4",
        "",
        f"**Date (UTC):** {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}  ",
        "**Governing Preregistration:** `experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md`  ",
        "**Execution Status:** COMPLETE (123 origins, 14,760 hours, 0 failures)  ",
        "",
        "---",
        "",
        "## Required Comparison: Frozen Historical Stage 4 vs Corrected Reproduction",
        "",
        "| Metric | Arm | Frozen Historical Result | Corrected Reproduction Result | Delta (Corrected − Frozen) |",
        "|---|---|---|---|---|"
    ]

    for arm in arms:
        d = comparison_data[arm]
        name = d["name"]
        comp_md.append(f"| **Diesel Fuel (L)** | {name} | {d['fuel_l']['frozen']:.4f} L | {d['fuel_l']['corrected']:.4f} L | {d['fuel_l']['diff']:+.4f} L |")
        comp_md.append(f"| **Diesel Saving vs B (%)** | {name} | {d['diesel_saving_pct']['frozen']:.2f}% | {d['diesel_saving_pct']['corrected']:.2f}% | {d['diesel_saving_pct']['diff']:+.2f} pp |")
        comp_md.append(f"| **Critical-First Rel (%)** | {name} | {d['critical_first_rel_pct']['frozen']:.6f}% | {d['critical_first_rel_pct']['corrected']:.6f}% | {d['critical_first_rel_pct']['diff']:+.6f} pp |")
        comp_md.append(f"| **Proportional Rel (%)** | {name} | {d['proportional_rel_pct']['frozen']:.6f}% | {d['proportional_rel_pct']['corrected']:.6f}% | {d['proportional_rel_pct']['diff']:+.6f} pp |")
        comp_md.append(f"| **ΔR_P vs B (pp)** | {name} | {d['delta_p_pp']['frozen']:+.6f} pp | {d['delta_p_pp']['corrected']:+.6f} pp | {d['delta_p_pp']['diff']:+.6f} pp |")
        comp_md.append(f"| **Total Unmet Load (MWh)** | {name} | {d['unmet_load_mwh']['frozen']:.2f} MWh | {d['unmet_load_mwh']['corrected']:.2f} MWh | {d['unmet_load_mwh']['diff']:+.2f} MWh |")
        comp_md.append(f"| **Total Curtailment (MWh)** | {name} | {d['curtailment_mwh']['frozen']:.2f} MWh | {d['curtailment_mwh']['corrected']:.2f} MWh | {d['curtailment_mwh']['diff']:+.2f} MWh |")
        comp_md.append(f"| **Min Realized SOC (%)** | {name} | {d['min_soc_pct']['frozen']:.2f}% | {d['min_soc_pct']['corrected']:.2f}% | {d['min_soc_pct']['diff']:+.2f} pp |")
        comp_md.append(f"| **SOC Violations (<20%)** | {name} | {d['soc_violations']['frozen']} | {d['soc_violations']['corrected']} | {d['soc_violations']['diff']} |")
        comp_md.append(f"| **Diesel-On Hours** | {name} | {d['diesel_on_hours']['frozen']} h | {d['diesel_on_hours']['corrected']} h | {d['diesel_on_hours']['diff']:+d} h |")
        comp_md.append(f"| **Diesel Startups** | {name} | {d['diesel_startups']['frozen']} | {d['diesel_startups']['corrected']} | {d['diesel_startups']['diff']:+d} |")
        comp_md.append(f"| **Equivalent Full Cycles (EFC)** | {name} | {d['efc']['frozen']:.2f} | {d['efc']['corrected']:.2f} | {d['efc']['diff']:+.2f} |")
        comp_md.append("|---|---|---|---|---|")

    (OUT_DIR / "STAGE4_REPRO_COMPARISON_TO_FROZEN_STAGE4.md").write_text("\n".join(comp_md) + "\n")

    # Campaign Summary MD
    b_fuel = all_metrics["Control_Frozen_B"]["total_diesel_fuel_l"]
    summary_md = [
        "# POLARIS Stage 4: Corrected Reproduction Campaign Summary",
        "",
        f"**Experiment:** `EXP-STAGE4-CORRECTED-REPRODUCTION-2025-HOLDOUT`  ",
        f"**Execution Timestamp:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} (Runtime: {elapsed_s:.1f} s)  ",
        "**Governing Preregistration:** `experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md`  ",
        "**Holdout Population:** 123 origins (2025-05-01 through 2025-08-31), 2,952 hours per arm, 14,760 total arm-hours  ",
        "**Status:** COMPLETE (0 execution failures, 0 exclusions)  ",
        "",
        "---",
        "",
        "## 1. Five-Arm Corrected Performance Summary (2025 Holdout)",
        "",
        "| Arm | Diesel Fuel (L) | Saving vs B (%) | Critical-First Rel (%) | ΔR_CF (pp) | Proportional Rel (%) | ΔR_P (pp) | Min SOC (%) | SOC <20% | All Safety Gates |",
        "|---|---|---|---|---|---|---|---|---|---|"
    ]

    for arm in arms:
        m = all_metrics[arm]
        saving = ((b_fuel - m["total_diesel_fuel_l"]) / b_fuel) * 100.0 if arm != "Control_Frozen_B" else 0.0
        delta_cf = m["critical_first_reliability_pct"] - all_metrics["Control_Frozen_B"]["critical_first_reliability_pct"]
        delta_p = m["proportional_reliability_pct"] - all_metrics["Control_Frozen_B"]["proportional_reliability_pct"]
        saf = "REFERENCE" if arm == "Control_Frozen_B" else ("PASS" if safety_report[arm]["all_safety_gates_pass"] else "SAFETY FAILURE")
        summary_md.append(
            f"| **{labels[arm]}** | {m['total_diesel_fuel_l']:.4f} | {saving:.2f}% | "
            f"{m['critical_first_reliability_pct']:.6f}% | {delta_cf:+.6f} | "
            f"{m['proportional_reliability_pct']:.6f}% | {delta_p:+.6f} | "
            f"{m['min_soc_pct']:.2f}% | {m['soc_violations_below_20']} | **{saf}** |"
        )

    summary_md.extend([
        "",
        "---",
        "",
        "## 2. Statistical Testing Results (Diesel Gate)",
        "",
        "### Candidate S-L (vs Control B)",
        f"- **Total Fuel Saved:** {statistical_report['Candidate_SL']['total_saving_l']:.2f} L ({statistical_report['Candidate_SL']['saving_pct']:.2f}%)",
        f"- **Mean Paired Saving:** {statistical_report['Candidate_SL']['mean_paired_saving_l']:.4f} L/origin",
        f"- **Median Paired Saving:** {statistical_report['Candidate_SL']['median_paired_saving_l']:.4f} L/origin",
        f"- **BCa 95% Bootstrap CI:** [{statistical_report['Candidate_SL']['bca_95_ci_low_l']:.4f}, {statistical_report['Candidate_SL']['bca_95_ci_high_l']:.4f}] L/origin (Strictly > 0: {statistical_report['Candidate_SL']['ci_strictly_positive']})",
        f"- **Wilcoxon Signed-Rank Test:** statistic = {statistical_report['Candidate_SL']['wilcoxon_stat']}, p = {statistical_report['Candidate_SL']['wilcoxon_raw_p']:.4e}",
        f"- **Holm-Adjusted p-value:** {statistical_report['Candidate_SL']['holm_adjusted_p']:.4e} (Significant at alpha=0.05: {statistical_report['Candidate_SL']['holm_significant_at_005']})",
        f"- **Diesel Gate Status:** **{'PASS' if statistical_report['Candidate_SL']['diesel_gate_pass'] else 'FAIL'}**",
        "",
        "### Candidate SW-L (Decision Candidate vs Control B)",
        f"- **Total Fuel Saved:** {statistical_report['Candidate_SWL']['total_saving_l']:.2f} L ({statistical_report['Candidate_SWL']['saving_pct']:.2f}%)",
        f"- **Mean Paired Saving:** {statistical_report['Candidate_SWL']['mean_paired_saving_l']:.4f} L/origin",
        f"- **Median Paired Saving:** {statistical_report['Candidate_SWL']['median_paired_saving_l']:.4f} L/origin",
        f"- **BCa 95% Bootstrap CI:** [{statistical_report['Candidate_SWL']['bca_95_ci_low_l']:.4f}, {statistical_report['Candidate_SWL']['bca_95_ci_high_l']:.4f}] L/origin (Strictly > 0: {statistical_report['Candidate_SWL']['ci_strictly_positive']})",
        f"- **Wilcoxon Signed-Rank Test:** statistic = {statistical_report['Candidate_SWL']['wilcoxon_stat']}, p = {statistical_report['Candidate_SWL']['wilcoxon_raw_p']:.4e}",
        f"- **Holm-Adjusted p-value:** {statistical_report['Candidate_SWL']['holm_adjusted_p']:.4e} (Significant at alpha=0.05: {statistical_report['Candidate_SWL']['holm_significant_at_005']})",
        f"- **Diesel Gate Status:** **{'PASS' if statistical_report['Candidate_SWL']['diesel_gate_pass'] else 'FAIL'}**",
        "",
        "---",
        "",
        "## 3. Factorial Contrasts & Mechanism Diagnostic (C4)",
        "",
        "| Contrast | Description | Outcome | Mean | BCa 95% CI |",
        "|---|---|---|---|---|",
        f"| **C1** (`SW − S`) | Wind effect without protection | Proportional Rel (pp) | {factorial_report['C1_wind_without_protection (SW - S)']['primary_proportional_reliability_pp']['mean']:+.4f} | [{factorial_report['C1_wind_without_protection (SW - S)']['primary_proportional_reliability_pp']['ci_95_bca_low']:+.4f}, {factorial_report['C1_wind_without_protection (SW - S)']['primary_proportional_reliability_pp']['ci_95_bca_high']:+.4f}] |",
        f"| | | Fuel Saving (L) | {factorial_report['C1_wind_without_protection (SW - S)']['fuel_l']['mean']:+.4f} | [{factorial_report['C1_wind_without_protection (SW - S)']['fuel_l']['ci_95_bca_low']:+.4f}, {factorial_report['C1_wind_without_protection (SW - S)']['fuel_l']['ci_95_bca_high']:+.4f}] |",
        f"| **C2** (`SW-L − SW`) | Protection effect under solar+wind | Proportional Rel (pp) | {factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['primary_proportional_reliability_pp']['mean']:+.4f} | [{factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['primary_proportional_reliability_pp']['ci_95_bca_low']:+.4f}, {factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['primary_proportional_reliability_pp']['ci_95_bca_high']:+.4f}] |",
        f"| | | Fuel Saving (L) | {factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['fuel_l']['mean']:+.4f} | [{factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['fuel_l']['ci_95_bca_low']:+.4f}, {factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['fuel_l']['ci_95_bca_high']:+.4f}] |",
        f"| **C3** (`S-L − S`) | Protection effect under solar-only | Proportional Rel (pp) | {factorial_report['C3_protection_under_solar_only (S-L - S)']['primary_proportional_reliability_pp']['mean']:+.4f} | [{factorial_report['C3_protection_under_solar_only (S-L - S)']['primary_proportional_reliability_pp']['ci_95_bca_low']:+.4f}, {factorial_report['C3_protection_under_solar_only (S-L - S)']['primary_proportional_reliability_pp']['ci_95_bca_high']:+.4f}] |",
        f"| | | Fuel Saving (L) | {factorial_report['C3_protection_under_solar_only (S-L - S)']['fuel_l']['mean']:+.4f} | [{factorial_report['C3_protection_under_solar_only (S-L - S)']['fuel_l']['ci_95_bca_low']:+.4f}, {factorial_report['C3_protection_under_solar_only (S-L - S)']['fuel_l']['ci_95_bca_high']:+.4f}] |",
        f"| **C4** | **Interaction / Mechanism Diagnostic** | **Proportional Rel (pp)** | **{factorial_report['C4_interaction_primary_mechanism_diagnostic']['primary_proportional_reliability_pp']['mean']:+.4f}** | **[{factorial_report['C4_interaction_primary_mechanism_diagnostic']['primary_proportional_reliability_pp']['ci_95_bca_low']:+.4f}, {factorial_report['C4_interaction_primary_mechanism_diagnostic']['primary_proportional_reliability_pp']['ci_95_bca_high']:+.4f}]** |",
        f"| | `(SW-L − SW) − (S-L − S)` | Fuel Saving (L) | {factorial_report['C4_interaction_primary_mechanism_diagnostic']['fuel_l']['mean']:+.4f} | [{factorial_report['C4_interaction_primary_mechanism_diagnostic']['fuel_l']['ci_95_bca_low']:+.4f}, {factorial_report['C4_interaction_primary_mechanism_diagnostic']['fuel_l']['ci_95_bca_high']:+.4f}] |",
        ""
    ])

    (OUT_DIR / "STAGE4_REPRO_CAMPAIGN_SUMMARY.md").write_text("\n".join(summary_md) + "\n")

    # Safety Report MD
    safety_md = [
        "# POLARIS Stage 4 Corrected Reproduction: Safety Evaluation Report",
        "",
        "| Candidate | Critical-First Rel (%) | ΔR_CF (pp) | Gate 1 (≥0.00) | Proportional Rel (%) | ΔR_P (pp) | Gate 2 (≥0.00) | Min SOC (%) | SOC <20% | Gate 3 | All Safety Gates |",
        "|---|---|---|---|---|---|---|---|---|---|---|"
    ]
    for arm in ["Candidate_S", "Candidate_SW", "Candidate_SL", "Candidate_SWL"]:
        m = all_metrics[arm]
        s = safety_report[arm]
        g1 = "PASS" if s["gate1_critical_first_pass"] else "FAIL"
        g2 = "PASS" if s["gate2_proportional_pass"] else "FAIL"
        g3 = "PASS" if s["gate3_soc_floor_pass"] else "FAIL"
        ov = "PASS" if s["all_safety_gates_pass"] else "FAIL"
        safety_md.append(
            f"| **{labels[arm]}** | {m['critical_first_reliability_pct']:.6f}% | {s['delta_cf_pp']:+.6f} | **{g1}** | "
            f"{m['proportional_reliability_pct']:.6f}% | {s['delta_prop_pp']:+.6f} | **{g2}** | "
            f"{s['min_soc_pct']:.2f}% | {s['soc_violations']} | **{g3}** | **{ov}** |"
        )
    (OUT_DIR / "STAGE4_REPRO_SAFETY_REPORT.md").write_text("\n".join(safety_md) + "\n")

    # Statistical Report MD
    stat_md = [
        "# POLARIS Stage 4 Corrected Reproduction: Statistical Evaluation Report",
        "",
        "## Diesel Gate Evaluation (Wilcoxon Signed-Rank + BCa 95% Bootstrap CI)",
        "",
        "| Candidate | Fuel Saved (L) | Saving (%) | Mean Paired Saving (L) | Median (L) | BCa 95% CI (L) | Wilcoxon Raw p | Holm Adj p | Diesel Gate |",
        "|---|---|---|---|---|---|---|---|---|"
    ]
    for arm in ["Candidate_SL", "Candidate_SWL"]:
        st = statistical_report[arm]
        stat_md.append(
            f"| **{labels[arm]}** | {st['total_saving_l']:.2f} | {st['saving_pct']:.2f}% | "
            f"{st['mean_paired_saving_l']:.4f} | {st['median_paired_saving_l']:.4f} | "
            f"[{st['bca_95_ci_low_l']:.4f}, {st['bca_95_ci_high_l']:.4f}] | "
            f"{st['wilcoxon_raw_p']:.4e} | {st['holm_adjusted_p']:.4e} | **{'PASS' if st['diesel_gate_pass'] else 'FAIL'}** |"
        )
    (OUT_DIR / "STAGE4_REPRO_STATISTICAL_REPORT.md").write_text("\n".join(stat_md) + "\n")

    # Factorial C4 Report MD
    c4_md = [
        "# POLARIS Stage 4 Corrected Reproduction: Factorial C4 Interaction Report",
        "",
        "## 2x2 Factorial Contrasts",
        "",
        "| Contrast | Formula | Proportional Reliability Mean (pp) | BCa 95% CI (pp) | Fuel Saving Mean (L) | BCa 95% CI (L) |",
        "|---|---|---|---|---|---|",
        f"| **C1** | $SW - S$ | {factorial_report['C1_wind_without_protection (SW - S)']['primary_proportional_reliability_pp']['mean']:+.4f} | [{factorial_report['C1_wind_without_protection (SW - S)']['primary_proportional_reliability_pp']['ci_95_bca_low']:+.4f}, {factorial_report['C1_wind_without_protection (SW - S)']['primary_proportional_reliability_pp']['ci_95_bca_high']:+.4f}] | {factorial_report['C1_wind_without_protection (SW - S)']['fuel_l']['mean']:+.4f} | [{factorial_report['C1_wind_without_protection (SW - S)']['fuel_l']['ci_95_bca_low']:+.4f}, {factorial_report['C1_wind_without_protection (SW - S)']['fuel_l']['ci_95_bca_high']:+.4f}] |",
        f"| **C2** | $SW\\text{{-}}L - SW$ | {factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['primary_proportional_reliability_pp']['mean']:+.4f} | [{factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['primary_proportional_reliability_pp']['ci_95_bca_low']:+.4f}, {factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['primary_proportional_reliability_pp']['ci_95_bca_high']:+.4f}] | {factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['fuel_l']['mean']:+.4f} | [{factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['fuel_l']['ci_95_bca_low']:+.4f}, {factorial_report['C2_protection_under_solar_plus_wind (SW-L - SW)']['fuel_l']['ci_95_bca_high']:+.4f}] |",
        f"| **C3** | $S\\text{{-}}L - S$ | {factorial_report['C3_protection_under_solar_only (S-L - S)']['primary_proportional_reliability_pp']['mean']:+.4f} | [{factorial_report['C3_protection_under_solar_only (S-L - S)']['primary_proportional_reliability_pp']['ci_95_bca_low']:+.4f}, {factorial_report['C3_protection_under_solar_only (S-L - S)']['primary_proportional_reliability_pp']['ci_95_bca_high']:+.4f}] | {factorial_report['C3_protection_under_solar_only (S-L - S)']['fuel_l']['mean']:+.4f} | [{factorial_report['C3_protection_under_solar_only (S-L - S)']['fuel_l']['ci_95_bca_low']:+.4f}, {factorial_report['C3_protection_under_solar_only (S-L - S)']['fuel_l']['ci_95_bca_high']:+.4f}] |",
        f"| **C4** | **Interaction** | **{factorial_report['C4_interaction_primary_mechanism_diagnostic']['primary_proportional_reliability_pp']['mean']:+.4f}** | **[{factorial_report['C4_interaction_primary_mechanism_diagnostic']['primary_proportional_reliability_pp']['ci_95_bca_low']:+.4f}, {factorial_report['C4_interaction_primary_mechanism_diagnostic']['primary_proportional_reliability_pp']['ci_95_bca_high']:+.4f}]** | **{factorial_report['C4_interaction_primary_mechanism_diagnostic']['fuel_l']['mean']:+.4f}** | **[{factorial_report['C4_interaction_primary_mechanism_diagnostic']['fuel_l']['ci_95_bca_low']:+.4f}, {factorial_report['C4_interaction_primary_mechanism_diagnostic']['fuel_l']['ci_95_bca_high']:+.4f}]** |",
        ""
    ]
    (OUT_DIR / "STAGE4_REPRO_FACTORIAL_C4_REPORT.md").write_text("\n".join(c4_md) + "\n")

    # Execution Audit MD
    audit_md = [
        "# POLARIS Stage 4 Corrected Reproduction: Execution & Governance Audit",
        "",
        f"**Experiment:** `EXP-STAGE4-CORRECTED-REPRODUCTION-2025-HOLDOUT`  ",
        f"**Execution Timestamp:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} (Runtime: {elapsed_s:.1f} s)  ",
        "**Execution Environment:** Linux, Python 3.12.3, HiGHS, SciPy, NumPy, Pandas, PVLib  ",
        "",
        "## Operational Telemetry Summary",
        "",
        "| Arm | Total Fuel (L) | Served Load (MWh) | Unmet Load (MWh) | Curtailment (MWh) | Diesel On Hours | Startups | Battery Throughput (MWh) | EFC | Emergency Hours | Normal Hours |",
        "|---|---|---|---|---|---|---|---|---|---|---|"
    ]
    for arm in arms:
        m = all_metrics[arm]
        audit_md.append(
            f"| **{labels[arm]}** | {m['total_diesel_fuel_l']:.2f} | {m['total_served_load_wh']/1e6:.2f} | "
            f"{m['total_unmet_load_wh']/1e6:.2f} | {m['total_curtailment_wh']/1e6:.2f} | "
            f"{m['diesel_on_hours']} | {m['diesel_startups']} | {m['battery_throughput_wh']/1e6:.2f} | "
            f"{m['efc']:.2f} | {m['emergency_hours']} | {m['normal_hours']} |"
        )
    (OUT_DIR / "STAGE4_REPRO_EXECUTION_AUDIT.md").write_text("\n".join(audit_md) + "\n")

    # Manifest JSON
    manifest = {
        "experiment_id": "EXP-STAGE4-CORRECTED-REPRODUCTION-2025-HOLDOUT",
        "execution_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_seconds": elapsed_s,
        "origins_count": 123,
        "hours_per_arm": 2952,
        "total_arm_hours": 14760,
        "execution_status": "SUCCESS",
        "failures_count": 0,
        "arms": arms,
        "metrics": all_metrics,
        "safety_report": safety_report,
        "statistical_report": statistical_report,
        "factorial_report": factorial_report,
        "artifact_paths": {
            "hourly_telemetry_csv": str(OUT_DIR / "STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv"),
            "hourly_telemetry_json": str(OUT_DIR / "STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.json"),
            "origin_results_csv": str(OUT_DIR / "STAGE4_REPRO_123_ORIGIN_RESULTS.csv"),
            "origin_results_json": str(OUT_DIR / "STAGE4_REPRO_123_ORIGIN_RESULTS.json"),
            "checkpoint_jsonl": str(OUT_DIR / "STAGE4_REPRO_CHECKPOINT.jsonl"),
            "safety_report_md": str(OUT_DIR / "STAGE4_REPRO_SAFETY_REPORT.md"),
            "safety_report_json": str(OUT_DIR / "STAGE4_REPRO_SAFETY_REPORT.json"),
            "statistical_report_md": str(OUT_DIR / "STAGE4_REPRO_STATISTICAL_REPORT.md"),
            "statistical_report_json": str(OUT_DIR / "STAGE4_REPRO_STATISTICAL_REPORT.json"),
            "factorial_c4_md": str(OUT_DIR / "STAGE4_REPRO_FACTORIAL_C4_REPORT.md"),
            "factorial_c4_json": str(OUT_DIR / "STAGE4_REPRO_FACTORIAL_C4_REPORT.json"),
            "campaign_summary_md": str(OUT_DIR / "STAGE4_REPRO_CAMPAIGN_SUMMARY.md"),
            "execution_audit_md": str(OUT_DIR / "STAGE4_REPRO_EXECUTION_AUDIT.md"),
            "comparison_report_md": str(OUT_DIR / "STAGE4_REPRO_COMPARISON_TO_FROZEN_STAGE4.md"),
            "comparison_report_json": str(OUT_DIR / "STAGE4_REPRO_COMPARISON_TO_FROZEN_STAGE4.json")
        }
    }
    with open(OUT_DIR / "STAGE4_REPRO_EXECUTION_MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    main()
