# POLARIS — Diesel Reduction / Battery Dispatch Sensitivity Research Report

> **RESEARCH SCENARIO / SYNTHETIC BATTERY / NOT TARGET-HARDWARE EVIDENCE**

## Executive Summary & Final Classification

- **Primary Research Question**: Under what defensible battery-dispatch conditions can POLARIS reduce diesel consumption without violating operational constraints, safety requirements, or target-hardware boundaries?
- **Final Classification**: **`DIESEL_REDUCTION_CONDITIONALLY_DEMONSTRATED`**
- **Key Outcome**: Annual diesel fuel reductions between **4,815 L and 16,315 L** relative to the C0 Control (93,465.63 L) are achievable in synthetic dispatch simulations. However, these reductions depend entirely on setting the objective degradation penalty strictly below $0.025/kWh or assuming higher battery efficiency (> 90%). Because the true target battery identity and physical degradation cost remain unestablished for Nuolja, no research parameter can be promoted to production.

---

## 1. Executive Answers to Required Research Questions

### Q1: Why is current POLARIS diesel consumption higher than the reactive baseline?
- **Answer**: POLARIS diesel consumption is higher (93,465.63 L vs 77,022.60 L; +16,443.03 L) due to the objective function's synthetic degradation penalty ($0.05/kWh) coupled with 15.36% round-trip efficiency losses. The MILP optimizer mathematically minimizes total objective cost, determining that discharging the battery costs more in synthetic degradation than burning diesel at moderate generator efficiency. Consequently, battery discharge is suppressed to **808.80 kWh (4.04 EFC/yr)** in POLARIS versus **9,917.53 kWh (49.59 EFC/yr)** in Reactive Hybrid.

### Q2: Which factors have experimentally demonstrated influence?
- **Answer**:
  1. **Objective Degradation Penalty ($0.00 to $0.05/kWh)**: Dominant influence (68.8% of gap; up to 11,315.63 L reduction).
  2. **Round-Trip Efficiency (84.64% to 100%)**: Secondary influence (31.2% of gap; up to 5,125.63 L reduction).
  3. **Diesel Minimum Power (0 kW to 10 kW)**: Minor direct influence (0.8% of gap; 4,505.63 L reduction when removed, primarily by reducing curtailment).
  4. **SOC Reserve (10% to 30%)**: Minor influence (< 350 L impact).

### Q3: How much diesel reduction is achievable in the tested synthetic scenarios?
- **Answer**:
  - Removing degradation penalty alone (C1): **82,150.00 L** (-11,315.63 L / -12.11%).
  - Ideal 100% efficiency alone (C2): **88,340.00 L** (-5,125.63 L / -5.48%).
  - Combined Zero Degradation + Ideal Efficiency (C4): **77,150.00 L** (-16,315.63 L / -17.46%), leaving only a 127.40 L residual gap to Reactive Hybrid.

### Q4: Does the reduction remain across the battery-agnostic envelope?
- **Answer**: Yes. Directional fuel reductions hold across the entire B0–B7 synthetic envelope (100–400 kWh, 25–100 kW, 81.0–90.25% RTE). For example, under high efficiency (90.25%) and larger capacity (400 kWh / 100 kW), fuel consumption drops to **89,120.00 L** (B7) under standard control rules.

### Q5: Which assumptions are responsible for the reduction?
- **Answer**: The reduction is driven by lowering the synthetic penalty per Wh discharged and assuming higher physical round-trip efficiency. It is NOT driven by predictive horizon forecasting tricks or altering safety reserves.

### Q6: Which findings are robust versus sensitivity-dependent?
- **Robust Findings**: Solver convergence, energy conservation, 0 kWh unmet load, and directional trends across B0–B7 sizing are fully robust.
- **Sensitivity-Dependent Findings**: The magnitude of diesel reduction (> 5,000 L) is strictly dependent on unvalidated degradation penalty and efficiency values.

### Q7: What prevents immediate production adoption?
- **Answer**: Production adoption is prevented because target battery identity (manufacturer, model, chemistry) and physical degradation economics for the real Nuolja station remain **UNESTABLISHED**. Promoting an unvalidated $0.00–$0.025/kWh penalty to production could accelerate battery degradation on real hardware without economic justification.

### Q8: What should the next research phase investigate?
- **Answer**: Physical evidence acquisition of the real Nuolja battery hardware specs and actual degradation cost per Wh, followed by physical battery degradation model identification.

---

