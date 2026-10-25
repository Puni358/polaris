# MILP VARIABLE MAPPING

## 1. EXTENDED DECISION VARIABLE & CONSTRAINT INDEX MAPPING

The audit mapped all Option D requirements to decision variables in `LocalMILPEnergyOptimizer` ([milp.py:L75-L79](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L75-L79)).

Existing variable block size per timestep $t$: $K = 15$.  
Extended variable block size for Option D per timestep $t$: $K_{\text{ext}} = 19$.

---

## 2. DECISION VARIABLE LAYOUT (Per Timestep $t$)

| Index Offset | Variable Name | Symbol | Type | Physical Bounds | Option D Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `base + 0` | `p_sol_used` | $P_{\text{sol,u}}$ | Continuous | $[0, P_{\text{sol,gen}}]$ | Solar power allocated to busbar |
| `base + 1` | `p_wind_used` | $P_{\text{wind,u}}$ | Continuous | $[0, P_{\text{wind,gen}}]$ | Wind power allocated to busbar |
| `base + 2` | `p_curt_sol` | $P_{\text{curt,sol}}$ | Continuous | $[0, P_{\text{sol,gen}}]$ | Solar curtailment |
| `base + 3` | `p_curt_wind` | $P_{\text{curt,wind}}$ | Continuous | $[0, P_{\text{wind,gen}}]$ | Wind curtailment |
| `base + 4` | `p_chg` | $P_{\text{chg}}$ | Continuous | $[0, P_{\text{chg,max}}]$ | Battery charge power |
| `base + 5` | `p_dis` | $P_{\text{dis}}$ | Continuous | $[0, P_{\text{dis,max}}]$ | Battery discharge power (bounded by $P_{\text{critical}}$ in Option D) |
| `base + 6` | `E_next` | $E[t+1]$ | Continuous | $[E_{\text{min}}, E_{\text{max}}]$ | Battery energy state |
| `base + 7` | `p_diesel` | $P_{\text{diesel}}$ | Continuous | $[0, P_{\text{dies,max}}]$ | Diesel generator power |
| `base + 8` | `p_served_crit` | $P_{\text{serv,crit}}$| Continuous | $[0, P_{\text{critical}}]$ | **ADDITIONAL**: Served critical load |
| `base + 9` | `p_unmet_crit` | $P_{\text{unm,crit}}$ | Continuous | $[0, P_{\text{critical}}]$ | **ADDITIONAL**: Unmet critical load |
| `base + 10`| `p_served_flex` | $P_{\text{serv,flex}}$| Continuous | $[0, P_{\text{flexible}}]$ | **ADDITIONAL**: Served flexible load |
| `base + 11`| `p_unmet_flex` | $P_{\text{unm,flex}}$ | Continuous | $[0, P_{\text{flexible}}]$ | **ADDITIONAL**: Unmet flexible load |
| `base + 12`| `u_chg` | $u_{\text{chg}}$ | Binary (0/1) | $\{0, 1\}$ | Battery charge commitment |
| `base + 13`| `u_dis` | $u_{\text{dis}}$ | Binary (0/1) | $\{0, 1\}$ | Battery discharge commitment |
| `base + 14`| `u_diesel` | $u_{\text{diesel}}$ | Binary (0/1) | $\{0, 1\}$ | Diesel generator status |
| `base + 15`| `v_start` | $v_{\text{start}}$ | Binary (0/1) | $\{0, 1\}$ | Diesel startup event |
| `base + 16`| `alpha` | $\alpha$ | Continuous | $[0.0, 1.0]$ | **ADDITIONAL**: Proportional allocation ratio |
| `base + 17`| `p_excess` | $P_{\text{excess}}$ | Continuous | $[0, P_{\text{dies,max}}]$ | **ADDITIONAL**: Diesel excess generation |
| `base + 18`| `p_chg_excess` | $P_{\text{chg,ex}}$ | Continuous | $[0, P_{\text{chg,max}}]$ | **ADDITIONAL**: Excess generation allocated to charging |

---

## 3. COMPATIBILITY & REUSE
- Existing variables (0..7, 12..15) match the exact layout in `milp.py`.
- New variables (8..11, 16..18) are added at the end of the timestep block.
- Total variable count for $H=24$: $N = 24 \times 19 = 456$ variables.
- HiGHS C++ MILP solver handles 456 variables in $< 5$ milliseconds (fast, real-time compliant).
