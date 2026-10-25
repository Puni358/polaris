"""
POLARIS Energy Management System (EMS)
EMS Control Router Implementation

Architectural Responsibility:
- Pure policy routing layer wrapping EmergencyConditionDetector (ECD) and optimizers.
- Consumes StationState, ForecastBundle, and system configs to evaluate EmergencyAssessment.
- Routes execution to Option B HiGHS Native MPC (NORMAL) or Option D Fallback Solver (EMERGENCY).
- Intercepts UNKNOWN_INVALID states to enforce fail-closed safety boundaries.
- Strictly read-only state inspection; zero side effects on physical state or optimizer mathematics.

Governance (docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md, item ECD-01, decided 2026-10-18;
see docs/decision_registers/HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md Section 9 for the exact decision text):
- Decision A = A-iii: T_required fails closed to UNKNOWN_INVALID unless an
  explicitly authorized, explicit numeric value is supplied in
  configs["ecd"]. The ungoverned 6.0h code default is REMOVED. The 72h
  prototype value is NOT promoted; no numerical T_required is invented here.
- Decision B = B-iii: critical-load-for-routing fails closed to
  UNKNOWN_INVALID unless configs["critical_load"] carries an explicit
  authorization flag, a real-station evidence-record id (EVID-xx, not a
  research-scoped design value such as CL-01), and a numeric value. This
  router NEVER substitutes current_state.last_observed_demand,
  bundle.demand.point[0], or any hardcoded floor for authoritative
  critical-load evidence (the pre-existing substitution chain this decision
  replaces).
- Decision C = M-A: UNKNOWN_INVALID is returned as its own distinct route by
  this router (see "6. Policy Routing" below) and is never remapped to
  EMERGENCY. No stale last-known-good value is substituted (no freshness
  policy is authorized) and no fallback dispatch value is invented here.

Config contract introduced to express authorization (consumed only here;
ECD itself remains a pure evaluator and is unaware of this schema):
    configs["ecd"] = {
        "t_required_hours": <float>,      # explicit numeric value
        "t_required_authorized": True,    # explicit authorization flag
    }
    configs["critical_load"] = {
        "authorized": True,                    # explicit authorization flag
        "evidence_id": "EVID-02",              # must reference a real-station
                                                # evidence record (EVID-xx);
                                                # a research-scoped design
                                                # value (e.g. "CL-01") does not
                                                # satisfy this check
        "authorized_critical_load_w": <float>, # explicit numeric value
    }
A synthetic scenario input (e.g. a CLI's --critical-load-kw, conventionally
surfaced to optimizers via configs["critical_demand_w"]) is a SEPARATE input
slot and is never read here -- it must never become authoritative routing
evidence.
"""

from typing import Dict, Any, Tuple, Optional
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.control.ecd import (
    EmergencyConditionDetector,
    AuthorizedHorizon,
    BatteryParameters,
    DieselParameters,
    OperatingMode,
    EmergencyAssessment
)

# Real-station critical-load evidence must be cited by an EVID-xx record
# (e.g. EVID-02, the real Nuolja critical-load measurement track). A
# research-scoped design value such as CL-01 (POLARIS_MASTER_DECISION_
# REGISTER.md, blocking_scope="research") is explicitly NOT sufficient
# authorization for routing use (docs/decision_registers/HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md
# Section 3, Decision B-ii: "CL-01's existing decision record does not reach
# this use"). This prefix check is this router's own minimal, additive
# enforcement of that already-recorded distinction; it invents no new
# governance, it only refuses to treat an out-of-scope id as in-scope.
_REQUIRED_CRITICAL_LOAD_EVIDENCE_PREFIX = "EVID-"


