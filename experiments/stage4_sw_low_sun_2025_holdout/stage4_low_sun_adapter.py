"""
POLARIS Research-Only Stage 4 Adapter: Low-Sun Stored-Energy Protection
Module: experiments.stage4_sw_low_sun_2025_holdout.stage4_low_sun_adapter

Governing Contracts:
  - experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md
  - experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.json
  - experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.md
  - experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.json

RESEARCH USE ONLY / CONFIRMATORY 2025 HOLDOUT EVALUATION:
Implements Candidate S-L (Solar-Only Net EBR with Low-Sun Stored-Energy Protection)
and Candidate SW-L (Solar + Synthetic Wind Net EBR with Low-Sun Stored-Energy Protection).

MATHEMATICAL SPECIFICATIONS (Section 5 of frozen preregistration):
  - Horizon window: k in {t .. min(t+5, 23)} for t in {0 .. 23}.
  - Efficiency eta = 0.92, dt = 1.0 h.
  - Critical demand c_k = min(11,600 W, D_forecast[k]).
  - Forecast solar s_k = bundle.solar_generation.point[k] (W).
  - Forecast wind w_k = bundle.wind_generation.point[k] (W).
  - Solar elevation e_k at horizon step k (degrees above horizon).
  - Low-sun indicator: L_k = 1[e_k < 15.0 deg] (strict inequality).

Formulas:
  1. Control B (governed unconditional):
     E_B[t] = (1 / eta) * sum_{k=t}^{min(t+5, 23)} c_k * dt

  2. Candidate S (solar-only net EBR, protection OFF):
     E_S[t] = (1 / eta) * sum_{k=t}^{min(t+5, 23)} max(0, c_k - s_k) * dt

  3. Candidate SW (solar + wind net EBR, protection OFF):
     E_SW[t] = (1 / eta) * sum_{k=t}^{min(t+5, 23)} max(0, c_k - s_k - w_k) * dt

  4. Candidate S-L (solar-only net EBR, protection ON):
     E_SL[t] = (1 / eta) * sum_{k=t}^{min(t+5, 23)} max(0, c_k - (1 - L_k) * s_k) * dt

  5. Candidate SW-L (solar + wind net EBR, protection ON, final candidate):
     E_SWL[t] = (1 / eta) * sum_{k=t}^{min(t+5, 23)} max(0, c_k - (1 - L_k) * (s_k + w_k)) * dt

  Horizon edge (all arms):
     E_stage2[23] = max(E_arm[23], E_term) with E_term = 100,000 Wh.

REQUIRED INVARIANCES & STRUCTURAL PROPERTIES:
  - If L_k = 1 for all k => E_SL = E_SWL = E_B
  - If L_k = 0 for all k => E_SL = E_S and E_SWL = E_SW
  - Pointwise ordering: E_SW <= E_SWL <= E_B and E_S <= E_SL <= E_B
  - Strict inequality: e_k < 15.0 => L_k = 1, e_k >= 15.0 => L_k = 0.
"""

import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd
import pvlib

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.dispatch_plan import DispatchPlan
from system.research.research_critical_demand_adapter import adapt_critical_demand_vector

# Governed POLARIS System Constants
ETA_DIS: float = 0.92
DT: float = 1.0
TERMINAL_TARGET_WH: float = 100000.0
CRITICAL_CEILING_W: float = 11600.0
LOW_SUN_THRESHOLD_DEG: float = 15.0

NUOLJA_LATITUDE: float = 68.362074
NUOLJA_LONGITUDE: float = 18.738752
NUOLJA_TIMEZONE: str = "Etc/GMT-1"


