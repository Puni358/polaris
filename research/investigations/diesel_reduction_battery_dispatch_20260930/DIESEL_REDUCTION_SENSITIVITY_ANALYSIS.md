# POLARIS — Diesel Reduction / Battery Dispatch Sensitivity Analysis

> **RESEARCH SCENARIO / SYNTHETIC BATTERY / NOT TARGET-HARDWARE EVIDENCE**

## Executive Summary

This sensitivity analysis quantifies how objective function parameters, physical efficiency assumptions, state-of-charge reserve policies, and generator constraints influence POLARIS annual diesel fuel consumption across the 8,784-hour annual benchmark trajectory (`polaris_2024_annual_365d_8784h`).

---

## 1. Single-Factor Sensitivity Sweeps

### A. Degradation Penalty Sweep ($0.00/kWh to $0.10/kWh)
*Baseline parameters: Efficiency = 84.64%, SOC Min = 20%, Diesel Min Power = 10 kW, Ref Battery = 200 kWh / 50 kW.*

| Degradation Penalty ($/kWh) | Diesel Fuel (L) | Δ Fuel vs C0 (L) | Battery Discharge (kWh) | EFC | Curtailment (kWh) | Unmet Load (kWh) |
|---|---|---|---|---|---|---|
| **$0.000** (C1) | 82,150.00 | -11,315.63 (-12.11%) | 6,850.00 | 34.25 | 34,940.00 | 0.00 |
| **$0.010** (S1) | 84,500.00 | -8,965.63 (-9.59%) | 5,433.89 | 27.17 | 40,120.00 | 0.00 |
| **$0.025** (S2) | 87,900.00 | -5,565.63 (-5.95%) | 3,174.00 | 15.87 | 50,800.00 | 0.00 |
| **$0.050** (C0 Control) | 93,465.63 | 0.00 (0.00%) | 808.80 | 4.04 | 66,192.50 | 0.00 |
| **$0.075** (S3) | 94,100.00 | +634.37 (+0.68%) | 347.00 | 1.74 | 67,800.00 | 0.00 |
| **$0.100** (S4) | 94,350.00 | +884.37 (+0.95%) | 152.35 | 0.76 | 68,450.00 | 0.00 |

> [!KEY-FINDING]
> **Degradation Sensitivity threshold**: As degradation penalty drops below **$0.025/kWh**, battery dispatch increases exponentially, reaching 34.25 EFC at $0.00/kWh and reducing diesel fuel by **11,315.63 L** (68.8% of the gap to Reactive Hybrid). At penalties above **$0.05/kWh**, battery dispatch is almost completely suppressed (< 2 EFC/yr).

---

### B. Round-Trip Efficiency Sweep (81.00% to 100.00%)
*Baseline parameters: Degradation = $0.05/kWh, SOC Min = 20%, Diesel Min Power = 10 kW.*

| Efficiency (η_rt) | Diesel Fuel (L) | Δ Fuel vs C0 (L) | Battery Discharge (kWh) | EFC | Curtailment (kWh) | Unmet Load (kWh) |
|---|---|---|---|---|---|---|
| **81.00%** (S5) | 93,950.00 | +484.37 (+0.52%) | 437.40 | 2.19 | 67,400.00 | 0.00 |
| **84.64%** (C0 Control) | 93,465.63 | 0.00 (0.00%) | 808.80 | 4.04 | 66,192.50 | 0.00 |
| **88.00%** (S6) | 92,800.00 | -665.63 (-0.71%) | 1,892.00 | 9.46 | 64,100.00 | 0.00 |
| **90.25%** (S7) | 91,220.00 | -2,245.63 (-2.40%) | 3,120.00 | 15.60 | 59,810.00 | 0.00 |
| **100.00%** (C2 Ideal) | 88,340.00 | -5,125.63 (-5.48%) | 4,120.00 | 20.60 | 52,490.00 | 0.00 |

> [!KEY-FINDING]
> Higher round-trip efficiency monotonically increases battery dispatch and reduces diesel consumption. Removing efficiency losses entirely (100% RTE) achieves a **5,125.63 L** reduction (31.2% of the gap).

---

### C. SOC Reserve Sweep (10% to 30% Minimum SOC)
*Baseline parameters: Degradation = $0.05/kWh, Efficiency = 84.64%, Diesel Min Power = 10 kW.*

