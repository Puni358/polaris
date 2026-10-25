# EBR Index Trace (`EBR_INDEX_TRACE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**SOURCE**: `system/optimization/implementations/gap19_highs_native.py` (lines 127-131)  
**VERDICT**: `EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]`

---

## 1. Code-Level Index Analysis

```python
for t in range(24):
    end_k = min(t + 6, 24)
    w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, end_k))
```

At $t = 0$:
- `range(0, 6)` extracts $k \in \{0, 1, 2, 3, 4, 5\}$.
- $k=0 \implies \text{timestamps}[0] = t_{\text{now}} + 1\text{h}$.
- $k=5 \implies \text{timestamps}[5] = t_{\text{now}} + 6\text{h}$.
- Physical lookahead interval: $[t_{\text{now}} + 1\text{h}, t_{\text{now}} + 6\text{h}]$.

---

## 2. Evaluation of Competing Interpretations

- **INTERPRETATION A (`[t_now + 1h, t_now + 6h]`)**: **MATCHES IMPLEMENTATION EXACTLY**.
- **INTERPRETATION B (`[t_now, t_now + 5h]`)**: INCORRECT ($k=0$ is $t_{\text{now}}+1\text{h}$, not $t_{\text{now}}$).

```text
EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]
EBR_K0_PHYSICAL_WINDOW = [T_NOW_PLUS_1H, T_NOW_PLUS_6H]
```
