"""Tests for the M9 decision pass (2026-10-11): delegated statuses in preflight, preserved project-lead
approvals, D10a amendment (C research-only, nothing promotion-eligible), D8 still blocking, per-bin Arm C
coverage diagnostics (PROTOCOL §4) and the D7a §6 reporting items. Synthetic data only; no repository data
file is read; every solver interface is mocked to fail (conftest.no_solver)."""
import json

import numpy as np
import pandas as pd
import pytest

import calibrate_arm_c as cal
import gates_three_arm as gates
import preflight as pf
import run_three_arm_2024 as r
import synthetic_fixtures as sf
from test_decision_resolution import ARMS, telemetry

DEL = "RESOLVED BY DELEGATED TECHNICAL AUTHORITY"
EXIST = "APPROVED BY EXISTING AUTHORITY"


@pytest.fixture(scope="module")
def stat():
    return r.load_frozen().stat


# ---------------------------------------------------------------- status vocabulary
def test_passing_statuses_are_the_same_in_preflight_and_gates():
    assert pf.PASSING_STATUSES == gates.PASSING_STATUSES == ("APPROVED", EXIST, DEL)


@pytest.mark.parametrize("status", [DEL, EXIST])
def test_non_explicit_status_without_authority_fails(status):
    cfg = sf.approve_everything(sf.load_real_cfg())
    cfg["decisions"]["D1"] = {"status": status, "evidence": "x"}
    assert any("decision D1" in f and "names no authority" in f for f in pf.check_decisions(cfg, ["D1"]))
    cfg["decisions"]["D1"]["authority"] = "   "
    assert any("names no authority" in f for f in pf.check_decisions(cfg, ["D1"]))
    cfg["decisions"]["D1"]["authority"] = "M9 delegation"
    assert not any("decision D1" in f for f in pf.check_decisions(cfg, ["D1"]))


def test_arm_c_and_secondary_need_authority_too():
    cfg = sf.approve_everything(sf.load_real_cfg())
    cfg["arm_c_method"]["alpha"] = {"value": 0.1, "status": DEL}
    assert any("arm_c_method.alpha" in f and "names no authority" in f for f in pf.check_arm_c_method(cfg))
    cfg["gates"]["soc_parity_secondary"].update(status=DEL)
    cfg["gates"]["soc_parity_secondary"].pop("authority", None)
    assert any("soc_parity_secondary" in f for f in pf.check_gates(cfg))


@pytest.mark.parametrize("status", ["CONDITIONALLY APPROVED", "RECOMMENDED — AWAITING PROJECT-LEAD APPROVAL",
                                    "BLOCKED — EVIDENCE REQUIRED", "REQUIRES PROJECT-LEAD AUTHORIZATION",
                                    "resolved by delegated technical authority"])
def test_other_statuses_never_pass(status):
    cfg = sf.approve_everything(sf.load_real_cfg())
    cfg["decisions"]["D8"] = {"status": status, "evidence": "x", "authority": "M9"}
    assert any("decision D8" in f for f in pf.check_decisions(cfg, ["D8"]))


# ---------------------------------------------------------------- existing approvals preserved
def test_project_lead_approvals_are_unchanged():
    cfg = sf.load_real_cfg()
    for d in ("D2", "D4", "D6", "D10"):
        assert cfg["decisions"][d]["status"] == "APPROVED", d
        assert "authority" not in cfg["decisions"][d], d          # not relabelled as delegated
    g = cfg["gates"]
    assert g["E1_holm_family"] == ["A", "C"] and g["primary_fuel_metric"] == "unadjusted"
    assert g["S4_strict_bootstrap_seed"] == 42 and g["S4_strict_interval"] == "two_sided_95_upper"
    assert g["S4_strict_mean_block_days"]["value"] == 10 and g["S4_strict_resamples"]["value"] == 10000
    assert gates.STRICT_INTERVALS["two_sided_95_upper"] == 97.5
    assert g["S4_strict_interval_record"]["percentile"] == 97.5


def test_secondary_stays_secondary_with_both_f_values():
    sec = sf.load_real_cfg()["gates"]["soc_parity_secondary"]
    assert sec["application"] == "per_origin" and sec["f_values_l_per_kwh"] == [0.3, 0.75]
    assert sec["role"] == "secondary, reported only, never decision-bearing"
    assert sec["protocol_aggregation_semantics"].startswith("NOT STATED")   # history kept, not rewritten


# ---------------------------------------------------------------- D8 / freeze / authorizations still block
def test_d8_resolved_only_on_the_recorded_device_venv_pass():
    # M9: CONDITIONALLY APPROVED until the device-venv run; resolved after it, with the output hash recorded.
    cfg = sf.load_real_cfg()
    d8 = cfg["decisions"]["D8"]
    assert d8["status"] == DEL and "device venv" in d8["condition"]
    report = sf.PKG / "reports/DEVICE_VENV_TESTS.txt"
    digest = pf.sha256_file(report)
    assert digest in d8["condition_met"]
    text = report.read_text()
    assert "/.venv/bin/python" in text.splitlines()[1]
    last = [l for l in text.splitlines() if l.startswith("=") and " passed" in l][-1]
    assert " failed" not in last and " error" not in last
    n = int(last.split()[1])
    assert text.count("\nPASSED ") == n and "\nFAILED " not in text and "\nERROR " not in text
    assert cfg["frozen"] is True


