# POLARIS EMS — HD-03 OPERATIONAL OVERRIDE RESOLVER SOURCE MAP

## 1. DATA FLOW & RESOLVER PRECEDENCE MAP

```
┌─────────────────────────────────────┐         ┌─────────────────────────────────────┐
│ DEPLOYMENT CONFIGURATION (OPTION C) │         │ AUTHORIZED OPERATIONAL INPUT (OPT A)│
│ - T_config baseline                 │         │ - T_oper override                   │
└──────────────────┬──────────────────┘         └──────────────────┬──────────────────┘
                   │                                               │
                   │ T_config payload                              │ T_oper payload
                   v                                               v
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 T_required RESOLVER                                 │
│                                                                                     │
│ PRECEDENCE LOGIC:                                                                   │
│ If T_oper is VALID and AUTHORIZED:                                                  │
│     resolved_T_required = T_oper                                                    │
│ Else if T_config is VALID:                                                          │
│     resolved_T_required = T_config                                                  │
│ Else:                                                                               │
│     Status = FAIL_CLOSED (No NORMAL/EMERGENCY issued)                             │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                                           │
                                           │ resolved_T_required / FAIL_CLOSED status
                                           v
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            EMERGENCY CONDITION DETECTOR                             │
│                                                                                     │
│ Role: CONSUMER ONLY                                                                 │
│ Consumes resolved_T_required directly from Resolver.                                │
│ Does NOT perform precedence evaluation, averaging, or source selection.             │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. COMPONENT RESPONSIBILITY BOUNDARIES

1. **Deployment Config Source (Option C)**: Supplies configured baseline ($T_{\text{config}}$).
2. **Authorized Operational Input Source (Option A)**: Supplies dynamic mission input ($T_{\text{oper}}$).
3. **$T_{\text{required}}$ Resolver**: Evaluates input status and applies precedence (`T_oper > T_config`). Emits single `resolved_T_required` value or `FAIL_CLOSED` fault signal.
4. **Emergency Condition Detector**: Consumes resolved value; zero precedence ownership (`CONSUMER_ONLY`).
