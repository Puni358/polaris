#!/usr/bin/env python3
"""
Deterministic single-origin smoke test for Stage81CorrectedForecastEngine.

Compares the runtime ForecastBundle (built via the new engine, through
system/forecasting/interface/base.py's ForecastEngine contract) against
standalone Stage 8.1 inference for the exact same origin, using the
already-verified corrected 2025 feature matrix and the already-verified
standalone 2025 blind predictions (produced by
run_2025_blind_evaluation.py in a prior step of this investigation).

Does not retrain, does not modify the model, does not touch any frozen
artifact. Read-only verification only.
"""
import sys
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/punith-bs/01polaris (Copy)")
from system.forecasting.implementations.s81_corrected_solar import (
    Stage81CorrectedForecastEngine, CANDIDATE_37_FEATURES, FROZEN_MODEL_SHA256,
)
from system.schemas.station_state import StationState

BASE = Path("/home/punith-bs/01polaris (Copy)")
MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"
STANDALONE_PRED_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv"
EXPECTED_MATRIX_HASH = "9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087"
EXPECTED_PRED_HASH = "65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("SMOKE TEST: Stage81CorrectedForecastEngine vs standalone Stage 8.1 inference")
    print("=" * 80)

    matrix_hash = sha256_of(MATRIX_PATH)
    pred_hash = sha256_of(STANDALONE_PRED_PATH)
    print(f"2025 corrected matrix hash: {matrix_hash}  match={matrix_hash == EXPECTED_MATRIX_HASH}")
    print(f"Standalone pred hash:       {pred_hash}  match={pred_hash == EXPECTED_PRED_HASH}")
    assert matrix_hash == EXPECTED_MATRIX_HASH
    assert pred_hash == EXPECTED_PRED_HASH

    df = pd.read_csv(MATRIX_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    origin = sorted(df["forecast_start"].unique())[0]
    print(f"\nSmoke-test origin: {origin}")

    origin_rows = df[df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
    assert len(origin_rows) == 24
    assert list(origin_rows["horizon_hour"]) == list(range(1, 25))

    feature_matrix = origin_rows[CANDIDATE_37_FEATURES].copy()
    expected_timestamps = list(origin_rows["timestamp"])

    # 1. Instantiate the engine (hash-verifies the frozen model on load)
    engine = Stage81CorrectedForecastEngine()
    print(f"Engine loaded, model hash verified against {FROZEN_MODEL_SHA256}")

    station_state = StationState(
        timestamp=origin.strftime("%Y-%m-%dT%H:%M:%SZ"),
        battery_soc_pct=50.0,
        battery_energy_wh=50000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=5000.0,
    )

    runtime_context = {"stage8_1_feature_matrix": feature_matrix}

    # 2. Run through the runtime ForecastEngine interface
    bundle = engine.predict(station_state, runtime_context)

    # 3. Standalone reference: the already-verified 2025 blind predictions for this origin
    standalone = pd.read_csv(STANDALONE_PRED_PATH)
    standalone["forecast_start"] = pd.to_datetime(standalone["forecast_start"], utc=True)
    standalone_origin = standalone[standalone["forecast_start"] == origin].sort_values("horizon_hour")
    assert len(standalone_origin) == 24
    standalone_pred = standalone_origin["pred_stage8_1_CORRECTED_blind2025"].values

    runtime_pred = np.array(bundle.solar_irradiance.point)

    print("\n--- VALUE COMPARISON ---")
    max_abs_diff = np.max(np.abs(runtime_pred - standalone_pred))
    print(f"Runtime predictions (first 5):     {runtime_pred[:5]}")
    print(f"Standalone predictions (first 5):  {standalone_pred[:5]}")
    print(f"Max abs diff (runtime vs standalone): {max_abs_diff:.10f}")
    values_match = bool(max_abs_diff < 1e-9)
    print(f"Values match (tolerance 1e-9): {values_match}")

    print("\n--- TIMESTAMP / HORIZON ALIGNMENT ---")
    runtime_ts = [pd.Timestamp(t) for t in bundle.timestamps]
    expected_ts = [pd.Timestamp(t) for t in expected_timestamps]
    ts_match = runtime_ts == expected_ts
    print(f"Runtime timestamps (first 3):  {bundle.timestamps[:3]}")
    print(f"Expected timestamps (first 3): {[t.strftime('%Y-%m-%dT%H:%M:%SZ') for t in expected_timestamps[:3]]}")
    print(f"Origin timestamp: {bundle.origin_timestamp}")
    print(f"All 24 timestamps match exactly: {ts_match}")

    print("\n--- FEATURE ORDER CHECK ---")
    order_ok = list(feature_matrix.columns) == CANDIDATE_37_FEATURES
    print(f"Feature matrix column order matches frozen CANDIDATE_37_FEATURES exactly: {order_ok}")

    print("\n--- FORECASTBUNDLE SCHEMA CHECK ---")
    print(f"schema_version: {bundle.schema_version}")
    print(f"horizon_hours: {bundle.horizon_hours}")
    print(f"len(solar_irradiance.point): {len(bundle.solar_irradiance.point)}")
    print(f"solar_irradiance.unit: {bundle.solar_irradiance.unit}")
    print(f"solar_generation.unit: {bundle.solar_generation.unit}")
    print(f"model_sha256 in metadata: {bundle.metadata.get('model_sha256')}")
    print(f"model_sha256 matches frozen constant: {bundle.metadata.get('model_sha256') == FROZEN_MODEL_SHA256}")
    schema_ok = (
        bundle.schema_version == "1.0.0" and bundle.horizon_hours == 24
        and len(bundle.solar_irradiance.point) == 24
        and bundle.solar_irradiance.unit == "W/m^2" and bundle.solar_generation.unit == "W"
    )

    print("\n--- NO FUTURE-TARGET-AS-INPUT CHECK ---")
    no_target_leak = "actual_SW_IN" not in feature_matrix.columns
    print(f"'actual_SW_IN' absent from the 37-feature input matrix: {no_target_leak}")

    print("\n" + "=" * 80)
    overall_pass = values_match and ts_match and order_ok and schema_ok and no_target_leak
    print(f"OVERALL SMOKE TEST: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 80)

    if not overall_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
