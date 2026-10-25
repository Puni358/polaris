# `w_stop` ALTERNATIVE FORMULATIONS

## POST-OPTIMIZATION DERIVATION OF SHUTDOWN EVENTS

If shutdown events are required for station reporting or dispatch metrics, they can be calculated cleanly **post-optimization** from the returned binary solution $u_{\text{diesel}}^*$:

$$\text{shutdown\_event}[t] = \max(0, u_{\text{diesel}}^*[t-1] - u_{\text{diesel}}^*[t])$$

This post-solve calculation produces exact shutdown metrics without introducing decision variables into the solver.

```text
SHUTDOWN_EVENT = DERIVED_REPORTING_QUANTITY
OPTIMIZATION_DECISION_VARIABLES_ADDED = 0
```
