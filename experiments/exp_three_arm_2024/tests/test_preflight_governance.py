"""Fail-closed governance checks (synthetic repo under tmp_path; no data file is read; no solver).

A TEST-ONLY fully approved configuration and signed record are used as a positive control, so each
negative test shows that exactly one missing item is enough to refuse."""
import json
import os

import pytest

import preflight as pf
import run_three_arm_2024 as r
import synthetic_fixtures as sf


def _approved_repo(tmp_path):
    repo = sf.build_fake_repo(tmp_path)
    cfg = sf.approve_everything(pf.load_config(repo))
    sf.write_cfg(repo, cfg)
    sf.write_manifest(repo)
    sf.freeze_prereg(repo)
    return repo, cfg


# ---------------------------------------------------------------- the real package config
def test_real_config_is_frozen_and_decisions_resolved():
    """State after the M9 freeze: D2, D4, D6, D10 approved by the project lead (M6-M8); D1, D3, D5, D7, D7a, D8,
    D10a and BUD resolved by delegated technical authority (D8 after the device-venv pass); D11 approved by
    existing authority (internal use); config frozen. (Before the freeze: D8 CONDITIONALLY APPROVED, frozen false.)"""
    cfg = sf.load_real_cfg()
    assert cfg["frozen"] is True
    assert pf.check_decisions(cfg, pf.EXECUTION_DECISIONS) == []
    assert pf.check_decisions(cfg, pf.CALIBRATION_DECISIONS) == []
    fails = []
    for d in ("D1", "D3", "D5", "D7", "D7a", "D8", "D10a", "BUD"):
        assert cfg["decisions"][d]["status"] == "RESOLVED BY DELEGATED TECHNICAL AUTHORITY", d
        assert "M9" in cfg["decisions"][d]["authority"], d
    assert cfg["decisions"]["D11"]["status"] == "APPROVED BY EXISTING AUTHORITY"
    assert cfg["decisions"]["D11-PUB"]["status"].startswith("BLOCKED")
    assert "D11-PUB" not in pf.EXECUTION_DECISIONS and "D11-PUB" not in pf.CALIBRATION_DECISIONS
    for d in ("D2", "D4"):
        assert cfg["decisions"][d]["status"] == "APPROVED" and "M6" in cfg["decisions"][d]["evidence"]
        assert not any(f"decision {d} " in f for f in fails), d
    assert cfg["decisions"]["D6"]["status"] == "APPROVED" and "M8" in cfg["decisions"]["D6"]["evidence"]
    assert not any("decision D6 " in f for f in fails)
    assert cfg["decisions"]["D10"]["status"] == "APPROVED" and "M7" in cfg["decisions"]["D10"]["evidence"]
    assert not any("decision D10 " in f for f in fails)


def test_real_config_gates_resolved():
    cfg = sf.load_real_cfg()
    fails = pf.check_gates(cfg)
    assert not any("E1_holm_family" in f for f in fails)
    assert cfg["gates"]["E1_holm_family"] == ["A", "C"]
    assert not any("S4_strict" in f for f in fails)            # D6 fully approved (M8)
    assert cfg["gates"]["S4_strict_interval"] == "two_sided_95_upper"
    assert fails == []                                         # M9: secondary applied per origin (delegated)
    g = cfg["gates"]
    assert g["S4"] == "ADOPTED" and g["S4_strict"] == "ADOPTED" and g["primary_fuel_metric"] == "unadjusted"
    assert g["S4_strict_bootstrap_seed"] == 42


def test_real_config_arm_c_method_resolved_by_delegation():
    cfg = sf.load_real_cfg()
    assert pf.check_arm_c_method(cfg) == []                    # M9 (was RECOMMENDED / PROPOSED through M8)
    for k, v in cfg["arm_c_method"].items():
        if not k.startswith("_"):
            assert v["status"] == "RESOLVED BY DELEGATED TECHNICAL AUTHORITY" and v["basis"], k


