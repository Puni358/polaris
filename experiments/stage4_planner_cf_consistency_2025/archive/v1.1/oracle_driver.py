"""
ORACLE audit driver (EXP-PLANNER-CF-CONSISTENCY-2025, §6.2, §6.6, §7 G1/G12, NG7, NG11).

Runs ORACLE-PHYS (NG7 oracle, reserve-free) and ORACLE-CTRL (secondary diagnostic) over the
123 preregistered origins, then feeds their outputs to the G1 and G12 audits through
oracle_audit_adapter.

Rules enforced here:
  - Explicit authorization is required (`authorized=True`). Otherwise PermissionError.
  - §9 protected hashes are verified before any oracle run.
  - G12 runs first. If any origin is blocked, no oracle run is interpreted and the driver
    returns BLOCKED (NG11). Blocked origins are never silently dropped.
  - An exception in any origin run is recorded as BLOCKED with the error. It is not skipped.
  - G1 is applied to ORACLE-PHYS only. Its failure is NG1 and is reported, not repaired.
  - NG7 is decided only from ORACLE-PHYS vs PC-Control fuel, and only when the campaign
    result is supplied. ORACLE-CTRL neither triggers nor cancels NG7.

Campaign candidate/control runs are not executed here.
"""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
for _p in (str(REPO), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import oracle_runner as oracle  # noqa: E402
import oracle_audit_adapter as oaa  # noqa: E402
from planner_cf_hash_guards import verify_protected_hashes  # noqa: E402

OUT_DIR = _HERE
TARGET_SAVING_PCT = 40.0
NG7_REACHABLE_THRESHOLD_PCT = TARGET_SAVING_PCT


def ng7_decision(oracle_phys_fuel_L: float, pc_control_fuel_L: float) -> Dict[str, Any]:
    """NG7: ORACLE-PHYS saving vs PC-Control < 40% => NOT REACHABLE (NO-GO for the 40% target)."""
    if pc_control_fuel_L <= 0.0:
        raise ValueError("PC-Control fuel must be positive")
    saving = 100.0 * (pc_control_fuel_L - oracle_phys_fuel_L) / pc_control_fuel_L
    reachable = saving >= NG7_REACHABLE_THRESHOLD_PCT
    return {"oracle_phys_saving_pct": saving, "NG7_TRIGGERED": not reachable,
            "status": "REACHABLE_IN_PRINCIPLE" if reachable else "NOT REACHABLE under physics and customer-first priorities"}


def _flatten(pairs: Sequence[Tuple[int, Any]], variant: str) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for oi, res in pairs:
        if res.variant != variant:
            continue
        for h in res.hourly:
            rows.append(dict(h, origin_id=int(oi), variant=variant))
    return pd.DataFrame(rows)


def run_oracle_audit(*, authorized: bool = False, out_dir: Optional[Path] = None,
                     repo: Path = REPO,
                     origins_fn: Callable[[], List[pd.Timestamp]] = oracle.origins_2025_may_aug,
                     lookup_fn: Callable[[], Dict[str, float]] = oracle.load_sw_in_lookup,
                     campaign_pc_control_fuel_L: Optional[float] = None) -> Dict[str, Any]:
    if not authorized:
        raise PermissionError("oracle execution requires explicit authorization (preregistration §14)")
    mismatches = verify_protected_hashes(repo)
    if mismatches:
        return {"status": "BLOCKED", "reason": "hash guards failed", "details": mismatches}

    origins = origins_fn()
    lookup = lookup_fn()
    g12 = oaa.g12_for_oracle(origins, lookup.keys())
    if not g12["PASS"]:
        return {"status": "BLOCKED", "reason": "G12 SITES coverage failed (NG11)",
                "g12": g12, "NG7": "cannot be established"}

    pairs: List[Tuple[int, Any]] = []
    errors: List[Dict[str, Any]] = []
    for idx, o in enumerate(origins, start=1):
        for variant in oracle.ORACLE_VARIANTS:
            try:
                pairs.append((idx, oracle.run_oracle_origin(o, variant, idx, lookup=lookup)))
            except Exception as e:  # recorded, never skipped silently
                errors.append({"origin_id": idx, "variant": variant, "error": f"{type(e).__name__}: {e}"})

    if errors:
        return {"status": "BLOCKED", "reason": "oracle run errors (not skipped)", "errors": errors, "g12": g12}

    g1 = oaa.g1_for_oracle(pairs, oaa.ORACLE_PHYS)
    phys = _flatten(pairs, oaa.ORACLE_PHYS)
    ctrl = _flatten(pairs, oaa.ORACLE_CTRL)
    phys_fuel = float(phys["fuel_l"].sum()) if len(phys) else float("nan")
    ctrl_fuel = float(ctrl["fuel_l"].sum()) if len(ctrl) else float("nan")

    result: Dict[str, Any] = {
        "status": "COMPLETE" if g1["PASS"] else "G1_FAIL_NG1",
        "g12": g12,
        "G1_ORACLE_PHYS": g1,
        "oracle_phys_fuel_L": phys_fuel,
        "oracle_ctrl_fuel_L": ctrl_fuel,
        "origins": len(origins),
    }
    if campaign_pc_control_fuel_L is not None:
        result["NG7"] = ng7_decision(phys_fuel, campaign_pc_control_fuel_L)

    target = Path(out_dir) if out_dir is not None else OUT_DIR
    target.mkdir(parents=True, exist_ok=True)
    phys.to_csv(target / "ORACLE_PHYS_HOURLY.csv", index=False)
    ctrl.to_csv(target / "ORACLE_CTRL_HOURLY.csv", index=False)
    with open(target / "ORACLE_AUDIT_REPORT.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    return result
