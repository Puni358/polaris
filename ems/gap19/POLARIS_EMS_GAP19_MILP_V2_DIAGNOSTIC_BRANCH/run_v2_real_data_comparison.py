#!/usr/bin/env python3
"""
MILP v2 -- SMALL REAL-DATA comparison against the frozen GAP19 control.

Uses the REAL, UNMODIFIED production pipeline pieces (H10RuntimeAdapter, EMSControlRouter,
LocalBaselineForecastEngine, GAP19HighsNativeOptimizer, system/config/*.yaml) exactly as the
existing diagnostic-branch harness (run_small_diagnostic_replay.py) does -- same imports, same
station-state construction, same critical_demand_w / terminal_target_wh derivation
(compute_terminal_target_wh imported unmodified from the frozen R1/R2 script). The ONLY new
code here is: (a) also calling the research-only V2 optimizer
(GAP19HighsNativeOptimizerMILPV2Research) with the byte-identical bundle/state/config GAP19
received, and (b) a comparison/diff of the two DispatchPlans.

NOT a rerun of the full 347-origin R1/R2 experiment. NOT a change to GAP19, V2, or any frozen
research assumption. NOT a production run (no human_execution_authorization).

Origins (8, hand-picked for seasonal/operational variety across the real 347-origin set):
  - 2024-01-25: deep winter, near-zero solar (polar night regime)
  - 2024-03-20: spring equinox, moderate solar
  - 2024-06-01: near-solstice, high solar (also in R1/R2's own 5-origin set)
  - 2024-06-19: known large-diesel-increase origin, J2 non-binding (from diagnostic branch)
  - 2024-08-12: known large-diesel-increase origin, J2-binding (from diagnostic branch)
  - 2024-09-22: autumn equinox, moderate solar
  - 2024-11-15: late autumn, low solar
  - 2024-12-21: winter solstice, minimal/no solar (most extreme low-solar case)
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

from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.gap19_highs_native_milp_v2_research import (
    GAP19HighsNativeOptimizerMILPV2Research,
)
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from run_research_simulation import compute_terminal_target_wh  # frozen R1/R2 formula, imported not copied

FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
PV_CONFIG_PATH = BASE / "system" / "config" / "solar_pv.yaml"

ORIGINS = [
    "2024-01-25T00:00:00Z",
    "2024-03-20T00:00:00Z",
    "2024-06-01T00:00:00Z",
    "2024-06-19T00:00:00Z",
    "2024-08-12T00:00:00Z",
    "2024-09-22T00:00:00Z",
    "2024-11-15T00:00:00Z",
    "2024-12-21T00:00:00Z",
]

EPS = 1e-3


def arrsum(a):
    return round(sum(a), 4)


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
        "sum_curtailment": arrsum(d["renewable_curtailment"]),
        "max_energy_balance_error": round(max(abs(v) for v in d["energy_balance_errors"]), 6),
    }
    if is_v2:
        s["sum_load_served_essential"] = arrsum(d["load_served_essential"])
        s["sum_unmet_essential"] = arrsum(d["unmet_essential"])
    return s


def check_demand_accounting(plan, demand, is_v2):
    """Per-hour: served [+ served_essential] + unmet == demand. Returns max abs error."""
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
    print("=" * 80)
    print("MILP v2 -- SMALL REAL-DATA comparison vs frozen GAP19 control")
    print("NOT the 347-origin experiment. NOT a change to GAP19, V2, or frozen assumptions.")
    print("=" * 80)

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
    option_d_solver = OptionDFallbackSolver()

    flags = []  # any infeasibility / unexpected divergence / checkpoint-assumption violation
    all_results = {}

    for origin_str in ORIGINS:
        origin = pd.Timestamp(origin_str)
        index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)

        # Identical warmed-up (non-cold-start) station state for BOTH optimizers at this origin
        # -- same construction the existing diagnostic-branch harness uses, so the router sees
        # NORMAL conditions consistent with R1/R2's own methodology.
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

        origin_result = {
            "origin": origin_str,
            "route": route,
            "critical_demand_sum": arrsum(critical_demand),
            "essential_demand_sum": arrsum(essential_demand),
            "total_demand_sum": arrsum(demand),
            "terminal_target_wh": round(terminal_target_wh, 2),
        }

        if route != "NORMAL":
            origin_result["note"] = (
                f"Router selected route='{route}' (not NORMAL) -- GAP19/V2 are NOT in this "
                f"path's domain (OptionDFallbackSolver handles EMERGENCY; router itself handles "
                f"UNKNOWN_INVALID). Neither optimizer was called for this origin, by design -- "
                f"this is not a comparison gap."
            )
            print(f"{origin_str}: route={route} -- GAP19/V2 comparison N/A (not NORMAL route)")
            all_results[origin_str] = origin_result
            continue

        gap19_plan = gap19.optimize(bundle, st_k, configs)
        v2_plan = v2.optimize(bundle, st_k, configs)

        gap19_summary = plan_summary(gap19_plan, is_v2=False)
        v2_summary = plan_summary(v2_plan, is_v2=True)

        gap19_infeasible = gap19_plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE")
        v2_infeasible = v2_plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE")
        if gap19_infeasible or v2_infeasible:
            flags.append({
                "origin": origin_str, "type": "INFEASIBILITY",
                "gap19_status": gap19_plan.constraint_status, "v2_status": v2_plan.constraint_status,
            })

        # Expected invariant: J1 (critical), J2 (reserve), J3 (diesel fuel) must be IDENTICAL
        # between GAP19 and V2 -- the Essential tier only touches J4. Any deviation here is an
        # unexpected divergence / possible checkpoint-assumption violation.
        j1_match = abs((gap19_plan.j1_objective or 0) - (v2_plan.j1_objective or 0)) < EPS
        j2_match = abs((gap19_plan.j2_objective or 0) - (v2_plan.j2_objective or 0)) < EPS
        j3_match = abs((gap19_plan.j3_objective or 0) - (v2_plan.j3_objective or 0)) < EPS
        if not (j1_match and j2_match and j3_match):
            flags.append({
                "origin": origin_str, "type": "UNEXPECTED_OBJECTIVE_STAGE_DIVERGENCE",
                "gap19_j1_j2_j3": [gap19_plan.j1_objective, gap19_plan.j2_objective, gap19_plan.j3_objective],
                "v2_j1_j2_j3": [v2_plan.j1_objective, v2_plan.j2_objective, v2_plan.j3_objective],
            })

        gap19_demand_err = check_demand_accounting(gap19_plan, demand, is_v2=False)
        v2_demand_err = check_demand_accounting(v2_plan, demand, is_v2=True)
        v2_essential_err = check_essential_balance(v2_plan, essential_demand)
        if max(gap19_demand_err, v2_demand_err, v2_essential_err) > 1e-2:
            flags.append({
                "origin": origin_str, "type": "DEMAND_ACCOUNTING_ERROR",
                "gap19_demand_err": gap19_demand_err, "v2_demand_err": v2_demand_err,
                "v2_essential_err": v2_essential_err,
            })

        # Checkpoint-assumption spot checks for this origin.
        if v2_summary["max_energy_balance_error"] > 1e-2 or gap19_summary["max_energy_balance_error"] > 1e-2:
            flags.append({"origin": origin_str, "type": "ENERGY_BALANCE_ERROR_EXCEEDS_TOLERANCE",
                           "gap19": gap19_summary["max_energy_balance_error"],
                           "v2": v2_summary["max_energy_balance_error"]})

        schedule_identical = (gap19_plan.diesel_power == v2_plan.diesel_power and
                               gap19_plan.battery_charge == v2_plan.battery_charge and
                               gap19_plan.battery_discharge == v2_plan.battery_discharge)

        origin_result.update({
            "gap19": gap19_summary,
            "v2": v2_summary,
            "j1_j2_j3_identical": j1_match and j2_match and j3_match,
            "demand_accounting": {"gap19_max_err_wh": gap19_demand_err, "v2_max_err_wh": v2_demand_err,
                                   "v2_essential_balance_max_err_wh": v2_essential_err},
            "dispatch_schedule_byte_identical": schedule_identical,
        })

        print(f"{origin_str}: route={route} GAP19_status={gap19_plan.constraint_status} "
              f"V2_status={v2_plan.constraint_status} J1J2J3_match={j1_match and j2_match and j3_match} "
              f"schedule_identical={schedule_identical} "
              f"v2_unmet_essential_sum={v2_summary['sum_unmet_essential']}")

        all_results[origin_str] = origin_result

    out_path = THIS_DIR / "V2_REAL_DATA_COMPARISON_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": (
                "MILP v2 SMALL REAL-DATA comparison. Research-only. Uses the REAL unmodified "
                "GAP19 optimizer and the real H1.0 fixture data via the same production pipeline "
                "pieces (adapter, router, baseline forecast engine, system/config/*.yaml) the "
                "existing diagnostic-branch harness uses. NOT a rerun of the 347-origin R1/R2 "
                "experiment. NOT a change to GAP19, V2, or any frozen research assumption. "
                "No human_execution_authorization sought or granted."
            ),
            "origins": ORIGINS,
            "results": all_results,
            "flags": flags,
        }, f, indent=2)

    print(f"\nResults written to {out_path}")
    print(f"Flags raised: {len(flags)}")
    for fl in flags:
        print(f"  - {fl}")
    print("REAL-DATA COMPARISON COMPLETE. GAP19 untouched. No optimizer behavior changed.")


if __name__ == "__main__":
    main()
