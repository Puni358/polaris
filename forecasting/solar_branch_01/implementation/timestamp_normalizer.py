"""
Timestamp Normalizer Module
Enforces strict ISO-8601 UTC timestamp formatting and monotonic increasing order.
"""

from datetime import datetime, timezone
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class TimestampNormalizer:
    """Normalizes timestamps to UTC DatetimeIndex and validates monotonicity."""

    @staticmethod
    def normalize_series(series: pd.Series) -> pd.DatetimeIndex:
        """
        Convert series to UTC DatetimeIndex and verify monotonic strictly increasing order.
        """
        try:
            dt_index = pd.DatetimeIndex(pd.to_datetime(series, utc=True))
        except Exception as e:
            raise ModelGovernanceError(f"Timestamp normalization failure: {str(e)}")

        if not dt_index.is_monotonic_increasing:
            raise ModelGovernanceError("Timestamps are not strictly monotonic increasing.")

        if dt_index.has_duplicates:
            raise ModelGovernanceError("Duplicate timestamps detected in time series.")

        return dt_index

    @staticmethod
    def to_iso8601_utc(dt: datetime) -> str:
        """Convert datetime object to canonical ISO-8601 UTC string (YYYY-MM-DDTHH:MM:SSZ)."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def canonicalize_string(ts_str: str) -> str:
        """Convert any valid timestamp representation to canonical YYYY-MM-DDTHH:MM:SSZ."""
        if not isinstance(ts_str, str) or not ts_str.strip():
            raise ModelGovernanceError(f"Invalid timestamp representation: '{ts_str}'")
        s = ts_str.strip().replace(" ", "T").replace("+00:00", "Z")
        if not s.endswith("Z"):
            s += "Z"
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            raise ModelGovernanceError(f"Failed to canonicalize timestamp '{ts_str}': {e}")

