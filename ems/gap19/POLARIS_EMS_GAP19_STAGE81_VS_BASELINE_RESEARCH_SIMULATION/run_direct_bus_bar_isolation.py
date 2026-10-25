#!/usr/bin/env python3
"""
DIRECT BUS-BAR PATHWAY ISOLATION. RESEARCH-ONLY. NOT a production run.

Smallest valid counterfactual isolating the direct bus-bar energy-balance mechanism from the
terminal-reserve mechanism, for a handful of representative origins (not a rerun of the full
347-origin window -- that full counterfactual already exists:
TERMINAL_ABLATION_RAW_RESULTS.json, where terminal_target_wh is forced to the solar-
insensitive 40000 Wh constant for both arms at ALL 347 origins, confirmed to make
planned_reserve_shortfall_wh == 0 for both arms at every one of the 245 NORMAL-route
origins -- i.e. J2 is already fully isolated-out in that run). This script re-executes ONLY
a handful of origins from that same ablated configuration (same monkeypatch, same frozen
GAP19/configs/StationState/forecast engines) but captures the FULL per-hour DispatchPlan
(solar_used, wind_used, battery_charge/discharge, diesel_power, renewable_curtailment,
load_served, unmet_load) for both engines, which the full 347-origin run's result-collection
code (frozen, from run_full_experiment.py) does not retain -- only per-cycle sums. This is
the smallest additional step needed to see, hour-by-hour, exactly where and why the two
engines' plans diverge once the reserve-envelope difference has been removed.

No production code, config, or frozen artifact is modified. Same in-process monkeypatch
technique as run_terminal_target_ablation.py (reused, not duplicated logic -- imports the
same frozen run_full_experiment module functions).
"""
import sys
import json
from pathlib import Path

import pandas as pd

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

import run_full_experiment as rfe
from system.schemas.station_state import StationState

ABLATED_TERMINAL_TARGET_WH = 40000.0

# Representative origins: largest-delta origin found in the full ablation run (2024-10-27),
# a mid-shoulder-season origin (2024-03-20), the already-established reference origin
# (2024-06-01), and a zero-delta origin for contrast (any origin NOT in the 137 nonzero set --
# 2024-01-25 is EMERGENCY-route so excluded; 2024-12-01 checked to be NORMAL + zero-delta
# below at runtime, not assumed).
CANDIDATE_ORIGINS = [
    "2024-10-27T00:00:00Z",  # largest delta under ablation
    "2024-03-20T00:00:00Z",  # shoulder season
    "2024-06-01T00:00:00Z",  # reference origin used throughout this diagnostic branch
    "2024-12-01T00:00:00Z",  # candidate contrast origin (checked below, not assumed zero)
]


