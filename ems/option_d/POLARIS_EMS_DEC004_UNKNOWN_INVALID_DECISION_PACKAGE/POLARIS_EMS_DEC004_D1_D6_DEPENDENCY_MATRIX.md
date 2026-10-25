# POLARIS EMS — DEC-004 D1–D6 CROSS-DECISION DEPENDENCY MATRIX

## 1. Executive Summary

This document maps the cross-decision interactions, coupling, and dependencies across Option D decisions **D1 through D6**. Resolving one decision impacts resource limits, escalation triggers, and power balance boundaries in adjacent decisions.

---

## 2. Interaction & Dependency Matrix

| Decision Domain | Affects D1 (Critical Load) | Affects D2 (Battery) | Affects D3 (Resource Fail) | Affects D4 (Shortfall) | Affects D5 (Escalation) | Affects D6 (Excess Power) |
|-----------------|---------------------------|----------------------|---------------------------|------------------------|-------------------------|---------------------------|
| **D1: Critical Load** | — | Determines discharge rate & duration | Defines deficit threshold ($P_{\text{supply}} < P_{\text{critical}}$) | Primary input for shortfall calculation | Higher critical load accelerates resource depletion | Defines net load before diesel minimum excess |
| **D2: Battery Policy** | Constrains available reserve power | — | Determines whether battery provides fallback supply | Supplies discharge power to mitigate shortfall | Battery capacity determines degraded run-time | Accepts excess diesel power ($P_{\text{BC}}$) |
| **D3: Resource Fail** | Forces load shedding if 0 supply | May trigger emergency battery discharge | — | Creates maximum critical load shortfall | Triggers early watchdog escalation | N/A (0 active generation) |
| **D4: Shortfall Policy** | Determines category priority order | N/A | Triggered when active resources fail | — | Critical shortfall triggers immediate escalation | N/A (Deficit state; no excess) |
| **D5: Escalation Watchdog** | Limits duration of critical load service | Sets max time for battery charging/discharging | Limits duration of 0-supply blackout | Sets max time allowed in critical shortfall | — | Limits duration of diesel excess charging |
| **D6: Excess Power** | Ensures critical load is fully powered | Provides charging power to battery ($P_{\text{BC}}$) | N/A | N/A | Excess fuel burn affects run-time limit | — |

---

## 3. Key Interdependency Findings

1. **D1 $\to$ D6 Coupling**: The magnitude of $P_{\text{critical}}$ directly controls $P_{\text{excess}} = \max(0, P_{\text{RE}} + P_{\text{D,min}} - P_{\text{critical}})$. A larger critical load reduces excess power available to charge the battery under D6.
2. **D2 $\to$ D6 Coupling**: The human-proposed D6 direction (charging battery with excess diesel power) is physically and logically dependent on D2 establishing battery charge acceptance rules and safety limits.
3. **D3 / D4 $\to$ D5 Coupling**: Resource failure (D3) or critical load shortfall (D4) represents severe degraded operation, which should accelerate escalation to `CRITICAL_TERMINATION` under D5.

---

## 4. Required Sequence of Human Governance Sealing

To prevent circular dependency, human governance decisions should be sealed in the following logical sequence:

```text
Step 1: D1 (Define Protected Critical Load)
   │
   ▼
Step 2: D6 (Confirm Excess Diesel Disposition Policy)
   │
   ▼
Step 3: D2 (Confirm Battery Fallback & Safety Rules)
   │
   ▼
Step 4: D3 (Confirm Zero-Resource Fallback Action)
   │
   ▼
Step 5: D4 (Confirm Critical Shortfall Shedding Priority)
   │
   ▼
Step 6: D5 (Confirm Watchdog & Escalation Limits)
```

Status: `DEPENDENCY_MATRIX_SEALED`
