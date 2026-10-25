# SCIENTIFIC CLAIM BOUNDARY

## 1. BOUNDED SCOPE OF FIXTURE-DRIVEN RUNTIME TESTS

This document explicitly defines the firewall between what a future fixture-driven runtime test WOULD establish versus what it CANNOT establish.

---

## 2. POSSIBLY ESTABLISHABLE (Software Engineering Scope)
A successful future fixture-driven runtime test (TEST-0 through TEST-3) WOULD establish:
1. **Software Interface Connectivity**: Verification that Data Provider, StationState, ForecastEngine, ForecastBundle, ECD, Policy Router, EnergyOptimizer, DispatchPlan, and DigitalTwin connect without runtime exceptions.
2. **Data Contract Compliance**: Verification that schemas enforce physical bounds, 1h monotonicity, non-negativity, and finite numerics across scenario execution.
3. **ECD Classification Integrity**: Verification that `EmergencyConditionDetector` correctly classifies `NORMAL`, `EMERGENCY`, and `UNKNOWN_INVALID` across synthetic stress cases.
4. **Option D Policy Alignment**: Verification that the software implementation of Option D rules (critical load support, excess charging, battery discharge restriction) follows synthetic assumptions.
5. **Truth Firewall Survival**: Verification that future actual observations ($t+1..t+24$) do not leak into controller forecast or optimization modules.
6. **Energy Balance Accounting**: Verification that discrete energy conservation $\sum P \Delta t = 0$ holds across all simulation steps.

---

## 3. NOT ESTABLISHABLE (Hard Scientific Boundary)
A successful fixture-driven runtime test CANNOT establish:
1. **Real Nuolja Survivability**: Zero real-world station survivability guarantees for Nuolja.
2. **Real Nuolja Load Requirements**: Zero empirical load validation (`DIRECT_NUOLJA_EVIDENCE = 0`).
3. **Real Nuolja Generator Performance**: Zero empirical diesel fuel consumption or efficiency curves.
4. **Real Nuolja Battery Degradation**: Zero empirical battery degradation or thermal performance validation.
5. **Real Nuolja Economic Savings**: Zero real-world cost savings or fuel reduction claims.
6. **Real Station Deployment Readiness**: Zero authorization for field deployment or operational hardware control.

---

## 4. GOVERNED CLAIM FIREWALL STATEMENT
> **AUTHORITATIVE DIRECTIVE**: All outputs, logs, reports, and execution metrics derived from `POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/` MUST be cited strictly as **SYNTHETIC SOFTWARE ARCHITECTURE INTEGRATION RESULTS**. Citing synthetic fixture results as empirical Nuolja facts is **STRICTLY PROHIBITED**.
