"""Import paths and safety fixtures for EXP-THREE-ARM-2024 tests.

Adds the repo root (for `system.*`), this package's scripts/ folder, and the folder holding the
unmodified EBR adapter. No data is read here.

Every test runs with the solver interfaces replaced by mocks that fail immediately if called:
  - highspy.Highs (the only solver entry point of Planner-CF v1, imported inside optimize());
  - run_three_arm_2024.load_planner_class (returns a class whose construction and optimize() raise);
  - PlannerCFV1Optimizer.optimize, if that module is already imported.
A test that reaches any of them fails with SolverCalled.
"""
import sys
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parents[1]
_REPO = _PKG.parents[1]
for p in (_REPO, _PKG / "scripts", _REPO / "experiments" / "stage4_sw_low_sun_2025_holdout"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


class SolverCalled(AssertionError):
    """Raised when a preparation test reaches a solver interface."""


def _forbidden(*_a, **_k):
    raise SolverCalled("a solver interface was called during a preparation test")


class ForbiddenPlanner:
    def __init__(self, *_a, **_k):
        _forbidden()

    def optimize(self, *_a, **_k):
        _forbidden()


@pytest.fixture(autouse=True)
def no_solver(monkeypatch):
    try:
        import highspy
        monkeypatch.setattr(highspy, "Highs", _forbidden)
    except ImportError:
        pass
    import run_three_arm_2024 as r
    monkeypatch.setattr(r, "load_planner_class", lambda: ForbiddenPlanner)
    mod = sys.modules.get("research_numerical_extractor_planner_cf_v1")
    if mod is not None:
        monkeypatch.setattr(mod.PlannerCFV1Optimizer, "optimize", _forbidden)
    yield
