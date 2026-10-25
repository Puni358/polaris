"""
PROPOSED — NOT APPLIED, NOT RUN.
Target path if approved: experiments/exp_three_arm_2024/test_d7a_parity.py

Fail-closed tests required by D7a item 5. These use synthetic inputs and the unmodified forecaster and
adapter; they read no 2024 or 2025 observation file. A failing test blocks execution.
"""
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
FROZEN = {
    "system/forecasting/implementations/causal_nwp_physics.py":
        "14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710",
    "experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py":
        "3427da6a7b1d7763f8fa655e541cd2a344aeefdd33379137c6311501799395d0",
    "experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py":
        "a8dd9fc7d84e3d2344ba4f99ba1b1cd0ec2165a83d8f7af438b69f8178815093",
    "system/simulation/research_realization_executor.py":
        "c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b",
    "data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv":
        "f3fe7cf2fff45f21feeceb850e63299a919da658d1474851b1cf611a35e43473",
    "data/POLARIS_v0_1_future_weather_forecasts_2024.csv":
        "8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16",
}


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@pytest.mark.parametrize("rel,exp", FROZEN.items())
def test_source_files_unchanged(rel, exp):
    assert _sha(REPO / rel) == exp, rel


def _engines():
    from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
    from solar_convention import apply_label_correction
    a = CausalNwpPhysicsForecastEngine()
    b = CausalNwpPhysicsForecastEngine()
    w = apply_label_correction(b)
    return a, b, w


def _state(ts="2024-03-15T07:00:00"):
    # Minimal StationState stand-in; the real runner passes the executor's next_state.
    return SimpleNamespace(timestamp=ts, battery_soc_pct=50.0, battery_energy_wh=100000.0,
                           last_observed_demand_w=15000.0, last_observed_wind_w=4500.0)


CLOUD = [30.0] * 24


def test_only_solar_channel_differs():
    a, b, w = _engines()
    ba = a.predict(_state(), {"fc_cloud_cover": CLOUD})
    bb = b.predict(_state(), {"fc_cloud_cover": CLOUD})
    assert w.calls == 2
    assert ba.timestamps == bb.timestamps
    assert ba.wind_generation.point == bb.wind_generation.point
    assert ba.demand.point == bb.demand.point
    assert ba.solar_generation.point != bb.solar_generation.point


def test_corrected_solar_equals_legacy_shifted_one_hour():
    """A-Fix at label L must equal legacy at label L-1h (same cloud), i.e. exactly a 1 h geometry shift."""
    a, b, _ = _engines()
    flat = [0.0] * 24
    fixed = b.predict(_state("2024-03-15T07:00:00"), {"fc_cloud_cover": flat}).solar_irradiance.point
    legacy = a.predict(_state("2024-03-15T06:00:00"), {"fc_cloud_cover": flat}).solar_irradiance.point
    assert fixed == legacy


def test_reserve_elevation_not_double_converted():
    """Reserve elevations come from bundle.timestamps, which must be identical in both arms."""
    import stage4_low_sun_adapter as s4a
    a, b, _ = _engines()
    prov = s4a.SolarElevationProvider(None)  # pvlib fallback, Etc/GMT-1; never the 2025 CSV
    ea = prov.get_elevation_vector(a.predict(_state(), {"fc_cloud_cover": CLOUD}).timestamps)
    eb = prov.get_elevation_vector(b.predict(_state(), {"fc_cloud_cover": CLOUD}).timestamps)
    assert ea == eb


def test_corrected_forecaster_matches_reserve_geometry():
    """After correction, forecaster sun elevation agrees with the reserve's UTC+1 elevation (<0.05 deg)."""
    import stage4_low_sun_adapter as s4a
    _, b, w = _engines()
    ts = pd.date_range("2024-03-15 08:00", periods=24, freq="h")
    utc_tagged = ts.tz_localize("UTC")
    el_fc = w.get_solarposition(utc_tagged)["elevation"].values
    prov = s4a.SolarElevationProvider(None)
    el_res = prov.get_elevation_vector([t.strftime("%Y-%m-%d %H:%M:%S") for t in ts])
    assert max(abs(x - y) for x, y in zip(el_fc, el_res)) < 0.05


def test_refuses_double_wrap():
    from solar_convention import apply_label_correction
    _, b, _ = _engines()
    with pytest.raises(RuntimeError):
        apply_label_correction(b)


def test_arm_configs_identical_except_correction():
    """The runner must expose per-arm configs; A and A-Fix may differ only in 'solar_label_correction'."""
    from run_three_arm_2024 import ARM_CONFIGS
    a, f = dict(ARM_CONFIGS["A"]), dict(ARM_CONFIGS["A_FIX"])
    assert a.pop("solar_label_correction") is False
    assert f.pop("solar_label_correction") is True
    a.pop("result_label"); f.pop("result_label")
    assert a == f
    assert ARM_CONFIGS["A"]["result_label"] == "LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT"
    assert ARM_CONFIGS["A_FIX"]["result_label"] == "DIAGNOSTIC — NOT PROMOTION-ELIGIBLE"
