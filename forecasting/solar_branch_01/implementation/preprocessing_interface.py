"""
Preprocessing Interface Module
Contract enforcing feature scaling and transformation fit strictly on training set.
"""

from typing import Union
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from system.governance.model_reproducibility import ModelGovernanceError


class PreprocessingInterface:
    """Standard scaler wrapper ensuring zero test set leakage."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, X_train: pd.DataFrame) -> None:
        """Fit scaler on training features strictly."""
        self.scaler.fit(X_train)
        self.is_fitted = True

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform features using fitted scaler parameters."""
        if not self.is_fitted:
            raise ModelGovernanceError("Fail-closed: Scaler must be fitted before transform.")
        return self.scaler.transform(X)

    def fit_transform(self, X_train: pd.DataFrame) -> np.ndarray:
        """Fit and transform training features strictly."""
        self.fit(X_train)
        return self.transform(X_train)