ORIGINAL_V1_RECORD_SHA256 = "5dd3c007f0b3d548bcab71339e78daa694c0c5f7d766b40e80cb6b5d932d711e"


def test_live_authorization_record_state():
    """Replaces test_authorizations_remain_unsigned (which asserted the pre-signature state). Live record after the
    D9 boundary change: calibration exactly as signed at 05:30:04Z; the 05:49:08Z preflight-only execution block
    preserved byte-for-byte in history. Project-lead decision (2026-10-11): the former final assertion here --
    that every field of the live `execution` section except `scope` is null -- described the state immediately
    after the v1->v2 migration, before any execute authorization had been signed. It was never a permanent
    invariant; it stopped describing reality once the project lead's explicit 2026-10-11T07:52:41Z authorization
    legitimately signed `execution`. Removed per approval; every other assertion below (schema version,
    history-text integrity, calibration preservation, migration metadata, scope) is unchanged and still holds."""
    import hashlib
    rec = json.loads((sf.PKG / "AUTHORIZATION_RECORD.json").read_text())
    assert rec["schema_version"] == 2
    h = rec["history"][0]
    assert hashlib.sha256(h["original_record_text"].encode()).hexdigest() == ORIGINAL_V1_RECORD_SHA256
    v1 = json.loads(h["original_record_text"])
    assert rec["calibration"] == v1["calibration"] and list(rec["calibration"]) == list(v1["calibration"])
    assert rec["calibration"]["signed_at_utc"] == "2026-10-11T05:30:04Z" and rec["calibration"]["decision"] == "APPROVE"
    assert h["section"] == v1["execution"] and h["section"]["signed_at_utc"] == "2026-10-11T05:49:08Z"
    assert h["original_key"] == "execution" and h["grants_authorization"] is False
    assert "preflight stage only" in h["intent_recorded_by_project_lead"]
    assert pf._is_iso_utc(h["superseded_at_utc"]) and h["superseded_at_utc"] > h["section"]["signed_at_utc"]
    assert rec["execution"]["scope"] == "EXECUTE_EXPERIMENT"


# ---------------------------------------------------------------- D10a amendment
def test_c_is_research_only_and_nothing_is_promotion_eligible():
    assert r.ARM_CONFIGS["C"]["result_label"] == r.LABEL_C
    assert r.LABEL_C.startswith("RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE")
    assert r.LABEL_A_FIX == "DIAGNOSTIC — NOT PROMOTION-ELIGIBLE"
    assert "NONCAUSAL" in r.LABEL_B and "DIAGNOSTIC" in r.LABEL_B
    assert all(spec["promotion_eligible"] is False for spec in r.ARM_CONFIGS.values())


def test_amendment_is_a_new_file_and_history_is_unchanged():
    add = (sf.PKG / "PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md").read_text()
    assert "`RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE`" in add and "D10a" in add
    hist = (sf.PKG / "reports/source_prep/PROTOCOL_ADDENDUM_D7a.md").read_text()
    assert "| C | corrected (see §4) | DIAGNOSTIC |" in hist                 # historical text untouched


# ---------------------------------------------------------------- in-sample coverage (calibration artifact)
def _sparse_top_rows():
    rows = []
    for o in range(40):
        fs = (pd.Timestamp("2024-01-01") + pd.Timedelta(days=o)).strftime("%Y-%m-%d %H:%M:%S")
        rows.append({"forecast_start": fs, "daylight": True, "elevation_deg": 20.0, "cloud_frac": 0.5,
                     "clear_sky_ghi": 400.0, "actual_SW_IN": 300.0 - o})
        if o < 19:
            rows.append({"forecast_start": fs, "daylight": True, "elevation_deg": 35.0, "cloud_frac": 0.5,
                         "clear_sky_ghi": 600.0, "actual_SW_IN": 200.0 - 5 * o})
    return pd.DataFrame(rows)


def _flat_method(**over):
    m = {k: (v["value"] if isinstance(v, dict) and "value" in v else v)
         for k, v in sf.load_real_cfg()["arm_c_method"].items() if not k.startswith("_")}
    m.update(elevation_bin_edges_deg=[15.0, 30.0, 90.0], cloud_bin_edges_fraction=[0.0, 1.0],
             bin_boundary_rule={"elevation": "right_closed", "cloud": "right_closed"}, **over)
    return m


