# BASE VARIABLE PRESERVATION

## 100% PRESERVATION OF BASELINE 360 VARIABLES

All 360 base decision variables from production `milp.py` retain their exact physical semantics, bounds, and ordering in indices $0 \dots 359$:
- $15t+0$: `p_sol_used` (`PRESERVED`)
- $15t+1$: `p_wind_used` (`PRESERVED`)
- $15t+2$: `p_curt_sol` (`PRESERVED`)
- $15t+3$: `p_curt_wind` (`PRESERVED`)
- $15t+4$: `p_chg` (`PRESERVED`)
- $15t+5$: `p_dis` (`PRESERVED`)
- $15t+6$: `E_next` (`PRESERVED`)
- $15t+7$: `p_diesel` (`PRESERVED`)
- $15t+8$: `p_served` (`PRESERVED`)
- $15t+9$: `p_unmet` (`PRESERVED`)
- $15t+10$: `p_flex` (`PRESERVED`)
- $15t+11$: `u_chg` (`PRESERVED`)
- $15t+12$: `u_dis` (`PRESERVED`)
- $15t+13$: `u_diesel` (`PRESERVED`)
- $15t+14$: `v_start` (`PRESERVED`)
