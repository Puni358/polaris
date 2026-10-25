"""
Abstract ForecastEngine Interface
Defines stable contract for all local forecasting engine implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState

class ForecastEngine(ABC):
    @abstractmethod
    def predict(self, station_state: StationState, runtime_context: Dict[str, Any]) -> ForecastBundle:
        """
        Generate a 24-hour ForecastBundle given current station state and observable history up to t0.
        MUST NOT access future actual observations.
        """
        pass

    def assert_governance_reproducible(self, run_dir: Any) -> bool:
        """
        Verifies that a model run directory contains MODEL_TRAINING_STATUS == REPRODUCIBLE.
        EMS integration is BLOCKED if governance validation fails.
        """
        from system.governance import assert_governance_reproducible
        return assert_governance_reproducible(run_dir)

