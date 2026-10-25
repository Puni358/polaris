# DIESEL EXCESS CHARGING ARCHITECTURE

## 1. D6 DIESEL MINIMUM OUTPUT & EXCESS CHARGING FORMULATION

Governance DEC-004 D6 requires:
> "If diesel is already required to support protected critical load and its minimum output creates excess generation:
> 1. use excess to charge battery
> 2. continue until battery allowable charging limit
> 3. curtail only remaining excess.
> NEVER: start diesel solely to charge battery."

---

## 2. MATHEMATICAL CONSTRAINTS & LOGIC

### A. Generator Minimum Power & Excess Generation
When the diesel generator is running ($u_{\text{diesel}}[t] = 1$), it must produce at least $P_{\text{diesel,min}} = 10.0$ kW ($10,000$ W).

If net critical load requirement ($P_{\text{crit,net}}[t] = P_{\text{critical}}[t] - P_{\text{ren,crit}}[t]$) is less than $P_{\text{diesel,min}}$, running the generator produces excess generation:

$$P_{\text{excess}}[t] = \max\left(0, P_{\text{diesel,min}} \cdot u_{\text{diesel}}[t] - P_{\text{crit,net}}[t]\right)$$

### B. Battery Charging from Excess
The excess generation MUST be allocated to battery charging up to its allowable charging limit ($P_{\text{chg,max}}$ and SOC ceiling $95\%$):

$$P_{\text{chg,excess}}[t] = \min\left(P_{\text{excess}}[t], P_{\text{chg,max}}, \frac{E_{\text{max}} - E[t]}{\eta_{\text{chg}} \Delta t}\right)$$

### C. Curtailment of Remaining Excess
Any remaining generation above battery charging capacity is curtailed:

$$P_{\text{curt,excess}}[t] = P_{\text{excess}}[t] - P_{\text{chg,excess}}[t]$$

### D. Prohibition of Diesel Startup Solely for Battery Charging
To enforce that diesel MUST NOT be started solely to charge the battery, a linear policy constraint ties diesel commitment ($u_{\text{diesel}}[t]$) to critical demand deficit:

$$u_{\text{diesel}}[t] \le \text{M} \cdot \left(P_{\text{critical}}[t] - P_{\text{ren}}[t] - P_{\text{dis,max}}[t]\right)_+$$

Where $(x)_+$ represents positive deficit. If available renewables + battery discharge can cover $P_{\text{critical}}[t]$, $u_{\text{diesel}}[t]$ is forced to $0$.
