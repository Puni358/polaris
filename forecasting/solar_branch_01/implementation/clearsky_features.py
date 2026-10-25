"""
Clear-Sky Features Module
Provides physical clear-sky reference features at forecast origin t.
"""

from datetime import datetime
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class ClearSkyFeatureBuilder:
    """Extracts clear-sky irradiance features for origin t."""

    @classmethod
    def compute_features(cls, clearsky_df: pd.DataFrame, origin_t: datetime) -> dict:
        """
        Lookup physical clear-sky SW_IN at origin_t.
        """
        if hasattr(origin_t, "strftime"):
            origin_t_str = origin_t.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            origin_t_str = str(origin_t)

        match = clearsky_df[clearsky_df["timestamp"] == origin_t_str]
        if match.empty:
            match = clearsky_df[clearsky_df["timestamp"] == origin_t]
        if match.empty:
            raise ModelGovernanceError(f"Fail-closed: No clear-sky reference found for timestamp {origin_t}")

        cs_col = "clearsky_sw_in" if "clearsky_sw_in" in match.columns else "clearsky_ghi"
        cs_val = float(match[cs_col].iloc[0])
        return {"clearsky_sw_in_origin": cs_val}
