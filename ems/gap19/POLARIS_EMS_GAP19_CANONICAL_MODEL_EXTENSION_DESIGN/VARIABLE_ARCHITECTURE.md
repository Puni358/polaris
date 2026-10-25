# VARIABLE ARCHITECTURE

## CANONICAL TARGET VARIABLE BREAKDOWN (433 TOTAL VARIABLES)

| Layer | Variable Name Scheme | Index Range | Count | Type | Physical Bounds | Semantics / Purpose |
|---|---|---|---|---|---|---|
| **Layer A** | Base 15 variables ($15t+0..14$) | $0..359$ | 360 | 96 Bin, 264 Cont | Physical asset bounds | Physical power, energy, commitment |
| **Layer A** | $w_{\text{stop}}(t)$ ($t=0..23$) | $360..383$ | 24 | Binary | $\{0, 1\}$ | Diesel shutdown status transition |
| **Layer B** | $P_{\text{unmet,crit}}(t)$ ($t=0..23$) | $384..407$ | 24 | Continuous | $[0, P_{\text{demand,crit}}(t)]$ | Protected critical load deficit |
| **Layer C** | $s_{\text{EBR}}(t)$ ($t=0..23$) | $408..431$ | 24 | Continuous | $[0, E_{\text{max}}]$ | Emergency reserve energy slack |
| **Layer C** | $s_{\text{term}}$ | $432$ | 1 | Continuous | $[0, E_{\text{max}}]$ | Terminal energy reserve slack |

- **Total Variables ($N_{\text{target}}$)**: 433
- **Total Binary Variables**: 120 (100% Layer A)
- **Total Continuous Variables**: 313 (264 Layer A + 24 Layer B + 25 Layer C)
