"""Arm C calibration: isolation, fail-closed method handling, bins, determinism and the artifact.
All data are synthetic. No repository data file is read, no calibration is run on real data, no solver."""
import copy
import json
import math

import numpy as np
import pandas as pd
import pytest

import calibrate_arm_c as cal
import preflight as pf
import synthetic_fixtures as sf

CFG = sf.load_real_cfg()
EV, WIN = CFG["evaluation"], CFG["calibration_window"]


def resolved_method(**over):
    m = copy.deepcopy(sf.approve_everything(CFG)["arm_c_method"])
    flat = {k: (v["value"] if isinstance(v, dict) and "value" in v else v) for k, v in m.items() if not k.startswith("_")}
    flat.update(over)
    return flat


def fake_geometry(fs):
    """Synthetic geometry: elevation sweeps -10..50 deg over the day; clear sky follows it."""
    el = [50.0 * math.sin(math.pi * (h - 3) / 20.0) if 3 <= h <= 23 else -10.0 for h in range(24)]
    cs = [max(0.0, 900.0 * math.sin(math.radians(e))) if e > 0 else 0.0 for e in el]
    return cs, el


def synthetic_calibration_rows(n_origins=119, gamma=0.4, start="2024-01-01"):
    days = [(pd.Timestamp(start) + pd.Timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n_origins)]
    w = sf.synthetic_weather(days)
    w["fc_cloud_cover"] = [float((i * 7 + h * 13) % 101) for i in range(n_origins) for h in range(24)]
    rows = cal.attach_geometry(cal.select_calibration_rows(w, EV, WIN), fake_geometry)
    noise = 25.0 * np.sin(np.arange(len(rows)) * 1.7)
    pt = cal.point_ghi(rows["clear_sky_ghi"].to_numpy(), rows["cloud_frac"].to_numpy(), gamma, rows["daylight"].to_numpy())
    rows["actual_SW_IN"] = np.where(rows["daylight"], np.maximum(0.0, pt + noise), 0.0)
    return rows


# ---------------------------------------------------------------- isolation
def test_evaluation_window_and_buffers_are_dropped():
    days = ["2024-04-28", "2024-04-29", "2024-04-30", "2024-05-01", "2024-06-15", "2024-08-31",
            "2024-09-01", "2024-09-02", "2024-09-03"]
    rows = cal.select_calibration_rows(sf.synthetic_weather(days), EV, WIN)
    assert sorted(rows["forecast_start"].unique()) == ["2024-04-28 00:00:00", "2024-04-29 00:00:00",
                                                       "2024-09-02 00:00:00", "2024-09-03 00:00:00"]


def test_isolation_fails_closed_even_if_the_filter_is_wrong(monkeypatch):
    monkeypatch.setattr(cal, "calibration_origin_filter", lambda fs, window: pd.Series(True, index=fs.index))
    with pytest.raises(PermissionError, match="evaluation-window"):
        cal.select_calibration_rows(sf.synthetic_weather(["2024-04-29", "2024-05-01"]), EV, WIN)
    with pytest.raises(PermissionError, match="buffer"):
        cal.select_calibration_rows(sf.synthetic_weather(["2024-04-29", "2024-04-30"]), EV, WIN)


def test_target_hours_inside_evaluation_window_rejected():
    w = sf.synthetic_weather(["2024-04-29"])
    w.loc[w.index[-1], "timestamp"] = "2024-05-01 00:00:00"
    with pytest.raises(PermissionError, match="target hours"):
        cal.assert_calibration_isolation(w, EV, WIN)


@pytest.mark.parametrize("ts", ["2025-01-01 00:00:00", "2025-06-01 12:00:00", "2023-12-31 23:00:00"])
def test_non_2024_rows_abort(ts):
    w = sf.synthetic_weather(["2024-01-10", "2024-01-11"])
    w.loc[5, "timestamp"] = ts
    with pytest.raises(PermissionError):
        cal.select_calibration_rows(w, EV, WIN)


def test_2025_origin_aborts():
    w = sf.synthetic_weather(["2024-01-10"])
    w["forecast_start"] = "2025-01-10 00:00:00"
    with pytest.raises(PermissionError):
        cal.select_calibration_rows(w, EV, WIN)


