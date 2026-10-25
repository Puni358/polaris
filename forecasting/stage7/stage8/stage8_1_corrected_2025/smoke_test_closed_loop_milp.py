#!/usr/bin/env python3
"""
Closed-loop smoke test: Stage 8.1 CORRECTED (frozen) -> ForecastBundle -> MILP -> simulator.step.

Uses the REAL, UNCHANGED production components exactly as
system/orchestration/worker.py's "Cell B" execution path calls them:
  - H10RuntimeAdapter (real H1.0 fixture: 2024, 8784 hourly rows,
    SITES Nuolja REAL_MEASURED solar)
  - EMSControlRouter.evaluate_and_route (unchanged)
  - GAP19HighsNativeOptimizer.optimize / OptionDFallbackSolver.solve (unchanged)
  - DigitalTwinSimulator.step (unchanged)

The ONLY thing swapped in for this one call is the forecast engine: instead
of LocalBaselineForecastEngine's synthetic sine-curve solar, this script
calls Stage81CorrectedForecastEngine (the new adapter wired last turn)
with a feature matrix drawn from the ALREADY-VERIFIED, ALREADY-CAUSAL
corrected 2024 Stage 8.1 feature matrix
(stage8_1_full_37_feature_matrix_2024_CORRECTED.csv) for the origin that
matches the fixture's current timestep -- not fabricated, not using any
future actual observation. This is NOT a global replacement of the
baseline: worker.py, baseline.py, the router, the optimizer, the
simulator, OptionD and the fixture are all read-only/unchanged here.

Executes exactly ONE simulated timestep (origin 2024-01-20T00:00:00Z,
fixture index 456), then stops -- no campaign.
"""
import sys
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, "/home/punith-bs/01polaris (Copy)")

from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.simulation.simulator import DigitalTwinSimulator
from system.forecasting.implementations.s81_corrected_solar import (
    Stage81CorrectedForecastEngine, CANDIDATE_37_FEATURES, FROZEN_MODEL_SHA256, FROZEN_MODEL_PATH,
)

BASE = Path("/home/punith-bs/01polaris (Copy)")
MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"

FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
SMOKE_ORIGIN = pd.Timestamp("2024-06-01T00:00:00Z")
SMOKE_INDEX = 3648  # hours since 2024-01-01T00:00:00Z


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("CLOSED-LOOP SMOKE TEST: Stage 8.1 CORRECTED -> ForecastBundle -> MILP -> simulator.step")
    print("=" * 80)

    # ---- 0. Hash verification before anything else ----
    matrix_hash = sha256_of(MATRIX_PATH)
    print(f"Corrected 2024 feature matrix hash: {matrix_hash}  match={matrix_hash == EXPECTED_MATRIX_HASH}")
    assert matrix_hash == EXPECTED_MATRIX_HASH
    model_hash = sha256_of(FROZEN_MODEL_PATH)
    print(f"Frozen model hash: {model_hash}  match={model_hash == FROZEN_MODEL_SHA256}")
    assert model_hash == FROZEN_MODEL_SHA256

    # ---- 1. Real, unchanged adapter / fixture ----
    adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
    print(f"\nFixture loaded: {adapter.total_records} records (expected 8784)")
    assert adapter.total_records == 8784

    st_k = adapter.get_station_state(SMOKE_INDEX, battery_soc_pct=50.0)
    print(f"Station state at index {SMOKE_INDEX}: timestamp={st_k.timestamp}")
    assert st_k.timestamp == "2024-06-01T00:00:00Z", f"Fixture index->timestamp mismatch: {st_k.timestamp}"

    runtime_ctx_fixture = adapter.get_runtime_context(SMOKE_INDEX)  # unchanged, real -- unused fields simply ignored
    next_actual = adapter.get_future_ground_truth(SMOKE_INDEX, horizon_hours=24)[0]
    print(f"Next actual (for simulator stepping ONLY, never a model input): {next_actual['timestamp']}, "
          f"actual_SW_IN={next_actual['actual_SW_IN']}")

    # ---- 2. Causal Stage 8.1 feature block for this exact origin ----
    df = pd.read_csv(MATRIX_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    origin_rows = df[df["forecast_start"] == SMOKE_ORIGIN].sort_values("horizon_hour").reset_index(drop=True)
    assert len(origin_rows) == 24, f"Expected 24 rows for origin, got {len(origin_rows)}"
    assert list(origin_rows["horizon_hour"]) == list(range(1, 25))
    assert "actual_SW_IN" not in CANDIDATE_37_FEATURES

    feature_matrix = origin_rows[CANDIDATE_37_FEATURES].copy()
    print(f"\nFeature block for origin {SMOKE_ORIGIN}: shape={feature_matrix.shape}, "
          f"columns match frozen order={list(feature_matrix.columns) == CANDIDATE_37_FEATURES}")

    # ---- 3. Forecast engine (the ONLY swapped component, explicit, not global) ----
    engine = Stage81CorrectedForecastEngine()
    runtime_ctx = {"stage8_1_feature_matrix": feature_matrix}
    bundle = engine.predict(st_k, runtime_ctx)
    print(f"\nForecastBundle generated. origin_timestamp={bundle.origin_timestamp}, "
          f"horizon_hours={bundle.horizon_hours}")
    print(f"solar_irradiance.point (first 6): {[round(v, 3) for v in bundle.solar_irradiance.point[:6]]}")

    # ---- 4. Independent standalone re-verification of those exact values ----
    import joblib
    standalone_model = joblib.load(FROZEN_MODEL_PATH)
    X = feature_matrix[CANDIDATE_37_FEATURES].values.astype(np.float64)
    residual = standalone_model.predict(X)
    pred_stage4_fold = feature_matrix["pred_stage4_fold"].values
    solar_elevation = feature_matrix["solar_elevation"].values
    clearsky_ghi = feature_matrix["clearsky_ghi"].values
    is_night_causal = (solar_elevation <= 0.0) | (clearsky_ghi == 0.0)
    standalone_pred = np.where(is_night_causal, 0.0, np.maximum(0.0, pred_stage4_fold + residual))

    runtime_pred = np.array(bundle.solar_irradiance.point)
    max_abs_diff = np.max(np.abs(runtime_pred - standalone_pred))
    print(f"\nRuntime vs standalone max abs diff: {max_abs_diff:.2e}")
    values_match = bool(max_abs_diff < 1e-9)
    assert values_match, "STOP: runtime ForecastBundle values do not match standalone Stage 8.1 inference!"

    # Timestamp/horizon alignment check
    expected_ts = [(SMOKE_ORIGIN + pd.Timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]
    ts_match = bundle.timestamps == expected_ts
    print(f"Timestamp alignment (horizon_hour=1 == origin+0h convention) matches: {ts_match}")
    assert ts_match, "STOP: timestamp/horizon alignment mismatch!"

    # ---- 5. Real, unchanged router / MILP / OptionD ----
    configs = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        cfg_file = BASE / "system" / "config" / f"{cfg_name}.yaml"
        if cfg_file.exists():
            with open(cfg_file) as f:
                configs[cfg_name] = yaml.safe_load(f)
    print(f"\nLoaded configs: {list(configs.keys())}")

    router = EMSControlRouter()
    optimizer = GAP19HighsNativeOptimizer()
    option_d_solver = OptionDFallbackSolver()
    simulator = DigitalTwinSimulator(configs)

    assessment, route = router.evaluate_and_route(st_k, bundle, configs)
    print(f"Router decision: route={route}")

    if route == "NORMAL":
        plan = optimizer.optimize(bundle, st_k, configs)
    elif route == "EMERGENCY":
        plan = option_d_solver.solve(assessment, bundle, st_k, configs)
    else:
        raise RuntimeError(f"STOP: unknown route '{route}' -- does not match frozen router contract.")

    print(f"MILP/OptionD plan constraint_status: {plan.constraint_status}")
    print(f"plan.battery_charge[0]={plan.battery_charge[0]:.2f}  "
          f"plan.battery_discharge[0]={plan.battery_discharge[0]:.2f}  "
          f"plan.diesel_power[0]={plan.diesel_power[0]:.2f}")

    # ---- 6. Real, unchanged simulator step (uses next_actual for TRUE outcome only) ----
    next_state = simulator.step(st_k, plan, next_actual)
    print(f"\nSimulator stepped. New state timestamp={next_state.timestamp}, "
          f"battery_soc_pct={next_state.battery_soc_pct:.2f}, "
          f"battery_energy_wh={next_state.battery_energy_wh:.1f}")

    print("\n" + "=" * 80)
    print("CLOSED-LOOP SMOKE TEST: PASS")
    print("Stage 8.1 (corrected, frozen) -> ForecastBundle -> MILP -> simulator.step executed for ONE timestep.")
    print("No long campaign run. No model/MILP/simulator/EMS/OptionD code modified.")
    print("=" * 80)


if __name__ == "__main__":
    main()
