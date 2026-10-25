"""
Harness-only executed-hour planned telemetry and G2/G3 evaluator (EXP-PLANNER-CF-CONSISTENCY-2025, §7).

Each re-solve produces a 24-hour plan, but only hour 0 of that plan is executed before the next
re-solve. This module keeps exactly one record per re-solve (the executed hour) and evaluates the
preregistered gates G2 and G3 on those records.

  - Records use PLANNED values from the executed hour (hour 0 of the plan), never lookahead rows.
  - E_t is the realized start-of-hour battery energy: the state passed into the re-solve.
  - G3 uses the preregistered feasibility equation (§7 G3, B5/B7):
        S_avail_t  = PV_realized + W_realized + diesel_planned            (no planned discharge)
        max_dis_t  = min(50,000 W, (E_t - E_min) * eta_dis)
        planned unmet_crit_t > tol  is feasible only if  S_avail_t + max_dis_t < D_c,t

Harness-only. Reads planner outputs; performs no solve and no realization. Production
DispatchPlan is not modified.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence

TOL_W = 1e-3
MAX_DISCHARGE_CAP_W = 50000.0


@dataclass
class ExecutedHourRecord:
    origin_id: int
    arm: str
    step: int                 # re-solve index = realized hour within the origin (0..23)
    plan_hour: int            # hour index inside the 24h plan that was executed (always 0)
    E_t_wh: float             # realized start-of-hour battery energy
    pv_real_w: float
    wind_real_w: float
    planned_diesel_w: float
    d_c_w: float              # realized critical demand for the executed hour
    max_discharge_w: float
    planned_served_c_w: float
    planned_served_nc_w: float
    planned_unmet_crit_w: float
    planned_unmet_nc_w: float
    planned_charge_w: float


class ExecutedHourRecorder:
    """Collects one executed-hour record per re-solve. Does not hold lookahead rows."""

    def __init__(self) -> None:
        self.records: List[ExecutedHourRecord] = []

    def record_resolve(self, *, origin_id: int, arm: str, step: int,
                       planned_rows: Sequence[Dict[str, Any]],
                       e_start_wh: float, pv_real_w: float, wind_real_w: float,
                       d_c_real_w: float, e_min_wh: float, eta_dis: float,
                       max_discharge_cap_w: float = MAX_DISCHARGE_CAP_W) -> ExecutedHourRecord:
        if len(planned_rows) != 24:
            raise ValueError(f"expected 24 planned rows per re-solve, got {len(planned_rows)}")
        row = planned_rows[0]
        if int(row["t"]) != 0:
            raise ValueError("executed row must be plan hour 0")
        max_dis = min(float(max_discharge_cap_w), max(0.0, (float(e_start_wh) - float(e_min_wh)) * float(eta_dis)))
        rec = ExecutedHourRecord(
            origin_id=int(origin_id), arm=str(arm), step=int(step), plan_hour=0,
            E_t_wh=float(e_start_wh), pv_real_w=float(pv_real_w), wind_real_w=float(wind_real_w),
            planned_diesel_w=float(row["diesel"]), d_c_w=float(d_c_real_w), max_discharge_w=float(max_dis),
            planned_served_c_w=float(row["served_c"]), planned_served_nc_w=float(row["served_nc"]),
            planned_unmet_crit_w=float(row["unmet_crit"]), planned_unmet_nc_w=float(row["unmet_nc"]),
            planned_charge_w=float(row["charge"]),
        )
        self.records.append(rec)
        return rec

    def as_dicts(self) -> List[Dict[str, Any]]:
        return [asdict(r) for r in self.records]


def evaluate_g2_g3(records: Sequence[Any], tol_w: float = TOL_W) -> Dict[str, Any]:
    """Deterministic G2/G3 evaluation over executed-hour records (dataclass or dict).

    Records are sorted by (arm, origin_id, step) before evaluation so output order is fixed.
    G2: NOT(planned unmet_nc > tol AND planned charge > tol).
    G3: planned unmet_crit > tol is allowed only if S_avail + max_discharge < D_c.
    """
    def g(r: Any, k: str) -> Any:
        return r[k] if isinstance(r, dict) else getattr(r, k)

    ordered = sorted(records, key=lambda r: (str(g(r, "arm")), int(g(r, "origin_id")), int(g(r, "step"))))
    g2_viol: List[tuple] = []
    g3_viol: List[tuple] = []
    for r in ordered:
        key = (str(g(r, "arm")), int(g(r, "origin_id")), int(g(r, "step")))
        if g(r, "planned_unmet_nc_w") > tol_w and g(r, "planned_charge_w") > tol_w:
            g2_viol.append(key)
        if g(r, "planned_unmet_crit_w") > tol_w:
            s_avail = float(g(r, "pv_real_w")) + float(g(r, "wind_real_w")) + float(g(r, "planned_diesel_w"))
            feasible = (s_avail + float(g(r, "max_discharge_w"))) < float(g(r, "d_c_w"))
            if not feasible:
                g3_viol.append(key)
    return {
        "n_records": len(ordered),
        "g2_violations": g2_viol,
        "g3_violations": g3_viol,
        "G2_PASS": len(g2_viol) == 0,
        "G3_PASS": len(g3_viol) == 0,
    }
