# Runtime Dataflow Trace Across All 8 Cycles

## 1. Cycle-by-Cycle Dataflow Trace Matrix

| Cycle | Origin Timestamp (UTC) | State Input ($E_{\text{batt}}$ / SOC) | Forecast Horizon Range | Solver Call | Committed Action ($t=0$) | State Output ($E_{\text{batt}}$ / SOC) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | `2024-01-01T20:00:00Z` | $160,000.00\text{ Wh}$ ($80.0\%$) | `20:00` $\to$ `19:00` | `highspy.run()` | $P_{\text{chg}}=29,064.27\text{ W}$ | $186,739.13\text{ Wh}$ ($93.37\%$) |
| **2** | `2024-01-01T21:00:00Z` | $186,739.13\text{ Wh}$ ($93.37\%$) | `21:00` $\to$ `20:00` | `highspy.run()` | $P_{\text{chg}}=0\text{ W}, P_{\text{dies}}=15,000\text{ W}$ | $186,739.13\text{ Wh}$ ($93.37\%$) |
| **3** | `2024-01-01T22:00:00Z` | $186,739.13\text{ Wh}$ ($93.37\%$) | `22:00` $\to$ `21:00` | `highspy.run()` | $P_{\text{chg}}=0\text{ W}, P_{\text{dies}}=15,000\text{ W}$ | $186,739.13\text{ Wh}$ ($93.37\%$) |
| **4** | `2024-01-01T23:00:00Z` | $186,739.13\text{ Wh}$ ($93.37\%$) | `23:00` $\to$ `22:00` | `highspy.run()` | $P_{\text{chg}}=0\text{ W}, P_{\text{dies}}=15,000\text{ W}$ | $186,739.13\text{ Wh}$ ($93.37\%$) |
| **5** | `2024-01-02T00:00:00Z` | $186,739.13\text{ Wh}$ ($93.37\%$) | `00:00` $\to$ `23:00` | `highspy.run()` | $P_{\text{chg}}=0\text{ W}, P_{\text{dies}}=15,000\text{ W}$ | $186,739.13\text{ Wh}$ ($93.37\%$) |
| **6** | `2024-01-02T01:00:00Z` | $186,739.13\text{ Wh}$ ($93.37\%$) | `01:00` $\to$ `00:00` | `highspy.run()` | $P_{\text{chg}}=0\text{ W}, P_{\text{dies}}=15,000\text{ W}$ | $186,739.13\text{ Wh}$ ($93.37\%$) |
| **7** | `2024-01-02T02:00:00Z` | $186,739.13\text{ Wh}$ ($93.37\%$) | `02:00` $\to$ `01:00` | `highspy.run()` | $P_{\text{chg}}=0\text{ W}, P_{\text{dies}}=15,000\text{ W}$ | $186,739.13\text{ Wh}$ ($93.37\%$) |
| **8** | `2024-01-02T03:00:00Z` | $186,739.13\text{ Wh}$ ($93.37\%$) | `03:00` $\to$ `02:00` | `highspy.run()` | $P_{\text{chg}}=0\text{ W}, P_{\text{dies}}=15,000\text{ W}$ | $186,739.13\text{ Wh}$ ($93.37\%$) |

---

## 2. Verdict

```
DATAFLOW_CONTINUITY_VERIFIED = YES
STATE_DATAFLOW_PROVEN = PASS
```
