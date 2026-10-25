# FAILURE MODE TEST

## Solver Failure Handling & Exception Audit

This document records the empirical failure mode tests on `highspy`.

---

## Failure Mode Test Cases

| Test Case | Injected Invalid Condition | Programmatic Response | Process Stability |
| :--- | :--- | :--- | :--- |
| **Test A: Infeasible Constraints** | $x_1 \ge 5$, $x_1 \le 2$ | `h.getModelStatus() == HighsModelStatus.kInfeasible` | **Stable** (No crash) |
| **Test B: Invalid Objective Index** | `h.getLinearObjective(99)` | Returns `HighsLinearObjective` with empty arrays | **Stable** (No crash) |
| **Test C: Unbounded Model** | Maximize $x_1$ with no upper bound | `h.getModelStatus() == HighsModelStatus.kUnbounded` | **Stable** (No crash) |

---

## Audit Verdict

```text
FAILURE_MODE_HANDLING = STABLE_PROGRAMMATIC_RETURNS
```
`highspy` handles infeasibility, unboundedness, and out-of-bound requests programmatically through status codes and return objects without crashing the Python interpreter.
