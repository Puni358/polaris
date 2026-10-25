# State Continuity Audit (`STATE_CONTINUITY_AUDIT.md`)

**GATE CONTEXT**: POLARIS EMS GAP19 — Controlled Digital-Twin 8-Cycle MPC Integration Test  
**VERDICT**: `PASS`

---

## 1. Field-by-Field Continuity Table

| Cycle Transition | Output Timestamp | Energy Output (Wh) | Energy Calculated (Wh) | SOC Output (%) | SOC Calculated (%) | Diesel Running | Diesel Hours | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Cycle 1 | `2024-01-01T21:00:00Z` | 186739.13 | 186739.13 | 93.37% | 93.37% | `True` | 1.0h | `PASS` |
| Cycle 2 | `2024-01-01T22:00:00Z` | 186739.13 | 186739.13 | 93.37% | 93.37% | `True` | 2.0h | `PASS` |
| Cycle 3 | `2024-01-01T23:00:00Z` | 186739.13 | 186739.13 | 93.37% | 93.37% | `True` | 3.0h | `PASS` |
| Cycle 4 | `2024-01-02T00:00:00Z` | 186739.13 | 186739.13 | 93.37% | 93.37% | `True` | 4.0h | `PASS` |
| Cycle 5 | `2024-01-02T01:00:00Z` | 186739.13 | 186739.13 | 93.37% | 93.37% | `True` | 5.0h | `PASS` |
| Cycle 6 | `2024-01-02T02:00:00Z` | 186739.13 | 186739.13 | 93.37% | 93.37% | `True` | 6.0h | `PASS` |
| Cycle 7 | `2024-01-02T03:00:00Z` | 186739.13 | 186739.13 | 93.37% | 93.37% | `True` | 7.0h | `PASS` |
| Cycle 8 | `2024-01-02T04:00:00Z` | 186739.13 | 186739.13 | 93.37% | 93.37% | `True` | 8.0h | `PASS` |

---

## 2. Field Continuity Audit Findings

| Field Name | Cycle N Output | Cycle N+1 Input | Propagation Relation | Audit Status |
| :--- | :--- | :--- | :--- | :---: |
| `timestamp` | `t_{n+1}` | `t_{n+1}` | Exact equality ($+1\text{h}$) | `PASS` |
| `battery_energy_wh` | $E_{n+1}$ | $E_{n+1}$ | $E_{n+1} = E_n + (\eta_{\text{ch}} P_{\text{chg}} - \frac{P_{\text{dis}}}{\eta_{\text{dis}}})\Delta t$ | `PASS` |
| `battery_soc_pct` | $\text{SOC}_{n+1}$ | $\text{SOC}_{n+1}$ | $\text{SOC}_{n+1} = E_{n+1} / C \times 100\%$ | `PASS` |
| `diesel_running` | `bool` | `bool` | $\mathbb{I}(P_{\text{diesel}} > 0)$ | `PASS` |
| `diesel_hours_running` | `hours` | `hours` | Cumulative counter ($+1.0\text{h}$ if running) | `PASS` |
| `operating_mode` | `NORMAL` | `NORMAL` | Preserved | `PASS` |

---

## 3. Fuel State Note

Fuel volume/mass is not represented in the `StationState` schema (fuel consumption rate is calculated strictly in solver metrics and telemetry).

Classified:
```text
FUEL_STATE_CONTINUITY = NOT_ESTABLISHED
STATE_CONTINUITY = PASS
```
