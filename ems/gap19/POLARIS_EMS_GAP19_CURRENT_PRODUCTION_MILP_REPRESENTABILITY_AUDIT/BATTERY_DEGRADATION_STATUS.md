# BATTERY DEGRADATION STATUS

## BATTERY DEGRADATION TERM IN CURRENT PRODUCTION `milp.py`

- **Current Implementation**: Present in scalar objective (Lines 109-110: `deg_penalty * dt * w_t * (p_chg + p_dis)`).
- **Status in Current Code**: `PRESENT`
- **Governance Placement Status**: Unresolved in GAP19 multi-objective specification. Options:
  1. Include in $J_3$ (Fuel & Asset Operational Cost)
  2. Include in $J_4$ (Efficiency/Degradation)
  3. Include as physical throughput constraint
  4. Separate objective $J_5$

```text
CURRENT_DEGRADATION_TERM = PRESENT
BATTERY_DEGRADATION_STAGE = GOVERNANCE_REQUIRED
```
