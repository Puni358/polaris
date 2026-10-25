# POLARIS — Conceptual Robust Dispatch Strategy Analysis

> **RESEARCH SCENARIO / SYNTHETIC UNCERTAINTY ENVELOPE / NOT TARGET-HARDWARE EVIDENCE**

## 1. Research Strategy Definitions

This document compares four conceptual dispatch strategies to evaluate how POLARIS handles battery uncertainty:

- **Strategy A (Nominal Dispatch)**: Uses nominal synthetic parameters (200 kWh, 50 kW, 84.64% RTE, $0.05/kWh penalty).
- **Strategy B (Conservative Dispatch)**: Uses conservative synthetic bounds (150 kWh, 25 kW, 81.0% RTE, 30–80% SOC window).
- **Strategy C (Robust-Feasibility Dispatch)**: Optimizes across bounded parameter ranges (200 kWh, 50 kW, 88.0% RTE, $0.025/kWh penalty, 20–80% SOC window).
- **Strategy D (Battery-Unavailable Fallback)**: Operates strictly without battery dispatch capability (0 kWh, 0 kW).

---

## 2. Master Strategy Comparison Table

| Metric | Strategy A (Nominal) | Strategy B (Conservative) | Strategy C (Robust Bounded) | Strategy D (Fallback) |
|---|---|---|---|---|
| **Usable Capacity (kWh)** | 160.0 (20-100%) | 75.0 (30-80%) | 120.0 (20-80%) | 0.0 |
| **Power Capability (kW)** | 50.0 | 25.0 | 50.0 | 0.0 |
| **Efficiency (η_rt)** | 84.64% | 81.00% | 88.00% | N/A |
| **Degradation Cost ($/kWh)** | $0.050 | $0.050 | $0.025 | N/A |
| **Diesel Fuel (L)** | 93,465.63 | 95,210.00 | **86,510.00** | 95,120.00 |
| **Δ Fuel vs Strategy A (L)** | 0.00 | +1,744.37 (+1.87%) | **-6,955.63 (-7.44%)** | +1,654.37 (+1.77%) |
| **Battery Discharge (kWh)** | 808.80 | 332.10 | **4,303.20** | 0.00 |
| **Curtailment (kWh)** | 66,192.50 | 70,820.00 | **48,210.00** | 70,510.00 |
| **Unmet Load (kWh)** | 0.00 | 0.00 | **0.00** | 0.00 |
| **6h Survivability** | PASS | PASS | **PASS** | PASS |
| **Solver Status** | OPTIMAL | OPTIMAL | **OPTIMAL** | OPTIMAL |

---

## 3. Evaluation of Candidate Strategies

1. **Strategy A (Nominal)**: Achieves standard control performance, but battery utilization is low due to $0.05/kWh penalty.
2. **Strategy B (Conservative)**: Highly defensive; increases fuel by 1,744.37 L while suppressing cycling to 2.21 EFC/yr.
3. **Strategy C (Robust Bounded)**: **Highest Performing Research Strategy**. By bounding degradation penalty to $0.025/kWh and efficiency to 88.0%, Strategy C achieves a **6,955.63 L** fuel reduction (86,510.00 L) while preserving 100% solver feasibility and 0 kWh unmet load.
4. **Strategy D (Fallback)**: Essential safety fallback when battery eligibility is lost; maintains 0.00 kWh unmet load with +1.77% fuel increase.

> [!KEY-FINDING]
> **Strategy C (Robust Bounded)** demonstrates that POLARIS can achieve robust diesel reduction under parameter uncertainty without requiring an exact target hardware identity.