def test_real_authorization_record_grants_no_execution():
    """Live record (schema v2, D9 boundary): tests the actual invariant -- check_authorization('execution', ...)
    refuses the live record -- via the real check the code runs, not by requiring the section to be unsigned.
    The section IS signed, following the project lead's explicit 2026-10-11T07:52:41Z authorization; it is
    refused because that authorization's execute_instruction_ref is already consumed by
    results/run_20261011T075716Z (the incident run), per the single-use guard (_execution_history /
    _consumed_execute_refs). Asserting the specific 'already been consumed by run_20261011T075716Z' message
    (rather than just a non-empty failure list) confirms the refusal comes from that real check, not a
    mocked result or an unrelated failure such as a stale hash. Calibration state and the preserved history
    are checked in test_decision_resolution_m9.py::test_live_authorization_record_state."""
    repo = sf.PKG.parents[1]
    cfg = sf.load_real_cfg()
    rec = json.loads((sf.PKG / "AUTHORIZATION_RECORD.json").read_text())
    assert rec["schema_version"] == pf.RECORD_SCHEMA_VERSION
    assert rec["execution"]["scope"] == pf.SCOPE_EXECUTE
    assert rec["execution_preflight"]["scope"] == pf.SCOPE_PREFLIGHT
    calibration_sha = pf.sha256_file(sf.PKG / "calibration" / "ARM_C_CALIBRATION.json")
    fails = pf.check_authorization(repo, cfg, "execution", calibration_sha)
    assert fails != []
    assert any("already been consumed by run_20261011T075716Z" in f for f in fails)


# ---------------------------------------------------------------- positive control
def test_positive_control_governance_checks_pass(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "calibration")
    assert pf.check_decisions(cfg, pf.EXECUTION_DECISIONS) == []
    assert pf.check_gates(cfg) == []
    assert pf.check_arm_c_method(cfg) == []
    assert pf.check_arms(cfg, r.ARM_CONFIGS) == []
    assert pf.check_hashes(repo, cfg) == []
    assert pf.check_package_manifest(repo) == []
    assert pf.check_preregistration_frozen(repo) == []
    assert pf.check_authorization(repo, cfg, "calibration") == []
    assert pf.check_output_root(repo, cfg) == []


# ---------------------------------------------------------------- authorization
def test_missing_authorization_record(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    (repo / sf.PKG_REL / "AUTHORIZATION_RECORD.json").unlink()
    assert pf.check_authorization(repo, cfg, "execution", "0" * 64) == ["authorization record missing"]


def test_unsigned_template_refused(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    fails = pf.check_authorization(repo, cfg, "execution", "0" * 64)
    assert any("not 'APPROVE'" in f for f in fails)
    assert any("unsigned" in f for f in fails)
    assert any("signer_role" in f for f in fails)


@pytest.mark.parametrize("field,value,msg", [
    ("decision", "PROPOSED", "not 'APPROVE'"),
    ("signer_name", "  ", "unsigned"),
    ("signer_role", "assistant", "signer_role"),
    ("signer_role", "Proposed for project-lead approval", "signer_role"),
    ("signed_at_utc", "yesterday", "signed_at_utc"),
    ("package_manifest_sha256", "f" * 64, "package_manifest_sha256"),
    ("experiment_config_sha256", "f" * 64, "experiment_config_sha256"),
])
def test_each_authorization_field_is_required(tmp_path, field, value, msg):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "calibration", **{field: value})
    fails = pf.check_authorization(repo, cfg, "calibration")
    assert len(fails) == 1 and msg in fails[0], fails


def test_calibration_signature_does_not_authorize_execution(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "calibration")
    fails = pf.check_authorization(repo, cfg, "execution", "a" * 64)
    assert any("execution decision" in f for f in fails)


def test_execution_binds_artifact_hash_and_ceiling(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760)
    assert pf.check_authorization(repo, cfg, "execution", "a" * 64) == []
    assert any("calibration_artifact_sha256" in f for f in pf.check_authorization(repo, cfg, "execution", "b" * 64))
    assert any("calibration_artifact_sha256" in f for f in pf.check_authorization(repo, cfg, "execution", None))
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=99999)
    assert any("solve_ceiling" in f for f in pf.check_authorization(repo, cfg, "execution", "a" * 64))


