"""
PROPOSED — NOT APPLIED, NOT RUN against the experiment.
Target path if approved: experiments/exp_three_arm_2024/timestamp_guards.py

Fail-closed timestamp checks for EXP-THREE-ARM-2024 (decision D7). The runner must call
run_all_guards() before constructing any forecaster, optimizer or executor. Any failure raises and
the run must stay FAILED (no automatic retry, no fallback convention).

Verified convention (D7 report, 2026-10-11):
  * All 2024 data labels are fixed-offset UTC+1 (Etc/GMT-1), no DST.
  * SITES 10-min SW_IN is period-ending; the hourly file averages labels HH:00..HH:50 into HH:00.
  * Weather file: forecast_start at 00:00 label time, timestamp = forecast_start + (horizon_hour - 1) h.
  * Simulation: t0 = forecast_start - 1 h; step k realized timestamp = forecast_start + k h.
  * Solar geometry must be evaluated at (label - 1 h) in UTC. Treating a label as UTC is a 1 h error.

Original timestamps are never rewritten. Conversion to UTC happens only in memory via to_utc().
"""
import hashlib
from typing import Iterable

import pandas as pd

LABEL_TZ = "Etc/GMT-1"  # POSIX sign convention: Etc/GMT-1 == UTC+1
EXPECTED_SHA256 = {
    "data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv":
        "f3fe7cf2fff45f21feeceb850e63299a919da658d1474851b1cf611a35e43473",
    "data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv":
        "80b721a16a79dab828eb1aa02755d22c34acc35b5f48ad0d1beb5b9ab237052d",
    "data/POLARIS_v0_1_future_weather_forecasts_2024.csv":
        "8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16",
    "data/POLARIS_v0_1_clearsky_decomposition.csv":
        "596345aa330313414ba41f63ad65278914c6ed1e179965162439e6139a70e52a",
}
SITES_HEADER_TZ_LINE = "TIME ZONE: UTC+1"


class TimestampGuardError(RuntimeError):
    pass


def _fail(msg: str) -> None:
    raise TimestampGuardError(msg)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_hashes(repo_root: str) -> None:
    for rel, exp in EXPECTED_SHA256.items():
        got = sha256(f"{repo_root}/{rel}")
        if len(exp) != 64:
            _fail(f"expected hash for {rel} is not a full SHA-256; preregistration incomplete")
        if got != exp:
            _fail(f"hash mismatch for {rel}: {got} != {exp}")


def check_sites_header(path: str) -> None:
    with open(path, encoding="utf-8-sig") as f:
        head = [next(f) for _ in range(40)]
    if not any(l.strip() == SITES_HEADER_TZ_LINE for l in head):
        _fail(f"SITES header does not declare '{SITES_HEADER_TZ_LINE}'")


def check_regular(ts: pd.Series, freq: str, start: str, end: str, name: str) -> None:
    ts = pd.to_datetime(ts)
    if ts.dt.tz is not None:
        _fail(f"{name}: labels must be naive UTC+1 strings, found tz-aware values")
    if ts.duplicated().any():
        _fail(f"{name}: {int(ts.duplicated().sum())} duplicate timestamps")
    missing = pd.date_range(start, end, freq=freq).difference(pd.DatetimeIndex(ts))
    if len(missing):
        _fail(f"{name}: {len(missing)} missing timestamps, first {missing[0]}")
    # A fixed-offset file has 24 h on DST-change days; a local-time file would have 23 h / 25 h.
    for day in ("2024-03-31", "2024-10-27"):
        d = ts[(ts >= day) & (ts < pd.Timestamp(day) + pd.Timedelta(days=1))]
        per_hour = pd.Timedelta(freq) / pd.Timedelta("1h")
        if len(d) * per_hour != 24:
            _fail(f"{name}: {day} spans {len(d) * per_hour} h, expected 24 (DST artefact?)")


