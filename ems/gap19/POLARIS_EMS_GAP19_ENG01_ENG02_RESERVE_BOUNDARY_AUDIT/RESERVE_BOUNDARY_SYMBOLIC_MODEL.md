# POLARIS EMS GAP19 — RESERVE BOUNDARY SYMBOLIC MODEL

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_ENG01_ENG02_RESERVE_BOUNDARY_AUDIT`  
**Model Type**: **PURELY SYMBOLIC MATHEMATICAL DEPENDENCY MODEL**  

---

## 1. Symbolic Dependency Chain

The mathematical relationship connecting protected critical load to the governed maximum $s_{\text{J2}}$ reserve-shortfall boundary is established symbolically as follows:

```text
Protected Critical Load Trajectory P_critical(t)
        │
        ▼
Required AC Critical Energy W_crit_required(t) over Lookahead Window T_required
        │
        ▼
Required Battery Stored-Energy Reserve E_EBR_target(t) (Discharge Efficiency Efficiency_dis)
        │
        ▼
Total Required Battery Energy Floor E_floor(t) (Minimum Operational SOC_min)
        │
        ▼
Slack Variable Deficit s_J2[t] = max(0, E_floor(t) - E_next[t])
        │
        ▼
Governed Maximum Reserve Shortfall s_J2,max = max_t E_EBR_target(t)
```

---

## 2. Symbolic Formulations

### A. Required AC-Side Critical Energy ($W_{\text{crit\_required}}$)
For any timestep $t$ in the optimization horizon $t \in [0, N-1]$ over lookahead window $T_{\text{required}}$ (in hours):
$$W_{\text{crit\_required}}(t) = \int_{t}^{t + T_{\text{required}}} P_{\text{critical}}(\tau) \, d\tau$$

For discrete timesteps with step size $\Delta t$:
$$W_{\text{crit\_required}}(t) = \sum_{k=t}^{\min(t + T_{\text{required\_steps}} - 1, N - 1)} P_{\text{critical}}[k] \cdot \Delta t$$

### B. Required Battery Stored-Energy Reserve ($E_{\text{EBR\_target}}$)
Accounting for battery inverter and electrochemical discharge efficiency ($\eta_{\text{dis}}$):
$$E_{\text{EBR\_target}}(t) = \frac{1}{\eta_{\text{dis}}} \cdot W_{\text{crit\_required}}(t) = \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{\min(t + T_{\text{required\_steps}} - 1, N - 1)} P_{\text{critical}}[k] \cdot \Delta t$$

### C. Total Battery Stored-Energy Reserve Floor ($E_{\text{floor}}$)
The battery must maintain energy above the minimum operational State of Charge ($SOC_{\min} \cdot C_{\text{bat}} = E_{\min}$):
$$E_{\text{floor}}(t) = E_{\text{EBR\_target}}(t) + E_{\min} = E_{\text{EBR\_target}}(t) + C_{\text{bat}} \cdot SOC_{\min}$$

### D. Reserve Shortfall Variable ($s_{\text{J2}}$)
The slack variable $s_{\text{J2}}[t]$ represents the instantaneous energy deficit below the reserve floor at timestep $t$:
$$E_{\text{next}}[t] + s_{\text{J2}}[t] \ge E_{\text{floor}}(t)$$
$$s_{\text{J2}}[t] \ge E_{\text{EBR\_target}}(t) + E_{\min} - E_{\text{next}}[t]$$

### E. Governed Maximum Shortfall Bound ($s_{\text{J2,max}}$)
The maximum acceptable reserve shortfall $s_{\text{J2,max}}$ across the optimization horizon occurs when the battery energy drops to its minimum operational limit ($E_{\text{next}}[t] = E_{\min}$):
$$s_{\text{J2,max}} = \max_{t} \left( E_{\text{floor}}(t) - E_{\min} \right) = \max_{t} E_{\text{EBR\_target}}(t)$$

$$s_{\text{J2,max}} = \max_{t} \left( \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{\min(t + T_{\text{required\_steps}} - 1, N - 1)} P_{\text{critical}}[k] \cdot \Delta t \right)$$

---

## 3. Explicit AC-Side vs Battery-Side Energy Separation

1. **AC-Side Energy ($W_{\text{crit\_required}}$)**: Energy consumed by electrical equipment on the AC bus.
2. **Battery Stored Energy ($E_{\text{EBR\_target}}$)**: Chemical energy required inside the battery cells to deliver $W_{\text{crit\_required}}$ on the AC bus after accounting for discharge loss ($1 / \eta_{\text{dis}}$).
3. **Discharge Efficiency ($\eta_{\text{dis}}$)**: Combined battery cell and inverter discharge efficiency.

---

## 4. Boundary Statement

**NO NUMERICAL VALUES INFERRED**: This formulation is strictly symbolic. No specific numerical values for $P_{\text{critical}}(t)$, $\eta_{\text{dis}}$, $C_{\text{bat}}$, or $s_{\text{J2,max}}$ are assumed or asserted as production standards.