# ---------------------------------------------------------------- single-use execution authorization
def _write_run_status(repo, run_name, ref, status="FAILED"):
    run_dir = repo / sf.PKG_REL / "results" / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "RUN_STATUS.json").write_text(json.dumps({"status": status, "execute_instruction_ref": ref}))
    return run_dir


@pytest.mark.parametrize("consumed_status", ["FAILED", "COMPLETE", "RUNNING"])
def test_consumed_execute_ref_blocks_reauthorization(tmp_path, consumed_status):
    """Regression test for the run_20261011T075716Z incident: an execute_instruction_ref that already
    appears in a results/run_*/RUN_STATUS.json must never pass check_authorization('execution') again,
    whatever that run's outcome was. This holds even if the live AUTHORIZATION_RECORD.json section is
    otherwise perfectly valid (signed, hash-bound, same ref) -- including after a revert of an
    unrelated code change that would otherwise make an old signature re-validate."""
    repo, cfg = _approved_repo(tmp_path)
    ref = "NON_CMSG_REF :: the same instruction used for the earlier, already-attempted run"
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760, execute_instruction_ref=ref)
    assert pf.check_authorization(repo, cfg, "execution", "a" * 64) == []     # sanity: valid before any run
    _write_run_status(repo, "run_20261011T075716Z", ref, status=consumed_status)
    fails = pf.check_authorization(repo, cfg, "execution", "a" * 64)
    assert any("already been consumed by run_20261011T075716Z" in f for f in fails)
    assert any(f"status {consumed_status!r}" in f for f in fails)


def test_unconsumed_execute_ref_is_not_blocked(tmp_path):
    """A results/run_*/RUN_STATUS.json recording a DIFFERENT execute_instruction_ref does not block
    the live, distinct, still-unused authorization."""
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760,
            execute_instruction_ref="a fresh, never-used instruction")
    _write_run_status(repo, "run_20261011T075716Z", "a different, already-used instruction", status="FAILED")
    assert pf.check_authorization(repo, cfg, "execution", "a" * 64) == []


def test_ambiguous_run_history_blocks_fresh_authorization(tmp_path):
    """Replaces test_malformed_run_status_does_not_crash_or_falsely_block (policy reversed, per
    project-lead decision 2026-10-11, following the run_20261011T075716Z incident): a RUN_STATUS.json
    that is not valid JSON must never be silently skipped. Absence of readable evidence is not proof
    that any reference is unused, so it blocks ALL execution authorization -- including a fresh,
    otherwise-valid, never-used reference -- until a human investigates and resolves it."""
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760,
            execute_instruction_ref="a fresh, never-used instruction")
    assert pf.check_authorization(repo, cfg, "execution", "a" * 64) == []   # sanity: valid beforehand
    broken = repo / sf.PKG_REL / "results" / "run_broken"
    broken.mkdir(parents=True, exist_ok=True)
    (broken / "RUN_STATUS.json").write_text("{not valid json")
    fails = pf.check_authorization(repo, cfg, "execution", "a" * 64)
    assert any("ambiguous run history" in f and "run_broken" in f for f in fails)


def test_run_status_without_a_ref_is_ambiguous_not_safe(tmp_path):
    """A readable, valid-JSON RUN_STATUS.json that simply lacks execute_instruction_ref is not proof
    of safety either -- the real runner always writes this field, so its absence is itself a sign of
    corruption or tampering, not a benign unrelated record."""
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760,
            execute_instruction_ref="a fresh, never-used instruction")
    no_ref = repo / sf.PKG_REL / "results" / "run_no_ref"
    no_ref.mkdir(parents=True, exist_ok=True)
    (no_ref / "RUN_STATUS.json").write_text(json.dumps({"status": "FAILED"}))
    fails = pf.check_authorization(repo, cfg, "execution", "a" * 64)
    assert any("ambiguous run history" in f and "run_no_ref" in f for f in fails)


