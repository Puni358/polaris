"""
PROPOSED — NOT APPLIED, NOT RUN.
Target path if approved: experiments/exp_three_arm_2024/solar_convention.py

Arm A-Fix correction for the D7 solar-position defect (decision D7a).

Why a Location wrapper and not converted timestamps:
  causal_nwp_physics.predict() takes station_state.timestamp and builds its 24 target times from it.
  The same timestamp also drives the baseline wind/demand channels (system/forecasting/implementations/
  baseline.py uses future_dt.hour), the weather lookup, the reserve's elevation lookup
  (bundle.timestamps -> SolarElevationProvider, which strips 'Z' and localizes Etc/GMT-1) and the
  executor's state chain. Passing UTC-converted timestamps would therefore (a) shift the wind and demand
  forecasts and (b) double-convert the reserve's solar elevation. Both would break arm parity.

  The wrapper changes exactly one thing: the instants at which pvlib evaluates sun position and clear-sky
  GHI inside the forecaster. Labels, cloud values, wind, demand, bundle.timestamps and everything
  downstream stay identical to Arm A. causal_nwp_physics.py stays byte-identical (SHA 14e72d8a...).

Mechanism: the forecaster builds dt_index = label-clock tagged as UTC (lines 302-303, 334). The true
UTC instant of a UTC+1 label is label - 1 h. The wrapper subtracts 1 h before calling pvlib and returns
results re-indexed to the original dt_index, so the forecaster's .iloc[h] reads are unchanged in shape.
"""
import pandas as pd

LABEL_UTC_OFFSET = pd.Timedelta(hours=1)  # verified in D7: labels are fixed UTC+1


class LabelCorrectedLocation:
    """Drop-in for the pvlib Location used by CausalNwpPhysicsForecastEngine (get_solarposition and
    get_clearsky only). Any other attribute access is refused so an unreviewed path cannot slip through."""

    _ALLOWED = ("get_solarposition", "get_clearsky")

    def __init__(self, inner):
        self._inner = inner
        self.calls = 0  # telemetry: proves the wrapper was actually used

    def _shift(self, times):
        idx = pd.DatetimeIndex(times)
        if idx.tz is None or str(idx.tz) != "UTC":
            raise ValueError(f"expected label-clock index tagged UTC, got tz={idx.tz}")
        return idx - LABEL_UTC_OFFSET, idx

    def get_solarposition(self, times, *a, **k):
        true_utc, orig = self._shift(times)
        self.calls += 1
        out = self._inner.get_solarposition(true_utc, *a, **k)
        out.index = orig
        return out

    def get_clearsky(self, times, *a, **k):
        true_utc, orig = self._shift(times)
        self.calls += 1
        out = self._inner.get_clearsky(true_utc, *a, **k)
        out.index = orig
        return out

    def __getattr__(self, name):
        raise AttributeError(f"LabelCorrectedLocation does not expose '{name}' (unreviewed path)")


def apply_label_correction(engine) -> LabelCorrectedLocation:
    """Arm A-Fix only. Wraps engine.location once; refuses to wrap twice (double-conversion guard)."""
    if isinstance(engine.location, LabelCorrectedLocation):
        raise RuntimeError("solar label correction already applied; refusing double conversion")
    if str(getattr(engine.location, "tz", "")) != "UTC":
        raise RuntimeError("forecaster Location tz is no longer 'UTC'; D7 premise changed, re-verify")
    wrapper = LabelCorrectedLocation(engine.location)
    engine.location = wrapper
    return wrapper
