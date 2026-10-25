# Horizon & Indexing Static Audit

## 1. Horizon Parameters

- **MPC Decision Horizon**: $H = 24\text{ hours}$ ($24$ discrete timesteps of $\Delta t = 1.0\text{ h}$).
- **Forecast Horizon**: $24\text{ hours}$ ($t \in [0, 23]$).
- **EBR Survivability Horizon**: $T_{\text{REQUIRED}} = 6\text{ hours}$ ($6$ timesteps).

---

## 2. Timestep Window & Boundary Extension Analysis

| Decision Step $t$ | Lookahead Window $W(t)$ | Window Length | Boundary Extension Behavior | Causal Verification |
| :---: | :---: | :---: | :--- | :---: |
| $t = 0$ | $[0, 5]$ | $6\text{ h}$ | Full 6-hour lookahead within forecast horizon | **CAUSAL** |
| $t = 15$ | $[15, 20]$ | $6\text{ h}$ | Full 6-hour lookahead within forecast horizon | **CAUSAL** |
| $t = 18$ | $[18, 23]$ | $6\text{ h}$ | Full 6-hour lookahead touches horizon edge | **CAUSAL** |
| $t = 19$ | $[19, 23]$ | $5\text{ h}$ | Window truncates to remaining 5 forecast hours | **CAUSAL** |
| $t = 20$ | $[20, 23]$ | $4\text{ h}$ | Window truncates to remaining 4 forecast hours | **CAUSAL** |
| $t = 21$ | $[21, 23]$ | $3\text{ h}$ | Window truncates to remaining 3 forecast hours | **CAUSAL** |
| $t = 22$ | $[22, 23]$ | $2\text{ h}$ | Window truncates to remaining 2 forecast hours | **CAUSAL** |
| $t = 23$ | $[23, 23]$ | $1\text{ h}$ | Single-hour EBR; coupled with Terminal Target via max | **CAUSAL** |

---

## 3. Causality & Information Firewall

- Line 128: `end_k = min(t + 6, 24)` strictly bounds lookahead indexing to $k \le 23$.
- Code does **NOT** access indices $k \ge 24$, avoiding non-causal queries.
- Horizon edge effect for $t \ge 19$ is resolved via receding-horizon MPC rolling execution (re-observing and obtaining fresh 24h forecast at $t+1$).

---

## 4. Verdict

```
MPC_DECISION_HORIZON = 24H
FORECAST_HORIZON = 24H
EBR_SURVIVABILITY_HORIZON = 6H
BOUNDARY_EXTENSION = TRUNCATED_CAUSAL_LOOKAHEAD
FUTURE_ACTUAL_ACCESS = NONE (0)
HORIZON_INDEXING_STATUS = PASS
```
