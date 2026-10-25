"""Input-integrity checks on the 2024 source files (D7 item 6). Reads only 2024 files:
SITES 2024 raw, SITES 2024 hourly, the 2024 weather file and the 2024 clear-sky decomposition.
No model, optimizer, executor or calibration is run."""
from pathlib import Path

import numpy as np
import pandas as pd
import pvlib

import timestamp_guards as tg

REPO = Path(__file__).resolve().parents[3]
LAT, LON = 68.362074, 18.738752


def _pvlib_elev_utc(idx_utc):
    loc = pvlib.location.Location(LAT, LON, tz="UTC")
    return loc.get_solarposition(pd.DatetimeIndex(idx_utc))["elevation"].values


def test_run_all_guards_pass():
    tg.run_all_guards(str(REPO), _pvlib_elev_utc)


def test_reserve_provider_matches_2024_decomposition():
    """The new runner's reserve path is SolarElevationProvider(None) (pvlib, Etc/GMT-1). The winner's reserve
    read a precomputed decomposition CSV. Compare the two methods on the 2024 decomposition (same builder,
    same convention). Tolerance 0.05 deg: about 12 s of solar motion, more than 100x smaller than the
    ~1 h (several degrees) defect the check must detect, and loose enough for pvlib-version rounding."""
    import stage4_low_sun_adapter as s4a
    dc = pd.read_csv(REPO / "data" / "POLARIS_v0_1_clearsky_decomposition.csv")
    prov = s4a.SolarElevationProvider(None)
    el = np.array(prov.get_elevation_vector([str(t) for t in dc["TIMESTAMP"]]))
    d = np.abs(el - dc["solar_elevation"].values)
    print(f"reserve_provider_vs_decomposition_2024: max_abs_deg={d.max():.6f} mean_abs_deg={d.mean():.6f} n={len(d)}")
    assert d.max() < 0.05
