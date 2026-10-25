#!/usr/bin/env python3
"""
RESEARCH-ONLY SIMULATION. NOT a production run. NOT a governance-authorized experiment.

Full-window controlled closed-loop MILP comparison: baseline forecast engine vs. frozen
Stage 8.1 CORRECTED forecast engine, over every daily origin present in the frozen,
hash-verified Stage 8.1 feature matrix (the only "established evaluation window" that
exists as frozen evidence in this repository -- see FROZEN_RESEARCH_EXPERIMENT_MANIFEST.md
§3). Reuses the SAME frozen terminal-reserve formula/constants as
`run_research_simulation.py` (imported, not re-implemented) so assumptions cannot drift
between the smoke test and the full run.

Per the manifest, this script:
  1. Re-verifies every frozen hash (matrix, model, this script's own sibling script,
     config YAMLs) before doing anything else. Any mismatch -> hard STOP.
  2. Runs one final baseline-vs-Stage8.1 smoke test (single origin) before the full run.
     Any failure -> hard STOP, full run not launched.
  3. Runs the full window, writing periodic checkpoints and raw per-cycle results.
  4. Any unexpected exception during the full run -> hard STOP (checkpoint preserved,
     no silent continuation, no assumption change).

Does NOT modify production code/config, does NOT tune either arm on results (the formula
is imported, frozen, and identical for all 694 cycles), and does NOT claim operational
performance -- see RESEARCH_SIMULATION_RESULTS_R1.md for the labeled comparison.
"""
import sys
import hashlib
import json
import time
from pathlib import Path

import pandas as pd
import yaml

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
THIS_DIR = Path(__file__).parent

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

# Frozen formula/constants reused by import -- NOT re-implemented, cannot drift.
from run_research_simulation import (
    compute_terminal_target_wh, TERMINAL_FLOOR_WH, LOOKAHEAD_WINDOW_HOURS, UNCERTAINTY_MARGIN,
)

MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
PV_CONFIG_PATH = BASE / "system" / "config" / "solar_pv.yaml"

EXPECTED_SCRIPT_HASH = "d68b343d60f67a2fc8143316278371342d3933f70d0e26d40f3c1c732d843bd1"
EXPECTED_DECISION_RECORD_HASH = "d8356282ca1550c255bf5d3f9e35c7256d322513da9824c990c9f3d1cc9fc26b"
EXPECTED_CONFIG_HASHES = {
    "battery.yaml": "eb06f81d8b11364e254cbcd5c37a4769874f8703e9e86e3b067b60d8858da216",
    "diesel.yaml": "421120967328e18366daf41b682fc9f1cbe91b0f9ebe2133b83290bb9e294ac3",
    "loads.yaml": "eacb84d1c25f8768de0ee0cf8fdb286d4dbc9254824d7c17aea738cbe9774467",
    "solar_pv.yaml": "611521090b7d551614c23d91fc190320a42bccee667929618d40bab987262e5e",
    "station.yaml": "e021368133587b5752b9471722d7997d1cd2aa2d674697a47b1b2f5b06052e42",
    "optimizer.yaml": "bdf5a61487fddf0695b8926a24499be17fef0181d3f755731d154c1fabbca1e8",
}

CHECKPOINT_EVERY = 50


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_frozen_manifest():
    print("--- Verifying frozen manifest (R1) ---")
    checks = []

    matrix_hash = sha256_of(MATRIX_PATH)
    checks.append(("matrix", matrix_hash, EXPECTED_MATRIX_HASH))

    model_hash = sha256_of(FROZEN_MODEL_PATH)
    checks.append(("stage8_1_model", model_hash, FROZEN_MODEL_SHA256))

    script_hash = sha256_of(THIS_DIR / "run_research_simulation.py")
    checks.append(("run_research_simulation.py", script_hash, EXPECTED_SCRIPT_HASH))

    record_hash = sha256_of(THIS_DIR / "RESEARCH_EXCEPTION_DECISION_RECORD.md")
    checks.append(("RESEARCH_EXCEPTION_DECISION_RECORD.md", record_hash, EXPECTED_DECISION_RECORD_HASH))

    for fname, expected in EXPECTED_CONFIG_HASHES.items():
        actual = sha256_of(BASE / "system" / "config" / fname)
        checks.append((f"config/{fname}", actual, expected))

    all_ok = True
    for name, actual, expected in checks:
        ok = actual == expected
        all_ok = all_ok and ok
        print(f"  {name}: {'MATCH' if ok else 'MISMATCH'}")
        if not ok:
            print(f"    expected={expected}")
            print(f"    actual  ={actual}")

    if not all_ok:
        raise RuntimeError(
            "STOP: frozen manifest verification FAILED. One or more inputs changed since "
            "R1 was frozen. Per instruction, halting rather than silently proceeding or "
            "re-freezing. No full run was launched."
        )

    print("All frozen manifest hashes verified OK.\n")

    # Assumption-value self-check: the imported constants must match the manifest's text.
    expected_floor = 40000.0
    expected_margin = 0.10
    expected_lookahead = 6
    if not (abs(TERMINAL_FLOOR_WH - expected_floor) < 1e-6
            and abs(UNCERTAINTY_MARGIN - expected_margin) < 1e-9
            and LOOKAHEAD_WINDOW_HOURS == expected_lookahead):
        raise RuntimeError(
            f"STOP: imported assumption constants do not match the frozen manifest "
            f"(floor={TERMINAL_FLOOR_WH}, margin={UNCERTAINTY_MARGIN}, lookahead={LOOKAHEAD_WINDOW_HOURS}). "
            f"Halting -- assumptions must not silently drift from R1."
        )
    print("Imported frozen assumption constants match manifest R1 values.\n")


