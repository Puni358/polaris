# Implementation & Activation Blocker Register

## 1. Unresolved Governance Blockers
- `GOV-BLK-01`: `UNKNOWN_INVALID_RUNTIME_ACTION` = `NOT_ESTABLISHED` (Requires human policy decision).
- `GOV-BLK-02`: `EMERGENCY_RETURN_POLICY` = `NOT_ESTABLISHED` (Requires human policy decision).

## 2. Unresolved Engineering Design Blockers
- `ENG-BLK-01`: `OPTION_D_HORIZON` = `ENGINEERING_DESIGN_REQUIRED` (1-step vs horizon selection).
- `ENG-BLK-02`: `MILP_INFEASIBILITY_NORMAL_ACTION` = `ENGINEERING_DESIGN_REQUIRED` (Solver infeasibility in NORMAL mode).

## 3. Station Engineering Input Blockers
- `ST-BLK-01`: Target Station Sub-circuit Load Mapping $P_{\text{critical}}(t)$.
- `ST-BLK-02`: Measured Generator Fuel Consumption Curves & Minimum Power Floor.
- `ST-BLK-03`: Measured Battery Usable Wh & Efficiency Curves.
