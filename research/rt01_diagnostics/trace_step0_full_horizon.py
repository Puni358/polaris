#!/usr/bin/env python3
"""
POLARIS -- RT-01 Bounded Diagnostic: Full 24-Hour Horizon Capture of the
Step-0 LocalMILPEnergyOptimizer Solve (168h endurance scenario)
====================================================================================

Owner-authorized, bounded, ONE-TIME, read-only diagnostic (directive dated
2026-10-18, "POLARIS -- RT-01 Full-Horizon MILP Diagnostic (Evidence Only)"),
continuing directly from RT01_STEP0_MILP_DISPATCH_ROOT_CAUSE_REVIEW.md. That
review found the step-0 decision (curtail all 33.1kW of forecast wind while
discharging the battery to serve demand) costs ~5.9x more in the solver's own
objective units than the "use wind directly" alternative, for the single
hour-0 term alone, but could not say whether hours 1-23 of the SAME 24-hour
receding-horizon solve justify this via legitimate multi-period shifting
(H1), expose a formulation defect (H2), or are merely exploiting a
miscalibrated 1000:1 curtailment:cycling penalty ratio with no real
multi-period benefit (H3) -- because the prior trace script
(trace_168h_endurance_scenario.py) only ever recorded index [0] of each
step's DispatchPlan, never the full horizon.

What this script is, precisely:
- A NEW, standalone, external harness, same non-invasive philosophy as
  trace_168h_endurance_scenario.py in this same directory (imports and calls
  the real, unmodified LocalMILPEnergyOptimizer.optimize(); no source file is
  edited; only in-process, instance/module-level attribute wrapping is used
  for telemetry, verified non-destructive by re-hashing on-disk files after
  the run).
- Unlike the prior script, it does NOT call runner.run_pipeline() at all,
  and therefore never touches runner.artifacts_dir (system/artifacts/*.json)
  -- production artifacts (latest_dispatch_plan.json,
  latest_forecast_bundle.json, run_report.json) are not written to, read
  from, or modified by this script. Instead it reproduces, by hand, from the
  PUBLIC methods of the same already-authorized PolarisLocalRunner instance,
  the EXACT sequence of calls run_pipeline() performs for step_idx == 0 only:
      1. initial_state = StationState(...)   [identical construction to
         runner.py lines 97-109, using the SAME runner.configs dict]
      2. runtime_context = runner.data_provider.get_runtime_state(0)
      3. bundle = runner.forecast_engine.predict(initial_state, runtime_context)
      4. assessment, route = runner.router.evaluate_and_route(initial_state, bundle, runner.configs)
         (recorded for confirmation only; NOT used to branch -- we call the
         MILP optimizer directly next regardless, because the prior passes'
         trace already established the step-0 route is NORMAL/MILP for this
         scenario, and this pass's job is to inspect that exact call's full
         horizon, not to re-derive routing.)
      5. plan = runner.optimizer.optimize(bundle, initial_state, runner.configs)
         <-- THE call under diagnosis. Called EXACTLY ONCE.
- To capture the full 24-hour MILP internals (not just the rounded,
  binaries-stripped DispatchPlan arrays), this script monkey-patches the
  module-level name `milp` inside the already-imported
  system.optimization.implementations.milp module (i.e.
  system.optimization.implementations.milp.milp, the scipy.optimize.milp
  function reference that LocalMILPEnergyOptimizer.optimize() calls
  internally at its line `res = milp(c=c, integrality=integrality,
  bounds=bounds, constraints=constraints)`). The wrapper records the exact
  c (cost) vector, integrality vector, Bounds, LinearConstraint(A, lhs, rhs)
  and the returned OptimizeResult (res.x, res.fun, res.status, res.message)
  into a module-level capture dict, then calls the ORIGINAL, UNMODIFIED
  scipy.optimize.milp function with the SAME arguments and returns ITS result
  completely unchanged. This is attribute shadowing in this script's own
  Python process only -- it does NOT edit milp.py (or any file) on disk, and
  the real HiGHS solver (via scipy) computes the real answer; we only
  observe it. milp.py's on-disk SHA-256 hash is verified identical before
  and after this script runs (see hash manifest in the JSON output and the
  companion report).
- The full 24-hour DispatchPlan arrays this optimizer already returns
  (solar_used, wind_used, battery_charge, battery_discharge, battery_soc,
  diesel_power, load_served, flexible_load_schedule, renewable_curtailment,
  unmet_load -- all length-24 lists; confirmed by reading milp.py lines
  366-399) are ALSO captured directly from the unmodified `plan` object, as
  an independent cross-check against the raw solver-vector decoding above.

Strict boundaries honored (see directive + RT01_STEP0_MILP_DISPATCH_ROOT_
CAUSE_REVIEW.md Section 6):
- Exactly ONE call to LocalMILPEnergyOptimizer.optimize() (equivalently, one
  call to the real scipy.optimize.milp solver), reproducing step 0 of the
  existing synthetic_168h_endurance_scenario.json / optimizer_type="milp"
  test configuration. No 168-step (or any multi-step) pipeline run.
- No production code, test, config, register, or protected file is edited.
  No parameter, threshold, or config value is changed from its on-disk value.
- No counterfactual/alternative solve is run (no re-solve with modified
  inputs/config) -- all H1/H2/H3 evidence below is derived purely by
  inspecting the single actual optimal solution already returned.
- No training/tuning, no campaign, no sealed/blind data.
- Nothing staged, committed, or pushed by this script.
- All outputs are written only under research/rt01_diagnostics/ in this
  repo; system/artifacts/*.json is never opened by this script (grep-
  confirmed below: this script contains no reference to `artifacts_dir`).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUTPUT_DIR = Path(__file__).resolve().parent

from system.runtime.runner import PolarisLocalRunner  # noqa: E402
from system.schemas.station_state import StationState  # noqa: E402
from system.tests.test_offline_runtime import (  # noqa: E402
    SYSTEM_DIR,
    _authorize_router_for_offline_runtime_test,
)
import system.optimization.implementations.milp as milp_module  # noqa: E402

SCENARIO_FILENAME = "synthetic_168h_endurance_scenario.json"

# ---------------------------------------------------------------------------
# 0. Pre-execution hash manifest of every file this diagnostic depends on or
#    whose immutability matters for governance (PROTECTED_FILES + milp.py +
#    the config files that supply the live penalty coefficients + the
#    scenario file). Recorded BEFORE any call is made.
# ---------------------------------------------------------------------------
HASH_TARGETS = [
    "system/optimization/implementations/milp.py",
    "system/optimization/implementations/gap19_highs_native.py",
    "system/optimization/implementations/option_d.py",
    "system/control/ecd.py",
    "system/control/router.py",
    "system/simulation/simulator.py",
    "system/runtime/runner.py",
    "system/orchestration/manifest.py",
    "system/config/optimizer.yaml",
    "system/config/battery.yaml",
    "system/config/diesel.yaml",
    "system/config/loads.yaml",
    "system/config/solar_pv.yaml",
    "system/config/station.yaml",
    f"system/data/scenarios/{SCENARIO_FILENAME}",
]


def sha256_of(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_hash_manifest() -> Dict[str, Optional[str]]:
    return {rel: sha256_of(REPO_ROOT / rel) for rel in HASH_TARGETS}


# ---------------------------------------------------------------------------
# 1. Non-invasive capture of the exact arguments/result of the single
#    scipy.optimize.milp call made inside LocalMILPEnergyOptimizer.optimize().
# ---------------------------------------------------------------------------
_capture: Dict[str, Any] = {}
_orig_scipy_milp = milp_module.milp


def _wrapped_scipy_milp(c=None, *, integrality=None, bounds=None, constraints=None, **kwargs):
    res = _orig_scipy_milp(
        c=c, integrality=integrality, bounds=bounds, constraints=constraints, **kwargs
    )
    _capture["c"] = list(c)
    _capture["integrality"] = list(integrality) if integrality is not None else None
    _capture["lb"] = list(bounds.lb) if bounds is not None else None
    _capture["ub"] = list(bounds.ub) if bounds is not None else None
    _capture["constraints_lb"] = list(constraints.lb)
    _capture["constraints_ub"] = list(constraints.ub)
    _capture["A"] = constraints.A.tolist()
    _capture["res_x"] = list(res.x) if res.x is not None else None
    _capture["res_fun"] = float(res.fun) if res.fun is not None else None
    _capture["res_status"] = int(res.status)
    _capture["res_message"] = str(res.message)
    _capture["res_success"] = bool(res.success)
    return res


def main() -> None:
    pre_hashes = build_hash_manifest()

    # --- Build the runner EXACTLY as the existing 168h/offline tests do ---
    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename=SCENARIO_FILENAME,
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    optimizer_class_name = type(runner.optimizer).__name__
    assert optimizer_class_name == "LocalMILPEnergyOptimizer", (
        f"Expected LocalMILPEnergyOptimizer, got {optimizer_class_name}"
    )

    # --- Reproduce run_pipeline()'s step_idx==0 setup verbatim (runner.py
    # lines 97-109), reading the SAME runner.configs dict the real pipeline
    # reads. This does not call run_pipeline(), so runner.artifacts_dir is
    # never written. ---
    first_step = runner.data_provider.timesteps[0]
    initial_state = StationState(
        timestamp=first_step["timestamp"],
        battery_soc_pct=runner.configs.get("battery", {}).get("initial_soc_pct", 50.0),
        battery_energy_wh=runner.configs.get("battery", {}).get("capacity_wh", 200000.0)
        * (runner.configs.get("battery", {}).get("initial_soc_pct", 50.0) / 100.0),
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=first_step["actual_SW_IN"],
        last_observed_demand=first_step["actual_demand"],
        last_observed_wind_generation=first_step["actual_wind_generation"],
        diesel_fuel_remaining_liters=runner.configs.get("diesel", {}).get("initial_fuel_l", 100.0),
    )

    runtime_context = runner.data_provider.get_runtime_state(0)
    bundle = runner.forecast_engine.predict(initial_state, runtime_context)

    # Confirm routing (observation only -- NOT used to branch; we know from
    # the prior bounded trace that step 0 of this scenario routes NORMAL and
    # is served by LocalMILPEnergyOptimizer).
    assessment, route = runner.router.evaluate_and_route(initial_state, bundle, runner.configs)

    # --- Monkey-patch the scipy solver reference used INSIDE milp.py, call
    # the real, unmodified optimize() exactly once, then restore. ---
    milp_module.milp = _wrapped_scipy_milp
    try:
        plan = runner.optimizer.optimize(bundle, initial_state, runner.configs)
    finally:
        milp_module.milp = _orig_scipy_milp

    post_hashes = build_hash_manifest()
    hash_diffs = {k: (pre_hashes[k], post_hashes[k]) for k in HASH_TARGETS if pre_hashes[k] != post_hashes[k]}

    # -----------------------------------------------------------------
    # 2. Decode the raw solver vectors into the full per-timestep family
    #    breakdown, cross-checked against the DispatchPlan's own arrays.
    # -----------------------------------------------------------------
    K = 15
    H = 24
    sol = _capture["res_x"]
    c = _capture["c"]

    bat_cfg = runner.configs.get("battery", {})
    capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
    max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
    min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))

    solar_gen = bundle.solar_generation.point
    wind_gen = bundle.wind_generation.point
    demand = bundle.demand.point

    horizon_rows = []
    totals = {
        "curt_sol_cost": 0.0, "curt_wind_cost": 0.0,
        "chg_cost": 0.0, "dis_cost": 0.0,
        "diesel_marginal_cost": 0.0, "diesel_base_cost": 0.0,
        "startup_cost": 0.0, "unmet_cost": 0.0,
    }

    for t in range(H):
        base = t * K
        raw = sol[base: base + K]
        idx_cost = {
            "curt_sol": c[base + 2] * raw[2],
            "curt_wind": c[base + 3] * raw[3],
            "chg": c[base + 4] * raw[4],
            "dis": c[base + 5] * raw[5],
            "diesel_marginal": c[base + 7] * raw[7],
            "unmet": c[base + 9] * raw[9],
            "diesel_base": c[base + 13] * raw[13],
            "startup": c[base + 14] * raw[14],
        }
        totals["curt_sol_cost"] += idx_cost["curt_sol"]
        totals["curt_wind_cost"] += idx_cost["curt_wind"]
        totals["chg_cost"] += idx_cost["chg"]
        totals["dis_cost"] += idx_cost["dis"]
        totals["diesel_marginal_cost"] += idx_cost["diesel_marginal"]
        totals["diesel_base_cost"] += idx_cost["diesel_base"]
        totals["startup_cost"] += idx_cost["startup"]
        totals["unmet_cost"] += idx_cost["unmet"]

        soc_pct_raw = (raw[6] / capacity_wh) * 100.0

        horizon_rows.append({
            "t": t,
            "forecast_solar_w": round(float(solar_gen[t]), 2),
            "forecast_wind_w": round(float(wind_gen[t]), 2),
            "forecast_demand_w": round(float(demand[t]), 2),
            "forecast_renewable_surplus_w": round(float(solar_gen[t] + wind_gen[t] - demand[t]), 2),
            "raw_p_sol_used": round(raw[0], 4),
            "raw_p_wind_used": round(raw[1], 4),
            "raw_p_curt_sol": round(raw[2], 4),
            "raw_p_curt_wind": round(raw[3], 4),
            "raw_p_chg": round(raw[4], 4),
            "raw_p_dis": round(raw[5], 4),
            "raw_E_next_wh": round(raw[6], 4),
            "raw_soc_pct": round(soc_pct_raw, 4),
            "raw_p_diesel": round(raw[7], 4),
            "raw_p_served": round(raw[8], 4),
            "raw_p_unmet": round(raw[9], 4),
            "raw_p_flex": round(raw[10], 4),
            "raw_u_chg": round(raw[11], 6),
            "raw_u_dis": round(raw[12], 6),
            "raw_u_diesel": round(raw[13], 6),
            "raw_v_start": round(raw[14], 6),
            "cost_curt_sol": round(idx_cost["curt_sol"], 6),
            "cost_curt_wind": round(idx_cost["curt_wind"], 6),
            "cost_chg": round(idx_cost["chg"], 6),
            "cost_dis": round(idx_cost["dis"], 6),
            "cost_diesel_marginal": round(idx_cost["diesel_marginal"], 6),
            "cost_diesel_base": round(idx_cost["diesel_base"], 6),
            "cost_startup": round(idx_cost["startup"], 6),
            "cost_unmet": round(idx_cost["unmet"], 6),
            # Cross-check against the DispatchPlan object's own (rounded,
            # binary-snapped) arrays:
            "plan_solar_used": plan.solar_used[t],
            "plan_wind_used": plan.wind_used[t],
            "plan_battery_charge": plan.battery_charge[t],
            "plan_battery_discharge": plan.battery_discharge[t],
            "plan_battery_soc_pct": plan.battery_soc[t],
            "plan_diesel_power": plan.diesel_power[t],
            "plan_load_served": plan.load_served[t],
            "plan_renewable_curtailment": plan.renewable_curtailment[t],
            "plan_unmet_load": plan.unmet_load[t],
            "plan_flexible_load": plan.flexible_load_schedule[t],
            "energy_balance_error": plan.energy_balance_errors[t],
        })

    objective_breakdown_total = sum(totals.values())

    # -----------------------------------------------------------------
    # 3. H1/H2/H3 evidence computations (all derived from the SINGLE
    #    actual optimal solution above -- no counterfactual re-solve).
    # -----------------------------------------------------------------
    total_curtailment_wh = sum(r["plan_renewable_curtailment"] for r in horizon_rows)
    curtailment_after_t0_wh = sum(r["plan_renewable_curtailment"] for r in horizon_rows[1:])
    any_charge_after_t0 = any(r["plan_battery_charge"] > 0.0 for r in horizon_rows[1:])
    charge_events = [r for r in horizon_rows[1:] if r["plan_battery_charge"] > 0.0]
    max_soc_reached_pct = max(r["plan_battery_soc_pct"] for r in horizon_rows)
    soc_ceiling_pct = max_soc_pct
    soc_floor_pct = min_soc_pct
    min_soc_reached_pct = min(r["plan_battery_soc_pct"] for r in horizon_rows)
    hours_at_or_near_ceiling = [
        r["t"] for r in horizon_rows if r["plan_battery_soc_pct"] >= soc_ceiling_pct - 0.5
    ]
    final_soc_pct = horizon_rows[-1]["plan_battery_soc_pct"]
    initial_soc_pct = initial_state.battery_soc_pct

    # Hour-0 excess cost (as computed in the root-cause review, Section 1)
    t0 = horizon_rows[0]
    actual_t0_cost = t0["cost_curt_wind"] + t0["cost_curt_sol"] + t0["cost_dis"] + t0["cost_chg"]
    # Locally-cheaper alternative at t0: use wind directly for demand, curtail only the surplus
    curt_penalty = float(
        runner.configs.get("optimizer", {}).get("weights", {}).get("renewable_curtailment_penalty", 0.001)
    )
    wind_fc = t0["forecast_wind_w"]
    demand_fc = t0["forecast_demand_w"]
    alt_curtail_wh = max(0.0, wind_fc - demand_fc)
    alt_t0_cost = curt_penalty * alt_curtail_wh
    hour0_excess_cost = actual_t0_cost - alt_t0_cost

    # Does the horizon ever reach the SOC ceiling? (tests whether freeing
    # battery headroom at t0 was ever actually capacity-binding later)
    ceiling_ever_binding = max_soc_reached_pct >= soc_ceiling_pct - 0.5

    evidence = {
        "total_curtailment_wh_24h": round(total_curtailment_wh, 2),
        "curtailment_wh_hours_1_to_23": round(curtailment_after_t0_wh, 2),
        "any_battery_charge_after_t0": any_charge_after_t0,
        "num_charge_events_after_t0": len(charge_events),
        "charge_event_hours": [r["t"] for r in charge_events],
        "max_soc_pct_reached_over_horizon": round(max_soc_reached_pct, 2),
        "min_soc_pct_reached_over_horizon": round(min_soc_reached_pct, 2),
        "soc_ceiling_pct_config": soc_ceiling_pct,
        "soc_floor_pct_config": soc_floor_pct,
        "soc_ceiling_ever_binding": ceiling_ever_binding,
        "hours_at_or_near_ceiling": hours_at_or_near_ceiling,
        "initial_soc_pct": initial_soc_pct,
        "final_soc_pct_hour24": final_soc_pct,
        "net_soc_change_pct": round(final_soc_pct - initial_soc_pct, 2),
        "hour0_actual_cost_usd": round(actual_t0_cost, 2),
        "hour0_alt_use_wind_directly_cost_usd": round(alt_t0_cost, 2),
        "hour0_excess_cost_usd": round(hour0_excess_cost, 2),
    }

    # -----------------------------------------------------------------
    # 4. Write outputs
    # -----------------------------------------------------------------
    out_json = OUTPUT_DIR / "rt01_step0_full_horizon_trace.json"
    out_csv = OUTPUT_DIR / "rt01_step0_full_horizon_trace.csv"

    payload = {
        "scenario_filename": SCENARIO_FILENAME,
        "optimizer_class": optimizer_class_name,
        "route_confirmed": route,
        "operating_mode_confirmed": assessment.operating_mode.value,
        "initial_state": {
            "timestamp": initial_state.timestamp,
            "battery_soc_pct": initial_state.battery_soc_pct,
            "battery_energy_wh": initial_state.battery_energy_wh,
            "diesel_running": initial_state.diesel_running,
            "diesel_fuel_remaining_liters": initial_state.diesel_fuel_remaining_liters,
            "last_observed_solar_irradiance": initial_state.last_observed_solar_irradiance,
            "last_observed_demand": initial_state.last_observed_demand,
            "last_observed_wind_generation": initial_state.last_observed_wind_generation,
        },
        "config_values_used": {
            "renewable_curtailment_penalty_per_wh": curt_penalty,
            "deg_penalty_per_wh": float(bat_cfg.get("deg_penalty_per_wh", 0.00005)),
            "max_soc_pct": max_soc_pct,
            "min_soc_pct": min_soc_pct,
            "max_charge_power_w": float(bat_cfg.get("max_charge_power_w", 50000.0)),
            "max_discharge_power_w": float(bat_cfg.get("max_discharge_power_w", 50000.0)),
            "charge_efficiency": float(bat_cfg.get("charge_efficiency", 0.92)),
            "discharge_efficiency": float(bat_cfg.get("discharge_efficiency", 0.92)),
        },
        "solver": {
            "res_success": _capture["res_success"],
            "res_status": _capture["res_status"],
            "res_message": _capture["res_message"],
            "res_fun_total_objective": _capture["res_fun"],
            "plan_objective_value_reported": plan.objective_value,
            "plan_constraint_status": plan.constraint_status,
            "objective_breakdown_total_reconstructed": round(objective_breakdown_total, 6),
            "objective_breakdown_matches_res_fun": abs(objective_breakdown_total - _capture["res_fun"]) < 1e-3,
        },
        "objective_breakdown_by_family_24h_total_usd": {k: round(v, 4) for k, v in totals.items()},
        "evidence_for_h1_h2_h3": evidence,
        "horizon_24h": horizon_rows,
        "pre_execution_hash_manifest": pre_hashes,
        "post_execution_hash_manifest": post_hashes,
        "hash_diffs_detected": hash_diffs,
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    import csv
    fieldnames = list(horizon_rows[0].keys())
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in horizon_rows:
            writer.writerow(row)

    # --- Console summary ---
    print("=" * 80)
    print("POLARIS RT-01 BOUNDED DIAGNOSTIC -- step-0 FULL 24h horizon trace")
    print("=" * 80)
    print(f"route_confirmed: {route}   solver: {optimizer_class_name}")
    print(f"res_success: {_capture['res_success']}   res_status: {_capture['res_status']}")
    print(f"res_fun (total objective): {_capture['res_fun']}")
    print(f"reconstructed objective breakdown total: {objective_breakdown_total:.6f}  "
          f"(matches res_fun: {abs(objective_breakdown_total - _capture['res_fun']) < 1e-3})")
    print(f"objective_breakdown_by_family: {json.dumps({k: round(v,4) for k,v in totals.items()}, indent=2)}")
    print(f"evidence: {json.dumps(evidence, indent=2)}")
    print(f"hash_diffs_detected (should be empty): {hash_diffs}")
    print(f"\nWrote: {out_json}")
    print(f"Wrote: {out_csv}")
    print("=" * 80)


if __name__ == "__main__":
    main()
