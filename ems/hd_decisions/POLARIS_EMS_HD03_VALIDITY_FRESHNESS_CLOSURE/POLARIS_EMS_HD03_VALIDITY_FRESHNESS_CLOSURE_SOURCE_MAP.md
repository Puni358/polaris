# POLARIS EMS — HD-03 VALIDITY & FRESHNESS CLOSURE SOURCE MAP

## 1. RESOLVER VALIDITY & FRESHNESS EVALUATION ARCHITECTURE

```
┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
│  DEPLOYMENT CONFIGURATION (OPTION C) │        │ AUTHORIZED OPERATIONAL INPUT (OPT A) │
└──────────────────┬───────────────────┘        └──────────────────┬───────────────────┘
                   │                                               │
                   │ configured payload                            │ operational payload
                   v                                               v
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                 T_required RESOLVER                                  │
│                                                                                      │
│ 1. VALIDITY EVALUATOR (CLOSED: BASIC_STRUCTURAL_VALIDITY):                           │
│    - Checks: present, numeric, finite, positive (T_required > 0), authorized unit.   │
│    - Rejects: NaN, Inf, 0, negative values -> candidate marked INVALID.             │
│                                                                                      │
│ 2. FRESHNESS EVALUATOR (CLOSED: F-C BOTH):                                           │
│    - Checks: current_time <= valid_until AND payload_age <= governed_max_age.       │
│    - If stale: T_oper candidate marked STALE/INVALID -> Fallback to T_config.        │
│                                                                                      │
│ 3. PRECEDENCE EVALUATION (CLOSED: OPERATIONAL_WINS):                                 │
│    - If T_oper is valid & fresh -> resolved_T_required = T_oper                      │
│    - Else if T_config is valid -> resolved_T_required = T_config                     │
│    - Else -> Status = FAIL_CLOSED (Zero NORMAL/EMERGENCY classification issued)      │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           │ resolved_T_required / FAIL_CLOSED status
                                           v
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                             EMERGENCY CONDITION DETECTOR                             │
│ Role: CONSUMER ONLY                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. EVALUATION RESPONSIBILITIES

- **Validity Guard**: Structural validation ($T_{\text{required}} > 0$, finite numeric).
- **Freshness Guard**: Dual-check payload expiry and TTL maximum age.
- **Resolver Core**: Executes precedence and outputs `resolved_T_required` or `FAIL_CLOSED`.
- **Emergency Detector**: Consumes output; zero validation/precedence ownership (`CONSUMER_ONLY`).
