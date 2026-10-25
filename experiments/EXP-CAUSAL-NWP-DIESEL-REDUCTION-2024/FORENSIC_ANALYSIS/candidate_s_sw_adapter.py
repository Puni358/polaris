"""
POLARIS Research-Only Candidate S & Candidate SW Adapter
Module: experiments.EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024.FORENSIC_ANALYSIS.candidate_s_sw_adapter

RESEARCH USE ONLY / CLOSED-LOOP DIESEL REDUCTION CANDIDATES:
Implements Candidate 2, Variant S (Solar-Only Net EBR) and Candidate 2, Variant SW
(Solar + Synthetic Wind Net EBR) for the POLARIS microgrid closed-loop evaluation harness.

MATHEMATICAL SPECIFICATIONS (from frozen EXP_CANDIDATE_S_SW_PREREGISTRATION.md):

1. Candidate 2, Variant S (Solar-Only Net EBR):
   For each reoptimization time step t in {0 .. 22}:
       E_EBR_S[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} max(0, critical_demand[k] - solar_generation_point[k]) * dt
   At horizon edge t = 23:
       E_stage2_target[23] = max((1 / eta_dis) * max(0, critical_demand[23] - solar_generation_point[23]) * dt, E_term_target)

   - Consumes direct electrical PV power: `bundle.solar_generation.point` in Watts.
   - Zero wind credit in reserve sizing (wind remains active in busbar balance).
   - Reverts to governed unconditional EBR when forecast solar is zero across the entire window.

2. Candidate 2, Variant SW (Solar + Synthetic Wind Net EBR):
   Adds -wind_generation_point[k] within the deficit bracket:
       E_EBR_SW[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} max(0, critical_demand[k] - solar_generation_point[k] - wind_generation_point[k]) * dt
   At horizon edge t = 23:
       E_stage2_target[23] = max((1 / eta_dis) * max(0, critical_demand[23] - solar_generation_point[23] - wind_generation_point[23]) * dt, E_term_target)

   - Synthetic Wind Caveat: Benchmark wind series is synthetic; evidence represents synthetic proof of concept.

ZERO PRODUCTION CODE MODIFICATIONS:
- GAP19 (system/optimization/implementations/gap19_highs_native.py) is UNTOUCHED.
- Causal NWP forecaster (system/forecasting/implementations/causal_nwp_physics.py) is UNTOUCHED.
- Production router (system/control/router.py) is UNTOUCHED.
- Simulator / realization executor (system/simulation/research_realization_executor.py) is UNTOUCHED.
- Governed baseline configs (system/config/*.yaml) are UNTOUCHED.
- Preregistration artifacts are UNTOUCHED.
"""

import math
from typing import List, Dict, Any, Optional
import pandas as pd

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.dispatch_plan import DispatchPlan
from system.research.research_critical_demand_adapter import (
    AdaptedClosedLoopRunner,
    adapt_critical_demand_vector
)

# Governed POLARIS System Constants
ETA_DIS: float = 0.92
DT: float = 1.0
TERMINAL_TARGET_WH: float = 100000.0
CRITICAL_CEILING_W: float = 11600.0


