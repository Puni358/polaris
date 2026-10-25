# D4 GAP19 COMPATIBILITY

## 1. SOLVER-NEUTRAL ALIGNMENT WITH GAP19 LEXICOGRAPHIC OBJECTIVE

The sealed D4 allocation formulation ($P_{i,\text{served}} = \alpha \cdot P_{i,\text{min}}$) was audited for compatibility with the GAP19 4-stage lexicographic objective hierarchy.

---

## 2. COMPATIBILITY ANALYSIS
1. **Stage 1 Alignment (Maximize Critical Reliability)**: Under GAP19, Stage 1 minimizes unmet critical demand ($P_{\text{unmet,crit}}$). The D4 proportional allocation rule ensures that when $P_{\text{unmet,crit}} > 0$, the remaining served critical power is distributed evenly across categories via $\alpha(t)$, preserving maximum proportional reliability across all critical services.
2. **Solver Neutrality**: The D4 proportional allocation linear constraints ($P_{i,\text{serv,crit}} - \alpha P_{i,\text{min}} = 0$) are solver-neutral linear equality constraints.
3. **Architecture Preservation**: Conceptual compatibility holds under BOTH sequential MILP lexicographic solves (Option A) and native HiGHS multi-objective solving (Option B).
