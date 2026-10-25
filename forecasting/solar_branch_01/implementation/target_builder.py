"""
Target Builder Module
Constructs multi-output target vector Y(t) = [SW_IN(t+1), ..., SW_IN(t+24)].
Ground-truth target construction only — NOT forecast generation.
"""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class TargetBuilder:
    """Builds ground-truth 24-hour target vectors Y(t) for forecast origins t."""

    HORIZONS = list(range(1, 25))  # t+1 to t+24

    @classmethod
    def build_target_vector(cls, sw_in_series: pd.Series, origin_idx: int, allow_padding: bool = False) -> np.ndarray:
        """
        Extract target vector Y(t) = [SW_IN(origin_idx + 1) ... SW_IN(origin_idx + 24)].
        Pads with 0.0 W/m^2 for horizons extending past series end if allow_padding is True.
        """
        if origin_idx + 24 >= len(sw_in_series):
            if not allow_padding:
                raise ModelGovernanceError("Fail-closed: Incomplete target horizon extends past series end.")
            avail = sw_in_series.iloc[origin_idx + 1 :].values
            pad_needed = 24 - len(avail)
            target_vals = np.pad(avail, (0, pad_needed), mode='constant', constant_values=0.0)
        else:
            target_vals = sw_in_series.iloc[origin_idx + 1 : origin_idx + 25].values

        if len(target_vals) != 24:
            raise ModelGovernanceError(f"Fail-closed: Expected 24 target values, got {len(target_vals)}")

        if np.isnan(target_vals).any():
            raise ModelGovernanceError("Fail-closed: NaN detected in ground-truth target vector.")

        return target_vals.astype(np.float64)

    @classmethod
    def build_target_matrix(cls, df: pd.DataFrame, sw_col: str = "SW_IN") -> Tuple[pd.DatetimeIndex, np.ndarray]:
        """
        Build target matrix Y for all eligible origins in df.
        Returns (origin_timestamps, target_matrix_24d).
        """
        origins = []
        target_rows = []
        n_rows = len(df)

        for idx in range(n_rows):
            origin_t = df["timestamp"].iloc[idx]
            try:
                y_vec = cls.build_target_vector(df[sw_col], idx, allow_padding=True)
                origins.append(origin_t)
                target_rows.append(y_vec)
            except ModelGovernanceError:
                continue

        return pd.DatetimeIndex(origins), np.array(target_rows, dtype=np.float64)