@pytest.mark.parametrize("mut,msg", [
    (lambda w: w.drop(index=3), "24 rows"),
    (lambda w: pd.concat([w, w.iloc[[0]]]), "duplicate"),
    (lambda w: w.assign(fc_cloud_cover=w["fc_cloud_cover"].where(w.index != 2, np.nan)), "non-finite"),
    (lambda w: w.assign(fc_cloud_cover=w["fc_cloud_cover"].where(w.index != 2, 120.0)), "outside"),
    (lambda w: w.assign(actual_SW_IN=w["actual_SW_IN"].where(w.index != 2, -5.0)), "negative"),
    (lambda w: w.assign(horizon_hour=w["horizon_hour"].where(w.index != 2, 9)), None),
])
def test_invalid_calibration_rows_rejected(mut, msg):
    w = mut(sf.synthetic_weather(["2024-02-01", "2024-02-02"]))
    with pytest.raises(cal.CalibrationError, match=msg):
        cal.select_calibration_rows(w, EV, WIN)


# ---------------------------------------------------------------- gamma
def test_gamma_recovered_on_synthetic_data():
    rows = synthetic_calibration_rows(gamma=0.4)
    fit = cal.fit_gamma(rows, cal.gamma_grid(CFG["arm_c_method"]["gamma_grid"]), None)
    assert fit["gamma_hat"] == pytest.approx(0.4)
    assert len(fit["mae_by_gamma"]) == 91


def test_gamma_tie_requires_an_approved_rule():
    rows = synthetic_calibration_rows()
    rows["cloud_frac"] = 0.0  # every gamma gives the same point forecast -> exact tie
    grid = cal.gamma_grid(CFG["arm_c_method"]["gamma_grid"])
    with pytest.raises(cal.CalibrationError, match="tie"):
        cal.fit_gamma(rows, grid, None)
    assert cal.fit_gamma(rows, grid, "smallest_gamma")["gamma_hat"] == pytest.approx(0.10)
    assert cal.fit_gamma(rows, grid, "largest_gamma")["gamma_hat"] == pytest.approx(1.00)


def test_point_forecast_zero_at_night():
    out = cal.point_ghi(np.array([0.0, 500.0, 500.0]), np.array([0.5, 0.5, 0.5]), 0.5, np.array([False, False, True]))
    assert out[0] == 0.0 and out[1] == 0.0 and out[2] == pytest.approx(500.0 * 0.5 ** 0.5)


# ---------------------------------------------------------------- bins and quantiles
EL = [0.0, 5.0, 15.0, 30.0, 90.0]
CL = [0.0, 0.2, 0.8, 1.0]


@pytest.mark.parametrize("rule", [None, "", "closest"])
def test_unresolved_boundary_rule_raises(rule):
    with pytest.raises(cal.CalibrationError):
        cal.assign_bin(np.array([3.0]), EL, rule)


def test_boundary_rules_are_explicit():
    v = np.array([0.0, 5.0, 15.0, 30.0, 90.0])
    assert cal.assign_bin(v, EL, "left_closed").tolist() == [0, 1, 2, 3, 3]
    assert cal.assign_bin(v, EL, "right_closed").tolist() == [0, 0, 1, 2, 3]
    c = np.array([0.0, 0.2, 0.8, 1.0])
    assert cal.assign_bin(c, CL, "left_closed").tolist() == [0, 1, 2, 2]
    assert cal.assign_bin(c, CL, "right_closed").tolist() == [0, 0, 1, 2]
    with pytest.raises(cal.CalibrationError):
        cal.assign_bin(np.array([95.0]), EL, "left_closed")


@pytest.mark.parametrize("method", [None, "", "conformal"])
def test_unresolved_quantile_method_raises(method):
    with pytest.raises(cal.CalibrationError):
        cal.alpha_quantile(np.arange(30.0), 0.1, method)


def test_split_conformal_order_statistic():
    r = np.array([5.0, -3.0, 1.0, 9.0, -8.0, 2.0, 0.0, 4.0, -1.0, 7.0, 3.0, 6.0, -2.0, 8.0, -5.0, 10.0, -4.0, 11.0, 12.0])
    assert cal.alpha_quantile(r, 0.1, "split_conformal_lower") == -5.0  # n=19, k=floor(0.1*20)=2
    with pytest.raises(cal.InsufficientBinError):
        cal.alpha_quantile(r[:8], 0.1, "split_conformal_lower")


