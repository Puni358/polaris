# Critical Demand Fallback Forensics

- **Code Action**: `critical_demand = demand`.
- **Mathematical Impact in MILP**: In Layer B ($P_{\text{served}}[t] + P_{\text{unmet,critical}}[t] = P_{\text{critical\_demand}}[t]$), if `critical_demand` equals total demand, then $P_{\text{unmet,critical}}[t]$ measures total unmet load and penalizes all unmet load at priority 1 ($J_1$).
- **Classification**: `IMPLEMENTATION_ONLY_NOT_GOVERNED`.
