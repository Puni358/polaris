# IMPLEMENTATION AUTHORIZATION SCOPE

## Executive Scope Summary

This document establishes the definitive scope boundaries for future implementation work on **POLARIS EMS Option D — Protected Critical Load Fallback**. It consolidates the authorization answers for all 15 core governance questions.

---

## 15 Authoritative Scope Answers

### 1. Authorized Implementation Work (Pending Human Sign-off)
The following pre-GAP19 implementation work is defined and structured for future approval:
- Additive schema extensions to `StationState`, `ForecastBundle`, and `DispatchPlan` for critical loads and operating modes.
- `SyntheticFixtureProvider` interface adapter to inject synthetic data into EMS pipelines.
- Runtime wiring of `EnergyCrisisDetector` (ECD) into `system/runtime/runner.py`.
- `OptionDPolicyLayer` and `ModeConstraintSet` solver-neutral policy router.
- 21-variable MILP linear constraint formulation in `system/optimization/implementations/milp.py`.
- Routing architecture for `UNKNOWN_INVALID` state into protected critical safe mode.
- Synthetic test harness executing Gates 0–10.

### 2. Files / Components That May Be Modified (`MUST_MODIFY` / `MAY_MODIFY`)
Upon explicit human authorization, the following source files may be updated:
- `system/schemas/state.py`, `forecast.py`, `dispatch.py` (Additive optional fields).
- `system/runtime/runner.py` (ECD wiring, state transformation, mode dispatch).
- `system/optimization/implementations/milp.py` (Additive 21-variable linear constraint set).
- `system/simulation/simulator.py` (Fuel tank decrementing logic for synthetic testing).

### 3. Files / Components That MUST Remain Untouched (`MUST_NOT_MODIFY`)
- `system/control/ecd.py` (Core logic frozen, fully verified, and reusable as-is).
- `system/forecasting/` (Stage8.1, Branch01, model training, evaluation scripts).
- `system/data/` (Synthetic fixture JSON files and scenario definition data).
- Production station configuration and security key registries.

### 4. Required Implementation Behavior
- Enforce $D4$ proportional load allocation ($P_{i,\text{served}} = \alpha P_{i,\text{min}}$) during power deficits.
- Enforce $D2$ battery discharge restriction exclusively to protected critical loads during Option D.
- Enforce $D6$ excess diesel generation routing to battery charging before curtailment.
- Prevent diesel start solely for battery charging.
- Route `UNKNOWN_INVALID` sensor states to Option D protected critical safe state.

### 5. Prohibited Implementation Behavior
- Do **NOT** introduce category priority or arbitrary priority weights across protected critical loads.
- Do **NOT** use requested demand ($P_{i,\text{requested}}$) as the basis for D4 proportional allocation.
- Do **NOT** allow battery power to supply noncritical flexible loads in Option D.
- Do **NOT** duplicate MILP solver logic inside ECD or `OptionDPolicyLayer`.
- Do **NOT** modify the current scalar MILP objective function into a pseudo-lexicographic objective with huge penalty weights.

### 6. Synthetic Fixture Values
- Heating: 15 kW, Water: 10 kW, Communications: 5 kW (Total Critical = 30 kW).
- Flexible Load: 15 kW (Total Synthetic Load = 45 kW).
- Battery: 200 kWh total, 20% min SOC (40 kWh), 95% max SOC (190 kWh), 50 kW power rating.
- Diesel Generator: 10–60 kW operating range.
- Synthetic Fuel Scenarios: 500 L, 20 L, 10 L.
- Synthetic Survivability Horizon: 72 hours.

### 7. Values Requiring Real Station Engineering Data
- Nuolja station equipment inventory and tier circuit topology.
- Real station dynamic minimum viable requirements $P_{i,\text{min}}(t)$.
- Real diesel fuel consumption maps and minimum load limits.
- Real battery C-rates, thermal degradation curves, and usable capacity.
- Real usable fuel tank volume and telemetry freshness thresholds.
- Production $T_{\text{required}} = 6.0\text{ hours}$ operational baseline.

### 8. Sealed Decisions
- **DEC-004**: Option D — Protected Critical Load Fallback.
- **D1**: Protected critical load dynamic minimums $P_{i,\text{min}}(t)$, conceptual categories.
- **D2**: Battery discharge restricted strictly to protected critical load during Option D.
- **D3**: Renewable + Diesel insufficient $\rightarrow$ battery supports protected critical load until boundary.
- **D4**: `PROPORTIONAL_TO_MINIMUM_VIABLE_CRITICAL_REQUIREMENTS` ($P_{i,\text{served}} = \alpha P_{i,\text{min}}$).
- **D5**: Dual escalation triggers (Time boundary OR resource survivability boundary).
- **D6**: Diesel excess $\rightarrow$ battery charging $\rightarrow$ curtailment; no diesel start solely to charge battery.
- **$T_{\text{required}}$ Governance**: Baseline $6.0\text{ hours}$, Hybrid config, Automated MFA Cryptographic Gate.

### 9. Unresolved Decisions
- Operator escalation quantitative thresholds (Time limit in hours, fuel volume limit in Liters).
- Recovery clearance policy (Automatic vs manual operator sign-off).
- Production telemetry freshness thresholds and key management.
- Real Nuolja critical equipment inventory and circuit mapping.

### 10. Items Implementable Pre-GAP19 (Strategy 2)
- Schema additive extensions.
- `SyntheticFixtureProvider` adapter.
- ECD runner integration and `OperatingMode` propagation.
- `OptionDPolicyLayer` and `ModeConstraintSet`.
- 21-variable scalar linear MILP constraint set under SciPy HiGHS.
- UNKNOWN_INVALID fallback routing.
- Synthetic test harness (Gates 0–10).

### 11. Items Deferred to GAP19
- Stage 1 Critical Reliability objective reformulation.
- Stage 2 EBR / Terminal Reserve multi-objective formulation.
- Stage 3 Governed Fuel objective formulation.
- Stage 4 Renewable / Curtailment Pareto objective formulation.
- Native HiGHS C++ multi-stage sequential lexicographic solver orchestration.

### 12. Tests Required Before Controlled Runtime Execution
- Gate 0: Static contract verification.
- Gate 1: Synthetic fixture adapter unit tests.
- Gate 2: ECD interface integration tests.
- Gate 3: `OperatingMode` & Policy Layer translation tests.
- Gate 4: D4 proportional allocation constraint mathematical tests.
- Gate 5: D6 excess generation charging tests.
- Gate 6: `UNKNOWN_INVALID` routing & fallback tests.
- Gate 7: Normal mode regression tests.

### 13. Tests Required Before Broader Synthetic Demonstration
- Gate 8: Single synthetic scenario closed-loop execution (SC-01).
- Gate 9: All five synthetic scenarios execution (SC-01 through SC-05).
- Gate 10: 24-hour closed-loop synthetic stability demonstration.

### 14. Permitted Scientific Claims
- Proves schema, interface, and data-flow integration correctness.
- Proves exact mathematical enforcement of D4, D2, and D6 under synthetic assumptions.
- Proves determinism, safety-state routing, and truth-firewall isolation.

### 15. Prohibited Scientific Claims
- Must **NOT** claim real Nuolja station survivability or fuel autonomy.
- Must **NOT** claim real station economic optimization or battery longevity.
- Must **NOT** claim production deployment readiness or commercial suitability.
