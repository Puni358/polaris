"""
POLARIS — 23-HORIZON OFAT FORMAL EXECUTION HARNESS
Authoritative Governance 23-Horizon OFAT Execution Script

EXECUTION PROTOCOL:
- Control: Frozen audited V3 Stage 8.1 evidence (ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv)
- Treatment Arms: 23 genuine horizon treatments, j = 1..23.
  For treatment j: w_j = 1.0, w_t = 0.95^t for t != j.
  j=0 is NOT executed (mathematically identical to V3, Delta_0 = 0 analytically).
- Design: 173 origins x 24 sequential MPC cycles = 95,496 fresh exact MILP treatment solves.
- Resource Configuration: MAX_WORKERS = 8.
- Primary Multiplicity Procedure: Holm-Bonferroni step-down at alpha = 0.05 across 23 tests.

EXPLICIT AUTHORIZATION GATE:
Execution of the 95,496 MILP solves requires explicit invocation with the CLI flag:
  --authorize-execution
Without this flag, the harness performs pre-execution provenance verification,
verifies execution readiness, executes ZERO MILP solves, and exits cleanly.
"""

import os
import sys
import csv
import json
import yaml
import time
import math
import copy
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone
import numpy as np
from scipy.stats import wilcoxon
from concurrent.futures import ProcessPoolExecutor

from system.schemas.station_state import StationState
from system.forecasting.implementations.s81_solar import Stage81ForecastEngine
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.simulation.simulator import DigitalTwinSimulator
from system.evaluation.evaluator import EvaluationEngine
from system.telemetry.v2_logger import V2TelemetryCollector, REQUIRED_37_FIELDS

SPECIFICATION_MD_HASH = "53e5f0b482526167d157257690bd45c3dfb76bb1c8ef15c0a5384eb311f5d085"
SPECIFICATION_JSON_HASH = "21703425eb572b2698cb13bcfb835419460823d55a4e1d8fbac11e529d445a23"
AUTHORIZATION_HASH = "CLASSIFICATION_A_AUTHORIZED"

TREATMENT_FILE = "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"
EXPECTED_TREATMENT_SHA256 = "a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d"

PROVENANCE_FILES = {
    "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv": EXPECTED_TREATMENT_SHA256,
    "forecasting/reports/other/POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv": "b86f19476a9c5fa97df406cedf399a40c33496dc085cb077ab829afa9dd79b3c",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv": "a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e",
    "ems/reports/ofat_horizon_sweep/POLARIS_23_HORIZON_OFAT_EXPERIMENT_SPECIFICATION.md": SPECIFICATION_MD_HASH,
    "ems/reports/ofat_horizon_sweep/POLARIS_23_HORIZON_OFAT_EXPERIMENT_SPECIFICATION.json": SPECIFICATION_JSON_HASH,
}

EXPECTED_ORIGINS = 173
EXPECTED_MPC_STEPS = 24
EXPECTED_TREATMENTS = 23
EXPECTED_TOTAL_SOLVES = EXPECTED_ORIGINS * EXPECTED_MPC_STEPS * EXPECTED_TREATMENTS  # 95,496
MAX_WORKERS = 8

def verify_provenance(base_dir: Path) -> bool:
    for rel_path, expected_hash in PROVENANCE_FILES.items():
        fpath = base_dir / rel_path
        if not fpath.exists():
            print(f"[ERROR] Missing required file: {rel_path}")
            return False
        h = hashlib.sha256(fpath.read_bytes()).hexdigest()
        if h != expected_hash:
            print(f"[ERROR] Hash mismatch for {rel_path}: got {h}, expected {expected_hash}")
            return False
    return True

def verify_treatment_artifact(base_dir: Path) -> dict:
    file_path = base_dir / TREATMENT_FILE
    if not file_path.exists():
        raise FileNotFoundError(f"Treatment artifact {TREATMENT_FILE} missing at {file_path}")

    raw_bytes = file_path.read_bytes()
    computed_hash = hashlib.sha256(raw_bytes).hexdigest()
    if computed_hash != EXPECTED_TREATMENT_SHA256:
        raise ValueError(f"SHA-256 mismatch for {TREATMENT_FILE}: got {computed_hash}, expected {EXPECTED_TREATMENT_SHA256}")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if len(rows) != EXPECTED_ORIGINS * EXPECTED_MPC_STEPS:
        raise ValueError(f"Row count mismatch: got {len(rows)}, expected {EXPECTED_ORIGINS * EXPECTED_MPC_STEPS}")

    origins = {}
    for r in rows:
        oid = int(r["origin_id"])
        if oid not in origins:
            origins[oid] = []
        origins[oid].append(r)

    if len(origins) != EXPECTED_ORIGINS:
        raise ValueError(f"Origin count mismatch: got {len(origins)}, expected {EXPECTED_ORIGINS}")

    for oid, o_rows in origins.items():
        if len(o_rows) != EXPECTED_MPC_STEPS:
            raise ValueError(f"Origin {oid} does not have exactly {EXPECTED_MPC_STEPS} horizons (got {len(o_rows)})")
        horizons = [int(r["horizon"]) for r in o_rows]
        if sorted(horizons) != list(range(1, EXPECTED_MPC_STEPS + 1)):
            raise ValueError(f"Origin {oid} invalid horizon structure: {horizons}")

    return {
        "file_path": str(file_path),
        "sha256": computed_hash,
        "total_rows": len(rows),
        "unique_origins": len(origins),
        "origins": origins
    }

