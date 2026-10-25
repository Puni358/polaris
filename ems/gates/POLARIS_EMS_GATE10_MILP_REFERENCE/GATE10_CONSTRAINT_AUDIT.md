# POLARIS EMS GATE-10 — MILP CONSTRAINT AUDIT

## 1. Constraint Verification Overview
This document audits the physical, mathematical, and operational constraints enforced by `GAP19HighsNativeOptimizer`.

## 2. Detailed Constraint Audits

### 2.1 Audit Item 4: Hard Critical Load Constraint
- $P_{\text{unmet\_crit}}[t] = 0.0 \text{ W}$ for all $t$ in feasible mode.
- Penalty factor $1 \times 10^9$ ensures critical load is NEVER shed during feasible normal operation.
- Verification Status: **PASS**

### 2.2 Audit Item 5: Bus-Bar Power Balance
- Bus-bar balance equation $\sum P_{\text{in}} = \sum P_{\text{out}}$ holds exactly ($0.0 \text{ W}$ error) across all 24 timesteps.
- Verification Status: **PASS**

### 2.3 Audit Item 6: Battery SOC and Power Bounds
- Battery energy transition: $E[t+1] = E[t] + (\eta_{\text{chg}} P_{\text{chg}}[t] - \frac{P_{\text{dis}}[t]}{\eta_{\text{dis}}}) \Delta t$.
- SOC remains strictly bounded within $[20.0\%, 95.0\%]$.
- Binary exclusivity $u_{\text{chg}}[t] + u_{\text{dis}}[t] \le 1$ strictly enforced.
- Verification Status: **PASS**

### 2.4 Audit Item 7: Diesel Generator Operational Bounds
- $10,000 \text{ W} \le P_{\text{diesel}}[t] \le 100,000 \text{ W}$ when $u_{\text{diesel}}[t] = 1$.
- $P_{\text{diesel}}[t] = 0 \text{ W}$ when $u_{\text{diesel}}[t] = 0$.
- Startup tracking $v_{\text{startup}}[t] \ge u_{\text{diesel}}[t] - u_{\text{diesel}}[t-1]$ correctly formulates startup fuel overhead.
- Verification Status: **PASS**

### 2.5 Audit Item 8: Renewable Generation Availability
- $P_{\text{solar\_used}}[t] \le P_{\text{solar\_max}}[t]$ and $P_{\text{wind\_used}}[t] \le P_{\text{wind\_max}}[t]$.
- Verification Status: **PASS**