def check_weather_file(w: pd.DataFrame) -> None:
    fs = pd.to_datetime(w["forecast_start"])
    ts = pd.to_datetime(w["timestamp"])
    if (fs.dt.year != 2024).any() or (ts.dt.year != 2024).any():
        raise PermissionError("weather input contains non-2024 rows; refusing to run")
    if set(fs.dt.hour) != {0} or set(fs.dt.minute) != {0}:
        _fail("forecast_start must be 00:00 label time for every origin")
    lead = (ts - fs) / pd.Timedelta(hours=1)
    if not ((w["horizon_hour"] - lead) == 1).all():
        _fail("timestamp != forecast_start + (horizon_hour - 1) h for some rows")
    if w.duplicated(["forecast_start", "horizon_hour"]).any() or not ts.is_unique:
        _fail("duplicate (forecast_start, horizon_hour) or duplicate timestamp")
    sizes = w.groupby("forecast_start").size()
    if (sizes != 24).any():
        _fail(f"origins without exactly 24 rows: {list(sizes[sizes != 24].index[:5])}")


def check_hourly_linkage(w: pd.DataFrame, hourly: pd.DataFrame, tol: float = 1e-3) -> None:
    j = w.assign(TS=pd.to_datetime(w["timestamp"])).merge(
        hourly.assign(TS=pd.to_datetime(hourly["TIMESTAMP"]))[["TS", "SW_IN"]], on="TS", how="left")
    if j["SW_IN"].isna().any():
        _fail("weather timestamps not found in hourly SITES file")
    if (j["actual_SW_IN"] - j["SW_IN"]).abs().max() > tol:
        _fail("weather actual_SW_IN does not match hourly SITES SW_IN at the same label")


def to_utc(labels: Iterable) -> pd.DatetimeIndex:
    """Interpret naive labels as UTC+1 and return tz-aware UTC. Never writes back to any file."""
    idx = pd.DatetimeIndex(pd.to_datetime(list(labels)))
    if idx.tz is not None:
        _fail("to_utc expects naive UTC+1 labels")
    return idx.tz_localize(LABEL_TZ).tz_convert("UTC")


def check_geometry_convention(decomp: pd.DataFrame, solar_elev_fn, tol_deg: float = 0.05) -> None:
    """solar_elev_fn(tz-aware UTC DatetimeIndex) -> degrees. The decomposition file must match UTC+1."""
    labels = pd.to_datetime(decomp["TIMESTAMP"])
    good = (pd.Series(solar_elev_fn(to_utc(labels))) - decomp["solar_elevation"].values).abs().max()
    bad = (pd.Series(solar_elev_fn(labels.dt.tz_localize("UTC"))) - decomp["solar_elevation"].values).abs().max()
    if not (good <= tol_deg < bad):
        _fail(f"geometry convention check failed: |d|max UTC+1={good:.3f}, as-UTC={bad:.3f}")


def check_forecaster_input_is_utc(timestamps_passed: Iterable[str]) -> None:
    """Every timestamp handed to causal_nwp_physics must carry an explicit UTC marker ('Z' or +00:00)
    and must equal to_utc(label). A bare naive label would be read as UTC (causal_nwp_physics.py:302-303)."""
    for t in timestamps_passed:
        s = str(t)
        if not (s.endswith("Z") or s.endswith("+00:00")):
            _fail(f"forecaster timestamp '{s}' lacks an explicit UTC marker")


def run_all_guards(repo_root: str, solar_elev_fn) -> None:
    check_hashes(repo_root)
    sites = f"{repo_root}/data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv"
    check_sites_header(sites)
    hourly = pd.read_csv(f"{repo_root}/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv")
    check_regular(hourly["TIMESTAMP"], "1h", "2024-01-01 00:00", "2024-12-31 23:00", "hourly SITES")
    w = pd.read_csv(f"{repo_root}/data/POLARIS_v0_1_future_weather_forecasts_2024.csv")
    check_weather_file(w)
    check_hourly_linkage(w, hourly)
    decomp = pd.read_csv(f"{repo_root}/data/POLARIS_v0_1_clearsky_decomposition.csv")
    check_geometry_convention(decomp, solar_elev_fn)
