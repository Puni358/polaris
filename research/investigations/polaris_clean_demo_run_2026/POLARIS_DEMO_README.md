# POLARIS Demonstration Package README

## 1. What is POLARIS?

**POLARIS** is an AI-driven predictive Energy Management System (EMS) designed for hybrid off-grid microgrids combining solar photovoltaics, wind generation, battery energy storage, and backup diesel generation. POLARIS utilizes receding-horizon Closed-Loop Model Predictive Control (MPC) and Mixed-Integer Linear Programming (MILP) to minimize fuel costs and battery degradation while guaranteeing 100% load reliability.

---

## 2. What Does the Demonstration Show?

The demonstration shows the complete, un-broken operational software chain executing offline on local hardware:

```text
Synthetic Inputs (Weather + Load)
            ↓
       Forecasting
            ↓
    Energy Optimization (MILP)
            ↓
     Dispatch Decisions (MPC H1)
            ↓
 Digital Twin State Simulation
            ↓
  System Evaluation & Reporting
```

---

## 3. What Scenarios Are Demonstrated?

1. **Scenario S0 — Baseline / Normal**: Stable diurnal solar/wind and nominal load. POLARIS operates on 100% renewables and battery storage (0.0 kWh diesel).
2. **Scenario S1 — Renewable Degradation**: 80% solar drop, 70% wind drop, elevated load. POLARIS dispatches diesel for 28 hours (1,108 kWh generation, 417 L fuel) while drawing the battery down to its 20% minimum boundary.
3. **Scenario S2 — Telemetry Degradation**: 4-hour synthetic telemetry hold. POLARIS handles stale inputs cleanly without solver exceptions or runtime crashes (0.0 kWh diesel).
4. **Scenario S3 — Combined Severe Stress**: Solar outage, 90% wind drop, 45 kW high load. POLARIS dispatches diesel for 44 hours (1,856 kWh generation, 664 L fuel), maintaining 100% load reliability.

---

## 4. What Does the Demonstration ACTUALLY Prove?

- **Software Execution & Architecture Integrity**: Proves that the POLARIS software modules (`LocalDataProvider`, `ForecastEngine`, `EMSControlRouter`, `EnergyOptimizer`, `DigitalTwinSimulator`, `EvaluationEngine`) execute cleanly end-to-end without runtime errors, schema mismatches, or solver failure.
- **Mathematical Energy Conservation**: Proves exact energy conservation ($E_{\text{load}} = E_{\text{ren}} + E_{\text{bat\_net}} + E_{\text{dies}} - \text{losses}$) across all receding-horizon timesteps with 0.000000 kWh error.
- **Predictable Control Behavior**: Proves that the MILP optimization model dispatches backup diesel generation in direct proportion to resource deficits while respecting battery SOC constraints.

---

## 5. What Does the Demonstration NOT Prove?

> [!WARNING]
> **Strict Epistemic Boundary**:
> - **NOT Real-World Generator Performance**: Demonstrates software logic only, NOT physical diesel engine governor dynamics or transient frequency/voltage behavior.
> - **NOT Nuolja Field Site Empirical Validation**: Uses synthetic scenario data; does NOT use real Nuolja SCADA telemetry.
> - **NOT Telemetry Freshness Safety Rules**: Software tolerance to a 4-hour telemetry hold in S2 does NOT prove physical plant safety or establish a G1.3-E freshness rule.

---

## 6. SIH-Facing Numbers Labeling

When presenting numbers from this demonstration to stakeholders or judges, they must be labeled strictly as **Controlled Synthetic Demonstration Results**:

- **1,108 kWh Diesel (S1)**: Result of controlled 80% solar / 70% wind synthetic drop.
- **1,856 kWh Diesel (S3)**: Result of controlled solar outage & 45 kW load synthetic stress.
- **0.0 kWh Unmet Load**: Result of high MILP penalty ($10,000 / kWh) vs diesel cost ($0.625 / kWh).
- **20.0% Ending SOC**: Result of MILP lower-bound battery constraint (`min_soc_pct = 20.0%`).

---

## 7. Final Demonstration Readiness Gate

```yaml
PREFLIGHT: PASS
S0_EXECUTION: PASS
S1_EXECUTION: PASS
S2_EXECUTION: PASS
S3_EXECUTION: PASS

S0_REPRODUCED: YES
S3_REPRODUCED: YES

DIESEL_REPORT_GENERATED: YES
REPORT_TRACEABLE: YES

DEMO_PACKAGE_COMPLETE: YES
DEMO_READY: YES
```

---

## 8. Final Governance Verification

```yaml
G1_3E_POLICY: LOCKED
EVIDENCE_BOUNDARY: C
RESOURCE_SPECIFIC_FRESHNESS_RULES: 0/8
NUOLJA_SPECIFIC_FRESHNESS_RULES: 0
EVD02: FROZEN_BLOCKER
PRODUCTION_GOVERNANCE: UNCHANGED
```
