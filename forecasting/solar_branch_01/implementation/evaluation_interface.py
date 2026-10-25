"""
Evaluation Interface Module
Calculates horizon-wise error metrics (MAE, RMSE) explicitly authorized by the Phase 2 specification contract.
"""

from typing import Dict
import numpy as np
from system.governance.model_reproducibility import ModelGovernanceError


class EvaluationInterface:
    """Calculates authorized evaluation metrics (MAE, RMSE) per target horizon h=1..24 and aggregate."""

    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate MAE and RMSE across 24h targets.
        Fails closed on shape mismatch or NaNs.
        """
        if y_true.shape != y_pred.shape:
            raise ModelGovernanceError(f"Fail-closed: Shape mismatch y_true {y_true.shape} vs y_pred {y_pred.shape}")

        if np.isnan(y_true).any() or np.isnan(y_pred).any():
            raise ModelGovernanceError("Fail-closed: NaN detected in ground-truth or predictions.")

        mae = float(np.mean(np.abs(y_true - y_pred)))
        rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

        metrics = {
            "overall_mae": mae,
            "overall_rmse": rmse
        }

        # Horizon-wise MAE
        if y_true.ndim == 2 and y_true.shape[1] == 24:
            for h in range(24):
                h_mae = float(np.mean(np.abs(y_true[:, h] - y_pred[:, h])))
                h_rmse = float(np.sqrt(np.mean((y_true[:, h] - y_pred[:, h]) ** 2)))
                metrics[f"h{h+1}_mae"] = h_mae
                metrics[f"h{h+1}_rmse"] = h_rmse

        return metrics
