# EBR Rolling Lookahead Window Audit Report

## 1. Rolling EBR Lookahead Window Audit

For every cycle origin $t_{\text{origin}}$, the 6-hour lookahead window $W(t)$ covers steps $k \in \{0, \dots, 5\}$ (corresponding to timestamps $t_{\text{origin}} \dots t_{\text{origin}} + 5\text{ h}$):

| Cycle | Origin Timestamp | 6h EBR Lookahead Window Start | 6h EBR Lookahead Window End | Expected $E_{\text{EBR,target}}[t=0]$ | Actual $E_{\text{EBR,target}}[t=0]$ | Reconciliation |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cycle 1** | `2024-01-01T20:00:00Z` | `2024-01-01T20:00:00Z` | `2024-01-02T01:00:00Z` | $130,434.78\text{ Wh}$ | $130,434.78\text{ Wh}$ | **EXACT MATCH** |
| **Cycle 2** | `2024-01-01T21:00:00Z` | `2024-01-01T21:00:00Z` | `2024-01-02T02:00:00Z` | $130,434.78\text{ Wh}$ | $130,434.78\text{ Wh}$ | **EXACT MATCH** |
| **Cycle 3** | `2024-01-01T22:00:00Z` | `2024-01-01T22:00:00Z` | `2024-01-02T03:00:00Z` | $130,434.78\text{ Wh}$ | $130,434.78\text{ Wh}$ | **EXACT MATCH** |
| **Cycle 4** | `2024-01-01T23:00:00Z` | `2024-01-01T23:00:00Z` | `2024-01-02T04:00:00Z` | $130,434.78\text{ Wh}$ | $130,434.78\text{ Wh}$ | **EXACT MATCH** |
| **Cycle 5** | `2024-01-02T00:00:00Z` | `2024-01-02T00:00:00Z` | `2024-01-02T05:00:00Z` | $130,434.78\text{ Wh}$ | $130,434.78\text{ Wh}$ | **EXACT MATCH** |
| **Cycle 6** | `2024-01-02T01:00:00Z` | `2024-01-02T01:00:00Z` | `2024-01-02T06:00:00Z` | $130,434.78\text{ Wh}$ | $130,434.78\text{ Wh}$ | **EXACT MATCH** |
| **Cycle 7** | `2024-01-02T02:00:00Z` | `2024-01-02T02:00:00Z` | `2024-01-02T07:00:00Z` | $130,434.78\text{ Wh}$ | $130,434.78\text{ Wh}$ | **EXACT MATCH** |
| **Cycle 8** | `2024-01-02T03:00:00Z` | `2024-01-02T03:00:00Z` | `2024-01-02T08:00:00Z` | $130,434.78\text{ Wh}$ | $130,434.78\text{ Wh}$ | **EXACT MATCH** |

---

## 2. Verdict

```
EBR_LOOKAHEAD_WINDOW_ROLLING = YES
EBR_CALCULATION_RECONCILED = YES
EBR_ROLLING_AUDIT_STATUS = PASS
```
