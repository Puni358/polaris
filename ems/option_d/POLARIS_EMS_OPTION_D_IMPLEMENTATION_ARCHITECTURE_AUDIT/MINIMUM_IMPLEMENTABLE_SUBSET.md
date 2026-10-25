# MINIMUM IMPLEMENTABLE SUBSET

## 1. CATEGORIZATION OF OPTION D IMPLEMENTATION ELEMENTS

The audit categorized every architectural element of Option D into its implementation status bucket.

---

## 2. CATEGORIZATION REGISTER

### A. `SAFE_TO_IMPLEMENT_NOW`
- `SyntheticFixtureProvider` adapter.
- Additive schema extensions (`StationState.fuel_remaining_liters`, `ForecastBundle.critical_demand`, `DispatchPlan.critical_load_served`).
- ECD runner wiring in `runner.py`.
- `OptionDPolicyLayer` (Policy Router preprocessor generating `ModeConstraintSet`).
- MILP decision variable extensions ($P_{\text{served,crit}}$, $P_{\text{unmet,crit}}$, $P_{\text{served,flex}}$, $P_{\text{unmet,flex}}$, $\alpha$).
- Linear constraints for Option D (battery discharge $\le P_{\text{critical}}$, renewable-first allocation, diesel excess charging, proportional allocation).
- `SafeStateFallbackRouter` for `UNKNOWN_INVALID`.
- `DigitalTwinSimulator` diesel fuel decrement logic.

### B. `WAIT_FOR_GAP19`
- Native HiGHS C++ multi-stage sequential lexicographic solver interface.
- Exact multi-objective Stage 1..4 Pareto frontier evaluation.

### C. `WAIT_FOR_ENGINEERING_INPUTS`
- Station-specific electrical circuit map for critical loads.
- Numeric engineering minimum viable power levels ($P_{i,\text{min}}$) for specific field equipment.

### D. `WAIT_FOR_GOVERNANCE_DECISION`
- Operator escalation maximum time boundary $T_{\text{max\_degraded}}$ and fuel threshold $V_{\text{escalate}}$.
- Automated vs manual recovery acknowledgment requirements.
