# POLARIS EMS GAP19 — S_J2 BOUND GOVERNANCE AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `IMPLEMENTATION_FACT`  

---

## 1. Codebase Provenance & Implementation Trace

In `system/optimization/implementations/gap19_highs_native.py` (Line 203):

```python
# Layer C: s_J2[t]
lb[idx_s_j2_start + t] = 0.0
ub[idx_s_j2_start + t] = capacity_wh # 200,000.0 Wh
```

---

## 2. Investigative Analysis

| Audit Question | Findings & Evidence | Classification |
| :--- | :--- | :--- |
| **Where does this bound come from?** | Line 203 of `gap19_highs_native.py`. Set equal to nominal battery capacity (`capacity_wh = 200,000.0`). | `IMPLEMENTATION_FACT` |
| **Is it governance?** | **NO**. No PRD, ADR, or governance decision form specified capping $s_{\text{J2}}$ at `capacity_wh`. | `NOT_GOVERNED` |
| **Is it physical?** | **NO**. A virtual reserve shortfall ($s_{\text{J2}}$) is an abstract mathematical penalty variable, not a physical battery parameter. Capping it at $200\text{ kWh}$ prevents it from measuring shortfalls $>200\text{ kWh}$. | `NON_PHYSICAL` |
| **Is it implementation?** | **YES**. It was introduced as a default finite upper bound during MILP formulation. | `IMPLEMENTATION_FACT` |
| **What changes if bound becomes $\infty$?** | The MILP solver remains mathematically feasible for any demand profile. Feasible power dispatch (diesel + renewables + battery) is found, $J1=0$ is maintained, and $J2 = \sum s_{\text{J2}}[t]$ reports the exact shortfall. | `MATHEMATICAL_FEASIBILITY_RESTORED` |
| **Would unbounding preserve $J2$ semantics?** | **YES**. Unbounding $s_{\text{J2}}$ aligns with soft-penalty lexicographic optimization ($J1 \succ J2 \succ J3 \succ J4$). | `SEMANTIC_ALIGNMENT` |
| **Could it conceal a physical deficit?** | **NO**. $J2$ explicitly reports $\sum s_{\text{J2}}[t]$ in `DispatchPlan` metadata. Exposing non-zero $J2$ makes the reserve deficit transparent to operators and downstream safety logic. | `TRANSPARENCY_PRESERVED` |

---

## 3. Mathematical Comparison Table

$$\text{Reserve Constraint: } E_{\text{next}}[t] + s_{\text{J2}}[t] \ge E_{\text{EBR\_target}}[t] + E_{\min}$$

| Parameter State | Max LHS ($E_{\max} + s_{\text{J2\_max}}$) | Feasible 6h Avg Power Limit | Behavior Under High Peak Load ($>53.67\text{ kW}$) |
| :--- | :---: | :---: | :--- |
| **Current (`ub = 200 kWh`)** | $390,000.0\text{ Wh}$ | $53.67\text{ kW}$ | **MILP Solver Infeasibility (`kInfeasible`)** $\rightarrow$ Triggers 100% Load Shedding Fallback (Blackout). |
| **Proposed (`ub = infinity`)** | $\infty$ | $\infty$ | **MILP Solver Optimal (`kOptimal`)** $\rightarrow$ Diesel runs to cover load ($J1=0$), $J2 > 0$ reports exact reserve deficit. |

---

## 4. Audit Verdict & Status

`S_J2_BOUND = IMPLEMENTATION_FACT`

Human governance authorization is required to change `ub[idx_s_j2_start + t] = np.inf` in future gates.
