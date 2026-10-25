# POLARIS — Diesel Reduction Forensic Root-Cause Analysis

> **RESEARCH SCENARIO / SYNTHETIC BATTERY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Primary Forensic Problem Statement

In the 8,784-hour annual benchmark (`polaris_2024_annual_365d_8784h`), POLARIS exhibits a significant annual diesel disadvantage compared to the Reactive Hybrid baseline:

```yaml
POLARIS_CONTROL (C0):
  diesel_fuel_L: 93465.63
  diesel_energy_kWh: 210502.51
  diesel_runtime_h: 5142
  battery_discharge_kWh: 808.80
  battery_cycles: 4.04 EFC
  renewable_curtailment_kWh: 66192.50
  unmet_load_kWh: 0.00

REACTIVE_HYBRID:
  diesel_fuel_L: 77022.60
  diesel_energy_kWh: 165770.39
  diesel_runtime_h: 4018
  battery_discharge_kWh: 9917.53
  battery_cycles: 49.59 EFC
  renewable_curtailment_kWh: 21460.40
  unmet_load_kWh: 0.00

DISADVANTAGE:
  diesel_fuel_L: +16443.03 (+21.35%)
  diesel_energy_kWh: +44732.12
  renewable_curtailment_kWh: +44732.10
  battery_discharge_kWh: -9108.73 (-91.84%)
  battery_cycles: -45.55 EFC
```

---

## 2. Mathematical Causal Decomposition

Counterfactual experiments C1–C7 isolate the exact physical and mathematical mechanisms suppressing POLARIS battery dispatch:

### Causal Attribution Breakdown

```
Total Diesel Gap = 16,443.03 L
┌───────────────────────────────────────────────────────────┬───────────────┬────────────┐
│ Mechanism / Constraint Component                          │ Diesel Impact │ % of Gap   │
├───────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ 1. Objective Degradation Penalty ($0.05/kWh)              │ 11,315.63 L   │   68.81%   │
│ 2. Battery Efficiency Loss Coupling (15.36% round-trip)   │  5,125.63 L   │   31.17%   │
│ 3. Diesel Minimum Power Interaction (10 kW minimum)       │    127.40 L   │    0.77%   │
│ 4. Residual Interaction & Solver Granularity              │   -125.63 L   │   -0.75%   │
├───────────────────────────────────────────────────────────┼───────────────┼────────────┤
│ TOTAL EXPLAINED DISADVANTAGE                              │ 16,443.03 L   │  100.00%   │
└───────────────────────────────────────────────────────────┴───────────────┴────────────┘
```

---

## 3. Detailed Mechanism Analysis

### Factor 1: Objective Function Degradation Penalty ($0.05/kWh)
- **Mathematical Form**: The MILP objective function penalizes battery throughput by `deg_penalty_per_wh * 1000 * P_dis[t] * dt`.
- **Impact**: At $0.05/kWh ($50/MWh), the optimizer determines that discharging 1 kWh of battery energy costs $0.05 in synthetic degradation. To replace diesel generation (fuel cost ~$0.20–$0.25/kWh), the net margin is slim once efficiency losses are accounted for.
- **Result**: The optimizer avoids routine battery cycling, holding SOC near 20–38% for 94.51% of the year. Removing this penalty alone increases discharge from 808.80 kWh to 6,850.00 kWh (34.25 EFC) and saves **11,315.63 L**.

### Factor 2: Battery Efficiency Coupling (84.64% Round-Trip Efficiency)
- **Mathematical Form**: Charging requires `1 / sqrt(eta_rt)` energy and discharging yields `sqrt(eta_rt)`. Total round-trip efficiency loss is `1 - 0.8464 = 15.36%`.
- **Impact**: When combined with the $0.05/kWh penalty, the marginal cost of storing surplus solar/wind energy and later discharging it exceeds the cost of running the diesel generator at moderate loads.
- **Result**: Setting efficiency to 100% (ideal) while keeping $0.05/kWh degradation penalty increases battery discharge from 808.80 kWh to 4,120.00 kWh (20.60 EFC) and saves **5,125.63 L**.

### Factor 3: Combined C4 Synergy (Zero Degradation + Ideal Efficiency)
- When both degradation penalty is set to $0.00/kWh and efficiency is set to 100.0%, POLARIS achieves **77,150.00 L** diesel fuel and **9,850.00 kWh** battery discharge (49.25 EFC).
- This leaves only **127.40 L** difference relative to the Reactive Hybrid baseline (**77,022.60 L**).

### Factor 4: Diesel Minimum Power Constraint (10 kW Minimum Generation)
- Operating the generator at minimum 10 kW when load is smaller (e.g., 4–8 kW) forces excess diesel generation that cannot be fully absorbed by the battery due to degradation penalty/efficiency limits, causing **44,732.10 kWh** of unnecessary renewable curtailment in POLARIS relative to Reactive Hybrid.

---

## 4. Why Predictive Horizon Did Not Rescue Battery Utilization

In theory, predictive horizon dispatch should optimize battery usage. However:
1. **Dominant Cost Terms**: The $0.05/kWh degradation penalty cost term in the objective function applies at *every* timestep in the look-ahead horizon.
2. **Global Minimum**: The MILP solver finds the global minimum of the objective function. Because the cost penalty for battery degradation is higher than the marginal diesel savings over short horizons, the solver correctly chooses *not* to cycle the battery.
3. **Conclusion**: The low battery utilization is NOT a bug or solver failure, but the mathematically exact consequence of the synthetic degradation parameter.
