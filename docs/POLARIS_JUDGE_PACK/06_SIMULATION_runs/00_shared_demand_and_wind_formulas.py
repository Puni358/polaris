"""
Single source of truth for the synthetic station inputs that EVERY scenario (reactive baseline,
Scenarios 2/3/4 and the terminal-rule variants) must see identically:

  demand : governed industrial profile (diurnal x seasonal, clipped 15-45 kW)
  wind   : 15 kW + 10 kW * sin(hour_of_day * pi / 6), a function of the CLOCK
           (same formula as run_n6_rhc_annual_*.py: ((idx + h) % 24) * pi / 6)
  solar  : real measured GHI x K_PV (51 W per W/m^2), supplied by each runner from the dataset

Wind and demand are looked up by the timestamp they apply to, so the physics step and every step
of a 24 h plan see the value for that real hour. (An earlier version of the scenario script indexed
wind by "hours since forecast origin", which made the simulated wind a constant 15 kW.)
"""
import math
import pandas as pd


def _diurnal_w(hour: int) -> float:
    if 0 <= hour <= 5:
        return 18000.0
    if hour == 6:
        return 22000.0
    if hour == 7:
        return 30000.0
    if hour == 8:
        return 38000.0
    if 9 <= hour <= 17:
        return 32000.0
    if hour == 18:
        return 36000.0
    if hour == 19:
        return 42000.0
    if 20 <= hour <= 21:
        return 30000.0
    return 22000.0


def _seasonal(month: int) -> float:
    if month in (11, 12, 1, 2):
        return 1.20
    if month in (5, 6, 7, 8):
        return 0.85
    return 1.00


def demand_at(dt: pd.Timestamp) -> float:
    return float(min(max(_diurnal_w(dt.hour) * _seasonal(dt.month), 15000.0), 45000.0))


def wind_at(dt: pd.Timestamp) -> float:
    return 15_000.0 + 10_000.0 * math.sin(dt.hour * math.pi / 6.0)
