# POLARIS SOLAR FORECAST BRANCH 01
## EMS INTEGRATION TEST PLAN (STATIC & CONTROLLED VALIDATION)

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Test Plan Type:** `STATIC INTERFACE & CAUSAL VALIDATION ONLY`  
**EMS Execution State:** `EMS_EXECUTION_AUTHORIZATION = NOT_GRANTED`  

---

### 1. Objective & Governance Boundaries
This test plan establishes the 20 static interface, causality, schema, determinism, and firewall tests required before Branch 01 can be integrated into any future EMS experiment. No MILP optimization runs, MPC loops, or Digital Twin simulations are executed during this static test plan.

---

### 2. Static Integration Test Categories
1. **Model & Artifact Integrity (INT_01 – INT_02)**: Verify serialized `model.joblib` loading and SHA-256 match against freeze manifest (`65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781`).
2. **Contract & Schema Alignment (INT_03 – INT_05)**: Verify 18-feature input schema, 24-horizon output vector, and ISO-8601 UTC timestamp monotonicity.
3. **Causality & NWP Safeguards (INT_06 – INT_08)**: Verify $t_{	ext{available}} \le t_{	ext{origin}}$, NWP issue run causality ($t_{	ext{issue}} \le t_{	ext{origin}}$), and clear-sky origin lookup.
4. **ForecastBundle & Engine Compatibility (INT_09 – INT_10)**: Verify creation of `ForecastBundle` Version 1.0.0 with solar irradiance ($	ext{W/m}^2$) and PV power ($	ext{W}$), and `ForecastEngine` predict interface.
5. **Truth Firewall & Robustness (INT_11 – INT_13)**: Verify Digital Twin truth isolation, fail-closed handling on NaN/Inf inputs, and non-negativity ($SW\_IN \ge 0.0$).
6. **EMS & Optimizer Boundary Preservation (INT_14 – INT_17)**: Verify `EnergyOptimizer`, `DispatchPlan`, `DigitalTwinSimulator`, and `s81_solar.py` remain 100% untouched.
7. **Determinism, Provenance & Rollback (INT_18 – INT_20)**: Verify zero prediction drift across replays, metadata traceability, and governed rollback policies.

---

### 3. Execution Requirements
All tests are non-executing or interface-only. If any static test fails, integration is halted immediately.
