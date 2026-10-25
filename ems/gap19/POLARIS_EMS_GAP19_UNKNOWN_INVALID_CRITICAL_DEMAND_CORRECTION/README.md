# POLARIS EMS GAP19 — UNKNOWN_INVALID & CRITICAL-DEMAND FALLBACK FORENSIC CORRECTION GATE

This package contains the independent forensic governance and implementation audit covering the `UNKNOWN_INVALID` operating mode path and the missing `P_critical_demand` fallback behavior in `GAP19HighsNativeOptimizer` (`system/optimization/implementations/gap19_highs_native.py`).

## Core Audit Summary
1. **UNKNOWN_INVALID Path**: Bypasses optimization entirely, returning a zero-dispatch, fail-closed `DispatchPlan` with `objective_value = 1e9` as a reporting sentinel. It is `IMPLEMENTATION_ONLY_NOT_GOVERNED` and excluded from the solver mathematical equivalence domain.
2. **Critical Demand Fallback Path**: If `critical_demand_w` is missing from `config`, defaults to total station demand (`forecast_bundle.demand.point`). This is `IMPLEMENTATION_ONLY_NOT_GOVERNED`.
3. **A/B Equivalence Contract**: The A/B equivalence experiment must explicitly supply `critical_demand_w` and run under `NORMAL` mode to ensure identical mathematical problem statements for Option A and Option B.

- **Gate Status**: `A_B_EQUIVALENCE_GATE = READY`
- **Implementation Status**: `IMPLEMENTATION_MODIFICATION = NOT_PERFORMED`
