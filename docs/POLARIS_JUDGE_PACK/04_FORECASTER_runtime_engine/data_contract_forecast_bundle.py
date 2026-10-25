"""
ForecastBundle Schema Definition (Version 1.0.0)
Strictly enforces separation between solar irradiance (W/m^2) and electrical generation (W),
finite numerical bounds, timestamp monotonicity, and field-specific physical non-negativity.
"""
import json
import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class TimeseriesForecast:
    def __init__(self, point: List[float], lower: List[float], upper: List[float], unit: str):
        if not (len(point) == len(lower) == len(upper) == 24):
            raise ValueError("All forecast arrays must contain exactly 24 horizon values.")
        
        self.point = []
        self.lower = []
        self.upper = []

        for idx, (p, l, u) in enumerate(zip(point, lower, upper)):
            fp, fl, fu = float(p), float(l), float(u)
            if math.isnan(fp) or math.isinf(fp) or math.isnan(fl) or math.isinf(fl) or math.isnan(fu) or math.isinf(fu):
                raise ValueError(f"Forecast contains non-finite numerical value (NaN/Inf) at index {idx}.")
            if not (fl <= fp <= fu) or not (fl <= fu):
                raise ValueError(f"Forecast interval inconsistency at index {idx}: lower ({fl}) <= point ({fp}) <= upper ({fu}) violated.")
            self.point.append(fp)
            self.lower.append(fl)
            self.upper.append(fu)
            
        self.unit = str(unit)

    def validate_non_negative(self, field_name: str):
        for idx, p in enumerate(self.point):
            if p < 0.0:
                raise ValueError(f"Physically impossible negative forecast quantity for {field_name} at index {idx}: {p}.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "point": self.point,
            "lower": self.lower,
            "upper": self.upper,
            "unit": self.unit
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeseriesForecast':
        return cls(
            point=data["point"],
            lower=data["lower"],
            upper=data["upper"],
            unit=data["unit"]
        )

class ForecastBundle:
    def __init__(
        self,
        schema_version: str,
        origin_timestamp: str,
        horizon_hours: int,
        timestamps: List[str],
        solar_irradiance: TimeseriesForecast,
        solar_generation: TimeseriesForecast,
        wind_generation: TimeseriesForecast,
        demand: TimeseriesForecast,
        metadata: Dict[str, Any],
        demand_critical: Optional[TimeseriesForecast] = None
    ):
        if horizon_hours != 24 or len(timestamps) != 24:
            raise ValueError("ForecastBundle must represent a 24-hour forecast horizon.")
        
        if schema_version != "1.0.0":
            raise ValueError(f"Unsupported schema_version '{schema_version}'; expected '1.0.0'.")

        if solar_irradiance.unit != "W/m^2":
            raise ValueError("Solar irradiance unit must be W/m^2.")
        if solar_generation.unit != "W":
            raise ValueError("Solar generation unit must be W.")
        if wind_generation.unit != "W":
            raise ValueError("Wind generation unit must be W.")
        if demand.unit != "W":
            raise ValueError("Demand unit must be W.")

        # Field-specific non-negativity checks
        solar_irradiance.validate_non_negative("solar_irradiance")
        solar_generation.validate_non_negative("solar_generation")
        wind_generation.validate_non_negative("wind_generation")
        demand.validate_non_negative("demand")

        if demand_critical is not None:
            if demand_critical.unit != "W":
                raise ValueError("Demand critical unit must be W.")
            demand_critical.validate_non_negative("demand_critical")
            for idx, (cp, dp) in enumerate(zip(demand_critical.point, demand.point)):
                if cp > dp + 1e-4:
                    raise ValueError(f"Protected critical load ({cp}W) exceeds total demand ({dp}W) at index {idx}.")

        # Timestamp parseability, origin consistency & 1h monotonicity checks
        try:
            parsed_ts = [datetime.fromisoformat(ts.replace("Z", "+00:00")) for ts in timestamps]
            parsed_origin = datetime.fromisoformat(origin_timestamp.replace("Z", "+00:00"))
        except Exception as e:
            raise ValueError(f"Unparseable ISO-8601 timestamp in ForecastBundle: {e}")

        first_diff_sec = (parsed_ts[0] - parsed_origin).total_seconds()
        if first_diff_sec not in (0.0, 3600.0):
            raise ValueError(f"Origin timestamp '{origin_timestamp}' is inconsistent with first forecast timestamp '{timestamps[0]}' (diff: {first_diff_sec}s).")

        for idx in range(len(parsed_ts) - 1):
            dt_diff = (parsed_ts[idx+1] - parsed_ts[idx]).total_seconds()
            if abs(dt_diff - 3600.0) > 1.0:
                raise ValueError(f"Non-monotonic or non-1-hour timestamp step between index {idx} and {idx+1}.")

        self.schema_version = schema_version
        self.origin_timestamp = origin_timestamp
        self.horizon_hours = horizon_hours
        self.timestamps = timestamps
        self.solar_irradiance = solar_irradiance
        self.solar_generation = solar_generation
        self.wind_generation = wind_generation
        self.demand = demand
        self.demand_critical = demand_critical
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "schema_version": self.schema_version,
            "origin_timestamp": self.origin_timestamp,
            "horizon_hours": self.horizon_hours,
            "timestamps": self.timestamps,
            "solar_irradiance": self.solar_irradiance.to_dict(),
            "solar_generation": self.solar_generation.to_dict(),
            "wind_generation": self.wind_generation.to_dict(),
            "demand": self.demand.to_dict(),
            "metadata": self.metadata
        }
        if self.demand_critical is not None:
            res["demand_critical"] = self.demand_critical.to_dict()
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ForecastBundle':
        dc = TimeseriesForecast.from_dict(data["demand_critical"]) if data.get("demand_critical") is not None else None
        return cls(
            schema_version=data["schema_version"],
            origin_timestamp=data["origin_timestamp"],
            horizon_hours=data["horizon_hours"],
            timestamps=data["timestamps"],
            solar_irradiance=TimeseriesForecast.from_dict(data["solar_irradiance"]),
            solar_generation=TimeseriesForecast.from_dict(data["solar_generation"]),
            wind_generation=TimeseriesForecast.from_dict(data["wind_generation"]),
            demand=TimeseriesForecast.from_dict(data["demand"]),
            metadata=data["metadata"],
            demand_critical=dc
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

