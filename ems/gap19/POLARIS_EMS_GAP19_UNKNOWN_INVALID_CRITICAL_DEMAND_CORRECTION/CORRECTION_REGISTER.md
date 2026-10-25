# Correction Register

| Issue | Actual Code Behavior | Governance Status | Classification | A/B Impact |
| :--- | :--- | :--- | :--- | :--- |
| `UNKNOWN_INVALID` | Bypasses solver, returns zero-dispatch `DispatchPlan` | `IMPLEMENTATION_ONLY_NOT_GOVERNED` | `BYPASS_OPTIMIZATION_FAILSAFE_DISPATCHPLAN` | Excluded from solver math domain |
| `1e9` Sentinel | Returned in `DispatchPlan.objective_value` | Reporting sentinel | `REPORTING_ONLY` | Zero impact on MILP objectives |
| Critical-Demand Fallback | Defaults `critical_demand` to total `demand` | `IMPLEMENTATION_ONLY_NOT_GOVERNED` | `DEFAULT_TO_TOTAL_DEMAND` | Resolved by explicit test contract |
| Total vs Critical Semantics | Not semantically equivalent | `NOT_ESTABLISHED` | `SEMANTIC_EQUIVALENCE_NOT_ESTABLISHED` | Quarantined via explicit inputs |
| Option D Interaction | Fail-closed guard, not active Option D dispatch | `IMPLEMENTATION_FALLBACK_NOT_OPTION_D` | `INTERFACE_ONLY` | None in `NORMAL` mode |
