"""D9 authorization boundary (schema v2, 2026-10-11): preflight authorization never grants execution.

Synthetic repo under tmp_path; no data file is read; every solver entry point stays mocked (conftest). A TEST-ONLY
approved config and TEST-ONLY signatures are used as positive controls so each negative test isolates one rule."""
import json

import pytest

import preflight as pf
import run_three_arm_2024 as r
import synthetic_fixtures as sf

ART = "a" * 64
CEIL = 14760


def _approved_repo(tmp_path):
    repo = sf.build_fake_repo(tmp_path)
    cfg = sf.approve_everything(pf.load_config(repo))
    sf.write_cfg(repo, cfg)
    sf.write_manifest(repo)
    sf.freeze_prereg(repo)
    return repo, cfg


def _record(repo):
    return json.loads((repo / sf.PKG_REL / "AUTHORIZATION_RECORD.json").read_text())


def _write_record(repo, rec):
    (repo / sf.PKG_REL / "AUTHORIZATION_RECORD.json").write_text(json.dumps(rec, indent=2))


def _auth(repo, cfg, mode, art=ART):
    return pf.check_execution_authorization(repo, cfg, mode, art)


# ---------------------------------------------------------------- scope
def test_preflight_only_signature_passes_preflight_but_not_execute(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution_preflight", calibration_sha=ART, solve_ceiling=CEIL)
    assert _auth(repo, cfg, "preflight") == []
    fails = _auth(repo, cfg, "execute")
    assert any("execution is unsigned" in f for f in fails)
    assert any("execute_instruction_ref" in f for f in fails)


def test_execute_scoped_signature_passes_both_modes(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL)
    assert _auth(repo, cfg, "preflight") == []
    assert _auth(repo, cfg, "execute") == []


@pytest.mark.parametrize("scope", ["PREFLIGHT_ONLY", None, "", "execute_experiment", "EXECUTE"])
def test_execution_section_with_wrong_or_missing_scope_fails_both_modes(tmp_path, scope):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL, scope=scope)
    for mode in ("preflight", "execute"):
        assert any("execution scope" in f for f in _auth(repo, cfg, mode)), mode


def test_preflight_section_with_execute_scope_is_invalid(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution_preflight", calibration_sha=ART, solve_ceiling=CEIL, scope=pf.SCOPE_EXECUTE)
    assert any("execution_preflight scope" in f for f in _auth(repo, cfg, "preflight"))
    assert _auth(repo, cfg, "execute") != []


@pytest.mark.parametrize("ref", [None, "", "   "])
def test_execute_requires_instruction_reference(tmp_path, ref):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL, execute_instruction_ref=ref)
    fails = _auth(repo, cfg, "execute")
    assert len(fails) == 1 and "execute_instruction_ref" in fails[0], fails


@pytest.mark.parametrize("version", [None, 1, "2", 3])
def test_other_schema_versions_fail_both_modes(tmp_path, version):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL)
    rec = _record(repo)
    if version is None:
        rec.pop("schema_version")
    else:
        rec["schema_version"] = version
    _write_record(repo, rec)
    for mode in ("preflight", "execute"):
        assert any("schema_version" in f for f in _auth(repo, cfg, mode)), mode


def test_v1_shaped_record_signed_like_the_0549_block_cannot_execute(tmp_path):
    """A v1-style execution section (no scope, no instruction reference), exactly how the preflight-only
    signature of 2026-10-11T05:49:08Z was written, does not authorize --execute (nor --preflight) under v2."""
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL)
    rec = _record(repo)
    rec["execution"].pop("scope")
    rec["execution"].pop("execute_instruction_ref")
    _write_record(repo, rec)
    assert _auth(repo, cfg, "execute") != []
    assert _auth(repo, cfg, "preflight") != []


