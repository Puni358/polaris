# Exact Normal Path (Option B HiGHS) Interface Contract

## Target Architecture Context
```text
StationState & ForecastBundle
  ↓
ECD Evaluator Core
  ↓
EMS Control Router (operating_mode == NORMAL)
  ↓
GAP19HighsNativeOptimizer.optimize(bundle, current_state, configs)
  ↓
DispatchPlan (Option B Lexicographic Order)
```

## Existing Unmodified Optimizer Signature
- **Class**: `GAP19HighsNativeOptimizer` (`system/optimization/implementations/gap19_highs_native.py`)
- **Method Signature**: `optimize(bundle: ForecastBundle, current_state: StationState, configs: Dict[str, Any]) -> DispatchPlan`

## Objective Hierarchy Guarantees (Protected & Unchanged)
The future router sits **AROUND** the normal MPC path and strictly preserves:
1. **$J1$ Priority**: Critical Reliability ($u_k = 0$, zero unmet demand).
2. **$J2$ Priority**: Governed Emergency Reserve Shortfall Penalty ($s_{J2} \ge 0$).
3. **$J3$ Priority**: Diesel Fuel & Operational Minimization.
4. **$J4$ Priority**: Renewable Utilization / Curtailment Minimization.
5. **Horizons**: 24-hour forecast horizon, 24-hour decision horizon, 6-hour EBR horizon.
