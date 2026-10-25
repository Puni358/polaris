"""
Baseline Interface Module
Abstract interface and reference implementations for benchmark baselines (Persistence, Clear-Sky ratio).
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd


class BaselineInterface(ABC):
    """Abstract interface for baseline predictors."""

    @abstractmethod
    def predict_origin(self, origin_t: pd.Timestamp, historical_sw_in: np.ndarray, clearsky_sw_in: np.ndarray) -> np.ndarray:
        """Return 24-element prediction vector Y_base(t)."""
        pass


class PersistenceBaseline(BaselineInterface):
    """24h persistence baseline repeating last observed SW_IN value at origin t."""

    def predict_origin(self, origin_t: pd.Timestamp, historical_sw_in: np.ndarray, clearsky_sw_in: np.ndarray) -> np.ndarray:
        last_val = historical_sw_in[-1]
        return np.full(24, last_val, dtype=np.float64)


class ClearSkyRatioBaseline(BaselineInterface):
    """Clear-sky ratio persistence baseline: kt(t) * clearsky_sw_in(t+h)."""

    def predict_origin(self, origin_t: pd.Timestamp, historical_sw_in: np.ndarray, clearsky_sw_in: np.ndarray) -> np.ndarray:
        last_obs = historical_sw_in[-1]
        last_cs = clearsky_sw_in[0]  # CS at origin
        kt = (last_obs / last_cs) if last_cs > 1.0 else 0.0
        kt = max(0.0, min(1.5, kt))
        cs_future = clearsky_sw_in[1:25]
        return (kt * cs_future).astype(np.float64)
