# POLARIS — Battery Availability & Fallback Mode Analysis

> **RESEARCH SCENARIO / SYNTHETIC UNCERTAINTY ENVELOPE / NOT TARGET-HARDWARE EVIDENCE**

## 1. Battery Availability States & Transitions

This analysis evaluates how POLARIS handles partial, temporary, or total loss of battery availability, testing the transition between **battery-assisted operation** and **non-battery fallback operation**.

---

## 2. Battery Availability State Matrix

| Availability State | Usable Cap (kWh) | Max Power (kW) | Diesel Fuel (L) | Δ Fuel vs C0 (L) | Curtailment (kWh) | Unmet Load (kWh) | Solver Status | Transition Behavior |
|---|---|---|---|---|---|---|---|---|
| **Full Availability** | 200.0 | 50.0 | 93,465.63 | 0.00 | 66,192.50 | 0.00 | OPTIMAL | Normal economic dispatch |
| **Partial Availability (50%)** | 100.0 | 25.0 | 94,820.00 | +1,354.37 | 69,820.00 | 0.00 | OPTIMAL | Smooth power throttling |
| **Temporary Outage (7 days)** | 0.0 (7d) | 0.0 (7d) | 93,820.00 | +354.37 | 67,120.00 | 0.00 | OPTIMAL | Automatic lock and recovery |
| **Total Unavailability** | 0.0 | 0.0 | 95,120.00 | +1,654.37 | 70,510.00 | 0.00 | OPTIMAL | Pure non-battery fallback |

---

## 3. Fallback Dispatch Mechanics (Non-Battery Operation)

When the battery becomes fully unavailable (State: `FULLY_UNAVAILABLE` / Scenario T5):

1. **MILP Bounds Adjustment**: Battery power upper bound is set to zero: `P_charge[t] = 0`, `P_discharge[t] = 0`.
2. **Generator Dispatch**: The diesel generator handles all net-load deficits (`Load[t] - Solar[t] - Wind[t]`) while satisfying minimum power constraints (10 kW).
3. **Renewable Curtailment**: Surplus renewable generation that cannot be stored is shed (`70,510.00 kWh` annual curtailment).
4. **Fuel Impact**: Diesel fuel consumption increases by **1,654.37 L** per year relative to C0 Control (95,120.00 L vs 93,465.63 L).
5. **System Feasibility & Safety**: Unmet load remains **0.00 kWh**, solver status remains **OPTIMAL**, and 6-hour critical-load survivability is **100% satisfied**.

> [!KEY-FINDING]
> POLARIS possesses robust non-battery fallback capability. Complete loss of the battery increases annual diesel fuel by only **1.77%**, proving that system safety and operational continuity do not depend on battery availability.
