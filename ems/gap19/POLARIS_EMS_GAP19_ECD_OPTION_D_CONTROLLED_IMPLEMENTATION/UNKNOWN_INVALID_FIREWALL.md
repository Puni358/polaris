# POLARIS EMS GAP19 — UNKNOWN_INVALID Firewall Report

## Governance Boundary & Runtime Status

```
UNKNOWN_INVALID_ROUTER_CLASSIFICATION =
    AUTHORIZED

UNKNOWN_INVALID_RUNNER_OPERATIONAL_ACTION =
    NOT_IMPLEMENTED

UNKNOWN_INVALID_RUNTIME_INTERFACE =
    ENGINEERING_INTERFACE_BLOCKER

UNKNOWN_INVALID_OPERATIONAL_ACTION =
    NOT_ESTABLISHED
```

## Immutable Policy Rules

- `UNKNOWN_INVALID` is distinct from `NORMAL` and distinct from `EMERGENCY`.
- `UNKNOWN_INVALID` states **MUST NOT** enter Option B.
- `UNKNOWN_INVALID` states **MUST NOT** enter Option D.
- The implementation does **NOT** silently invent:
  - Termination / `FAILED_TERMINATED`
  - Shutdown
  - Zero-dispatch
  - Hold-last-plan
  - Generator start
  - Load shedding
- Execution stops at the `ENGINEERING_INTERFACE_BLOCKER` boundary.
