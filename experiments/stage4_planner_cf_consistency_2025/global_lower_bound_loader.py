"""
Real-data loader infrastructure for the global lower bound (EXP-PLANNER-CF-CONSISTENCY-2025, Study 1).

INFRASTRUCTURE ONLY. Nothing in this module reads real data at import time. The loader is called
only by the authorized AGY run. Tests use synthetic fixtures with the same schema.

The loader FAILS CLOSED on: wrong population count, duplicate origins, missing or duplicate hours,
wrong horizon, timestamp misalignment, NaN or negative values, SW_IN mismatch against the SITES
file, and file-hash mismatch when pins are supplied.

Derivations (identical to the oracle and corrected runners; checked against them in tests):
  PV_t      = min(max(0, SW_IN_t * 300 * 0.20 * 0.85), 60000) W          (pv_from_sw_in)
  wind_t    = max(0, round(4500 + 5000 * sin((t+1) * pi/6), 2)) W        (oracle_runner.wind_w)
  demand_t  = max(10000, round(15000 + 3000 * cos((t+1) * pi/12), 2)) W  (oracle_runner.demand_w)
  critical  = min(11600, demand_t);  non-critical = demand_t - critical
  initial   = SOC 50 % (E0 = 100,000 Wh), diesel off, fuel 100 L (recorded, not used by the bound)
"""

import hashlib
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

WINDOW_START = pd.Timestamp("2025-05-01 00:00:00")
WINDOW_END = pd.Timestamp("2025-08-31 00:00:00")
N_ORIGINS = 123
HOURS = 24
PV_AREA_M2 = 300.0
PV_EFF = 0.20
PV_PR = 0.85
PV_MAX_W = 60000.0
CRITICAL_CEILING_W = 11600.0
DEMAND_FLOOR_W = 10000.0
INITIAL_E0_WH = 100000.0
INITIAL_SOC_PCT = 50.0
INITIAL_FUEL_L = 100.0
SW_MATCH_TOL = 1e-9

WEATHER_COLS = ("forecast_start", "horizon_hour", "timestamp", "actual_SW_IN")
SITES_COLS = ("TIMESTAMP", "SW_IN")


class LoaderError(RuntimeError):
    """Raised on any failed check. The loader never returns partial data."""


@dataclass
class OriginRecord:
    origin_index: int
    forecast_start: str
    timestamps: List[str]
    solar_w: List[float]
    wind_w: List[float]
    demand_w: List[float]
    critical_w: List[float]
    noncritical_w: List[float]
    initial_state: Dict[str, float] = field(default_factory=lambda: {
        "E0_wh": INITIAL_E0_WH, "soc_pct": INITIAL_SOC_PCT, "diesel_on": False, "fuel_l": INITIAL_FUEL_L})


def pv_from_sw_in(sw_in: float) -> float:
    return max(0.0, min(float(sw_in) * PV_AREA_M2 * PV_EFF * PV_PR, PV_MAX_W))


def wind_w(t: int) -> float:
    return max(0.0, round(4500.0 + 5000.0 * math.sin((t + 1) * math.pi / 6.0), 2))


