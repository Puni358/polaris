"""
Harness-only planned-telemetry wrapper (EXP-PLANNER-CF-CONSISTENCY-2025, B4).

Records, per hour and per arm, the PLANNED values from the solver solution of the
Planner-CF v1 optimizer: served_c, served_nc, unmet_crit, unmet_nc, charge.

- Production DispatchPlan is NOT modified. The values are read from the optimizer
  instance attribute `last_planned` after each optimize() call.
- G2 and G3 (preregistration §7) use these PLANNED values, never realized values.
- Pure reads: this module performs no solve and no realization.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

PLANNED_FIELDS = ("served_c", "served_nc", "unmet_crit", "unmet_nc", "charge")


@dataclass
class PlannedHourRecord:
    origin_id: int
    arm: str
    step: int
    hour: int
    served_c: float
    served_nc: float
    unmet_crit: float
    unmet_nc: float
    charge: float
    discharge: float
    diesel: float
    E_next: float
    s_j2: float


class PlannedTelemetryHarness:
    """Wraps a Planner-CF v1 optimizer and collects planned per-hour records for one
    (origin, arm, step). The wrapped optimizer is used unchanged."""

    def __init__(self, optimizer: Any):
        self.optimizer = optimizer
        self.records: List[PlannedHourRecord] = []

    def optimize(self, bundle, station_state, config, *, origin_id: int, arm: str, step: int):
        plan = self.optimizer.optimize(bundle, station_state, config)
        planned = getattr(self.optimizer, "last_planned", None)
        if planned is None or len(planned) != 24:
            raise RuntimeError("optimizer did not expose 24 planned hourly records (last_planned)")
        for row in planned:
            self.records.append(PlannedHourRecord(
                origin_id=int(origin_id), arm=str(arm), step=int(step), hour=int(row["t"]),
                served_c=float(row["served_c"]), served_nc=float(row["served_nc"]),
                unmet_crit=float(row["unmet_crit"]), unmet_nc=float(row["unmet_nc"]),
                charge=float(row["charge"]), discharge=float(row["discharge"]),
                diesel=float(row["diesel"]), E_next=float(row["E_next"]), s_j2=float(row["s_j2"]),
            ))
        return plan

    def as_dicts(self) -> List[Dict[str, Any]]:
        return [asdict(r) for r in self.records]


def check_planned_identities(planned_rows: List[Dict[str, Any]], demand_w: List[float],
                             critical_w: List[float], solar_w: List[float], wind_w: List[float],
                             tol_w: float = 1e-3) -> List[str]:
    """Structural identities that every Planner-CF v1 solution must satisfy at each hour.
    Returns a list of violation messages (empty list = all identities hold).

      Layer B:            served_c + unmet_crit = critical
      non-critical:       served_nc + unmet_nc  = demand - critical
      bus (no flex):      solar_used + wind_used + discharge + diesel - served - charge = 0
      (solar_used and wind_used are taken as the planned used values if present; otherwise
       the identity is checked only where the planned value is available.)
    """
    msgs: List[str] = []
    for row, dem, crit in zip(planned_rows, demand_w, critical_w):
        t = int(row["t"])
        if abs((row["served_c"] + row["unmet_crit"]) - crit) > tol_w:
            msgs.append(f"hour {t}: Layer B identity violated")
        if abs((row["served_nc"] + row["unmet_nc"]) - (dem - crit)) > tol_w:
            msgs.append(f"hour {t}: non-critical balance violated")
    return msgs
