# POLARIS EMS — DEC-004 GOVERNANCE RESOLUTION (D1–D6 DEFINITIONS)

## Executive Resolution Statement

This document formally records the consolidated, internally consistent policy rules **D1 through D6** governing **Option D — Protected Critical-Load Fallback** under **DEC-004: UNKNOWN_INVALID Operational Response**.

These six governance rules were formulated during prior decision preparation and are hereby sealed as authoritative policy rules. They must not be modified or reinterpreted during future engineering definition or software implementation.

---

## Sealed Governance Rules D1–D6

### Rule D1: DYNAMIC CRITICAL-LOAD REQUIREMENT
- Protected critical equipment is defined strictly by station engineering and policy.
- Required critical power may vary dynamically across time steps, represented conceptually as $P_{\text{critical}}(t)$.
- The EMS optimizer must **NOT** dynamically reclassify noncritical loads into protected equipment or vice versa.
- Conceptual protected critical categories include:
  1. Essential space heating required for human survivability in extreme environments.
  2. Essential water treatment, pumping, and filtration.
  3. Emergency communications, telemetry, and control systems.
- Station-specific equipment, circuit, and breaker mappings remain open site-engineering inputs.

### Rule D2: RESTRICTED BATTERY DISCHARGE
- Energy Storage System (ESS / Battery) discharge is permitted **ONLY** to support protected critical systems ($P_{\text{critical}}$).
- The battery is **NOT** a general station energy source during Option D degraded operations.
- The battery must **NOT** support noncritical loads under any circumstances during Option D.
- Battery discharge may support critical systems when renewable generation plus diesel generation are insufficient or unavailable.
- Exact battery discharge SOC boundaries remain unresolved engineering inputs.

### Rule D3: BATTERY CRITICAL SUPPORT WHEN RENEWABLE + DIESEL ARE UNAVAILABLE
- When renewable generation is zero/insufficient and diesel generation is unavailable, the battery continues supporting protected critical systems.
- Noncritical loads remain strictly excluded.
- Battery support continues while awaiting operator resolution or until a governed resource-survivability boundary (SOC floor) is reached.
- Option D is **NOT** an immediate fail-closed shutdown policy (unlike Option A).

### Rule D4: CRITICAL POWER SHORTFALL ALLOCATION & ESCALATION
- The system must attempt to maintain **ALL** protected critical systems at engineering-defined minimum viable operating levels.
- If total available power (renewable + diesel + battery) is less than total critical demand:
  1. Proportionally allocate available power across all protected critical systems based on engineering-defined minimum viable levels.
  2. Do **NOT** invent arbitrary category priorities at runtime (e.g., shedding water before heating unless explicitly authorized by station policy).
  3. Immediately trigger mandatory escalation to an authorized human operator.
  4. Continue physically feasible critical service delivery.

### Rule D5: HYBRID ESCALATION POLICY
- Mandatory operator escalation occurs upon reaching a **TIME BOUNDARY** ($T_{\text{max,degraded}}$) OR a **RESOURCE-SURVIVABILITY BOUNDARY** ($F_{\text{reserve,min}}$, battery SOC floor), whichever occurs first.
- Numerical threshold values have not yet been authorized by governance; they remain open parameters.
- Escalation does **NOT** automatically cause immediate shutdown of protected critical services.

### Rule D6: EXCESS DIESEL GENERATION CHARGING & CURTAILMENT
- If diesel generation is running because it is required for protected critical service, and minimum diesel operating output ($P_{\text{gen,min}}$) exceeds critical demand ($P_{\text{critical}}$):
  1. Charge the battery using the unavoidable excess diesel generation where technically allowable.
  2. Continue charging until the battery reaches its allowable charge limit / SOC ceiling.
  3. Curtail any remaining excess diesel generation above the battery charge acceptance limit.
- **FIREWALL RULE**: The system must **NOT** start diesel generation merely to charge the battery when critical systems do not require diesel output.

---

## Policy Invariants

1. **Policy Status**: `SELECTED_AND_SEALED`
2. **Implementation Requirement**: Future implementation must strictly enforce D1–D6 without introducing ungoverned heuristics.
3. **Engineering Parameter Separation**: D1–D6 define policy principles; concrete numerical parameters ($T_{\text{required}}$, $P_{\text{critical}}$, SOC limits, fuel thresholds) are station-engineering inputs to be plugged into D1–D6 without altering D1–D6 structure.
