# GAP19 COMPATIBILITY

## 1. ALIGNMENT WITH SEALED GAP19 GOVERNED OBJECTIVE HIERARCHY

The proposed Option D architecture was audited for compatibility with the sealed GAP19 4-stage lexicographic objective hierarchy.

```text
GAP19 GOVERNED OBJECTIVE HIERARCHY
┌────────────────────────────────────────────────────────┐
│ STAGE 1: Maximize Critical Reliability                 │
│          (Minimize P_unmet_crit)                       │
├────────────────────────────────────────────────────────┤
│ STAGE 2: Preserve Emergency Battery Reserve (EBR)      │
│          (Ensure E(t_N) >= E_target)                   │
├────────────────────────────────────────────────────────┤
│ STAGE 3: Minimize Diesel Fuel Consumption              │
│          (Minimize sum F(P_diesel) * dt)               │
├────────────────────────────────────────────────────────┤
│ STAGE 4: Minimize Renewable Curtailment / Maximize Use │
│          (Minimize sum P_curt * dt)                    │
└────────────────────────────────────────────────────────┘
```

---

## 2. COMPATIBILITY MAPPING ACROSS GAP19 STAGES

| GAP19 Objective Stage | Option D Behavioral Element | Mathematical Formulation in Solver | Solver Independence |
| :--- | :--- | :--- | :--- |
| **Stage 1 (Critical Reliability)** | Protection of $P_{\text{critical}}(t)$ & D4 Proportional Allocation | Unmet critical load penalty OR lexicographic hard priority | **100% Compatible** |
| **Stage 2 (Emergency Battery Reserve)**| Preservation of battery capacity for $T_{\text{required}}$ | Terminal energy constraint $E[t_N] \ge E_{\text{EBR}}$ | **100% Compatible** |
| **Stage 3 (Diesel Fuel)** | Avoid starting diesel solely for battery charging | Fuel minimization objective / diesel startup penalty | **100% Compatible** |
| **Stage 4 (Renewable Utilization)**| Renewable-first support & D6 diesel excess charging | Curtailment minimization objective | **100% Compatible** |

---

## 3. SOLVER-NEUTRAL ARCHITECTURE
- **Current MILP Engine**: Uses scalar HiGHS MILP solver with tiered cost weights ($w_1 = 10.0$ \$/Wh for unmet critical, $w_2 = 0.001$ \$/Wh for curtailment).
- **Future GAP19 Engine**: Uses native HiGHS multi-objective / sequential lexicographic solves.
- **Verdict**: Because Option E separates policy constraint generation (`ModeConstraintSet`) from objective formulation, the Option D policy rules remain **100% SOLVER-NEUTRAL**. They work identically under scalar MILP today and GAP19 native lexicographic solving tomorrow.
