"""
POLARIS Energy Management System (EMS)
Emergency Condition Detector (ECD) Core Implementation

Architectural Responsibility:
- Evaluate microgrid resource survivability (battery & diesel) against target horizon T_target.
- Classify system operating mode: NORMAL, EMERGENCY, or UNKNOWN_INVALID.
- Determine E3 resource preservation relationships (preserved vs limiting resource).
- Pure evaluator function: strictly read-only state inspection; ZERO side effects or dispatch actions.

Governance:
- HD-03 Operational Target Precedence
- E3 Survivability Margin Semantics
- Fail-Closed Safety Boundary (UNKNOWN_INVALID != EMERGENCY)
"""

from typing import Optional, List, Tuple, Union, Protocol
from dataclasses import dataclass
from enum import Enum
import math


class OperatingMode(str, Enum):
    NORMAL = "NORMAL"
    EMERGENCY = "EMERGENCY"
    UNKNOWN_INVALID = "UNKNOWN_INVALID"


class ResourceSelection(str, Enum):
    BATTERY = "BATTERY"
    DIESEL = "DIESEL"
    BOTH = "TIE / BOTH"
    NONE = "N/A"


class ValidityStatus(str, Enum):
    VALID = "VALID"
    MISSING_T_REQUIRED = "MISSING_T_REQUIRED"
    EXPIRED_T_REQUIRED = "EXPIRED_T_REQUIRED"
    UNAUTHORIZED_T_REQUIRED = "UNAUTHORIZED_T_REQUIRED"
    INVALID_TELEMETRY = "INVALID_TELEMETRY"
    INVALID_CRITICAL_LOAD = "INVALID_CRITICAL_LOAD"
    MISSING_CRITICAL_LOAD_AUTHORIZATION = "MISSING_CRITICAL_LOAD_AUTHORIZATION"
    INVALID_CONFIG = "INVALID_CONFIG"


@dataclass(frozen=True)
class AuthorizedHorizon:
    """Upstream authority payload for operational horizon T_required."""
    t_required_hours: Optional[float]
    is_authenticated: bool = True
    is_authorized: bool = True
    expires_at: Optional[float] = None
    current_time: Optional[float] = None


@dataclass(frozen=True)
class BatteryParameters:
    capacity_wh: float
    min_soc_pct: float
    max_soc_pct: float
    discharge_efficiency: float
    max_discharge_power_w: float


@dataclass(frozen=True)
class DieselParameters:
    base_fuel_consumption_l_per_h: float
    marginal_fuel_consumption_l_per_wh: float
    min_power_w: float
    max_power_w: float
    physical_startup_fuel_l: float = 0.0


@dataclass(frozen=True)
class ECDConfig:
    tie_epsilon_hours: float = 1.0e-6  # 3.6 ms engineering comparison epsilon
    max_telemetry_age_seconds: Optional[float] = None  # Parameterized deployment config


class CriticalLoadTrajectory(Protocol):
    """Abstract interface for critical demand trajectories (BLK-010 resolution)."""
    def get_cumulative_energy_wh(self, duration_hours: float) -> float: ...
    def find_time_for_energy_wh(self, target_energy_wh: float) -> float: ...
    def get_cumulative_fuel_liters(self, duration_hours: float, base_lph: float, marginal_lpwh: float) -> float: ...
    def find_time_for_fuel_liters(self, target_fuel_l: float, base_lph: float, marginal_lpwh: float) -> float: ...


