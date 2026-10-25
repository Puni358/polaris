# POLARIS EMS — DEC-004 OPTION D GOVERNANCE ANALYSIS (D1–D6)

## 1. Executive Summary

This document establishes the overarching governance analysis framework for the six operational resolution questions (**D1 through D6**) required to fully specify **Option D: Protected Critical-Load Fallback** for **DEC-004 (Operational Response to ECD UNKNOWN_INVALID)**.

Option D is a candidate operating concept designed to preserve authorized life-safety loads while awaiting valid telemetry or human operator intervention. This document provides the mathematical equations, failure-state distinctions, and evidence boundaries required for human governance decision-making.

---

## 2. Formal Governance Power-Balance Equations

The following conceptual power-balance equations govern Option D analysis. They describe instantaneous electrical power allocation and resource constraints without implementing optimization logic:

### 2.1 Variables & Definitions
- $P_{\text{critical}}$: Authorized protected critical load demand [kW]
- $P_{\text{RE}} = P_{\text{solar}} + P_{\text{wind}}$: Immediately available uncurtailed renewable generation [kW]
- $P_{\text{D}}$: Active diesel generator active power output [kW]
- $P_{\text{BD}}$: Battery active discharge power supplied to load [kW]
- $P_{\text{BC}}$: Active battery charging power absorbed from generation [kW]
- $P_{\text{supply}}$: Total available electrical generation/discharge power [kW]

### 2.2 Power Balance & Allocation Equations
$$\begin{aligned}
P_{\text{supply}} &= P_{\text{RE}} + P_{\text{D}} + P_{\text{BD}} \\
P_{\text{served}} &= \min(P_{\text{critical}}, P_{\text{supply}}) \\
P_{\text{unmet}} &= \max(0, P_{\text{critical}} - P_{\text{supply}}) \\
P_{\text{excess}} &= \max(0, P_{\text{supply}} - P_{\text{critical}}) \\
P_{\text{BC}} &= \min(P_{\text{excess}}, P_{\text{BC,max}}, \text{battery\_acceptance}) \\
P_{\text{curtail}} &= \max(0, P_{\text{excess}} - P_{\text{BC}})
\end{aligned}$$

*Note: These equations represent conceptual governance constraints only and do NOT constitute implemented control logic.*

---

## 3. Failure-State Taxonomy & Separation

Option D maintains strict separation between operational microgrid failure states:

```
┌────────────────────────────────────────────────────────────────────────┐
│                         ECD Input Evaluation                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌─────────────────────┐                           ┌─────────────────────┐
│    Inputs Valid     │                           │   Inputs Invalid    │
└──────────┬──────────┘                           └──────────┬──────────┘
           │                                                 │
     ┌─────┴─────┐                                           ▼
     ▼           ▼                                ┌─────────────────────┐
┌─────────┐ ┌───────────┐                         │   UNKNOWN_INVALID   │
│ NORMAL  │ │ EMERGENCY │                         └──────────┬──────────┘
└─────────┘ └───────────┘                                    │
                                           ┌─────────────────┴─────────────────┐
                                           ▼                                   ▼
                                 ┌───────────────────┐               ┌───────────────────┐
                                 │ Generation Match  │               │Resource Shortfall │
                                 └───────────────────┘               └───────────────────┘
```

1. **`NORMAL`**: Inputs are valid; ECD verifies endurance $T \ge T_{\text{required}}$; full 24-hour MILP optimization (`EnergyOptimizer`) authorized.
2. **`EMERGENCY`**: Inputs are valid; ECD verifies endurance $T < T_{\text{required}}$; governed emergency dispatch activated.
3. **`UNKNOWN_INVALID`**: Telemetry missing, corrupt, stale, or unauthenticated; survivability cannot be established. EMS enters candidate Option D fallback.
4. **`UNKNOWN_INVALID + RESOURCE_SHORTFALL`**: Generation/storage physically insufficient to meet critical demand ($P_{\text{supply}} < P_{\text{critical}}$).
5. **`UNKNOWN_INVALID + CRITICAL_LOAD_SHORTFALL`**: Unmet critical load persists ($P_{\text{unmet}} > 0$).

---

## 4. Summary Status of D1–D6 Resolution Questions

| Decision ID | Question Description | Established Evidence | Status |
|-------------|----------------------|----------------------|--------|
| **D1** | Exact Protected Critical-Load Definition | 3 conceptual categories (heating, water, comms) | `HUMAN_DECISION_REQUIRED` |
| **D2** | Battery Behavior during Option D | Excess diesel charging proposed; discharge unresolved | `HUMAN_DECISION_REQUIRED` |
| **D3** | Zero Renewables + Diesel Unavailable | 0 kW automated generation state | `HUMAN_DECISION_REQUIRED` |
| **D4** | Critical Load Cannot Be Fully Supplied | Supply deficit ($P_{\text{supply}} < P_{\text{critical}}$) mechanics | `HUMAN_DECISION_REQUIRED` |
| **D5** | Maximum Option D Duration / Escalation | Degraded mode watchdog boundary | `HUMAN_DECISION_REQUIRED` |
| **D6** | Diesel Minimum Output Exceeds Critical Demand | Human-proposed direction: charge battery, then curtail | `HUMAN_PROPOSED_DIRECTION` |

Status: `GOVERNANCE_ANALYSIS_SEALED`