class SolarElevationProvider:
    """
    Provides deterministic solar elevation for 2025 timestamps.
    Matches forecasting/clear_sky/compute_clearsky_2025.py exactly:
    Location(lat=68.362074, lon=18.738752, tz='Etc/GMT-1').
    """
    def __init__(self, decomposition_csv: Optional[Union[str, Path]] = None):
        self._cache: Dict[str, float] = {}
        if decomposition_csv is not None and Path(decomposition_csv).exists():
            df = pd.read_csv(decomposition_csv)
            if "TIMESTAMP" in df.columns and "solar_elevation" in df.columns:
                for ts, el in zip(df["TIMESTAMP"], df["solar_elevation"]):
                    # Store both normalized forms
                    ts_clean = str(ts).strip()
                    self._cache[ts_clean] = float(el)
                    self._cache[ts_clean.replace(" ", "T") + "Z"] = float(el)
                    self._cache[ts_clean.replace(" ", "T")] = float(el)

        self._location = pvlib.location.Location(
            latitude=NUOLJA_LATITUDE,
            longitude=NUOLJA_LONGITUDE,
            tz=NUOLJA_TIMEZONE,
            name="SITES Nuolja Middle Station"
        )

    def get_solar_elevation(self, timestamp_str: str) -> float:
        """
        Returns solar elevation in degrees for the given timestamp.
        Uses cached decomposition value if available, else computes via pvlib.
        """
        ts_clean = timestamp_str.strip()
        if ts_clean in self._cache:
            return self._cache[ts_clean]

        norm_ts = ts_clean.replace("T", " ").replace("Z", "")
        if norm_ts in self._cache:
            return self._cache[norm_ts]

        # Compute with pvlib using frozen convention (Etc/GMT-1)
        times = pd.DatetimeIndex([norm_ts]).tz_localize(NUOLJA_TIMEZONE)
        solpos = self._location.get_solarposition(times)
        elevation = float(solpos["elevation"].iloc[0])
        self._cache[ts_clean] = elevation
        self._cache[norm_ts] = elevation
        return elevation

    def get_elevation_vector(self, timestamps: List[str]) -> List[float]:
        """Returns solar elevations for a list of timestamps."""
        return [self.get_solar_elevation(ts) for ts in timestamps]


def compute_governed_ebr(
    critical_demand_w: List[float],
    eta_dis: float = ETA_DIS,
    dt: float = DT
) -> List[float]:
    """
    Computes governed 6-hour lookahead unconditional EBR trajectory:
        E_B[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} critical_demand[k] * dt
    """
    if len(critical_demand_w) != 24:
        raise ValueError(f"critical_demand_w must have length 24, got {len(critical_demand_w)}")
    if eta_dis <= 0.0:
        raise ValueError(f"eta_dis must be positive, got {eta_dis}")
    if dt <= 0.0:
        raise ValueError(f"dt must be positive, got {dt}")

    ebr = []
    for t in range(24):
        end_k = min(t + 6, 24)
        w_sum = sum(critical_demand_w[k] * dt for k in range(t, end_k))
        ebr.append(w_sum / eta_dis)

    assert len(ebr) == 24
    assert all(math.isfinite(v) and v >= 0.0 for v in ebr)
    return ebr


def compute_variant_s_ebr(
    critical_demand_w: List[float],
    solar_w: List[float],
    eta_dis: float = ETA_DIS,
    dt: float = DT
) -> List[float]:
    """
    Computes Candidate S (Solar-Only Net EBR, protection OFF):
        E_S[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} max(0, critical_demand[k] - solar_w[k]) * dt
    """
    if len(critical_demand_w) != 24:
        raise ValueError(f"critical_demand_w must have length 24, got {len(critical_demand_w)}")
    if len(solar_w) != 24:
        raise ValueError(f"solar_w must have length 24, got {len(solar_w)}")
    if eta_dis <= 0.0:
        raise ValueError(f"eta_dis must be positive, got {eta_dis}")
    if dt <= 0.0:
        raise ValueError(f"dt must be positive, got {dt}")

    for k in range(24):
        if not math.isfinite(critical_demand_w[k]) or critical_demand_w[k] < 0.0:
            raise ValueError(f"critical_demand_w[{k}] invalid: {critical_demand_w[k]}")
        if not math.isfinite(solar_w[k]) or solar_w[k] < 0.0:
            raise ValueError(f"solar_w[{k}] invalid: {solar_w[k]}")

    ebr = []
    for t in range(24):
        end_k = min(t + 6, 24)
        s = 0.0
        for k in range(t, end_k):
            net_deficit = max(0.0, critical_demand_w[k] - solar_w[k])
            s += net_deficit * dt
        ebr.append(s / eta_dis)

    assert len(ebr) == 24
    assert all(math.isfinite(v) and v >= 0.0 for v in ebr)
    return ebr


