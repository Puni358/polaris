# POLARIS EMS — MINIMUM FIXTURE ECD COVERAGE AUDIT

## 1. Executive Summary

This document audits the coverage of Emergency Condition Detector (ECD) logic paths by the minimum synthetic fixture.

---

## 2. ECD Coverage Mapping

```
                               ┌───────────────────────────┐
                               │   ECD Evaluation Engine   │
                               └─────────────┬─────────────┘
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               ▼                             ▼                             ▼
     [Scenario 1: NORMAL]         [Scenarios 2-4: EMERGENCY]     [Scenario 5: UNKNOWN_INVALID]
  T_bat >= 6h AND T_dsl >= 6h   T_bat < 6h  OR  T_dsl < 6h     Missing/Expired T_required Payload
```

| ECD Output State | Scenario Mapping | Condition Exercised | Coverage Status |
| :--- | :--- | :--- | :--- |
| `NORMAL` | Scenario 1 | Both $T_{\text{battery}} \ge 6\text{h}$ and $T_{\text{diesel}} \ge 6\text{h}$. | `100% COVERED` |
| `EMERGENCY` (Battery) | Scenario 2 | $T_{\text{battery}} < 6\text{h}$, $T_{\text{diesel}} \ge 6\text{h}$. | `100% COVERED` |
| `EMERGENCY` (Diesel) | Scenario 3 | $T_{\text{battery}} \ge 6\text{h}$, $T_{\text{diesel}} < 6\text{h}$. | `100% COVERED` |
| `EMERGENCY` (Both) | Scenario 4 | Both $T_{\text{battery}} < 6\text{h}$ and $T_{\text{diesel}} < 6\text{h}$. | `100% COVERED` |
| `UNKNOWN_INVALID` | Scenario 5 | Missing or expired $T_{\text{required}}$ payload. | `100% COVERED` |

---

## 3. Status

```yaml
MINIMUM_ECD_COVERAGE: COMPLETE_100_PERCENT
VERIFICATION: All 5 ECD risk classification states and missing-input fail-closed paths are fully covered.
```
