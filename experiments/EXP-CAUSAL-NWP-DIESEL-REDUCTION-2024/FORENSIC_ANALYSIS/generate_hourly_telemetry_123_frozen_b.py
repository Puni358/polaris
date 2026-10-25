"""
Generate exact hourly telemetry artifact for Frozen Control B across all 123 NORMAL origins.
Artifact: experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/hourly_trace_123_frozen_b/hourly_telemetry_123_frozen_b.json

123 origins * 24 hours = 2,952 rows.
Computes exact hourly proportional allocation and exact critical-first allocation.
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

import pandas as pd

REPO = Path("/home/punith-bs/01polaris (Copy)")
os.chdir(REPO)
sys.path.insert(0, str(REPO))

HERE = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS"
OUT_DIR = HERE / "hourly_trace_123_frozen_b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FROZEN_PATH = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"
WEATHER_PATH = REPO / "data/POLARIS_v0_1_future_weather_forecasts_2024.csv"

FROZEN = json.load(open(FROZEN_PATH))
WEATHER = pd.read_csv(WEATHER_PATH)

_tr = None
_base_cfg = None


def _init_worker():
    global _tr, _base_cfg
    spec = importlib.util.spec_from_file_location("trace", HERE / "trace_hourly.py")
    _tr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_tr)
    _base_cfg = _tr.camp.load_canonical_configs()


def run_single_origin(fr):
    oi = fr["origin_index"]
    fs = fr["forecast_start"]
    t0 = fr["t0_timestamp"]

    sub = WEATHER[WEATHER["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]

    rep, steps = _tr.trace_arm("B", oi, fs, t0, WEATHER, (rs, rw, rd, rts), _base_cfg)

    # Reproduction check against frozen Arm B
    fb = fr["arms"]["ARM_B_CANDIDATE"]
    assert abs(rep.cumulative_diesel_fuel_l - fb["diesel_fuel_liters"]) < 1e-3, f"Fuel mismatch at origin {oi}"
    assert abs(rep.cumulative_unmet_load_wh - fb["unmet_critical_load_wh"]) < 1e-2, f"Unmet mismatch at origin {oi}"
    assert abs(rep.cumulative_served_load_wh - fb["served_load_wh"]) < 1e-2, f"Served mismatch at origin {oi}"
    assert abs(rep.cumulative_curtailment_wh - fb["curtailment_wh"]) < 1e-2, f"Curtailment mismatch at origin {oi}"

    rows = []
    assert len(rep.step_records) == 24, f"Origin {oi} has {len(rep.step_records)} steps, expected 24"
    for h, sr in enumerate(rep.step_records):
        row = {
            "origin_index": oi,
            "hour": h,
            "forecast_start": fs,
            "target_timestamp": sr.target_timestamp,
            "realized_demand_w": sr.realized_demand_w,
            "served_load_w": sr.served_load_w,
            "unmet_load_w": sr.unmet_load_w,
            "realized_solar_w": sr.realized_solar_w,
            "realized_wind_w": sr.realized_wind_w,
            "realized_diesel_w": sr.realized_diesel_w,
            "realized_battery_discharge_w": sr.realized_battery_discharge_w,
            "realized_battery_charge_w": sr.realized_battery_charge_w,
            "realized_soc_pct": sr.realized_soc_pct,
            "curtailment_w": sr.curtailment_w,
            "diesel_fuel_consumed_l": sr.diesel_fuel_consumed_l,
            "busbar_balance_error_w": sr.busbar_balance_error_w
        }
        rows.append(row)
    return {
        "origin_index": oi,
        "fuel_l": rep.cumulative_diesel_fuel_l,
        "unmet_wh": rep.cumulative_unmet_load_wh,
        "served_wh": rep.cumulative_served_load_wh,
        "curtail_wh": rep.cumulative_curtailment_wh,
        "min_soc_pct": min(sr.realized_soc_pct for sr in rep.step_records),
        "rows": rows
    }


def main():
    print("=" * 80)
    print("GENERATING EXACT HOURLY TELEMETRY ARTIFACT: 123 ORIGINS FROZEN CONTROL B")
    print("=" * 80)
    t0_all = time.time()

    with Pool(processes=4, initializer=_init_worker) as pool:
        results = []
        for i, res in enumerate(pool.imap_unordered(run_single_origin, FROZEN, chunksize=1), 1):
            results.append(res)
            if i % 10 == 0 or i == len(FROZEN):
                print(f"[{i}/{len(FROZEN)}] origins executed and verified...", flush=True)

    results.sort(key=lambda r: r["origin_index"])

    all_rows = []
    for r in results:
        all_rows.extend(r["rows"])

    # Verification checks
    unique_origins = sorted(list(set(row["origin_index"] for row in all_rows)))
    assert len(unique_origins) == 123, f"Expected 123 unique origins, got {len(unique_origins)}"
    assert len(all_rows) == 2952, f"Expected 2952 rows, got {len(all_rows)}"

    # Check for duplicate (origin_index, hour)
    seen = set()
    for row in all_rows:
        key = (row["origin_index"], row["hour"])
        assert key not in seen, f"Duplicate record for origin {key[0]} hour {key[1]}"
        seen.add(key)
    assert len(seen) == 2952, f"Expected 2952 unique origin-hour keys, got {len(seen)}"

    # Serialize hourly telemetry artifact
    out_json_path = OUT_DIR / "hourly_telemetry_123_frozen_b.json"
    with open(out_json_path, "w") as f:
        json.dump(all_rows, f, indent=2)
    telemetry_sha256 = hashlib.sha256(out_json_path.read_bytes()).hexdigest()
    print(f"\nSerialized {len(all_rows)} rows to {out_json_path}")
    print(f"Artifact SHA-256: {telemetry_sha256}")

    # Compute EXACT hourly proportional allocation
    total_crit_demand = 0.0
    total_realized_demand = 0.0
    total_served_load = 0.0
    total_unmet_load = 0.0

    # Hourly proportional
    total_served_crit_prop = 0.0
    total_unmet_crit_prop = 0.0

    # Critical first
    total_served_crit_first = 0.0
    total_unmet_crit_first = 0.0

    for row in all_rows:
        d_real = row["realized_demand_w"]
        s_tot = row["served_load_w"]
        u_tot = row["unmet_load_w"]

        d_crit = min(11600.0, d_real)

        total_crit_demand += d_crit
        total_realized_demand += d_real
        total_served_load += s_tot
        total_unmet_load += u_tot

        # Proportional:
        s_crit_prop = s_tot * (d_crit / d_real)
        u_crit_prop = d_crit - s_crit_prop

        total_served_crit_prop += s_crit_prop
        total_unmet_crit_prop += u_crit_prop

        # Critical first:
        supply = (
            row["realized_solar_w"]
            + row["realized_wind_w"]
            + row["realized_diesel_w"]
            + row["realized_battery_discharge_w"]
        )
        s_crit_first = min(d_crit, supply)
        u_crit_first = d_crit - s_crit_first

        total_served_crit_first += s_crit_first
        total_unmet_crit_first += u_crit_first

    r_prop_exact = 1.0 - (total_unmet_crit_prop / total_crit_demand)
    r_crit_first_exact = 1.0 - (total_unmet_crit_first / total_crit_demand)
    r_flat_prop_approx = 1.0 - ((total_unmet_load * (total_crit_demand / total_realized_demand)) / total_crit_demand)

    print("\n" + "=" * 80)
    print("EXACT RECONCILED BASELINE METRICS (2,952 HOURLY ROWS)")
    print("=" * 80)
    print(f"Total Unique Origins:             {len(unique_origins)}")
    print(f"Total Hourly Rows:                {len(all_rows)}")
    print(f"Total Critical Demand:            {total_crit_demand:.2f} Wh ({total_crit_demand/1e3:.2f} kWh)")
    print(f"Total Realized Demand:            {total_realized_demand:.2f} Wh ({total_realized_demand/1e3:.2f} kWh)")
    print(f"Total Realized Served:            {total_served_load:.2f} Wh ({total_served_load/1e3:.2f} kWh)")
    print(f"Total Realized Unmet:             {total_unmet_load:.2f} Wh ({total_unmet_load/1e3:.2f} kWh)")
    print("-" * 80)
    print(f"CRITICAL-FIRST ALLOCATION:")
    print(f"  Served Critical Load:           {total_served_crit_first:.2f} Wh ({total_served_crit_first/1e3:.2f} kWh)")
    print(f"  Unmet Critical Load:            {total_unmet_crit_first:.2f} Wh ({total_unmet_crit_first/1e3:.2f} kWh)")
    print(f"  Critical-First Reliability:     {r_crit_first_exact * 100.0:.6f}%")
    print("-" * 80)
    print(f"EXACT HOURLY PROPORTIONAL ALLOCATION:")
    print(f"  Served Critical Load:           {total_served_crit_prop:.2f} Wh ({total_served_crit_prop/1e3:.2f} kWh)")
    print(f"  Unmet Critical Load:            {total_unmet_crit_prop:.2f} Wh ({total_unmet_crit_prop/1e3:.2f} kWh)")
    print(f"  Exact Proportional Reliability: {r_prop_exact * 100.0:.6f}%")
    print("-" * 80)
    print(f"COMPARISON AGAINST FLAT PROPORTIONAL APPROXIMATION:")
    print(f"  Flat Proportional Approx:       {r_flat_prop_approx * 100.0:.6f}% (Old 82.2845%)")
    print(f"  Exact Hourly Proportional:      {r_prop_exact * 100.0:.6f}%")
    print(f"  Discrepancy (Exact - Approx):   {(r_prop_exact - r_flat_prop_approx) * 100.0:+.6f} percentage points")
    print("=" * 80)

    summary = {
        "execution_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": round(time.time() - t0_all, 2),
        "origins_count": len(unique_origins),
        "total_hourly_rows": len(all_rows),
        "telemetry_artifact": {
            "path": str(out_json_path.relative_to(REPO)),
            "sha256": telemetry_sha256,
            "row_count": len(all_rows)
        },
        "critical_first": {
            "total_critical_demand_wh": round(total_crit_demand, 2),
            "total_served_critical_wh": round(total_served_crit_first, 2),
            "total_unmet_critical_wh": round(total_unmet_crit_first, 2),
            "reliability_pct": round(r_crit_first_exact * 100.0, 6)
        },
        "exact_hourly_proportional": {
            "total_critical_demand_wh": round(total_crit_demand, 2),
            "total_served_critical_wh": round(total_served_crit_prop, 2),
            "total_unmet_critical_wh": round(total_unmet_crit_prop, 2),
            "reliability_pct": round(r_prop_exact * 100.0, 6)
        },
        "flat_proportional_approximation": {
            "reliability_pct": round(r_flat_prop_approx * 100.0, 6),
            "discrepancy_pp": round((r_prop_exact - r_flat_prop_approx) * 100.0, 6)
        },
        "frozen_totals_verification": {
            "total_diesel_fuel_liters": round(sum(r["fuel_l"] for r in results), 4),
            "total_unmet_load_wh": round(total_unmet_load, 2),
            "total_served_load_wh": round(total_served_load, 2),
            "total_curtailment_wh": round(sum(r["curtail_wh"] for r in results), 2),
            "min_soc_pct": round(min(r["min_soc_pct"] for r in results), 2),
            "all_123_origins_reproduced": True
        }
    }

    summary_path = OUT_DIR / "hourly_telemetry_123_frozen_b_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    summary_sha256 = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    print(f"Summary JSON SHA-256: {summary_sha256}")


if __name__ == "__main__":
    main()
