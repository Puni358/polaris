"""
NWP Selector Module
Strictly causal NWP issue selector enforcing t_issue <= forecast_origin t.
"""

from datetime import datetime, timezone
from typing import List, Optional
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class NWPSelector:
    """Selects latest valid AROME issue run t_issue <= forecast_origin t."""

    @staticmethod
    def select_latest_valid_issue(
        forecast_origin: datetime,
        available_issue_runs: List[datetime]
    ) -> datetime:
        """
        Find latest issue run t_issue such that t_issue <= forecast_origin.
        Fails closed if no valid issue exists or if t_issue > forecast_origin.
        """
        if forecast_origin.tzinfo is None:
            forecast_origin = forecast_origin.replace(tzinfo=timezone.utc)

        valid_runs = []
        for run in available_issue_runs:
            if run.tzinfo is None:
                run = run.replace(tzinfo=timezone.utc)
            if run <= forecast_origin:
                valid_runs.append(run)

        if not valid_runs:
            raise ModelGovernanceError(f"Fail-closed: No valid NWP issue run found at or before origin {forecast_origin}")

        latest_issue = max(valid_runs)
        if latest_issue > forecast_origin:
            raise ModelGovernanceError(f"Fail-closed: NWP issue causality violation: {latest_issue} > {forecast_origin}")

        return latest_issue