def build_components():
    df = pd.read_csv(MATRIX_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)

    configs_base = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        cfg_file = BASE / "system" / "config" / f"{cfg_name}.yaml"
        if cfg_file.exists():
            with open(cfg_file) as f:
                configs_base[cfg_name] = yaml.safe_load(f)

    adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
    if adapter.total_records != 8784:
        raise RuntimeError(f"STOP: fixture record count changed ({adapter.total_records} != 8784).")

    baseline_engine = LocalBaselineForecastEngine(PV_CONFIG_PATH)
    stage81_engine = Stage81CorrectedForecastEngine()
    router = EMSControlRouter()
    optimizer = GAP19HighsNativeOptimizer()
    option_d_solver = OptionDFallbackSolver()
    simulator = DigitalTwinSimulator(configs_base)

    diesel_cfg = configs_base.get("diesel", {})
    base_fuel_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marginal_fuel_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))
    battery_capacity_wh = float(configs_base.get("battery", {}).get("capacity_wh", 200000.0))

    return (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
            option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, battery_capacity_wh)


def run_one_cycle(engine_label, engine, adapter, router, optimizer, option_d_solver,
                   simulator, configs_base, matrix_df, origin, index,
                   base_fuel_lph, marginal_fuel_lpwh):
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

    next_actual = adapter.get_future_ground_truth(index, horizon_hours=24)[0]

    if engine_label == "stage8_1_corrected":
        origin_rows = matrix_df[matrix_df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
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
    configs["critical_demand_w"] = [min(critical_load_baseline_w, d) for d in bundle.demand.point]

    terminal_target_wh = compute_terminal_target_wh(bundle)
    configs["terminal_target_wh"] = terminal_target_wh

    t_solve0 = time.time()
    assessment, route = router.evaluate_and_route(st_k, bundle, configs)
    if route == "NORMAL":
        plan = optimizer.optimize(bundle, st_k, configs)
    elif route == "EMERGENCY":
        plan = option_d_solver.solve(assessment, bundle, st_k, configs)
    else:
        raise RuntimeError(f"STOP: unknown route '{route}' -- does not match frozen router contract.")
    solve_time_s = time.time() - t_solve0

    fuel_before = st_k.diesel_fuel_remaining_liters
    next_state = simulator.step(st_k, plan, next_actual)
    fuel_after = next_state.diesel_fuel_remaining_liters
    t0_fuel_consumed_l = round(fuel_before - fuel_after, 6)

    # Planned (NOT realized) full-24h-horizon aggregates, from the MILP's own plan.
    planned_diesel_energy_wh = sum(plan.diesel_power) * 1.0
    planned_diesel_fuel_l = sum(
        (base_fuel_lph if p > 0 else 0.0) + marginal_fuel_lpwh * p for p in plan.diesel_power
    )
    planned_unmet_load_wh = sum(plan.unmet_load) * 1.0
    planned_curtailment_wh = sum(plan.renewable_curtailment) * 1.0
    planned_battery_charge_wh = sum(plan.battery_charge) * 1.0
    planned_battery_discharge_wh = sum(plan.battery_discharge) * 1.0
    planned_soc_min = min(plan.battery_soc)
    planned_soc_max = max(plan.battery_soc)
    planned_reserve_shortfall_wh = sum(plan.reserve_shortfall) * 1.0 if plan.reserve_shortfall else 0.0

    return {
        "engine": engine_label,
        "origin": expected_ts,
        "route": route,
        "terminal_target_wh": round(terminal_target_wh, 2),
        "constraint_status": plan.constraint_status,
        "solve_time_s": round(solve_time_s, 4),
        # Realized (t0, actually executed) outcomes:
        "t0_battery_charge_w": round(plan.battery_charge[0], 2),
        "t0_battery_discharge_w": round(plan.battery_discharge[0], 2),
        "t0_diesel_power_w": round(plan.diesel_power[0], 2),
        "t0_fuel_consumed_l": t0_fuel_consumed_l,
        "next_battery_soc_pct": round(next_state.battery_soc_pct, 3),
        "next_battery_energy_wh": round(next_state.battery_energy_wh, 1),
        # Planned (NOT realized) full-24h-horizon aggregates:
        "planned_diesel_energy_wh": round(planned_diesel_energy_wh, 1),
        "planned_diesel_fuel_l": round(planned_diesel_fuel_l, 4),
        "planned_unmet_load_wh": round(planned_unmet_load_wh, 2),
        "planned_curtailment_wh": round(planned_curtailment_wh, 2),
        "planned_battery_charge_wh": round(planned_battery_charge_wh, 1),
        "planned_battery_discharge_wh": round(planned_battery_discharge_wh, 1),
        "planned_soc_min_pct": round(planned_soc_min, 3),
        "planned_soc_max_pct": round(planned_soc_max, 3),
        "planned_reserve_shortfall_wh": round(planned_reserve_shortfall_wh, 2),
        "j1_objective": plan.j1_objective, "j2_objective": plan.j2_objective,
        "j3_objective": plan.j3_objective, "j4_objective": plan.j4_objective,
    }


def final_smoke_test(components):
    print("--- Final baseline-vs-Stage8.1 smoke test (single origin) before full run ---")
    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, _cap) = components
    origin = pd.Timestamp("2024-06-01T00:00:00Z")
    index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
    for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
        r = run_one_cycle(engine_label, engine, adapter, router, optimizer, option_d_solver,
                           simulator, configs_base, df, origin, index, base_fuel_lph, marginal_fuel_lpwh)
        print(f"  {engine_label}: route={r['route']} status={r['constraint_status']} "
              f"terminal_target_wh={r['terminal_target_wh']}")
        if r["constraint_status"] not in ("OPTIMAL",):
            raise RuntimeError(f"STOP: final smoke test did not reach OPTIMAL for {engine_label} "
                                f"(status={r['constraint_status']}). Full run not launched.")
    print("Final smoke test PASSED. Launching full experiment.\n")


