# MILP Infeasibility ECD Routing Audit

## Forensic Audit Baseline & Rejection of Defect
The multi-scenario stress forensic audit established:
1. `RUNTIME_INFEASIBILITY_HANDLING = DEFECT` in historical implementation.
2. `ZERO_DISPATCH_AS_FINAL_GOVERNED_RESPONSE = REJECTED`.

## Governed Target Pathway vs Current Implemented Path

### Current Implemented Path (In `runner.py`):
```text
EnergyOptimizer returns OPTIMIZATION_INFEASIBLE
  ↓
FaultEvent (GOVERNED_DEGRADED, GOVERNED_ZERO_DISPATCH)
  ↓
Simulator executes zero dispatch (State advances, load drops to 0)
```
*(Status: HISTORICAL DEFECT — TO BE REPLACED)*

### Governed Target Pathway:
```text
EnergyOptimizer status == OPTIMIZATION_INFEASIBLE
  ↓
Status passed as input signal to ECD / Emergency Assessment Pathway
  ↓
ECD evaluates physical survivability from actual StationState
  ↓
Is operating_mode == EMERGENCY?
  ├── YES: EMS Router activates Option D Protected Critical-Load Fallback.
  └── NO: Solver infeasibility under NORMAL mode triggers governed degraded solver fallback (without declaring false emergency).
```

---

## Interface Requirements
1. `EnergyOptimizer` returns `constraint_status`.
2. Router intercepts `constraint_status == OPTIMIZATION_INFEASIBLE`.
3. Status is passed into ECD telemetry assessment context.
4. `ZERO_DISPATCH` is **NEVER** executed as a final response.
