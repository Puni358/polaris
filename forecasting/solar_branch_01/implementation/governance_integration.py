"""
Governance Integration Module
Integrates Branch 01 pipeline components with system.governance.model_reproducibility state machine.
"""

from typing import Dict, Any
from system.governance.model_reproducibility import PolarisModelGovernanceManager, ModelGovernanceError


class GovernanceIntegration:
    """Wraps core governance enforcement and state transitions."""

    def __init__(self, branch_id: str = "POLARIS_SOLAR_FORECAST_BRANCH_01"):
        self.branch_id = branch_id
        self.framework = PolarisModelGovernanceManager(
            branch_id=branch_id,
            model_id=branch_id,
            model_type="SOLAR_FORECAST"
        )

    def create_governed_run(self, run_id: str) -> Dict[str, Any]:
        """Initialize new governed run context."""
        return {
            "run_id": run_id,
            "branch_id": self.branch_id,
            "status": "IN_PROGRESS",
            "framework": self.framework
        }

    def transition_state(self, current_state: str, target_state: str, is_success: bool) -> str:
        """Enforce state machine transitions."""
        valid_states = ["IN_PROGRESS", "TRAINING_COMPLETE", "SERIALIZATION_VERIFIED", "REPLAY_VERIFIED", "REPRODUCIBLE", "NOT_REPRODUCIBLE"]

        if target_state not in valid_states:
            raise ModelGovernanceError(f"Invalid target state: {target_state}")

        if not is_success:
            return "NOT_REPRODUCIBLE"

        return target_state
