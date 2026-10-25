# CURRENT MILP VARIABLE AUDIT

## Detailed 15-Variable Timestep Structure Audit

This document details the exact 15 decision variables defined per timestep $t \in \{0, \dots, 23\}$ in [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py).

---

## Timestep Variable Index Register ($K = 15$)

| Index Offset | Variable Name | Type | Lower Bound | Upper Bound | Physical Unit | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `base + 0` | `p_sol_used` | Continuous | $0.0$ | $P_{\text{solar,gen}}(t)$ | Watts ($\text{W}$) | Solar power allocated to immediate load/charge. |
| `base + 1` | `p_wind_used` | Continuous | $0.0$ | $P_{\text{wind,gen}}(t)$ | Watts ($\text{W}$) | Wind power allocated to immediate load/charge. |
| `base + 2` | `p_curt_sol` | Continuous | $0.0$ | $P_{\text{solar,gen}}(t)$ | Watts ($\text{W}$) | Curtailed solar power. |
| `base + 3` | `p_curt_wind` | Continuous | $0.0$ | $P_{\text{wind,gen}}(t)$ | Watts ($\text{W}$) | Curtailed wind power. |
| `base + 4` | `p_chg` | Continuous | $0.0$ | $P_{\text{max,chg}}$ | Watts ($\text{W}$) | Battery charging power. |
| `base + 5` | `p_dis` | Continuous | $0.0$ | $P_{\text{max,dis}}$ | Watts ($\text{W}$) | Battery discharging power. |
| `base + 6` | `E_next` | Continuous | $E_{\text{min}}$ | $E_{\text{max}}$ | Watt-hours ($\text{Wh}$) | Battery state-of-charge energy at end of timestep $t$. |
| `base + 7` | `p_diesel` | Continuous | $0.0$ | $P_{\text{max,diesel}}$ | Watts ($\text{W}$) | Diesel generator output power. |
| `base + 8` | `p_served` | Continuous | $0.0$ | $P_{\text{demand}}(t)$ | Watts ($\text{W}$) | Critical load power served. |
| `base + 9` | `p_unmet` | Continuous | $0.0$ | $P_{\text{demand}}(t)$ | Watts ($\text{W}$) | Unmet critical load power. |
| `base + 10` | `p_flex` | Continuous | $0.0$ | $P_{\text{flex,power}}$ | Watts ($\text{W}$) | Flexible load power served. |
| `base + 11` | `u_chg` | Binary | $0.0$ | $1.0$ | $\{0, 1\}$ | Battery charging indicator. |
| `base + 12` | `u_dis` | Binary | $0.0$ | $1.0$ | $\{0, 1\}$ | Battery discharging indicator. |
| `base + 13` | `u_diesel` | Binary | $0.0$ | $1.0$ | $\{0, 1\}$ | Diesel generator commitment status. |
| `base + 14` | `v_start` | Binary | $0.0$ | $1.0$ | $\{0, 1\}$ | Diesel generator startup indicator. |
