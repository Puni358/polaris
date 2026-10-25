# Cycle-by-Cycle Transition Table (`CYCLE_TRANSITION_TABLE.md`)

**GATE CONTEXT**: POLARIS EMS GAP19 — Digital Twin State-Continuity Forensic Review  
**VERDICT**: `PASS`

---

## Complete 8-Cycle State Transition Matrix

| Transition | Origin TS | Next TS | Input Energy (Wh) | Input SOC (%) | Committed Action $k=0$ ($P_{\text{chg}}, P_{\text{dis}}, P_{\text{dies}}$) [W] | Output Energy (Wh) | Output SOC (%) | Diesel Run | Diesel Hours | State Provenance | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Initial** | `2024-01-01T20:00:00Z` | — | 160,000.00 | 80.00% | — | — | — | `False` | 0.0h | Scenario Fixture | — |
| **C1 → C2** | `2024-01-01T20:00:00Z` | `2024-01-01T21:00:00Z` | 160,000.00 | 80.00% | `(29064.27, 0.0, 44064.27)` | 186,739.13 | 93.37% | `True` | 1.0h | Digital Twin Step | `PASS` |
| **C2 → C3** | `2024-01-01T21:00:00Z` | `2024-01-01T22:00:00Z` | 186,739.13 | 93.37% | `(0.0, 0.0, 15000.00)` | 186,739.13 | 93.37% | `True` | 2.0h | Digital Twin Step | `PASS` |
| **C3 → C4** | `2024-01-01T22:00:00Z` | `2024-01-01T23:00:00Z` | 186,739.13 | 93.37% | `(0.0, 0.0, 15000.00)` | 186,739.13 | 93.37% | `True` | 3.0h | Digital Twin Step | `PASS` |
| **C4 → C5** | `2024-01-01T23:00:00Z` | `2024-01-02T00:00:00Z` | 186,739.13 | 93.37% | `(0.0, 0.0, 15000.00)` | 186,739.13 | 93.37% | `True` | 4.0h | Digital Twin Step | `PASS` |
| **C5 → C6** | `2024-01-02T00:00:00Z` | `2024-01-02T01:00:00Z` | 186,739.13 | 93.37% | `(0.0, 0.0, 15000.00)` | 186,739.13 | 93.37% | `True` | 5.0h | Digital Twin Step | `PASS` |
| **C6 → C7** | `2024-01-02T01:00:00Z` | `2024-01-02T02:00:00Z` | 186,739.13 | 93.37% | `(0.0, 0.0, 15000.00)` | 186,739.13 | 93.37% | `True` | 6.0h | Digital Twin Step | `PASS` |
| **C7 → C8** | `2024-01-02T02:00:00Z` | `2024-01-02T03:00:00Z` | 186,739.13 | 93.37% | `(0.0, 0.0, 15000.00)` | 186,739.13 | 93.37% | `True` | 7.0h | Digital Twin Step | `PASS` |
| **C8 End** | `2024-01-02T03:00:00Z` | `2024-01-02T04:00:00Z` | 186,739.13 | 93.37% | `(0.0, 0.0, 15000.00)` | 186,739.13 | 93.37% | `True` | 8.0h | Digital Twin Step | `PASS` |

---

## Transformation Analysis

- **Battery Stored Energy ($E$)**: Updated in C1 by $+26,739.13$ Wh via $29,064.27 \text{ W} \times 0.92 \times 1\text{h}$. Sustained at $186,739.13$ Wh ($\text{SOC} = 93.37\%$) in C2–C8 because battery charge and discharge power decisions are 0.0 W.
- **Diesel Runtime Hours**: Monotonically increments by $+1.0\text{h}$ per cycle ($0.0 \to 1.0 \to 2.0 \to 3.0 \to 4.0 \to 5.0 \to 6.0 \to 7.0 \to 8.0\text{h}$) because committed diesel dispatch power is $>0.0$ W across all 8 cycles.
- **Timestamp**: Strictly increments by $+1\text{h}$ ISO 8601 UTC across all transitions, including the midnight crossing at $C4 \to C5$.
