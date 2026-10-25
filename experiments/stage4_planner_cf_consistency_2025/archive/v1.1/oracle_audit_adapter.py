"""
Oracle-output adapter for the G1 and G12 audits (EXP-PLANNER-CF-CONSISTENCY-2025, §6.2, §7, §16.3).

Converts ORACLE-PHYS / ORACLE-CTRL run results (oracle_runner.OracleOriginResult) into the frame
shapes that planner_cf_audit_gates.g1_realizability and g12_oracle_coverage expect.

Pure functions. No oracle run is started here. G12 takes the SITES key set as an argument, so the
caller decides the source. The campaign driver supplies the authoritative file.
"""

from typing import Any, Dict, Iterable, List, Sequence, Tuple

import pandas as pd

import planner_cf_audit_gates as gates

ORACLE_PHYS = "ORACLE-PHYS"
ORACLE_CTRL = "ORACLE-CTRL"


def oracle_frames(pairs: Iterable[Tuple[int, Any]], variant: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """(origin_index, OracleOriginResult) pairs -> (realized hourly frame, executed-hour frame).

    Realized frame columns: origin_id, hour, arm, battery_charge (realized charge, W).
    Executed frame: the planner's executed-hour records (planned_charge_w, ...), for that variant.
    """
    realized: List[Dict[str, Any]] = []
    executed: List[Dict[str, Any]] = []
    for origin_index, res in pairs:
        if res.variant != variant:
            continue
        for h in res.hourly:
            realized.append({"origin_id": int(origin_index), "hour": int(h["step"]), "arm": variant,
                             "battery_charge": float(h["charge_w"])})
        for e in res.executed:
            executed.append(dict(e, origin_id=int(origin_index)))
    return pd.DataFrame(realized), pd.DataFrame(executed)


def g1_for_oracle(pairs: Sequence[Tuple[int, Any]], variant: str = ORACLE_PHYS) -> Dict[str, Any]:
    """G1 realizability for one oracle variant. NG1 applies to ORACLE-PHYS (the NG7 oracle)."""
    realized, executed = oracle_frames(pairs, variant)
    out = gates.g1_realizability(realized, executed)
    out["variant"] = variant
    out["origins"] = int(executed["origin_id"].nunique()) if len(executed) else 0
    return out


def g12_for_oracle(origins: Sequence[pd.Timestamp], sites_keys: Iterable[str]) -> Dict[str, Any]:
    """G12 SITES coverage. sites_keys: 'YYYY-MM-DD HH:MM:SS' keys of the authoritative SITES file."""
    out = gates.g12_oracle_coverage(origins, sites_keys)
    out["n_origins"] = len(origins)
    return out


def g7_repeat_origin(origins: Sequence[pd.Timestamp]) -> int:
    """Deterministic G7 repeat origin (§16.3): the earliest origin in the sorted population, index 1.
    It is chosen before any result exists and does not depend on outcomes."""
    ordered = sorted(origins)
    if not ordered:
        raise ValueError("empty origin population")
    return 1
