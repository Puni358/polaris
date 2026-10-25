# POLARIS EMS — HD-03 MISSING T_required DECISION TABLE

## 1. COMPACT POLICY DECISION TABLE

| Policy | Repository Support | Numerical Value Needed? | Compatibility |
| :--- | :--- | :--- | :--- |
| **M-A Fail Closed** | `SUPPORTED_BY_EXISTING_GOVERNANCE` | No | Fully compatible with detector `CONSUMER_ONLY` and POLARIS `FAIL_CLOSED` pattern |
| **M-B Emergency** | `NOT_ESTABLISHED` | No | Conservative for critical load; unestablished in codebase |
| **M-C Last Valid** | `CONFLICTS_WITH_GOVERNANCE` | No | Conflicts with strict prohibition against unvalidated stale data forward-filling |
| **M-D Fallback** | `NOT_ESTABLISHED` | Yes | Requires separate numerical policy value; conflicts with non-derivation directive |

---

## 2. EXACT HUMAN DECISION REQUIRED

EXACT_HUMAN_DECISION_REQUIRED =
The human stakeholder must select whether the Emergency Condition Detector fails closed (M-A), declares emergency mode (M-B), uses the last valid T_required (M-C), or uses a separately governed numerical fallback (M-D) when no valid T_required is available.