def compute_governed_ebr(
    critical_demand_w: List[float],
    eta_dis: float = ETA_DIS,
    dt: float = DT
) -> List[float]:
    """
    Computes the governed 6-hour lookahead unconditional EBR trajectory.
    Matches GAP19 lines 127-131:
        E_req[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} critical_demand[k] * dt
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
        val = w_sum / eta_dis
        ebr.append(val)

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
    Computes Candidate 2, Variant S (Solar-Only Net EBR) trajectory:
        E_EBR_S[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} max(0, critical_demand[k] - solar_w[k]) * dt

    For each reoptimization time step t in {0 .. 23}.
    Consumes direct electrical PV power in Watts (solar_w).
    Zero wind credit is awarded.
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
    Computes Candidate 2, Variant SW (Solar + Synthetic Wind Net EBR) trajectory:
        E_EBR_SW[t] = (1 / eta_dis) * sum_{k=t}^{min(t+5, 23)} max(0, critical_demand[k] - solar_w[k] - wind_w[k]) * dt

    For each reoptimization time step t in {0 .. 23}.
    Consumes direct electrical PV power in Watts (solar_w) and wind generation in Watts (wind_w).
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


class CandidateEBROptimizerWrapper:
    """
    Non-invasive optimizer wrapper around GAP19HighsNativeOptimizer.
    Intercepts the optimization call, calculates candidate-specific EBR trajectory
    from the current ForecastBundle and adapted critical demand, and passes it
    through the standard `config["ebr_target_wh"]` interface without touching GAP19.
    """

    def __init__(self, inner_optimizer: Any, variant: str):
        valid_variants = ("S", "SW", "FROZEN_B", "OFF")
        if variant not in valid_variants:
            raise ValueError(f"Unknown variant '{variant}', expected one of {valid_variants}")
        self.inner_optimizer = inner_optimizer
        self.variant = variant
        self.call_history: List[Dict[str, Any]] = []

    def optimize(
        self,
        bundle: ForecastBundle,
        station_state: StationState,
        config: Dict[str, Any]
    ) -> DispatchPlan:
        # Step configs copy to prevent side effects
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

        ebr_used: Optional[List[float]] = None
        if self.variant == "S":
            ebr_used = compute_variant_s_ebr(crit_w, solar_w)
            step_config["ebr_target_wh"] = ebr_used
        elif self.variant == "SW":
            ebr_used = compute_variant_sw_ebr(crit_w, solar_w, wind_w)
            step_config["ebr_target_wh"] = ebr_used
        elif self.variant == "OFF":
            ebr_used = [0.0] * 24
            step_config["ebr_target_wh"] = ebr_used
        elif self.variant == "FROZEN_B":
            # Baseline uses internal governed unconditional formula
            step_config.pop("ebr_target_wh", None)

        plan = self.inner_optimizer.optimize(bundle, station_state, step_config)

        # Record step observation for diagnostics/verification
        self.call_history.append({
            "variant": self.variant,
            "forecast_solar_w": solar_w,
            "forecast_wind_w": wind_w,
            "critical_demand_w": crit_w,
            "ebr_trajectory_wh": ebr_used,
            "j2_shortfall_wh": plan.j2_objective if plan.j2_objective is not None else 0.0,
            "constraint_status": plan.constraint_status
        })

        return plan

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner_optimizer, name)


class CandidateSClosedLoopRunner(AdaptedClosedLoopRunner):
    """
    Research closed-loop runner for Candidate 2, Variant S (Solar-Only Net EBR).
    Inherits AdaptedClosedLoopRunner and equips the optimizer with the Variant S interceptor.
    """
    def __init__(self, configs: Dict[str, Any]):
        super().__init__(configs)
        self.variant = "S"
        self.optimizer = CandidateEBROptimizerWrapper(self.optimizer, variant="S")


class CandidateSWClosedLoopRunner(AdaptedClosedLoopRunner):
    """
    Research closed-loop runner for Candidate 2, Variant SW (Solar + Synthetic Wind Net EBR).
    Inherits AdaptedClosedLoopRunner and equips the optimizer with the Variant SW interceptor.
    """
    def __init__(self, configs: Dict[str, Any]):
        super().__init__(configs)
        self.variant = "SW"
        self.optimizer = CandidateEBROptimizerWrapper(self.optimizer, variant="SW")


class CandidateControlBClosedLoopRunner(AdaptedClosedLoopRunner):
    """
    Research closed-loop runner for Frozen Control B (MEPS Causal NWP + 6h Governed Unconditional EBR).
    Inherits AdaptedClosedLoopRunner without EBR overrides.
    """
    def __init__(self, configs: Dict[str, Any]):
        super().__init__(configs)
        self.variant = "FROZEN_B"
        self.optimizer = CandidateEBROptimizerWrapper(self.optimizer, variant="FROZEN_B")
