# J1 REPRESENTABILITY AUDIT

## CRITICAL RELIABILITY OBJECTIVE ($J_1$)

- **Governed Definition**: $J_1 = \sum_{t=0}^{23} P_{\text{unmet,critical}}(t) \cdot \Delta t$
- **Current Variable in `milp.py`**: `p_unmet` ($15t+9$)
- **Current Variable Definition**: Defined via $p_{\text{served}} + p_{\text{unmet}} = P_{\text{demand}}(t)$, where $P_{\text{demand}}(t)$ is total station demand.

### FINDINGS
1. `milp.py` has a single `p_unmet` variable representing unmet *total station demand*.
2. `milp.py` does NOT separate demand into protected critical demand vs flexible/deferrable demand vs non-critical demand.
3. Repurposing total station `p_unmet` as critical `p_unmet` assumes 100% of station demand is critical, which contradicts the governed 5-tier load specification.

```text
J1_REPRESENTABILITY = BLOCKED
REASON = BLOCKED_BY_MISSING_CRITICAL_LOAD_VARIABLE
```
