"""
NWP Lead Mapper Module
Calculates effective lead time H_effective = h + (t_origin - t_issue) for target horizon h in 1..24.
"""

from datetime import datetime, timezone
from typing import Dict, Tuple
from system.governance.model_reproducibility import ModelGovernanceError


class NWPLeadMapper:
    """Maps forecast target horizon h at origin t to effective AROME lead time."""

    @staticmethod
    def calculate_effective_lead(
        origin_time: datetime,
        issue_time: datetime,
        horizon_step: int
    ) -> int:
        """
        Calculate H_effective = horizon_step + int((origin_time - issue_time) in hours).
        Fails closed if issue_time > origin_time.
        """
        if origin_time.tzinfo is None:
            origin_time = origin_time.replace(tzinfo=timezone.utc)
        if issue_time.tzinfo is None:
            issue_time = issue_time.replace(tzinfo=timezone.utc)

        if issue_time > origin_time:
            raise ModelGovernanceError(
                f"Fail-closed: NWP issue causality violation: issue_time ({issue_time}) > origin_time ({origin_time})"
            )

        shift_hours = int((origin_time - issue_time).total_seconds() // 3600)
        effective_lead = horizon_step + shift_hours

        if effective_lead < 1 or effective_lead > 48:
            raise ModelGovernanceError(
                f"Fail-closed: Effective lead {effective_lead} out of valid AROME bounds [1, 48]"
            )

        return effective_lead
