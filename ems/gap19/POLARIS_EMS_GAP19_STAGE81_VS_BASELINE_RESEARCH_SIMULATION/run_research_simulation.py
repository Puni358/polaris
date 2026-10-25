#!/usr/bin/env python3
"""
RESEARCH-ONLY SIMULATION. NOT a production run. NOT a governance-authorized experiment.

Compares, for a handful of independent single-cycle closed-loop evaluations
(ForecastBundle -> EMSControlRouter -> GAP19HighsNativeOptimizer -> DigitalTwinSimulator.step),
the baseline forecast engine against the frozen Stage 8.1 CORRECTED forecast engine.

All production code (system/*, worker.py, gap19_highs_native.py, *.yaml configs) is used
UNCHANGED and UNMODIFIED. The one missing governed input, `terminal_target_wh`, is supplied
by THIS SCRIPT ONLY, computed per the SIMULATED_RESEARCH_ASSUMPTION formula frozen in
RESEARCH_EXCEPTION_DECISION_RECORD.md in this same directory. It is injected through GAP19's
existing config["terminal_target_wh"] input slot -- the same mechanism this codebase's own
unit tests already use -- not by changing GAP19 itself.

Results below are RESEARCH-SIMULATION OUTPUTS ONLY. They describe the behavior of a MILP
dispatch model under two different forecast inputs, with assumption values that are
explicitly NOT stakeholder-authorized. They do not describe, predict, or claim real station
or operational performance, and do not claim either forecast engine "wins".
"""
import sys
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))

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

MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
PV_CONFIG_PATH = BASE / "system" / "config" / "solar_pv.yaml"

# ---- SIMULATED_RESEARCH_ASSUMPTION constants (frozen in RESEARCH_EXCEPTION_DECISION_RECORD.md) ----
TECHNICAL_MIN_SOC_FRACTION = 0.20          # CURRENT_IMPLEMENTATION_FACT (battery.yaml)
BATTERY_CAPACITY_WH = 200000.0             # CURRENT_IMPLEMENTATION_FACT (battery.yaml)
TERMINAL_FLOOR_WH = TECHNICAL_MIN_SOC_FRACTION * BATTERY_CAPACITY_WH  # SIMULATED_RESEARCH_ASSUMPTION (floor=technical min)
LOOKAHEAD_WINDOW_HOURS = 6                 # GOVERNANCE_AUTHORIZED: T_REQUIRED = 6h
UNCERTAINTY_MARGIN = 0.10                  # SIMULATED_RESEARCH_ASSUMPTION (borrowed from unauthorized NC-07)

