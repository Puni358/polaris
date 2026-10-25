# POLARIS EMS GATE-09 — OPTION B CONSTRAINT AUDIT

## 1. Constraint Verification Purpose
This document provides a mathematical and empirical audit of all 6 constraint categories enforced by Option B (`GAP19HighsNativeOptimizer`).

## 2. Mathematical & Empirical Constraint Audit

### 2.1 Critical Load Constraint (Audit Item 3)
- **Constraint**: $P_{\text{served}}[t] + P_{\text{unmet\_crit}}[t] = P_{\text{crit}}[t]$
- **Penalty**: Objective function includes $1 \times 10^9 \cdot P_{\text{unmet\_crit}}[t]$.
- **Audit Verification**: For all 24 steps in feasible NORMAL mode, $P_{\text{unmet\_crit}}[t] = 0.0$ and $P_{\text{served}}[t] = P_{\text{crit}}[t]$. Hard critical load policy is 100% satisfied.
- Status: **PASS**

### 2.2 Physical Battery & SOC Constraints (Audit Item 4)
- **Constraint**: $E_{\min} \le E_{\text{bat}}[t] \le E_{\max}$, $0 \le P_{\text{chg}}[t] \le P_{\text{chg\_max}} \cdot u_{\text{chg}}[t]$, $0 \le P_{\text{dis}}[t] \le P_{\text{dis\_max}} \cdot u_{\text{dis}}[t]$, $u_{\text{chg}}[t] + u_{\text{dis}}[t] \le 1$.
- **Audit Verification**: Evaluated across 24h horizon. SOC remains strictly inside $[20.0\%, 95.0\%]$. Exclusivity $u_{\text{chg}} + u_{\text{dis}} \le 1$ holds.
- Status: **PASS**

### 2.3 Diesel Generator Constraints (Audit Item 5)
- **Constraint**: $P_{\text{min\_diesel}} \cdot u_{\text{diesel}}[t] \le P_{\text{diesel}}[t] \le P_{\text{max\_diesel}} \cdot u_{\text{diesel}}[t]$.
- **Audit Verification**: When diesel runs ($u_{\text{diesel}}=1$), power output is bounded between $10 \text{ kW}$ and $100 \text{ kW}$. When off ($u_{\text{diesel}}=0$), power output is $0 \text{ W}$.
- Status: **PASS**

### 2.4 Bus-Bar Power Balance (Audit Item 6)
- **Constraint**: $P_{\text{solar\_used}}[t] + P_{\text{wind\_used}}[t] + P_{\text{discharge}}[t] + P_{\text{diesel}}[t] = P_{\text{served}}[t] + P_{\text{charge}}[t] + P_{\text{spill}}[t]$.
- **Audit Verification**: `energy_balance_errors` computed across all 24 hours equals $0.0 \text{ W}$ for every timestep.
- Status: **PASS**

### 2.5 Renewable Generation & Curtailment (Audit Item 7)
- **Constraint**: $0 \le P_{\text{solar\_used}}[t] \le P_{\text{solar\_max}}[t]$, $0 \le P_{\text{wind\_used}}[t] \le P_{\text{wind\_max}}[t]$, $P_{\text{curtailment}} \ge 0$.
- **Audit Verification**: Solar and wind usage never exceed forecast available generation.
- Status: **PASS**

## 3. Constraint Audit Summary

| Constraint Category | Governed Mathematical Boundary | Empirical Result | Status |
| :--- | :--- | :--- | :---: |
| Critical Load | $P_{\text{unmet\_crit}} = 0$ in feasible mode | $0.0 \text{ W}$ unmet load | PASS |
| Battery SOC | $20.0\% \le \text{SOC} \le 95.0\%$ | Bounded in $[20.0\%, 95.0\%]$ | PASS |
| Battery Exclusivity | $u_{\text{chg}} + u_{\text{dis}} \le 1$ | No simultaneous chg/dis | PASS |
| Diesel Bounds | $10 \text{ kW} \le P_{\text{diesel}} \le 100 \text{ kW}$ when active | Fully respected | PASS |
| Power Balance | Bus-Bar $\sum P_{\text{gen}} = \sum P_{\text{load}}$ | $0.0 \text{ W}$ balance error | PASS |
| Renewables | $P_{\text{used}} \le P_{\text{gen\_max}}$ | No generation exceedance | PASS |
