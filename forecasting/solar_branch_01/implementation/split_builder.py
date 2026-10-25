"""
Split Builder Module
Chronological split builder enforcing 24h embargo boundary protection between splits.
"""

from typing import Dict, Tuple
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class SplitBuilder:
    """
    Enforces approved chronological splits:
    - Train: 2024-01-01 through 2024-08-31
    - Validation: 2024-09-01 through 2024-10-31
    - Test: 2024-11-01 through 2024-12-31

    Applies 24h embargo protection: origins whose target window t+1..t+24 extends into the next split boundary are excluded.
    """

    TRAIN_START = pd.Timestamp("2024-01-01T00:00:00Z")
    TRAIN_END = pd.Timestamp("2024-08-31T23:00:00Z")

    VAL_START = pd.Timestamp("2024-09-01T00:00:00Z")
    VAL_END = pd.Timestamp("2024-10-31T23:00:00Z")

    TEST_START = pd.Timestamp("2024-11-01T00:00:00Z")
    TEST_END = pd.Timestamp("2024-12-31T23:00:00Z")

    EMBARGO_HOURS = 24

    @classmethod
    def apply_split(
        cls,
        origins: pd.DatetimeIndex,
        X_df: pd.DataFrame,
        Y_mat: pd.DataFrame
    ) -> Dict[str, Tuple[pd.DatetimeIndex, pd.DataFrame, pd.DataFrame]]:
        """
        Split origins, X_df, and Y_mat into Train, Validation, and Test sets with embargo filtering.
        """
        if len(origins) != len(X_df) or len(origins) != len(Y_mat):
            raise ModelGovernanceError("Length mismatch between origins, X, and Y.")

        train_embargo_end = cls.TRAIN_END - pd.Timedelta(hours=cls.EMBARGO_HOURS)
        val_embargo_end = cls.VAL_END - pd.Timedelta(hours=cls.EMBARGO_HOURS)

        train_mask = (origins >= cls.TRAIN_START) & (origins <= train_embargo_end)
        val_mask = (origins >= cls.VAL_START) & (origins <= val_embargo_end)
        test_mask = (origins >= cls.TEST_START) & (origins <= cls.TEST_END)

        splits = {
            "train": (origins[train_mask], X_df.iloc[train_mask].reset_index(drop=True), Y_mat.iloc[train_mask].reset_index(drop=True)),
            "validation": (origins[val_mask], X_df.iloc[val_mask].reset_index(drop=True), Y_mat.iloc[val_mask].reset_index(drop=True)),
            "test": (origins[test_mask], X_df.iloc[test_mask].reset_index(drop=True), Y_mat.iloc[test_mask].reset_index(drop=True))
        }

        return splits
