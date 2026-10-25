#!/usr/bin/env python3
"""
MILP-v2 DIAGNOSTIC BRANCH -- full-window counterfactual causal isolation.

Does NOT modify production code, optimizer behavior, R1/R2, assumptions, or models. Calls
the REAL, UNMODIFIED GAP19HighsNativeOptimizer.optimize() with identical initial states and
configs to R1/R2; the ONLY thing varied across conditions is which VALUE is passed into the
existing `config["terminal_target_wh"]` input slot and which forecast bundle's
solar/demand/wind feed the solve -- no new code path, no new objective term, no weighting
change.

Three conditions, all using the real optimizer:

  REAL-BASELINE   = baseline solar/demand/wind + terminal computed FROM baseline's own solar
                    (this is just R2's baseline arm -- loaded from R2's own frozen raw
                    results, NOT re-solved, to keep R1/R2 strictly as frozen references
                    rather than re-deriving them)
  REAL-STAGE81    = stage8.1 solar + baseline demand/wind + terminal computed FROM stage8.1's
                    own solar (R2's stage8.1 arm -- also loaded from frozen R2 results)
  CF-B STAGE81_FIXED_TERM = stage8.1 solar + baseline demand/wind (identical physical inputs
                    to REAL-STAGE81) BUT terminal_target_wh held FIXED at whatever value
                    REAL-BASELINE's own solar would have produced for that same origin
                    (i.e., the reserve target does not react to the stage8.1 forecast at all)
                    -- this is the ONE new, actually re-solved condition in this script.

Isolation logic (differencing, not re-weighting):
  Mechanism-1 (pure solar/energy-balance effect, terminal held fixed)
      = CF-B_STAGE81_FIXED_TERM − REAL-BASELINE         (solar differs, terminal does NOT)
  Mechanism-2 (terminal-target reactivity effect, solar held fixed)
      = REAL-STAGE81 − CF-B_STAGE81_FIXED_TERM          (terminal differs, solar does NOT)
  Combined (R2's actual, already-reported effect)
      = REAL-STAGE81 − REAL-BASELINE
  Interaction/residual = Combined − (Mechanism-1 + Mechanism-2)  [reported, not assumed zero]

A null/determinism control (re-solving REAL-BASELINE's own inputs a second, independent
time, on a small sample) is also run, to verify "same forecast in both arms gives exactly
zero delta" (item 1 of the requested counterfactuals) before trusting the main isolation.
"""
import sys
import json
import time
from pathlib import Path

import pandas as pd
import yaml

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
THIS_DIR = Path(__file__).parent
R1R2_DIR = BASE / "ems/gap19/POLARIS_EMS_GAP19_STAGE81_VS_BASELINE_RESEARCH_SIMULATION"
sys.path.insert(0, str(R1R2_DIR))

from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.forecasting.implementations.s81_corrected_solar import (
    Stage81CorrectedForecastEngine, CANDIDATE_37_FEATURES, FROZEN_MODEL_SHA256, FROZEN_MODEL_PATH,
)
from run_research_simulation import compute_terminal_target_wh  # frozen formula, imported not copied

MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
PV_CONFIG_PATH = BASE / "system" / "config" / "solar_pv.yaml"
R2_RAW_RESULTS = R1R2_DIR / "R2_FULL_EXPERIMENT_RAW_RESULTS.json"
CHECKPOINT_EVERY = 50
NULL_CHECK_ORIGINS = 5


def sha256_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def plan_metrics(plan, terminal_target_wh, route, solve_time_s):
    return {
        "route": route,
        "constraint_status": plan.constraint_status,
        "solve_time_s": round(solve_time_s, 4),
        "terminal_target_wh": round(terminal_target_wh, 2),
        "planned_diesel_fuel_l": None,  # filled by caller using diesel.yaml formula
        "diesel_power_sum_w": round(sum(plan.diesel_power), 2),
        "planned_curtailment_wh": round(sum(plan.renewable_curtailment), 2),
        "planned_unmet_load_wh": round(sum(plan.unmet_load), 2),
        "planned_battery_charge_wh": round(sum(plan.battery_charge), 2),
        "planned_battery_discharge_wh": round(sum(plan.battery_discharge), 2),
        "soc_min_pct": round(min(plan.battery_soc), 3),
        "soc_max_pct": round(max(plan.battery_soc), 3),
        "j1_objective": plan.j1_objective, "j2_objective": plan.j2_objective,
        "j3_objective": plan.j3_objective, "j4_objective": plan.j4_objective,
        "reserve_shortfall_sum_wh": round(sum(plan.reserve_shortfall), 2) if plan.reserve_shortfall else 0.0,
    }


