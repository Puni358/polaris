# POLARIS EMS — HD-03 AUTHORITATIVE RESOLVER & RUNTIME DATA FLOW

## 1. COMPLETE RESOLVER & RUNTIME DATA FLOW

```
                            MPC-CYCLE BOUNDARY (k)
                                       │
┌──────────────────────────────────────┴──────────────────────────────────────┐
│                            T_required RESOLVER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. INSPECT OPERATIONAL PAYLOAD (OPTION A):                                  │
│    - Authenticated & Authorized Source? (CLOSED_AUTHENTICATED_AUTHORIZED)   │
│    - Structurally Valid? (T_required > 0, finite float)                     │
│    - Fresh? (Not expired & payload_age <= TTL)                              │
│                                                                             │
│ 2. EVALUATE PRECEDENCE:                                                     │
│    - If Operational Payload Passes (1) ──► resolved_T_req = T_oper          │
│    - Else Inspect Deployment Config (OPTION C)                              │
│         - If Config Valid ──────────────► resolved_T_req = T_config        │
│         - Else ─────────────────────────► Status = FAIL_CLOSED              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                         resolved_T_req (Duration Delta t > 0)
                                       │
                                       v
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EMERGENCY CONDITION DETECTOR                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Role: CONSUMER ONLY                                                         │
│ Evaluates survivability over resolved_T_req under stress scenario:           │
│ P_solar = 0, P_wind = 0 (HD-04 Option A)                                    │
│ Output: NORMAL / EMERGENCY Mode Flag (or FAIL_CLOSED exception)             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       v
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  EMS / MPC                                  │
│ Executes rolling MPC optimization for timestep k over H = 24h.              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. RUNTIME REFRESH SEMANTICS

- **MPC Cycle Locking**: $T_{\text{required}}$ resolution occurs strictly at MPC step boundaries ($k=0, 1, 2, \dots$).
- **No Per-Timestep Mutation**: Mid-cycle mutations, random jitter, or unauthorized operational injections between step boundaries are rejected.
- **Fail-Closed Guarantee**: If operational payload expires mid-run and deployment config is invalid/absent, system triggers `FAIL_CLOSED` (no classification issued).
