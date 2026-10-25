"""
Synthetic/unit tests for the ORACLE audit driver (EXP-PLANNER-CF-CONSISTENCY-2025, §6, NG7, NG11).

The oracle solver is replaced with a stub. The origin list and SITES key set are fabricated. No real
origin or oracle is run.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXP))

import oracle_runner as oracle  # noqa: E402
import oracle_driver as drv  # noqa: E402
from oracle_runner import OracleOriginResult  # noqa: E402


def _origins():
    return [pd.Timestamp("2025-05-01")] * 123


def _keys():
    base = pd.Timestamp("2025-05-01")
    return [(base + pd.Timedelta(hours=j)).strftime("%Y-%m-%d %H:%M:%S") for j in range(47)]


def _result(variant, origin_index, charge_realized=500.0, charge_planned=500.0, fuel=10.0):
    res = OracleOriginResult(origin="2025-05-01", variant=variant)
    res.hourly = [{"step": h, "charge_w": charge_realized, "fuel_l": fuel / 24.0} for h in range(24)]
    res.executed = [{"origin_id": origin_index, "arm": variant, "step": h, "plan_hour": 0,
                     "planned_charge_w": charge_planned} for h in range(24)]
    return res


def _stub(charge_realized=500.0, charge_planned=500.0, fail_origin=None, fuel=10.0):
    def run(origin, variant, origin_index, lookup=None, configs=None):
        if fail_origin is not None and origin_index == fail_origin and variant == "ORACLE-PHYS":
            raise RuntimeError("synthetic solver failure")
        return _result(variant, origin_index, charge_realized, charge_planned, fuel)
    return run


@pytest.fixture
def patched(monkeypatch):
    def apply(run_fn):
        monkeypatch.setattr(oracle, "run_oracle_origin", run_fn)
    return apply


def _ok_kwargs(tmp_path, **extra):
    kw = dict(authorized=True, out_dir=tmp_path, origins_fn=_origins, lookup_fn=lambda: {k: 1.0 for k in _keys()})
    kw.update(extra)
    return kw


def test_requires_authorization(tmp_path):
    with pytest.raises(PermissionError):
        drv.run_oracle_audit(authorized=False, out_dir=tmp_path)


def test_g12_failure_blocks_before_any_oracle_run(tmp_path, patched):
    def must_not_run(*a, **k):
        raise AssertionError("oracle must not run when G12 fails")
    patched(must_not_run)
    res = drv.run_oracle_audit(**_ok_kwargs(tmp_path, lookup_fn=lambda: {k: 1.0 for k in _keys()[:-1]}))
    assert res["status"] == "BLOCKED" and res["g12"]["PASS"] is False
    assert res["NG7"] == "cannot be established"


def test_complete_path_runs_both_variants_and_passes_G1(tmp_path, patched):
    patched(_stub())
    res = drv.run_oracle_audit(**_ok_kwargs(tmp_path, campaign_pc_control_fuel_L=6000.0))
    assert res["status"] == "COMPLETE"
    assert res["G1_ORACLE_PHYS"]["PASS"] is True
    assert res["g12"]["PASS"] is True
    assert res["origins"] == 123
    assert res["oracle_phys_fuel_L"] == pytest.approx(123 * 10.0)
    assert (tmp_path / "ORACLE_PHYS_HOURLY.csv").exists()
    assert (tmp_path / "ORACLE_CTRL_HOURLY.csv").exists()
    assert (tmp_path / "ORACLE_AUDIT_REPORT.json").exists()


def test_G1_mismatch_is_reported_as_NG1_not_repaired(tmp_path, patched):
    patched(_stub(charge_realized=500.0, charge_planned=520.0))
    res = drv.run_oracle_audit(**_ok_kwargs(tmp_path))
    assert res["status"] == "G1_FAIL_NG1"
    assert res["G1_ORACLE_PHYS"]["PASS"] is False


def test_origin_exception_blocks_and_is_recorded(tmp_path, patched):
    patched(_stub(fail_origin=7))
    res = drv.run_oracle_audit(**_ok_kwargs(tmp_path))
    assert res["status"] == "BLOCKED"
    assert res["errors"] == [{"origin_id": 7, "variant": "ORACLE-PHYS",
                              "error": "RuntimeError: synthetic solver failure"}]


def test_ng7_triggers_below_40_percent_saving():
    r = drv.ng7_decision(oracle_phys_fuel_L=5000.0, pc_control_fuel_L=6000.0)
    assert r["oracle_phys_saving_pct"] == pytest.approx(16.6667, abs=1e-3)
    assert r["NG7_TRIGGERED"] is True


def test_ng7_not_triggered_at_40_percent_saving():
    r = drv.ng7_decision(oracle_phys_fuel_L=3600.0, pc_control_fuel_L=6000.0)
    assert r["NG7_TRIGGERED"] is False


def test_ng7_depends_only_on_oracle_phys(tmp_path, patched):
    patched(_stub(fuel=10.0))
    a = drv.run_oracle_audit(**_ok_kwargs(tmp_path, campaign_pc_control_fuel_L=6000.0))
    b_run = _stub(fuel=10.0)

    def ctrl_different(origin, variant, origin_index, lookup=None, configs=None):
        res = b_run(origin, variant, origin_index, lookup, configs)
        if variant == "ORACLE-CTRL":
            for h in res.hourly:
                h["fuel_l"] = 999.0
        return res
    patched(ctrl_different)
    b = drv.run_oracle_audit(**_ok_kwargs(tmp_path, campaign_pc_control_fuel_L=6000.0))
    assert a["NG7"] == b["NG7"]
    assert a["oracle_ctrl_fuel_L"] != b["oracle_ctrl_fuel_L"]


def test_hash_guard_failure_blocks(tmp_path, patched, monkeypatch):
    patched(_stub())
    monkeypatch.setattr(drv, "verify_protected_hashes", lambda repo: ["hash mismatch: x"])
    res = drv.run_oracle_audit(**_ok_kwargs(tmp_path))
    assert res["status"] == "BLOCKED" and res["reason"] == "hash guards failed"
