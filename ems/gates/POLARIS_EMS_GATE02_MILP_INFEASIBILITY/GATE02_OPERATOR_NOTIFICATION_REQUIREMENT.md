# POLARIS GATE-02 — OPERATOR NOTIFICATION REQUIREMENT
## GOVERNANCE REQUIREMENT FOR OPERATOR-VISIBLE NOTIFICATION ON RELAXATION

---

## 1. MANDATORY GOVERNANCE REQUIREMENT STATEMENT

```yaml
OPERATOR_NOTIFICATION_REQUIREMENT: MANDATORY_ON_RELAXATION
RELAXATION_EVENT_VISIBILITY: OPERATOR_SURFACED
DECISION_SOURCE: HUMAN_PROJECT_OWNER_DIRECTIVE
```

### Formal Governance Requirement
> *"Every occurrence of governed constraint relaxation executed by the EMS solver MUST generate an operator-visible notification/event detailing which constraints were relaxed and the magnitude of the relaxation."*

---

## 2. GOVERNANCE BOUNDARIES & NON-INVENTIONS

To preserve architectural neutrality and enforce engineering firewalls, the following implementation choices are **EXTERNALLY BOUNDED AND NOT INVENTED IN THIS SPECIFICATION**:

1. **UI Technology & Framework**: No web framework, desktop GUI, or dashboard technology is specified or mandated.
2. **Alert Transport Protocol**: No SMS, email, webhook, MQTT, REST, or SCADA protocol is specified.
3. **Timeout & Acknowledgement**: No notification timeout, retry interval, or operator acknowledgement protocol is invented.
4. **Authentication & Access Control**: No user role, login system, or authorization token mechanism is invented.

---

## 3. REQUIRED NOTIFICATION DATA ELEMENTS

When implemented in future software releases, the notification event payload MUST contain at minimum the following diagnostic metadata:

- **Event Timestamp**: ISO-8601 UTC timestamp of the optimization cycle.
- **Original Solver Status**: `OPTIMIZATION_INFEASIBLE` status from the primary MILP pass.
- **Relaxation Tier Invoked**: The specific Tier B / Tier C constraint classes softened during the re-solve pass.
- **Relaxation Vector Summary**: List of relaxed variables (e.g. flexible load shed kW, terminal SOC shortfall %).
- **Status Outcome**: Whether the relaxed re-solve pass succeeded (`FEASIBLE_RELAXED`) or failed (`STILL_INFEASIBLE`).
