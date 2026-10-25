# CURRENT MILP CONSTRAINT AUDIT

## Audit of Physical & Operational Constraints

This document details the 12 physical constraint equations implemented per timestep in [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py).

---

## Constraint Equation Register

### 1. Solar Generation Decomposition
$$P_{\text{sol,used}}(t) + P_{\text{curt,sol}}(t) = P_{\text{solar,gen}}(t)$$

### 2. Wind Generation Decomposition
$$P_{\text{wind,used}}(t) + P_{\text{curt,wind}}(t) = P_{\text{wind,gen}}(t)$$

### 3. Bus-Bar Energy Balance Equation
$$P_{\text{sol,used}}(t) + P_{\text{wind,used}}(t) + P_{\text{dis}}(t) + P_{\text{diesel}}(t) - P_{\text{served}}(t) - P_{\text{chg}}(t) - P_{\text{flex}}(t) = 0$$

### 4. Demand Deficit Balance Equation
$$P_{\text{served}}(t) + P_{\text{unmet}}(t) = P_{\text{demand}}(t)$$

### 5–6. Battery Power Bounds vs Binary Commitments
$$P_{\text{chg}}(t) - P_{\text{max,chg}} \cdot u_{\text{chg}}(t) \le 0$$
$$P_{\text{dis}}(t) - P_{\text{max,dis}} \cdot u_{\text{dis}}(t) \le 0$$

### 7. Battery Charge / Discharge Exclusivity
$$u_{\text{chg}}(t) + u_{\text{dis}}(t) \le 1$$

### 8. Battery Discrete Energy State Transition Equation
$$E(t+1) - E(t) - \eta_{\text{chg}} P_{\text{chg}}(t) \Delta t + \frac{P_{\text{dis}}(t)}{\eta_{\text{dis}}} \Delta t = 0$$

### 9–10. Generator Power Bounds when Operating
$$P_{\text{diesel}}(t) - P_{\text{min,diesel}} \cdot u_{\text{diesel}}(t) \ge 0$$
$$P_{\text{diesel}}(t) - P_{\text{max,diesel}} \cdot u_{\text{diesel}}(t) \le 0$$

### 11. Generator Startup Tracking Equation
$$v_{\text{start}}(t) - u_{\text{diesel}}(t) + u_{\text{diesel}}(t-1) \ge 0$$

### 12. Flexible Load Deferrable Window Energy Total Constraint
$$\sum_{t=t_{\text{start}}}^{t_{\text{finish}}-1} P_{\text{flex}}(t) = E_{\text{flex,total}}$$
