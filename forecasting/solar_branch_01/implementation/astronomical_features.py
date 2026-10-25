"""
Astronomical Features Module
Calculates deterministic astronomical features (solar elevation, zenith, azimuth, cyclics) at origin t.
"""

from datetime import datetime, timezone
import math
import numpy as np
import pandas as pd


class AstronomicalFeatureBuilder:
    """Calculates deterministic astronomical features for Nuolja site (68.3582° N, 18.7842° E)."""

    LATITUDE = 68.3582
    LONGITUDE = 18.7842

    @classmethod
    def compute_features(cls, timestamp: datetime) -> dict:
        """
        Compute deterministic solar elevation, zenith, sin/cos hour of day, and sin/cos day of year.
        """
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        day_of_year = timestamp.timetuple().tm_yday
        hour_of_day = timestamp.hour + timestamp.minute / 60.0

        sin_hour = math.sin(2 * math.pi * hour_of_day / 24.0)
        cos_hour = math.cos(2 * math.pi * hour_of_day / 24.0)
        sin_doy = math.sin(2 * math.pi * day_of_year / 365.25)
        cos_doy = math.cos(2 * math.pi * day_of_year / 365.25)

        # Solar declination approximation
        declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
        dec_rad = math.radians(declination)
        lat_rad = math.radians(cls.LATITUDE)

        # Solar hour angle
        solar_noon_hour = 12.0 - (cls.LONGITUDE / 15.0)
        hour_angle = (hour_of_day - solar_noon_hour) * 15.0
        ha_rad = math.radians(hour_angle)

        sin_elev = math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
        elevation = math.degrees(math.asin(max(-1.0, min(1.0, sin_elev))))
        zenith = max(0.0, 90.0 - elevation)

        return {
            "solar_elevation": elevation,
            "solar_zenith": zenith,
            "sin_hour": sin_hour,
            "cos_hour": cos_hour,
            "sin_doy": sin_doy,
            "cos_doy": cos_doy
        }