def compute_variant_sw_ebr(
    critical_demand_w: List[float],
    solar_w: List[float],
    wind_w: List[float],
    eta_dis: float = ETA_DIS,
    dt: float = DT
) -> List[float]:
    """
    Computes Candidate SW (Solar + Synthetic Wind Net EBR, protection OFF):
        E_SW[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} max(0, critical_demand[k] - solar_w[k] - wind_w[k]) * dt
    """
    if len(critical_demand_w) != 24:
        raise ValueError(f"critical_demand_w must have length 24, got {len(critical_demand_w)}")
    if len(solar_w) != 24:
        raise ValueError(f"solar_w must have length 24, got {len(solar_w)}")
    if len(wind_w) != 24:
        raise ValueError(f"wind_w must have length 24, got {len(wind_w)}")
    if eta_dis <= 0.0:
        raise ValueError(f"eta_dis must be positive, got {eta_dis}")
    if dt <= 0.0:
        raise ValueError(f"dt must be positive, got {dt}")

    for k in range(24):
        if not math.isfinite(critical_demand_w[k]) or critical_demand_w[k] < 0.0:
            raise ValueError(f"critical_demand_w[{k}] invalid: {critical_demand_w[k]}")
        if not math.isfinite(solar_w[k]) or solar_w[k] < 0.0:
            raise ValueError(f"solar_w[{k}] invalid: {solar_w[k]}")
        if not math.isfinite(wind_w[k]) or wind_w[k] < 0.0:
            raise ValueError(f"wind_w[{k}] invalid: {wind_w[k]}")

    ebr = []
    for t in range(24):
        end_k = min(t + 6, 24)
        s = 0.0
        for k in range(t, end_k):
            net_deficit = max(0.0, critical_demand_w[k] - solar_w[k] - wind_w[k])
            s += net_deficit * dt
        ebr.append(s / eta_dis)

    assert len(ebr) == 24
    assert all(math.isfinite(v) and v >= 0.0 for v in ebr)
    return ebr


def compute_variant_sl_ebr(
    critical_demand_w: List[float],
    solar_w: List[float],
    solar_elevations_deg: List[float],
    threshold_deg: float = LOW_SUN_THRESHOLD_DEG,
    eta_dis: float = ETA_DIS,
    dt: float = DT,
    protection_enabled: bool = True
) -> List[float]:
    """
    Computes Candidate S-L (Solar-Only Net EBR with Low-Sun Stored-Energy Protection):
        E_SL[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} max(0, critical_demand[k] - (1 - L_k) * solar_w[k]) * dt
    where:
        L_k = 1 if (e_k < threshold_deg and protection_enabled) else 0.
    """
    if len(critical_demand_w) != 24:
        raise ValueError(f"critical_demand_w must have length 24, got {len(critical_demand_w)}")
    if len(solar_w) != 24:
        raise ValueError(f"solar_w must have length 24, got {len(solar_w)}")
    if len(solar_elevations_deg) != 24:
        raise ValueError(f"solar_elevations_deg must have length 24, got {len(solar_elevations_deg)}")
    if eta_dis <= 0.0:
        raise ValueError(f"eta_dis must be positive, got {eta_dis}")
    if dt <= 0.0:
        raise ValueError(f"dt must be positive, got {dt}")

    for k in range(24):
        if not math.isfinite(critical_demand_w[k]) or critical_demand_w[k] < 0.0:
            raise ValueError(f"critical_demand_w[{k}] invalid: {critical_demand_w[k]}")
        if not math.isfinite(solar_w[k]) or solar_w[k] < 0.0:
            raise ValueError(f"solar_w[{k}] invalid: {solar_w[k]}")
        if not math.isfinite(solar_elevations_deg[k]):
            raise ValueError(f"solar_elevations_deg[{k}] invalid: {solar_elevations_deg[k]}")

    # Strict inequality per Section 7: L_k = 1 iff e_k < 15.0 deg
    L = [
        1 if (protection_enabled and solar_elevations_deg[k] < threshold_deg) else 0
        for k in range(24)
    ]

    ebr = []
    for t in range(24):
        end_k = min(t + 6, 24)
        s = 0.0
        for k in range(t, end_k):
            effective_solar = (1 - L[k]) * solar_w[k]
            net_deficit = max(0.0, critical_demand_w[k] - effective_solar)
            s += net_deficit * dt
        ebr.append(s / eta_dis)

    assert len(ebr) == 24
    assert all(math.isfinite(v) and v >= 0.0 for v in ebr)
    return ebr


