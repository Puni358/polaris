# Terminal Reserve Rolling Horizon Audit Report

## 1. Rolling Boundary Location Verification

The terminal reserve requirement ($E_{\text{term,target}} = 100,000.00\text{ Wh}$) enters the model strictly at the final decision step $t=23$ of each cycle's 24-hour decision horizon.

| Cycle | Origin Timestamp ($t_0$) | Decision Horizon Boundary ($t_{23}$) | Terminal Target Applied | Verification |
| :---: | :---: | :---: | :---: | :---: |
| **Cycle 1** | `2024-01-01T20:00:00Z` | `2024-01-02T19:00:00Z` | $100,000.00\text{ Wh}$ | **ROLLING BOUNDARY MATCH** |
| **Cycle 2** | `2024-01-01T21:00:00Z` | `2024-01-02T20:00:00Z` | $100,000.00\text{ Wh}$ | **ROLLING BOUNDARY MATCH** |
| **Cycle 3** | `2024-01-01T22:00:00Z` | `2024-01-02T21:00:00Z` | $100,000.00\text{ Wh}$ | **ROLLING BOUNDARY MATCH** |
| **Cycle 4** | `2024-01-01T23:00:00Z` | `2024-01-02T22:00:00Z` | $100,000.00\text{ Wh}$ | **ROLLING BOUNDARY MATCH** |
| **Cycle 5** | `2024-01-02T00:00:00Z` | `2024-01-03T23:00:00Z` | $100,000.00\text{ Wh}$ | **ROLLING BOUNDARY MATCH** |
| **Cycle 6** | `2024-01-02T01:00:00Z` | `2024-01-03T00:00:00Z` | $100,000.00\text{ Wh}$ | **ROLLING BOUNDARY MATCH** |
| **Cycle 7** | `2024-01-02T02:00:00Z` | `2024-01-03T01:00:00Z` | $100,000.00\text{ Wh}$ | **ROLLING BOUNDARY MATCH** |
| **Cycle 8** | `2024-01-02T03:00:00Z` | `2024-01-03T02:00:00Z` | $100,000.00\text{ Wh}$ | **ROLLING BOUNDARY MATCH** |

---

## 2. Forensic Findings

1. The terminal reserve target moves forward dynamically with each hourly MPC step.
2. It does **NOT** remain anchored to a fixed static calendar date.
3. Terminal reserve enters **only** at $t=23$ of each cycle's relative horizon.

---

## 3. Verdict

```
TERMINAL_RESERVE_MOVES_WITH_HORIZON = YES
STATIC_CALENDAR_ANCHORING = NO
TERMINAL_RESERVE_ROLLING_AUDIT_STATUS = PASS
```
