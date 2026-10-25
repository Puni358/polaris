# POLARIS EMS — HD-05D Governance Gap Report

**Audit Objective**: Identify the precise remaining unresolved items that require human governance decisions before HD-05 can be implemented in production.

---

## 1. Closed vs. Open Decision Summary

### CLOSED Decisions (Fixed Policy — Do Not Reopen)
- **HD-05A**: Battery degradation/cycling belongs in **Stage 3 — Resource Management**.
- **HD-05B**: Extra diesel fuel may be consumed during **NORMAL operation** to reduce unnecessary battery cycling.
- **HD-05C**: Battery degradation is subordinate to critical service and emergency resilience during **EMERGENCY operation**.

---

### OPEN Decisions (Unresolved Governance Gaps)

| Gap ID | Description | Impact on Implementation | Resolution Options |
| :--- | :--- | :--- | :--- |
| **GAP-HD05D-1** | **Stage-3 Mathematical Structure Selection** | Determines whether Stage 3 uses scalar weighting, constraints, or lexicographic subobjectives. | Select Option A (Monetary), B (Liter-based), C (Constrained), or D (Lexicographic). |
| **GAP-HD05D-2** | **Numerical Parameter Selection** | Provides the specific quantitative knob needed for the selected Stage-3 structure. | Depending on Gap 1:<br>- Option A: Authorize fuel price $[\$/\text{L}]$ and degradation value $[\$/\text{Wh}]$.<br>- Option B: Authorize exchange factor $\lambda_{\text{deg}} \ [\text{L/\text{Wh}}]$.<br>- Option C: Authorize max cycling budget $B_{\text{deg}} \ [\text{Wh}]$.<br>- Option D: Authorize fuel tolerance $\epsilon$ (e.g. $1-5\%$). |
| **GAP-HD05D-3** | **Emergency Degradation Subordination Encoding** | Determines how HD-05C is mathematically implemented during Emergency Mode. | - Option 1: Zero degradation weight ($c_{\text{deg}} = 0$) during Emergency.<br>- Option 2: Omit Stage 3 entirely during Emergency.<br>- Option 3: Relax cycling budget $B_{\text{deg}} \to \infty$ during Emergency. |
| **GAP-HD05D-4** | **Schema Additions for Battery Degradation** | Determines what degradation metrics should be tracked in `StationState` and telemetry. | Add cumulative battery throughput $[\text{Wh}]$ or estimated equivalent full cycles to state schemas. |

---

## 2. Hard Authorization Requirements

Implementation of Stage-3 objective logic or modifications to solver code (`milp.py`) **MUST NOT PROCEED** until:

1. Human governance approves a specific mathematical formulation option for Stage 3 (Gap 1).
2. Human governance authorizes the corresponding quantitative parameter (Gap 2).
3. Human governance authorizes the emergency subordination encoding (Gap 3).
