# D4 DYNAMIC CRITICAL LOAD

## 1. DYNAMIC $P_{i,\text{min}}(t)$ REQUIREMENT ALIGNMENT

DEC-004 D1 states:
> "Required critical power may vary dynamically: $P_{\text{critical}}(t)$. The station defines the protected equipment. The runtime must not dynamically redefine which equipment is protected merely because power is scarce."

---

## 2. ARCHITECTURAL IMPLICATIONS FOR D4
1. **Dynamic Minimum Viable Vectors**: Minimum viable operating levels $P_{i,\text{min}}(t)$ are time-varying functions of environmental factors (e.g. ambient temperature affecting heating minimums or water usage schedules).
2. **Fixed Protected Set, Dynamic Power**: The set of protected equipment categories $\mathcal{C} = \{\text{heating}, \text{water}, \text{comms}\}$ is fixed by station engineering, while their power requirement vector $P_{i,\text{min}}(t)$ varies hour-by-hour in `ForecastBundle`.
3. **Proportional Allocation Over Time**: At each timestep $t$, $\alpha(t)$ is re-evaluated based on that hour's dynamic minimum requirements:
$$\alpha(t) = \frac{P_{\text{crit,avail}}(t)}{\sum_{i \in \mathcal{C}} P_{i,\text{min}}(t)}$$
