# POLARIS — Optimizer Decision Forensics

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Decision Logic Trace for Representative Disadvantage Periods

This document traces why the MILP solver chose diesel generation over battery discharge during specific representative periods in the annual trajectory.

---

## 2. Representative Sample Trace (Hour 4,120 to Hour 4,144 — Summer Net Load Spike)

- **Context**: Solar generation drops for 4 hours; net load = 8.5 kW. Battery SOC = 35.0% (usable energy = 30 kWh).
- **Physical State**: Battery power available (50 kW), SOC available (35% > 20% min), telemetry valid (T0).

### Optimizer Evaluation Breakdown (C0 Control vs Exp B)

| Parameter / Cost Term | POLARIS C0 Control | Experiment B (~50 EFC) |
|---|---|---|
| **Degradation Penalty per Wh** | $0.00005 ($0.05/kWh) | $0.00000 ($0.00/kWh) |
| **Round-Trip Efficiency** | 84.64% | 100.0% |
| **Battery Discharge Cost** | $0.05 / kWh + $0.035 (eff loss) = **$0.085/kWh** | **$0.000/kWh** |
| **Marginal Diesel Fuel Cost** | **$0.078/kWh** (at efficient generator operating point) | **$0.078/kWh** |
| **MILP Decision** | **DISCHARGE BLOCKED** — Diesel selected | **DISCHARGE ENABLED** — Battery selected |
| **Diesel Burned** | 7.8 L | 0.0 L |

---

## 3. Mathematical Explanation of Optimizer Behavior

The MILP solver minimizes total objective cost over the 24-hour lookahead horizon:

$$\min \sum_{t=1}^{T} \left( c_{\text{fuel}} \cdot F_{\text{diesel}}[t] + c_{\text{deg}} \cdot P_{\text{dis}}[t] \cdot \Delta t + c_{\text{start}} \cdot S[t] + c_{\text{curt}} \cdot P_{\text{curt}}[t] \right)$$

Because $c_{\text{deg}} = 0.00005$ $/Wh ($50/MWh) adds a direct linear penalty on every Wh of battery discharge, the solver correctly calculates that cycling the battery to replace diesel generation increases total objective cost whenever generator efficiency is moderate or high.

> [!KEY-FINDING]
> The optimizer is **not malfunctioning**. It is solving the objective function with exact mathematical optimality. The high diesel consumption is the mathematically intended outcome of encoding a $0.05/kWh linear wear penalty into the objective function.
