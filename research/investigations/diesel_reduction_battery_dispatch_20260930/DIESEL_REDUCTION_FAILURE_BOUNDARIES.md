# POLARIS — Diesel Reduction Failure Boundaries & Boundary Analysis

> **RESEARCH SCENARIO / SYNTHETIC BATTERY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Overview of Failure & Degradation Boundaries

This document establishes the physical, operational, and numerical failure boundaries of battery dispatch for diesel reduction in POLARIS.

---

## 2. Identified Physical & Economic Boundary Thresholds

### Boundary 1: Degradation Penalty Suppression Threshold ($0.05/kWh)
- **Threshold**: `deg_penalty_per_wh > 0.045 $/Wh`
- **Behavior**: When degradation penalty is above $0.045/kWh, annual battery dispatch is suppressed to `< 5 EFC/yr`.
- **Failure Mode**: Economic dispatch shutoff. The battery acts primarily as an emergency reserve rather than a daily cycling asset.

### Boundary 2: Battery Power Capability Limit (< 15 kW)
- **Threshold**: `P_batt_max < 15 kW` (for 200 kWh system, C-rate < 0.075C)
- **Behavior**: Power rating is insufficient to absorb solar/wind peaks or back up load spikes without starting the diesel generator.
- **Result**: Diesel fuel consumption spikes above 95,000 L, and renewable curtailment increases above 70,000 kWh.

### Boundary 3: Battery Energy Capacity Limit (< 50 kWh)
- **Threshold**: `E_batt_max < 50 kWh`
- **Behavior**: Capacity is insufficient to maintain the 6-hour critical load survivability reserve requirement (6 h × 6 kW = 36 kWh net usable + 20% min SOC = 45 kWh minimum required capacity).
- **Result**: At capacities below 45 kWh, solver returns `INFEASIBLE` under 6-hour survivability governance rules.

### Boundary 4: Round-Trip Efficiency Floor (< 75.0%)
- **Threshold**: `eta_rt < 0.750`
- **Behavior**: High energy losses during charge-discharge cycles make battery dispatch net-negative for diesel displacement even when degradation penalty is $0.00/kWh.
- **Result**: Renewable curtailment increases due to energy loss during storage.

### Boundary 5: Generator Minimum Loading Boundary (> 15 kW)
- **Threshold**: `P_diesel_min > 15 kW`
- **Behavior**: Forces severe over-generation during low net-load hours, causing excessive curtailment (> 80,000 kWh) and high fuel consumption (> 98,000 L).

---

## 3. Boundary Matrix Summary

| Parameter | Operational Range | Warning Boundary | Failure Threshold | Failure Consequence |
|---|---|---|---|---|
| **Degradation Penalty** | $0.00–$0.025/kWh | $0.035/kWh | > $0.050/kWh | Battery dispatch suppressed (< 4 EFC/yr) |
| **Battery Power** | 25–100 kW | 15–20 kW | < 12 kW | Cannot catch net-load ramps |
| **Battery Capacity** | 100–400 kWh | 50–70 kWh | < 45 kWh | MILP solver INFEASIBLE under 6h survivability |
| **Round-Trip Efficiency** | 84.64–90.25% | 78.0% | < 75.0% | Net fuel penalty from cycle losses |
| **SOC Minimum** | 10–25% | 28.0% | > 35.0% | Operational window choked, dispatch suppressed |

---

## 4. Governance Implications

> [!CAUTION]
> POLARIS must NOT be operated with battery capacity < 45 kWh or degradation penalty parameters arbitrarily set to zero without physical hardware backing. Attempting to force diesel reduction by overriding physical limits leads to infeasibility or premature battery destruction.
