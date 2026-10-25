# PRODUCTION TO TARGET DELTA

## COMPREHENSIVE DELTA FROM 360-VARIABLE SCALAR MODEL TO CANONICAL TARGET

| Property | Current Production `milp.py` | Canonical GAP19 Target MILP | Architectural Action |
|---|---|---|---|
| Variable Count $N$ | 360 | 433 | Additive extension (+73 vars) |
| Binary Count | 96 | 120 | Additive extension (+24 $w_{\text{stop}}$) |
| Continuous Count | 264 | 313 | Additive extension (+49 cont) |
| Constraint Count $M$ | 264 | 313 | Additive extension (+49 constr) |
| Objective Architecture | Single scalar sum ($) | Lexicographic $[J_1, J_2, J_3, J_4]$ | Native HiGHS Option B mapping |
| Emergency Reserve | Absent | $s_{\text{EBR}}(t)$ slacks & constraints | Stage-2 extension |
| Terminal Reserve | Absent | $s_{\text{term}}$ slack & constraint | Stage-2 extension |
| Critical Load Deficit | Absent (tied to total) | $P_{\text{unmet,crit}}(t)$ variable & balance | Layer B extension |
| Option D Policy | Absent | Mode parameter & Option D constraints | Layer D extension |
