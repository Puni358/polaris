# POLARIS EMS GAP19 — ECD DATA-BLOCKED BOUNDARY

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_DATA_BLOCKED_OPERATIONAL_ARCHITECTURE`  

---

## 1. ECD Status Partitioning Matrix

| ECD Aspect | Status | Established Scope | Data-Blocked Scope |
| :--- | :--- | :--- | :--- |
| **Emergency Authority** | `ESTABLISHED_AS_GOVERNED` | Sole authority to declare `EMERGENCY = TRUE` (Decision D3). | $J2>0$ & MILP status cannot override ECD authority. |
| **Mathematical Core** | `ESTABLISHED` | Canonical survivability equation ($T_{\text{required}}$ lookahead). | Tested on synthetic canonical test fixture only. |
| **Production Integration** | `NOT_IMPLEMENTED` | Class structure exists in `system/optimization/ecd.py`. | Un-connected to `runner.py` active dispatch loop. |
| **Telemetry & Freshness** | `NOT_ESTABLISHED` | None. | Cryptographic signatures and data TTLs missing. |
| **Station Validation** | `NOT_ESTABLISHED` | $T_{\text{required\_baseline}} = 6\text{h}$ semantics sealed. | Station logistics SLA & blizzard records missing. |

---

## 2. Explicit Signal Separation Rules

```text
ECD = EMERGENCY AUTHORITY (Determines survivability state)
  ≠
J2 = RESERVE-SHORTFALL SIGNAL (Informational soft penalty metric)
  ≠
MILP_INFEASIBILITY = OPTIMIZATION STATUS (Input signal to ECD assessment)
```

These three signals **MUST NOT** be collapsed into one threshold.