def test_unresolved_residual_space_raises():
    rows = synthetic_calibration_rows()
    with pytest.raises(cal.CalibrationError):
        cal.residuals(rows[rows["daylight"]], 0.4, None, lambda x: x)


@pytest.mark.parametrize("policy", [None, "fill_global", "nearest"])
def test_insufficient_bin_policy_unresolved_raises(policy):
    rows = synthetic_calibration_rows()
    with pytest.raises(cal.InsufficientBinError):
        cal.quantile_table(rows, 0.4, resolved_method(insufficient_bin_policy=policy, min_origin_days_per_bin=10_000), lambda x: x)


def test_fail_policy_raises_on_sparse_bin():
    rows = synthetic_calibration_rows()
    with pytest.raises(cal.InsufficientBinError, match="policy: fail"):
        cal.quantile_table(rows, 0.4, resolved_method(insufficient_bin_policy="fail", min_origin_days_per_bin=10_000), lambda x: x)


def test_merge_is_recorded_and_never_silent():
    rows = synthetic_calibration_rows()
    rows = rows[~((rows["elevation_deg"] > 30.0) & (rows["cloud_frac"] >= 0.8))]  # make one bin empty
    qt = cal.quantile_table(rows, 0.4, resolved_method(insufficient_bin_policy="merge_lower_elevation"), lambda x: x)
    assert qt["merges"] and qt["merges"][0]["from"] == [3, 2]
    merged = [t for t in qt["table"] if t["elevation_bin"] == 3 and t["cloud_bin"] == 2][0]
    assert merged["pooled_group"] == [2, 2]
    assert len(qt["table"]) == 12
    with pytest.raises(cal.InsufficientBinError, match="no neighbour"):
        cal.quantile_table(rows, 0.4, resolved_method(insufficient_bin_policy="merge_higher_elevation"), lambda x: x)


def test_quantile_table_is_deterministic_and_complete():
    rows = synthetic_calibration_rows()
    m = resolved_method()
    a = cal.quantile_table(rows, 0.4, m, lambda x: x)
    b = cal.quantile_table(rows.sample(frac=1.0, random_state=3), 0.4, m, lambda x: x)
    assert a == b
    assert {(t["elevation_bin"], t["cloud_bin"]) for t in a["table"]} == {(e, c) for e in range(4) for c in range(3)}
    assert all(t["origin_days"] >= 20 for t in a["table"])


def test_lower_bound_never_exceeds_point_and_missing_bin_raises():
    rows = synthetic_calibration_rows()
    qt = cal.quantile_table(rows, 0.4, resolved_method(), lambda x: x)
    el = np.array([-5.0, 3.0, 10.0, 20.0, 40.0])
    cs = np.array([0.0, 100.0, 300.0, 500.0, 800.0])
    cf = np.array([0.5, 0.1, 0.5, 0.9, 0.0])
    pt = cal.point_ghi(cs, cf, 0.4, (el > 0) & (cs > 0))
    lb = np.array(cal.lower_bound(pt, el, cf, cs, qt))
    assert lb[0] == 0.0 and np.all(lb >= 0.0) and np.all(lb <= pt + 1e-12)
    qt2 = copy.deepcopy(qt)
    qt2["table"] = [t for t in qt2["table"] if not (t["elevation_bin"] == 3 and t["cloud_bin"] == 0)]
    with pytest.raises(cal.CalibrationError, match="no calibrated quantile"):
        cal.lower_bound(pt, el, cf, cs, qt2)


# ---------------------------------------------------------------- artifact
def _cfg_resolved():
    c = sf.approve_everything(CFG)
    return c


def _artifact(rows=None):
    c = _cfg_resolved()
    rows = synthetic_calibration_rows() if rows is None else rows
    w = c["paths"]["weather"]
    return cal.build_artifact(rows, c, {w: c["expected_sha256"]["inputs"][w]}, "synthetic", lambda x: x), c


def test_artifact_records_provenance_and_is_deterministic():
    a, c = _artifact()
    b, _ = _artifact()
    a.pop("created_at_utc"), b.pop("created_at_utc")
    assert a == b
    for k in ("n_origins", "first_origin", "last_origin", "origins", "gamma_fit", "quantiles", "source_sha256",
              "software", "method_config", "calibration_window"):
        assert k in a
    assert set(a["software"]) == {"python", "numpy", "pandas", "pvlib"}


