"""
Forecast Origin Generator Module
Dynamically derives supported forecast origins t from data contracts and causal availability.
Does NOT hardcode 8784.
"""

from typing import List, Tuple
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class OriginGenerator:
    """Generates valid MPC forecast origins t based on lookback and target availability."""

    def __init__(self, lookback_hours: int = 24, target_hours: int = 24):
        self.lookback_hours = lookback_hours
        self.target_hours = target_hours

    def derive_supported_origins(self, df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DatetimeIndex:
        """
        Derive valid forecast origins t requiring:
        1. Historical lookback window of `lookback_hours` exists ending at t.
        2. Target window of `target_hours` exists starting at t+1.
        """
        if timestamp_col not in df.columns:
            raise ModelGovernanceError(f"Missing required timestamp column: {timestamp_col}")

        n_total = len(df)
        min_start_idx = self.lookback_hours
        max_end_idx = n_total - self.target_hours

        if min_start_idx >= max_end_idx:
            raise ModelGovernanceError("Insufficient dataframe length to satisfy lookback and target requirements.")

        valid_origins = df[timestamp_col].iloc[min_start_idx:max_end_idx].reset_index(drop=True)
        return pd.DatetimeIndex(valid_origins)