class EMSControlRouter:
    """
    EMS Policy Control Router wrapping ECD evaluator.
    """

    def __init__(self, ecd_config: Optional[Any] = None):
        self.ecd = EmergencyConditionDetector(config=ecd_config)

    def evaluate_and_route(
        self,
        current_state: StationState,
        bundle: ForecastBundle,
        configs: Dict[str, Any]
    ) -> Tuple[EmergencyAssessment, str]:
        """
        Evaluates ECD microgrid survivability assessment and determines policy route.
        Returns (EmergencyAssessment, route_mode) where route_mode is "NORMAL", "EMERGENCY", or "UNKNOWN_INVALID".
        """
        # 1. Authority / Horizon Payload (Decision A = A-iii)
        # No ungoverned default. A value is only treated as authorized when
        # configs["ecd"] explicitly says so via "t_required_authorized". If
        # that flag is absent/false, the horizon payload is marked
        # unauthenticated/unauthorized so ECD's own existing fail-closed
        # validation rejects it (ValidityStatus.UNAUTHORIZED_T_REQUIRED).
        ecd_cfg = configs.get("ecd", {})
        raw_t_required = ecd_cfg.get("t_required_hours")
        t_required_authorized = bool(ecd_cfg.get("t_required_authorized", False))

        if raw_t_required is None:
            horizon_value: Optional[float] = None
        else:
            try:
                horizon_value = float(raw_t_required)
            except (TypeError, ValueError):
                # Malformed (non-numeric) value: pass through as NaN so
                # ECD's own numeric validation fails closed with a precise
                # reason, rather than this router silently discarding it.
                horizon_value = float('nan')

        auth_horizon = AuthorizedHorizon(
            t_required_hours=horizon_value,
            is_authenticated=t_required_authorized,
            is_authorized=t_required_authorized
        )

        # 2. Critical Load Evidence (Decision B = B-iii)
        # No substitution from current_state.last_observed_demand,
        # bundle.demand.point[0], or a hardcoded floor. A numeric value is
        # used only when configs["critical_load"] explicitly marks itself
        # authorized AND cites a real-station evidence record (EVID-xx), AND
        # supplies a value. Otherwise `None` is passed to ECD, which fails
        # closed (ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION).
        cl_cfg = configs.get("critical_load", {})
        critical_load_authorized = bool(cl_cfg.get("authorized", False))
        critical_load_evidence_id = cl_cfg.get("evidence_id")
        raw_critical_load = cl_cfg.get("authorized_critical_load_w")

        evidence_in_scope = (
            isinstance(critical_load_evidence_id, str)
            and critical_load_evidence_id.strip().upper().startswith(_REQUIRED_CRITICAL_LOAD_EVIDENCE_PREFIX)
        )

        if critical_load_authorized and evidence_in_scope and raw_critical_load is not None:
            try:
                critical_load_input: Optional[float] = float(raw_critical_load)
            except (TypeError, ValueError):
                # Malformed (non-numeric) value: let ECD's own numeric
                # validation fail closed with a precise reason.
                critical_load_input = float('nan')
        else:
            critical_load_input = None

        # 3. Telemetry & Fuel State (unrelated to ECD-01; unchanged)
        soc_pct = float(current_state.battery_soc_pct)

        fuel_l = current_state.diesel_fuel_remaining_liters
        if fuel_l is None:
            fuel_l = float(configs.get("diesel", {}).get("initial_fuel_l", 100.0))

        # 4. Hardware Parameters (unrelated to ECD-01; unchanged)
        bat_cfg = configs.get("battery", {})
        battery_params = BatteryParameters(
            capacity_wh=float(bat_cfg.get("capacity_wh", 200000.0)),
            min_soc_pct=float(bat_cfg.get("min_soc_pct", 20.0)),
            max_soc_pct=float(bat_cfg.get("max_soc_pct", 95.0)),
            discharge_efficiency=float(bat_cfg.get("discharge_efficiency", 0.92)),
            max_discharge_power_w=float(bat_cfg.get("max_discharge_power_w", 50000.0))
        )

        diesel_cfg = configs.get("diesel", {})
        diesel_params = DieselParameters(
            base_fuel_consumption_l_per_h=float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0)),
            marginal_fuel_consumption_l_per_wh=float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025)),
            min_power_w=float(diesel_cfg.get("min_power_w", 10000.0)),
            max_power_w=float(diesel_cfg.get("max_power_w", 50000.0)),
            physical_startup_fuel_l=float(diesel_cfg.get("physical_startup_fuel_l", 0.0))
        )

        # 5. Evaluate Emergency Condition
        assessment = self.ecd.evaluate(
            horizon_input=auth_horizon,
            critical_load=critical_load_input,
            soc_pct=soc_pct,
            fuel_remaining_liters=fuel_l,
            battery_params=battery_params,
            diesel_params=diesel_params
        )

        # 6. Policy Routing (Decision C = M-A)
        # UNKNOWN_INVALID is passed through as its own distinct route. It is
        # NEVER remapped to EMERGENCY, and no stale/last-known-good value or
        # fallback dispatch value is substituted here.
        if assessment.operating_mode == OperatingMode.NORMAL:
            route = "NORMAL"
        elif assessment.operating_mode == OperatingMode.EMERGENCY:
            route = "EMERGENCY"
        else:
            route = "UNKNOWN_INVALID"

        return assessment, route