def test_in_sample_coverage_is_recorded_per_cell_and_pooled():
    rows = _sparse_top_rows()
    qt = cal.quantile_table(rows, 1.0, _flat_method(), lambda x: x)
    top = [t for t in qt["table"] if (t["elevation_bin"], t["cloud_bin"]) == (1, 0)][0]
    mid = [t for t in qt["table"] if (t["elevation_bin"], t["cloud_bin"]) == (0, 0)][0]
    assert top["own_origin_days"] == 19 and top["own_n_hours"] == 19 and mid["own_n_hours"] == 40
    r_all = (rows.actual_SW_IN - 0.5 * rows.clear_sky_ghi).to_numpy()
    r_top = r_all[rows.elevation_deg.to_numpy() > 30]
    q = top["q_alpha"]
    assert top["in_sample_coverage_pooled"] == pytest.approx(np.mean(r_all >= q)) == mid["in_sample_coverage_pooled"]
    assert top["in_sample_coverage_own"] == pytest.approx(np.mean(r_top >= q))
    assert top["in_sample_coverage_pooled"] >= 0.9       # split-conformal lower bound at alpha 0.10


def test_in_sample_coverage_does_not_change_the_quantiles():
    rows = _sparse_top_rows()
    qt = cal.quantile_table(rows, 1.0, _flat_method(), lambda x: x)
    pooled = (rows.actual_SW_IN - 0.5 * rows.clear_sky_ghi).to_numpy()
    assert {t["q_alpha"] for t in qt["table"]} == {cal.alpha_quantile(pooled, 0.10, "split_conformal_lower")}


# ---------------------------------------------------------------- evaluation-window coverage (after the run)
def _c_rows():
    rows = []
    for o in (1, 2):
        for h, (day, e, c, lb, act) in enumerate([(False, None, None, 0.0, 0.0), (True, 3, 1, 100.0, 150.0),
                                                   (True, 3, 1, 100.0, 90.0), (True, 2, 0, 50.0, 50.0)]):
            rows.append({"arm": "C", "origin_id": o, "hour": h, "c_daylight_h0": day, "c_elevation_bin_h0": e,
                         "c_cloud_bin_h0": c, "c_lower_bound_h0": lb, "c_actual_h0": act})
    rows.append({"arm": "A", "origin_id": 1, "hour": 0})
    return pd.DataFrame(rows)


def test_evaluation_coverage_per_bin_daylight_only():
    res = gates.arm_c_evaluation_coverage(_c_rows())
    assert res["status"].startswith("REPORTED (diagnostic")
    assert res["n_daylight_hours"] == 6 and res["overall_coverage"] == pytest.approx(4 / 6)
    by = {(b["elevation_bin"], b["cloud_bin"]): b for b in res["by_bin"]}
    assert by[(3, 1)] == {"elevation_bin": 3, "cloud_bin": 1, "n_hours": 4, "origin_days": 2, "coverage": 0.5}
    assert by[(2, 0)]["coverage"] == 1.0                  # equality counts as covered


def test_evaluation_coverage_absent_fields_are_reported_not_invented():
    df = telemetry(fuel={a: 1.0 for a in ARMS})
    assert gates.arm_c_evaluation_coverage(df)["status"].startswith("NOT AVAILABLE")


def test_arm_c_loop_records_bound_and_realized_value_for_the_executed_hour():
    from test_runner_three_arm import _run, _synthetic_calibration
    hc, _, _, _, w = _run("C", calibration=_synthetic_calibration())
    sw = w[w.forecast_start == "2024-06-10 00:00:00"].sort_values("horizon_hour").actual_SW_IN.tolist()
    assert [h["c_target_timestamp_h0"] for h in hc] == [h["timestamp"] for h in hc]
    assert [h["c_actual_h0"] for h in hc] == pytest.approx(sw)
    for h in hc:
        assert h["c_residual_space"] == "ghi_w_m2"
        assert 0.0 <= h["c_lower_bound_h0"] <= h["c_point_h0"] + 1e-9
        assert (h["c_elevation_bin_h0"] is not None) == h["c_daylight_h0"]
    assert any(h["c_daylight_h0"] for h in hc)
    res = gates.arm_c_evaluation_coverage(pd.DataFrame(hc))
    assert res["n_daylight_hours"] == sum(h["c_daylight_h0"] for h in hc)
    ha, _, _, _, _ = _run("A")
    assert not any(k.startswith("c_") for k in ha[0])     # other arms carry no Arm C fields


# ---------------------------------------------------------------- D7a §6 reporting items
def test_d7a_reporting_items_present(stat):
    df = telemetry(fuel={a: 1.0 for a in ARMS})
    df["j2_shortfall_wh"] = 2.0
    df["diesel_fuel_remaining_l"] = 50.0
    df.loc[(df.arm == "C") & (df.hour == 5), "diesel_fuel_remaining_l"] = 0.0
    m = gates.arm_metrics(df, "C", stat)
    n_c = int((df.arm == "C").sum())
    assert m["j2_reserve_shortfall_Wh"] == pytest.approx(2.0 * n_c)
    assert m["fuel_exhausted_hours"] == int(((df.arm == "C") & (df.hour == 5)).sum())
    last = df[df.arm == "C"].sort_values(["origin_id", "hour"]).groupby("origin_id")["soc_after"].last().mean()
    assert m["final_soc_pct_mean"] == pytest.approx(last)


def test_handover_is_outside_the_manifest_because_it_records_the_manifest_hash():
    assert "HANDOVER.md" in pf.MANIFEST_EXCLUDED
    assert "HANDOVER.md" not in pf.manifest_files(sf.PKG)
