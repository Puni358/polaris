# POLARIS EMS — HD-03 SEMANTIC CLOSURE DECISION TABLE

## 1. COMPACT POLICY DECISION TABLE

| Governance Item | Policy Selected | Authoritative Rule | Governance Status |
| :--- | :--- | :--- | :--- |
| **Operational Source Authority** | `AUTHENTICATED_AUTHORIZED` | Operational overrides require authenticated & explicitly authorized senders. | **CLOSED** (`CLOSED_AUTHENTICATED_AUTHORIZED_OPERATIONAL_SOURCE`) |
| **Time Semantics** | `POSITIVE_DURATION` | $T_{\text{required}}$ is a positive duration ($\Delta t > 0$) from decision point. Payload includes explicit expiry metadata. | **CLOSED** (`CLOSED_POSITIVE_DURATION_PLUS_EXPLICIT_EXPIRY`) |
| **Runtime Variability** | `MPC_CYCLE_REFRESH` | $T_{\text{required}}$ is evaluated at MPC-cycle boundaries. Mid-cycle per-timestep mutations forbidden. | **CLOSED** (`CLOSED_MPC_CYCLE_REFRESH`) |
| **Cryptographic Mechanism** | Unresolved | Algorithm, key-management, and certificate schema open. | `HD03_CRYPTOGRAPHIC_MECHANISM = NOT_ESTABLISHED` |
| **Numerical TTL Duration** | Unresolved | Maximum age guard duration (seconds/hours) open. | `HD03_TTL_VALUE = NOT_ESTABLISHED` |
| **Clock-Drift Threshold** | Unresolved | Max allowable clock drift tolerance open. | `HD03_CLOCK_DRIFT_THRESHOLD = NOT_ESTABLISHED` |
| **Numerical $T_{\text{required}}$ Value** | Unresolved | Station operational survival hours open. | `HD03_NUMERICAL_VALUE = NOT_ESTABLISHED` |

---

## 2. SUMMARY OF CLOSED VS REMAINING IMPLEMENTATION ITEMS

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                ALL CLOSED HD-03 POLICIES                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Source Architecture: C+A (Deployment Config Baseline + Authorized Operational Ext)  │
│ 2. Precedence & Conflict: Operational Wins When Valid & Authorized                     │
│ 3. Missing Data Policy: Fail Closed (No NORMAL/EMERGENCY classification issued)        │
│ 4. Structural Validity: T_required > 0, finite, numeric, present, unambiguous          │
│ 5. Freshness Model: F-C BOTH (Explicit expiry timestamp + Maximum age TTL guard)       │
│ 6. Operational Authority: Authenticated & explicitly authorized source required        │
│ 7. Time Semantics: Positive duration (Delta t > 0) from decision point                 │
│ 8. Runtime Variability: Governed update boundary locked to MPC cycle                   │
│ 9. Detector Ownership: CONSUMER_ONLY (Upstream resolver produces effective T_req)    │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              REMAINING UNRESOLVED ITEMS                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ - HD03_NUMERICAL_VALUE (Site-specific survival hours)                                  │
│ - HD03_TTL_VALUE (Max payload age duration)                                           │
│ - HD03_CLOCK_DRIFT_THRESHOLD (Max clock drift seconds)                                │
│ - HD03_CRYPTOGRAPHIC_MECHANISM (Signature algorithm / PKI design)                    │
│ - HD03_UNIT_STATUS (Float hours vs timesteps schema declaration)                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
