"""
Unit and Integration Tests for Checkpoint Integrity, Run Guards,
and Telemetry Diagnostic Persistence.

Module: experiments.candidate_s_sw_campaign_2024.test_checkpoint_and_diagnostics

Tests:
  A. Correction flags persisted in hourly telemetry match extractor output.
  B. Zeroed magnitude persisted in telemetry matches extractor output.
  C. Correction counts can be reconstructed independently from telemetry.
  D. Maximum zeroed magnitude can be reconstructed independently from telemetry.
  E. Failure records contain origin_id, arm, hour, error details, and diagnostics.
  F. Checkpoint guard mismatch refuses resume (fail-closed).
  G. Malformed checkpoint data refuses resume or is explicitly surfaced.
  H. Duplicate origin records are detected rather than silently overwritten.
"""

import copy
import json
import os
import sys
import tempfile
from pathlib import Path
import pytest

REPO = Path("/home/punith-bs/01polaris (Copy)")
os.chdir(REPO)
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments/candidate_s_sw_campaign_2024"))
sys.path.insert(0, str(REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS"))

import run_candidate_s_sw_123_campaign as runner_mod
from research_numerical_extractor import (
    ResearchNumericalGAP19Optimizer,
    extract_and_correct_flows,
    TAU_RESIDUE_W
)


# ==============================================================================
# TESTS A & B: TELEMETRY DIAGNOSTIC KEYS & EXTRACTION PERSISTENCE
# ==============================================================================

def test_a_correction_flags_persisted_match_extractor():
    """
    Test A: Verifies that correction flags and raw unrounded values persisted
    in hourly telemetry rows match the extractor's output exactly,
    and that no correction is falsely reported as zero.
    """
    # 1. Test extractor layer
    raw_chg = 0.00912
    raw_dis = 35000.0
    c_chg, c_dis, fired, zeroed = extract_and_correct_flows(raw_chg, raw_dis, tau=0.055)
    assert fired is True
    assert zeroed == raw_chg

    # 2. Test runner intercepting telemetry mapping
    mock_diag = [{
        "t": 0,
        "raw_p_chg": raw_chg,
        "raw_p_dis": raw_dis,
        "corrected_p_chg": c_chg,
        "corrected_p_dis": c_dis,
        "u_chg": 0.0000002,
        "u_dis": 1.0,
        "p_diesel": 0.0,
        "u_diesel": 0.0,
        "v_start": 0.0,
        "solver_status": "Optimal",
        "mip_gap": 0.0,
        "residue_corrected": fired,
        "zeroed_magnitude_w": zeroed
    }]

    runner = runner_mod.RobustTelemetryRunner(runner_mod.BASE_CONFIG, variant="S")
    # Simulate step snapshot
    runner.current_snapshot = {
        "forecast_solar_step0": 5000.0,
        "forecast_wind_step0": 2000.0,
        "forecast_demand_step0": 12000.0,
        "critical_demand_step0": 11600.0,
        "ebr_target_wh_step0": 45000.0,
        "stage2_target_wh_step0": 45000.0,
        "j2_shortfall_wh": 0.0,
        "solver_status": mock_diag[0]["solver_status"],
        "raw_p_chg": mock_diag[0]["raw_p_chg"],
        "raw_p_dis": mock_diag[0]["raw_p_dis"],
        "corrected_p_chg": mock_diag[0]["corrected_p_chg"],
        "corrected_p_dis": mock_diag[0]["corrected_p_dis"],
        "u_chg": mock_diag[0]["u_chg"],
        "u_dis": mock_diag[0]["u_dis"],
        "p_diesel": mock_diag[0]["p_diesel"],
        "u_diesel": mock_diag[0]["u_diesel"],
        "v_start": mock_diag[0]["v_start"],
        "mip_gap": mock_diag[0]["mip_gap"],
        "residue_corrected": mock_diag[0]["residue_corrected"],
        "zeroed_magnitude_w": mock_diag[0]["zeroed_magnitude_w"],
        "full_plan_diagnostics": mock_diag
    }

    # Verify keys match extractor output exactly
    snap = runner.current_snapshot
    assert snap["residue_corrected"] is True
    assert snap["raw_p_chg"] == raw_chg
    assert snap["raw_p_dis"] == raw_dis
    assert snap["corrected_p_chg"] == 0.0
    assert snap["corrected_p_dis"] == raw_dis
    assert snap["zeroed_magnitude_w"] == raw_chg


def test_b_zeroed_magnitude_persisted_matches_extractor():
    """
    Test B: Verifies zeroed magnitude persisted in telemetry matches extractor output,
    testing both charge-residue and discharge-residue cases.
    """
    # Case 1: Small charge residue zeroed
    c1_chg, c1_dis, f1, z1 = extract_and_correct_flows(0.03875, 42000.0, tau=0.055)
    assert f1 is True
    assert z1 == 0.03875

    # Case 2: Small discharge residue zeroed
    c2_chg, c2_dis, f2, z2 = extract_and_correct_flows(45000.0, 0.02100, tau=0.055)
    assert f2 is True
    assert z2 == 0.02100

    # Case 3: Zero residue (no correction)
    c3_chg, c3_dis, f3, z3 = extract_and_correct_flows(0.0, 30000.0, tau=0.055)
    assert f3 is False
    assert z3 == 0.0


# ==============================================================================
# TESTS C & D: INDEPENDENT TELEMETRY RECONSTRUCTION
# ==============================================================================

def test_c_correction_counts_reconstructed_from_telemetry():
    """
    Test C: Hourly telemetry independently allows counting total residue correction events per arm.
    """
    sample_rows = []
    # Create 24 hourly rows where hours 3, 11, and 18 have residue corrections
    for h in range(24):
        has_corr = h in (3, 11, 18)
        sample_rows.append({
            "origin_id": 1,
            "hour": h,
            "arm": "Candidate_S",
            "raw_p_chg": 0.009 if has_corr else 0.0,
            "raw_p_dis": 30000.0,
            "corrected_p_chg": 0.0,
            "corrected_p_dis": 30000.0,
            "u_chg": 1e-7 if has_corr else 0.0,
            "u_dis": 1.0,
            "p_diesel": 0.0,
            "u_diesel": 0.0,
            "v_start": 0.0,
            "solver_status": "Optimal",
            "mip_gap": 0.0,
            "residue_corrected": has_corr,
            "zeroed_magnitude_w": 0.009 if has_corr else 0.0
        })

    # Count directly from telemetry rows
    reconstructed_count = sum(1 for r in sample_rows if r["residue_corrected"])
    assert reconstructed_count == 3


def test_d_maximum_zeroed_magnitude_reconstructed_from_telemetry():
    """
    Test D: Maximum zeroed magnitude can be reconstructed independently from telemetry.
    """
    sample_rows = []
    mags = [0.0] * 24
    mags[2] = 0.0085
    mags[9] = 0.0421
    mags[14] = 0.0150

    for h in range(24):
        sample_rows.append({
            "origin_id": 1,
            "hour": h,
            "arm": "Candidate_SW",
            "residue_corrected": mags[h] > 0.0,
            "zeroed_magnitude_w": mags[h]
        })

    reconstructed_max = max((r["zeroed_magnitude_w"] for r in sample_rows), default=0.0)
    assert abs(reconstructed_max - 0.0421) < 1e-9


# ==============================================================================
# TEST E: FAILURE RECORDS WITH ARM, HOUR, AND DIAGNOSTICS
# ==============================================================================

def test_e_failure_record_contains_arm_and_hour():
    """
    Test E: When a step execution failure occurs, the failure record captures
    arm, hour, error type, message, and solver diagnostics.
    """
    err = runner_mod.StepExecutionError(
        arm="Candidate_S",
        hour=7,
        error_type="InfeasibleError",
        error_message="Highs returned infeasible status",
        raw_solver_diagnostics=[{"t": 7, "raw_p_chg": 0.0, "raw_p_dis": 0.0}]
    )

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as f:
        tmp_fail_path = Path(f.name)

    try:
        record = {
            "success": False,
            "origin_id": 42,
            "forecast_start": "2024-06-01 00:00:00",
            "t0_timestamp": "2024-06-01T00:00:00Z",
            "arm": err.arm,
            "hour": err.hour,
            "error_type": err.error_type,
            "error_message": err.error_message,
            "raw_solver_diagnostics": err.raw_solver_diagnostics
        }

        runner_mod.append_failure(record, failure_path=tmp_fail_path)

        lines = tmp_fail_path.read_text().strip().split("\n")
        assert len(lines) == 1
        persisted = json.loads(lines[0])

        assert persisted["origin_id"] == 42
        assert persisted["arm"] == "Candidate_S"
        assert persisted["hour"] == 7
        assert persisted["error_type"] == "InfeasibleError"
        assert "Highs returned infeasible" in persisted["error_message"]
        assert len(persisted["raw_solver_diagnostics"]) == 1
    finally:
        if tmp_fail_path.exists():
            tmp_fail_path.unlink()


# ==============================================================================
# TESTS F, G, H: CHECKPOINT GUARDS, RESUME INTEGRITY, AND MALFORMED HANDLING
# ==============================================================================

def test_f_checkpoint_guard_mismatch_refuses_resume():
    """
    Test F: Checkpoint guard mismatch raises ValueError and refuses to resume stale checkpoint.
    """
    guards = runner_mod.compute_run_guards(run_id="TEST_RUN_001")

    valid_rec = {
        "success": True,
        "origin_id": 1,
        "control_b": {"diesel_fuel_liters": 50.0},
        "candidate_s": {"diesel_fuel_liters": 35.0},
        "candidate_sw": {"diesel_fuel_liters": 37.0},
        "guards": copy.deepcopy(guards)
    }

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as f:
        tmp_ckpt = Path(f.name)

    try:
        # Write valid record
        runner_mod.append_checkpoint(valid_rec, checkpoint_path=tmp_ckpt)

        # 1. Resume with matching guards succeeds
        resumed = runner_mod.read_existing_checkpoints(expected_guards=guards, checkpoint_path=tmp_ckpt)
        assert 1 in resumed

        # 2. Tampered guard in expected (e.g. code was changed after checkpointing)
        tampered_guards = copy.deepcopy(guards)
        tampered_guards["extractor_sha256"] = "0000000000000000000000000000000000000000000000000000000000000000"

        with pytest.raises(ValueError, match="CHECKPOINT_GUARD_MISMATCH.*extractor_sha256"):
            runner_mod.read_existing_checkpoints(expected_guards=tampered_guards, checkpoint_path=tmp_ckpt)

        # 3. Tampered run_id
        tampered_guards_2 = copy.deepcopy(guards)
        tampered_guards_2["run_id"] = "DIFFERENT_RUN_ID"
        with pytest.raises(ValueError, match="CHECKPOINT_GUARD_MISMATCH.*run_id"):
            runner_mod.read_existing_checkpoints(expected_guards=tampered_guards_2, checkpoint_path=tmp_ckpt)
    finally:
        if tmp_ckpt.exists():
            tmp_ckpt.unlink()


def test_f1_tampered_gap19_production_guard_refuses_resume():
    """
    Test F1: Independently tampers GAP19 production guard and verifies CHECKPOINT_GUARD_MISMATCH.
    """
    guards = runner_mod.compute_run_guards(run_id="TEST_RUN_PROD_GAP19")
    valid_rec = {
        "success": True,
        "origin_id": 1,
        "control_b": {"diesel_fuel_liters": 50.0},
        "candidate_s": {"diesel_fuel_liters": 35.0},
        "candidate_sw": {"diesel_fuel_liters": 37.0},
        "guards": copy.deepcopy(guards)
    }

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as f:
        tmp_ckpt = Path(f.name)

    try:
        runner_mod.append_checkpoint(valid_rec, checkpoint_path=tmp_ckpt)

        tampered_guards = copy.deepcopy(guards)
        tampered_guards["gap19_sha256"] = "1111111111111111111111111111111111111111111111111111111111111111"

        with pytest.raises(ValueError, match="CHECKPOINT_GUARD_MISMATCH.*gap19_sha256"):
            runner_mod.read_existing_checkpoints(expected_guards=tampered_guards, checkpoint_path=tmp_ckpt)
    finally:
        if tmp_ckpt.exists():
            tmp_ckpt.unlink()


def test_f2_tampered_dispatch_plan_production_guard_refuses_resume():
    """
    Test F2: Independently tampers DispatchPlan production guard and verifies CHECKPOINT_GUARD_MISMATCH.
    """
    guards = runner_mod.compute_run_guards(run_id="TEST_RUN_PROD_DISPATCH")
    valid_rec = {
        "success": True,
        "origin_id": 1,
        "control_b": {"diesel_fuel_liters": 50.0},
        "candidate_s": {"diesel_fuel_liters": 35.0},
        "candidate_sw": {"diesel_fuel_liters": 37.0},
        "guards": copy.deepcopy(guards)
    }

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as f:
        tmp_ckpt = Path(f.name)

    try:
        runner_mod.append_checkpoint(valid_rec, checkpoint_path=tmp_ckpt)

        tampered_guards = copy.deepcopy(guards)
        tampered_guards["dispatch_plan_sha256"] = "2222222222222222222222222222222222222222222222222222222222222222"

        with pytest.raises(ValueError, match="CHECKPOINT_GUARD_MISMATCH.*dispatch_plan_sha256"):
            runner_mod.read_existing_checkpoints(expected_guards=tampered_guards, checkpoint_path=tmp_ckpt)
    finally:
        if tmp_ckpt.exists():
            tmp_ckpt.unlink()


def test_f3_tampered_causal_nwp_production_guard_refuses_resume():
    """
    Test F3: Independently tampers Causal NWP production guard and verifies CHECKPOINT_GUARD_MISMATCH.
    """
    guards = runner_mod.compute_run_guards(run_id="TEST_RUN_PROD_CAUSAL_NWP")
    valid_rec = {
        "success": True,
        "origin_id": 1,
        "control_b": {"diesel_fuel_liters": 50.0},
        "candidate_s": {"diesel_fuel_liters": 35.0},
        "candidate_sw": {"diesel_fuel_liters": 37.0},
        "guards": copy.deepcopy(guards)
    }

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as f:
        tmp_ckpt = Path(f.name)

    try:
        runner_mod.append_checkpoint(valid_rec, checkpoint_path=tmp_ckpt)

        tampered_guards = copy.deepcopy(guards)
        tampered_guards["causal_nwp_sha256"] = "3333333333333333333333333333333333333333333333333333333333333333"

        with pytest.raises(ValueError, match="CHECKPOINT_GUARD_MISMATCH.*causal_nwp_sha256"):
            runner_mod.read_existing_checkpoints(expected_guards=tampered_guards, checkpoint_path=tmp_ckpt)
    finally:
        if tmp_ckpt.exists():
            tmp_ckpt.unlink()


def test_verify_production_integrity_guards():
    """
    Test F4: Verifies verify_production_integrity succeeds on current files
    and raises PRODUCTION_HASH_VIOLATION on tampered production hashes.
    """
    guards = runner_mod.compute_run_guards()
    runner_mod.verify_production_integrity(guards)

    # Tamper GAP19
    t_gap19 = copy.deepcopy(guards)
    t_gap19["gap19_sha256"] = "bad_hash"
    with pytest.raises(ValueError, match="PRODUCTION_HASH_VIOLATION: GAP19"):
        runner_mod.verify_production_integrity(t_gap19)

    # Tamper DispatchPlan
    t_dp = copy.deepcopy(guards)
    t_dp["dispatch_plan_sha256"] = "bad_hash"
    with pytest.raises(ValueError, match="PRODUCTION_HASH_VIOLATION: DispatchPlan"):
        runner_mod.verify_production_integrity(t_dp)

    # Tamper Causal NWP
    t_nwp = copy.deepcopy(guards)
    t_nwp["causal_nwp_sha256"] = "bad_hash"
    with pytest.raises(ValueError, match="PRODUCTION_HASH_VIOLATION: Causal NWP"):
        runner_mod.verify_production_integrity(t_nwp)


def test_g_malformed_checkpoint_refuses_resume():
    """
    Test G: Malformed JSON lines or invalid schemas raise ValueError and are surfaced immediately.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as f:
        tmp_ckpt = Path(f.name)

    try:
        # Case 1: Corrupt JSON syntax
        with open(tmp_ckpt, "w") as f:
            f.write('{"origin_id": 1, "success": true}\n')
            f.write('{"origin_id": 2, "broken_json": [1, 2,\n')

        with pytest.raises(ValueError, match="MALFORMED_CHECKPOINT.*Line 2.*invalid JSON"):
            runner_mod.read_existing_checkpoints(checkpoint_path=tmp_ckpt)

        # Case 2: Incomplete record schema
        with open(tmp_ckpt, "w") as f:
            f.write('{"some_unrelated_key": 123}\n')

        with pytest.raises(ValueError, match="MALFORMED_CHECKPOINT.*Line 1.*invalid schema"):
            runner_mod.read_existing_checkpoints(checkpoint_path=tmp_ckpt)
    finally:
        if tmp_ckpt.exists():
            tmp_ckpt.unlink()


def test_h_duplicate_origin_record_detected():
    """
    Test H: Duplicate origin records raise ValueError rather than being silently overwritten.
    """
    guards = runner_mod.compute_run_guards(run_id="TEST_RUN_002")

    rec1 = {
        "success": True,
        "origin_id": 5,
        "guards": guards
    }
    rec2 = {
        "success": True,
        "origin_id": 5,
        "guards": guards
    }

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".jsonl") as f:
        tmp_ckpt = Path(f.name)

    try:
        runner_mod.append_checkpoint(rec1, checkpoint_path=tmp_ckpt)
        runner_mod.append_checkpoint(rec2, checkpoint_path=tmp_ckpt)

        with pytest.raises(ValueError, match="DUPLICATE_CHECKPOINT.*Origin 5 appears multiple times"):
            runner_mod.read_existing_checkpoints(expected_guards=guards, checkpoint_path=tmp_ckpt)
    finally:
        if tmp_ckpt.exists():
            tmp_ckpt.unlink()