def main():
    print("=" * 80)
    print("MILP-v2 DIAGNOSTIC BRANCH -- full-window counterfactual causal isolation")
    print("R1/R2, optimizer, assumptions, models, config: all UNCHANGED.")
    print("=" * 80)

    matrix_hash = sha256_of(MATRIX_PATH)
    if matrix_hash != EXPECTED_MATRIX_HASH:
        raise RuntimeError(f"STOP: matrix hash mismatch")
    model_hash = sha256_of(FROZEN_MODEL_PATH)
    if model_hash != FROZEN_MODEL_SHA256:
        raise RuntimeError(f"STOP: model hash mismatch")
    if not R2_RAW_RESULTS.exists():
        raise RuntimeError("STOP: R2_FULL_EXPERIMENT_RAW_RESULTS.json not found -- R2 must "
                            "exist and remain frozen as the reference for REAL-BASELINE/REAL-STAGE81.")
    print("Hashes verified OK; R2 frozen reference found.\n")

    with open(R2_RAW_RESULTS) as f:
        r2_data = json.load(f)
    r2_by_origin = {}
    for r in r2_data["results"]:
        r2_by_origin.setdefault(r["origin"], {})[r["engine"]] = r

    df = pd.read_csv(MATRIX_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    origins = sorted(df["forecast_start"].unique())
    origins = [pd.Timestamp(o) for o in origins]

    configs_base = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        cfg_file = BASE / "system" / "config" / f"{cfg_name}.yaml"
        if cfg_file.exists():
            with open(cfg_file) as f:
                configs_base[cfg_name] = yaml.safe_load(f)

    diesel_cfg = configs_base.get("diesel", {})
    base_fuel_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marginal_fuel_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

    def fuel_liters(diesel_power_list):
        return sum((base_fuel_lph if p > 0 else 0.0) + marginal_fuel_lpwh * p for p in diesel_power_list)

    adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
    if adapter.total_records != 8784:
        raise RuntimeError("STOP: fixture record count changed")

    baseline_engine = LocalBaselineForecastEngine(PV_CONFIG_PATH)
    stage81_engine = Stage81CorrectedForecastEngine()
    router = EMSControlRouter()
    optimizer = GAP19HighsNativeOptimizer()
    option_d_solver = OptionDFallbackSolver()

    def build_state_and_bundles(origin, index):
        st_k_raw = adapter.get_station_state(index, battery_soc_pct=50.0)
        expected_ts = origin.strftime("%Y-%m-%dT%H:%M:%SZ")
        if st_k_raw.timestamp != expected_ts:
            raise RuntimeError(f"STOP: fixture mismatch at {origin}")
        st_k = StationState(
            timestamp=st_k_raw.timestamp, battery_soc_pct=80.0, battery_energy_wh=160000.0,
            diesel_running=True, diesel_hours_running=2.0,
            last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
            last_observed_demand=st_k_raw.last_observed_demand,
            last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
            diesel_fuel_remaining_liters=500.0,
        )
        bundle_baseline = baseline_engine.predict(st_k, {})
        origin_rows = df[df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
        feature_matrix = origin_rows[CANDIDATE_37_FEATURES].copy()
        bundle_stage81 = stage81_engine.predict(st_k, {"stage8_1_feature_matrix": feature_matrix})
        return st_k, bundle_baseline, bundle_stage81, expected_ts

    def solve_cf_b(st_k, bundle_stage81, terminal_fixed_value, critical_load_baseline_w):
        configs = dict(configs_base)
        configs["critical_demand_w"] = [min(critical_load_baseline_w, d) for d in bundle_stage81.demand.point]
        configs["terminal_target_wh"] = terminal_fixed_value  # HELD FIXED -- not recomputed from stage81 solar
        t0 = time.time()
        assessment, route = router.evaluate_and_route(st_k, bundle_stage81, configs)
        if route == "NORMAL":
            plan = optimizer.optimize(bundle_stage81, st_k, configs)
        elif route == "EMERGENCY":
            plan = option_d_solver.solve(assessment, bundle_stage81, st_k, configs)
        else:
            raise RuntimeError(f"STOP: unknown route '{route}'")
        solve_time = time.time() - t0
        return plan, route, solve_time

    # --- Null/determinism control (item 1: "same solar forecast in both arms") ---
    print("--- Null/determinism control: re-solving REAL-BASELINE's own inputs independently ---")
    null_mismatches = []
    for origin in origins[:NULL_CHECK_ORIGINS]:
        index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
        st_k, bundle_baseline, _bundle_stage81, ts = build_state_and_bundles(origin, index)
        critical_load_baseline_w = float(
            configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        terminal_b = compute_terminal_target_wh(bundle_baseline)
        configs = dict(configs_base)
        configs["critical_demand_w"] = [min(critical_load_baseline_w, d) for d in bundle_baseline.demand.point]
        configs["terminal_target_wh"] = terminal_b
        assessment, route = router.evaluate_and_route(st_k, bundle_baseline, configs)
        if route != "NORMAL":
            continue
        plan1 = optimizer.optimize(bundle_baseline, st_k, configs)
        plan2 = optimizer.optimize(bundle_baseline, st_k, configs)  # independent second solve, identical inputs
        identical = (plan1.to_dict() == plan2.to_dict())
        if not identical:
            null_mismatches.append(ts)
        print(f"  {ts}: identical={identical}")
    if null_mismatches:
        raise RuntimeError(f"STOP: null/determinism control FAILED at origins {null_mismatches}. "
                            "Same inputs must give identical output before trusting the isolation below.")
    print("Null/determinism control PASSED: identical inputs give bit-identical plans.\n")

    # --- Full-window CF-B run ---
    print(f"--- Full-window CF-B (stage8.1 solar, terminal held fixed at baseline's value) ---")
    print(f"Evaluation window: {len(origins)} daily origins\n")

    results = []
    t_start = time.time()
    try:
        for i, origin in enumerate(origins):
            index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
            st_k, bundle_baseline, bundle_stage81, ts = build_state_and_bundles(origin, index)
            critical_load_baseline_w = float(
                configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
            )
            terminal_baseline_value = compute_terminal_target_wh(bundle_baseline)

            plan, route, solve_time = solve_cf_b(st_k, bundle_stage81, terminal_baseline_value, critical_load_baseline_w)
            m = plan_metrics(plan, terminal_baseline_value, route, solve_time) if route == "NORMAL" else {
                "route": route, "constraint_status": getattr(plan, "constraint_status", "OPTION_D_FALLBACK"),
                "terminal_target_wh": round(terminal_baseline_value, 2),
            }
            if route == "NORMAL":
                m["planned_diesel_fuel_l"] = round(fuel_liters(plan.diesel_power), 4)
            m["origin"] = ts
            m["condition"] = "CF_B_STAGE81_SOLAR_TERMINAL_FIXED_AT_BASELINE"
            results.append(m)

            if (i + 1) % CHECKPOINT_EVERY == 0 or (i + 1) == len(origins):
                elapsed = time.time() - t_start
                print(f"Checkpoint: {i+1}/{len(origins)} origins done, elapsed={elapsed:.1f}s")
                with open(THIS_DIR / "COUNTERFACTUAL_CF_B_CHECKPOINT.json", "w") as f:
                    json.dump({"origins_done": i + 1, "origins_total": len(origins), "results": results}, f, indent=2)
    except Exception as exc:
        print(f"\nSTOP: unexpected failure after {len(results)} cycles: {exc}")
        with open(THIS_DIR / "COUNTERFACTUAL_CF_B_CHECKPOINT.json", "w") as f:
            json.dump({"halted": True, "error": str(exc), "results": results}, f, indent=2)
        raise

    out_path = THIS_DIR / "COUNTERFACTUAL_CF_B_RAW_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": "MILP-v2 DIAGNOSTIC BRANCH. Counterfactual CF-B: stage8.1 solar + "
                           "baseline demand/wind, terminal_target_wh HELD FIXED at the value "
                           "baseline's own solar would have produced. Real, unmodified "
                           "optimizer. R1/R2 untouched (loaded as frozen reference, not re-run).",
            "null_determinism_control": "PASSED",
            "origins_total": len(origins), "elapsed_s": round(time.time() - t_start, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nCF-B raw results written to {out_path}")
    print(f"Total elapsed: {round(time.time() - t_start, 1)}s")
    print("\nCOUNTERFACTUAL ISOLATION RUN COMPLETE. No optimizer behavior changed. R1/R2 untouched.")


if __name__ == "__main__":
    main()
