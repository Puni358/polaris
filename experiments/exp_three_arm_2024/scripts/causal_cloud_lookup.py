"""
Causal cloud-trajectory lookup for EXP-THREE-ARM-2024 (research only).

Fixes finding L1: the existing runners build `weather_lookup` from the WHOLE weather file keyed by
timestamp (system/research/closed_loop_causal_nwp_runner.py:183-218,
system/research/research_critical_demand_adapter.py:84-104,
experiments/stage4_planner_cf_consistency_2025/planner_cf_campaign_runner.py:105-116). With
t0 = forecast_start - 1 h, step k requests targets forecast_start + k .. forecast_start + 23 + k, so the
last k targets are read from the NEXT origin's forecast package, which is not established as available
at decision time forecast_start - 1 h + k.

Rule implemented here (most conservative, no latency assumption needed):
  - Only the 24 rows of the CURRENT origin's package (the one available at t0) may be used.
  - Targets beyond that package's last timestamp are filled by holding the package's last value
    (persistence of the final forecast hour). The number of held hours is returned for telemetry.
"""
from typing import Dict, List, Tuple

import pandas as pd


class OriginCloudPackage:
    def __init__(self, weather_df: pd.DataFrame, forecast_start: str):
        sub = weather_df[weather_df["forecast_start"] == forecast_start].sort_values("horizon_hour")
        if len(sub) != 24:
            raise RuntimeError(f"origin {forecast_start} has {len(sub)} rows, expected 24")
        ts = pd.to_datetime(sub["timestamp"], utc=True)
        vals = [float(v) for v in sub["fc_cloud_cover"]]
        for v in vals:
            if not (0.0 <= v <= 100.0):
                raise ValueError(f"invalid cloud cover {v} in origin {forecast_start}")
        self.forecast_start = forecast_start
        self._lookup: Dict[pd.Timestamp, float] = dict(zip(ts, vals))
        self.first_ts = ts.min()
        self.last_ts = ts.max()
        self.last_val = vals[-1]

    def trajectory(self, decision_dt: pd.Timestamp) -> Tuple[List[float], int]:
        """24 cloud values for targets decision_dt + 1h .. + 24h, using only this package."""
        decision_dt = pd.Timestamp(decision_dt)
        if decision_dt.tzinfo is None:
            decision_dt = decision_dt.tz_localize("UTC")
        out: List[float] = []
        held = 0
        for h in range(1, 25):
            t = decision_dt + pd.Timedelta(hours=h)
            if t < self.first_ts:
                raise ValueError(f"target {t} precedes package start {self.first_ts}")
            if t <= self.last_ts:
                out.append(self._lookup[t])
            else:
                out.append(self.last_val)
                held += 1
        return out, held


def assert_no_protected_dates(weather_df: pd.DataFrame) -> None:
    """Fail closed if any row of the input belongs to 2025 (blind window, boundaries or otherwise)."""
    fs = pd.to_datetime(weather_df["forecast_start"])
    ts = pd.to_datetime(weather_df["timestamp"])
    if (fs.dt.year != 2024).any() or (ts.dt.year != 2024).any():
        raise PermissionError("EXP-THREE-ARM-2024 input contains non-2024 rows; refusing to run.")
