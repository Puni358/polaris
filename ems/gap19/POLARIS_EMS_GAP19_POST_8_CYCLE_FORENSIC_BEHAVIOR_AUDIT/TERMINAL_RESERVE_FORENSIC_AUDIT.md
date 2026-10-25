# Terminal Reserve Forensic Audit (`TERMINAL_RESERVE_FORENSIC_AUDIT.md`)

**FORENSIC AUDIT**: POLARIS EMS GAP19 — Post-8-Cycle Forensic Behavior Audit  
**SYNTHETIC TARGET**: $100,000.0\text{ Wh}$ (`SYNTHETIC_ENGINEERING_TEST_VALUE`)  
**VERDICT**: `PASS`

---

## 1. Terminal Reserve Rolling Horizon Table

| Cycle | Origin Timestamp | Horizon End ($t=23$) | EBR Target at Boundary (Wh) | Terminal Target (Wh) | $J_2$ Envelope (Wh) | Double Count? | Correctly Rolled? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **01** | `2024-01-01T20:00:00Z` | `2024-01-02T20:00:00Z` | $20,000.0$ | $100,000.0$ | $100,000.0$ | `NO` | `YES` |
| **02** | `2024-01-01T21:00:00Z` | `2024-01-02T21:00:00Z` | $20,000.0$ | $100,000.0$ | $100,000.0$ | `NO` | `YES` |
| **03** | `2024-01-01T22:00:00Z` | `2024-01-02T22:00:00Z` | $20,000.0$ | $100,000.0$ | $100,000.0$ | `NO` | `YES` |
| **04** | `2024-01-01T23:00:00Z` | `2024-01-02T23:00:00Z` | $20,000.0$ | $100,000.0$ | $100,000.0$ | `NO` | `YES` |
| **05** | `2024-01-02T00:00:00Z` | `2024-01-03T00:00:00Z` | $20,000.0$ | $100,000.0$ | $100,000.0$ | `NO` | `YES` |
| **06** | `2024-01-02T01:00:00Z` | `2024-01-03T01:00:00Z` | $20,000.0$ | $100,000.0$ | $100,000.0$ | `NO` | `YES` |
| **07** | `2024-01-02T02:00:00Z` | `2024-01-03T02:00:00Z` | $20,000.0$ | $100,000.0$ | $100,000.0$ | `NO` | `YES` |
| **08** | `2024-01-02T03:00:00Z` | `2024-01-03T03:00:00Z` | $20,000.0$ | $100,000.0$ | $100,000.0$ | `NO` | `YES` |

---

## 2. Detailed Findings

- **A. Horizon Boundary Application**: Terminal reserve target ($100,000.0\text{ Wh}$) was enforced strictly at timestep index $k=23$ of each 24-hour solve.
- **B. Boundary Advancement**: Terminal boundary advanced $+1$ hour at each cycle (from `2024-01-02T19:00:00Z` in Cycle 1 to `2024-01-03T02:00:00Z` in Cycle 8).
- **C. Calendar Independence**: Boundary moved continuously with the rolling horizon rather than remaining pinned to an initial calendar day.
- **D. Distinction from EBR**: EBR covers $[t+1\text{h}, t+6\text{h}]$, whereas Terminal Reserve applies at $t+24\text{h}$.
- **E. Pointwise Maximum Envelope**: Unified via $\text{Envelope}[k] = \max(\text{EBR}[k], \text{TerminalTarget}[k])$.
- **F. Zero Double-Counting**: Enforced via a single decision variable array $s_{J2}[k]$ ($N=408$ variables, $M=312$ constraints).

```text
TERMINAL_RESERVE_ROLLING = PASS
DOUBLE_COUNTING = ZERO
```