def compute_variant_swl_ebr(
    critical_demand_w: List[float],
    solar_w: List[float],
    wind_w: List[float],
    solar_elevations_deg: List[float],
    threshold_deg: float = LOW_SUN_THRESHOLD_DEG,
    eta_dis: float = ETA_DIS,
    dt: float = DT,
    protection_enabled: bool = True
) -> List[float]:
    """
    Computes Candidate SW-L (Solar + Synthetic Wind Net EBR with Low-Sun Stored-Energy Protection):
        E_SWL[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} max(0, critical_demand[k] - (1 - L_k) * (solar_w[k] + wind_w[k])) * dt
    where:
        L_k = 1 if (e_k < threshold_deg and protection_enabled) else 0.
    """
    if len(critical_demand_w) != 24:
        raise ValueError(f"critical_demand_w must have length 24, got {len(critical_demand_w)}")
    if len(solar_w) != 24:
        raise ValueError(f"solar_w must have length 24, got {len(solar_w)}")
    if len(wind_w) != 24:
        raise ValueError(f"wind_w must have length 24, got {len(wind_w)}")
    if len(solar_elevations_deg) != 24:
        raise ValueError(f"solar_elevations_deg must have length 24, got {len(solar_elevations_deg)}")
    if eta_dis <= 0.0:
        raise ValueError(f"eta_dis must be positive, got {eta_dis}")
    if dt <= 0.0:
        raise ValueError(f"dt must be positive, got {dt}")

    for k in range(24):
        if not math.isfinite(critical_demand_w[k]) or critical_demand_w[k] < 0.0:
            raise ValueError(f"critical_demand_w[{k}] invalid: {critical_demand_w[k]}")
        if not math.isfinite(solar_w[k]) or solar_w[k] < 0.0:
            raise ValueError(f"solar_w[{k}] invalid: {solar_w[k]}")
        if not math.isfinite(wind_w[k]) or wind_w[k] < 0.0:
            raise ValueError(f"wind_w[{k}] invalid: {wind_w[k]}")
        if not math.isfinite(solar_elevations_deg[k]):
            raise ValueError(f"solar_elevations_deg[{k}] invalid: {solar_elevations_deg[k]}")

    # Strict inequality per Section 7: L_k = 1 iff e_k < 15.0 deg
    L = [
        1 if (protection_enabled and solar_elevations_deg[k] < threshold_deg) else 0
        for k in range(24)
    ]

    ebr = []
    for t in range(24):
        end_k = min(t + 6, 24)
        s = 0.0
        for k in range(t, end_k):
            effective_renewable = (1 - L[k]) * (solar_w[k] + wind_w[k])
            net_deficit = max(0.0, critical_demand_w[k] - effective_renewable)
            s += net_deficit * dt
        ebr.append(s / eta_dis)

    assert len(ebr) == 24
    assert all(math.isfinite(v) and v >= 0.0 for v in ebr)
    return ebr


def compute_stage2_target_vector(
    ebr_trajectory: List[float],
    terminal_target_wh: float = TERMINAL_TARGET_WH
) -> List[float]:
    """
    Constructs the exact stage2 target vector as performed by GAP19 lines 147-151:
        e_stage2_target[t] = ebr_target_wh_list[t] for t in {0 .. 22}
        e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)
    """
    if len(ebr_trajectory) != 24:
        raise ValueError(f"ebr_trajectory must have length 24, got {len(ebr_trajectory)}")

    stage2 = [0.0] * 24
    for t in range(23):
        stage2[t] = float(ebr_trajectory[t])
    stage2[23] = max(float(ebr_trajectory[23]), float(terminal_target_wh))
    return stage2