def main():
    print("=" * 80)
    print("FULL RESEARCH-ONLY CLOSED-LOOP MILP EXPERIMENT -- R1 frozen assumptions")
    print("NOT a production run. NOT governance-authorized. RESEARCH-SIMULATION ONLY.")
    print("=" * 80)

    verify_frozen_manifest()
    components = build_components()
    final_smoke_test(components)

    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, _cap) = components

    origins = sorted(df["forecast_start"].unique())
    origins = [pd.Timestamp(o) for o in origins]
    print(f"Established evaluation window: {len(origins)} daily origins, "
          f"{origins[0]} .. {origins[-1]}\n")

    results = []
    t_start = time.time()
    try:
        for i, origin in enumerate(origins):
            index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
            for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
                r = run_one_cycle(engine_label, engine, adapter, router, optimizer, option_d_solver,
                                   simulator, configs_base, df, origin, index, base_fuel_lph, marginal_fuel_lpwh)
                results.append(r)

            if (i + 1) % CHECKPOINT_EVERY == 0 or (i + 1) == len(origins):
                elapsed = time.time() - t_start
                print(f"Checkpoint: {i+1}/{len(origins)} origins done ({len(results)} cycles), "
                      f"elapsed={elapsed:.1f}s")
                ckpt_path = THIS_DIR / "RESEARCH_FULL_EXPERIMENT_CHECKPOINT.json"
                with open(ckpt_path, "w") as f:
                    json.dump({
                        "disclaimer": "RESEARCH-SIMULATION ONLY. In-progress checkpoint.",
                        "origins_done": i + 1, "origins_total": len(origins),
                        "cycles_done": len(results), "elapsed_s": round(elapsed, 1),
                        "results": results,
                    }, f, indent=2)
    except Exception as exc:
        print(f"\nSTOP: unexpected failure during full run after {len(results)} cycles: {exc}")
        ckpt_path = THIS_DIR / "RESEARCH_FULL_EXPERIMENT_CHECKPOINT.json"
        with open(ckpt_path, "w") as f:
            json.dump({
                "disclaimer": "RESEARCH-SIMULATION ONLY. Run HALTED due to failure.",
                "halted": True, "error": str(exc),
                "cycles_done": len(results), "results": results,
            }, f, indent=2)
        raise

    out_path = THIS_DIR / "RESEARCH_FULL_EXPERIMENT_RAW_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": "RESEARCH-SIMULATION OUTPUT ONLY. SIMULATED_RESEARCH_ASSUMPTION "
                           "terminal reserve (R1, frozen). Not a real operational result, "
                           "not stakeholder-authorized, not a performance claim.",
            "manifest": "FROZEN_RESEARCH_EXPERIMENT_MANIFEST.md (R1)",
            "origins_total": len(origins), "cycles_total": len(results),
            "elapsed_s": round(time.time() - t_start, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nFull raw results written to {out_path}")
    print(f"Total: {len(origins)} origins, {len(results)} cycles, "
          f"{round(time.time() - t_start, 1)}s elapsed.")
    print("\nFULL RESEARCH-ONLY EXPERIMENT COMPLETE. No production code or config was modified.")


if __name__ == "__main__":
    main()
