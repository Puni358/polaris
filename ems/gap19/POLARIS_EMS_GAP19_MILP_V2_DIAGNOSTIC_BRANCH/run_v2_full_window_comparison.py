#!/usr/bin/env python3
"""
MILP v2 -- CONTROLLED FULL-WINDOW comparison vs. the frozen GAP19 control.

Uses the same 347 real origins as the existing research harness
(stage8_1_full_37_feature_matrix_2024_CORRECTED.csv's forecast_start column -- the same
"347 clean origins across 2024" referenced throughout this codebase), the same production
pipeline pieces (H10RuntimeAdapter, EMSControlRouter, LocalBaselineForecastEngine,
system/config/*.yaml), and the same frozen terminal_target_wh formula
(compute_terminal_target_wh, imported unmodified from run_research_simulation.py) as
run_v2_real_data_comparison.py (the small 8-origin version of this same comparison).

For EVERY one of the 347 origins, BOTH optimizers receive a byte-identical ForecastBundle,
StationState, and config dict:
  1. the frozen GAP19HighsNativeOptimizer (control, UNMODIFIED)
  2. the research-only GAP19HighsNativeOptimizerMILPV2Research

This is a controlled OPTIMIZER-FORMULATION experiment (does GAP19 vs V2 differ, and how),
NOT a production deployment, NOT a forecast-engine ablation (one forecast engine, baseline,
used identically for both optimizer arms), and NOT a rerun of R1/R2's own baseline-vs-
Stage-8.1 forecast comparison. No code, config, model, or forecast engine is modified by
this script. GAP19 is called exactly as production code calls it.
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

from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.gap19_highs_native_milp_v2_research import (
    GAP19HighsNativeOptimizerMILPV2Research,
)
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from run_research_simulation import compute_terminal_target_wh  # frozen R1/R2 formula, imported not copied

MATRIX_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
PV_CONFIG_PATH = BASE / "system" / "config" / "solar_pv.yaml"

EPS = 1e-3


def arrsum(a):
    return round(sum(a), 4)


def diesel_startup_count(diesel_power):
    """Number of 0 -> >0 transitions in the 24h diesel_power series (startup events)."""
    count = 0
    prev_on = diesel_power[0] > EPS
    if prev_on:
        count += 1  # running from hour 0 counts as an active run segment start
    for t in range(1, 24):
        on = diesel_power[t] > EPS
        if on and not prev_on:
            count += 1
        prev_on = on
    return count


def diesel_on_hours(diesel_power):
    return sum(1 for p in diesel_power if p > EPS)


def plan_summary(plan, is_v2):
    d = plan.to_dict()
    s = {
        "constraint_status": d.get("constraint_status"),
        "j1_objective": d.get("j1_objective"),
        "j2_objective": d.get("j2_objective"),
        "j3_objective": d.get("j3_objective"),
        "j4_objective": d.get("j4_objective"),
        "sum_load_served": arrsum(d["load_served"]),
        "sum_unmet_load": arrsum(d["unmet_load"]),
        "sum_battery_charge": arrsum(d["battery_charge"]),
        "sum_battery_discharge": arrsum(d["battery_discharge"]),
        "soc_min": round(min(d["battery_soc"]), 2),
        "soc_max": round(max(d["battery_soc"]), 2),
        "sum_diesel_power": arrsum(d["diesel_power"]),
        "diesel_on_hours": diesel_on_hours(d["diesel_power"]),
        "diesel_startup_events": diesel_startup_count(d["diesel_power"]),
        "sum_curtailment": arrsum(d["renewable_curtailment"]),
        "max_energy_balance_error": round(max(abs(v) for v in d["energy_balance_errors"]), 6),
    }
    if is_v2:
        s["sum_load_served_essential"] = arrsum(d["load_served_essential"])
        s["sum_unmet_essential"] = arrsum(d["unmet_essential"])
    return s


def check_demand_accounting(plan, demand, is_v2):
    d = plan.to_dict()
    errs = []
    for t in range(24):
        total = d["load_served"][t] + d["unmet_load"][t]
        if is_v2:
            total += d["load_served_essential"][t]
        errs.append(abs(total - demand[t]))
    return round(max(errs), 6)


def check_essential_balance(plan, essential_demand):
    d = plan.to_dict()
    errs = []
    for t in range(24):
        total = d["load_served_essential"][t] + d["unmet_essential"][t]
        errs.append(abs(total - essential_demand[t]))
    return round(max(errs), 6)


def main():
    t_start = time.time()
    print("=" * 80)
    print("MILP v2 -- CONTROLLED FULL-WINDOW comparison (347 origins) vs frozen GAP19 control")
    print("Controlled optimizer-formulation experiment. NOT a production deployment.")
    print("NOT a forecast-engine ablation. GAP19/V2/config/forecast code UNMODIFIED.")
    print("=" * 80)

    df = pd.read_csv(MATRIX_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    origins = sorted(df["forecast_start"].unique())
    print(f"Loaded {len(origins)} origins from {MATRIX_PATH.name}")

    configs_base = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        cfg_file = BASE / "system" / "config" / f"{cfg_name}.yaml"
        if cfg_file.exists():
            with open(cfg_file) as f:
                configs_base[cfg_name] = yaml.safe_load(f)

    essential_max_power_w = float(
        configs_base.get("loads", {}).get("curtailable_loads", [{}])[0].get("max_power_w", 5000.0)
    )

    adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
    baseline_engine = LocalBaselineForecastEngine(PV_CONFIG_PATH)
    router = EMSControlRouter()
    gap19 = GAP19HighsNativeOptimizer()
    v2 = GAP19HighsNativeOptimizerMILPV2Research()

    flags = []
    all_results = {}
    route_counts = {"NORMAL": 0, "EMERGENCY": 0, "OTHER": 0}

    for i, origin in enumerate(origins):
        origin_str = origin.strftime("%Y-%m-%dT%H:%M:%SZ")
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

        bundle = baseline_engine.predict(st_k, {})

        critical_load_baseline_w = float(
            configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        critical_demand = [min(critical_load_baseline_w, d) for d in bundle.demand.point]
        demand = list(bundle.demand.point)
        essential_demand = [
            min(essential_max_power_w, max(0.0, demand[t] - critical_demand[t])) for t in range(24)
        ]

        terminal_target_wh = compute_terminal_target_wh(bundle)

        configs = dict(configs_base)
        configs["critical_demand_w"] = critical_demand
        configs["terminal_target_wh"] = terminal_target_wh

        assessment, route = router.evaluate_and_route(st_k, bundle, configs)
        route_counts[route] = route_counts.get(route, 0) + 1

        origin_result = {
            "route": route,
            "critical_demand_sum": arrsum(critical_demand),
            "essential_demand_sum": arrsum(essential_demand),
            "total_demand_sum": arrsum(demand),
            "terminal_target_wh": round(terminal_target_wh, 2),
        }

        if route != "NORMAL":
            origin_result["note"] = f"route='{route}' -- not in GAP19/V2 domain, not compared"
            all_results[origin_str] = origin_result
            continue

        gap19_plan = gap19.optimize(bundle, st_k, configs)
        v2_plan = v2.optimize(bundle, st_k, configs)

        gap19_summary = plan_summary(gap19_plan, is_v2=False)
        v2_summary = plan_summary(v2_plan, is_v2=True)

        gap19_infeasible = gap19_plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE")
        v2_infeasible = v2_plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE")
        if gap19_infeasible or v2_infeasible:
            flags.append({"origin": origin_str, "type": "INFEASIBILITY",
                          "gap19_status": gap19_plan.constraint_status, "v2_status": v2_plan.constraint_status})

        j1_match = abs((gap19_plan.j1_objective or 0) - (v2_plan.j1_objective or 0)) < EPS
        j2_match = abs((gap19_plan.j2_objective or 0) - (v2_plan.j2_objective or 0)) < EPS
        j3_match = abs((gap19_plan.j3_objective or 0) - (v2_plan.j3_objective or 0)) < EPS
        if not (j1_match and j2_match and j3_match):
            flags.append({"origin": origin_str, "type": "UNEXPECTED_OBJECTIVE_STAGE_DIVERGENCE",
                          "gap19_j1_j2_j3": [gap19_plan.j1_objective, gap19_plan.j2_objective, gap19_plan.j3_objective],
                          "v2_j1_j2_j3": [v2_plan.j1_objective, v2_plan.j2_objective, v2_plan.j3_objective]})

        gap19_demand_err = check_demand_accounting(gap19_plan, demand, is_v2=False)
        v2_demand_err = check_demand_accounting(v2_plan, demand, is_v2=True)
        v2_essential_err = check_essential_balance(v2_plan, essential_demand)
        if max(gap19_demand_err, v2_demand_err, v2_essential_err) > 1e-2:
            flags.append({"origin": origin_str, "type": "DEMAND_ACCOUNTING_ERROR",
                          "gap19_demand_err": gap19_demand_err, "v2_demand_err": v2_demand_err,
                          "v2_essential_err": v2_essential_err})

        if v2_summary["max_energy_balance_error"] > 1e-2 or gap19_summary["max_energy_balance_error"] > 1e-2:
            flags.append({"origin": origin_str, "type": "ENERGY_BALANCE_ERROR_EXCEEDS_TOLERANCE",
                          "gap19": gap19_summary["max_energy_balance_error"], "v2": v2_summary["max_energy_balance_error"]})

        diesel_sum_match = abs(gap19_summary["sum_diesel_power"] - v2_summary["sum_diesel_power"]) < 1.0
        if not diesel_sum_match:
            flags.append({"origin": origin_str, "type": "UNEXPECTED_DIESEL_AGGREGATE_DIVERGENCE",
                          "gap19_sum_diesel": gap19_summary["sum_diesel_power"], "v2_sum_diesel": v2_summary["sum_diesel_power"]})

        schedule_identical = (gap19_plan.diesel_power == v2_plan.diesel_power and
                               gap19_plan.battery_charge == v2_plan.battery_charge and
                               gap19_plan.battery_discharge == v2_plan.battery_discharge)

        origin_result.update({
            "gap19": gap19_summary,
            "v2": v2_summary,
            "j1_j2_j3_identical": j1_match and j2_match and j3_match,
            "diesel_sum_identical": diesel_sum_match,
            "demand_accounting": {"gap19_max_err_wh": gap19_demand_err, "v2_max_err_wh": v2_demand_err,
                                   "v2_essential_balance_max_err_wh": v2_essential_err},
            "dispatch_schedule_byte_identical": schedule_identical,
        })

        all_results[origin_str] = origin_result

        if (i + 1) % 25 == 0 or (i + 1) == len(origins):
            print(f"  ... {i+1}/{len(origins)} origins processed "
                  f"({route_counts.get('NORMAL',0)} NORMAL compared, {route_counts.get('EMERGENCY',0)} EMERGENCY, "
                  f"{len(flags)} flags so far) [{round(time.time()-t_start,1)}s elapsed]")

    out_path = THIS_DIR / "V2_FULL_WINDOW_COMPARISON_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": (
                "MILP v2 CONTROLLED FULL-WINDOW comparison (347 origins). Research-only. "
                "Controlled optimizer-formulation experiment comparing the REAL unmodified "
                "GAP19 optimizer against the research-only V2 optimizer, with byte-identical "
                "ForecastBundle/StationState/config at every origin. NOT a production "
                "deployment. NOT a forecast-engine ablation. No code, config, model, or "
                "forecast engine was modified. No human_execution_authorization sought or "
                "granted for any production use."
            ),
            "num_origins": len(origins),
            "route_counts": route_counts,
            "results": all_results,
            "flags": flags,
            "elapsed_seconds": round(time.time() - t_start, 1),
        }, f, indent=2)

    print(f"\nResults written to {out_path}")
    print(f"Route counts: {route_counts}")
    print(f"Flags raised: {len(flags)}")
    for fl in flags[:50]:
        print(f"  - {fl}")
    print(f"Elapsed: {round(time.time() - t_start, 1)}s")
    print("FULL-WINDOW COMPARISON COMPLETE. GAP19 untouched. No optimizer behavior changed.")


if __name__ == "__main__":
    main()
