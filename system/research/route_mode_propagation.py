"""
Research-harness route-mode propagation.

The router (system/control/router.py: EMSControlRouter.evaluate_and_route) assesses
NORMAL / EMERGENCY / UNKNOWN_INVALID and returns it as route_mode. The research
closed-loop runners previously passed the unchanged StationState to the optimizer,
whose operating_mode is only ever initialised to NORMAL and carried forward by the
realization executor. The EMERGENCY-only MILP constraint therefore never activated.

propagate_route_mode() returns a planning copy of the station state whose
operating_mode is the router's assessed route. The realization state chain is
untouched: the caller keeps using the original state for execution.
"""

import copy
from typing import Any


def propagate_route_mode(station_state: Any, route_mode: str) -> Any:
    """Return a shallow planning copy of station_state with operating_mode = route_mode."""
    planning_state = copy.copy(station_state)
    planning_state.operating_mode = str(route_mode).upper()
    return planning_state