def demand_w(t: int) -> float:
    return max(DEMAND_FLOOR_W, round(15000.0 + 3000.0 * math.cos((t + 1) * math.pi / 12.0), 2))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _require_columns(df: pd.DataFrame, cols: Sequence[str], name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise LoaderError(f"{name}: missing columns {missing}")


def load_population(weather_csv: Path, sites_csv: Path, *,
                    expected_weather_sha256: Optional[str] = None,
                    expected_sites_sha256: Optional[str] = None) -> List[OriginRecord]:
    """Validates and derives the 123-origin population. Fails closed on any violation."""
    weather_csv, sites_csv = Path(weather_csv), Path(sites_csv)
    if expected_weather_sha256 is not None and sha256_file(weather_csv) != expected_weather_sha256:
        raise LoaderError("weather file hash mismatch")
    if expected_sites_sha256 is not None and sha256_file(sites_csv) != expected_sites_sha256:
        raise LoaderError("SITES file hash mismatch")

    w = pd.read_csv(weather_csv)
    s = pd.read_csv(sites_csv)
    _require_columns(w, WEATHER_COLS, "weather")
    _require_columns(s, SITES_COLS, "SITES")

    fs_all = pd.to_datetime(w["forecast_start"], errors="coerce")
    w = w.assign(_fs=fs_all)
    in_window = w[(w["_fs"] >= WINDOW_START) & (w["_fs"] <= WINDOW_END)].copy()
    if in_window["_fs"].isna().any():
        raise LoaderError("unparseable forecast_start in window")
    for c in ("horizon_hour", "timestamp", "actual_SW_IN"):
        if in_window[c].isna().any():
            raise LoaderError(f"NaN in {c}")
    if (in_window["actual_SW_IN"].astype(float) < 0).any():
        raise LoaderError("negative actual_SW_IN")

    starts = sorted(in_window["_fs"].unique())
    if len(starts) != N_ORIGINS:
        raise LoaderError(f"population count {len(starts)} != {N_ORIGINS}")

    if in_window.duplicated(["_fs", "horizon_hour"]).any():
        raise LoaderError("duplicate (forecast_start, horizon_hour) rows")

    sites_map = dict(zip(s["TIMESTAMP"].astype(str), s["SW_IN"].astype(float)))
    if s["SW_IN"].isna().any():
        raise LoaderError("NaN in SITES SW_IN")

    records: List[OriginRecord] = []
    for idx, fs in enumerate(starts, start=1):
        sub = in_window[in_window["_fs"] == fs].sort_values("horizon_hour")
        if len(sub) != HOURS:
            raise LoaderError(f"origin {fs}: {len(sub)} rows, expected {HOURS}")
        hours = sub["horizon_hour"].astype(int).tolist()
        expected_hours = list(range(1, HOURS + 1))
        if hours != expected_hours:
            raise LoaderError(
                f"origin {fs}: canonical horizon_hour must be "
                f"1..{HOURS}, got {hours}"
            )
        ts = sub["timestamp"].astype(str).tolist()
        expected_ts = [(fs + pd.Timedelta(hours=t)).strftime("%Y-%m-%d %H:%M:%S") for t in range(HOURS)]
        if [str(pd.Timestamp(x)) for x in ts] != [str(pd.Timestamp(x)) for x in expected_ts]:
            raise LoaderError(f"origin {fs}: timestamps are not forecast_start + 0..{HOURS - 1} hours")
        sw = sub["actual_SW_IN"].astype(float).tolist()
        for t, (tsv, v) in enumerate(zip(expected_ts, sw)):
            if tsv not in sites_map:
                raise LoaderError(f"origin {fs}: SITES has no timestamp {tsv}")
            if abs(sites_map[tsv] - v) > SW_MATCH_TOL:
                raise LoaderError(f"origin {fs}: SW_IN mismatch at {tsv}")
        solar = [pv_from_sw_in(v) for v in sw]
        wind = [wind_w(t) for t in range(HOURS)]
        dem = [demand_w(t) for t in range(HOURS)]
        crit = [min(CRITICAL_CEILING_W, d) for d in dem]
        noncrit = [d - c for d, c in zip(dem, crit)]
        records.append(OriginRecord(origin_index=idx, forecast_start=str(pd.Timestamp(fs)),
                                    timestamps=expected_ts, solar_w=solar, wind_w=wind, demand_w=dem,
                                    critical_w=crit, noncritical_w=noncrit))
    if len({r.forecast_start for r in records}) != N_ORIGINS:
        raise LoaderError("duplicate origins after derivation")
    return records


def to_origin_inputs(records: Sequence[OriginRecord]):
    """Converts validated records to the global-bound input type (no file access)."""
    import global_lower_bound as g
    return [g.OriginInputs(origin_id=r.origin_index, solar_w=r.solar_w, wind_w=r.wind_w, demand_w=r.demand_w,
                           e0_wh=float(r.initial_state["E0_wh"])) for r in records]