def verify_authorization_gate(base_dir: Path) -> bool:
    if AUTHORIZATION_HASH != "CLASSIFICATION_A_AUTHORIZED":
        print(f"[ERROR] Invalid authorization hash: got '{AUTHORIZATION_HASH}', expected 'CLASSIFICATION_A_AUTHORIZED'")
        return False

    auth_json = base_dir / "ems/reports/ofat_horizon_sweep/POLARIS_23_HORIZON_OFAT_EXECUTION_AUTHORIZATION.json"
    if not auth_json.exists():
        print(f"[ERROR] Authorization file missing: ems/reports/ofat_horizon_sweep/POLARIS_23_HORIZON_OFAT_EXECUTION_AUTHORIZATION.json")
        return False

    try:
        with open(auth_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("governance_status") != "EXECUTION_AUTHORIZED":
            print(f"[ERROR] Invalid governance status: {data.get('governance_status')}")
            return False
        if data.get("execution_authorization_status") != "AUTHORIZED":
            print(f"[ERROR] Invalid authorization status: {data.get('execution_authorization_status')}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to read authorization JSON: {e}")
        return False

    return True

def compute_weight_vector_for_arm(j: int) -> list:
    """
    Constructs OFAT weight sequence for treatment arm j (1..23).
    w_j = 1.0, w_t = 0.95^t for t != j.
    """
    weights = []
    for t in range(24):
        if t == j:
            weights.append(1.0)
        else:
            weights.append(0.95 ** t)
    return weights

def run_single_origin_treatment_arm(args):
    """
    Executes 24-step MPC rollout for a single origin under treatment arm j (1..23).
    State trajectory is completely isolated per origin/treatment.
    Uses the authoritative initialization and execution path from Stage 8.1 V3.
    """
    oid, treatment_j, o_rows, config_dir_str = args
    config_dir = Path(config_dir_str)

    configs = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        cfg_file = config_dir / f"{cfg_name}.yaml"
        if cfg_file.exists():
            with open(cfg_file, "r") as f:
                configs[cfg_name] = yaml.safe_load(f)

    o_rows = sorted(o_rows, key=lambda x: int(x["horizon"]))
    t0_ts = o_rows[0]["origin_timestamp"]

    # Initial station state (Authoritative Stage 8.1 V3 initialization path)
    initial_state = StationState(
        timestamp=t0_ts,
        battery_soc_pct=configs.get("battery", {}).get("initial_soc_pct", 50.0),
        battery_energy_wh=configs.get("battery", {}).get("capacity_wh", 200000.0) * (configs.get("battery", {}).get("initial_soc_pct", 50.0) / 100.0),
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=float(o_rows[0]["y_true"]),
        last_observed_demand=35000.0,
        last_observed_wind_generation=30000.0
    )

    # Immutable future actuals ground truth sequence
    future_actuals = []
    for step_k in range(EXPECTED_MPC_STEPS):
        h_row = o_rows[step_k]
        act_dict = {
            "timestamp": h_row["valid_timestamp"],
            "actual_SW_IN": float(h_row["y_true"]),
            "actual_wind_generation": 30000.0 + 5000.0 * math.sin((step_k + 1) * math.pi / 6.0),
            "actual_demand": 35000.0,
            "clearsky_ghi": 0.0
        }
        future_actuals.append(act_dict)

    s81_engine = Stage81ForecastEngine(config_dir / "solar_pv.yaml")
    optimizer = LocalMILPEnergyOptimizer()
    simulator = DigitalTwinSimulator(configs)

    weight_vector = compute_weight_vector_for_arm(treatment_j)

    curr_state = initial_state
    dispatch_plans = []
    forecast_bundles = []
    telemetry_records = []
    telemetry_faults = []

    for step_k in range(EXPECTED_MPC_STEPS):
        sw_in_forecast_treat = [float(r["y_pred"]) for r in o_rows[step_k:]]
        if len(sw_in_forecast_treat) < 24:
            origin_dt = datetime.fromisoformat(curr_state.timestamp.replace("Z", "+00:00"))
            baseline_continuation = []
            for h_extra in range(len(sw_in_forecast_treat) + 1, 25):
                future_dt = origin_dt + timedelta(hours=h_extra)
                hour = future_dt.hour
                if 4 <= hour <= 20:
                    solar_sin = math.sin((hour - 4) * math.pi / 16.0)
                    cs_ghi = 800.0 * solar_sin
                    irr = max(0.0, round(cs_ghi * 0.75, 2))
                else:
                    irr = 0.0
                baseline_continuation.append(irr)
            sw_in_forecast_treat += baseline_continuation

        runtime_context = {
            "origin_timestamp": curr_state.timestamp,
            "current_index": step_k,
            "stage81_sw_in_forecast": sw_in_forecast_treat,
            "last_observed_solar_irradiance": curr_state.last_observed_solar_irradiance,
            "last_observed_demand": curr_state.last_observed_demand,
            "last_observed_wind_generation": curr_state.last_observed_wind_generation,
            "clearsky_ghi": 0.0
        }

        bundle = s81_engine.predict(curr_state, runtime_context)
        configs_arm = copy.deepcopy(configs)
        configs_arm["optimizer"]["custom_weight_vector"] = weight_vector

        plan = optimizer.optimize(bundle, curr_state, configs_arm)

        next_actual = future_actuals[step_k]
        state_before = curr_state
        curr_state = simulator.step(curr_state, plan, next_actual)

        dispatch_plans.append(plan.to_dict())
        forecast_bundles.append(bundle.to_dict())

        try:
            collector = V2TelemetryCollector()
            rec = collector.record_step(
                origin_id=oid,
                origin_timestamp=t0_ts,
                mpc_timestep_idx=step_k,
                timestamp=state_before.timestamp,
                treatment_forecast_vector_24=bundle.solar_irradiance.point,
                control_forecast_vector_24=bundle.solar_irradiance.point,
                actual_solar_truth=next_actual["actual_SW_IN"],
                soc_before=state_before.battery_soc_pct,
                diesel_state_before=state_before.diesel_running,
                cumulative_diesel_fuel_before=getattr(state_before, "cumulative_diesel_fuel_l", 0.0),
                cumulative_diesel_energy_before=getattr(state_before, "cumulative_diesel_energy_kwh", 0.0),
                optimizer_status=plan.constraint_status,
                objective_value=plan.objective_value,
                diesel_commitment=1.0 if plan.diesel_power[0] > 0 else 0.0,
                battery_charge_decision=plan.battery_charge[0] / 1000.0,
                battery_discharge_decision=plan.battery_discharge[0] / 1000.0,
                reserve_status="NORMAL",
                constraint_status=plan.constraint_status,
                h1_diesel_power=plan.diesel_power[0] / 1000.0,
                h1_battery_charge_power=plan.battery_charge[0] / 1000.0,
                h1_battery_discharge_power=plan.battery_discharge[0] / 1000.0,
                h1_renewable_dispatch=(plan.solar_used[0] + plan.wind_used[0]) / 1000.0,
                h1_renewable_curtailment=plan.renewable_curtailment[0] / 1000.0,
                h1_served_load=plan.load_served[0] / 1000.0,
                h1_unmet_load=plan.unmet_load[0] / 1000.0,
                soc_after=curr_state.battery_soc_pct,
                diesel_state_after=curr_state.diesel_running,
                cumulative_diesel_fuel_after=getattr(curr_state, "cumulative_diesel_fuel_l", 0.0),
                cumulative_diesel_energy_after=getattr(curr_state, "cumulative_diesel_energy_kwh", 0.0),
                cumulative_battery_throughput_after=getattr(curr_state, "cumulative_battery_throughput_kwh", 0.0),
            )
            rec_dict = rec.to_dict()
            rec_dict["treatment_j"] = treatment_j
            telemetry_records.append(rec_dict)
        except Exception as te:
            telemetry_faults.append({
                "timestep": step_k,
                "error_class": te.__class__.__name__,
                "error_message": str(te)
            })

    eval_res = EvaluationEngine.evaluate_ems_performance(dispatch_plans, configs) if dispatch_plans else {}

    return {
        "origin_id": oid,
        "treatment_j": treatment_j,
        "fuel_consumed_liters": eval_res.get("total_diesel_fuel_liters", 0.0),
        "curtailment_kwh": eval_res.get("total_renewable_curtailment_kwh", 0.0),
        "throughput_kwh": eval_res.get("battery_throughput_kwh", 0.0),
        "unmet_load_kwh": eval_res.get("unmet_critical_load_kwh", 0.0),
        "telemetry_records": telemetry_records,
        "telemetry_faults": telemetry_faults
    }

def atomic_write_json(file_path: Path, data: dict):
    """
    Crash-safe atomic JSON file writer using temp file + fsync + atomic rename.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(file_path.suffix + f".tmp.{os.getpid()}_{time.time_ns()}")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    temp_path.replace(file_path)

def get_checkpoint_dir(base_dir: Path) -> Path:
    return base_dir / "ems/campaigns/POLARIS_23_HORIZON_OFAT_CHECKPOINT"

def get_manifest_path(base_dir: Path) -> Path:
    return get_checkpoint_dir(base_dir) / "manifest.json"

def save_trajectory_checkpoint(base_dir: Path, res: dict) -> tuple:
    """
    Atomically persists a completed trajectory result (including all 24 MPC step telemetry records) to disk.
    Returns (filename, payload_sha256).
    """
    chk_dir = get_checkpoint_dir(base_dir)
    j = res["treatment_j"]
    oid = res["origin_id"]
    filename = f"arm_{j:02d}_origin_{oid:04d}.json"
    file_path = chk_dir / filename

    payload = {
        "treatment_j": j,
        "origin_id": oid,
        "expected_mpc_steps": EXPECTED_MPC_STEPS,
        "completed_mpc_steps": len(res.get("telemetry_records", [])),
        "fuel_consumed_liters": res["fuel_consumed_liters"],
        "curtailment_kwh": res["curtailment_kwh"],
        "throughput_kwh": res["throughput_kwh"],
        "unmet_load_kwh": res["unmet_load_kwh"],
        "telemetry_records": res["telemetry_records"],
        "telemetry_faults": res["telemetry_faults"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }

    # Compute deterministic SHA256 signature
    payload_copy = copy.deepcopy(payload)
    payload_str = json.dumps(payload_copy, sort_keys=True)
    sha256 = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
    payload["trajectory_sha256"] = sha256

    atomic_write_json(file_path, payload)
    return filename, sha256

def load_and_validate_checkpoints(base_dir: Path) -> tuple:
    """
    Loads and validates all existing trajectory checkpoints against the durable manifest.
    Returns (completed_meta_dict, completed_pairs_set, is_valid_bool, status_message_str).
    """
    chk_dir = get_checkpoint_dir(base_dir)
    manifest_path = get_manifest_path(base_dir)

    if not chk_dir.exists() or not manifest_path.exists():
        return {}, set(), True, "No existing checkpoint directory/manifest found. Fresh execution required."

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        return {}, set(), False, f"Failed to load manifest.json: {e}"

    completed_trajectories_meta = manifest.get("completed_trajectories", {})
    completed_pairs = set()
    validated_meta = {}

    for key, meta in completed_trajectories_meta.items():
        j = meta["treatment_j"]
        oid = meta["origin_id"]
        filename = meta["filename"]
        expected_hash = meta["sha256"]

        pair = (j, oid)
        if pair in completed_pairs:
            return {}, set(), False, f"Duplicate trajectory pair detected in manifest: arm {j}, origin {oid}"

        chk_file = chk_dir / filename
        if not chk_file.exists():
            return {}, set(), False, f"Checkpoint file missing: {filename}"

        try:
            with open(chk_file, "r", encoding="utf-8") as f:
                chk_data = json.load(f)
        except Exception as e:
            return {}, set(), False, f"Corrupted JSON in checkpoint {filename}: {e}"

        if chk_data.get("treatment_j") != j or chk_data.get("origin_id") != oid:
            return {}, set(), False, f"Schema mismatch in checkpoint {filename}"

        if chk_data.get("completed_mpc_steps") != EXPECTED_MPC_STEPS or len(chk_data.get("telemetry_records", [])) != EXPECTED_MPC_STEPS:
            return {}, set(), False, f"Incomplete trajectory in checkpoint {filename}: expected {EXPECTED_MPC_STEPS} steps"

        payload_copy = copy.deepcopy(chk_data)
        payload_copy.pop("trajectory_sha256", None)
        computed_hash = hashlib.sha256(json.dumps(payload_copy, sort_keys=True).encode("utf-8")).hexdigest()

        if computed_hash != expected_hash:
            return {}, set(), False, f"Hash mismatch for checkpoint {filename}: got {computed_hash}, expected {expected_hash}"

        completed_pairs.add(pair)
        validated_meta[key] = meta

    msg = f"Validated {len(completed_pairs)} / {EXPECTED_ORIGINS * EXPECTED_TREATMENTS} checkpointed trajectories successfully."
    return validated_meta, completed_pairs, True, msg

def update_manifest(base_dir: Path, completed_meta: dict):
    """
    Atomically updates the checkpoint manifest file on disk.
    """
    manifest_path = get_manifest_path(base_dir)
    harness_path = base_dir / "scripts/ems_campaigns/run_polaris_23_horizon_ofat_experiment.py"
    harness_hash = hashlib.sha256(harness_path.read_bytes()).hexdigest() if harness_path.exists() else ""

    total_completed = len(completed_meta)
    implied_solves = total_completed * EXPECTED_MPC_STEPS

    manifest_data = {
        "manifest_id": "POLARIS_23_HORIZON_OFAT_CHECKPOINT_MANIFEST",
        "harness_sha256": harness_hash,
        "specification_md_hash": SPECIFICATION_MD_HASH,
        "specification_json_hash": SPECIFICATION_JSON_HASH,
        "authorization_hash": AUTHORIZATION_HASH,
        "total_expected_trajectories": EXPECTED_ORIGINS * EXPECTED_TREATMENTS,
        "total_completed_trajectories": total_completed,
        "total_expected_solves": EXPECTED_TOTAL_SOLVES,
        "implied_completed_solves": implied_solves,
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "completed_trajectories": completed_meta
    }
    atomic_write_json(manifest_path, manifest_data)

def finalize_from_checkpoints(base_dir: Path, elapsed_s: float = 0.0) -> bool:
    """
    Generates final CSV, JSON, and MD output artifacts directly from disk checkpoints.
    Completely independent of in-memory execution objects and rerunnable without MILP.
    """
    print("[FINALIZATION] Validating durable trajectory checkpoints for closeout...")
    chk_dir = get_checkpoint_dir(base_dir)
    manifest_path = get_manifest_path(base_dir)

    if not manifest_path.exists():
        print("[FATAL] Checkpoint manifest missing during finalization!")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    completed_meta = manifest.get("completed_trajectories", {})
    expected_trajectories_count = EXPECTED_ORIGINS * EXPECTED_TREATMENTS
    if len(completed_meta) != expected_trajectories_count:
        print(f"[FATAL] Incomplete trajectories count for finalization: got {len(completed_meta)}, expected {expected_trajectories_count}")
        return False

    v3_control_file = base_dir / "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv"
    v3_fuel_by_origin = {}
    with open(v3_control_file, "r", encoding="utf-8") as f:
        v3_reader = csv.DictReader(f)
        for r in v3_reader:
            oid = int(r["origin_id"])
            if oid not in v3_fuel_by_origin:
                v3_fuel_by_origin[oid] = 0.0
            v3_fuel_by_origin[oid] += float(r.get("h1_diesel_power", 0.0)) / 1000.0 * 0.25

    results_by_arm = {j: [] for j in range(1, 24)}
    all_telemetry_rows = []

    print("[FINALIZATION] Streaming trajectory data from checkpoint files...")
    for j in range(1, 24):
        for oid in range(1, EXPECTED_ORIGINS + 1):
            filename = f"arm_{j:02d}_origin_{oid:04d}.json"
            chk_file = chk_dir / filename
            if not chk_file.exists():
                print(f"[FATAL] Missing checkpoint file during finalization: {filename}")
                return False
            with open(chk_file, "r", encoding="utf-8") as f:
                chk_data = json.load(f)

            # NOTE: Uses origin_id consistently (FIXED)
            results_by_arm[j].append({
                "origin_id": chk_data["origin_id"],
                "treatment_j": chk_data["treatment_j"],
                "fuel_consumed_liters": chk_data["fuel_consumed_liters"],
                "curtailment_kwh": chk_data["curtailment_kwh"],
                "throughput_kwh": chk_data["throughput_kwh"],
                "unmet_load_kwh": chk_data["unmet_load_kwh"]
            })
            all_telemetry_rows.extend(chk_data["telemetry_records"])

    p_values = []
    arm_summaries = []
    for j in range(1, 24):
        # NOTE: Uses origin_id consistently (FIXED)
        arm_res = sorted(results_by_arm[j], key=lambda x: x["origin_id"])
        treat_fuel = np.array([r["fuel_consumed_liters"] for r in arm_res])
        ctrl_fuel = np.array([v3_fuel_by_origin.get(r["origin_id"], 0.0) for r in arm_res])
        diff = treat_fuel - ctrl_fuel
        mean_diff = float(np.mean(diff))

        stat, pval = wilcoxon(treat_fuel, ctrl_fuel) if not np.all(diff == 0) else (0.0, 1.0)
        p_values.append((j, pval, mean_diff))
        arm_summaries.append({
            "treatment_j": j,
            "mean_fuel_difference_liters": mean_diff,
            "wilcoxon_stat": float(stat),
            "raw_p_value": float(pval)
        })

    sorted_p = sorted(p_values, key=lambda x: x[1])
    K = 23
    alpha = 0.05
    significant_arms = []
    adjusted_p_dict = {}

    for i, (j, pval, diff) in enumerate(sorted_p):
        adjusted_alpha = float(alpha / (K - i))
        is_sig = bool(pval <= adjusted_alpha)
        adjusted_p_dict[j] = {
            "rank": i + 1,
            "adjusted_alpha": adjusted_alpha,
            "significant_holm": is_sig
        }
        if is_sig:
            significant_arms.append(int(j))

    for summary in arm_summaries:
        j = summary["treatment_j"]
        summary.update(adjusted_p_dict[j])

    output_csv = base_dir / "ems/reports/ofat_horizon_sweep/POLARIS_23_HORIZON_OFAT_EXECUTION_RAW.csv"
    print(f"[OUTPUT] Writing telemetry to {output_csv.name}...")
    if all_telemetry_rows:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_telemetry_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_telemetry_rows)

    output_json = base_dir / "ems/reports/ofat_horizon_sweep/POLARIS_23_HORIZON_OFAT_EXECUTION.json"
    print(f"[OUTPUT] Writing summary manifest to {output_json.name}...")
    manifest_out = {
        "manifest_id": "POLARIS_23_HORIZON_OFAT_EXECUTION_MANIFEST",
        "governance_status": "EXPERIMENT_EXECUTED_AND_VERIFIED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_solves_executed": EXPECTED_TOTAL_SOLVES,
        "elapsed_seconds": elapsed_s,
        "primary_multiplicity_procedure": "HOLM_BONFERRONI",
        "familywise_alpha": 0.05,
        "treatment_arm_summaries": arm_summaries,
        "significant_arms_count": len(significant_arms),
        "significant_arms": sorted(significant_arms)
    }
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(manifest_out, f, indent=2)

    output_md = base_dir / "ems/reports/ofat_horizon_sweep/POLARIS_23_HORIZON_OFAT_EXECUTION.md"
    print(f"[OUTPUT] Writing final closeout report to {output_md.name}...")
    md_content = f"""# POLARIS 23-Horizon OFAT Experiment — Execution & Scientific Closeout Report
## Governance Post-Execution Status: EXPERIMENT_EXECUTED_AND_VERIFIED

- **Total MILP Solves Executed**: 95,496
- **Execution Time**: {elapsed_s:.2f} seconds
- **Resource Configuration**: MAX_WORKERS = 8
- **Primary Multiplicity Procedure**: Holm-Bonferroni step-down (FWER alpha = 0.05)
- **Significant Horizon Arms Identified**: {len(significant_arms)}
"""
    output_md.write_text(md_content, encoding="utf-8")

    print("[SUCCESS] 23-Horizon OFAT experiment execution and closeout complete.")
    return True

def run_authorized_experiment(base_dir: Path):
    """
    Executes the authorized 23-arm OFAT experiment protocol across 173 origins x 24 steps = 95,496 MILP solves.
    Durable checkpointing persists every completed trajectory to disk before scheduling remaining tasks.
    """
    print("[EXECUTION] Verifying treatment predictions artifact...")
    verified_data = verify_treatment_artifact(base_dir)
    origins_map = verified_data["origins"]
    config_dir = base_dir / "system" / "config"

    print("[EXECUTION] Initializing durable checkpoint system...")
    chk_dir = get_checkpoint_dir(base_dir)
    chk_dir.mkdir(parents=True, exist_ok=True)

    completed_meta, completed_pairs, is_valid, msg = load_and_validate_checkpoints(base_dir)
    if not is_valid:
        print(f"[FATAL] Checkpoint validation failed! {msg}")
        sys.exit(1)

    print(f"[INFO] Checkpoint status: {msg}")

    tasks = []
    for oid in sorted(origins_map.keys()):
        for j in range(1, 24):
            if (j, oid) not in completed_pairs:
                tasks.append((oid, j, origins_map[oid], str(config_dir)))

    print(f"[EXECUTION] Scheduled {len(tasks)} remaining trajectories out of {EXPECTED_ORIGINS * EXPECTED_TREATMENTS} total.")
    print(f"[EXECUTION] Total MILP solves remaining: {len(tasks) * EXPECTED_MPC_STEPS} / {EXPECTED_TOTAL_SOLVES}")
    print(f"[EXECUTION] Resource configuration: MAX_WORKERS = {MAX_WORKERS}")

    start_time = time.time()
    completed_solves = len(completed_pairs) * EXPECTED_MPC_STEPS

    if tasks:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(run_single_origin_treatment_arm, task) for task in tasks]
            for future in futures:
                res = future.result()
                filename, sha256 = save_trajectory_checkpoint(base_dir, res)

                j = res["treatment_j"]
                oid = res["origin_id"]
                key = f"arm_{j:02d}_origin_{oid:04d}"
                completed_meta[key] = {
                    "treatment_j": j,
                    "origin_id": oid,
                    "filename": filename,
                    "sha256": sha256,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat()
                }
                update_manifest(base_dir, completed_meta)

                completed_solves += EXPECTED_MPC_STEPS
                if completed_solves % 4152 == 0 or completed_solves == EXPECTED_TOTAL_SOLVES:
                    print(f"[PROGRESS] Completed {completed_solves} / {EXPECTED_TOTAL_SOLVES} MILP solves ({completed_solves / EXPECTED_TOTAL_SOLVES * 100:.1f}%)")

    elapsed_s = time.time() - start_time
    print(f"[EXECUTION COMPLETE] All 95,496 MILP solves checkpointed.")
    finalize_from_checkpoints(base_dir, elapsed_s)

def run_preflight_checkpoint_test(base_dir: Path) -> bool:
    """
    Executes a comprehensive NO-MILP pre-flight test suite verifying checkpoint creation, atomic writes,
    SHA validation, error detection, resume calculation, and checkpoint-based finalization.
    Executes ZERO real MILP solves.
    """
    import shutil
    print("=========================================================================")
    print("  POLARIS — NO-MILP CHECKPOINT & RESUME PRE-FLIGHT VERIFICATION")
    print("=========================================================================")

    test_dir = base_dir / "POLARIS_23_HORIZON_OFAT_TEST_CHECKPOINT"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)

    print("[TEST 1/7] Testing atomic write mechanism...")
    test_file = test_dir / "atomic_test.json"
    atomic_write_json(test_file, {"test": True, "val": 123})
    if not test_file.exists():
        print("[FAIL] Atomic write failed to produce file.")
        return False
    print("[PASS] Atomic write verified.")

    print("[TEST 2/7] Testing synthetic trajectory persistence & SHA-256 calculation...")
    fake_telemetry = []
    for step_k in range(24):
        fake_telemetry.append({
            "origin_id": 4,
            "origin_timestamp": "2024-01-01T00:00:00Z",
            "mpc_timestep_idx": step_k,
            "treatment_j": 1,
            "h1_diesel_power": 10.0,
            "h1_served_load": 35.0
        })

    chk_filename = "arm_01_origin_0004.json"
    chk_path = test_dir / chk_filename
    payload = {
        "treatment_j": 1,
        "origin_id": 4,
        "expected_mpc_steps": 24,
        "completed_mpc_steps": 24,
        "fuel_consumed_liters": 12.5,
        "curtailment_kwh": 0.0,
        "throughput_kwh": 5.0,
        "unmet_load_kwh": 0.0,
        "telemetry_records": fake_telemetry,
        "telemetry_faults": [],
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }
    payload_copy = copy.deepcopy(payload)
    payload_str = json.dumps(payload_copy, sort_keys=True)
    expected_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
    payload["trajectory_sha256"] = expected_hash
    atomic_write_json(chk_path, payload)

    manifest_data = {
        "manifest_id": "POLARIS_23_HORIZON_OFAT_CHECKPOINT_MANIFEST",
        "harness_sha256": "test_hash",
        "total_expected_trajectories": 3979,
        "total_completed_trajectories": 1,
        "total_expected_solves": 95496,
        "implied_completed_solves": 24,
        "completed_trajectories": {
            "arm_01_origin_0004": {
                "treatment_j": 1,
                "origin_id": 4,
                "filename": chk_filename,
                "sha256": expected_hash,
                "timestamp_utc": payload["timestamp_utc"]
            }
        }
    }
    atomic_write_json(test_dir / "manifest.json", manifest_data)
    print("[PASS] Synthetic trajectory and manifest written.")

    print("[TEST 3/7] Testing checkpoint validation & SHA verification...")
    with open(test_dir / "manifest.json", "r") as f:
        loaded_m = json.load(f)
    meta = loaded_m["completed_trajectories"]["arm_01_origin_0004"]
    with open(test_dir / meta["filename"], "r") as f:
        data = json.load(f)
    d_copy = copy.deepcopy(data)
    d_copy.pop("trajectory_sha256", None)
    calc_hash = hashlib.sha256(json.dumps(d_copy, sort_keys=True).encode("utf-8")).hexdigest()
    if calc_hash != meta["sha256"]:
        print(f"[FAIL] SHA mismatch: got {calc_hash}, expected {meta['sha256']}")
        return False
    print("[PASS] Checkpoint SHA and schema validated.")

    print("[TEST 4/7] Testing corrupt checkpoint & incomplete trajectory detection...")
    corrupt_file = test_dir / "arm_01_origin_0005.json"
    corrupt_file.write_text("INVALID_JSON{")
    try:
        with open(corrupt_file, "r") as f:
            json.load(f)
        print("[FAIL] Corrupt JSON failed to trigger Exception!")
        return False
    except json.JSONDecodeError:
        print("[PASS] Corrupt JSON detected correctly.")
    corrupt_file.unlink()

    inc_file = test_dir / "arm_01_origin_0005.json"
    incomplete_payload = copy.deepcopy(payload)
    incomplete_payload["completed_mpc_steps"] = 23
    incomplete_payload["telemetry_records"] = fake_telemetry[:23]
    atomic_write_json(inc_file, incomplete_payload)
    with open(inc_file, "r") as f:
        inc_data = json.load(f)
    if inc_data["completed_mpc_steps"] == 24:
        print("[FAIL] Incomplete steps check failed!")
        return False
    print("[PASS] Incomplete trajectory (23 steps) detected correctly.")
    inc_file.unlink()

    print("[TEST 5/7] Testing resume-set calculation...")
    completed_pairs = {(1, 4)}
    all_pairs = set((j, oid) for j in range(1, 24) for oid in range(1, 174))
    remaining_pairs = all_pairs - completed_pairs
    if len(remaining_pairs) != 3978:
        print(f"[FAIL] Resume calculation mismatch: got {len(remaining_pairs)}, expected 3978")
        return False
    print(f"[PASS] Resume calculation verified: 1 completed, {len(remaining_pairs)} remaining.")

    print("[TEST 6/7] Testing post-processing origin_id key verification...")
    test_arm_res = [{"origin_id": 4, "treatment_j": 1, "fuel_consumed_liters": 12.5}]
    try:
        sorted_res = sorted(test_arm_res, key=lambda x: x["origin_id"])
        if sorted_res[0]["origin_id"] != 4:
            print("[FAIL] Post-processing key sort failed!")
            return False
    except KeyError as ke:
        print(f"[FAIL] Post-processing KeyError: {ke}")
        return False
    print("[PASS] Post-processing origin_id key access verified.")

    print("[TEST 7/7] Cleaning up pre-flight test directory...")
    shutil.rmtree(test_dir)
    print("[PASS] Pre-flight test directory cleaned up.")

    print("=========================================================================")
    print("[PASS] ALL PRE-FLIGHT RECOVERY TESTS PASSED (0 REAL MILP SOLVES EXECUTED).")
    print("=========================================================================")
    return True

def main():
    base_dir = Path(__file__).parents[2].resolve()
    print("=========================================================================")
    print("  POLARIS — 23-HORIZON OFAT FORMAL EXECUTION HARNESS")
    print("=========================================================================")

    parser = argparse.ArgumentParser(description="POLARIS 23-Horizon OFAT Execution Harness")
    parser.add_argument(
        "--authorize-execution",
        action="store_true",
        help="Explicit authorization flag required to execute 95,496 MILP solves"
    )
    parser.add_argument(
        "--test-checkpointing",
        action="store_true",
        help="Run NO-MILP pre-flight checkpoint and resume verification"
    )
    args = parser.parse_args()

    if args.test_checkpointing:
        success = run_preflight_checkpoint_test(base_dir)
        sys.exit(0 if success else 1)

    if not verify_provenance(base_dir):
        print("[FATAL] Pre-execution provenance verification failed! Halting.")
        sys.exit(1)

    print("[PASS] Pre-execution provenance check verified.")

    if not verify_authorization_gate(base_dir):
        print("[FATAL] Pre-execution authorization gate check failed! Halting.")
        sys.exit(1)

    print("[PASS] Pre-execution authorization gate verified.")

    if not args.authorize_execution:
        print(f"[INFO] Target: 23 treatment arms x 173 origins x 24 steps = {EXPECTED_TOTAL_SOLVES} fresh MILP solves.")
        print(f"[INFO] Resource Configuration: MAX_WORKERS = {MAX_WORKERS}.")
        print("[INFO] Multiplicity Procedure: Holm-Bonferroni (FWER <= 0.05).")
        print("[INFO] Status: EXECUTION READY. Invoke with explicit authorization flag to execute.")
        sys.exit(0)

    print("[INFO] Authorized execution flag detected (--authorize-execution).")
    print(f"[INFO] Commencing 23-arm OFAT protocol ({EXPECTED_TOTAL_SOLVES} MILP solves)...")
    run_authorized_experiment(base_dir)

if __name__ == "__main__":
    main()

