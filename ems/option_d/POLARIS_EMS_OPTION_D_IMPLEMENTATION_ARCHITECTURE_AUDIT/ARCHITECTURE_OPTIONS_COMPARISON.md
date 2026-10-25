# ARCHITECTURE OPTIONS COMPARISON

## 1. COMPARISON OF CANDIDATE ARCHITECTURES (OPTIONS A THROUGH E)

The audit systematically evaluated five candidate architectural placements for SEALED DEC-004 Option D within the POLARIS runtime pipeline.

```text
OPTION A: ECD → Option D Policy Layer → Modified Optimizer Inputs → Existing EnergyOptimizer
OPTION B: ECD → Dedicated Emergency Heuristic Dispatcher → DispatchPlan
OPTION C: ECD → Operating Mode → Single EnergyOptimizer (Mode-dependent internal logic)
OPTION D: ECD → Policy Layer → Mode Constraint Set → Common EnergyOptimizer → Common DispatchPlan
OPTION E: Hybrid (Option D + Safe-State Zero-Dispatch Fallback Router)
```

---

## 2. EVALUATION MATRIX ACROSS 11 ARCHITECTURAL CRITERIA

| Evaluation Criterion | Option A | Option B | Option C | Option D | Option E (Recommended) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Semantic Cleanliness** | Poor (distorts demand input) | High (isolated dispatcher) | Medium (blurs policy & solver) | **High** (clean abstraction) | **Highest** (clean + safe fallback) |
| **2. Architectural Compatibility** | High | Low (bypasses solver) | Medium | **High** | **Highest** (matches runner pipeline) |
| **3. GAP19 Solver Compatibility** | Low (distorts objective) | Zero (bypasses solver) | Medium (solver-tied) | **High** (solver-neutral) | **Highest** (100% solver-neutral) |
| **4. Code Reuse** | High | Low (duplicate physics) | Medium | **High** (reuses MILP engine) | **High** (reuses MILP + safe fallback) |
| **5. Schema Impact** | None | High | Medium | **Minimal Additive** | **Minimal Additive** |
| **6. Testing Complexity** | Medium | High (dual dispatchers) | High (complex solver states)| **Low** (isolated contract) | **Low** (isolated contract) |
| **7. Duplicate Logic Risk** | Low | **CRITICAL** (duplicate physics)| Medium | **Zero** | **Zero** |
| **8. Policy/Optimizer Leakage** | **HIGH** (leaks policy into data) | None | **HIGH** (hardcoded in solver) | **Zero** (clean constraint set) | **Zero** (clean constraint set) |
| **9. Future Rewrite Risk** | High | High | High | Low | **Zero** |
| **10. Option D Exactness** | Partial | High | Partial | **Exact** | **Exact** |
| **11. Normal Mode Preservation**| Risk of side effects | Perfect | Risk of side effects | **Guaranteed** | **Guaranteed** |

---

## 3. RATIONALE AGAINST REJECTED OPTIONS

### Why Option B (Dedicated Heuristic Dispatcher) Was Rejected:
- Option B bypasses mathematical optimization during emergency modes and relies on a hardcoded rule-based heuristic dispatcher.
- **Flaws**:
  1. Duplicates physical energy balance, battery state-of-charge, generator efficiency, and loss equations already present in `EnergyOptimizer`.
  2. Sub-optimal dispatch during complex emergency states where battery charging from diesel excess must be mathematically optimized across 24 receding horizon timesteps.
  3. Creates a permanent dual-dispatcher codebase that must be maintained separately.

### Why Option C (Hardcoding Option D inside MILP) Was Rejected:
- Option C embeds Option D policy rules directly inside the `LocalMILPEnergyOptimizer` python class via mode flags.
- **Flaws**:
  1. Pollutes the mathematical solver engine with domain-specific operating policy logic.
  2. Binds Option D rules tightly to SciPy / HiGHS solver data structures, making future solver replacement (GAP19 native HiGHS C++ API or Gurobi) extremely fragile and costly.
  3. Risk of normal-mode regression if internal constraint branches are mutated.