class Stage4EBROptimizerWrapper:
    """
    Non-invasive optimizer wrapper supporting all 5 arms for Stage 4:
    - FROZEN_B: Governed unconditional EBR
    - S: Candidate S (Solar-only net EBR, protection OFF)
    - SW: Candidate SW (Solar + wind net EBR, protection OFF)
    - SL (or S-L): Candidate S-L (Solar-only net EBR, low-sun protection ON)
    - SWL (or SW-L): Candidate SW-L (Solar + wind net EBR, low-sun protection ON)

    Passes the candidate-specific ebr_target_wh vector through config without modifying GAP19.
    """
    def __init__(
        self,
        inner_optimizer: Any,
        variant: str,
        elevation_provider: Optional[SolarElevationProvider] = None,
        threshold_deg: float = LOW_SUN_THRESHOLD_DEG
    ):
        norm_variant = variant.upper().replace("-", "")
        valid_variants = ("FROZENB", "S", "SW", "SL", "SWL")
        if norm_variant not in valid_variants:
            raise ValueError(f"Unknown variant '{variant}', expected one of {valid_variants}")

        self.inner_optimizer = inner_optimizer
        self.variant = norm_variant
        self.raw_variant_name = variant
        self.elevation_provider = elevation_provider or SolarElevationProvider()
        self.threshold_deg = threshold_deg
        self.call_history: List[Dict[str, Any]] = []

    def optimize(
        self,
        bundle: ForecastBundle,
        station_state: StationState,
        config: Dict[str, Any]
    ) -> DispatchPlan:
        step_config = dict(config)

        # Critical demand vector
        crit_w = step_config.get("critical_demand_w")
        if crit_w is None:
            crit_ceiling = float(
                step_config.get("loads", {}).get("critical_load", {}).get(
                    "baseline_power_w",
                    step_config.get("critical_demand_baseline_w", CRITICAL_CEILING_W)
                )
            )
            crit_w = adapt_critical_demand_vector(crit_ceiling, bundle.demand.point)
            step_config["critical_demand_w"] = crit_w

        solar_w = list(bundle.solar_generation.point)
        wind_w = list(bundle.wind_generation.point)

        # Get solar elevations for the 24 horizon timestamps
        elevations = self.elevation_provider.get_elevation_vector(bundle.timestamps)

        ebr_used: Optional[List[float]] = None
        if self.variant == "FROZENB":
            ebr_used = compute_governed_ebr(crit_w)
            step_config.pop("ebr_target_wh", None)
        elif self.variant == "S":
            ebr_used = compute_variant_s_ebr(crit_w, solar_w)
            step_config["ebr_target_wh"] = ebr_used
        elif self.variant == "SW":
            ebr_used = compute_variant_sw_ebr(crit_w, solar_w, wind_w)
            step_config["ebr_target_wh"] = ebr_used
        elif self.variant == "SL":
            ebr_used = compute_variant_sl_ebr(
                crit_w, solar_w, elevations, threshold_deg=self.threshold_deg, protection_enabled=True
            )
            step_config["ebr_target_wh"] = ebr_used
        elif self.variant == "SWL":
            ebr_used = compute_variant_swl_ebr(
                crit_w, solar_w, wind_w, elevations, threshold_deg=self.threshold_deg, protection_enabled=True
            )
            step_config["ebr_target_wh"] = ebr_used

        plan = self.inner_optimizer.optimize(bundle, station_state, step_config)

        self.call_history.append({
            "variant": self.variant,
            "forecast_solar_w": solar_w,
            "forecast_wind_w": wind_w,
            "critical_demand_w": crit_w,
            "solar_elevations_deg": elevations,
            "ebr_trajectory_wh": ebr_used,
            "j2_shortfall_wh": plan.j2_objective if plan.j2_objective is not None else 0.0,
            "constraint_status": plan.constraint_status
        })

        return plan

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner_optimizer, name)
