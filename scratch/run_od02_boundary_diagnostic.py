"""
POLARIS — Minimal Batch Diagnostic Runner: OD-02 Boundary Evaluation (Authoring Only)
Tracking ID: RUN-2026-OD02-DIAG-01
Reference Specification: SPEC-2026-OD02-DIAG-01
Canonical Governance: MDR v1.9.13 (Pass 23, 2026-10-19)

STATUS: GATE B.4 AUTHORIZED — SCRIPT AUTHORING AND STATIC TESTS ONLY.
GATE C STATUS: STRICTLY NOT AUTHORIZED (Zero optimizer/HiGHS execution permitted).

GOVERNANCE CONTRACT:
- Decision OD-02 remains FROZEN (solar point shifted 1..23 -> 0..22, slot 23 = 0.0 W fallback).
- winner: null preserved.
- 2025 blind evaluation data remains strictly quarantined.
- Production code, MDR, and baseline artifacts remain UNTOUCHED.
- Variant V0 ONLY. Variants V1-V3 remain rejected/disabled.
- Processes exactly the verified 10-origin manifest from 2024-EVEN.
- Fails closed BEFORE optimizer construction or solver invocation unless Gate C is authorized.
"""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Ensure repository root is on sys.path
REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

if "diag_od02_boundary" in sys.modules and "scratch.diag_od02_boundary" not in sys.modules:
    sys.modules["scratch.diag_od02_boundary"] = sys.modules["diag_od02_boundary"]
elif "scratch.diag_od02_boundary" in sys.modules and "diag_od02_boundary" not in sys.modules:
    sys.modules["diag_od02_boundary"] = sys.modules["scratch.diag_od02_boundary"]

from scratch.diag_od02_boundary import (
    ContinuousActionVector,
    DatasetIngestionFirewall,
    GateExecutionBlockedError,
    InputManifestItem,
    MDR_CANONICAL_VERSION,
    ObjectiveComponents,
    QuarantineViolationError,
    SolverTerminationStatus,
    align_bundle_variant_0,
    assert_gate_c_authorized,
    check_quarantine_compliance,
    execute_diagnostic_solve,
    extract_first_action_from_dispatch_plan,
    extract_objectives_from_dispatch_plan,
    prepare_gap19_solver_config,
    VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN,
)
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState

# ==============================================================================
# 1. GOVERNED CONSTANTS & APPROVED MANIFEST PROVENANCE
# ==============================================================================

RUNNER_TRACKING_ID = "RUN-2026-OD02-DIAG-01"
DEFAULT_OUTPUT_DIR = "experiments/diagnostics/diag_od02_boundary_2024"

# Governed physical conversion parameters (Nuolja Station)
K_PV_CONVERSION_W_PER_WM2 = 51.0
INVERTER_MAX_POWER_W = 60000.0
SYNTHETIC_BASE_DEMAND_W = 15000.0
SYNTHETIC_CRITICAL_DEMAND_W = 11600.0  # Governed 11.6 kW comfort load (CL-01)
GENERIC_WIND_POWER_W = 5000.0
BATTERY_CAPACITY_WH = 200000.0
BATTERY_MIN_SOC_PCT = 20.0
BATTERY_MAX_SOC_PCT = 95.0
EBR_BASE_WH = 15000.0
SCALE_FLOOR_WH = 100.0
Q90_W_CONFORMAL_MULTIPLIER = 1.5702
ETA_DISCHARGE = 0.92

# Approved 2024 input files allow-list
APPROVED_2024_INPUT_ALLOW_LIST: List[InputManifestItem] = [
    InputManifestItem(
        file_path="forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv",
        expected_sha256="0cfc8002e6bf0e8ad11d9ec9832b45a1f085c9d435934a24a3c4edb6b51d62ad",
        description="Canonical fold assignment matrix (174 EVEN origins)",
        is_verified=True,
    ),
    InputManifestItem(
        file_path="data/POLARIS_v0_1_clearsky_decomposition.csv",
        expected_sha256="596345aa330313414ba41f63ad65278914c6ed1e179965162439e6139a70e52a",
        description="Nuolja station clear-sky solar elevation and irradiance decomposition",
        is_verified=True,
    ),
    InputManifestItem(
        file_path="data/POLARIS_v0_1_future_weather_forecasts_2024.csv",
        expected_sha256="8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16",
        description="Historical NWP future weather forecasts for 2024",
        is_verified=True,
    ),
]


