"""
Input, population, configuration and solver-settings manifests for the global lower bound
(EXP-PLANNER-CF-CONSISTENCY-2025, Study 1 governance).

Generation only. This module computes hashes from records that are passed in. It never reads real
data and never writes a manifest file. Real hashes are frozen only immediately before AGY
authorization, by an explicit call made outside this module.
"""

import hashlib
import json
from typing import Any, Dict, List, Sequence

import highspy

import global_lower_bound as g
from global_lower_bound_loader import OriginRecord, N_ORIGINS, HOURS

SOLVER_SETTINGS = {
    "solver": "HiGHS (highspy)",
    "threads": 1,
    "output_flag": False,
    "mip_rel_gap": 1e-9,
    "time_limit_s": g.TIME_LIMIT_S,   # K7: 60 s per origin (governance decision)
    "gap_limit_l_absolute": g.GAP_LIMIT_L,
}


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def input_schema(records: Sequence[OriginRecord]) -> List[Dict[str, Any]]:
    """Canonical per-origin input table used for the input hash."""
    return [{
        "origin_index": r.origin_index,
        "forecast_start": r.forecast_start,
        "timestamps": r.timestamps,
        "solar_w": [round(float(v), 9) for v in r.solar_w],
        "wind_w": [round(float(v), 9) for v in r.wind_w],
        "demand_w": [round(float(v), 9) for v in r.demand_w],
        "critical_w": [round(float(v), 9) for v in r.critical_w],
        "noncritical_w": [round(float(v), 9) for v in r.noncritical_w],
        "initial_state": r.initial_state,
    } for r in records]


def input_hash(records: Sequence[OriginRecord]) -> str:
    return sha256_bytes(canonical_json(input_schema(records)))


def population_manifest(records: Sequence[OriginRecord]) -> Dict[str, Any]:
    if len(records) != N_ORIGINS:
        raise ValueError(f"population manifest requires {N_ORIGINS} origins, got {len(records)}")
    for r in records:
        if len(r.solar_w) != HOURS:
            raise ValueError("each origin must have 24 hours")
    rows = [{"origin_index": r.origin_index, "forecast_start": r.forecast_start} for r in records]
    return {
        "n_origins": len(records),
        "hours_per_origin": HOURS,
        "origins": rows,
        "population_hash": sha256_bytes(canonical_json(rows)),
    }


def configuration_hash() -> str:
    return g.config_hash()


def solver_settings_hash() -> str:
    settings = dict(SOLVER_SETTINGS, highspy_version=str(getattr(highspy, "__version__", "unknown")))
    return sha256_bytes(canonical_json(settings))


def build_manifest(records: Sequence[OriginRecord], code_hashes: Dict[str, str]) -> Dict[str, Any]:
    """Assembles the manifest in memory. Callers decide whether to persist it."""
    return {
        "population": population_manifest(records),
        "input_hash": input_hash(records),
        "configuration_hash": configuration_hash(),
        "solver_settings": dict(SOLVER_SETTINGS),
        "solver_settings_hash": solver_settings_hash(),
        "code_hashes": dict(code_hashes),
        "frozen": False,
        "note": "generated from supplied records; real hashes frozen only immediately before AGY authorization",
    }