class ConstantCriticalLoad(CriticalLoadTrajectory):
    """Constant critical load implementation (prototype synthetic fixture)."""
    def __init__(self, load_w: float):
        self.load_w = float(load_w)

    def get_cumulative_energy_wh(self, duration_hours: float) -> float:
        return self.load_w * duration_hours

    def find_time_for_energy_wh(self, target_energy_wh: float) -> float:
        if self.load_w <= 0.0:
            return float('inf')
        return target_energy_wh / self.load_w

    def get_cumulative_fuel_liters(self, duration_hours: float, base_lph: float, marginal_lpwh: float) -> float:
        fuel_rate = base_lph + (marginal_lpwh * self.load_w)
        return fuel_rate * duration_hours

    def find_time_for_fuel_liters(self, target_fuel_l: float, base_lph: float, marginal_lpwh: float) -> float:
        fuel_rate = base_lph + (marginal_lpwh * self.load_w)
        if fuel_rate <= 0.0:
            return float('inf')
        return target_fuel_l / fuel_rate


class TimeSeriesCriticalLoad(CriticalLoadTrajectory):
    """Stepwise/time-varying critical load implementation (production trajectory)."""
    def __init__(self, power_trajectory_w: List[float], step_hours: float = 1.0):
        self.power_trajectory_w = [float(p) for p in power_trajectory_w]
        self.step_hours = float(step_hours)

    def get_cumulative_energy_wh(self, duration_hours: float) -> float:
        energy = 0.0
        remaining = duration_hours
        for p in self.power_trajectory_w:
            if remaining <= 0:
                break
            dt = min(remaining, self.step_hours)
            energy += p * dt
            remaining -= dt
        if remaining > 0 and len(self.power_trajectory_w) > 0:
            energy += self.power_trajectory_w[-1] * remaining
        return energy

    def find_time_for_energy_wh(self, target_energy_wh: float) -> float:
        if target_energy_wh <= 0.0:
            return 0.0
        accumulated = 0.0
        time = 0.0
        for p in self.power_trajectory_w:
            step_energy = p * self.step_hours if p > 0.0 else 0.0
            if accumulated + step_energy >= target_energy_wh:
                needed = target_energy_wh - accumulated
                return time + (needed / p if p > 0 else 0.0)
            accumulated += step_energy
            time += self.step_hours
        if len(self.power_trajectory_w) > 0 and self.power_trajectory_w[-1] > 0:
            needed = target_energy_wh - accumulated
            return time + (needed / self.power_trajectory_w[-1])
        return float('inf')

    def get_cumulative_fuel_liters(self, duration_hours: float, base_lph: float, marginal_lpwh: float) -> float:
        fuel = 0.0
        remaining = duration_hours
        for p in self.power_trajectory_w:
            if remaining <= 0:
                break
            dt = min(remaining, self.step_hours)
            rate = base_lph + (marginal_lpwh * p)
            fuel += rate * dt
            remaining -= dt
        if remaining > 0 and len(self.power_trajectory_w) > 0:
            rate = base_lph + (marginal_lpwh * self.power_trajectory_w[-1])
            fuel += rate * remaining
        return fuel

    def find_time_for_fuel_liters(self, target_fuel_l: float, base_lph: float, marginal_lpwh: float) -> float:
        if target_fuel_l <= 0.0:
            return 0.0
        accumulated = 0.0
        time = 0.0
        for p in self.power_trajectory_w:
            rate = base_lph + (marginal_lpwh * p)
            step_fuel = rate * self.step_hours
            if accumulated + step_fuel >= target_fuel_l:
                needed = target_fuel_l - accumulated
                return time + (needed / rate if rate > 0 else 0.0)
            accumulated += step_fuel
            time += self.step_hours
        last_rate = base_lph + (marginal_lpwh * (self.power_trajectory_w[-1] if self.power_trajectory_w else 0.0))
        if last_rate > 0:
            needed = target_fuel_l - accumulated
            return time + (needed / last_rate)
        return float('inf')


@dataclass(frozen=True)
class EmergencyAssessment:
    """Canonical Output Data Structure of the ECD."""
    operating_mode: OperatingMode
    battery_endurance_hours: float
    diesel_endurance_hours: float
    battery_margin_hours: float
    diesel_margin_hours: float
    preserved_resource: ResourceSelection
    limiting_resource: ResourceSelection
    tie_status: bool
    validity_status: ValidityStatus
    failure_reason: Optional[str] = None
    target_horizon_hours: Optional[float] = None


