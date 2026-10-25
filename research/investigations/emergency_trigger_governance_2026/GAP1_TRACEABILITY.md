# POLARIS — GAP 1 TRACEABILITY MATRIX

## Executive Overview

This traceability matrix establishes the lineage of **GAP 1: Credible Dispatchable Generation Modeling** across POLARIS specification artifacts, codebase schema files, mathematical formulas, verification test cases, and downstream governance gaps.

---

## 1. Traceability Mapping Table

| Artifact / File | Element / Section | Gap 1 Relation / Role | Current Status |
| :--- | :--- | :--- | :--- |
| `system/schemas/station_state.py` | `diesel_running`, `diesel_fuel_remaining_liters` | Source telemetry inputs for generator availability ($A_k$) and fuel ($V_{\text{fuel}}$). | `IMPLEMENTED` |
| `system/simulation/simulator.py` | `base_fuel_lph`, `marginal_fuel_lpwh`, `initial_fuel_l` | Fuel consumption model for digital twin simulator. | `IMPLEMENTED` |
| `system/optimization/implementations/gap19_highs_native.py` | `min_power_w`, `max_power_w`, `startup_fuel_l` | MILP optimization parameters for diesel dispatch ($10\text{ kW}$ to $100\text{ kW}$). | `IMPLEMENTED` |
| `EMERGENCY_TRIGGER_IMPLEMENTATION_SPEC.md` | Section 2.2 ($E_{\text{gen\_credible}}$) | Original proposed formula ($E_{\text{gen\_credible}} = \sum P_{\text{gen\_max}} \times 6\text{ h}$). | `AUDITED` (Model A) |
| `EMERGENCY_TRIGGER_MATH_RECONCILIATION.md` | Section 5 ($E_{\text{gen\_credible\_bus}}$) | Mathematical reconciliation identifying generator capping and fuel bounds. | `RECONCILED` |
| `EMERGENCY_TRIGGER_GAP_AUDIT.md` | Section GAP 1 | Identified GAP 1 unresolved question and candidate Models A–E. | `AUDITED` |
| `EMERGENCY_TRIGGER_CORRECTED_TEST_PLAN.md` | Test Cases H, I, J, K, R | Validates generator trip, fuel loss, and multi-resource adequacy behavior. | `RECONCILED` |
| `GAP1_GENERATOR_INPUT_INVENTORY.md` | Complete Document | Inventory of codebase fields classified into Project Fact, Assumption, Implemented, Missing, Unknown. | `RESEARCH_COMPLETE` |
| `GAP1_GENERATOR_MODEL_COMPARISON.md` | Complete Document | Neutral comparative evaluation matrix across 12 criteria for Models A–E. | `RESEARCH_COMPLETE` |
| `GAP1_HUMAN_DECISION_BRIEF.md` | Complete Document | Neutral decision brief framing Options A–E for human governance sign-off. | `RESEARCH_COMPLETE` |

---

## 2. Downstream Gap Dependencies

The choice of generator credibility model directly impacts four downstream governance items:

1. **GAP 2 (Renewable Credibility)**: If Model C (Fuel-Constrained) or Model D (Demand Bounded) is selected for generation, the net critical energy gap $E_{\text{critical\_req}} - E_{\text{gen\_credible}}$ dictates how much renewable forecast energy ($E_{\text{ren\_credible}}$) is required to prevent Emergency entry.
2. **GAP 3 (Emergency Exit Requirements)**: If generator availability ($A_k = 1$) is required to establish credibility under GAP 1, it directly informs whether generator availability is mandatory for Emergency Exit.
3. **GAP 4 (Missing Forecast Fallback)**: If generator credibility under GAP 1 is sufficient to cover 6 hours of critical load alone ($E_{\text{gen\_credible}} \ge 69.60\text{ kWh}$), missing renewable forecasts have ZERO impact on Emergency state determination.
4. **GAP 5 (Exit Transition Path)**: Generator credibility status determines whether the system can exit Emergency into `RESERVE_DEFICIT` mode once diesel generation is online.
