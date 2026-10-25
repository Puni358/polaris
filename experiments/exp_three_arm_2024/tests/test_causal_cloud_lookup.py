"""Isolated synthetic tests (no repository data read). Run only after authorization."""
import pandas as pd
import pytest

from causal_cloud_lookup import OriginCloudPackage, assert_no_protected_dates

SENTINEL = 77.7  # value placed ONLY in the next origin's package


def _two_origin_df():
    rows = []
    for d, val in (("2024-06-01", 10.0), ("2024-06-02", SENTINEL)):
        fs = pd.Timestamp(d)
        for h in range(1, 25):
            rows.append({"forecast_start": fs.strftime("%Y-%m-%d %H:%M:%S"), "horizon_hour": h,
                         "timestamp": (fs + pd.Timedelta(hours=h - 1)).strftime("%Y-%m-%d %H:%M:%S"),
                         "fc_cloud_cover": val + h / 100.0})
    return pd.DataFrame(rows)


@pytest.mark.parametrize("k", range(24))
def test_never_reads_next_origin(k):
    df = _two_origin_df()
    pkg = OriginCloudPackage(df, "2024-06-01 00:00:00")
    t0 = pd.Timestamp("2024-06-01 00:00:00", tz="UTC") - pd.Timedelta(hours=1)
    traj, held = pkg.trajectory(t0 + pd.Timedelta(hours=k))
    assert len(traj) == 24
    assert all(v < SENTINEL for v in traj)
    assert held == k  # step k needs exactly k hours beyond the package


def test_step0_equals_package():
    df = _two_origin_df()
    pkg = OriginCloudPackage(df, "2024-06-01 00:00:00")
    t0 = pd.Timestamp("2024-05-31 23:00:00", tz="UTC")
    traj, held = pkg.trajectory(t0)
    expected = df[df.forecast_start == "2024-06-01 00:00:00"].sort_values("horizon_hour").fc_cloud_cover.tolist()
    assert traj == expected and held == 0


def test_rejects_2025_rows():
    df = _two_origin_df()
    df.loc[0, "timestamp"] = "2025-06-01 00:00:00"
    with pytest.raises(PermissionError):
        assert_no_protected_dates(df)


def test_static_guard_runner_has_no_2025_paths():
    """Static check: the experiment runner must not reference any 2025 data path or the
    2025 campaign modules that load them (planner_cf_campaign_runner, planner_cf_hash_guards)."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / "scripts" / "run_three_arm_2024.py").read_text()
    for banned in ("2025.csv", "DECOMPOSITION_2025", "WEATHER_2025", "planner_cf_campaign_runner",
                   "planner_cf_hash_guards", "stage4_planner_cf_consistency_2025/CAMPAIGN"):
        assert banned not in src, banned
