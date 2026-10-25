#!/usr/bin/env python3
"""
R2 pre-flight check: verify wind_generation and demand are bit-identical between the
baseline and Stage 8.1 forecast engines at EVERY one of the 347 evaluation origins.

Read-only: calls ForecastEngine.predict() only. No optimizer, no simulator, no config
change, no production code modification. If any origin fails this check, the script
exits non-zero and NO further R2 step may proceed (hard gate).
"""
import sys
import hashlib
import json
from pathlib import Path

import pandas as pd

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
THIS_DIR = Path(__file__).parent

from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.forecasting.implementations.s81_corrected_solar import (
    Stage81CorrectedForecastEngine, CANDIDATE_37_FEATURES, FROZEN_MODEL_SHA256, FROZEN_MODEL_PATH,
)

MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
PV_CONFIG_PATH = BASE / "system" / "config" / "solar_pv.yaml"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("--- R2 pre-flight: identical wind/demand check across all origins ---")
    matrix_hash = sha256_of(MATRIX_PATH)
    if matrix_hash != EXPECTED_MATRIX_HASH:
        print(f"STOP: matrix hash mismatch ({matrix_hash} != {EXPECTED_MATRIX_HASH})")
        sys.exit(1)
    model_hash = sha256_of(FROZEN_MODEL_PATH)
    if model_hash != FROZEN_MODEL_SHA256:
        print(f"STOP: model hash mismatch ({model_hash} != {FROZEN_MODEL_SHA256})")
        sys.exit(1)
    print("Matrix/model hashes verified OK.")

    df = pd.read_csv(MATRIX_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    origins = sorted(df["forecast_start"].unique())
    origins = [pd.Timestamp(o) for o in origins]

    adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
    if adapter.total_records != 8784:
        print(f"STOP: fixture record count changed ({adapter.total_records} != 8784)")
        sys.exit(1)

    baseline_engine = LocalBaselineForecastEngine(PV_CONFIG_PATH)
    stage81_engine = Stage81CorrectedForecastEngine()

    mismatches = []
    checked = 0
    for origin in origins:
        index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
        st_k_raw = adapter.get_station_state(index, battery_soc_pct=50.0)
        expected_ts = origin.strftime("%Y-%m-%dT%H:%M:%SZ")
        if st_k_raw.timestamp != expected_ts:
            mismatches.append({"origin": expected_ts, "error": f"fixture index mismatch: {st_k_raw.timestamp}"})
            continue

        st_k = StationState(
            timestamp=st_k_raw.timestamp, battery_soc_pct=80.0, battery_energy_wh=160000.0,
            diesel_running=True, diesel_hours_running=2.0,
            last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
            last_observed_demand=st_k_raw.last_observed_demand,
            last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
            diesel_fuel_remaining_liters=500.0,
        )

        bundle_b = baseline_engine.predict(st_k, {})
        origin_rows = df[df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
        feature_matrix = origin_rows[CANDIDATE_37_FEATURES].copy()
        bundle_s = stage81_engine.predict(st_k, {"stage8_1_feature_matrix": feature_matrix})

        wind_equal = bundle_b.wind_generation.point == bundle_s.wind_generation.point
        demand_equal = bundle_b.demand.point == bundle_s.demand.point
        checked += 1
        if not (wind_equal and demand_equal):
            mismatches.append({
                "origin": expected_ts,
                "wind_equal": wind_equal,
                "demand_equal": demand_equal,
            })

    result = {
        "origins_checked": checked,
        "origins_total": len(origins),
        "mismatches": mismatches,
        "all_identical": len(mismatches) == 0 and checked == len(origins),
    }
    out_path = THIS_DIR / "R2_IDENTICAL_INPUT_VERIFICATION.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Checked {checked}/{len(origins)} origins.")
    print(f"Mismatches: {len(mismatches)}")
    print(f"Result written to {out_path}")

    if not result["all_identical"]:
        print("STOP: wind/demand are NOT identical between arms at one or more origins.")
        sys.exit(1)

    print("PASS: wind_generation and demand are bit-identical between baseline and "
          "Stage 8.1 arms at all 347 origins.")


if __name__ == "__main__":
    main()