# ==============================================================================
# 2. RESULT SCHEMA (STRICT TYPING & VALUE FIDELITY)
# ==============================================================================

@dataclass
class DiagnosticOriginResult:
    """
    Per-origin diagnostic execution result record.
    Distinguishes unavailable fields (None) from measured zero values (0.0).
    """
    origin_id: int
    origin_timestamp: str
    stratum: str
    parity: str
    canonical_fold: int
    variant_id: int = 0
    variant_name: str = "Variant 0 (Frozen OD-02 Baseline)"
    
    # Solver execution outcome
    solver_status: str = "NOT_RUN"
    is_successful_solve: bool = False
    
    # Lexicographic objective tiers (None if unavailable or infeasible)
    j1_critical_deficit_wh: Optional[float] = None
    j2_reserve_shortfall_wh: Optional[float] = None
    j3_diesel_fuel_liters: Optional[float] = None
    j4_curtailment_wh: Optional[float] = None
    
    # Decision vector at dispatch step t=0 (None if unavailable or infeasible)
    first_action: Optional[Dict[str, Optional[float]]] = None
    
    # Operational & error metadata
    runtime_seconds: float = 0.0
    error_message: Optional[str] = None
    execution_timestamp: str = ""
    input_hashes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes result to dictionary, preserving explicit None values."""
        return asdict(self)


# ==============================================================================
# 3. MANIFEST & PROVENANCE VALIDATION (FAIL-CLOSED)
# ==============================================================================

def verify_origin_manifest(manifest: Sequence[Dict[str, Any]]) -> None:
    """
    Enforces fail-closed validation of the 10-origin 2024-EVEN sampling frame.
    Strictly rejects any unapproved origin, ODD parity, or 2025/blind contamination.
    """
    if len(manifest) != 10:
        raise ValueError(f"Fail-closed: Expected exactly 10 diagnostic origins, got {len(manifest)}.")

    regime_counts = {"REGIME_A_POLAR_DAY": 0, "REGIME_B_DYNAMIC_SHOULDER": 0, "REGIME_C_POLAR_NIGHT": 0}
    seen_ids = set()
    seen_timestamps = set()

    for item in manifest:
        orig_id = item.get("forecast_origin")
        ts = str(item.get("timestamp", ""))
        parity = item.get("parity")
        stratum = item.get("stratum")

        # 1. Uniqueness
        if orig_id in seen_ids:
            raise ValueError(f"Fail-closed: Duplicate origin ID {orig_id} in manifest.")
        if ts in seen_timestamps:
            raise ValueError(f"Fail-closed: Duplicate origin timestamp {ts} in manifest.")
        seen_ids.add(orig_id)
        seen_timestamps.add(ts)

        # 2. Strict 2024-EVEN parity check
        if parity != "EVEN":
            raise ValueError(f"Fail-closed: Origin {orig_id} has invalid parity '{parity}'; expected 'EVEN'.")
        if orig_id % 2 != 0:
            raise ValueError(f"Fail-closed: Origin {orig_id} is odd, violates 2024-EVEN requirement.")

        # 3. Quarantine defense-in-depth token check
        check_quarantine_compliance(ts)
        if not ts.startswith("2024-"):
            raise QuarantineViolationError(f"Fail-closed: Origin timestamp '{ts}' is not in 2024.")
        if not ts.endswith("T00:00:00Z"):
            raise ValueError(f"Fail-closed: Origin '{ts}' violates mandatory midnight-UTC origin contract.")

        # 4. Stratum validation
        if stratum not in regime_counts:
            raise ValueError(f"Fail-closed: Unknown stratum '{stratum}' for origin {orig_id}.")
        regime_counts[stratum] += 1

    # Verify exact stratification: 4 Polar Day, 3 Dynamic Shoulder, 3 Polar Night
    if regime_counts["REGIME_A_POLAR_DAY"] != 4:
        raise ValueError(f"Fail-closed: Expected 4 Polar Day origins, got {regime_counts['REGIME_A_POLAR_DAY']}.")
    if regime_counts["REGIME_B_DYNAMIC_SHOULDER"] != 3:
        raise ValueError(f"Fail-closed: Expected 3 Dynamic Shoulder origins, got {regime_counts['REGIME_B_DYNAMIC_SHOULDER']}.")
    if regime_counts["REGIME_C_POLAR_NIGHT"] != 3:
        raise ValueError(f"Fail-closed: Expected 3 Polar Night origins, got {regime_counts['REGIME_C_POLAR_NIGHT']}.")


def compute_file_sha256(path: Path | str) -> str:
    """Computes SHA-256 digest of a local file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# 4. PRODUCTION SCHEMA CONSTRUCTORS & DATA BUILDERS
