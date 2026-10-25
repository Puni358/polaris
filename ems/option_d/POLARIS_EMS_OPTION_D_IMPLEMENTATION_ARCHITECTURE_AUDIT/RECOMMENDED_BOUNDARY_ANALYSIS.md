# RECOMMENDED BOUNDARY ANALYSIS

## 1. SELECTED ARCHITECTURE: HYBRID POLICY-DERIVED CONSTRAINT ARCHITECTURE (OPTION E)

The audit selects **Option E (Hybrid Policy-Derived Constraint Transformation + Common EnergyOptimizer + Fail-Closed Safe-State Fallback)** as the single architecturally sound design for POLARIS EMS Option D.

```text
                               ┌────────────────────────┐
                               │     StationState       │
                               └───────────┬────────────┘
                                           │
                                           ▼
┌─────────────────┐             ┌──────────────────────┐
│ ForecastBundle  ├────────────►│ ECD Core Evaluator   │
└────────┬────────┘             └──────────┬───────────┘
         │                                 │
         │                                 ▼  (EmergencyAssessment)
         │                      ┌──────────────────────┐
         │                      │ Option D Policy      │
         │                      │ Transformation Layer │
         │                      └──────────┬───────────┘
         │                                 │
         │                                 ▼  (ModeConstraintSet: NORMAL / OPTION_D / SAFE_STATE)
         │                      ┌──────────────────────┐
         └─────────────────────►│ Common               │
                                │ EnergyOptimizer      │
                                └──────────┬───────────┘
                                           │
                                           ▼  (DispatchPlan)
                                ┌──────────────────────┐
                                │ Safe-State Router /  │
                                │ Fail-Closed Fallback │
                                └──────────┬───────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │ Digital Twin         │
                                └──────────────────────┘
```

---

## 2. SEPARATION OF RESPONSIBILITIES

1. **`EmergencyConditionDetector` (ECD)**: Pure functional evaluator. Inspects telemetry and $T_{\text{required}}$ to produce `EmergencyAssessment` (`operating_mode`, `validity_status`, survivability margins). Zero dispatch logic or constraint generation.
2. **`OptionDPolicyLayer` (Policy Router)**: Decoupled policy preprocessor. Receives `EmergencyAssessment`, `StationState`, and `ForecastBundle`. Transforms mode directives into a solver-neutral `ModeConstraintSet` object.
3. **`EnergyOptimizer` (MILP / GAP19)**: Pure mathematical optimization engine. Receives `ForecastBundle`, `StationState`, and `ModeConstraintSet`. Builds exact MILP constraints and solves the mathematical program. Reused in ALL operating modes.
4. **`SafeStateFallbackRouter`**: Fail-closed guard. If solver returns infeasible or if `validity_status != VALID` (`UNKNOWN_INVALID`), bypasses solver and emits a governed zero-dispatch / protected-critical-only fallback `DispatchPlan`.
5. **`DigitalTwinSimulator`**: Receding-horizon offline simulation engine. Receives step 1 dispatch decision and updates physical state.

---

## 3. WHY THIS BOUNDARY ELIMINATES ARCHITECTURAL DEBT
- **Zero Duplicate Solver Physics**: Normal mode and Option D emergency mode share the exact same mathematical solver infrastructure (`EnergyOptimizer`).
- **100% GAP19 Compatibility**: `ModeConstraintSet` defines policy constraints as linear inequalities ($A x \le b$), which work identically under scalar MILP today and GAP19 multi-stage lexicographic optimization tomorrow.
- **Normal Mode Immunity**: In `NORMAL` mode, `ModeConstraintSet` is empty or unconstrained ($P_{\text{dis,max}} = 50$ kW, all loads served). Normal EMS optimization behavior is mathematically identical to baseline.
- **Fail-Closed Safety**: `UNKNOWN_INVALID` states are handled deterministically by `SafeStateFallbackRouter` without crashing the optimizer or running unvalidated telemetry through HiGHS.
