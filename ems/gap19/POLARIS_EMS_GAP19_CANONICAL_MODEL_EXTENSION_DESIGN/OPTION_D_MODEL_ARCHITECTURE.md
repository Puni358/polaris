# OPTION D MODEL ARCHITECTURE

## PROTECTED CRITICAL LOAD FALLBACK POLICY ARCHITECTURE

1. **Operating Mode Ingestion**: Receives `operating_mode` parameter from ECD (`NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID`).
2. **Proportional Critical Allocation (D4)**:
   - When total available power $P_{\text{avail,crit}} < \sum P_{\text{min},i}$, allocate served power proportionally:
     $$P_{i,\text{served}}(t) = \alpha(t) P_{i,\text{min}}(t), \quad \alpha(t) = \frac{P_{\text{avail,crit}}(t)}{\sum P_{\text{min},i}(t)} \in [0, 1]$$
   - Edge case $\sum P_{\text{min},i} = 0$: Handled cleanly with $\alpha(t) = 1.0$.
3. **Critical-Only Battery Discharge (D3)**:
   - In `EMERGENCY` mode: $P_{\text{batt,dis}}(t) \le P_{\text{served,crit}}(t)$ (Battery discharges ONLY to serve protected critical load).
4. **Excess Diesel Generation Routing (D6)**:
   - If diesel runs for critical load and produces excess power due to $P_{\text{diesel,min}}$, excess power is routed to battery charging up to $P_{\text{chg,max}}$. Remaining excess is curtailed.

`OPTION_D_ARCHITECTURE` = `ESTABLISHED`