def test_unknown_mode_or_stage_raises(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    for bad in ("", "EXECUTE", "dry-run", None):
        with pytest.raises(ValueError):
            pf.check_execution_authorization(repo, cfg, bad, ART)
        with pytest.raises(ValueError):
            r.full_preflight(repo, cfg, bad)
    with pytest.raises(ValueError):
        pf.check_authorization(repo, cfg, "history", ART)
    with pytest.raises(TypeError):
        r.full_preflight(repo, cfg)  # no default mode


def test_execute_signed_before_preflight_signature_is_refused(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution_preflight", calibration_sha=ART, solve_ceiling=CEIL, signed_at_utc="2026-10-11T06:00:00Z")
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL, signed_at_utc="2026-10-11T05:59:59Z")
    assert any("precedes execution_preflight" in f for f in _auth(repo, cfg, "execute"))


# ---------------------------------------------------------------- history never authorizes
def test_history_never_grants_authorization(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL)
    valid = _record(repo)["execution"]
    rec = sf.null_record(cfg)
    rec["history"] = [{"original_key": "execution", "section": valid, "grants_authorization": True},
                      {"execution": valid, "execution_preflight": valid}]
    _write_record(repo, rec)
    for mode in ("preflight", "execute"):
        assert any("unsigned" in f for f in _auth(repo, cfg, mode)), mode


# ---------------------------------------------------------------- hash and value mismatches
@pytest.mark.parametrize("stage", ["execution_preflight", "execution"])
@pytest.mark.parametrize("field,value,msg", [
    ("package_manifest_sha256", "f" * 64, "package_manifest_sha256"),
    ("experiment_config_sha256", "f" * 64, "experiment_config_sha256"),
    ("calibration_artifact_sha256", "b" * 64, "calibration_artifact_sha256"),
    ("solve_ceiling", "14760", "solve_ceiling"),
    ("solve_ceiling", 14760.0, "solve_ceiling"),
    ("solve_ceiling", 99999, "solve_ceiling"),
    ("decision", "APPROVE_PREFLIGHT", "not 'APPROVE'"),
    ("signer_role", "assistant", "signer_role"),
    ("signed_at_utc", "2026-10-11 06:00:00", "signed_at_utc"),
])
def test_each_execution_field_is_bound(tmp_path, stage, field, value, msg):
    repo, cfg = _approved_repo(tmp_path)
    kw = {"calibration_sha": ART, "solve_ceiling": CEIL}
    if field == "solve_ceiling":
        kw["solve_ceiling"] = value
    else:
        kw[field] = value
    sf.sign(repo, stage, **kw)
    fails = pf.check_authorization(repo, cfg, stage, ART)
    assert len(fails) == 1 and msg in fails[0], fails


def test_package_edit_after_signing_invalidates_both_scopes(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution_preflight", calibration_sha=ART, solve_ceiling=CEIL)
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL)
    (repo / sf.PKG_REL / "scripts" / "placeholder.py").write_text("# edited after signing\n")
    sf.write_manifest(repo)
    for mode in ("preflight", "execute"):
        assert any("package_manifest_sha256" in f for f in _auth(repo, cfg, mode)), mode


# ---------------------------------------------------------------- calibration authorization preservation
def _art(created="2026-10-11T05:30:32Z"):
    return {"created_at_utc": created}


def test_calibration_authorization_binds_the_artifact(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "calibration", signed_at_utc="2026-10-11T05:30:04Z")
    assert pf.check_calibration_authorization(repo, cfg, _art()) == []
    assert any("signed after" in f for f in pf.check_calibration_authorization(repo, cfg, _art("2026-10-11T05:30:03Z")))
    assert any("created_at_utc" in f for f in pf.check_calibration_authorization(repo, cfg, None))


def test_unsigned_calibration_blocks_both_modes(tmp_path, monkeypatch):
    import calibrate_arm_c as cal
    repo, cfg = _approved_repo(tmp_path)
    monkeypatch.setattr(cal, "load_artifact", lambda p, c: (_art(), ART))
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL)
    for mode in ("preflight", "execute"):
        rep, _, _ = r.full_preflight(repo, cfg, mode)
        assert any(f.startswith("[calibration_authorization] calibration is unsigned") for f in rep.failures), mode


def test_calibration_config_hash_must_be_current(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "calibration", signed_at_utc="2026-10-11T05:30:04Z", experiment_config_sha256="f" * 64)
    assert any("experiment_config_sha256" in f for f in pf.check_calibration_authorization(repo, cfg, _art()))


