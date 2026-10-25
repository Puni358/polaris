"""
Generic Model Interface Module
Abstract contract enforcing fit, predict, save, and load operations.
Supports TEST_ONLY mock model for pipeline infrastructure tests.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Union
import numpy as np
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class GenericModelInterface(ABC):
    """Abstract model interface contract for Branch 01 predictors."""

    @abstractmethod
    def fit(self, X_train: pd.DataFrame, Y_train: np.ndarray) -> None:
        """Fit model on training feature matrix and target matrix."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict 24-step target vectors for input feature matrix X."""
        pass

    @abstractmethod
    def save(self, path: Union[str, Path]) -> None:
        """Serialize model to disk."""
        pass

    @abstractmethod
    def load(self, path: Union[str, Path]) -> None:
        """Load serialized model from disk."""
        pass


class TestOnlyMockModel(GenericModelInterface):
    """
    DETERMINISTIC TEST_ONLY MOCK MODEL FIXTURE.
    Used strictly for testing serialization, schema validation, and replay infrastructure.
    MUST NOT be used for scientific forecasting, model fitting, or inference.
    """

    def __init__(self, is_fitted: bool = False, model_name: str = "TEST_ONLY_MOCK_MODEL"):
        self.is_fitted = is_fitted
        self.model_name = model_name
        self.label = "TEST_ONLY"

    def fit(self, X_train: pd.DataFrame, Y_train: np.ndarray) -> None:
        """Mock fit operation for test fixtures."""
        self.is_fitted = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate deterministic synthetic mock prediction Y_mock for test verification."""
        if not self.is_fitted:
            raise ModelGovernanceError("Fail-closed: Cannot predict with unfitted model.")

        n_samples = len(X)
        # Deterministic mock prediction based on clearsky_sw_in_origin or zeros
        mock_pred = np.zeros((n_samples, 24), dtype=np.float64)
        if "clearsky_sw_in_origin" in X.columns:
            cs = X["clearsky_sw_in_origin"].values
            for h in range(24):
                mock_pred[:, h] = cs * 0.5
        return mock_pred

    def save(self, path: Union[str, Path]) -> None:
        import joblib
        data = {
            "model_name": self.model_name,
            "is_fitted": self.is_fitted,
            "label": self.label
        }
        joblib.dump(data, path)

    def load(self, path: Union[str, Path]) -> None:
        import joblib
        data = joblib.load(path)
        if data.get("label") != "TEST_ONLY":
            raise ModelGovernanceError("Loaded object is not a valid TEST_ONLY mock model.")
        self.model_name = data["model_name"]
        self.is_fitted = data["is_fitted"]
        self.label = data["label"]
