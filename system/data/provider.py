"""
Local Data & Weather Providers
Provides offline data access strictly from local disk storage without network dependencies.
"""
import json
from pathlib import Path
from typing import Dict, Any, List

class LocalDataProvider:
    def __init__(self, scenario_path: Path):
        if not scenario_path.exists():
            raise FileNotFoundError(f"Local scenario file not found at {scenario_path}")
        with open(scenario_path, "r") as f:
            self.scenario_data = json.load(f)
        self.timesteps = self.scenario_data["timesteps"]
        self.total_timesteps = len(self.timesteps)

    def get_runtime_state(self, current_index: int) -> Dict[str, Any]:
        """
        Returns observable historical information up to current_index.
        STRICTLY excludes future actual observations beyond current_index.
        """
        if current_index >= self.total_timesteps:
            raise IndexError("Current index exceeds scenario timesteps.")
        
        history = self.timesteps[:current_index + 1]
        current_step = self.timesteps[current_index]

        return {
            "origin_timestamp": current_step["timestamp"],
            "current_index": current_index,
            "history": history,
            "last_observed_solar_irradiance": current_step["actual_SW_IN"],
            "last_observed_demand": current_step["actual_demand"],
            "last_observed_wind_generation": current_step["actual_wind_generation"],
            "clearsky_ghi": current_step["clearsky_ghi"]
        }

    def get_future_ground_truth(self, current_index: int, horizon_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Returns hidden future actual observations for simulation/evaluation ONLY.
        Must NEVER be exposed to ForecastEngine or EnergyOptimizer during runtime.
        """
        start = current_index + 1
        end = min(start + horizon_hours, self.total_timesteps)
        future_steps = self.timesteps[start:end]

        # If scenario ends before full horizon, pad with persistence
        if len(future_steps) < horizon_hours:
            last_step = future_steps[-1] if len(future_steps) > 0 else self.timesteps[-1]
            pad_count = horizon_hours - len(future_steps)
            for i in range(pad_count):
                future_steps.append({
                    "timestep_index": last_step["timestep_index"] + i + 1,
                    "timestamp": f"padded_{i}",
                    "actual_SW_IN": last_step["actual_SW_IN"],
                    "clearsky_ghi": last_step["clearsky_ghi"],
                    "actual_wind_generation": last_step["actual_wind_generation"],
                    "actual_demand": last_step["actual_demand"]
                })
        return future_steps