def test_missing_status_file_in_existing_run_dir_is_ambiguous(tmp_path):
    """Crash-window case: execute() creates run_dir via mkdir() before its first _status() write
    (run_three_arm_2024.py's execute(), between the mkdir and the first _status call). A kill in that
    window leaves a run_* directory with no RUN_STATUS.json at all -- this must block, not be
    silently treated as 'no attempt happened'."""
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760,
            execute_instruction_ref="a fresh, never-used instruction")
    empty_run = repo / sf.PKG_REL / "results" / "run_20260101T000000Z"
    empty_run.mkdir(parents=True, exist_ok=True)   # directory only, no RUN_STATUS.json -- the crash window
    fails = pf.check_authorization(repo, cfg, "execution", "a" * 64)
    assert any("ambiguous run history" in f and "run_20260101T000000Z" in f and "missing" in f for f in fails)


def test_unreadable_status_file_is_ambiguous(tmp_path):
    """OS-level read errors (permission denied, not just malformed JSON) must also block, not be
    silently skipped."""
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760,
            execute_instruction_ref="a fresh, never-used instruction")
    unreadable_dir = repo / sf.PKG_REL / "results" / "run_unreadable"
    unreadable_dir.mkdir(parents=True, exist_ok=True)
    status_path = unreadable_dir / "RUN_STATUS.json"
    status_path.write_text(json.dumps({"status": "FAILED", "execute_instruction_ref": "irrelevant"}))
    status_path.chmod(0o000)
    try:
        if os.access(status_path, os.R_OK):
            pytest.skip("running with privileges that bypass file permissions (e.g. root); "
                       "cannot exercise an OS-level read error here")
        fails = pf.check_authorization(repo, cfg, "execution", "a" * 64)
        assert any("ambiguous run history" in f and "run_unreadable" in f for f in fails)
    finally:
        status_path.chmod(0o644)


def test_consumed_ref_and_ambiguous_history_can_both_be_reported(tmp_path):
    """A consumed reference and separately-ambiguous evidence elsewhere are independent failures;
    fixing one does not silently clear the other."""
    repo, cfg = _approved_repo(tmp_path)
    ref = "an instruction already used by one run, while another run's evidence is ambiguous"
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760, execute_instruction_ref=ref)
    _write_run_status(repo, "run_consumed", ref, status="FAILED")
    broken = repo / sf.PKG_REL / "results" / "run_broken"
    broken.mkdir(parents=True, exist_ok=True)
    (broken / "RUN_STATUS.json").write_text("not json at all")
    fails = pf.check_authorization(repo, cfg, "execution", "a" * 64)
    assert any("already been consumed by run_consumed" in f for f in fails)
    assert any("ambiguous run history" in f and "run_broken" in f for f in fails)


def test_config_change_after_signing_invalidates(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "calibration")
    cfg["gates"]["S4"] = "NOT_ADOPTED"
    sf.write_cfg(repo, cfg)
    fails = pf.check_authorization(repo, cfg, "calibration")
    assert any("experiment_config_sha256" in f for f in fails)
    assert any("hash differs from manifest" in f for f in pf.check_package_manifest(repo))


# ---------------------------------------------------------------- decisions and gates
@pytest.mark.parametrize("dec", pf.EXECUTION_DECISIONS)
@pytest.mark.parametrize("status", ["PENDING", "UNRESOLVED", "CONDITIONALLY APPROVED", "Proposed", None])
def test_any_unapproved_decision_refuses(tmp_path, dec, status):
    cfg = sf.approve_everything(sf.load_real_cfg())
    cfg["decisions"][dec]["status"] = status
    assert pf.check_decisions(cfg, pf.EXECUTION_DECISIONS) != []


def test_approval_without_evidence_refused():
    cfg = sf.approve_everything(sf.load_real_cfg())
    cfg["decisions"]["D7a"]["evidence"] = None
    assert pf.check_decisions(cfg, pf.EXECUTION_DECISIONS) == ["decision D7a has no approval evidence"]


def test_unfrozen_config_refused():
    cfg = sf.approve_everything(sf.load_real_cfg())
    cfg["frozen"] = False
    assert pf.check_decisions(cfg, pf.EXECUTION_DECISIONS) == ["configuration is not marked frozen"]


