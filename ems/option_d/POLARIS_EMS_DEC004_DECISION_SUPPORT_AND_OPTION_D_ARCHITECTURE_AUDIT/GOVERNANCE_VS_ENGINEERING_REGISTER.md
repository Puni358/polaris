# POLARIS EMS — GOVERNANCE VS. ENGINEERING PARAMETER REGISTER

## 1. Executive Summary

This register strictly separates unresolved items into three distinct domains: **Human Governance Decisions**, **Station Engineering Inputs**, and **Implementation Definitions**. This separation prevents technical implementation from usurping human policy authority.

---

## 2. Categorized Registers

### LIST A — HUMAN GOVERNANCE DECISIONS STILL REQUIRED
1. **Final DEC-004 Candidate Selection**: Formal human selection of operational response across Option A (Hold Plan), Option B (Zero Dispatch), Option C (Operator Trip), and Option D (Protected Critical Fallback).
2. **DEC-001 / BLK-006 Production $T_{\text{required}}$ Horizon**: Production numerical value and override TTL for target survivability horizon.
3. **DEC-002 / BLK-007 Telemetry Maximum Age**: Production maximum allowable age for SCADA telemetry payloads.
4. **DEC-003 / BLK-008 Ingress Signature Scheme**: Production cryptographic authentication scheme for upstream payloads.
5. **Option D Watchdog Duration Limit ($T_{\text{max,degraded}}$)**: Maximum allowed time in degraded Option D before mandatory operator escalation.
6. **Minimum Fuel Reserve Threshold ($F_{\text{reserve,min}}$)**: Minimum fuel reserve floor triggering mandatory escalation.

---

### LIST B — STATION ENGINEERING INPUTS REQUIRED
7. **Protected Critical Equipment Inventory**: Site-specific list of physical equipment belonging to Heating, Water, and Comms categories.
8. **Electrical Breaker / Panel Mapping**: Hardware mapping connecting physical load switches to critical categories.
9. **Dynamic Load Calculation Model ($P_{\text{critical}}(t)$)**: Thermal and operational functions defining required critical power under varying ambient conditions.
10. **Minimum Viable Operating Levels ($P_{\text{min,viable}}$)**: Minimum power threshold below which each critical system cannot safely operate.
11. **Inrush / Surge Current Tolerance**: Generator and battery surge capacity requirements for motor startup.
12. **Generator Turndown Ratio & Minimum Power ($P_{\text{D,min}}$)**: Site-specific continuous minimum loading limit for physical diesel generator.
13. **Generator Fuel Burn Curve**: Measured or nameplate fuel consumption curve ($F = f(P)$) for physical generator set.
14. **Battery Charge Acceptance Limit ($P_{\text{BC,max}}$)**: Maximum continuous active charge power allowable for battery bank.
15. **Battery Reserve Floor ($SOC_{\text{min}}$)**: Hard minimum SOC boundary for battery discharge.
16. **Battery Maximum SOC Ceiling ($SOC_{\text{max}}$)**: Hard maximum SOC boundary to halt charging.
17. **Battery Thermal Cutoff Limits**: Temperature thresholds for charge/discharge lockout.

---

### LIST C — IMPLEMENTATION DEFINITIONS REQUIRED
18. **Mode Transition State Handling**: Software state machine logic for transitioning between `NORMAL`, `UNKNOWN_INVALID`, and `CRITICAL_TERMINATION`.
19. **MILP Constraint Representation**: Formulation of linear proportional fairness constraints for critical load shortfall.
20. **Escalation Event Representation**: Schema definition for emitting D4/D5 escalation alerts.
21. **State Recovery Behavior**: Runner logic for discarding degraded plans and resuming 24h MILP optimization upon valid ECD return.
22. **Additive Schema Extensions**: Addition of `protected_critical_load_w` and `shed_noncritical_load_w` fields to `DispatchPlan`.
23. **Policy Router Placement**: Wiring of `OptionDPolicyRouter` inside `PolarisLocalRunner`.

---

## 3. Separation Summary

```text
GOVERNANCE_DECISIONS_REQUIRED   = 6
ENGINEERING_INPUTS_REQUIRED     = 11
IMPLEMENTATION_DEFINITIONS      = 6
TOTAL_REGISTERED_ITEMS          = 23
```

Status: `REGISTER_SEALED`
