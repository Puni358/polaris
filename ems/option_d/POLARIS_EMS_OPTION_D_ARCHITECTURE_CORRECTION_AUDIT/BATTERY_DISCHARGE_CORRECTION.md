# BATTERY DISCHARGE CORRECTION

## 1. BUSBAR DECOMPOSITION FOR BATTERY CRITICAL-ONLY DISCHARGE

The audit corrected the upper-bound constraint $0 \le P_{\text{dis}}[t] \le P_{\text{critical}}[t]$ to prove that battery energy CANNOT physically or economically leak to noncritical loads.

---

## 2. INSUFFICIENCY OF UPPER-BOUND ALONE

Setting $P_{\text{dis}}[t] \le P_{\text{critical}}[t]$ on a common busbar equation:
$$P_{\text{sol,u}} + P_{\text{wind,u}} + P_{\text{dis}} + P_{\text{diesel}} = P_{\text{served,crit}} + P_{\text{served,flex}} + P_{\text{chg}}$$
does **NOT** guarantee that battery energy serves critical load. In a linear solver, if diesel is running and battery is discharging, battery power could flow to $P_{\text{served,flex}}$ while diesel serves $P_{\text{served,crit}}$.

---

## 3. CORRECTED DECOUPLED LOAD BUSBAR FORMULATION

To enforce DEC-004 D2 ("Battery discharge during Option D is permitted ONLY for protected critical load"):

### Critical Load Busbar Balance:
$$P_{\text{served,crit}}[t] = P_{\text{sol,crit}}[t] + P_{\text{wind,crit}}[t] + P_{\text{dis}}[t] + P_{\text{dies,crit}}[t]$$

### Flexible Load Busbar Balance:
$$P_{\text{served,flex}}[t] = P_{\text{sol,flex}}[t] + P_{\text{wind,flex}}[t] + P_{\text{dies,flex}}[t]$$

- **Key Rule**: $P_{\text{dis}}[t]$ is **STRICTLY OMITTED** from the flexible load balance equation.
- **Result**: Battery discharge power $P_{\text{dis}}[t]$ can physically enter ONLY the critical load balance equation. Battery discharge to flexible load is mathematically forced to **ZERO**.