def test_calibration_under_a_recorded_prior_freeze_stays_valid_after_refreeze(tmp_path):
    """Re-freezing changes the manifest. A calibration signed against the previous manifest stays valid only if
    that manifest is recorded in PREREGISTRATION.md as a prior freeze."""
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "calibration", signed_at_utc="2026-10-11T05:30:04Z")
    old = pf.sha256_file(repo / sf.PKG_REL / "PACKAGE_MANIFEST.sha256")
    (repo / sf.PKG_REL / "scripts" / "placeholder.py").write_text("# boundary fix\n")
    sf.write_manifest(repo)
    sf.freeze_prereg(repo)
    assert any("prior freeze" in f for f in pf.check_calibration_authorization(repo, cfg, _art()))
    prereg = repo / sf.PKG_REL / "PREREGISTRATION.md"
    prereg.write_text(prereg.read_text() + f"\nPrior freeze (superseded): {old} (TEST-ONLY)\n")
    assert pf.prior_freezes(repo) == [old]
    assert pf.check_preregistration_frozen(repo) == []  # the current-freeze line still decides the freeze check
    assert pf.check_calibration_authorization(repo, cfg, _art()) == []


def test_signing_execution_sections_leaves_calibration_unchanged(tmp_path):
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "calibration")
    before = _record(repo)["calibration"]
    sf.sign(repo, "execution_preflight", calibration_sha=ART, solve_ceiling=CEIL)
    sf.sign(repo, "execution", calibration_sha=ART, solve_ceiling=CEIL)
    assert _record(repo)["calibration"] == before


# ---------------------------------------------------------------- --execute refusal, end to end
def _poison(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("execution machinery reached")
    for name in ("load_frozen", "load_planner_class", "ArmForecaster", "run_origin", "evaluation_origins"):
        monkeypatch.setattr(r, name, boom)


def test_execute_refused_with_preflight_only_authorization(tmp_path, monkeypatch, capsys):
    """Everything else valid, the inputs guards stubbed to pass: a preflight-only signature makes --preflight pass
    and --execute exit 2 before any planner, forecaster, optimizer or output directory exists."""
    import calibrate_arm_c as cal
    import timestamp_guards as tg
    repo, cfg = _approved_repo(tmp_path)
    monkeypatch.setattr(cal, "load_artifact", lambda p, c: (_art(), ART))
    monkeypatch.setattr(tg, "run_all_guards", lambda *a, **k: None)
    monkeypatch.setattr(r.pd, "read_csv", lambda *a, **k: None)
    sf.sign(repo, "calibration", signed_at_utc="2026-10-11T05:30:04Z")
    sf.sign(repo, "execution_preflight", calibration_sha=ART, solve_ceiling=CEIL)
    _poison(monkeypatch)
    monkeypatch.setattr(r, "evaluation_origins", lambda w, c: [])  # the [inputs] stage itself is not under test
    results = repo / sf.PKG_REL / "results"
    before = sorted(p.name for p in results.iterdir())
    assert r.main(["--repo", str(repo), "--preflight"]) == 0
    assert r.main(["--repo", str(repo), "--execute"]) == 2
    err = capsys.readouterr().err
    assert "execution refused" in err and "execution is unsigned" in err
    assert sorted(p.name for p in results.iterdir()) == before


def test_execute_refused_on_unsigned_template(tmp_path, monkeypatch, capsys):
    import calibrate_arm_c as cal
    repo, cfg = _approved_repo(tmp_path)
    monkeypatch.setattr(cal, "load_artifact", lambda p, c: (_art(), ART))
    sf.sign(repo, "calibration", signed_at_utc="2026-10-11T05:30:04Z")
    _poison(monkeypatch)
    assert r.main(["--repo", str(repo), "--execute"]) == 2
    assert "execution is unsigned" in capsys.readouterr().err


def test_execute_rechecks_scope_even_if_preflight_is_bypassed(tmp_path, monkeypatch, capsys):
    """Defence in depth inside execute(): with full_preflight forced to report success, a preflight-only
    record still stops execute() before any machinery."""
    repo, cfg = _approved_repo(tmp_path)
    sf.sign(repo, "execution_preflight", calibration_sha=ART, solve_ceiling=CEIL)
    monkeypatch.setattr(r, "full_preflight", lambda repo_, cfg_, mode_: (pf.PreflightReport(mode_), {}, ART))
    _poison(monkeypatch)
    assert r.execute(repo, cfg) == 2
    assert "no valid execute-scoped authorization" in capsys.readouterr().err
