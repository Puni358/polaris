#!/usr/bin/env python3
"""
POLARIS -- RT-01 Bounded Diagnostic: 168h Renewable-Utilization Gap Quantification
====================================================================================

Owner-authorized, bounded, ONE-TIME, read-only diagnostic (directive dated
2026-10-18, continuing directly from
ems/reports/rt01_runtime_fixes/RT01_69PCT_RENEWABLE_UTILIZATION_GAP_INVESTIGATION.md). Purpose: quantify the
already-CONFIRMED Option-D renewable-curtailment mechanism (OptionDFallbackSolver
has no code path to charge the battery from surplus renewables -- the only
charging path is gated on excess diesel; system/optimization/implementations/
option_d.py lines 127, 192-199) with one real, bounded 168-hour pipeline run
and full per-step telemetry, WITHOUT implementing any fix.

What this script is, precisely:
- A NEW, standalone, external harness, built by extending the exact pattern of
  research/rt01_diagnostics/trace_168h_endurance_scenario.py (same imports,
  same runner construction, same fixture, same single run_pipeline call). It
  IMPORTS the real, unmodified PROTECTED_FILES classes (EMSControlRouter,
  OptionDFallbackSolver, DigitalTwinSimulator via PolarisLocalRunner) and the
  real, unmodified, already-authorized test fixture function
  `_authorize_router_for_offline_runtime_test` from
  system/tests/test_offline_runtime.py.
- It runs the EXACT SAME call the existing 168h closure tests make
  (test_cumulative_physical_conservation_168h and its siblings in
  system/tests/test_offline_runtime.py):
      runner = PolarisLocalRunner(SYSTEM_DIR,
                                   scenario_filename="synthetic_168h_endurance_scenario.json",
                                   optimizer_type="milp")
      _authorize_router_for_offline_runtime_test(runner)
      report = runner.run_pipeline(steps_to_run=168)
  -- called exactly ONCE in this script, with no config/fixture/scenario
  changes of any kind.
- To capture per-step telemetry, this script monkey-patches four BOUND
  INSTANCE methods on the already-constructed runner's component objects
  (runner.router.evaluate_and_route, runner.optimizer.optimize,
  runner.option_d_solver.solve, runner.simulator.step) with thin wrappers
  that call the ORIGINAL, UNMODIFIED method, record its inputs/outputs into
  a local Python list, and return the original method's result completely
  unchanged. This is instance-level attribute shadowing in this script's own
  Python process; it does NOT edit, patch, or write to any file on disk.
  router.py, ecd.py, option_d.py, gap19_highs_native.py, simulator.py,
  runner.py, and manifest.py are never opened for writing by this script,
  and their on-disk SHA-256 hashes are verified unchanged before and after
  (printed to console and written into the output JSON's
  `protected_file_hash_manifest`).
- ARTIFACT ISOLATION (the one gap the prior trace script did not close --
  it disclosed, but did not prevent, regeneration of
  system/artifacts/{latest_dispatch_plan.json,latest_forecast_bundle.json,
  run_report.json} by the real run_pipeline() call). This script snapshots
  the bytes of those three files (if present) before the run and restores
  them byte-for-byte afterward, so the authoritative production artifacts
  are left exactly as found. This does not touch any PROTECTED_FILES source,
  test, config, scenario, or governance-register file -- only the three
  non-tracked, non-protected run_report/dispatch_plan/forecast_bundle JSON
  caches under system/artifacts/.

Strict boundaries honored:
- Exactly one run of run_pipeline(steps_to_run=168) on the unmodified
  synthetic_168h_endurance_scenario.json, with the unmodified
  _authorize_router_for_offline_runtime_test fixture.
- No production code, test, config, register, or protected file is edited.
- No fix, no renewable-to-battery charging implementation, no ECD/router
  behavior change. The "eligible for charging" figure below is a pure
  post-hoc arithmetic upper bound computed from the ALREADY-OBSERVED
  (unmodified) battery trajectory -- it does not simulate, assume, or claim
  what would happen if charging were actually implemented.
- No campaign, no diesel comparison, no full suite, no training/tuning, no
  sealed/blind data.
- Nothing staged, committed, or pushed by this script.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUTPUT_DIR = Path(__file__).resolve().parent

from system.runtime.runner import PolarisLocalRunner  # noqa: E402
from system.tests.test_offline_runtime import (  # noqa: E402
    SYSTEM_DIR,
    _authorize_router_for_offline_runtime_test,
)

# --- Section A: Protected-file hash manifest (verified before AND after) ---

PROTECTED_FILES_FOR_HASHING = [
    SYSTEM_DIR / "control" / "router.py",
    SYSTEM_DIR / "control" / "ecd.py",
    SYSTEM_DIR / "optimization" / "implementations" / "option_d.py",
    SYSTEM_DIR / "optimization" / "implementations" / "gap19_highs_native.py",
    SYSTEM_DIR / "simulation" / "simulator.py",
    SYSTEM_DIR / "runtime" / "runner.py",
    SYSTEM_DIR / "orchestration" / "manifest.py",
]


def sha256_of(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def hash_manifest() -> Dict[str, Optional[str]]:
    return {str(p.relative_to(REPO_ROOT)): sha256_of(p) for p in PROTECTED_FILES_FOR_HASHING}


# --- Section B: Artifact isolation (snapshot + restore, no overwrite left behind) ---

ARTIFACT_FILES_TO_ISOLATE = [
    "latest_dispatch_plan.json",
    "latest_forecast_bundle.json",
    "run_report.json",
]


def snapshot_artifacts(artifacts_dir: Path) -> Dict[str, Optional[bytes]]:
    snap: Dict[str, Optional[bytes]] = {}
    for name in ARTIFACT_FILES_TO_ISOLATE:
        p = artifacts_dir / name
        snap[name] = p.read_bytes() if p.exists() else None
    return snap


def restore_artifacts(artifacts_dir: Path, snap: Dict[str, Optional[bytes]]) -> Dict[str, bool]:
    """Restores each file to its pre-run byte content (or removes it if it did not
    exist before the run). Returns {name: restored_ok}."""
    result: Dict[str, bool] = {}
    for name, original_bytes in snap.items():
        p = artifacts_dir / name
        if original_bytes is None:
            if p.exists():
                p.unlink()
            result[name] = not p.exists()
        else:
            p.write_bytes(original_bytes)
            result[name] = p.read_bytes() == original_bytes
    return result


def build_instrumented_runner() -> "tuple[PolarisLocalRunner, List[Dict[str, Any]]]":
    """Builds the runner EXACTLY as the existing 168h tests do, then attaches
    non-invasive, instance-level telemetry wrappers. Returns (runner, trace)
    where `trace` is populated in place as run_pipeline executes."""

    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename="synthetic_168h_endurance_scenario.json",
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    trace: List[Dict[str, Any]] = []
    step_ctx: Dict[str, Any] = {"prev_route": None}

    # --- Battery / diesel config constants, read (not invented) from the
    # same runner.configs dict the real solvers/simulator themselves read,
    # used only to compute the post-hoc "eligible for charging" upper bound.
    bat_cfg = runner.configs.get("battery", {})
    capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
    max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
    max_chg_w = float(bat_cfg.get("max_charge_power_w", 50000.0))
    eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
    max_e_wh = capacity_wh * (max_soc_pct / 100.0)

    # --- 1. Router wrapper: capture pre-step state + assessment + route ---
    orig_evaluate_and_route = runner.router.evaluate_and_route

    def wrapped_evaluate_and_route(current_state, bundle, configs):
        assessment, route = orig_evaluate_and_route(current_state, bundle, configs)
        step_ctx["route"] = route
        step_ctx["route_changed_from_previous"] = (
            step_ctx.get("prev_route") is not None and step_ctx.get("prev_route") != route
        )
        step_ctx["operating_mode"] = assessment.operating_mode.value
        step_ctx["validity_status"] = assessment.validity_status.value
        step_ctx["battery_endurance_hours"] = assessment.battery_endurance_hours
        step_ctx["diesel_endurance_hours"] = assessment.diesel_endurance_hours
        step_ctx["battery_margin_hours"] = assessment.battery_margin_hours
        step_ctx["diesel_margin_hours"] = assessment.diesel_margin_hours
        step_ctx["preserved_resource"] = assessment.preserved_resource.value
        step_ctx["limiting_resource"] = assessment.limiting_resource.value
        step_ctx["fuel_before_l"] = current_state.diesel_fuel_remaining_liters
        step_ctx["soc_before_pct"] = current_state.battery_soc_pct
        step_ctx["battery_energy_wh_before"] = current_state.battery_energy_wh
        step_ctx["forecast_solar_h1_w"] = (
            float(bundle.solar_generation.point[0]) if bundle.solar_generation.point else None
        )
        step_ctx["forecast_wind_h1_w"] = (
            float(bundle.wind_generation.point[0]) if bundle.wind_generation.point else None
        )
        step_ctx["forecast_demand_h1_w"] = (
            float(bundle.demand.point[0]) if bundle.demand.point else None
        )
        return assessment, route

    runner.router.evaluate_and_route = wrapped_evaluate_and_route

    # --- 2. NORMAL-route optimizer wrapper ---
    orig_optimize = runner.optimizer.optimize
    optimizer_class_name = type(runner.optimizer).__name__

    def wrapped_optimize(bundle, current_state, configs):
        plan = orig_optimize(bundle, current_state, configs)
        step_ctx["solver"] = optimizer_class_name
        step_ctx["plan"] = plan
        step_ctx["solver_constraint_status"] = getattr(plan, "constraint_status", None)
        return plan

    runner.optimizer.optimize = wrapped_optimize

    # --- 3. EMERGENCY-route Option D wrapper ---
    orig_solve = runner.option_d_solver.solve
    option_d_class_name = type(runner.option_d_solver).__name__

    def wrapped_solve(assessment, bundle, current_state, configs):
        plan = orig_solve(assessment, bundle, current_state, configs)
        step_ctx["solver"] = option_d_class_name
        step_ctx["plan"] = plan
        step_ctx["solver_constraint_status"] = getattr(plan, "constraint_status", None)
        return plan

    runner.option_d_solver.solve = wrapped_solve

    # --- 4. Simulator wrapper: finalize the per-step record ---
    orig_step = runner.simulator.step

    def wrapped_step(current_state, dispatch_plan, actuals_next_step):
        state_after = orig_step(current_state, dispatch_plan, actuals_next_step)

        plan = step_ctx.get("plan")
        solar_h1 = float(plan.solar_used[0]) if plan is not None else None
        wind_h1 = float(plan.wind_used[0]) if plan is not None else None
        curtail_h1 = float(plan.renewable_curtailment[0]) if plan is not None else None
        chg_h1 = float(plan.battery_charge[0]) if plan is not None else None
        dis_h1 = float(plan.battery_discharge[0]) if plan is not None else None
        diesel_h1 = float(plan.diesel_power[0]) if plan is not None else None
        served_h1 = float(plan.load_served[0]) if plan is not None else None
        unmet_h1 = float(plan.unmet_load[0]) if plan is not None else None
        plan_soc_h1 = float(plan.battery_soc[0]) if plan is not None else None
        energy_balance_err_h1 = None
        if plan is not None and getattr(plan, "energy_balance_errors", None):
            try:
                energy_balance_err_h1 = float(plan.energy_balance_errors[0])
            except (IndexError, TypeError):
                energy_balance_err_h1 = None

        # Post-hoc eligibility upper bound, computed ONLY from the ALREADY-
        # OBSERVED (unmodified) pre-step battery energy and this step's
        # ALREADY-OBSERVED (unmodified) curtailment. Does not simulate a
        # counterfactual charging decision -- see report for why this is an
        # upper bound, not a guaranteed recoverable figure.
        headroom_dc_wh = max(0.0, max_e_wh - step_ctx.get("battery_energy_wh_before", 0.0))
        max_chg_avail_w = min(max_chg_w, headroom_dc_wh / eta_chg if eta_chg > 0 else 0.0)
        eligible_charge_w = (
            min(curtail_h1, max_chg_avail_w) if curtail_h1 is not None else None
        )

        record = {
            "step": len(trace),
            "timestamp": current_state.timestamp,
            "route": step_ctx.get("route"),
            "route_changed_from_previous": step_ctx.get("route_changed_from_previous"),
            "operating_mode": step_ctx.get("operating_mode"),
            "solver": step_ctx.get("solver"),
            "solver_constraint_status": step_ctx.get("solver_constraint_status"),
            "validity_status": step_ctx.get("validity_status"),
            "preserved_resource": step_ctx.get("preserved_resource"),
            "limiting_resource": step_ctx.get("limiting_resource"),
            "battery_endurance_hours": step_ctx.get("battery_endurance_hours"),
            "diesel_endurance_hours": step_ctx.get("diesel_endurance_hours"),
            "battery_margin_hours": step_ctx.get("battery_margin_hours"),
            "diesel_margin_hours": step_ctx.get("diesel_margin_hours"),
            "fuel_before_l": step_ctx.get("fuel_before_l"),
            "fuel_after_l": state_after.diesel_fuel_remaining_liters,
            "soc_before_pct": step_ctx.get("soc_before_pct"),
            "soc_after_pct": state_after.battery_soc_pct,
            "battery_energy_wh_before": step_ctx.get("battery_energy_wh_before"),
            "battery_energy_wh_after": state_after.battery_energy_wh,
            "forecast_solar_h1_w": step_ctx.get("forecast_solar_h1_w"),
            "forecast_wind_h1_w": step_ctx.get("forecast_wind_h1_w"),
            "forecast_demand_h1_w": step_ctx.get("forecast_demand_h1_w"),
            "forecast_renewable_avail_h1_w": (
                (step_ctx.get("forecast_solar_h1_w") or 0.0) + (step_ctx.get("forecast_wind_h1_w") or 0.0)
            ),
            "plan_solar_used_h1_w": solar_h1,
            "plan_wind_used_h1_w": wind_h1,
            "plan_renewable_used_h1_w": (
                (solar_h1 or 0.0) + (wind_h1 or 0.0) if solar_h1 is not None else None
            ),
            "plan_renewable_curtailment_h1_w": curtail_h1,
            "plan_battery_charge_h1_w": chg_h1,
            "plan_battery_discharge_h1_w": dis_h1,
            "plan_diesel_power_h1_w": diesel_h1,
            "plan_load_served_h1_w": served_h1,
            "plan_unmet_load_h1_w": unmet_h1,
            "plan_battery_soc_h1_pct_SOLVER_INTERNAL": plan_soc_h1,
            "plan_energy_balance_error_h1_w": energy_balance_err_h1,
            "actual_demand_w": actuals_next_step.get("actual_demand"),
            "actual_SW_IN": actuals_next_step.get("actual_SW_IN"),
            "actual_wind_generation_w": actuals_next_step.get("actual_wind_generation"),
            "eligible_for_charging_upper_bound_w": eligible_charge_w,
            "charge_headroom_dc_wh_before_step": headroom_dc_wh,
            "max_chg_avail_w_before_step": max_chg_avail_w,
        }
        trace.append(record)
        step_ctx["prev_route"] = step_ctx.get("route")
        for k in list(step_ctx.keys()):
            if k != "prev_route":
                del step_ctx[k]
        return state_after

    runner.simulator.step = wrapped_step

    return runner, trace


def main() -> None:
    print("=" * 80)
    print("POLARIS RT-01 BOUNDED DIAGNOSTIC -- 168h renewable-gap quantification run")
    print("=" * 80)

    pre_hashes = hash_manifest()
    print("Pre-run protected-file hashes recorded for", len(pre_hashes), "files.")

    artifacts_dir = SYSTEM_DIR / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifact_snapshot = snapshot_artifacts(artifacts_dir)

    runner, trace = build_instrumented_runner()

    exit_status = "OK"
    run_report: Optional[Dict[str, Any]] = None
    try:
        run_report = runner.run_pipeline(steps_to_run=168)
    except Exception as exc:  # pragma: no cover - diagnostic harness, report and re-raise info
        exit_status = f"EXCEPTION: {type(exc).__name__}: {exc}"
        raise
    finally:
        restore_result = restore_artifacts(artifacts_dir, artifact_snapshot)
        post_hashes = hash_manifest()

    hash_diffs = {
        f: (pre_hashes.get(f), post_hashes.get(f))
        for f in pre_hashes
        if pre_hashes.get(f) != post_hashes.get(f)
    }

    out_json = OUTPUT_DIR / "rt01_168h_renewable_gap_quantification_trace.json"
    out_csv = OUTPUT_DIR / "rt01_168h_renewable_gap_quantification_trace.csv"

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "run_report_summary": {
                    "timesteps_executed": run_report["timesteps_executed"] if run_report else None,
                    "execution_status": run_report["execution_status"] if run_report else exit_status,
                    "ems_evaluation": run_report["ems_evaluation"] if run_report else None,
                },
                "pre_run_protected_file_hashes": pre_hashes,
                "post_run_protected_file_hashes": post_hashes,
                "protected_file_hash_diffs": hash_diffs,
                "artifact_isolation_restore_result": restore_result,
                "per_step_trace": trace,
            },
            f,
            indent=2,
            default=str,
        )

    if trace:
        fieldnames = list(trace[0].keys())
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in trace:
                writer.writerow(row)

    # --- Console summary (also captured by the report) ---
    print(f"timesteps_executed: {run_report['timesteps_executed'] if run_report else 'N/A'}")
    print(f"execution_status:   {run_report['execution_status'] if run_report else exit_status}")
    print(f"protected_file_hash_diffs: {hash_diffs if hash_diffs else 'NONE (all 7 files unchanged)'}")
    print(f"artifact_isolation_restore_result: {restore_result}")

    if run_report is not None:
        ems_eval = run_report["ems_evaluation"]
        print(f"renewable_utilization_pct: {ems_eval.get('renewable_utilization_pct')}")

    from collections import Counter

    solver_counts = Counter(r["solver"] for r in trace)
    route_counts = Counter(r["route"] for r in trace)
    print(f"Route counts:  {dict(route_counts)}")
    print(f"Solver counts: {dict(solver_counts)}")

    option_d_steps = [r for r in trace if r["solver"] == "OptionDFallbackSolver"]
    if option_d_steps:
        step_indices = [r["step"] for r in option_d_steps]
        print(
            f"OptionDFallbackSolver active steps: {len(option_d_steps)} "
            f"(first={min(step_indices)}, last={max(step_indices)})"
        )
    else:
        print("OptionDFallbackSolver was never invoked in this run.")

    total_renewable_avail_wh = sum((r["forecast_renewable_avail_h1_w"] or 0.0) for r in trace)
    total_renewable_used_wh = sum((r["plan_renewable_used_h1_w"] or 0.0) for r in trace)
    total_curtailed_wh = sum((r["plan_renewable_curtailment_h1_w"] or 0.0) for r in trace)
    total_eligible_wh = sum((r["eligible_for_charging_upper_bound_w"] or 0.0) for r in trace)

    optd_curtailed_wh = sum((r["plan_renewable_curtailment_h1_w"] or 0.0) for r in option_d_steps)
    optd_eligible_wh = sum((r["eligible_for_charging_upper_bound_w"] or 0.0) for r in option_d_steps)

    print(f"Total H1 renewable available (Wh): {total_renewable_avail_wh:.2f}")
    print(f"Total H1 renewable used (Wh):      {total_renewable_used_wh:.2f}")
    print(f"Total H1 curtailed (Wh):            {total_curtailed_wh:.2f}")
    print(f"Conservation check (used+curtailed vs avail): "
          f"{(total_renewable_used_wh + total_curtailed_wh):.2f} vs {total_renewable_avail_wh:.2f}")
    print(f"Total eligible-for-charging upper bound, ALL steps (Wh): {total_eligible_wh:.2f}")
    print(f"Total curtailed DURING OptionD-active steps (Wh): {optd_curtailed_wh:.2f}")
    print(f"Total eligible-for-charging DURING OptionD-active steps (Wh): {optd_eligible_wh:.2f}")

    if total_renewable_avail_wh > 0:
        baseline_util = total_renewable_used_wh / total_renewable_avail_wh * 100.0
        upper_bound_util = (total_renewable_used_wh + total_eligible_wh) / total_renewable_avail_wh * 100.0
        optd_only_upper_bound_util = (
            (total_renewable_used_wh + optd_eligible_wh) / total_renewable_avail_wh * 100.0
        )
        print(f"Reproduced renewable_utilization_pct (from this trace): {baseline_util:.4f}")
        print(f"Upper-bound utilization if ALL eligible-for-charging Wh were recovered: {upper_bound_util:.4f}")
        print(f"Upper-bound utilization if ONLY OptionD-window eligible Wh recovered: {optd_only_upper_bound_util:.4f}")

    print(f"\nWrote: {out_json}")
    print(f"Wrote: {out_csv}")
    print("=" * 80)


if __name__ == "__main__":
    main()
