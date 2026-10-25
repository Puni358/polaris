# BOUND AUDIT

## BOUND SPECIFICATION AND AUDIT

All 385 variables possess explicitly declared physical lower bounds ($lb$) and upper bounds ($ub$).

1. **Non-negativity**: All variables have $lb_j \ge 0.0$.
2. **Physical Asset Ratings**:
   - Diesel generation upper bound: $5000.0\text{ W}$.
   - Battery charge/discharge power upper bounds: $2500.0\text{ W}$.
   - Battery minimum energy capacity bound: $2000.0\text{ Wh}$ (20% of 10 kWh nominal).
   - Battery maximum energy capacity bound: $10000.0\text{ Wh}$.
3. **Availability Bounds**:
   - $P_{\text{pv,use}}(t), P_{\text{pv,curt}}(t) \le P_{\text{pv,avail}}(t)$.
   - $P_{\text{wind,use}}(t), P_{\text{wind,curt}}(t) \le P_{\text{wind,avail}}(t)$.
   - $P_{\text{unmet}}(t) \le P_{\text{load}}(t)$.
4. **Binary Bounds**: $u_j \in [0.0, 1.0]$.

`BOUND_IDENTITY_A_B` = `PASS`
