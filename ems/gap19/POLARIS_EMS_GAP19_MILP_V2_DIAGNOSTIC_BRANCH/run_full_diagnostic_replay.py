#!/usr/bin/env python3
"""
MILP-v2 DIAGNOSTIC BRANCH -- full 347-origin instrumentation pass.

Extends the validated small replay (run_small_diagnostic_replay.py) to all 347 R2 origins,
both arms (694 cycles). Uses the exact same R1/R2 frozen formula, config, and optimizer code
paths -- imported, not copied -- so nothing about R1/R2's assumptions, the optimizer, or any
model can drift. This is READ-ONLY instrumentation added on top of the real, unmodified
GAP19HighsNativeOptimizer.optimize() call; no objective weight, terminal formula, or
optimizer behavior is changed. No counterfactual re-solve is performed anywhere in this
script -- every cycle is solved exactly once, under the real, single, unmodified objective.

Per the diagnostic module's own documented limitation: the per-timestep "binding" vs
"non-binding" diesel split is a SAME-TIMESTEP ASSOCIATION, not a causal isolation. This
script does not infer causality beyond that association.
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
from system.simulation.simulator import DigitalTwinSimulator
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.forecasting.implementations.s81_corrected_solar import (
    Stage81CorrectedForecastEngine, CANDIDATE_37_FEATURES, FROZEN_MODEL_SHA256, FROZEN_MODEL_PATH,
)
from run_research_simulation import compute_terminal_target_wh  # frozen R1/R2 formula, imported not copied

from diagnostic_instrumentation import instrument_cycle

MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
PV_CONFIG_PATH = BASE / "system" / "config" / "solar_pv.yaml"
CHECKPOINT_EVERY = 50


def sha256_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_preconditions():
    matrix_hash = sha256_of(MATRIX_PATH)
    if matrix_hash != EXPECTED_MATRIX_HASH:
        raise RuntimeError(f"STOP: matrix hash mismatch ({matrix_hash} != {EXPECTED_MATRIX_HASH})")
    model_hash = sha256_of(FROZEN_MODEL_PATH)
    if model_hash != FROZEN_MODEL_SHA256:
        raise RuntimeError(f"STOP: model hash mismatch ({model_hash} != {FROZEN_MODEL_SHA256})")
    print("Matrix/model hashes verified OK (same as R1/R2).")


def run_one_instrumented_cycle(engine_label, engine, adapter, router, optimizer, option_d_solver,
                                configs_base, df, origin, index, eta_dis, dt):
    st_k_raw = adapter.get_station_state(index, battery_soc_pct=50.0)
    expected_ts = origin.strftime("%Y-%m-%dT%H:%M:%SZ")
    if st_k_raw.timestamp != expected_ts:
        raise RuntimeError(f"STOP: fixture index->timestamp mismatch: {st_k_raw.timestamp} vs {expected_ts}")

    st_k = StationState(
        timestamp=st_k_raw.timestamp, battery_soc_pct=80.0, battery_energy_wh=160000.0,
        diesel_running=True, diesel_hours_running=2.0,
        last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
        last_observed_demand=st_k_raw.last_observed_demand,
        last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
        diesel_fuel_remaining_liters=500.0,
    )

    if engine_label == "stage8_1_corrected":
        origin_rows = df[df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
        if len(origin_rows) != 24:
            raise RuntimeError(f"STOP: expected 24 feature rows for origin {origin}, got {len(origin_rows)}")
        feature_matrix = origin_rows[CANDIDATE_37_FEATURES].copy()
        bundle = engine.predict(st_k, {"stage8_1_feature_matrix": feature_matrix})
    else:
        bundle = engine.predict(st_k, {})

    configs = dict(configs_base)
    critical_load_baseline_w = float(
        configs.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
    )
    critical_demand = [min(critical_load_baseline_w, d) for d in bundle.demand.point]
    configs["critical_demand_w"] = critical_demand

    terminal_target_wh = compute_terminal_target_wh(bundle)
    configs["terminal_target_wh"] = terminal_target_wh

    assessment, route = router.evaluate_and_route(st_k, bundle, configs)
    if route == "NORMAL":
        plan = optimizer.optimize(bundle, st_k, configs)  # REAL, UNMODIFIED optimizer call
        diag = instrument_cycle(plan, critical_demand, terminal_target_wh, eta_dis, dt, 0.0)
        diag["route"] = route
        diag["origin"] = expected_ts
        diag["engine"] = engine_label
        return diag
    elif route == "EMERGENCY":
        plan = option_d_solver.solve(assessment, bundle, st_k, configs)
        return {
            "route": "EMERGENCY", "origin": expected_ts, "engine": engine_label,
            "note": "OptionD route -- terminal_target_wh/J2 envelope not read by this path.",
        }
    else:
        raise RuntimeError(f"STOP: unknown route '{route}'")


def main():
    print("=" * 80)
    print("MILP-v2 DIAGNOSTIC BRANCH -- FULL 347-origin instrumentation pass")
    print("R1/R2, optimizer, assumptions, models, config: all UNCHANGED.")
    print("No counterfactual re-solve. Same-timestep association only, not causal isolation.")
    print("=" * 80)

    verify_preconditions()

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

    adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
    if adapter.total_records != 8784:
        raise RuntimeError(f"STOP: fixture record count changed ({adapter.total_records} != 8784)")

    baseline_engine = LocalBaselineForecastEngine(PV_CONFIG_PATH)
    stage81_engine = Stage81CorrectedForecastEngine()
    router = EMSControlRouter()
    optimizer = GAP19HighsNativeOptimizer()
    option_d_solver = OptionDFallbackSolver()
    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    dt = 1.0

    print(f"Evaluation window (same as R1/R2): {len(origins)} daily origins, "
          f"{origins[0]} .. {origins[-1]}\n")

    results = []
    t_start = time.time()
    try:
        for i, origin in enumerate(origins):
            index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
            for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
                r = run_one_instrumented_cycle(engine_label, engine, adapter, router, optimizer,
                                                option_d_solver, configs_base, df, origin, index, eta_dis, dt)
                results.append(r)

            if (i + 1) % CHECKPOINT_EVERY == 0 or (i + 1) == len(origins):
                elapsed = time.time() - t_start
                print(f"Checkpoint: {i+1}/{len(origins)} origins done ({len(results)} cycles), "
                      f"elapsed={elapsed:.1f}s")
                with open(THIS_DIR / "FULL_DIAGNOSTIC_CHECKPOINT.json", "w") as f:
                    json.dump({
                        "disclaimer": "MILP-v2 DIAGNOSTIC BRANCH. In-progress checkpoint. Read-only instrumentation.",
                        "origins_done": i + 1, "origins_total": len(origins),
                        "cycles_done": len(results), "elapsed_s": round(elapsed, 1),
                        "results": results,
                    }, f, indent=2)
    except Exception as exc:
        print(f"\nSTOP: unexpected failure after {len(results)} cycles: {exc}")
        with open(THIS_DIR / "FULL_DIAGNOSTIC_CHECKPOINT.json", "w") as f:
            json.dump({
                "disclaimer": "MILP-v2 DIAGNOSTIC BRANCH. Run HALTED due to failure.",
                "halted": True, "error": str(exc), "cycles_done": len(results), "results": results,
            }, f, indent=2)
        raise

    out_path = THIS_DIR / "FULL_DIAGNOSTIC_RAW_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": "MILP-v2 DIAGNOSTIC BRANCH. Full 347-origin read-only instrumentation "
                           "pass over the REAL, UNMODIFIED GAP19 optimizer. R1/R2 untouched. No "
                           "counterfactual re-solve. Same-timestep association, not causal isolation.",
            "origins_total": len(origins), "cycles_total": len(results),
            "elapsed_s": round(time.time() - t_start, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nFull diagnostic raw results written to {out_path}")
    print(f"Total: {len(origins)} origins, {len(results)} cycles, "
          f"{round(time.time() - t_start, 1)}s elapsed.")
    print("\nFULL DIAGNOSTIC PASS COMPLETE. No optimizer behavior changed. R1/R2 untouched.")


if __name__ == "__main__":
    main()
