# POLARIS — EMERGENCY TRIGGER GOVERNANCE DECISION RECORD

## Executive Status & Authorization

```yaml
HUMAN_APPROVAL: TRUE
GOVERNANCE_STATUS: APPROVED
DATE: 2026-09-27
AUTHORITY: Human Project Owner / POLARIS Governance Board
TARGET_SYSTEM: POLARIS Energy Management System (ECD Module)
PRODUCTION_MODIFICATIONS_PERMITTED: FALSE (Specification & Test Plan Only)
```

---

## 1. Summary of Approved Governance Decisions

The human project owner has formally approved the emergency mode trigger semantics for POLARIS. The governing principles are recorded below:

### DECISION 1: CRITICAL-LOAD FAILURE (HARD IMMEDIATE TRIGGER)
- **Rule**: Actual validated critical-load service failure ($P_{\text{critical, served}} < P_{\text{critical, required}}$) is an **immediate Emergency trigger**.
- **Governance Constraint**: The system must NOT wait multiple control intervals after confirmed valid critical-load failure telemetry is received. Physical load shedding / Option C protection activates instantly upon validated failure.

### DECISION 2: IMMINENT SURVIVABILITY FAILURE (PREEMPTIVE TRIGGER)
- **Rule**: Emergency Mode may be entered *before* actual critical-load failure occurs when the system can no longer credibly guarantee the governed six-hour critical-load survivability requirement ($75.65\text{ kWh}$ / $11.6\text{ kW} \times 6\text{ h} / 0.92$) using currently available/credible resources.
- **Governance Constraint**: This must **NOT** be implemented as a naive static threshold like `SOC < 37.83% => Emergency`. It must be evaluated dynamically via a comprehensive survivability resource-adequacy calculation.

### DECISION 3: RESERVE DEFICIT (NORMAL OPERATIONAL STATE)
- **Rule**: Reserve deficit alone **NEVER** triggers Emergency Mode.
- **Governance Constraint**: The six-hour stored reserve target ($75.65\text{ kWh} = 37.83\%$ of nominal capacity) is a **NORMAL-MODE reserve target**, not an Emergency threshold. When battery energy is below target but critical-load survivability remains secure, the system state is strictly `RESERVE_DEFICIT / RECOVERY`. Load shedding is prohibited.

### DECISION 4: RESOURCE LOSS (RESOURCE-ADEQUACY ASSESSMENT)
- **Rule**: No arbitrary resource or SOC combination is an inherent Emergency trigger.
- **Governance Constraint**: Loss of renewable generation (solar/wind), diesel generator capacity, or battery storage triggers Emergency Mode **ONLY** when the remaining available resources are mathematically proven insufficient to guarantee six-hour critical-load survivability. Resource loss is evaluated via resource-adequacy calculation.

### DECISION 5: EMERGENCY EXIT (AUTOMATIC RETURN WITH OPERATOR OVERRIDE)
- **Rule**: Automatic return from Emergency Mode to `NORMAL` mode is permitted when:
  1. The emergency-causing condition has cleared.
  2. Critical load ($11.6\text{ kW}$) is reliably serviceable.
  3. Critical-load survivability (6-hour autonomy requirement) is once again secure.
  4. Sufficient controllable resources exist for normal microgrid operation.
- **Governance Constraint**: Preserves existing governance: `AUTOMATIC_RETURN_WITH_OPERATOR_NOTIFICATION_AND_OVERRIDE`. No artificial static SOC threshold may be introduced merely for exit convenience.

---

## 2. Explicit Correction of Prior Terminology & Mathematics

This decision record formally corrects prior ambiguity in SOC percentage and energy reserve definitions across the POLARIS project artifacts:

### 2.1 The Stored Reserve Requirement
- **Critical Load ($P_{\text{critical}}$)**: $11.6\text{ kW}$
- **Required Autonomy ($T_{\text{autonomy}}$)**: $6.0\text{ hours}$
- **Discharge Efficiency ($\eta_{\text{dis}}$)**: $0.92$
- **6-Hour Critical Reserve Energy ($E_{\text{reserve}}$)**:
  $$E_{\text{reserve}} = \frac{11.6\text{ kW} \times 6.0\text{ h}}{0.92} = 75.652\text{ kWh}$$

### 2.2 Corrected Nominal SOC Equivalent
- **Nominal Battery Capacity ($C_{\text{nom}}$)**: $200.0\text{ kWh}$
- **Stored Reserve as Percentage of Nominal Capacity**:
  $$SOC_{\text{reserve\_nominal}} = \frac{75.652\text{ kWh}}{200.0\text{ kWh}} = 37.826\% \approx 37.83\%$$

### 2.3 Explicit Correction of $57.83\%$ vs $37.83\%$
- **Prior Misinterpretation ($57.83\%$ SOC)**:
  In earlier J2 reserve discussions, $57.83\%\text{ SOC}$ ($115.65\text{ kWh}$) was derived by adding the $20.0\%$ physical minimum SOC floor ($40.0\text{ kWh}$) to the $37.83\%$ reserve energy ($75.65\text{ kWh}$).
- **Formal Correction**:
  - $37.83\%\text{ SOC} = 75.65\text{ kWh}$ represents the **six-hour stored reserve target**.
  - $57.83\%\text{ SOC} = 115.65\text{ kWh}$ was the old combined J2 target.
  - **MANDATORY RULE**: **$57.83\%$ MUST NOT BE REUSED AS THE EMERGENCY THRESHOLD.**

---

## 3. Implementation Guardrails & Absolute Constraints

The following constraints are binding on all future POLARIS engineering work:

1. **Production Code Lock**: No code modifications shall be made to `ecd.py`, `gap19_highs_native.py`, `router.py`, `option_d.py`, or `simulator.py` during this phase.
2. **Campaign Integrity**: Frozen 2024 annual campaign results (Cell A, Cell A2, Cell B) remain unchanged and protected.
3. **Telemetry Safeguard**: `UNKNOWN_INVALID != EMERGENCY`. Sensor errors must never cause false Option C load curtailment.

---

## 4. Record Sign-Off

- **Human Approval**: `TRUE`
- **Specification Status**: `COMPLETE & GOVERNED`
- **Implementation Status**: `PENDING AUTHORIZATION`
