# POLARIS GATE-03 — OPERATOR NOTIFICATION POLICY
## MANDATORY NOTIFICATION MANDATE UPON AUTOMATIC EMERGENCY RETURN

---

## 1. MANDATORY GOVERNANCE NOTIFICATION POLICY

```yaml
OPERATOR_NOTIFICATION_POLICY: MANDATORY_UPON_AUTOMATIC_RETURN
PRE_RETURN_OPERATOR_CONFIRMATION: NOT_REQUIRED
POLICY_SOURCE: SEALED_HUMAN_PROJECT_OWNER_DIRECTIVE
```

### Authoritative Policy Statement
> *"When the microgrid transitions from `EMERGENCY` mode back to `NORMAL` mode automatically upon ECD evaluation, POLARIS SHALL immediately issue an operator-visible notification informing the authorized operator of the state transition."*

---

## 2. MANDATORY NOTIFICATION PAYLOAD CONTENT

The notification payload issued upon automatic emergency return MUST communicate the following three elements:

1. **Prior Emergency State**: Explicit statement that the microgrid was previously operating in `EMERGENCY` mode.
2. **Current Normal Evaluation**: Statement that ECD currently evaluates system survivability as `NORMAL` ($m_{\text{battery}} \ge 0.0$ and $m_{\text{diesel}} \ge 0.0$).
3. **Automatic Return Execution**: Statement that automatic return to `NORMAL` optimization dispatch (Option B / MILP) has been executed.

---

## 3. POLICY VS. UNENGINEERED IMPLEMENTATION BOUNDARY

| Dimension | Sealed Governance Policy | Not Yet Specified / Engineering Boundary |
| :--- | :--- | :--- |
| **Notification Execution** | **MANDATORY** upon automatic return. | **NOT YET SPECIFIED** (Transport protocol, UI API, DB schema). |
| **Notification Content** | **MANDATORY** 3-part payload (Prior Emergency, Current Normal, Auto-Return executed). | **NOT YET SPECIFIED** (Exact text string formatting, localization). |
| **Pre-Return Delay** | **ZERO**. Return occurs automatically without waiting for operator. | **NOT YET SPECIFIED** (Display latency, refresh rate). |
