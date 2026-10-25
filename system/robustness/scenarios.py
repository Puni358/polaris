"""
D5 Scenarios Registry (D5 Implementation)
Defines frozen scenario specifications and gate fixtures (S1-S6, D5-1 through D5-6) in strict compliance with the frozen D5 contract.

Enforces gate-fixture immutability:
- Perturbation factors, scenario composition, horizon, iteration count, persistence, and causality rules are immutable.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class D5ScenarioConfig:
    scenario_id: str
    gate_id: str
    name: str
    affected_variables: List[str]
    solar_scale: float
    wind_scale: float
    demand_scale: float
    irradiance_scale: float
    horizon_hours: int
    duration_iterations: int
    scenario_filename: str
    purpose: str
    provenance: str = "PROPOSED — NOT YET EXECUTED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class D5ScenarioRegistry:
    """
    Registry of frozen D5 scenario specifications.
    Provides immutable access to scenario definitions.
    """

    _SCENARIOS: Dict[str, D5ScenarioConfig] = {
        "D5-1": D5ScenarioConfig(
            scenario_id="S1",
            gate_id="D5-1",
            name="Solar Underprediction Sensitivity",
            affected_variables=["P_solar", "SW_IN"],
            solar_scale=0.70,
            wind_scale=1.00,
            demand_scale=1.00,
            irradiance_scale=0.70,
            horizon_hours=24,
            duration_iterations=24,
            scenario_filename="demo_scenario.json",
            purpose="Tests EMS response when available solar generation is systematically underrepresented in the forecast."
        ),
        "D5-2": D5ScenarioConfig(
            scenario_id="S2",
            gate_id="D5-2",
            name="Solar Overprediction Sensitivity",
            affected_variables=["P_solar", "SW_IN"],
            solar_scale=1.30,
            wind_scale=1.00,
            demand_scale=1.00,
            irradiance_scale=1.30,
            horizon_hours=24,
            duration_iterations=24,
            scenario_filename="demo_scenario.json",
            purpose="Tests EMS response when available solar generation is systematically overrepresented in the forecast."
        ),
        "D5-3": D5ScenarioConfig(
            scenario_id="S3",
            gate_id="D5-3",
            name="Wind Underprediction Sensitivity",
            affected_variables=["P_wind"],
            solar_scale=1.00,
            wind_scale=0.70,
            demand_scale=1.00,
            irradiance_scale=1.00,
            horizon_hours=24,
            duration_iterations=24,
            scenario_filename="demo_scenario.json",
            purpose="Tests EMS response when available wind generation is systematically underrepresented in the forecast."
        ),
        "D5-4": D5ScenarioConfig(
            scenario_id="S4",
            gate_id="D5-4",
            name="Demand Overprediction Impact",
            affected_variables=["P_demand"],
            solar_scale=1.00,
            wind_scale=1.00,
            demand_scale=1.20,
            irradiance_scale=1.00,
            horizon_hours=24,
            duration_iterations=24,
            scenario_filename="demo_scenario.json",
            purpose="Tests EMS response when station demand is systematically overrepresented in the forecast."
        ),
        "D5-5": D5ScenarioConfig(
            scenario_id="S5",
            gate_id="D5-5",
            name="Compound Over-Optimistic Forecast Stress",
            affected_variables=["P_solar", "P_wind", "P_demand"],
            solar_scale=1.30,
            wind_scale=1.30,
            demand_scale=0.80,
            irradiance_scale=1.30,
            horizon_hours=24,
            duration_iterations=24,
            scenario_filename="demo_scenario.json",
            purpose="Tests a deliberately specified compound stress condition in which renewable generation is overpredicted and demand is underpredicted."
        ),
        "D5-6": D5ScenarioConfig(
            scenario_id="S6",
            gate_id="D5-6",
            name="168-Hour Persistent Error",
            affected_variables=["P_solar", "P_wind"],
            solar_scale=1.15,
            wind_scale=1.15,
            demand_scale=1.00,
            irradiance_scale=1.15,
            horizon_hours=24,
            duration_iterations=168,
            scenario_filename="synthetic_168h_endurance_scenario.json",
            purpose="Characterizes cumulative operational and state effects across 168 closed-loop iterations under persistent +15% renewable overprediction."
        )
    }

    @classmethod
    def get_scenario(cls, gate_or_scenario_id: str) -> D5ScenarioConfig:
        key = gate_or_scenario_id.upper()
        if key in cls._SCENARIOS:
            return cls._SCENARIOS[key]
        
        # Map S1..S6 to D5-1..D5-6
        s_to_gate = {"S1": "D5-1", "S2": "D5-2", "S3": "D5-3", "S4": "D5-4", "S5": "D5-5", "S6": "D5-6"}
        if key in s_to_gate:
            return cls._SCENARIOS[s_to_gate[key]]

        raise KeyError(f"Unknown D5 scenario/gate ID '{gate_or_scenario_id}'. Valid keys: D5-1..D5-6, S1..S6.")

    @classmethod
    def list_scenarios(cls) -> List[D5ScenarioConfig]:
        return list(cls._SCENARIOS.values())
