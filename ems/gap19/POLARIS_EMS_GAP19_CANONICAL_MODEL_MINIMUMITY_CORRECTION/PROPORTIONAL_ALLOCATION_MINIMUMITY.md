# PROPORTIONAL ALLOCATION MINIMUMITY AUDIT

## AUDIT OF PROPORTIONAL ALLOCATION FACTOR $\alpha(t)$

- **D4 Policy Requirement**: $P_{i,\text{served}}(t) = \alpha(t) P_{i,\text{min}}(t)$ when available critical power is insufficient.
- **Variable Audit**: $\alpha(t) = \frac{P_{\text{avail,crit}}(t)}{\sum P_{\text{min},i}(t)}$ is determined directly from external inputs and total available power. It does NOT need to be an optimization decision variable.
- **Minimumity Result**: $\alpha(t)$ optimization variables are **NOT_REQUIRED**.

```text
PROPORTIONAL_ALPHA_VARIABLE_STATUS = NOT_REQUIRED
```
