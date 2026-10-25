# CURRENT VARIABLE MAP

## COMPLETE VARIABLE INDEXING TABLE FOR PRODUCTION `milp.py` (360 VARIABLES)

Each timestep $t \in \{0, \dots, 23\}$ contains $K = 15$ variables ($15 \times 24 = 360$):

| Index Formula ($15t + k$) | Variable Name | Physical Meaning | Type | Lower Bound | Upper Bound | Source Lines |
|---|---|---|---|---|---|---|
| $15t + 0$ | `p_sol_used` | Solar power used by microgrid | Continuous | $0.0$ | $P_{\text{pv,avail}}(t)$ | Line 117 |
| $15t + 1$ | `p_wind_used` | Wind power used by microgrid | Continuous | $0.0$ | $P_{\text{wind,avail}}(t)$ | Line 118 |
| $15t + 2$ | `p_curt_sol` | Solar power curtailed | Continuous | $0.0$ | $P_{\text{pv,avail}}(t)$ | Line 119 |
| $15t + 3$ | `p_curt_wind` | Wind power curtailed | Continuous | $0.0$ | $P_{\text{wind,avail}}(t)$ | Line 120 |
| $15t + 4$ | `p_chg` | Battery charging power | Continuous | $0.0$ | $P_{\text{chg,max}}$ ($50\text{kW}$) | Line 121 |
| $15t + 5$ | `p_dis` | Battery discharging power | Continuous | $0.0$ | $P_{\text{dis,max}}$ ($50\text{kW}$) | Line 122 |
| $15t + 6$ | `E_next` | Battery energy state at $t+1$ | Continuous | $E_{\text{min}}$ ($20\%$) | $E_{\text{max}}$ ($95\%$) | Line 123 |
| $15t + 7$ | `p_diesel` | Diesel generator power output | Continuous | $0.0$ | $P_{\text{diesel,max}}$ ($100\text{kW}$)| Line 124 |
| $15t + 8$ | `p_served` | Served load power | Continuous | $0.0$ | $P_{\text{demand}}(t)$ | Line 125 |
| $15t + 9$ | `p_unmet` | Unmet load power | Continuous | $0.0$ | $P_{\text{demand}}(t)$ | Line 126 |
| $15t + 10$ | `p_flex` | Flexible load served power | Continuous | $0.0$ | $P_{\text{flex,max}}$ | Line 128 |
| $15t + 11$ | `u_chg` | Battery charge mode binary | Binary | $0$ | $1$ | Line 139 |
| $15t + 12$ | `u_dis` | Battery discharge mode binary | Binary | $0$ | $1$ | Line 140 |
| $15t + 13$ | `u_diesel` | Diesel generator running status | Binary | $0$ | $1$ | Line 141 |
| $15t + 14$ | `v_start` | Diesel generator startup event | Binary | $0$ | $1$ | Line 142 |
