# RENEWABLE FIRST ARCHITECTURE

## 1. MATHEMATICAL FORMULATION OF RENEWABLE-FIRST BEHAVIOR

Governance DEC-004 requires:
> "Renewable generation is used first for protected critical service."

---

## 2. MATHEMATICAL COMPARISON OF CANDIDATE INTERPRETATIONS

| Formulation | Mathematical Representation | Compliance with DEC-004 | Architectural Alignment |
| :--- | :--- | :--- | :--- |
| **Interpretation A** | Explicit variable allocation: $P_{\text{ren,crit}} = \min(P_{\text{ren}}, P_{\text{critical}})$ | **COMPLIANT** | Direct linear constraint in MILP |
| **Interpretation B** | High penalty cost on diesel generation when renewables available | Partial | Objective-dependent (violates solver neutrality) |
| **Interpretation C** | Renewable mandatory dispatch before battery discharge | Partial | Distorts battery energy storage economics |

---

## 3. EXACT CONSTRAINTS FOR INTERPRETATION A (RECOMMENDED)

In the extended MILP formulation, renewable power available at timestep $t$ ($P_{\text{ren}}[t] = P_{\text{solar}}[t] + P_{\text{wind}}[t]$) is explicitly allocated via linear constraints:

$$\begin{aligned}
P_{\text{ren,crit}}[t] &\le P_{\text{ren}}[t] \\
P_{\text{ren,crit}}[t] &\le P_{\text{critical}}[t] \\
P_{\text{served,crit}}[t] &= P_{\text{ren,crit}}[t] + P_{\text{dies,crit}}[t] + P_{\text{batt,crit}}[t]
\end{aligned}$$

This formulation guarantees that available renewable power directly satisfies protected critical demand before any diesel generation is dispatched or battery energy is discharged for critical load.
