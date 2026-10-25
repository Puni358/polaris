"""
StationState Schema Definition
Encapsulates runtime state of microgrid components at a specific forecast origin t0.
"""
import json
from typing import Dict, Any, Optional

class StationState:
    def __init__(
        self,
        timestamp: str,
        battery_soc_pct: float,
        battery_energy_wh: float,
        diesel_running: bool,
        diesel_hours_running: float,
        last_observed_solar_irradiance: float,
        last_observed_demand: float,
        last_observed_wind_generation: float,
        operating_mode: str = "NORMAL",
        ebr_target_wh_override: Optional[float] = None,
        terminal_target_wh_override: Optional[float] = None,
        diesel_fuel_remaining_liters: Optional[float] = None
    ):
        self.timestamp = str(timestamp)
        self.battery_soc_pct = float(battery_soc_pct)
        self.battery_energy_wh = float(battery_energy_wh)
        self.diesel_running = bool(diesel_running)
        self.diesel_hours_running = float(diesel_hours_running)
        self.last_observed_solar_irradiance = float(last_observed_solar_irradiance)
        self.last_observed_demand = float(last_observed_demand)
        self.last_observed_wind_generation = float(last_observed_wind_generation)
        self.operating_mode = str(operating_mode).upper()
        self.ebr_target_wh_override = float(ebr_target_wh_override) if ebr_target_wh_override is not None else None
        self.terminal_target_wh_override = float(terminal_target_wh_override) if terminal_target_wh_override is not None else None
        self.diesel_fuel_remaining_liters = float(diesel_fuel_remaining_liters) if diesel_fuel_remaining_liters is not None else None

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "timestamp": self.timestamp,
            "battery_soc_pct": self.battery_soc_pct,
            "battery_energy_wh": self.battery_energy_wh,
            "diesel_running": self.diesel_running,
            "diesel_hours_running": self.diesel_hours_running,
            "last_observed_solar_irradiance": self.last_observed_solar_irradiance,
            "last_observed_demand": self.last_observed_demand,
            "last_observed_wind_generation": self.last_observed_wind_generation,
            "operating_mode": self.operating_mode
        }
        if self.ebr_target_wh_override is not None:
            res["ebr_target_wh_override"] = self.ebr_target_wh_override
        if self.terminal_target_wh_override is not None:
            res["terminal_target_wh_override"] = self.terminal_target_wh_override
        if self.diesel_fuel_remaining_liters is not None:
            res["diesel_fuel_remaining_liters"] = self.diesel_fuel_remaining_liters
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StationState':
        return cls(
            timestamp=data["timestamp"],
            battery_soc_pct=data["battery_soc_pct"],
            battery_energy_wh=data["battery_energy_wh"],
            diesel_running=data["diesel_running"],
            diesel_hours_running=data["diesel_hours_running"],
            last_observed_solar_irradiance=data["last_observed_solar_irradiance"],
            last_observed_demand=data["last_observed_demand"],
            last_observed_wind_generation=data["last_observed_wind_generation"],
            operating_mode=data.get("operating_mode", "NORMAL"),
            ebr_target_wh_override=data.get("ebr_target_wh_override"),
            terminal_target_wh_override=data.get("terminal_target_wh_override"),
            diesel_fuel_remaining_liters=data.get("diesel_fuel_remaining_liters")
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


