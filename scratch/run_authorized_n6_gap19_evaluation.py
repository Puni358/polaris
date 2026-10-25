#!/usr/bin/env python3
"""
POLARIS — Authorized End-to-End N6 + GAP19 Evaluation Runner on 2024 Data
Authorization Scope: EXECUTE_N6_2024_END_TO_END
Project Lead Authorization granted 2026-10-21.

Strict Invariants:
1. Preserve frozen N6 model, GAP19 formulation, OD-02-C alignment, MDR, and production configs.
2. Quarantined/blind 2025 data is strictly untouched.
3. No retraining, tuning, synthetic sine-wave substitution, or mocked optimizer outputs.
4. Fail-closed: record all solver statuses, infeasibilities, and errors explicitly.
5. Write all artifacts strictly to scratch/.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path("/home/punith-bs/01polaris (Copy)")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from system.control.router import EMSControlRouter
from system.evaluation.n6_multi_origin_harness.adapters import _align_n6_bundle_od02
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.forecasting.implementations.n6_solar import (
    FEATURE_NAMES,
    FROZEN_MODEL_PATH,
    FROZEN_MODEL_SHA256,
    N6SolarForecastEngine,
)
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.schemas.dispatch_plan import DispatchPlan
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.simulation.simulator import DigitalTwinSimulator

# Paths
OUTPUT_DIR = REPO_ROOT / "scratch/authorized_n6_gap19_eval_2024"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = OUTPUT_DIR / "EXECUTION_TRACE.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

CAND_K_MATRIX_PATH = (
    REPO_ROOT
    / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet"
)
CANDIDATE_N_MANIFEST_PATH = (
    REPO_ROOT
    / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json"
)
FIXTURE_PATH = REPO_ROOT / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv"
EXPECTED_FIXTURE_SHA256 = "762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_governance_invariants():
    logging.info("Verifying governance invariants and cryptographic asset hashes...")
    # 1. Model hash
    if not FROZEN_MODEL_PATH.exists():
        raise FileNotFoundError(f"Frozen N6 model not found at {FROZEN_MODEL_PATH}")
    actual_model_hash = compute_sha256(FROZEN_MODEL_PATH)
    if actual_model_hash != FROZEN_MODEL_SHA256:
        raise ValueError(f"N6 model SHA mismatch! {actual_model_hash} != {FROZEN_MODEL_SHA256}")
    logging.info(f"  [OK] N6 Model SHA-256 verified: {actual_model_hash[:16]}...")

    # 2. Candidate N manifest & winner: null
    if not CANDIDATE_N_MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Candidate N manifest not found at {CANDIDATE_N_MANIFEST_PATH}")
    with open(CANDIDATE_N_MANIFEST_PATH, "r", encoding="utf-8") as f:
        cand_manifest = json.load(f)
    if cand_manifest.get("winner") is not None:
        raise ValueError("Governance violation: winner must remain null!")
    logging.info("  [OK] CANDIDATE_N_MANIFEST winner: null invariant confirmed.")

    # 3. 2024 H1.0 Fixture
    if not FIXTURE_PATH.exists():
        raise FileNotFoundError(f"Fixture not found at {FIXTURE_PATH}")
    actual_fixture_hash = compute_sha256(FIXTURE_PATH)
    if actual_fixture_hash != EXPECTED_FIXTURE_SHA256:
        raise ValueError(f"Fixture SHA mismatch! {actual_fixture_hash} != {EXPECTED_FIXTURE_SHA256}")
    logging.info(f"  [OK] H1.0 Fixture SHA-256 verified: {actual_fixture_hash[:16]}...")


def load_system_configs() -> Dict[str, Any]:
    configs = {}
    config_dir = REPO_ROOT / "system" / "config"
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        with open(config_dir / f"{cfg_name}.yaml", "r", encoding="utf-8") as f:
            configs[cfg_name] = yaml.safe_load(f)
    return configs


def prepare_origin_features(df_mat: pd.DataFrame, origin_dt: pd.Timestamp) -> pd.DataFrame:
    origin_rows = df_mat[df_mat["forecast_start"] == origin_dt].sort_values("horizon_hour").reset_index(drop=True)
    if len(origin_rows) != 24:
        raise ValueError(f"Origin {origin_dt} has {len(origin_rows)} rows (expected 24)")

    # Synthesize 36th feature if missing
    if "elevation_x_transition_cloud" not in origin_rows.columns:
        is_trans = ((origin_rows["cloud_frac"] >= 0.2) & (origin_rows["cloud_frac"] < 0.6)).astype(np.float64)
        origin_rows["elevation_x_transition_cloud"] = origin_rows["solar_elevation"] * is_trans

    # Drop realized columns to strictly enforce causal integrity
    features_df = origin_rows.drop(columns=["actual_SW_IN", "residual_target"], errors="ignore")
    return features_df


def run_single_origin_evaluation(
    origin_str: str,
    fixture_index: int,
    features_df: pd.DataFrame,
    adapter: H10RuntimeAdapter,
    n6_engine: N6SolarForecastEngine,
    base_engine: LocalBaselineForecastEngine,
    router: EMSControlRouter,
    optimizer: GAP19HighsNativeOptimizer,
    simulator: DigitalTwinSimulator,
    configs: Dict[str, Any],
    initial_soc_pct: float = 80.0,
    initial_fuel_l: float = 500.0,
    warmed_up_diesel: bool = True,
) -> Dict[str, Any]:
    """
    Executes one complete 24-hour evaluation at origin_str for both Candidate N6 and Baseline arms.
    """
    st_raw = adapter.get_station_state(fixture_index, battery_soc_pct=initial_soc_pct)
    cap_wh = float(configs.get("battery", {}).get("capacity_wh", 200000.0))
    battery_e_wh = cap_wh * (initial_soc_pct / 100.0)

    st_initial = StationState(
        timestamp=st_raw.timestamp,
        battery_soc_pct=initial_soc_pct,
        battery_energy_wh=battery_e_wh,
        diesel_running=warmed_up_diesel,
        diesel_hours_running=2.0 if warmed_up_diesel else 0.0,
        last_observed_solar_irradiance=st_raw.last_observed_solar_irradiance,
        last_observed_demand=st_raw.last_observed_demand,
        last_observed_wind_generation=st_raw.last_observed_wind_generation,
        diesel_fuel_remaining_liters=initial_fuel_l,
        operating_mode="NORMAL",
    )

    future_actuals = adapter.get_future_ground_truth(fixture_index, horizon_hours=24)

    critical_load_baseline_w = float(
        configs.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
    )

    # ----------------------------------------------------
    # Candidate N6 Arm
    # ----------------------------------------------------
    t0_n6 = time.perf_counter()
    n6_error = None
    plan_n6 = None
    route_n6 = "UNKNOWN"
    n6_solve_time_s = 0.0

    try:
        raw_bundle_n6 = n6_engine.predict(st_initial, {"n6_feature_matrix": features_df})
        aligned_bundle_n6 = _align_n6_bundle_od02(raw_bundle_n6, origin_timestamp_str=origin_str)

        cfg_n6 = copy.deepcopy(configs)
        cfg_n6["ebr_target_wh"] = aligned_bundle_n6.metadata["ebr_target_wh"]
        cfg_n6["terminal_reserve_model"] = "INITIAL_STATE"
        cfg_n6["critical_demand_w"] = [
            min(critical_load_baseline_w, d) for d in aligned_bundle_n6.demand.point
        ]
        cfg_n6.setdefault("ecd", {}).update({"t_required_hours": 6.0, "t_required_authorized": True})
        cfg_n6.setdefault("critical_load", {}).update({
            "authorized": True,
            "evidence_id": f"EVID-N6-{origin_str}",
            "authorized_critical_load_w": critical_load_baseline_w,
        })

        assessment_n6, route_n6 = router.evaluate_and_route(st_initial, aligned_bundle_n6, cfg_n6)
        if route_n6 == "NORMAL":
            plan_n6 = optimizer.optimize(aligned_bundle_n6, st_initial, cfg_n6)
        else:
            n6_error = f"Router routed to non-NORMAL: {route_n6}"
    except Exception as e:
        n6_error = str(e)
    t1_n6 = time.perf_counter()
    n6_solve_time_s = t1_n6 - t0_n6

    # Step simulation if plan succeeded
    n6_sim_records = []
    curr_st_n6 = copy.deepcopy(st_initial)
    if plan_n6 is not None and plan_n6.constraint_status == "OPTIMAL":
        for t in range(24):
            step_plan = DispatchPlan(
                schema_version="1.0.0",
                timestamps=[plan_n6.timestamps[t]] * 24,
                solar_used=[plan_n6.solar_used[t]] * 24,
                wind_used=[plan_n6.wind_used[t]] * 24,
                battery_charge=[plan_n6.battery_charge[t]] * 24,
                battery_discharge=[plan_n6.battery_discharge[t]] * 24,
                battery_soc=[plan_n6.battery_soc[t]] * 24,
                diesel_power=[plan_n6.diesel_power[t]] * 24,
                load_served=[plan_n6.load_served[t]] * 24,
                flexible_load_schedule=[plan_n6.flexible_load_schedule[t]] * 24,
                renewable_curtailment=[plan_n6.renewable_curtailment[t]] * 24,
                unmet_load=[plan_n6.unmet_load[t]] * 24,
                objective_value=plan_n6.objective_value,
                constraint_status=plan_n6.constraint_status,
                energy_balance_errors=[0.0] * 24,
            )
            curr_st_n6 = simulator.step(curr_st_n6, step_plan, future_actuals[t])
            n6_sim_records.append({
                "step": t,
                "diesel_power_w": plan_n6.diesel_power[t],
                "battery_charge_w": plan_n6.battery_charge[t],
                "battery_discharge_w": plan_n6.battery_discharge[t],
                "solar_used_w": plan_n6.solar_used[t],
                "wind_used_w": plan_n6.wind_used[t],
                "renewable_curtailment_w": plan_n6.renewable_curtailment[t],
                "unmet_load_w": plan_n6.unmet_load[t],
                "soc_pct": curr_st_n6.battery_soc_pct,
                "fuel_remaining_l": curr_st_n6.diesel_fuel_remaining_liters,
            })

    # ----------------------------------------------------
    # Baseline Arm (LocalBaselineForecastEngine)
    # ----------------------------------------------------
    t0_base = time.perf_counter()
    base_error = None
    plan_base = None
    route_base = "UNKNOWN"
    base_solve_time_s = 0.0

    try:
        ctx_base = adapter.get_runtime_context(fixture_index)
        bundle_base = base_engine.predict(st_initial, ctx_base)

        cfg_base = copy.deepcopy(configs)
        cfg_base["terminal_reserve_model"] = "INITIAL_STATE"
        cfg_base["critical_demand_w"] = [
            min(critical_load_baseline_w, d) for d in bundle_base.demand.point
        ]
        cfg_base.setdefault("ecd", {}).update({"t_required_hours": 6.0, "t_required_authorized": True})
        cfg_base.setdefault("critical_load", {}).update({
            "authorized": True,
            "evidence_id": f"EVID-BASE-{origin_str}",
            "authorized_critical_load_w": critical_load_baseline_w,
        })

        assessment_base, route_base = router.evaluate_and_route(st_initial, bundle_base, cfg_base)
        if route_base == "NORMAL":
            plan_base = optimizer.optimize(bundle_base, st_initial, cfg_base)
        else:
            base_error = f"Baseline router routed to non-NORMAL: {route_base}"
    except Exception as e:
        base_error = str(e)
    t1_base = time.perf_counter()
    base_solve_time_s = t1_base - t0_base

    # Step simulation for Baseline if plan succeeded
    base_sim_records = []
    curr_st_base = copy.deepcopy(st_initial)
    if plan_base is not None and plan_base.constraint_status == "OPTIMAL":
        for t in range(24):
            step_plan_base = DispatchPlan(
                schema_version="1.0.0",
                timestamps=[plan_base.timestamps[t]] * 24,
                solar_used=[plan_base.solar_used[t]] * 24,
                wind_used=[plan_base.wind_used[t]] * 24,
                battery_charge=[plan_base.battery_charge[t]] * 24,
                battery_discharge=[plan_base.battery_discharge[t]] * 24,
                battery_soc=[plan_base.battery_soc[t]] * 24,
                diesel_power=[plan_base.diesel_power[t]] * 24,
                load_served=[plan_base.load_served[t]] * 24,
                flexible_load_schedule=[plan_base.flexible_load_schedule[t]] * 24,
                renewable_curtailment=[plan_base.renewable_curtailment[t]] * 24,
                unmet_load=[plan_base.unmet_load[t]] * 24,
                objective_value=plan_base.objective_value,
                constraint_status=plan_base.constraint_status,
                energy_balance_errors=[0.0] * 24,
            )
            curr_st_base = simulator.step(curr_st_base, step_plan_base, future_actuals[t])
            base_sim_records.append({
                "step": t,
                "diesel_power_w": plan_base.diesel_power[t],
                "battery_charge_w": plan_base.battery_charge[t],
                "battery_discharge_w": plan_base.battery_discharge[t],
                "solar_used_w": plan_base.solar_used[t],
                "wind_used_w": plan_base.wind_used[t],
                "renewable_curtailment_w": plan_base.renewable_curtailment[t],
                "unmet_load_w": plan_base.unmet_load[t],
                "soc_pct": curr_st_base.battery_soc_pct,
                "fuel_remaining_l": curr_st_base.diesel_fuel_remaining_liters,
            })

    # Accounting
    n6_fuel_burned = (
        round(initial_fuel_l - curr_st_n6.diesel_fuel_remaining_liters, 4)
        if (plan_n6 is not None and plan_n6.constraint_status == "OPTIMAL")
        else None
    )
    base_fuel_burned = (
        round(initial_fuel_l - curr_st_base.diesel_fuel_remaining_liters, 4)
        if (plan_base is not None and plan_base.constraint_status == "OPTIMAL")
        else None
    )

    n6_diesel_hours = sum(1 for r in n6_sim_records if r["diesel_power_w"] > 0)
    base_diesel_hours = sum(1 for r in base_sim_records if r["diesel_power_w"] > 0)

    n6_unmet_wh = sum(r["unmet_load_w"] for r in n6_sim_records)
    base_unmet_wh = sum(r["unmet_load_w"] for r in base_sim_records)

    n6_solar_used_wh = sum(r["solar_used_w"] for r in n6_sim_records)
    n6_solar_curtailed_wh = sum(r["renewable_curtailment_w"] for r in n6_sim_records)

    return {
        "origin": origin_str,
        "fixture_index": fixture_index,
        "n6": {
            "status": plan_n6.constraint_status if plan_n6 else "FAILED",
            "error": n6_error,
            "route": route_n6,
            "solve_time_s": round(n6_solve_time_s, 3),
            "objective": plan_n6.objective_value if plan_n6 else None,
            "diesel_fuel_burned_l": n6_fuel_burned,
            "diesel_run_hours": n6_diesel_hours,
            "unmet_load_wh": n6_unmet_wh,
            "solar_used_wh": n6_solar_used_wh,
            "solar_curtailed_wh": n6_solar_curtailed_wh,
            "min_soc_pct": min((r["soc_pct"] for r in n6_sim_records), default=None),
            "max_soc_pct": max((r["soc_pct"] for r in n6_sim_records), default=None),
            "final_soc_pct": n6_sim_records[-1]["soc_pct"] if n6_sim_records else None,
            "completed_steps": len(n6_sim_records),
        },
        "baseline": {
            "status": plan_base.constraint_status if plan_base else "FAILED",
            "error": base_error,
            "route": route_base,
            "solve_time_s": round(base_solve_time_s, 3),
            "objective": plan_base.objective_value if plan_base else None,
            "diesel_fuel_burned_l": base_fuel_burned,
            "diesel_run_hours": base_diesel_hours,
            "unmet_load_wh": base_unmet_wh,
            "min_soc_pct": min((r["soc_pct"] for r in base_sim_records), default=None),
            "max_soc_pct": max((r["soc_pct"] for r in base_sim_records), default=None),
            "final_soc_pct": base_sim_records[-1]["soc_pct"] if base_sim_records else None,
            "completed_steps": len(base_sim_records),
        },
        "delta_fuel_l": (
            round(n6_fuel_burned - base_fuel_burned, 4)
            if (n6_fuel_burned is not None and base_fuel_burned is not None)
            else None
        ),
    }


def main():
    start_wall_time = time.time()
    logging.info("=" * 80)
    logging.info("POLARIS — FULL END-TO-END N6 + GAP19 EVALUATION (2024 DATASET)")
    logging.info("Authorized Scope: EXECUTE_N6_2024_END_TO_END")
    logging.info("=" * 80)

    # 1. Verification of governance
    verify_governance_invariants()

    # 2. Ingestion & Component Setup
    logging.info("Loading subsystem configs and instantiating real components...")
    configs = load_system_configs()
    with open(OUTPUT_DIR / "CONFIG_SNAPSHOT.json", "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2)

    adapter = H10RuntimeAdapter(str(REPO_ROOT / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"))
    fixture_ts_map = {r["timestamp"]: i for i, r in enumerate(adapter.rows)}

    logging.info(f"Loaded H1.0 fixture: {len(adapter.rows)} records (2024 canonical)")

    df_mat = pd.read_parquet(CAND_K_MATRIX_PATH)
    df_mat["forecast_start"] = pd.to_datetime(df_mat["forecast_start"], utc=True)
    all_parquet_origins = df_mat["forecast_start"].drop_duplicates().sort_values().tolist()
    logging.info(f"Loaded candidate_k clean matrix: {len(all_parquet_origins)} 00:00 UTC origins")

    n6_engine = N6SolarForecastEngine()
    base_engine = LocalBaselineForecastEngine(REPO_ROOT / "system/config/solar_pv.yaml")
    router = EMSControlRouter()
    optimizer = GAP19HighsNativeOptimizer()
    simulator = DigitalTwinSimulator(configs)

    # --------------------------------------------------------------------------
    # Phase 3: Mode A — Representative Smoke Simulation (2024-06-01T00:00:00Z)
    # --------------------------------------------------------------------------
    smoke_dt = pd.Timestamp("2024-06-01 00:00:00+00:00")
    smoke_str = "2024-06-01T00:00:00Z"
    smoke_idx = fixture_ts_map.get(smoke_str)
    if smoke_idx is None:
        raise ValueError(f"Smoke origin {smoke_str} not found in H1.0 fixture!")

    logging.info("\n" + "=" * 80)
    logging.info(f"PHASE 3: MODE A — REPRESENTATIVE SMOKE SIMULATION ({smoke_str}, index {smoke_idx})")
    logging.info("=" * 80)

    smoke_features = prepare_origin_features(df_mat, smoke_dt)
    smoke_res = run_single_origin_evaluation(
        origin_str=smoke_str,
        fixture_index=smoke_idx,
        features_df=smoke_features,
        adapter=adapter,
        n6_engine=n6_engine,
        base_engine=base_engine,
        router=router,
        optimizer=optimizer,
        simulator=simulator,
        configs=configs,
        initial_soc_pct=80.0,
        initial_fuel_l=500.0,
        warmed_up_diesel=True,
    )

    with open(OUTPUT_DIR / "MODE_A_SMOKE_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(smoke_res, f, indent=2)

    logging.info("Smoke Run Results:")
    logging.info(f"  Candidate N6 Solver Status:   {smoke_res['n6']['status']}")
    logging.info(f"  Candidate N6 Router Mode:     {smoke_res['n6']['route']}")
    logging.info(f"  Candidate N6 Diesel Consumed: {smoke_res['n6']['diesel_fuel_burned_l']} L")
    logging.info(f"  Candidate N6 Diesel Run Hours:{smoke_res['n6']['diesel_run_hours']} h")
    logging.info(f"  Candidate N6 Completed Steps: {smoke_res['n6']['completed_steps']} / 24")
    logging.info(f"  Baseline Diesel Consumed:     {smoke_res['baseline']['diesel_fuel_burned_l']} L")
    logging.info(f"  Delta Fuel (N6 - Base):       {smoke_res['delta_fuel_l']} L")

    # Assert Smoke Acceptance Criteria
    assert smoke_res["n6"]["status"] == "OPTIMAL", f"Smoke failed: N6 solver status {smoke_res['n6']['status']}"
    assert smoke_res["n6"]["completed_steps"] == 24, f"Smoke failed: completed {smoke_res['n6']['completed_steps']} steps"
    assert smoke_res["n6"]["diesel_fuel_burned_l"] is not None and smoke_res["n6"]["diesel_fuel_burned_l"] > 0, "Smoke failed: zero/null diesel"
    logging.info("\n[PASS] Mode A Smoke Acceptance Criteria strictly verified! Proceeding to Mode B...")

    # --------------------------------------------------------------------------
    # Phase 4: Mode B — Full Evaluation across all Eligible 2024 Origins
    # --------------------------------------------------------------------------
    logging.info("\n" + "=" * 80)
    logging.info("PHASE 4: MODE B — FULL 2024 MULTI-ORIGIN EVALUATION")
    logging.info(f"Target Origin Count: {len(all_parquet_origins)} eligible 00:00 UTC origins")
    logging.info("=" * 80)

    per_origin_results = []
    solves_attempted = 0
    solves_optimal = 0
    solves_failed = 0

    total_n6_fuel_liters = 0.0
    total_base_fuel_liters = 0.0
    total_n6_run_hours = 0
    total_base_run_hours = 0
    total_n6_solar_used_wh = 0.0
    total_n6_curtailed_wh = 0.0
    total_n6_unmet_wh = 0.0
    total_base_unmet_wh = 0.0

    mode_b_start_time = time.time()

    for idx, orig_dt in enumerate(all_parquet_origins):
        orig_str = orig_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        f_idx = fixture_ts_map.get(orig_str)

        if f_idx is None:
            logging.warning(f"[{idx+1}/{len(all_parquet_origins)}] Origin {orig_str} not in fixture! Skipping.")
            continue

        try:
            feats = prepare_origin_features(df_mat, orig_dt)
            res = run_single_origin_evaluation(
                origin_str=orig_str,
                fixture_index=f_idx,
                features_df=feats,
                adapter=adapter,
                n6_engine=n6_engine,
                base_engine=base_engine,
                router=router,
                optimizer=optimizer,
                simulator=simulator,
                configs=configs,
                initial_soc_pct=80.0,
                initial_fuel_l=500.0,
                warmed_up_diesel=True,
            )
            solves_attempted += 1

            if res["n6"]["status"] == "OPTIMAL":
                solves_optimal += 1
                total_n6_fuel_liters += res["n6"]["diesel_fuel_burned_l"]
                total_n6_run_hours += res["n6"]["diesel_run_hours"]
                total_n6_solar_used_wh += res["n6"]["solar_used_wh"]
                total_n6_curtailed_wh += res["n6"]["solar_curtailed_wh"]
                total_n6_unmet_wh += res["n6"]["unmet_load_wh"]
            else:
                solves_failed += 1
                logging.error(f"Solver non-optimal for {orig_str}: {res['n6']['status']} - {res['n6']['error']}")

            if res["baseline"]["status"] == "OPTIMAL":
                total_base_fuel_liters += res["baseline"]["diesel_fuel_burned_l"]
                total_base_run_hours += res["baseline"]["diesel_run_hours"]
                total_base_unmet_wh += res["baseline"]["unmet_load_wh"]

            per_origin_results.append(res)

        except Exception as e:
            solves_attempted += 1
            solves_failed += 1
            logging.error(f"Execution error at origin {orig_str}: {e}")
            per_origin_results.append({
                "origin": orig_str,
                "fixture_index": f_idx,
                "n6": {"status": "EXCEPTION", "error": str(e)},
                "baseline": {"status": "SKIPPED", "error": "Preceding exception"},
            })

        if (idx + 1) % 50 == 0 or (idx + 1) == len(all_parquet_origins):
            elapsed = time.time() - mode_b_start_time
            rate = (idx + 1) / elapsed
            rem = (len(all_parquet_origins) - (idx + 1)) / rate if rate > 0 else 0
            logging.info(
                f"Progress: {idx+1}/{len(all_parquet_origins)} origins ({(idx+1)/len(all_parquet_origins)*100:.1f}%) | "
                f"N6 Burn: {total_n6_fuel_liters:,.1f} L | Base Burn: {total_base_fuel_liters:,.1f} L | "
                f"Optimal Solves: {solves_optimal}/{solves_attempted} | ETA: {rem/60:.1f} min"
            )

    # --------------------------------------------------------------------------
    # Metrics Aggregation & Artifact Export
    # --------------------------------------------------------------------------
    total_runtime_s = round(time.time() - start_wall_time, 2)
    aggregate_summary = {
        "evaluation_scope": "EXECUTE_N6_2024_END_TO_END",
        "timestamp_completed_utc": datetime.now(timezone.utc).isoformat(),
        "total_wall_runtime_seconds": total_runtime_s,
        "mode_a_smoke_summary": {
            "origin": smoke_str,
            "status": smoke_res["n6"]["status"],
            "diesel_consumed_liters": smoke_res["n6"]["diesel_fuel_burned_l"],
            "baseline_consumed_liters": smoke_res["baseline"]["diesel_fuel_burned_l"],
            "delta_liters": smoke_res["delta_fuel_l"],
        },
        "mode_b_campaign_summary": {
            "origins_in_catalog": len(all_parquet_origins),
            "origins_attempted": solves_attempted,
            "origins_completed_optimal": solves_optimal,
            "origins_failed": solves_failed,
            "temporal_resolution": "Fixed 00:00 UTC daily origins, 24-hour lookahead horizon, 1-hour physical simulation steps",
            "candidate_n6": {
                "total_diesel_consumed_liters": round(total_n6_fuel_liters, 2),
                "mean_diesel_per_origin_liters": round(total_n6_fuel_liters / max(1, solves_optimal), 2),
                "total_generator_run_hours": total_n6_run_hours,
                "total_solar_energy_used_kwh": round(total_n6_solar_used_wh / 1000.0, 2),
                "total_solar_curtailed_kwh": round(total_n6_curtailed_wh / 1000.0, 2),
                "total_unmet_load_kwh": round(total_n6_unmet_wh / 1000.0, 2),
            },
            "frozen_baseline": {
                "total_diesel_consumed_liters": round(total_base_fuel_liters, 2),
                "mean_diesel_per_origin_liters": round(total_base_fuel_liters / max(1, solves_optimal), 2),
                "total_generator_run_hours": total_base_run_hours,
                "total_unmet_load_kwh": round(total_base_unmet_wh / 1000.0, 2),
            },
            "comparison": {
                "delta_diesel_consumed_liters": round(total_n6_fuel_liters - total_base_fuel_liters, 2),
                "relative_difference_pct": round(
                    ((total_n6_fuel_liters - total_base_fuel_liters) / max(1e-6, total_base_fuel_liters)) * 100.0, 2
                ),
            },
        },
        "cryptographic_manifest": {
            "n6_model_sha256": FROZEN_MODEL_SHA256,
            "fixture_h10_sha256": EXPECTED_FIXTURE_SHA256,
            "candidate_k_parquet_sha256": compute_sha256(CAND_K_MATRIX_PATH),
        },
    }

    with open(OUTPUT_DIR / "MODE_B_PER_ORIGIN_RESULTS.json", "w", encoding="utf-8") as f:
        json.dump(per_origin_results, f, indent=2)

    with open(OUTPUT_DIR / "MODE_B_SUMMARY_METRICS.json", "w", encoding="utf-8") as f:
        json.dump(aggregate_summary, f, indent=2)

    run_manifest = {
        "run_id": f"RUN_N6_2024_EVAL_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "authorized_scope": "EXECUTE_N6_2024_END_TO_END",
        "output_directory": str(OUTPUT_DIR),
        "files_generated": [
            "EXECUTION_TRACE.log",
            "CONFIG_SNAPSHOT.json",
            "MODE_A_SMOKE_REPORT.json",
            "MODE_B_PER_ORIGIN_RESULTS.json",
            "MODE_B_SUMMARY_METRICS.json",
            "RUN_MANIFEST.json",
        ],
    }
    with open(OUTPUT_DIR / "RUN_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2)

    logging.info("\n" + "=" * 80)
    logging.info("POLARIS EVALUATION COMPLETE!")
    logging.info(f"Total Runtime: {total_runtime_s} seconds")
    logging.info(f"Artifacts preserved in: {OUTPUT_DIR}")
    logging.info("=" * 80)


if __name__ == "__main__":
    main()