@pytest.mark.parametrize("mut,msg", [
    (lambda g: g.update(E1_holm_family=None), "D10"),
    (lambda g: g.update(E1_holm_family=[]), "non-empty"),
    (lambda g: g.update(E1_holm_family=["A", "B"]), "'B'"),
    (lambda g: g.update(S4=None), "S4 status"),
    (lambda g: g.pop("S4"), "S4 status"),
    (lambda g: g.update(S4_strict="maybe"), "S4_strict status"),
    (lambda g: g.update(S4_strict="ADOPTED", S4="NOT_ADOPTED", S4_strict_bootstrap_seed=1,
                        S4_strict_interval="two_sided_95_upper",
                        S4_strict_mean_block_days={"value": 10, "status": "APPROVED"},
                        S4_strict_resamples={"value": 10000, "status": "APPROVED"}), "without S4"),
    (lambda g: g.update(S4_strict_bootstrap_seed=None), "seed"),
    (lambda g: g.update(S4_strict_bootstrap_seed="42"), "seed"),
    (lambda g: g.update(S4_strict_interval=None), "S4_strict_interval unresolved"),
    (lambda g: g.update(primary_fuel_metric=None), "D4"),
    (lambda g: g.update(primary_fuel_metric="soc_parity_adjusted"), "D4"),
    (lambda g: g["soc_parity_secondary"].update(status="RECOMMENDED"), "soc_parity_secondary"),
    (lambda g: g["soc_parity_secondary"].update(application="aggregate"), "per_origin"),
    (lambda g: g["soc_parity_secondary"].update(f_values_l_per_kwh=[0.5]), "per_origin"),
])
def test_unresolved_gate_settings_refused(mut, msg):
    cfg = sf.approve_everything(sf.load_real_cfg())
    mut(cfg["gates"])
    fails = pf.check_gates(cfg)
    assert any(msg in f for f in fails), fails


def test_s4_strict_requires_approved_interval_block_and_resamples():
    cfg = sf.approve_everything(sf.load_real_cfg())
    cfg["gates"].update(S4_strict_interval=None)
    fails = pf.check_gates(cfg)
    assert any("S4_strict_interval unresolved" in f for f in fails)
    cfg["gates"]["S4_strict_mean_block_days"]["status"] = "PROPOSED"
    assert any("S4_strict_mean_block_days not APPROVED" in f for f in pf.check_gates(cfg))


# ---------------------------------------------------------------- hashes and manifest
def test_hash_mismatch_refused(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    rel = "system/forecasting/implementations/causal_nwp_physics.py"
    (repo / rel).write_text("tampered\n")
    fails = pf.check_hashes(repo, cfg)
    assert len(fails) == 1 and rel in fails[0]


def test_missing_frozen_file_refused(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    rel = "data/POLARIS_v0_1_future_weather_forecasts_2024.csv"
    (repo / rel).unlink()
    assert pf.check_hashes(repo, cfg) == [f"{rel}: file missing"]


def test_malformed_expected_hash_refused(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    cfg["expected_sha256"]["inputs"]["data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"] = "TBD"
    assert any("missing or malformed" in f for f in pf.check_hashes(repo, cfg))


def test_package_file_added_after_manifest_refused(tmp_path):
    repo, _ = _approved_repo(tmp_path)
    (repo / sf.PKG_REL / "scripts" / "extra.py").write_text("x = 1\n")
    assert any("extra.py: present in package but not in manifest" in f for f in pf.check_package_manifest(repo))


def test_preregistration_without_freeze_hash_refused(tmp_path):
    repo, _ = _approved_repo(tmp_path)
    (repo / sf.PKG_REL / "PREREGISTRATION.md").write_text("# draft, not frozen\n")
    assert pf.check_preregistration_frozen(repo) != []


def test_real_preregistration_freeze_line_is_blank_or_matches_the_manifest():
    # The §9 hash can only be written after the manifest (which contains this test) is generated, so the suite
    # runs once before it is written. Either way a written hash must equal the current manifest's hash.
    text = (sf.PKG / "PREREGISTRATION.md").read_text()
    import re
    m = re.search(r"^PACKAGE_MANIFEST\.sha256 SHA-256:\s*(\S+)", text, re.M)   # the §9 line itself
    assert m is not None
    if m.group(1) != "______":
        assert m.group(1) == pf.sha256_file(sf.PKG / "PACKAGE_MANIFEST.sha256")
        assert pf.check_preregistration_frozen(sf.PKG.parents[1]) == []
