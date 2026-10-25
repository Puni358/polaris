# INTEGRATION RISK MATRIX

## 1. TECHNICAL RISK CLASSIFICATION & MITIGATION MATRIX

Every gap identified in the audit was classified by technical risk category and severity.

| Identified Architectural Gap | Technical Risk Category | Severity | Technical Impact | Governed Mitigation Action |
| :--- | :--- | :--- | :--- | :--- |
| **Ground Truth Leakage** | `truth_leakage` | **CRITICAL** | Controller accesses future actuals $t+1..t+24$ | Maintain strict provider isolation in `runner.py` |
| **Demand Field Repurposing** | `semantic_mismatch` | **HIGH** | Overwriting `demand.point` with critical demand breaks total accounting | Enforce additive `critical_demand` field in `ForecastBundle` |
| **Fuel Inventory Absence** | `runtime_absence` | **HIGH** | Generator runs without fuel depletion tracking in simulator | Add `fuel_remaining_liters` to `StationState` & simulator |
| **ECD Disconnected from Runner** | `runtime_absence` | **HIGH** | Operating mode classification bypassed completely | Wire `ECD.evaluate()` directly inside `runner.py` loop |
| **Option D Policy Layer Missing** | `policy_mismatch` | **HIGH** | MILP ignores Option D rules (e.g. battery critical-only) | Implement lightweight Policy Router preprocessor |
| **Unit Scaling Mismatch (kW vs W)**| `numerical_mismatch` | **MEDIUM** | $1000\times$ magnitude error in energy calculations | Enforce unit scaling ($kW \times 1000 \to W$) in provider |
| **Scalar vs Lexicographic Objective**| `policy_mismatch` | **MEDIUM** | Optimizer optimizes cost instead of strict 4-stage hierarchy | Maintain Objective Firewall; bound claims |
| **`UNKNOWN_INVALID` Unhandled** | `recovery_gap` | **MEDIUM** | Pipeline crashes on malformed telemetry instead of safe-state | Implement fail-closed zero-dispatch fallback |
| **$P_{\text{max}}$ Generator Discrepancy**| `numerical_mismatch` | **LOW** | Config specifies $100$ kW vs fixture $60$ kW | Report discrepancy; non-blocking for $45$ kW max demand |

---

## 2. RISK CATEGORY DEFINITION
- **CRITICAL**: Risk of scientific contamination or invalidation of research claims.
- **HIGH**: Functional execution failure or silent corruption of governed state logic.
- **MEDIUM**: Sub-optimal optimization behavior or interface mismatch.
- **LOW**: Discrepancy in documentation or non-binding configuration bounds.