def main():
    print("=" * 80)
    print("DIRECT BUS-BAR PATHWAY ISOLATION -- per-hour deep dive, same ablated config")
    print("(terminal_target_wh = 40000 constant, both arms) as the full 347-origin ablation.")
    print("NOT a production run. RESEARCH-ONLY. Frozen code/config unmodified.")
    print("=" * 80)

    rfe.verify_frozen_manifest()

    original_fn = rfe.compute_terminal_target_wh
    rfe.compute_terminal_target_wh = lambda bundle: ABLATED_TERMINAL_TARGET_WH
    print(f"Monkeypatched compute_terminal_target_wh -> constant {ABLATED_TERMINAL_TARGET_WH} "
          f"Wh, in-process only (same as run_terminal_target_ablation.py).\n")

    all_detail = {}
    try:
        components = rfe.build_components()
        (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
         option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, _cap) = components

        for origin_str in CANDIDATE_ORIGINS:
            origin = pd.Timestamp(origin_str)
            index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)

            origin_detail = {}
            for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
                st_k_raw = adapter.get_station_state(index, battery_soc_pct=50.0)
                st_k = StationState(
                    timestamp=st_k_raw.timestamp, battery_soc_pct=80.0, battery_energy_wh=160000.0,
                    diesel_running=True, diesel_hours_running=2.0,
                    last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
                    last_observed_demand=st_k_raw.last_observed_demand,
                    last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
                    diesel_fuel_remaining_liters=500.0,
                )
                if engine_label == "stage8_1_corrected":
                    from system.forecasting.implementations.s81_corrected_solar import CANDIDATE_37_FEATURES
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
                configs["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle)  # == 40000.0

                assessment, route = router.evaluate_and_route(st_k, bundle, configs)
                if route != "NORMAL":
                    origin_detail[engine_label] = {"route": route, "note": "not NORMAL, skipped"}
                    continue
                plan = optimizer.optimize(bundle, st_k, configs)

                origin_detail[engine_label] = {
                    "route": route,
                    "constraint_status": plan.constraint_status,
                    "critical_demand": [round(v, 1) for v in critical_demand],
                    "solar_generation_forecast_w": [round(v, 1) for v in bundle.solar_generation.point],
                    "wind_generation_forecast_w": [round(v, 1) for v in bundle.wind_generation.point],
                    "demand_forecast_w": [round(v, 1) for v in bundle.demand.point],
                    "solar_used_w": plan.solar_used,
                    "wind_used_w": plan.wind_used,
                    "battery_charge_w": plan.battery_charge,
                    "battery_discharge_w": plan.battery_discharge,
                    "battery_soc_pct": plan.battery_soc,
                    "diesel_power_w": plan.diesel_power,
                    "load_served_w": plan.load_served,
                    "unmet_load_w": plan.unmet_load,
                    "renewable_curtailment_w": plan.renewable_curtailment,
                    "reserve_shortfall_w": plan.reserve_shortfall,
                    "j1_objective": plan.j1_objective, "j2_objective": plan.j2_objective,
                    "j3_objective": plan.j3_objective, "j4_objective": plan.j4_objective,
                    "sum_diesel_fuel_l": round(sum(
                        (base_fuel_lph if p > 0 else 0.0) + marginal_fuel_lpwh * p for p in plan.diesel_power
                    ), 4),
                }

            all_detail[origin_str] = origin_detail

            if "baseline" in all_detail[origin_str] and "stage8_1_corrected" in all_detail[origin_str]:
                b = all_detail[origin_str]["baseline"]
                s = all_detail[origin_str]["stage8_1_corrected"]
                if "diesel_power_w" in b and "diesel_power_w" in s:
                    print(f"{origin_str}: baseline_diesel_fuel_l={b['sum_diesel_fuel_l']} "
                          f"stage81_diesel_fuel_l={s['sum_diesel_fuel_l']} "
                          f"delta={round(s['sum_diesel_fuel_l']-b['sum_diesel_fuel_l'],4)}")
                else:
                    print(f"{origin_str}: route(s) not both NORMAL -- baseline={b.get('route')} stage81={s.get('route')}")

        out_path = THIS_DIR / "DIRECT_BUS_BAR_ISOLATION_DETAIL.json"
        with open(out_path, "w") as f:
            json.dump({
                "disclaimer": (
                    "DIRECT BUS-BAR PATHWAY ISOLATION. RESEARCH-ONLY per-hour detail for a "
                    "handful of representative origins, under the same ablated "
                    "(terminal_target_wh=40000 constant) configuration as "
                    "TERMINAL_ABLATION_RAW_RESULTS.json. Not a rerun of the full 347-origin "
                    "window. Not a production run. Not stakeholder-authorized."
                ),
                "ablated_terminal_target_wh": ABLATED_TERMINAL_TARGET_WH,
                "origins": CANDIDATE_ORIGINS,
                "detail": all_detail,
            }, f, indent=2)
        print(f"\nPer-hour detail written to {out_path}")
    finally:
        rfe.compute_terminal_target_wh = original_fn


if __name__ == "__main__":
    main()