def test_artifact_never_overwritten(tmp_path):
    a, c = _artifact()
    p = tmp_path / "calibration" / "ARM_C_CALIBRATION.json"
    h = cal.write_artifact_exclusive(a, p)
    assert h == pf.sha256_file(p)
    with pytest.raises(FileExistsError):
        cal.write_artifact_exclusive(a, p)
    assert pf.sha256_file(p) == h


def test_load_artifact_accepts_valid_and_rejects_tampering(tmp_path):
    a, c = _artifact()
    p = tmp_path / "a.json"
    cal.write_artifact_exclusive(a, p)
    art, digest = cal.load_artifact(p, c)
    assert digest == pf.sha256_file(p)

    def bad(mut, msg):
        b = copy.deepcopy(a)
        mut(b)
        q = tmp_path / f"bad_{abs(hash(msg))}.json"
        q.write_text(json.dumps(b))
        with pytest.raises(cal.CalibrationError, match=msg):
            cal.load_artifact(q, c)

    bad(lambda b: b["origins"].append("2024-06-15 00:00:00"), "outside the approved calibration window")
    bad(lambda b: b["origins"].append("2024-04-30 00:00:00"), "outside the approved calibration window")
    bad(lambda b: b["method_config"].update(alpha={"value": 0.2, "status": "APPROVED"}), "different arm_c_method")
    bad(lambda b: b["quantiles"]["table"].pop(), "incomplete")
    bad(lambda b: b["source_sha256"].update({c["paths"]["weather"]: "0" * 64}), "weather hash")
    bad(lambda b: b["gamma_fit"].update(gamma_hat=1.5), "outside the grid")
    bad(lambda b: b.update(experiment_id="OTHER"), "identity")


def test_missing_artifact_raises(tmp_path):
    with pytest.raises(cal.CalibrationError, match="missing"):
        cal.load_artifact(tmp_path / "nope.json", _cfg_resolved())


# ---------------------------------------------------------------- CLI refuses without authorization
def test_main_refuses_before_reading_data(tmp_path, monkeypatch, capsys):
    repo = sf.build_fake_repo(tmp_path)

    def boom(*a, **k):
        raise AssertionError("calibration touched data or geometry despite failed preflight")
    monkeypatch.setattr(cal.pd, "read_csv", boom)
    monkeypatch.setattr(cal, "corrected_geometry_provider", boom)
    assert cal.main(["--repo", str(repo)]) == 2
    err = capsys.readouterr().err
    assert "CALIBRATION REFUSED" in err and "unsigned" in err   # decisions all pass after the M9 freeze


def test_main_refuses_when_artifact_exists_even_if_signed(tmp_path, monkeypatch, capsys):
    repo = sf.build_fake_repo(tmp_path)
    cfg = sf.approve_everything(pf.load_config(repo))
    sf.write_cfg(repo, cfg)
    sf.write_manifest(repo)
    sf.freeze_prereg(repo)
    sf.sign(repo, "calibration")
    art = repo / cfg["paths"]["calibration_artifact"]
    art.parent.mkdir(parents=True)
    art.write_text("{}")
    monkeypatch.setattr(cal.pd, "read_csv", lambda *a, **k: (_ for _ in ()).throw(AssertionError("read")))
    assert cal.main(["--repo", str(repo)]) == 2
    assert "refusing to overwrite" in capsys.readouterr().err


def test_corrected_geometry_matches_arm_c_runtime_geometry():
    """The calibration geometry must equal what Arm C (and A-Fix) use at run time: forecaster with the
    label correction, cloud 0, sun at label - 1 h. Synthetic state only."""
    import run_three_arm_2024 as r
    geom = cal.corrected_geometry_provider()
    cs, el = geom("2024-03-15 00:00:00")
    fc = r.ArmForecaster("A_FIX")
    st = r.make_initial_state("2024-03-14T23:00:00Z")
    b = fc.engine.predict(st, {"fc_cloud_cover": [0.0] * 24})
    el2 = fc.wrapper.get_solarposition(pd.to_datetime(b.timestamps, utc=True))["elevation"].to_numpy()
    assert np.allclose(cs, b.solar_irradiance.point) and np.allclose(el, el2)
    assert b.timestamps[0].startswith("2024-03-15T00:00")
