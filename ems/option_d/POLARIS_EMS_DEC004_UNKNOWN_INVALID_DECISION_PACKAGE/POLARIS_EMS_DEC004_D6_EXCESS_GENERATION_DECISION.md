# POLARIS EMS — DEC-004-D6: DIESEL MINIMUM OUTPUT EXCESS GENERATION DISPOSITION

> [!IMPORTANT]
> **GOVERNANCE DECISION PREPARATION — HUMAN PROPOSED DIRECTION**
> This document details decision **DEC-004-D6**. The human governance decision-maker has provided a candidate direction. This document analyzes its mathematical, electrical, and safety consequences to prepare it for final sealing.

---

## 1. Governance Question & Human Proposed Direction

**DEC-004-D6**: *How shall excess electrical generation be managed when the diesel generator minimum operating constraint ($P_{\text{D,min}}$) plus available renewables ($P_{\text{RE}}$) produces more power than the remaining protected critical demand ($P_{\text{critical}}$)?*

### Human-Proposed Candidate Policy Direction:
When diesel minimum output exceeds remaining protected critical demand:
1. Apply available renewable generation ($P_{\text{RE}}$) to protected critical demand ($P_{\text{critical}}$) first.
2. Start and dispatch diesel generation ($P_{\text{D}} \ge P_{\text{D,min}}$) to supply remaining critical demand.
3. If diesel minimum output produces excess generation above critical demand:
   - **Absorb excess generation into the battery ($P_{\text{BC}}$) where technically feasible.**
   - **Curtail remaining excess power ($P_{\text{curtail}}$) only after allowable battery charging capacity is exhausted or unavailable.**

*Governance Status*: `HUMAN_PROPOSED_DIRECTION` (Not yet formally sealed as final policy).

---

## 2. Mathematical Equations & Symbolic Form

$$\begin{aligned}
P_{\text{excess}} &= \max\left(0, P_{\text{RE}} + P_{\text{D,min}} - P_{\text{critical}}\right) \\
P_{\text{BC}} &= \min\left(P_{\text{excess}}, P_{\text{BC,max}}, \text{battery\_acceptance}\right) \\
P_{\text{curtail}} &= P_{\text{excess}} - P_{\text{BC}}
\end{aligned}$$

---

## 3. Synthetic Illustrative Numerical Examples

> [!CAUTION]
> **SYNTHETIC ILLUSTRATIVE EXAMPLE ONLY**
> The values below are **NOT STATION DATA**, **NOT DEPLOYMENT PARAMETERS**, and **NOT GOVERNANCE VALUES**.

### Scenario Setup:
- **Conceptual Critical Load**: $7\text{ kW}$
- **Available Renewables**: $3\text{ kW}$ ($2\text{ kW}$ solar + $1\text{ kW}$ wind)
- **Remaining Critical Demand**: $7 - 3 = 4\text{ kW}$
- **Diesel Generator Minimum Power**: $10\text{ kW}$ (`min_power_w = 10000.0` in prototype config)
- **Total Generation**: $3\text{ kW} + 10\text{ kW} = 13\text{ kW}$
- **Gross Excess Power**: $13 - 7 = 6\text{ kW}$

```text
Generation: 13 kW (Renewables 3 kW + Diesel 10 kW)
 ├── Critical Load Served: 7 kW
 └── Gross Excess Power: 6 kW
      ├── Case 1: Battery Accepts 6 kW ──► P_BC = 6 kW, Curtailment = 0 kW
      ├── Case 2: Battery Acceptance 4 kW ─► P_BC = 4 kW, Curtailment = 2 kW
      └── Case 3: Battery Unavailable ───► P_BC = 0 kW, Curtailment = 6 kW
```

### Numerical Cases:
1. **Case 1 (Battery Available & Accepts 6 kW)**:  
   $$P_{\text{BC}} = 6.0\text{ kW}, \quad P_{\text{curtail}} = 0.0\text{ kW}$$  
   *Result*: All excess energy is stored in the battery. Zero renewable/generator curtailment.

2. **Case 2 (Battery Partially Full / Acceptance Capped at 4 kW)**:  
   $$P_{\text{BC}} = 4.0\text{ kW}, \quad P_{\text{curtail}} = 2.0\text{ kW}$$  
   *Result*: $4\text{ kW}$ charges battery; remaining $2\text{ kW}$ excess generation is curtailed.

3. **Case 3 (Battery Full / Faulted / Unavailable)**:  
   $$P_{\text{BC}} = 0.0\text{ kW}, \quad P_{\text{curtail}} = 6.0\text{ kW}$$  
   *Result*: Battery absorbs $0\text{ kW}$; all $6\text{ kW}$ excess generation is curtailed via load bank or inverter curtailment.

---

## 4. Battery Charging Safety & Engineering Requirements

Before the proposed D6 direction can be authorized for implementation, the following engineering conditions must be defined:

1. **Charge Acceptance Limit ($P_{\text{BC,max}}$)**: Maximum safe charge rate during unmonitored degraded operation.
2. **Maximum SOC Ceiling ($SOC_{\text{max}}$)**: Hard cutoff (e.g. $90\%$ or $95\%$) above which charging is prohibited to prevent overcharge.
3. **Thermal Safety Threshold**: Maximum battery temperature above which charging must abort.
4. **Telemetry Validity Requirement**: Rules governing whether battery charging is permitted if telemetry signal is degraded.

---

## 5. Human Decision Form (DEC-004-D6)

```text
DECISION ID: DEC-004-D6
QUESTION: How shall excess diesel generation be disposed under Option D?

HUMAN PROPOSED DIRECTION:
  - Route excess generation to battery charging where feasible.
  - Curtail remaining excess power after battery capacity is exhausted.

FINAL GOVERNANCE SEAL: [ SEAL PROPOSED DIRECTION / MODIFY DIRECTION / REJECT ]

HUMAN DECISION STATUS: HUMAN_PROPOSED_DIRECTION (Awaiting Formal Seal)
AUTHORIZED BY: ___________________________
DATE: _______________
```

Status: `D6_PROPOSED_DIRECTION_ANALYZED`
