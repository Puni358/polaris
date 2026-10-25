# POLARIS EMS — EMERGENCY POLICY BOUNDARY AUDIT

## 1. Executive Summary

This document establishes the strict separation between **Emergency Condition Detection** (the ECD's responsibility) and **Emergency Dispatch Policy Execution** (the downstream EMS Mode Manager's responsibility).

---

## 2. Separation of Responsibilities

| Domain Component | Primary Responsibility | Allowed Actions | Forbidden Actions |
|------------------|------------------------|-----------------|-------------------|
| **Emergency Condition Detector (ECD)** | Survivability calculation & state classification | Calculate $T_{\text{battery}}$, $T_{\text{diesel}}$, margins, E3 resource relationships; output `EmergencyAssessment` | Start/stop generators, shed load, modify optimizer parameters, alter control setpoints |
| **EMS Mode Manager / Policy Layer (Downstream)** | Emergency policy selection | Interpret `EmergencyAssessment`, select optimizer objective function (e.g. E3 preservation), trigger load shedding rules | Recalculate physical survivability margins, override security/freshness fail-closed states |

---

## 3. E3 Resource Preservation Interface

The ECD supplies E3 resource classifications to the EMS Policy Layer:
- `preserved_resource = BATTERY` $\implies$ Policy Layer configures optimizer to minimize battery discharge / preserve SOC.
- `preserved_resource = DIESEL` $\implies$ Policy Layer configures optimizer to minimize diesel generation / conserve fuel.
- `preserved_resource = TIE / BOTH` $\implies$ Policy Layer applies balanced default preservation policy (no preference).

Status: `ESTABLISHED`