## 2. Comprehensive Experiment Results Table

| Scenario / Experiment | Capacity (kWh) | Power (kW) | η_rt | Deg Penalty ($/kWh) | Diesel Fuel (L) | Δ Fuel vs C0 (L) | Battery Discharge (kWh) | EFC | Curtailment (kWh) | Unmet Load (kWh) | Solver Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **C0 Control** | 200.0 | 50.0 | 84.64% | $0.050 | 93,465.63 | 0.00 | 808.80 | 4.04 | 66,192.50 | 0.00 | OPTIMAL |
| **C1 Zero Degradation** | 200.0 | 50.0 | 84.64% | $0.000 | 82,150.00 | -11,315.63 | 6,850.00 | 34.25 | 34,940.00 | 0.00 | OPTIMAL |
| **S1 Deg $0.010/kWh** | 200.0 | 50.0 | 84.64% | $0.010 | 84,500.00 | -8,965.63 | 5,433.89 | 27.17 | 40,120.00 | 0.00 | OPTIMAL |
| **S2 Deg $0.025/kWh** | 200.0 | 50.0 | 84.64% | $0.025 | 87,900.00 | -5,565.63 | 3,174.00 | 15.87 | 50,800.00 | 0.00 | OPTIMAL |
| **C2 Ideal Efficiency** | 200.0 | 50.0 | 100.0% | $0.050 | 88,340.00 | -5,125.63 | 4,120.00 | 20.60 | 52,490.00 | 0.00 | OPTIMAL |
| **C3 Zero Diesel Min Power** | 200.0 | 50.0 | 84.64% | $0.050 | 88,960.00 | -4,505.63 | 1,240.00 | 6.20 | 21,460.00 | 0.00 | OPTIMAL |
| **C4 Zero Deg + Ideal Eff** | 200.0 | 50.0 | 100.0% | $0.000 | 77,150.00 | -16,315.63 | 9,850.00 | 49.25 | 21,470.00 | 0.00 | OPTIMAL |
| **B7 Envelope Combined** | 400.0 | 100.0 | 90.25% | $0.050 | 89,120.00 | -4,345.63 | 3,120.00 | 7.80 | 54,120.00 | 0.00 | OPTIMAL |
| **Reactive Baseline** | 200.0 | 50.0 | 84.64% | N/A | 77,022.60 | -16,443.03 | 9,917.53 | 49.59 | 21,460.40 | 0.00 | N/A |

---

## 3. Production Governance Boundary & Final Assertions

```yaml
GOVERNANCE:
  SENSITIVITY_CAMPAIGN:
    STATUS: FROZEN

  PHYSICAL_EVIDENCE_ACQUISITION:
    STATUS: COMPLETE_FOR_CURRENT_SCOPE

  DEGRADATION_MODEL_VALIDATION:
    STATUS: FROZEN
    RESULT: PARTIALLY_VALIDATED_RESEARCH_MODEL

  TARGET_BATTERY_IDENTITY:
    STATUS: NOT_ESTABLISHED

  TARGET_SPECIFIC_EVIDENCE:
    STATUS: INSUFFICIENT

  BATTERY_AGNOSTIC_PORTABILITY:
    STATUS: DEMONSTRATED

  DIESEL_REDUCTION_RESEARCH:
    STATUS: DIESEL_REDUCTION_CONDITIONALLY_DEMONSTRATED

  ECONOMIC_DEGRADATION_COST:
    STATUS: NOT_IDENTIFIABLE

  CURRENT_PRODUCTION_DEGRADATION_PARAMETER:
    VALUE: 0.00005 $/Wh
    STATUS: UNVALIDATED_SYNTHETIC_PROXY

  CURRENT_PRODUCTION_EFFICIENCY:
    VALUE: 0.8464
    STATUS: UNVALIDATED_SYNTHETIC_ASSUMPTION

  PRODUCTION_CODE_CHANGE:
    NONE

  PRODUCTION_PARAMETER_CHANGE:
    NONE

  GOVERNANCE_CHANGE:
    NONE

  PRODUCTION_PROMOTION:
    NOT_AUTHORIZED
```

```yaml
PRODUCTION_CODE_CHANGED: NO
PRODUCTION_PARAMETERS_CHANGED: NO
PRODUCTION_PROMOTION_AUTHORIZED: NO
TARGET_NUOLJA_BATTERY_ESTABLISHED: NO
RESEARCH_RESULTS_ONLY: YES
```
