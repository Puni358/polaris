# OPERATOR ESCALATION ARCHITECTURE

## 1. TIME & RESOURCE BOUNDARY ESCALATION ARCHITECTURE

Governance DEC-004 D5 requires:
> "Operator escalation occurs at time boundary OR resource-survivability boundary, whichever occurs first. Actual threshold values remain engineering inputs. Escalation does NOT automatically imply shutdown."

---

## 2. PLACEMENT & EVENT ARCHITECTURE

```text
                               ┌────────────────────────┐
                               │   Runtime Supervisor   │
                               └───────────┬────────────┘
                                           │
               ┌───────────────────────────┴───────────────────────────┐
               ▼                                                       ▼
┌──────────────────────────────┐                       ┌──────────────────────────────┐
│  Time Boundary Check         │                       │  Resource Boundary Check     │
├──────────────────────────────┤                       ├──────────────────────────────┤
│ Degraded Duration Counter    │                       │ Fuel < V_crit (e.g. 50L)     │
│ t_degraded >= t_max_degraded │                       │ SOC < SOC_crit (e.g. 25%)    │
└──────────────┬───────────────┘                       └──────────────┬───────────────┘
               │                                                       │
               └───────────────────────────┬───────────────────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │ Operator Escalation    │
                               │ Event Dispatcher       │
                               └────────────────────────┘
```

---

## 3. ARCHITECTURAL PLACEMENT & RULES
1. **Outside Mathematical Solver**: Operator escalation logic belongs in the **Runtime Supervisor / Event Router** (`system/runtime/`), NOT inside `milp.py` or solver objective terms.
2. **Non-Destructive Action**: Escalation emits an asynchronous `FaultEvent` (`severity="OPERATOR_ESCALATION_REQUIRED"`), updates run metadata, and flags UI alarms. It does NOT automatically force immediate microgrid shutdown.
3. **Trigger Criteria**:
   - Time boundary: Continuous degraded operation duration $t_{\text{degraded}} \ge T_{\text{max\_degraded}}$ (e.g. 6 hours).
   - Resource boundary: Fuel remaining $V_{\text{fuel}} \le V_{\text{escalate}}$ OR usable battery energy $E_{\text{batt}} \le E_{\text{escalate}}$.
