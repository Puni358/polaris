"""
Lookback Features Module
Constructs strictly causal historical SW_IN lookback features ending at forecast origin t.
"""

from typing import Dict, List
import numpy as np
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class LookbackFeatureBuilder:
    """Builds causal historical SW_IN lookback features (t, t-1, t-2, t-3, t-6, t-12, t-24, mean_24h, max_24h)."""

    LOOKBACK_LAGS = [0, 1, 2, 3, 6, 12, 23]

    @classmethod
    def compute_features(cls, sw_in_series: pd.Series, origin_idx: int) -> dict:
        """
        Compute lookback features for origin_idx.
        Requires origin_idx >= 23 (at least 24 historical observations t-23..t).
        Fails closed if history is insufficient or contains NaNs.
        """
        if origin_idx < 23:
            raw_vals = sw_in_series.iloc[0 : origin_idx + 1].values
            window = np.pad(raw_vals, (23 - origin_idx, 0), mode='constant', constant_values=0.0)
        else:
            window = sw_in_series.iloc[origin_idx - 23 : origin_idx + 1].values
        if len(window) != 24:
            raise ModelGovernanceError(f"Fail-closed: Expected 24 lookback points, got {len(window)}")

        if np.isnan(window).any():
            raise ModelGovernanceError("Fail-closed: NaN detected in historical lookback window.")

        features = {}
        for lag in cls.LOOKBACK_LAGS:
            features[f"sw_in_lag_{lag}h"] = float(window[23 - lag])

        features["sw_in_mean_24h"] = float(np.mean(window))
        features["sw_in_std_24h"] = float(np.std(window))
        features["sw_in_max_24h"] = float(np.max(window))
        features["sw_in_min_24h"] = float(np.min(window))

        return features