# Daily origins to evaluate (5 independent single-cycle closed-loop evaluations).
ORIGINS = [
    pd.Timestamp("2024-06-01T00:00:00Z"),
    pd.Timestamp("2024-06-02T00:00:00Z"),
    pd.Timestamp("2024-06-03T00:00:00Z"),
    pd.Timestamp("2024-06-04T00:00:00Z"),
    pd.Timestamp("2024-06-05T00:00:00Z"),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_terminal_target_wh(bundle):
    """SIMULATED_RESEARCH_ASSUMPTION formula -- see RESEARCH_EXCEPTION_DECISION_RECORD.md.
    Uses ONLY this cycle's own 24h ForecastBundle (no hindsight, no future actuals).
    """
    window = range(24 - LOOKAHEAD_WINDOW_HOURS, 24)  # last 6 of the 24 horizon hours
    deficit_wh = 0.0
    for k in window:
        crit_demand_w = bundle.demand.point[k]
        renewable_avail_w = bundle.solar_generation.point[k] + bundle.wind_generation.point[k]
        net_w = max(0.0, crit_demand_w - renewable_avail_w)
        deficit_wh += net_w * 1.0  # 1 hour timestep
    return TERMINAL_FLOOR_WH + deficit_wh * (1.0 + UNCERTAINTY_MARGIN)


def run_one_cycle(engine_label, engine, adapter, router, optimizer, option_d_solver,
                   simulator, configs_base, matrix_df, origin, index):
    st_k_raw = adapter.get_station_state(index, battery_soc_pct=50.0)
    assert st_k_raw.timestamp == origin.strftime("%Y-%m-%dT%H:%M:%SZ"), \
        f"Fixture index->timestamp mismatch: {st_k_raw.timestamp} vs {origin}"

    # Warmed-up (non-cold-start) state so the router selects NORMAL (GAP19), matching the
    # existing proven smoke-test pattern -- not a new assumption, reused unchanged.
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
        assert len(origin_rows) == 24
        feature_matrix = origin_rows[CANDIDATE_37_FEATURES].copy()
        runtime_ctx = {"stage8_1_feature_matrix": feature_matrix}
        bundle = engine.predict(st_k, runtime_ctx)
    else:
        bundle = engine.predict(st_k, {})

    configs = dict(configs_base)
    critical_load_baseline_w = float(
        configs.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
    )
    configs["critical_demand_w"] = [min(critical_load_baseline_w, d) for d in bundle.demand.point]

    terminal_target_wh = compute_terminal_target_wh(bundle)
    configs["terminal_target_wh"] = terminal_target_wh  # SIMULATED_RESEARCH_ASSUMPTION, this script only

    assessment, route = router.evaluate_and_route(st_k, bundle, configs)

    if route == "NORMAL":
        plan = optimizer.optimize(bundle, st_k, configs)
    elif route == "EMERGENCY":
        plan = option_d_solver.solve(assessment, bundle, st_k, configs)
    else:
        raise RuntimeError(f"STOP: unknown route '{route}'")

    next_state = simulator.step(st_k, plan, next_actual)

    return {
        "engine": engine_label,
        "origin": origin.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "route": route,
        "terminal_target_wh": round(terminal_target_wh, 2),
        "constraint_status": plan.constraint_status,
        "battery_charge_t0_w": round(plan.battery_charge[0], 2),
        "battery_discharge_t0_w": round(plan.battery_discharge[0], 2),
        "diesel_power_t0_w": round(plan.diesel_power[0], 2),
        "next_battery_soc_pct": round(next_state.battery_soc_pct, 3),
        "next_battery_energy_wh": round(next_state.battery_energy_wh, 1),
    }


def main():
    print("=" * 80)
    print("RESEARCH-ONLY SIMULATION -- NOT a production run, NOT governance-authorized.")
    print("See RESEARCH_EXCEPTION_DECISION_RECORD.md for all SIMULATED_RESEARCH_ASSUMPTION labels.")
    print("=" * 80)

    matrix_hash = sha256_of(MATRIX_PATH)
    assert matrix_hash == EXPECTED_MATRIX_HASH, "STOP: corrected feature matrix hash mismatch."
    model_hash = sha256_of(FROZEN_MODEL_PATH)
    assert model_hash == FROZEN_MODEL_SHA256, "STOP: frozen Stage 8.1 model hash mismatch."
    print("Frozen matrix/model hashes verified.\n")

    adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
    assert adapter.total_records == 8784

    df = pd.read_csv(MATRIX_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)

    configs_base = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        cfg_file = BASE / "system" / "config" / f"{cfg_name}.yaml"
        if cfg_file.exists():
            with open(cfg_file) as f:
                configs_base[cfg_name] = yaml.safe_load(f)

    baseline_engine = LocalBaselineForecastEngine(PV_CONFIG_PATH)
    stage81_engine = Stage81CorrectedForecastEngine()

    router = EMSControlRouter()
    optimizer = GAP19HighsNativeOptimizer()
    option_d_solver = OptionDFallbackSolver()
    simulator = DigitalTwinSimulator(configs_base)

    results = []
    for origin in ORIGINS:
        delta_hours = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
        for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
            r = run_one_cycle(engine_label, engine, adapter, router, optimizer, option_d_solver,
                               simulator, configs_base, df, origin, delta_hours)
            results.append(r)
            print(json.dumps(r))

    out_path = Path(__file__).parent / "RESEARCH_SIMULATION_RAW_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": "RESEARCH-SIMULATION OUTPUT ONLY. Uses SIMULATED_RESEARCH_ASSUMPTION "
                           "values (see RESEARCH_EXCEPTION_DECISION_RECORD.md). Not a real "
                           "operational result, not a stakeholder-authorized configuration, "
                           "not a performance claim for either forecast engine.",
            "results": results,
        }, f, indent=2)
    print(f"\nRaw results written to {out_path}")
    print("\nRESEARCH-ONLY SIMULATION COMPLETE. No production code or config was modified.")


if __name__ == "__main__":
    main()
