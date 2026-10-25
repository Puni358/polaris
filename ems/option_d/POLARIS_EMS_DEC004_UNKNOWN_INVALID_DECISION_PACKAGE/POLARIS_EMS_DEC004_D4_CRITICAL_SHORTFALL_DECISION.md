# POLARIS EMS — DEC-004-D4: CRITICAL-LOAD SHORTFALL SHEDDING POLICY

> [!IMPORTANT]
> **GOVERNANCE DECISION PREPARATION**
> This document prepares decision **DEC-004-D4** for human governance review. It analyzes shedding policies when available generation is insufficient to supply full protected critical load. It does **NOT** select or approve a policy.

---

## 1. Exact Governance Question

**DEC-004-D4**: *What shedding or allocation policy shall apply when available generation/storage power ($P_{\text{supply}}$) is physically less than the authorized protected critical load demand ($P_{\text{supply}} < P_{\text{critical}}$)?*

---

## 2. Authoritative Evidence & Technical Boundaries

### 2.1 Established Evidence
- **Supply Deficit**: If $P_{\text{supply}} < P_{\text{critical}}$, unmet critical demand is positive ($P_{\text{unmet}} = P_{\text{critical}} - P_{\text{supply}} > 0$).
- **Protection vs. Guarantee**: Governance Option D attempts to *protect* critical loads, but cannot *guarantee* 100% service when physical energy resources are deficient.

### 2.2 Unestablished Items (Requires Definition)
- **Critical Category Hierarchy**: Unresolved whether essential heating, water treatment, and communications have equal priority or a ranked priority hierarchy (e.g. Heating > Water > Comms).
- **Partial Service Safety**: Unresolved whether operating a critical load category at partial voltage/power is safe or causes equipment damage.

---

## 3. Policy Candidate Options for Human Review

- **Option D4-A (Ranked Priority Shedding)**: Shed critical load categories according to an authorized hierarchy (e.g., shed Communications first ($1\text{ kW}$), then Water ($2\text{ kW}$), preserving Heating ($4\text{ kW}$)).
- **Option D4-B (Proportional Shedding / Brownout)**: Reduce power proportionally across all active critical load circuits.
- **Option D4-C (Total Critical Trip)**: If 100% critical load cannot be maintained, trip all critical circuits to prevent equipment brownout and initiate immediate operator escalation.

---

## 4. Synthetic Illustrative Numerical Example

> [!CAUTION]
> **SYNTHETIC ILLUSTRATIVE EXAMPLE ONLY**
> The values below are **NOT STATION DATA**, **NOT DEPLOYMENT PARAMETERS**, and **NOT GOVERNANCE VALUES**.

### Scenario Setup:
- **Conceptual Critical Load**: $7\text{ kW}$ ($4\text{ kW}$ Heating + $2\text{ kW}$ Water + $1\text{ kW}$ Comms)
- **Available Renewables**: $2\text{ kW}$
- **Available Diesel Generation**: $3\text{ kW}$
- **Total Available Supply**: $2 + 3 = 5\text{ kW}$
- **Critical Load Deficit**: $7 - 5 = 2\text{ kW}$

### Option Outcomes under Example:
- **Under Option D4-A (Ranked Priority)**: Shed Comms ($1\text{ kW}$) + partial Water ($1\text{ kW}$). Serve Heating ($4\text{ kW}$) + Water ($1\text{ kW}$). Served = $5\text{ kW}$.
- **Under Option D4-B (Proportional)**: Supply each load at $\frac{5}{7} \approx 71.4\%$ power allocation.
- **Under Option D4-C (Total Trip)**: Shed all $7\text{ kW}$ critical load. Served = $0\text{ kW}$.

---

## 5. Cross-Decision Interactions & Dependencies

- **Interaction with D1 (Critical Load Definition)**: D1 category definitions directly feed D4 priority hierarchy.
- **Interaction with D5 (Escalation)**: Critical shortfall ($P_{\text{unmet}} > 0$) triggers immediate D5 escalation.

---

## 6. Required Engineering Definitions

1. Category priority ranking authorized by station life-safety officer.
2. Minimum power threshold below which water treatment or heating units trip on low-voltage protection.

---

## 7. Human Decision Form (DEC-004-D4)

```text
DECISION ID: DEC-004-D4
QUESTION: What shedding policy applies when generation is less than critical load under Option D?

SELECTED POLICY OPTION: [ D4-A (Ranked Priority) / D4-B (Proportional) / D4-C (Total Trip) / OTHER ]

HUMAN DECISION STATUS: UNRESOLVED (Awaiting Human Selection)
AUTHORIZED BY: ___________________________
DATE: _______________
```

Status: `D4_DECISION_PREPARATION_COMPLETE`
