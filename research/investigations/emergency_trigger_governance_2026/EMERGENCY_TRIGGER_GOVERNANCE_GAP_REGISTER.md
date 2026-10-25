# POLARIS — EMERGENCY TRIGGER GOVERNANCE GAP REGISTER

## Executive Summary

This register explicitly catalogues all **UNRESOLVED GOVERNANCE DECISIONS** and **ENGINEERING ASSUMPTIONS** identified during the mathematical reconciliation pass. 

To preserve governance integrity, no engineering assumption has been promoted to a human-approved governance decision. All items below are flagged for human review prior to production code implementation.

---

## 1. Unresolved Governance & Assumption Register

| Gap ID | Parameter / Logic Area | Current Implementation Assumption | Governance Status | Consequences & Options for Human Decision |
| :---: | :--- | :--- | :--- | :--- |
| **GAP-01** | **Dispatchable Generator Credibility Model** | Model assumes $E_{\text{gen}} = P_{\text{gen\_max}} \times 6\text{ h}$ (Unbounded maximum generator capability). | `UNRESOLVED_GOVERNANCE_DECISION` | **Option A**: Unbounded potential energy ($P_{\text{max}} \times 6\text{h}$).<br>**Option B**: Cap generator energy at net critical load demand.<br>**Option C**: Bounded by measured day-tank fuel volume. |
| **GAP-02** | **Renewable Forecast Derating Factors** | Derates solar/wind forecast by 50% ($\gamma_{\text{solar}} = 0.50, \gamma_{\text{wind}} = 0.50$). | `ENGINEERING_ASSUMPTION` | **Option A**: Retain conservative 50% confidence factor.<br>**Option B**: Use 100% raw forecast ($0.0$ derating).<br>**Option C**: Set renewable contribution to 0.0 for emergency survivability. |
| **GAP-03** | **Emergency Exit Hysteresis Margin** | Requires $M_{\text{surv}} \ge +10.0\text{ kWh}$ buffer before exiting Emergency Mode. | `ENGINEERING_ASSUMPTION` | **Option A**: Retain $+10.0\text{ kWh}$ hysteresis buffer.<br>**Option B**: Require $M_{\text{surv}} \ge 0.0\text{ kWh}$ (Zero buffer).<br>**Option C**: Require battery $SOC \ge 50.0\%$. |
| **GAP-04** | **Emergency Exit Persistence Window** | Requires satisfying exit criteria for $P = 4$ consecutive intervals (1.0 hour). | `ENGINEERING_ASSUMPTION` | **Option A**: Retain 4 intervals (1 hour).<br>**Option B**: Reduce to 2 intervals (30 minutes).<br>**Option C**: Allow instant exit upon 1 valid interval. |
| **GAP-05** | **Emergency Exit Generator Availability Requirement** | Requires at least one primary diesel generator to be operational ($A_k = 1$) for automatic exit. | `UNRESOLVED_GOVERNANCE_DECISION` | **Option A**: Require mandatory online generator for automatic exit.<br>**Option B**: Allow exit on high battery SOC ($>80\%$) even if diesel is offline. |

---

## 2. Complete Governance Parameter Classification Matrix

| Parameter Name | Value / Rule | Classification | Status & Authority |
| :--- | :---: | :--- | :--- |
| Validated Critical-Load Service Failure Trigger | Immediate | `GOVERNED_HUMAN_DECISION` | **APPROVED** (Decision 1) |
| Imminent Survivability Failure Trigger ($M_{\text{surv}} < 0$) | Preemptive | `GOVERNED_HUMAN_DECISION` | **APPROVED** (Decision 2) |
| Reserve Deficit Alone Never Triggers Emergency | Locked Rule | `GOVERNED_HUMAN_DECISION` | **APPROVED** (Decision 3) |
| Resource Loss Adequacy Assessment | Dynamic | `GOVERNED_HUMAN_DECISION` | **APPROVED** (Decision 4) |
| Automatic Exit with Operator Override | Enabled | `GOVERNED_HUMAN_DECISION` | **APPROVED** (Decision 5) |
| Nominal Battery Capacity ($C_{\text{nom}}$) | $200.0\text{ kWh}$ | `DOCUMENTED_PROJECT_FACT` | Fixed Benchmark Parameter |
| Physical Minimum SOC ($SOC_{\text{min}}$) | $20.0\%$ | `DOCUMENTED_PROJECT_FACT` | Fixed Physical Parameter |
| Physical Maximum SOC ($SOC_{\text{max}}$) | $95.0\%$ | `DOCUMENTED_PROJECT_FACT` | Fixed Physical Parameter |
| Discharge Efficiency ($\eta_{\text{dis}}$) | $0.92$ | `DOCUMENTED_PROJECT_FACT` | Fixed Electrical Parameter |
| Protected Critical Load ($P_{\text{critical}}$) | $11.6\text{ kW}$ | `DOCUMENTED_PROJECT_FACT` | Fixed Load Parameter |
| Required Critical Autonomy ($T_{\text{autonomy}}$) | $6.0\text{ hours}$ | `DOCUMENTED_PROJECT_FACT` | Fixed Requirement |
| Stored Reserve Target ($E_{\text{reserve\_stored}}$) | $75.652\text{ kWh}$ | `DERIVED_MATHEMATICAL_VALUE` | Derived: $(11.6 \times 6) / 0.92$ |
| Stored Reserve Target SOC ($SOC_{\text{target}}$) | $37.826\%$ | `DERIVED_MATHEMATICAL_VALUE` | Derived: $75.652 / 200.0$ |
| Required Critical Delivered Energy | $69.60\text{ kWh}$ | `DERIVED_MATHEMATICAL_VALUE` | Derived: $11.6 \times 6.0$ |
| Deliverable Energy at 37.83% SOC | $32.80\text{ kWh}$ | `DERIVED_MATHEMATICAL_VALUE` | Derived: $(0.37826 - 0.20) \times 200 \times 0.92$ |
| Historical Standalone J2 Target SOC | $57.826\%$ | `DERIVED_MATHEMATICAL_VALUE` | Historical Reference |
| Generator Credibility Model | Unbounded ($P_{\text{max}} \times 6\text{h}$) | `UNRESOLVED_GOVERNANCE_DECISION` | **GAP-01** (Requires Decision) |
| Renewable Confidence Factors ($\gamma_{\text{solar}}, \gamma_{\text{wind}}$) | $0.50$ | `ENGINEERING_ASSUMPTION` | **GAP-02** (Requires Review) |
| Exit Buffer Margin ($M_{\text{exit\_margin}}$) | $+10.0\text{ kWh}$ | `ENGINEERING_ASSUMPTION` | **GAP-03** (Requires Review) |
| Exit Persistence Window | $4\text{ intervals}$ ($1.0\text{h}$) | `ENGINEERING_ASSUMPTION` | **GAP-04** (Requires Review) |
| Exit Diesel Availability Requirement | Mandatory | `UNRESOLVED_GOVERNANCE_DECISION` | **GAP-05** (Requires Decision) |
