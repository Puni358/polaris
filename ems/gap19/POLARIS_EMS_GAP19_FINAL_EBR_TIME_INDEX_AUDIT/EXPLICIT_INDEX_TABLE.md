# Explicit Index Mapping Table (`EXPLICIT_INDEX_TABLE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**REPRESENTATIVE MPC ORIGIN**: $t_{\text{now}} = \text{2024-01-01T20:00:00Z}$ (Cycle 1)  
**VERDICT**: `EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]`

---

## 1. Array Index Mapping Table

| Array Index $k$ | Forecast Timestamp | Critical-Demand Timestamp | Target Hour Interval | Committed Action Interval | Resulting State Timestamp |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$k=0$** | `2024-01-01T21:00:00Z` | `2024-01-01T21:00:00Z` | `20:00 → 21:00` ($t_{\text{now}}+1\text{h}$) | `20:00 → 21:00` (**COMMITTED**) | `2024-01-01T21:00:00Z` ($S_1$) |
| **$k=1$** | `2024-01-01T22:00:00Z` | `2024-01-01T22:00:00Z` | `21:00 → 22:00` ($t_{\text{now}}+2\text{h}$) | `21:00 → 22:00` (Planned) | `2024-01-01T22:00:00Z` (Planned) |
| **$k=2$** | `2024-01-01T23:00:00Z` | `2024-01-01T23:00:00Z` | `22:00 → 23:00` ($t_{\text{now}}+3\text{h}$) | `22:00 → 23:00` (Planned) | `2024-01-01T23:00:00Z` (Planned) |
| **$k=3$** | `2024-01-02T00:00:00Z` | `2024-01-02T00:00:00Z` | `23:00 → 00:00` ($t_{\text{now}}+4\text{h}$) | `23:00 → 00:00` (Planned) | `2024-01-02T00:00:00Z` (Planned) |
| **$k=4$** | `2024-01-02T01:00:00Z` | `2024-01-02T01:00:00Z` | `00:00 → 01:00` ($t_{\text{now}}+5\text{h}$) | `00:00 → 01:00` (Planned) | `2024-01-02T01:00:00Z` (Planned) |
| **$k=5$** | `2024-01-02T02:00:00Z` | `2024-01-02T02:00:00Z` | `01:00 → 02:00` ($t_{\text{now}}+6\text{h}$) | `01:00 → 02:00` (Planned) | `2024-01-02T02:00:00Z` (Planned) |
| **$k=6$** | `2024-01-02T03:00:00Z` | `2024-01-02T03:00:00Z` | `02:00 → 03:00` ($t_{\text{now}}+7\text{h}$) | `02:00 → 03:00` (Planned) | `2024-01-02T03:00:00Z` (Planned) |
| $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ |
| **$k=23$** | `2024-01-02T20:00:00Z` | `2024-01-02T20:00:00Z` | `19:00 → 20:00` ($t_{\text{now}}+24\text{h}$) | `19:00 → 20:00` (Planned) | `2024-01-02T20:00:00Z` (Planned) |

---

## 2. EBR Window Mapping at $k=0$

For the committed action $k=0$ at origin $t_{\text{now}} = \text{20:00}$, the governed 6-hour lookahead sums critical demand over $k \in \{0, 1, 2, 3, 4, 5\}$:
$$\text{EBR Window} = [\text{timestamps}[0], \text{timestamps}[5]] = [\text{21:00}, \text{02:00}] \equiv [t_{\text{now}} + 1\text{h}, t_{\text{now}} + 6\text{h}]$$

```text
EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]
```