# ==============================================================================

def build_diagnostic_forecast_bundle(
    origin_metadata: Dict[str, Any],
    solar_irradiance_raw_wm2: Sequence[float],
) -> ForecastBundle:
    """
    Constructs a valid production ForecastBundle conforming to Version 1.0.0.
    Derives solar electrical generation via governed plant conversion factor K_pv.
    Computes split-conformal EBR trajectory and attaches it to bundle metadata.
    """
    origin_ts = str(origin_metadata["timestamp"])
    dt_origin = datetime.fromisoformat(origin_ts.replace("Z", "+00:00"))
    
    # 24 consecutive hourly timestamps [t0 + 1h, ..., t0 + 24h]
    timestamps = [
        (dt_origin + timedelta(hours=h + 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for h in range(24)
    ]
    
    # Solar irradiance (W/m^2)
    raw_irr = [float(max(0.0, s)) for s in solar_irradiance_raw_wm2]
    if len(raw_irr) != 24:
        raise ValueError(f"Fail-closed: Expected 24 solar irradiance values, got {len(raw_irr)}.")

    # Solar generation (W) via plant conversion factor
    gen_pts = [min(K_PV_CONVERSION_W_PER_WM2 * s, INVERTER_MAX_POWER_W) for s in raw_irr]
    
    # TimeseriesForecast objects
    sol_irr = TimeseriesForecast(raw_irr, raw_irr, raw_irr, "W/m^2")
    sol_gen = TimeseriesForecast(gen_pts, gen_pts, gen_pts, "W")
    wind_gen = TimeseriesForecast([GENERIC_WIND_POWER_W] * 24, [GENERIC_WIND_POWER_W] * 24, [GENERIC_WIND_POWER_W] * 24, "W")
    demand_tot = TimeseriesForecast([SYNTHETIC_BASE_DEMAND_W] * 24, [SYNTHETIC_BASE_DEMAND_W] * 24, [SYNTHETIC_BASE_DEMAND_W] * 24, "W")
    demand_crit = TimeseriesForecast([SYNTHETIC_CRITICAL_DEMAND_W] * 24, [SYNTHETIC_CRITICAL_DEMAND_W] * 24, [SYNTHETIC_CRITICAL_DEMAND_W] * 24, "W")

    # Governed rolling 6-hour conformal EBR reserve calculation
    # ebr[t] = max(EBR_BASE_WH, Q90_W * (sum(s_hourly[t:t+6]) + SCALE_FLOOR_WH))
    s_hourly_wh = [K_PV_CONVERSION_W_PER_WM2 * s / ETA_DISCHARGE for s in raw_irr]
    ebr_target_wh: List[float] = []
    for t in range(24):
        t_end = min(t + 6, 24)
        scale_w_t = sum(s_hourly_wh[t:t_end]) + SCALE_FLOOR_WH
        ebr_val = max(EBR_BASE_WH, Q90_W_CONFORMAL_MULTIPLIER * scale_w_t)
        ebr_target_wh.append(float(round(ebr_val, 2)))

    metadata = {
        "model_id": "candidate_n6_production_reference",
        "origin_id": origin_metadata["forecast_origin"],
        "parity": origin_metadata["parity"],
        "stratum": origin_metadata["stratum"],
        "ebr_target_wh": ebr_target_wh,
        "reserve_policy": "POLICY_B",
        "generation_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=origin_ts,
        horizon_hours=24,
        timestamps=timestamps,
        solar_irradiance=sol_irr,
        solar_generation=sol_gen,
        wind_generation=wind_gen,
        demand=demand_tot,
        demand_critical=demand_crit,
        metadata=metadata,
    )


def build_diagnostic_station_state(
    origin_metadata: Dict[str, Any],
    initial_soc_pct: float = 50.0,
) -> StationState:
    """Constructs a valid production StationState conforming to schema."""
    origin_ts = str(origin_metadata["timestamp"])
    battery_energy_wh = BATTERY_CAPACITY_WH * (initial_soc_pct / 100.0)
    
    return StationState(
        timestamp=origin_ts,
        battery_soc_pct=initial_soc_pct,
        battery_energy_wh=battery_energy_wh,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=SYNTHETIC_BASE_DEMAND_W,
        last_observed_wind_generation=GENERIC_WIND_POWER_W,
        operating_mode="NORMAL",
    )


# ==============================================================================
# 5. SINGLE-ORIGIN EXECUTION UNIT (V0 ONLY)
# ==============================================================================

def execute_single_origin_diagnostic(
    origin: Dict[str, Any],
    raw_irradiance_24h: Sequence[float],
    config: Dict[str, Any],
    mock_optimizer: Optional[Any] = None,
) -> DiagnosticOriginResult:
    """
    Executes diagnostic evaluation for a single origin under frozen Variant V0.
    FAILS CLOSED unless Gate C is authorized or an explicit mock double is supplied in tests.
    """
    t_start = time.perf_counter()
    exec_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    res = DiagnosticOriginResult(
        origin_id=origin["forecast_origin"],
        origin_timestamp=origin["timestamp"],
        stratum=origin["stratum"],
        parity=origin["parity"],
        canonical_fold=origin["canonical_fold"],
        variant_id=0,
        variant_name="Variant 0 (Frozen OD-02 Baseline)",
        execution_timestamp=exec_ts,
    )

    try:
        # 1. Enforce Gate C firewall check BEFORE constructing or executing solver
        assert_gate_c_authorized()

        # 2. Build production ForecastBundle and StationState
        raw_bundle = build_diagnostic_forecast_bundle(origin, raw_irradiance_24h)
        station_state = build_diagnostic_station_state(origin)

        # 3. Apply Variant 0 (Frozen OD-02 Baseline shift: raw 1..23 -> 0..22, slot 23 = 0.0)
        v0_bundle = align_bundle_variant_0(raw_bundle)

        # 4. Execute solver conforming to EnergyOptimizer protocol
        status, u0, objs = execute_diagnostic_solve(
            variant_bundle=v0_bundle,
            station_state=station_state,
            config=config,
            mock_optimizer=mock_optimizer,
        )

        res.solver_status = status.value
        res.runtime_seconds = round(time.perf_counter() - t_start, 4)

        if status == SolverTerminationStatus.OPTIMAL and u0 is not None and objs is not None:
            res.is_successful_solve = True
            res.j1_critical_deficit_wh = objs.j1_critical_deficit
            res.j2_reserve_shortfall_wh = objs.j2_reserve_shortfall
            res.j3_diesel_fuel_liters = objs.j3_diesel_fuel_cost
            res.j4_curtailment_wh = objs.j4_curtailment_penalty
            res.first_action = u0.continuous.to_dict()
        else:
            res.is_successful_solve = False
            res.error_message = f"Solver returned non-optimal status: {status.value}"

    except GateExecutionBlockedError as err:
        res.solver_status = "BLOCKED_GATE_C_NOT_AUTHORIZED"
        res.error_message = str(err)
        res.runtime_seconds = round(time.perf_counter() - t_start, 4)
        raise

    except Exception as err:
        res.solver_status = "EXECUTION_ERROR"
        res.error_message = f"{type(err).__name__}: {str(err)}"
        res.runtime_seconds = round(time.perf_counter() - t_start, 4)

    return res


# ==============================================================================
# 6. BATCH RUNNER ORCHESTRATION & OUTPUT CONFINEMENT
# ==============================================================================

def run_batch_od02_diagnostic(
    manifest: Optional[Sequence[Dict[str, Any]]] = None,
    allow_list: Optional[List[InputManifestItem]] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    mock_optimizer: Optional[Any] = None,
    synthetic_irradiance_by_origin: Optional[Dict[int, List[float]]] = None,
) -> Dict[str, Any]:
    """
    Executes or plans batch diagnostic across the 10 verified 2024-EVEN origins.
    
    FIREWALL GUARANTEE:
    Unless Gate C is authorized (or a test mock optimizer is provided in unit tests),
    this function strictly raises GateExecutionBlockedError before any solver call.
    """
    manifest_to_use = list(manifest or VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN)
    allow_list_to_use = list(allow_list or APPROVED_2024_INPUT_ALLOW_LIST)

    # 1. Validate manifest fail-closed
    verify_origin_manifest(manifest_to_use)

    # 2. Validate input files fail-closed via DatasetIngestionFirewall
    firewall = DatasetIngestionFirewall(allow_list_to_use)
    input_hashes = {}
    for item in allow_list_to_use:
        firewall.validate_file(item.file_path)
        input_hashes[item.file_path] = item.expected_sha256

    # 3. Output directory confinement validation
    out_path = Path(output_dir)
    if "2025" in str(out_path).lower() or "blind" in str(out_path).lower():
        raise QuarantineViolationError(f"Fail-closed: output_dir '{output_dir}' violates quarantine.")

    # 4. Enforce Gate C authorization
    assert_gate_c_authorized()

    # 5. Base configuration for GAP19
    base_config: Dict[str, Any] = {
        "battery": {
            "capacity_wh": BATTERY_CAPACITY_WH,
            "min_soc_pct": BATTERY_MIN_SOC_PCT,
            "max_soc_pct": BATTERY_MAX_SOC_PCT,
            "charge_efficiency": 0.92,
            "discharge_efficiency": ETA_DISCHARGE,
            "max_charge_power_w": 50000.0,
            "max_discharge_power_w": 50000.0,
        },
        "diesel": {
            "min_power_w": 10000.0,
            "max_power_w": 100000.0,
            "base_fuel_consumption_l_per_h": 5.0,
            "marginal_fuel_consumption_l_per_wh": 0.00025,
            "startup_fuel_l": 2.0,
        },
        "optimizer": {
            "timestep_hours": 1.0,
        },
        "policy_b": True,
    }

    results: List[DiagnosticOriginResult] = []
    
    # 6. Process origins one at a time
    for origin in manifest_to_use:
        orig_id = origin["forecast_origin"]
        
        # In authoring/mock test mode, synthetic irradiance is supplied
        if synthetic_irradiance_by_origin is not None and orig_id in synthetic_irradiance_by_origin:
            raw_irr = synthetic_irradiance_by_origin[orig_id]
        else:
            # Polar day / shoulder / night default profile for mock evaluation
            if origin["stratum"] == "REGIME_A_POLAR_DAY":
                raw_irr = [500.0] * 24
            elif origin["stratum"] == "REGIME_C_POLAR_NIGHT":
                raw_irr = [0.0] * 24
            else:
                raw_irr = [300.0 if 6 <= h <= 18 else 0.0 for h in range(24)]

        orig_res = execute_single_origin_diagnostic(
            origin=origin,
            raw_irradiance_24h=raw_irr,
            config=base_config,
            mock_optimizer=mock_optimizer,
        )
        orig_res.input_hashes = dict(input_hashes)
        results.append(orig_res)

    # 7. Build summary payload
    summary_payload = {
        "tracking_id": RUNNER_TRACKING_ID,
        "mdr_version": MDR_CANONICAL_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_origins": len(results),
        "successful_solves": sum(1 for r in results if r.is_successful_solve),
        "failed_solves": sum(1 for r in results if not r.is_successful_solve),
        "origins": [r.to_dict() for r in results],
    }

    # Write output to confined directory if authorized
    out_path.mkdir(parents=True, exist_ok=True)
    out_file = out_path / "od02_boundary_diagnostic_summary.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    return summary_payload


if __name__ == "__main__":
    print(f"[{RUNNER_TRACKING_ID}] POLARIS OD-02 Boundary Diagnostic Batch Runner")
    print(f"MDR Governance: v{MDR_CANONICAL_VERSION}")
    print("Pre-execution check: Evaluating Gate C authorization...")
    try:
        assert_gate_c_authorized()
    except GateExecutionBlockedError as e:
        print(f"\n[BLOCKED] {e}")
        print("Gate C execution is NOT authorized. Runner exiting safely without side effects.")
        sys.exit(0)
