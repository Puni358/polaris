# POLARIS Step 10B: Hybrid Diesel Counterfactual Feasibility Audit

## Executive Summary

A read-only methodological feasibility audit was conducted to determine whether a scientifically valid same-H1.0 same-truth control counterfactual can be defined for a future separate experiment.

- **Same-Environment Control Feasibility:** **`YES`**
- **Proposed Control Policy ID:** `POLARIS_BASELINE_RULE_BASED_CONTROL`
- **Control Execution Status in Step 10B:** **`NOT EXECUTED`** (Zero control solves executed)
- **Diesel Savings Calculated in Step 10B:** **`NO`**
- **Future Control Solves Required:** `24` (Under a separate future governance authorization)
- **Final Classification:** **`A — VALID SAME-ENVIRONMENT CONTROL FEASIBLE`**

---

## 1. Same-Truth Preservation Requirements

A future paired counterfactual comparison will be methodologically valid because it will preserve:

1. **Same Input Fixture:** `POLARIS_HYBRID_FIXTURE_H1_0/` (`762297aae21c...`)
2. **Same Trajectory Window:** `2024-01-01T00:00:00Z` to `2024-01-01T23:00:00Z` (Row 0..23)
3. **Same Initial State ($t_0$):** SOC `50.0%`, Battery Energy `100,000 Wh`, Diesel `Off`
4. **Same Hidden Ground Truth:** Identical hourly solar SW_IN, wind speed proxy, generic turbine curve, and synthetic station load
5. **Same Microgrid Physics & Constraints:** Identical `DigitalTwinSimulator`, battery parameters, diesel constraints, and inverter limits
6. **Same MPC Horizon & Firewall:** 24h receding horizon with strict future-truth firewall enforcement

---

## 2. Distinction Between Three Core Questions

| Question | Current Status | Findings / Rationale |
| :--- | :---: | :--- |
| **Q1: Observed Fuel Consumption**<br> *How much diesel did this H1.0 trajectory consume?* | **OBSERVED DIRECTLY** | **`195.500 L`** (reconciled directly from raw 24-step telemetry). |
| **Q2: Paired Fuel Difference**<br> *How much diesel did H1.0 save vs same-truth control?* | **NOT CALCULATED** | No control trajectory was executed during Step 10B. |
| **Q3: Real Station Savings**<br> *How much diesel would POLARIS save at a real station?* | **NOT ESTABLISHED** | Real station electrical demand & Nuolja wind generation data remain DATA_BLOCKED / NOT_ESTABLISHED. |

---

## 3. Predeclared Future Endpoints

When a future control experiment is authorized, the endpoints will be defined as:

```plain
Delta Fuel_diesel = Fuel_treatment - Fuel_control  [Liters]
```

- Delta Fuel_diesel < 0: Treatment used less diesel under the same H1.0 environment.
- Delta Fuel_diesel > 0: Treatment used more diesel under the same H1.0 environment.

Secondary Endpoints:
- Delta Energy_diesel (kWh)
- Delta Energy_renewable (kWh)
- Delta Curtailment (kWh)
- Delta Throughput_battery (kWh)

---

## 4. Mandatory Final Status Block

```plain
STEP10B_EVIDENCE_FREEZE = PASS
OBSERVED_DIESEL_CONSUMPTION_L = 195.500
OBSERVED_DIESEL_RECONCILIATION = PASS

CONTROL_EXECUTED = NO
DIESEL_SAVING_CALCULATED = NO

SAME_TRUTH_CONTROL_FEASIBLE = YES
CONTROL_POLICY = POLARIS_BASELINE_RULE_BASED_CONTROL
FUTURE_CONTROL_SOLVES_REQUIRED = 24

MILP_SOLVES_DURING_AUDIT = 0
SIMULATOR_STEPS_DURING_AUDIT = 0

FROZEN_EVIDENCE_MODIFIED = NO
FINAL_EVIDENCE_CLASSIFICATION = A
```
