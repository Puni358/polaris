# EBR Rolling Forensic Audit (`EBR_ROLLING_FORENSIC_AUDIT.md`)

**FORENSIC AUDIT**: POLARIS EMS GAP19 — Post-8-Cycle Forensic Behavior Audit  
**GOVERNED SEMANTICS**: $T_{\text{REQUIRED}} = 6\text{ HOURS}$, Critical Demand = $20,000\text{ W}$ constant  
**VERDICT**: `PASS`

---

## 1. Governed EBR Rolling Window Table

| Cycle | Origin Timestamp | EBR Window Start ($t+1\text{h}$) | EBR Window End ($t+6\text{h}$) | Critical Load Source | EBR Target (Wh) | Causal? | Correctly Rolled? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **01** | `2024-01-01T20:00:00Z` | `2024-01-01T21:00:00Z` | `2024-01-02T02:00:00Z` | `ForecastBundle.demand_critical` | $120,000.0$ | `YES` | `YES` |
| **02** | `2024-01-01T21:00:00Z` | `2024-01-01T22:00:00Z` | `2024-01-02T03:00:00Z` | `ForecastBundle.demand_critical` | $120,000.0$ | `YES` | `YES` |
| **03** | `2024-01-01T22:00:00Z` | `2024-01-01T23:00:00Z` | `2024-01-02T04:00:00Z` | `ForecastBundle.demand_critical` | $120,000.0$ | `YES` | `YES` |
| **04** | `2024-01-01T23:00:00Z` | `2024-01-02T00:00:00Z` | `2024-01-02T05:00:00Z` | `ForecastBundle.demand_critical` | $120,000.0$ | `YES` | `YES` |
| **05** | `2024-01-02T00:00:00Z` | `2024-01-02T01:00:00Z` | `2024-01-02T06:00:00Z` | `ForecastBundle.demand_critical` | $120,000.0$ | `YES` | `YES` |
| **06** | `2024-01-02T01:00:00Z` | `2024-01-02T02:00:00Z` | `2024-01-02T07:00:00Z` | `ForecastBundle.demand_critical` | $120,000.0$ | `YES` | `YES` |
| **07** | `2024-01-02T02:00:00Z` | `2024-01-02T03:00:00Z` | `2024-01-02T08:00:00Z` | `ForecastBundle.demand_critical` | $120,000.0$ | `YES` | `YES` |
| **08** | `2024-01-02T03:00:00Z` | `2024-01-02T04:00:00Z` | `2024-01-02T09:00:00Z` | `ForecastBundle.demand_critical` | $120,000.0$ | `YES` | `YES` |

---

## 2. Detailed Findings

- **Lookahead Definition**: For every MPC origin $t_n$, the EBR lookahead evaluates $W(t) = [t_n+1\text{h}, t_n+6\text{h}]$.
- **Window Movement**: The 6-hour window advanced by exactly $+1$ hour at every cycle, crossing midnight (`23:00` $\to$ `00:00`) seamlessly.
- **No Calendar Truncation**: EBR lookahead evaluated the true rolling 6-hour horizon without truncating at end-of-calendar-day.
- **Shortfall Verification**: $J_2$ reserve shortfall $s_{J2} = 0.0\text{ Wh}$ across all cycles.

```text
EBR_ROLLING = PASS
EBR_LOOKAHEAD_HOURS = 6
```
