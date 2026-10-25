"""
Abstract EnergyOptimizer Interface
Defines stable contract for microgrid dispatch optimization solvers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

class EnergyOptimizer(ABC):
    @abstractmethod
    def optimize(
        self,
        forecast_bundle: ForecastBundle,
        station_state: StationState,
        config: Dict[str, Any]
    ) -> DispatchPlan:
        """
        Generate a 24-hour DispatchPlan given forecasts, station state, and configuration.
        Must enforce physical energy-balance equations at every timestep.
        """
        pass
