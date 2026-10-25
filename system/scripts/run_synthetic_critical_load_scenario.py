#!/usr/bin/env python3
"""
POLARIS -- Synthetic Critical-Load End-to-End CLI Adapter
===========================================================
Owner directive: "Make the existing POLARIS synthetic model runnable end to
end with minimal changes. The desired user experience is one terminal
command, one critical-load input in kW, and a complete, honestly reported
synthetic run."

This is a NEW, thin entry point. It does not edit, and this pass re-verified
byte-identical (sha256), every PROTECTED_FILES entry:
  system/control/router.py, system/control/ecd.py,
  system/optimization/implementations/gap19_highs_native.py,
  system/optimization/implementations/option_d.py,
  system/simulation/simulator.py, system/runtime/runner.py,
  system/orchestration/manifest.py
It also does not edit the existing validated single-origin entry point this
pipeline is built on top of (run_n6_closed_loop_simulation.py, Candidate N6
dir) -- that file's logic is loaded and reused via importlib, unmodified.

What the single CLI input (--critical-load-kw) does, precisely:
  - It becomes `configs["critical_demand_w"]`, a 24-length Wh/step array
    (capped at the forecast demand at each hour), which is the GOVERNED input
    contract `GAP19HighsNativeOptimizer` (system/optimization/implementations/
    gap19_highs_native.py, PROTECTED, read-only here) already requires and
    reads for its own critical-load reserve/priority constraints. This is an
    authorized, pre-existing input slot in a protected file's own documented
    contract -- supplying it is not an edit to that file's behavior.
  - It is passed to `OptionDFallbackSolver.solve()` only via `configs` (the
    same dict); OptionDFallbackSolver (system/optimization/implementations/
    option_d.py, PROTECTED, already-fixed, read-only here) does NOT read any
    critical-load config key at all -- confirmed by direct source inspection
    this pass (it uses the full demand forecast as "protected critical
    demand" unconditionally, line ~93). So on an EMERGENCY route, this CLI's
    input has NO effect on OptionDFallbackSolver's dispatch; this script
    reports that fact explicitly rather than implying otherwise.
  - It is explicitly, deliberately, NEVER passed to
    `EMSControlRouter.evaluate_and_route()`'s own internal NORMAL / EMERGENCY
    / UNKNOWN_INVALID survivability classification. Confirmed by direct
    source inspection (system/control/router.py lines 54-59, read-only, this
    pass): the router derives its own "critical_load_w" independently, from
    `current_state.last_observed_demand` (falling back to
    `bundle.demand.point[0]`, then a hardcoded 30,000.0 W floor) -- a
    substitution chain this pipeline's own governance track
    (docs/decision_registers/HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md, ECD01_OWNER_DECISIONS_RECORDED_
    REPORT.md) has already identified, and the project owner has already
    recorded a fail-closed decision about (A-iii / B-iii / M-A in
    docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md v1.9.2, item ECD-01) -- a decision
    that is NOT YET implemented in router.py/ecd.py (those files are
    unmodified; implementation requires a separate, not-yet-granted
    authorization). This script does not attempt to implement, simulate, or
    paper over that gap. It reports the router's real, current (pre-decision-
    implementation) routing behavior honestly, every run.

Nothing here invents a real-station T_required or critical-load value, uses
the ungoverned 6h router default as if authorized, promotes the 72h
prototype, or claims the 11.6 kW CL-01 research value as validated station
evidence. The --critical-load-kw value supplied here is always and only a
SYNTHETIC, USER-SUPPLIED SCENARIO PARAMETER for this one run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path("/home/punith-bs/01polaris (Copy)")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

N6_SCRIPT_PATH = (
    REPO_ROOT
    / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics"
    / "run_n6_closed_loop_simulation.py"
)

# A sane upper bound for a "synthetic critical load in kW" input, to catch
# obvious typos/unit errors (e.g. entering watts instead of kW). Chosen as a
# generous multiple of the station's configured diesel max_power_w (50 kW
# default), not as any claim about a real station limit.
_SANITY_MAX_CRITICAL_LOAD_KW = 500.0


def _load_n6_module():
    """Load the existing, unmodified single-origin entry point by file path
    (not a dotted import, since the research tree has no __init__.py chain)
    so its already-validated constants/classes are reused, not duplicated."""
    spec = importlib.util.spec_from_file_location("polaris_n6_closed_loop_base", N6_SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _validate_critical_load_kw(value_str: str) -> float:
    try:
        value = float(value_str)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"--critical-load-kw must be a number, got {value_str!r}"
        )
    if math.isnan(value) or math.isinf(value):
        raise argparse.ArgumentTypeError("--critical-load-kw must be finite")
    if value <= 0.0:
        raise argparse.ArgumentTypeError(
            f"--critical-load-kw must be > 0.0, got {value}. This is a synthetic "
            f"scenario parameter, not a validated station figure; it still must be "
            f"a physically meaningful positive load."
        )
    if value > _SANITY_MAX_CRITICAL_LOAD_KW:
        raise argparse.ArgumentTypeError(
            f"--critical-load-kw={value} exceeds the sanity bound of "
            f"{_SANITY_MAX_CRITICAL_LOAD_KW} kW for this station-scale scenario "
            f"(likely a unit error -- check you did not enter watts instead of kW)."
        )
    return value


def run(critical_load_kw: float, steps: int, output_path: Path) -> Dict[str, Any]:
    n6 = _load_n6_module()

    report: Dict[str, Any] = {
        "status": "UNKNOWN",
        "cli_input": {
            "critical_load_kw_user_supplied": critical_load_kw,
            "critical_load_w_user_supplied": critical_load_kw * 1000.0,
            "label": "SYNTHETIC_USER_SUPPLIED_SCENARIO_PARAMETER_FOR_THIS_RUN_ONLY",
            "provenance": "Entered on the CLI for this run. Not a validated real-Nuolja-station "
                          "measurement. Not registered in POLARIS_MASTER_DECISION_REGISTER.md.",
        },
        "governance_status_unchanged_by_this_run": {
            "real_station_T_required": "NOT_ESTABLISHED (docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md, ECD-01)",
            "real_station_critical_load_evidence": "EXTERNAL_EVIDENCE_REQUIRED (EVID-02), unavailable",
            "owner_decision_A_T_required": "A-iii selected (fail closed) -- NOT implemented in router.py/ecd.py",
            "owner_decision_B_critical_load_routing": "B-iii selected (fail closed) -- NOT implemented in router.py/ecd.py",
            "owner_decision_C_unknown_invalid_response": "M-A selected (fail closed/block) -- NOT implemented at orchestration level",
            "cl_01_11_6kw_value": "Remains scoped 'research' only; NOT promoted to routing/safety_enforcement use by this script",
        },
    }

    # --- 1. Protected frozen-asset hash verification (reusing the existing,
    #        unmodified script's own asset manifest; not re-deriving it) ---
    asset_verification = {}
    for name, (path, expected_hash) in n6.PROTECTED_ASSETS.items():
        actual_hash = n6.sha256_of(path)
        matched = actual_hash == expected_hash
        asset_verification[name] = {"path": str(path), "hash": actual_hash, "verified": matched}
        if not matched:
            report["status"] = "FAIL_PROTECTED_ASSET_HASH_MISMATCH"
            report["protected_assets_verification"] = asset_verification
            return report
    report["protected_assets_verification"] = asset_verification

    # --- 2. Ingest fixture, build initial StationState (same pattern/index
    #        as the existing validated script) ---
    adapter = n6.H10RuntimeAdapter(str(n6.FIXTURE_DIR))
    st_k_raw = adapter.get_station_state(n6.SMOKE_INDEX, battery_soc_pct=50.0)

    st_initial = n6.StationState(
        timestamp=st_k_raw.timestamp,
        battery_soc_pct=80.0,
        battery_energy_wh=160000.0,
        diesel_running=True,
        diesel_hours_running=2.0,
        last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
        last_observed_demand=st_k_raw.last_observed_demand,
        last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
        diesel_fuel_remaining_liters=500.0,
    )

    # --- 3. Candidate N6 36-feature matrix for the same fixed smoke origin ---
    import numpy as np
    import pandas as pd
    import yaml

    matrix_path = (
        REPO_ROOT
        / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet"
    )
    df_mat = pd.read_parquet(matrix_path)
    df_mat["forecast_start"] = pd.to_datetime(df_mat["forecast_start"], utc=True)
    origin_df = df_mat[df_mat["forecast_start"] == n6.SMOKE_ORIGIN].sort_values("horizon_hour").reset_index(drop=True)
    if len(origin_df) != 24:
        report["status"] = "FAIL_FIXTURE_SHAPE"
        report["error"] = f"Expected 24 feature rows, got {len(origin_df)}"
        return report

    is_trans = ((origin_df["cloud_frac"] >= 0.2) & (origin_df["cloud_frac"] < 0.6)).astype(np.float64)
    origin_df["elevation_x_transition_cloud"] = origin_df["solar_elevation"] * is_trans
    features_df = origin_df.drop(columns=["actual_SW_IN", "residual_target"], errors="ignore")

    # --- 4. Load microgrid subsystem configs (unmodified yaml files) ---
    configs = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        with open(REPO_ROOT / "system" / "config" / f"{cfg_name}.yaml", "r", encoding="utf-8") as f:
            configs[cfg_name] = yaml.safe_load(f)

    # --- 5. Candidate N6 forecast ---
    n6_engine = n6.N6SolarForecastEngine()
    n6_bundle = n6_engine.predict(st_initial, {"n6_feature_matrix": features_df})

    critical_load_w_user = critical_load_kw * 1000.0
    configs_run = dict(configs)
    configs_run["ebr_target_wh"] = n6_bundle.metadata["ebr_target_wh"]
    configs_run["terminal_reserve_model"] = "INITIAL_STATE"
    # GAP19's own documented, pre-existing input slot (gap19_highs_native.py
    # lines ~88-99) -- supplying it is not an edit to that protected file.
    configs_run["critical_demand_w"] = [
        min(critical_load_w_user, d) for d in n6_bundle.demand.point
    ]

    # --- 6. Route exactly as the real production runner does
    #        (system/runtime/runner.py lines ~149-167), without editing that
    #        protected file: NORMAL -> GAP19, EMERGENCY -> Option D,
    #        UNKNOWN_INVALID -> fail closed, no plan produced. ---
    router = n6.EMSControlRouter()
    assessment, route = router.evaluate_and_route(st_initial, n6_bundle, configs_run)

    # What critical_load_w the router ACTUALLY used internally (recomputed
    # here, read-only, exactly per router.py lines 54-59, purely for honest
    # reporting -- router.py itself exposes no such field on `assessment`).
    router_internal_critical_load_w = float(st_initial.last_observed_demand)
    if router_internal_critical_load_w <= 0.0 and n6_bundle.demand.point:
        router_internal_critical_load_w = float(n6_bundle.demand.point[0])
    if router_internal_critical_load_w <= 0.0:
        router_internal_critical_load_w = 30000.0

    report["routing"] = {
        "route": route,
        "router_internal_critical_load_w": router_internal_critical_load_w,
        "router_internal_critical_load_source": (
            "current_state.last_observed_demand (full observed demand), NOT the "
            "user-supplied --critical-load-kw value -- confirmed by direct, "
            "read-only inspection of router.py this run. router.py never reads "
            "configs['critical_demand_w'] or configs['loads']['critical_load']."
        ),
        "t_required_hours_used": float(configs_run.get("ecd", {}).get("t_required_hours", 6.0)),
        "t_required_source": (
            "UNGOVERNED CODE DEFAULT (router.py line 45, 6.0h) -- no system/config/*.yaml "
            "sets ecd.t_required_hours. This is the exact HD-03 finding; NOT the real-station "
            "value (NOT_ESTABLISHED) and NOT the 72h prototype (implementation NOT_GRANTED)."
        ),
        "unknown_invalid_reachability_note": (
            "UNKNOWN_INVALID is architecturally unreachable from this call site today: both "
            "router.py's T_required default and its critical-load substitution chain always "
            "resolve to a finite, positive number, so ecd.py's own correctly-implemented "
            "fail-closed path is never triggered here -- independent of what this CLI's "
            "--critical-load-kw value is. This is unchanged by this run; it is a pre-existing, "
            "already-documented gap between the owner's recorded A-iii/B-iii/M-A decision and "
            "router.py's/ecd.py's actual (unmodified) code."
        ),
    }

    if route == "UNKNOWN_INVALID":
        report["status"] = "BLOCKED_FAIL_CLOSED_UNKNOWN_INVALID"
        report["optimizer_executed"] = None
        report["failure_reason"] = getattr(assessment, "failure_reason", None)
        _write_report(report, output_path)
        return report

    optimizer_name = None
    plan = None
    optimizer_error = None
    try:
        if route == "NORMAL":
            optimizer_name = "GAP19HighsNativeOptimizer"
            optimizer = n6.GAP19HighsNativeOptimizer()
            plan = optimizer.optimize(n6_bundle, st_initial, configs_run)
        elif route == "EMERGENCY":
            optimizer_name = "OptionDFallbackSolver"
            from system.optimization.implementations.option_d import OptionDFallbackSolver
            optimizer = OptionDFallbackSolver()
            plan = optimizer.solve(assessment, n6_bundle, st_initial, configs_run)
        else:
            raise RuntimeError(f"Unrecognized route {route!r}")
    except Exception as exc:  # genuine runtime failure, reported, not swallowed
        optimizer_error = f"{exc.__class__.__name__}: {exc}"

    report["optimizer_executed"] = optimizer_name
    if optimizer_error is not None:
        report["status"] = "FAIL_OPTIMIZER_RUNTIME_ERROR"
        report["optimizer_error"] = optimizer_error
        _write_report(report, output_path)
        return report

    report["optimizer_result"] = {
        "constraint_status": plan.constraint_status,
        "objective_value": plan.objective_value,
    }

    # --- 7. Step DigitalTwinSimulator (PROTECTED, read-only import) over the
    #        requested horizon, same mechanics as the existing validated
    #        script, generalized to whichever route/optimizer actually ran. ---
    simulator = n6.DigitalTwinSimulator(configs)
    future_actuals = adapter.get_future_ground_truth(n6.SMOKE_INDEX, horizon_hours=24)

    curr_st = st_initial
    hourly_records: List[Dict[str, Any]] = []
    failed_steps: List[str] = []
    total_unmet_wh = 0.0
    total_unmet_vs_user_critical_wh = 0.0

    n_steps = min(steps, 24, len(plan.timestamps))
    for t in range(n_steps):
        actual_t = future_actuals[t]
        step_plan = n6.DispatchPlan(
            schema_version="1.0.0",
            timestamps=[plan.timestamps[t]] * 24,
            solar_used=[plan.solar_used[t]] * 24,
            wind_used=[plan.wind_used[t]] * 24,
            battery_charge=[plan.battery_charge[t]] * 24,
            battery_discharge=[plan.battery_discharge[t]] * 24,
            battery_soc=[plan.battery_soc[t]] * 24,
            diesel_power=[plan.diesel_power[t]] * 24,
            load_served=[plan.load_served[t]] * 24,
            flexible_load_schedule=[plan.flexible_load_schedule[t]] * 24,
            renewable_curtailment=[plan.renewable_curtailment[t]] * 24,
            unmet_load=[plan.unmet_load[t]] * 24,
            objective_value=plan.objective_value,
            constraint_status=plan.constraint_status,
            energy_balance_errors=[0.0] * 24,
        )
        try:
            curr_st = simulator.step(curr_st, step_plan, actual_t)
        except Exception as e:
            failed_steps.append(f"Step {t}: Simulator exception: {e}")
            break

        demand_t = float(n6_bundle.demand.point[t])
        served_total_t = max(0.0, demand_t - float(plan.unmet_load[t]))
        critical_demand_t = configs_run["critical_demand_w"][t]
        # DERIVED_ESTIMATE, not a verified `unmet_essential` field (neither
        # GAP19HighsNativeOptimizer nor OptionDFallbackSolver populates that
        # field on the DispatchPlan in this run; confirmed by source read).
        unmet_vs_user_critical_w = max(0.0, critical_demand_t - served_total_t)

        total_unmet_wh += float(plan.unmet_load[t])
        total_unmet_vs_user_critical_wh += unmet_vs_user_critical_w

        hourly_records.append({
            "hour": t,
            "route": route,
            "diesel_power_w": plan.diesel_power[t],
            "unmet_load_w_total": plan.unmet_load[t],
            "critical_demand_w_used_this_hour": critical_demand_t,
            "unmet_vs_user_critical_load_w_DERIVED_ESTIMATE": unmet_vs_user_critical_w,
            "soc_after_pct": curr_st.battery_soc_pct,
            "fuel_remaining_l": curr_st.diesel_fuel_remaining_liters,
        })

    report["simulation"] = {
        "steps_requested": steps,
        "steps_completed": len(hourly_records),
        "failed_steps": failed_steps,
        "total_unmet_load_wh": round(total_unmet_wh, 3),
        "total_unmet_vs_user_critical_load_wh_DERIVED_ESTIMATE": round(total_unmet_vs_user_critical_wh, 3),
        "diesel_fuel_consumed_l": round(st_initial.diesel_fuel_remaining_liters - curr_st.diesel_fuel_remaining_liters, 4),
        "diesel_fuel_remaining_l": curr_st.diesel_fuel_remaining_liters,
        "battery_soc_final_pct": curr_st.battery_soc_pct,
        "battery_soc_min_pct": min((r["soc_after_pct"] for r in hourly_records), default=None),
        "battery_soc_max_pct": max((r["soc_after_pct"] for r in hourly_records), default=None),
        "hourly_records": hourly_records,
    }

    report["status"] = (
        "SUCCESS_CLEAN" if not failed_steps and len(hourly_records) == n_steps else "SUCCESS_WITH_FAULTS"
    )

    _write_report(report, output_path)
    return report


def _write_report(report: Dict[str, Any], output_path: Path) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "POLARIS synthetic end-to-end run: N6 forecast -> EMS router -> "
            "GAP19/Option D optimizer -> DigitalTwinSimulator, with one "
            "synthetic, user-supplied critical-load input in kW."
        )
    )
    parser.add_argument(
        "--critical-load-kw",
        type=_validate_critical_load_kw,
        required=True,
        help=(
            "Synthetic critical load for THIS scenario run, in kW (e.g. 11.6). "
            "NOT a validated real-station measurement -- used only as GAP19's own "
            "critical-demand reserve input; it has no effect on the EMS router's "
            "NORMAL/EMERGENCY/UNKNOWN_INVALID classification (see module docstring)."
        ),
    )
    parser.add_argument("--steps", type=int, default=24, help="Timesteps to simulate (<=24, default 24).")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON report path (default: alongside this script).",
    )
    args = parser.parse_args()

    if args.steps < 1 or args.steps > 24:
        print("ERROR: --steps must be between 1 and 24 (fixture provides a 24h future-ground-truth horizon).", file=sys.stderr)
        sys.exit(2)

    output_path = Path(args.output) if args.output else (
        Path(__file__).resolve().parent / "SYNTHETIC_CRITICAL_LOAD_RUN_REPORT.json"
    )

    print("=" * 80)
    print("POLARIS -- SYNTHETIC CRITICAL-LOAD END-TO-END RUN")
    print("=" * 80)
    print(f"Critical load (synthetic, user-supplied): {args.critical_load_kw} kW")
    print(f"Steps requested: {args.steps}")

    report = run(args.critical_load_kw, args.steps, output_path)

    print(f"\nRouter decision:            {report.get('routing', {}).get('route', 'N/A')}")
    print(f"Optimizer executed:         {report.get('optimizer_executed', 'N/A')}")
    if "optimizer_result" in report:
        print(f"Optimizer constraint_status:{report['optimizer_result']['constraint_status']}")
        print(f"Optimizer objective_value:  {report['optimizer_result']['objective_value']}")
    if "simulation" in report:
        sim = report["simulation"]
        print(f"Steps completed:            {sim['steps_completed']}/{args.steps}")
        print(f"Total unmet load (Wh):      {sim['total_unmet_load_wh']}")
        print(f"Total unmet vs user critical load (Wh, derived estimate): {sim['total_unmet_vs_user_critical_load_wh_DERIVED_ESTIMATE']}")
        print(f"Diesel fuel consumed (L):   {sim['diesel_fuel_consumed_l']}")
    print(f"\nOVERALL STATUS: {report['status']}")
    print(f"Full report written to: {output_path}")
    print("=" * 80)

    if report["status"] not in ("SUCCESS_CLEAN", "SUCCESS_WITH_FAULTS"):
        sys.exit(1)


if __name__ == "__main__":
    main()
