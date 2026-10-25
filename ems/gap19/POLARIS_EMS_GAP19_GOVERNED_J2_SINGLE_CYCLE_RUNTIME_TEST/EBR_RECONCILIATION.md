# EBR Calculation Reconciliation Report

## 1. Governed EBR Lookahead Equation

The governed Emergency Battery Reserve (EBR) target is calculated over the 6-hour forward lookahead window $W(t) = \{t, \dots, \min(t+5, 23)\}$ taking into account battery discharge efficiency $\eta_{\text{dis}} = 0.92$:

\[
E_{\text{EBR,target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k \in W(t)} P_{\text{crit}}[k] \cdot \Delta t
\]

---

## 2. Independent Target Trajectory Reconciliation

For constant synthetic protected critical demand $P_{\text{crit}} = 20,000\text{ W}$ and $\Delta t = 1.0\text{ h}$:

| Timestep $t$ | Lookahead Window $W(t)$ | Sum Critical Demand ($W(t)$) | Expected $E_{\text{EBR,target}}[t]$ | Optimizer Target | Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| $t = 0 \dots 18$ | $6\text{ hours}$ ($t \dots t+5$) | $120,000\text{ Wh}$ | **$130,434.78\text{ Wh}$** | $130,434.78\text{ Wh}$ | **MATCH** |
| $t = 19$ | $5\text{ hours}$ ($19 \dots 23$) | $100,000\text{ Wh}$ | **$108,695.65\text{ Wh}$** | $108,695.65\text{ Wh}$ | **MATCH** |
| $t = 20$ | $4\text{ hours}$ ($20 \dots 23$) | $80,000\text{ Wh}$ | **$86,956.52\text{ Wh}$** | $86,956.52\text{ Wh}$ | **MATCH** |
| $t = 21$ | $3\text{ hours}$ ($21 \dots 23$) | $60,000\text{ Wh}$ | **$65,217.39\text{ Wh}$** | $65,217.39\text{ Wh}$ | **MATCH** |
| $t = 22$ | $2\text{ hours}$ ($22 \dots 23$) | $40,000\text{ Wh}$ | **$43,478.26\text{ Wh}$** | $43,478.26\text{ Wh}$ | **MATCH** |
| $t = 23$ | $1\text{ hour}$ ($23$) | $20,000\text{ Wh}$ | **$21,739.13\text{ Wh}$** | $21,739.13\text{ Wh}$ | **MATCH** |

---

## 3. Findings

1. The optimizer's internal EBR lookahead calculations match independent hand calculations **to 2 decimal places**.
2. Discharge efficiency $\eta_{\text{dis}} = 0.92$ is correctly included.
3. No future actual observations or indices beyond $t=23$ are accessed.

---

## 4. Verdict

```
EBR_CALCULATION_CORRECT = YES
INDEXING_CORRECT = YES
DISCHARGE_EFFICIENCY_ACCOUNTED = YES
EBR_RECONCILIATION_STATUS = PASS
```
