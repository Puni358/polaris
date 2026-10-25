# IMPLEMENTATION STRATEGY CORRECTION

## 1. CLARIFICATION OF STRATEGY 2 PRE-GAP19 BOUNDARIES

The audit clarified the precise meaning of recommending **Strategy 2** (implementing interfaces, ECD wiring, Option D policy router, and 21-variable MILP constraints prior to GAP19 solver deployment).

---

## 2. BOUNDARY CLARIFICATION

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 SAFE PRE-GAP19 IMPLEMENTATION (Strategy 2)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Additive Schemas (ForecastBundle.critical_demand, StationState.fuel)     │
│ 2. SyntheticFixtureProvider Adapter                                         │
│ 3. ECD Runner Wiring in runner.py                                           │
│ 4. OptionDPolicyLayer generating ModeConstraintSet                          │
│ 5. 21-Variable Linear Constraint Formulation in MILP                        │
│ 6. SafeStateFallbackRouter for UNKNOWN_INVALID                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  MUST WAIT FOR GAP19 SOLVER ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Native HiGHS C++ Sequential Lexicographic Optimization                   │
│ 2. Exact GAP19 Stage 1..4 Pareto Objective Logging                          │
│ 3. Final Multi-Objective Tradeoff Balancing                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. SUMMARY
- Recommending Strategy 2 does **NOT** imply implementing the final GAP19 multi-stage solver today.
- It implements the complete, solver-neutral Option D constraint infrastructure today under SciPy HiGHS MILP, leaving the GAP19 multi-stage solver integration for Phase 7.
