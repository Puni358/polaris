# POLARIS EMS — HD-03 VALIDITY & FRESHNESS RESOLVER SOURCE MAP

## 1. RESOLVER VALIDITY & FRESHNESS DATA FLOW

```
┌─────────────────────────────────────┐         ┌─────────────────────────────────────┐
│ DEPLOYMENT CONFIGURATION (OPTION C) │         │ AUTHORIZED OPERATIONAL INPUT (OPT A)│
│ - T_config baseline                 │         │ - T_oper override                   │
└──────────────────┬──────────────────┘         │ - issue_timestamp & valid_until     │
                   │                            └──────────────────┬──────────────────┘
                   │ T_config payload                              │ T_oper payload
                   v                                               v
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 T_required RESOLVER                                 │
│                                                                                     │
│ 1. STRUCTURAL VALIDITY CHECK (V-A):                                                 │
│    - Is input present, numeric, finite, positive (T_required > 0)?                  │
│    - Rejects NaN, Inf, 0, negative values -> FAIL CLOSED                            │
│                                                                                     │
│ 2. OPERATIONAL FRESHNESS CHECK (F-C):                                               │
│    - Is operational input age <= TTL and current_time <= valid_until?               │
│    - If stale: T_oper rejected -> Fallback to T_config candidate                    │
│                                                                                     │
│ 3. PRECEDENCE RESOLUTION:                                                           │
│    - Valid & fresh T_oper -> resolved_T_required = T_oper                           │
│    - Valid T_config (when T_oper stale/absent) -> resolved_T_required = T_config    │
│    - Zero valid candidates -> FAIL CLOSED status (no classification issued)         │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                                           │
                                           │ resolved_T_required / FAIL_CLOSED
                                           v
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            EMERGENCY CONDITION DETECTOR                             │
│ Role: CONSUMER ONLY                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. EVALUATOR RESPONSIBILITIES

1. **Validity Evaluator**: Enforces $T_{\text{required}} > 0$ and non-NaN/finite bounds.
2. **Freshness Evaluator**: Checks payload timestamp and TTL. If stale, marks $T_{\text{oper}}$ invalid.
3. **Precedence Engine**: Selects $T_{\text{oper}}$ when valid/fresh; falls back to $T_{\text{config}}$ when valid; emits `FAIL_CLOSED` if zero valid candidates exist.
