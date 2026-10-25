# Base 360-Variable Preservation Audit

The layout of the first 360 variables per timestep $t$ ($K=15$) matches the baseline `milp.py` model exactly:

- `base + 0`: $P_{\text{sol,used}}[t]$
- `base + 1`: $P_{\text{wind,used}}[t]$
- `base + 2`: $P_{\text{curt,sol}}[t]$
- `base + 3`: $P_{\text{curt,wind}}[t]$
- `base + 4`: $P_{\text{chg}}[t]$
- `base + 5`: $P_{\text{dis}}[t]$
- `base + 6`: $E_{\text{next}}[t]$
- `base + 7`: $P_{\text{diesel}}[t]$
- `base + 8`: $P_{\text{served}}[t]$
- `base + 9`: $P_{\text{unmet}}[t]$
- `base + 10`: $P_{\text{flex}}[t]$
- `base + 11`: $u_{\text{chg}}[t]$ (Binary)
- `base + 12`: $u_{\text{dis}}[t]$ (Binary)
- `base + 13`: $u_{\text{diesel}}[t]$ (Binary)
- `base + 14`: $v_{\text{start}}[t]$ (Binary)

`BASE_360_PRESERVATION = PASS`