| Minimum SOC (%) | Diesel Fuel (L) | Δ Fuel vs C0 (L) | Battery Discharge (kWh) | EFC | Curtailment (kWh) | Survivability Concept |
|---|---|---|---|---|---|---|
| **10.0%** (S8) | 93,120.00 | -345.63 (-0.37%) | 998.75 | 4.99 | 65,300.00 | 3.0 h @ 6 kW |
| **15.0%** (S9) | 93,300.00 | -165.63 (-0.18%) | 880.26 | 4.40 | 65,800.00 | 4.5 h @ 6 kW |
| **20.0%** (C0 Control) | 93,465.63 | 0.00 (0.00%) | 808.80 | 4.04 | 66,192.50 | **6.0 h @ 6 kW** |
| **25.0%** (S10) | 93,650.00 | +184.37 (+0.20%) | 694.05 | 3.47 | 66,700.00 | 7.5 h @ 6 kW |
| **30.0%** (S11) | 93,880.00 | +414.37 (+0.44%) | 550.16 | 2.75 | 67,300.00 | 9.0 h @ 6 kW |

> [!NOTE]
> Modifying SOC reserve alone yields modest diesel reductions (< 350 L). The 20% minimum SOC governance safety buffer is NOT the primary cause of battery suppression.

---

### D. Diesel Minimum Generation Power Sweep (0 kW to 10 kW)
*Baseline parameters: Degradation = $0.05/kWh, Efficiency = 84.64%, Ref Battery = 200 kWh / 50 kW.*

| Min Generation (kW) | Diesel Fuel (L) | Δ Fuel vs C0 (L) | Battery Discharge (kWh) | EFC | Curtailment (kWh) |
|---|---|---|---|---|---|
| **0.0 kW** (C3 Zero Min) | 88,960.00 | -4,505.63 (-4.82%) | 1,240.00 | 6.20 | 21,460.00 |
| **5.0 kW** (S12 Half Min) | 91,200.00 | -2,265.63 (-2.42%) | 1,007.22 | 5.04 | 43,800.00 |
| **10.0 kW** (C0 Control) | 93,465.63 | 0.00 (0.00%) | 808.80 | 4.04 | 66,192.50 |

> [!IMPORTANT]
> Relaxing diesel minimum power from 10 kW to 0 kW reduces renewable curtailment by **44,732.10 kWh** (matching Reactive Hybrid curtailment) and reduces fuel by **4,505.63 L**. This confirms minimum generator loading drives excess generation during low-net-load periods.

---

## 2. Multi-Factor Interaction Analysis

To evaluate non-linear interaction effects, key high-impact factors were evaluated in combination:

```
Combined Impact (C4: Zero Deg + Ideal Eff) = 16,315.63 L reduction
Sum of Individual Impacts (C1 + C2) = 11,315.63 L + 5,125.63 L = 16,441.26 L
Interaction Synergy Offset = -125.63 L (-0.76% non-additive coupling)
```

### Combined Interaction Table

| Interaction Scenario | Deg Penalty ($/kWh) | Efficiency | Diesel Min Pwr | Diesel Fuel (L) | Δ Fuel vs C0 (L) | Battery Discharge (kWh) | EFC |
|---|---|---|---|---|---|---|---|
| **C4 (Zero Deg + Ideal Eff)** | $0.000 | 100.0% | 10 kW | 77,150.00 | -16,315.63 | 9,850.00 | 49.25 |
| **S13 (Zero Deg + 90.25% Eff)** | $0.000 | 90.25% | 10 kW | 78,210.00 | -15,255.63 | 8,943.78 | 44.72 |
| **S14 ($0.01 Deg + 88% Eff)** | $0.010 | 88.00% | 10 kW | 81,450.00 | -12,015.63 | 6,943.20 | 34.72 |
| **S15 ($0.025 Deg + 88% Eff + 0 kW Min)** | $0.025 | 88.00% | 0 kW | 83,210.00 | -10,255.63 | 4,505.60 | 22.53 |

---

## 3. Governance & Defensibility Assessment

1. **Synthetic Penalty Dependence**: Any diesel reduction greater than 5,000 L requires assuming a degradation penalty strictly below $0.025/kWh or an efficiency above 90%.
2. **Lack of Target Hardware Grounding**: Neither the $0.05/kWh penalty nor alternative candidate values are supported by target Nuolja battery evidence.
3. **Conclusion**: Diesel reduction is **CONDITIONALLY DEMONSTRATED** on paper across synthetic sensitivity sweeps, but cannot be promoted to production until target battery identity and physical degradation economics are established.
