"""
Feature Matrix Builder Module
Assembles complete deterministic feature matrix X(t) with fixed column ordering.
"""

from typing import List, Tuple
import numpy as np
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError
from forecasting.solar_branch_01.implementation.astronomical_features import AstronomicalFeatureBuilder
from forecasting.solar_branch_01.implementation.lookback_features import LookbackFeatureBuilder
from forecasting.solar_branch_01.implementation.clearsky_features import ClearSkyFeatureBuilder


class FeatureMatrixBuilder:
    """Assembles X(t) feature vectors with deterministic ordering and provenances."""

    ORDERED_FEATURE_NAMES = [
        "sw_in_lag_0h",
        "sw_in_lag_1h",
        "sw_in_lag_2h",
        "sw_in_lag_3h",
        "sw_in_lag_6h",
        "sw_in_lag_12h",
        "sw_in_lag_23h",
        "sw_in_mean_24h",
        "sw_in_std_24h",
        "sw_in_max_24h",
        "sw_in_min_24h",
        "solar_elevation",
        "solar_zenith",
        "sin_hour",
        "cos_hour",
        "sin_doy",
        "cos_doy",
        "clearsky_sw_in_origin"
    ]

    @classmethod
    def build_feature_vector(
        cls,
        sw_in_series: pd.Series,
        timestamps: pd.Series,
        origin_idx: int,
        clearsky_df: pd.DataFrame
    ) -> np.ndarray:
        """
        Build single 18-element feature vector X(t) for origin index origin_idx.
        """
        origin_t = timestamps.iloc[origin_idx]

        lookback_feats = LookbackFeatureBuilder.compute_features(sw_in_series, origin_idx)
        astro_feats = AstronomicalFeatureBuilder.compute_features(origin_t)
        cs_feats = ClearSkyFeatureBuilder.compute_features(clearsky_df, origin_t)

        all_feats = {**lookback_feats, **astro_feats, **cs_feats}

        vec = []
        for name in cls.ORDERED_FEATURE_NAMES:
            if name not in all_feats:
                raise ModelGovernanceError(f"Missing required feature: {name}")
            vec.append(all_feats[name])

        return np.array(vec, dtype=np.float64)

    @classmethod
    def build_feature_matrix(
        cls,
        obs_df: pd.DataFrame,
        clearsky_df: pd.DataFrame,
        sw_col: str = "SW_IN"
    ) -> Tuple[pd.DatetimeIndex, pd.DataFrame]:
        """
        Build feature matrix X for all valid origins in obs_df.
        Returns (valid_origins, feature_dataframe).
        """
        origins = []
        rows = []
        n_rows = len(obs_df)

        for idx in range(n_rows):
            origin_t = obs_df["timestamp"].iloc[idx]
            try:
                vec = cls.build_feature_vector(obs_df[sw_col], obs_df["timestamp"], idx, clearsky_df)
                origins.append(origin_t)
                rows.append(vec)
            except ModelGovernanceError:
                continue

        X_df = pd.DataFrame(rows, columns=cls.ORDERED_FEATURE_NAMES)
        return pd.DatetimeIndex(origins), X_df
