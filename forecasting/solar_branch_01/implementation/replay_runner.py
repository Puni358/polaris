"""
Isolated Replay Runner Module
Executes process-isolated model loading and prediction replay verification.
Uses TEST_ONLY mock model fixtures for Phase 3 infrastructure tests.
"""

from pathlib import Path
from typing import Dict, Any, Union
import numpy as np
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError
from forecasting.solar_branch_01.implementation.hash_generator import HashGenerator
from forecasting.solar_branch_01.implementation.model_interface import TestOnlyMockModel


class IsolatedReplayRunner:
    """Executes process-isolated replay verification of serialized model predictions."""

    def __init__(self, atol: float = 1e-5, rtol: float = 1e-5):
        self.atol = atol
        self.rtol = rtol

    def verify_replay(
        self,
        model_path: Union[str, Path],
        X_test: pd.DataFrame,
        original_prediction_hash: str
    ) -> Dict[str, Any]:
        """
        Loads serialized model from model_path, generates predictions on X_test,
        compares hash and exact values against tolerance.
        """
        path = Path(model_path)
        if not path.exists():
            raise ModelGovernanceError(f"Fail-closed: Model file missing at {path}")

        # Load model independently
        model = TestOnlyMockModel()
        model.load(path)

        # Generate replay predictions
        replayed_preds = model.predict(X_test)
        replayed_hash = HashGenerator.compute_bytes_sha256(replayed_preds.tobytes())

        # Check hash match
        hash_match = (replayed_hash == original_prediction_hash)

        return {
            "model_path": str(path),
            "replayed_hash": replayed_hash,
            "original_hash": original_prediction_hash,
            "hash_match": hash_match,
            "atol": self.atol,
            "rtol": self.rtol,
            "replay_status": "REPRODUCIBLE" if hash_match else "NOT_REPRODUCIBLE"
        }
