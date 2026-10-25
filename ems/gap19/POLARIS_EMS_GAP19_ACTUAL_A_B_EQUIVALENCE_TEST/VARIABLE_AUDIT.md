# VARIABLE AUDIT

## COMPLETE INDEXING AND VARIABLE CLASSIFICATION (385 VARIABLES)

| Variable Index Range | Name Scheme | Count | Type | Physical Bounds | Units |
|---|---|---|---|---|---|
| $15t + 0$ ($t=0..23$) | $P_{\text{diesel}}(t)$ | 24 | Continuous | $[0.0, 5000.0]$ | W |
| $15t + 1$ ($t=0..23$) | $u_{\text{diesel}}(t)$ | 24 | Binary | $\{0, 1\}$ | unitless |
| $15t + 2$ ($t=0..23$) | $v_{\text{start}}(t)$ | 24 | Binary | $\{0, 1\}$ | unitless |
| $15t + 3$ ($t=0..23$) | $w_{\text{stop}}(t)$ | 24 | Binary | $\{0, 1\}$ | unitless |
| $15t + 4$ ($t=0..23$) | $P_{\text{batt,ch}}(t)$ | 24 | Continuous | $[0.0, 2500.0]$ | W |
| $15t + 5$ ($t=0..23$) | $P_{\text{batt,dis}}(t)$ | 24 | Continuous | $[0.0, 2500.0]$ | W |
| $15t + 6$ ($t=0..23$) | $u_{\text{ch}}(t)$ | 24 | Binary | $\{0, 1\}$ | unitless |
| $15t + 7$ ($t=0..23$) | $u_{\text{dis}}(t)$ | 24 | Binary | $\{0, 1\}$ | unitless |
| $15t + 8$ ($t=0..23$) | $E_{\text{batt}}(t)$ | 24 | Continuous | $[2000.0, 10000.0]$ | Wh |
| $15t + 9$ ($t=0..23$) | $P_{\text{pv,use}}(t)$ | 24 | Continuous | $[0.0, P_{\text{pv,avail}}(t)]$ | W |
| $15t + 10$ ($t=0..23$) | $P_{\text{pv,curt}}(t)$ | 24 | Continuous | $[0.0, P_{\text{pv,avail}}(t)]$ | W |
| $15t + 11$ ($t=0..23$) | $P_{\text{wind,use}}(t)$ | 24 | Continuous | $[0.0, P_{\text{wind,avail}}(t)]$ | W |
| $15t + 12$ ($t=0..23$) | $P_{\text{wind,curt}}(t)$ | 24 | Continuous | $[0.0, P_{\text{wind,avail}}(t)]$ | W |
| $15t + 13$ ($t=0..23$) | $P_{\text{unmet}}(t)$ | 24 | Continuous | $[0.0, P_{\text{load}}(t)]$ | W |
| $15t + 14$ ($t=0..23$) | $P_{\text{flex,served}}(t)$ | 24 | Continuous | $[0.0, 500.0]$ | W |
| $360..383$ | $s_{\text{EBR}}(t)$ | 24 | Continuous | $[0.0, 10000.0]$ | Wh |
| $384$ | $s_{\text{term}}$ | 1 | Continuous | $[0.0, 10000.0]$ | Wh |

- **Total Variable Count**: 385
- **Binary Variables**: 120
- **Continuous Variables**: 265