class EmergencyConditionDetector:
    """
    Emergency Condition Detector (ECD) Core Evaluator.
    Pure functional evaluator satisfying POLARIS EMS ECD Contract.
    """

    def __init__(self, config: Optional[ECDConfig] = None):
        self.config = config or ECDConfig()

    def evaluate(
        self,
        horizon_input: Union[AuthorizedHorizon, float],
        critical_load: Optional[Union[CriticalLoadTrajectory, float]],
        soc_pct: float,
        fuel_remaining_liters: float,
        battery_params: BatteryParameters,
        diesel_params: DieselParameters
    ) -> EmergencyAssessment:
        """
        Evaluate microgrid survivability against target horizon and classify operating state.
        """
        # 1. Parse and validate authority / horizon input
        if isinstance(horizon_input, AuthorizedHorizon):
            auth = horizon_input
        elif isinstance(horizon_input, (int, float)):
            auth = AuthorizedHorizon(t_required_hours=float(horizon_input))
        else:
            return self._fail_closed(ValidityStatus.MISSING_T_REQUIRED, "Target horizon input is missing or malformed.")

        if not auth.is_authenticated:
            return self._fail_closed(ValidityStatus.UNAUTHORIZED_T_REQUIRED, "Target horizon payload is unauthenticated.")
        if not auth.is_authorized:
            return self._fail_closed(ValidityStatus.UNAUTHORIZED_T_REQUIRED, "Target horizon payload is unauthorized.")

        if auth.t_required_hours is None or math.isnan(auth.t_required_hours) or math.isinf(auth.t_required_hours):
            return self._fail_closed(ValidityStatus.MISSING_T_REQUIRED, "Target horizon t_required is missing or non-finite.")

        if auth.t_required_hours <= 0.0:
            return self._fail_closed(ValidityStatus.MISSING_T_REQUIRED, f"Invalid target horizon value: {auth.t_required_hours}")

        if auth.expires_at is not None and auth.current_time is not None:
            if auth.current_time > auth.expires_at:
                return self._fail_closed(ValidityStatus.EXPIRED_T_REQUIRED, f"Target horizon expired at {auth.expires_at}")

        t_target = auth.t_required_hours

        # 2. Parse and validate critical load input
        # `None` is treated distinctly from a malformed-but-present value:
        # it means no authorized, authoritative critical-load evidence was
        # supplied at all (e.g. the caller has no EVID-02-class station
        # measurement to offer), as opposed to a value that was supplied but
        # is non-finite/non-positive/wrongly-typed. Both fail closed to
        # UNKNOWN_INVALID; the distinct status makes the reason legible
        # (docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md ECD-01, Decision B = B-iii).
        if critical_load is None:
            return self._fail_closed(
                ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION,
                "Critical load input is missing: no authorized, authoritative "
                "critical-load evidence was supplied."
            )
        if isinstance(critical_load, (int, float)):
            if critical_load <= 0.0 or math.isnan(critical_load) or math.isinf(critical_load):
                return self._fail_closed(ValidityStatus.INVALID_CRITICAL_LOAD, f"Invalid critical load value: {critical_load}")
            load_traj: CriticalLoadTrajectory = ConstantCriticalLoad(float(critical_load))
        elif hasattr(critical_load, 'find_time_for_energy_wh'):
            load_traj = critical_load
        else:
            return self._fail_closed(ValidityStatus.INVALID_CRITICAL_LOAD, "Critical load input is invalid.")

        # 3. Validate telemetry & parameters
        if math.isnan(soc_pct) or math.isinf(soc_pct) or soc_pct < 0.0 or soc_pct > 100.0:
            return self._fail_closed(ValidityStatus.INVALID_TELEMETRY, f"Invalid battery SOC percentage: {soc_pct}")

        if math.isnan(fuel_remaining_liters) or math.isinf(fuel_remaining_liters) or fuel_remaining_liters < 0.0:
            return self._fail_closed(ValidityStatus.INVALID_TELEMETRY, f"Invalid fuel quantity: {fuel_remaining_liters}")

        if battery_params.capacity_wh <= 0.0 or battery_params.discharge_efficiency <= 0.0 or battery_params.discharge_efficiency > 1.0:
            return self._fail_closed(ValidityStatus.INVALID_CONFIG, "Invalid battery configuration parameters.")

        if diesel_params.base_fuel_consumption_l_per_h < 0.0 or diesel_params.marginal_fuel_consumption_l_per_wh < 0.0:
            return self._fail_closed(ValidityStatus.INVALID_CONFIG, "Invalid diesel generator parameters.")

        # 4. Calculate usable battery AC energy and endurance
        soc_usable_pct = max(0.0, soc_pct - battery_params.min_soc_pct)
        usable_dc_energy_wh = battery_params.capacity_wh * (soc_usable_pct / 100.0)
        usable_ac_energy_wh = usable_dc_energy_wh * battery_params.discharge_efficiency

        t_battery = load_traj.find_time_for_energy_wh(usable_ac_energy_wh)

        # 5. Calculate diesel fuel endurance
        available_fuel_l = max(0.0, fuel_remaining_liters - diesel_params.physical_startup_fuel_l)
        t_diesel = load_traj.find_time_for_fuel_liters(
            available_fuel_l,
            diesel_params.base_fuel_consumption_l_per_h,
            diesel_params.marginal_fuel_consumption_l_per_wh
        )

        # 6. Calculate survivability margins against t_target
        m_battery = t_battery - t_target
        m_diesel = t_diesel - t_target

        # 7. Evaluate emergency operating mode
        if m_battery >= 0.0 and m_diesel >= 0.0:
            mode = OperatingMode.NORMAL
        else:
            mode = OperatingMode.EMERGENCY

        # 8. Evaluate E3 resource selection and tie detection
        margin_diff = abs(m_battery - m_diesel)
        is_tie = margin_diff <= self.config.tie_epsilon_hours

        if mode == OperatingMode.NORMAL:
            if is_tie:
                preserved = ResourceSelection.BOTH
                limiting = ResourceSelection.BOTH
            else:
                preserved = ResourceSelection.NONE
                limiting = ResourceSelection.NONE
        else:  # EMERGENCY
            if is_tie:
                preserved = ResourceSelection.BOTH
                limiting = ResourceSelection.BOTH
            elif m_battery > m_diesel:
                preserved = ResourceSelection.BATTERY
                limiting = ResourceSelection.DIESEL
            else:
                preserved = ResourceSelection.DIESEL
                limiting = ResourceSelection.BATTERY

        return EmergencyAssessment(
            operating_mode=mode,
            battery_endurance_hours=t_battery,
            diesel_endurance_hours=t_diesel,
            battery_margin_hours=m_battery,
            diesel_margin_hours=m_diesel,
            preserved_resource=preserved,
            limiting_resource=limiting,
            tie_status=is_tie,
            validity_status=ValidityStatus.VALID,
            failure_reason=None,
            target_horizon_hours=t_target
        )

    def _fail_closed(self, status: ValidityStatus, reason: str) -> EmergencyAssessment:
        """Fail closed to UNKNOWN_INVALID without declaring EMERGENCY or NORMAL."""
        return EmergencyAssessment(
            operating_mode=OperatingMode.UNKNOWN_INVALID,
            battery_endurance_hours=0.0,
            diesel_endurance_hours=0.0,
            battery_margin_hours=0.0,
            diesel_margin_hours=0.0,
            preserved_resource=ResourceSelection.NONE,
            limiting_resource=ResourceSelection.NONE,
            tie_status=False,
            validity_status=status,
            failure_reason=reason,
            target_horizon_hours=None
        )
