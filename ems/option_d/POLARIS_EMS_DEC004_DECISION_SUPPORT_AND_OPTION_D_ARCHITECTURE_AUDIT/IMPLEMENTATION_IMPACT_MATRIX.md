# POLARIS EMS — DEC-004 IMPLEMENTATION IMPACT MATRIX

## 1. Executive Summary

This document details the component-by-component software, schema, testing, and operational impact for Candidate Options **A**, **B**, **C**, and **D**.

---

## 2. Implementation Impact Comparison Table

| Component / Layer | Option A: Hold Last Plan | Option B: Zero Dispatch | Option C: Operator Intervention | Option D: Protected Critical Fallback |
|-------------------|--------------------------|-------------------------|---------------------------------|--------------------------------------|
| **Runtime Runner (`runner.py`)** | Cache `last_valid_dispatch_plan`; substitute plan when ECD outputs `UNKNOWN_INVALID`. | Intercept `UNKNOWN_INVALID`; solve 0-power dispatch plan ($P=0$). | Intercept `UNKNOWN_INVALID`; raise `CRITICAL_TERMINATION` fault. | Add `OptionDPolicyRouter`; suppress noncritical load; dispatch critical load. |
| **Schema Impact** | Additive `plan_hold_count` in `DispatchPlan` metadata. | Additive `FaultEvent` class code. | Additive `FaultEvent` class code. | Additive `protected_critical_load_w` & `shed_noncritical_load_w` in `DispatchPlan`. |
| **ECD Core (`ecd.py`)** | None (pure evaluator). | None (pure evaluator). | None (pure evaluator). | None (pure evaluator). |
| **Mode / Policy Layer** | Consumes `UNKNOWN_INVALID`; triggers plan hold state. | Consumes `UNKNOWN_INVALID`; triggers 0-power state. | Consumes `UNKNOWN_INVALID`; triggers terminal trip. | Consumes `UNKNOWN_INVALID`; engages Option D degraded policy router. |
| **MPC Loop** | Re-applies prior plan steps. | Advances state via 0-power state. | Suspends MPC execution. | Advances state via critical-only MILP dispatch. |
| **EnergyOptimizer (`milp.py`)** | Bypassed during hold period. | Bypassed (0-power hardcoded). | Bypassed (pipeline halted). | Solves receding-horizon MILP with demand = $P_{\text{critical}}(t)$. |
| **DigitalTwinSimulator** | Advances simulator using held setpoints. | Advances simulator using 0-power physics. | Frozen at fault step. | Advances simulator using critical-only power flow. |
| **Telemetry Requirements** | Requires last valid plan timestamp. | Requires battery energy & fuel telemetry. | Requires fault logging endpoint. | Requires dynamic $P_{\text{critical}}(t)$ & breaker status telemetry. |
| **Operator HMI / SCADA** | Exposes hold plan warning icon. | Exposes 0-dispatch degraded alarm. | Exposes `CRITICAL_TERMINATION` lockout alarm. | Exposes Option D degraded alarm & D4/D5 escalation alerts. |
| **Testing Burden** | Integration test for plan caching & watchdog. | Integration test for 0-power state advancement. | Integration test for pipeline halt. | Integration tests for critical load shedding & excess diesel charging. |
| **Unresolved Engineering Inputs** | Maximum allowed hold duration limit. | None (uses 0-power physics). | None (uses runner halt). | Critical equipment mapping, $P_{\text{critical}}(t)$, minimum viable levels $P_{\text{min,viable}}$, battery limits. |
| **Unresolved Governance Inputs** | Hold plan watchdog policy. | Policy sign-off on 0-dispatch. | Policy sign-off on terminal trip. | DEC-004 final selection across A, B, C, D. |

Status: `IMPACT_MATRIX_SEALED`
