# CRITICAL LOAD GOVERNANCE CORRECTION
## EQUAL STATUTORY PRIORITY & PROPORTIONAL ALLOCATION RULES

### 1. SPECIFICATION RECONCILIATION
The 3-component protected critical load vector is retained in the synthetic fixture specification:
- **Heating**: $15.0\text{ kW}$
- **Water Treatment / Filtration**: $10.0\text{ kW}$
- **Emergency Communications**: $5.0\text{ kW}$
- **Total Aggregate Protected Demand ($P_{\text{critical\_total}}$)**: $30.0\text{ kW}$

### 2. HARD GOVERNANCE BOUNDARY RULE
**FORMAL GOVERNANCE STATEMENT**:
> *"The three protected critical load components (Heating 15 kW, Water 10 kW, Communications 5 kW) share EQUAL STATUTORY GOVERNANCE STATUS under Option D (DEC-004).*
>
> *Their different numerical power magnitudes (15 kW vs 10 kW vs 5 kW) do NOT establish a priority hierarchy (e.g. Heating > Water > Comms).*
>
> *The three components exist strictly to provide a non-uniform multi-dimensional vector for software validation of Option D proportional-allocation logic during supply deficits."*

### 3. PROPORTIONAL ALLOCATION MATHEMATICAL FORMULATION
When total available power $P_{\text{avail}}(t)$ is insufficient to cover total protected critical demand ($P_{\text{avail}}(t) < 30.0\text{ kW}$), power is allocated across the three subsystems strictly according to their baseline baseline ratio $\alpha_i$:

$$\alpha_{\text{heating}} = \frac{15}{30} = 50.0\%$$
$$\alpha_{\text{water}} = \frac{10}{30} = 33.33\%$$
$$\alpha_{\text{comms}} = \frac{5}{30} = 16.67\%$$

$$\text{Allocated } P_i(t) = P_{\text{avail}}(t) \times \alpha_i \quad \text{for } i \in \{\text{heating, water, comms}\}$$

Zero hierarchical load shedding occurs within protected critical components. All noncritical/flexible load ($15\text{ kW}$) is shed first before proportional allocation is applied to protected critical loads.

`CRITICAL_LOAD_GOVERNANCE_STATUS = RECONCILED_AND_CLEARED`.
