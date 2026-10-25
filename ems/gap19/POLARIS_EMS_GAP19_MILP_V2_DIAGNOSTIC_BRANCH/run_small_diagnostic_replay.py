#!/usr/bin/env python3
"""
MILP-v2 DIAGNOSTIC BRANCH -- small validation replay.

Calls the REAL, UNMODIFIED GAP19HighsNativeOptimizer.optimize() (same code, same config,
same inputs as R1/R2) for a SMALL set of origins chosen to cover both regimes identified in
prior forensic reports:
  - 2024-08-12: large diesel increase, reserve envelope binding (from R1/R2 top-8 list)
  - 2024-06-19: large diesel increase, reserve envelope NOT binding for either arm (the
    "Mechanism 1 alone" case from the prior forensic report)
  - 2024-06-01: a typical/small-delta origin, for contrast

This is a REPLAY for instrumentation validation only -- NOT a rerun of the full 347-origin
R1/R2 experiment, NOT a change to R1/R2's frozen assumptions, NOT a change to optimizer
behavior. The optimizer call, config, and terminal-target formula are byte-identical to
R1/R2's own run_one_cycle (reused by direct import).
"""
import sys
import json
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
    Stage81CorrectedForecastEngine, CANDIDATE_37_FEATURES,
)
from run_research_simulation import compute_terminal_target_wh  # frozen R1/R2 formula, imported not copied

from diagnostic_instrumentation import instrument_cycle

MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
PV_CONFIG_PATH = BASE / "system" / "config" / "solar_pv.yaml"

DIAGNOSTIC_ORIGINS = [
    "2024-08-12T00:00:00Z",  # large diesel increase, J2-binding regime
    "2024-06-19T00:00:00Z",  # large diesel increase, J2 non-binding (Mechanism 1 alone)
    "2024-06-01T00:00:00Z",  # small/typical delta, for contrast
]


def main():
    print("=" * 80)
    print("MILP-v2 DIAGNOSTIC BRANCH -- small instrumentation-validation replay")
    print("NOT a rerun of R1/R2. NOT a change to optimizer behavior or frozen assumptions.")
    print("=" * 80)

    df = pd.read_csv(MATRIX_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)

    configs_base = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        cfg_file = BASE / "system" / "config" / f"{cfg_name}.yaml"
        if cfg_file.exists():
            with open(cfg_file) as f:
                configs_base[cfg_name] = yaml.safe_load(f)

    adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
    baseline_engine = LocalBaselineForecastEngine(PV_CONFIG_PATH)
    stage81_engine = Stage81CorrectedForecastEngine()
    router = EMSControlRouter()
    optimizer = GAP19HighsNativeOptimizer()
    option_d_solver = OptionDFallbackSolver()
    simulator = DigitalTwinSimulator(configs_base)

    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    min_soc_pct = float(configs_base.get("battery", {}).get("min_soc_pct", 20.0))
    capacity_wh = float(configs_base.get("battery", {}).get("capacity_wh", 200000.0))
    min_e_wh = capacity_wh * (min_soc_pct / 100.0)
    dt = 1.0

    all_results = {}
    for origin_str in DIAGNOSTIC_ORIGINS:
        origin = pd.Timestamp(origin_str)
        index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
        st_k_raw = adapter.get_station_state(index, battery_soc_pct=50.0)
        st_k = StationState(
            timestamp=st_k_raw.timestamp, battery_soc_pct=80.0, battery_energy_wh=160000.0,
            diesel_running=True, diesel_hours_running=2.0,
            last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
            last_observed_demand=st_k_raw.last_observed_demand,
            last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
            diesel_fuel_remaining_liters=500.0,
        )

        origin_result = {}
        for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
            if engine_label == "stage8_1_corrected":
                origin_rows = df[df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
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
            elif route == "EMERGENCY":
                plan = option_d_solver.solve(assessment, bundle, st_k, configs)
            else:
                raise RuntimeError(f"STOP: unknown route '{route}'")

            if route == "NORMAL":
                diag = instrument_cycle(plan, critical_demand, terminal_target_wh, eta_dis, dt, min_e_wh)
                diag["route"] = route
            else:
                diag = {"route": route, "note": "EMERGENCY/OptionD route -- terminal_target_wh/J2 envelope not read by this path (confirmed by code trace); not instrumented further here."}

            origin_result[engine_label] = diag
            print(f"{origin_str} [{engine_label}]: route={route} "
                  f"status={diag.get('constraint_status', 'n/a')} "
                  f"binding_timesteps={diag.get('binding_timestep_count', 'n/a')}")

        all_results[origin_str] = origin_result

    out_path = THIS_DIR / "DIAGNOSTIC_REPLAY_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": "MILP-v2 DIAGNOSTIC BRANCH. Small validation replay only. "
                           "Uses the REAL unmodified GAP19 optimizer; instrumentation adds "
                           "no change to optimizer behavior. NOT a rerun of R1/R2's full "
                           "347-origin experiment. RESEARCH/DIAGNOSTIC USE ONLY.",
            "origins": DIAGNOSTIC_ORIGINS,
            "results": all_results,
        }, f, indent=2)
    print(f"\nDiagnostic replay results written to {out_path}")
    print("DIAGNOSTIC REPLAY COMPLETE. R1/R2 untouched. No optimizer behavior changed.")


if __name__ == "__main__":
    main()
