# POLARIS EMS — HD-03 VALIDITY & FRESHNESS CLOSURE DECISION TABLE

## 1. COMPACT POLICY DECISION TABLE

| Governance Item | Policy Selected | Authoritative Rule | Status |
| :--- | :--- | :--- | :--- |
| **Structural Validity** | `BASIC_STRUCTURAL_VALIDITY` | Valid iff present, numeric, finite, positive ($T_{\text{required}} > 0$), authorized unit, unambiguous. | **CLOSED** (`CLOSED_BASIC_STRUCTURAL_VALIDITY`) |
| **Upper Bound ($T_{\text{max}}$)** | None authorized | `HD03_UPPER_BOUND = NOT_ESTABLISHED`. No upper bound assumption permitted. | **NOT ESTABLISHED** |
| **Freshness Model** | `F-C BOTH` | Operational payload valid iff `not_expired(explicit_expiry)` AND `age <= governed_max_age`. | **CLOSED** (`CLOSED_FC_BOTH`) |
| **Numerical TTL Value** | None selected | `HD03_TTL_VALUE = NOT_ESTABLISHED`. Numerical TTL duration open. | **NOT ESTABLISHED** |
| **Clock-Drift Threshold** | None selected | `HD03_CLOCK_DRIFT_THRESHOLD = NOT_ESTABLISHED`. Clock drift tolerance open. | **NOT ESTABLISHED** |

---

## 2. SUMMARY OF CLOSED VS OPEN PARAMETERS

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CLOSED CONCEPTUAL POLICIES                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ - Structural Validity: T_required > 0, finite, numeric, present, unambiguous           │
│ - Invalid States: missing, null, NaN, Inf, zero (0), negative (<0), wrong units         │
│ - Freshness Architecture: F-C BOTH (Explicit expiry timestamp + Maximum age TTL guard) │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               REMAINING OPEN PARAMETERS                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ - Numerical TTL Duration (seconds/hours)                                               │
│ - Clock-Drift Threshold (seconds)                                                      │
│ - Upper Bound Duration T_max                                                           │
│ - Operational Source Authority & Signature Requirements                                │
│ - Time Semantics (Duration vs Recovery Timestamp)                                      │
│ - Dynamic Runtime Variability Frequency                                                │
│ - Numerical T_required Survival Hours                                                  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
