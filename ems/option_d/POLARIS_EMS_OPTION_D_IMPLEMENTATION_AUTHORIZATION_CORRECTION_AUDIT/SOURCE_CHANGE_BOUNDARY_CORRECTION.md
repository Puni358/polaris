# SOURCE CHANGE BOUNDARY CORRECTION

## Re-Audited Source Change Classification Matrix

This document provides the re-audited, corrected file impact classification for all repository files.

---

## Corrected File Classification Table

| File Path | Original Status | Corrected Status | Reason for Reclassification |
| :--- | :--- | :--- | :--- |
| `system/schemas/state.py` | `MUST_MODIFY` | `MUST_MODIFY` | Mandatory additive optional fields for critical/flexible load split. |
| `system/schemas/forecast.py` | `MUST_MODIFY` | `MUST_MODIFY` | Mandatory additive optional fields for forecasted critical load. |
| `system/schemas/dispatch.py` | `MUST_MODIFY` | `MUST_MODIFY` | Mandatory additive optional fields for $\alpha(t)$ and critical served reporting. |
| `system/runtime/runner.py` | `MUST_MODIFY` | `MUST_MODIFY` | Mandatory wiring of frozen ECD and policy layer into execution loop. |
| `system/optimization/implementations/milp.py` | `MAY_MODIFY` | `MAY_MODIFY` | Proposed pre-GAP19 21-variable constraint formulation. |
| `system/simulation/simulator.py` | `MUST_MODIFY` | `MAY_MODIFY_AFTER_SEPARATE_AUTHORIZATION` | **RECLASSIFIED**: Static source audit showed fuel level tracking is not present in existing simulator. |
| `system/control/ecd.py` | `MUST_NOT_MODIFY` | `MUST_NOT_MODIFY` | Core logic frozen, fully verified, and reusable as-is. |
| `system/forecasting/` | `MUST_NOT_MODIFY` | `MUST_NOT_MODIFY` | Isolated by Forecasting Firewall. |
| `system/data/` | `MUST_NOT_MODIFY` | `MUST_NOT_MODIFY` | Isolated by Synthetic Production Firewall. |
| Production Config & Keys | `MUST_NOT_MODIFY` | `MUST_NOT_MODIFY` | Production security open. |

---

## Corrected Category Totals

- **`MUST_MODIFY`**: 4 files (`state.py`, `forecast.py`, `dispatch.py`, `runner.py`).
- **`MAY_MODIFY`**: 1 file (`milp.py` — Proposed pre-GAP19 formulation).
- **`MAY_MODIFY_AFTER_SEPARATE_AUTHORIZATION`**: 1 file (`simulator.py` — Reclassified from MUST_MODIFY).
- **`MUST_NOT_MODIFY`**: All other repository files.
