# POLARIS EMS — FORENSIC MILP OBJECTIVE COMPATIBILITY AUDIT (OBJ-001 TO OBJ-011)

## 1. Executive Summary

This document presents the forensic claim audit evaluating **Claim 3: MILP / Objective Compatibility** (`OPTION_D_MILP_COMPATIBILITY`). It forensically separates `CURRENT_IMPLEMENTATION_FACTS` from `GOVERNED_TARGET_ARCHITECTURE`.

### Forensic Verdict: `OBJECTIVE_CLASSIFICATION_CORRECTION_REQUIRED = YES`

---

## 2. 11 Subclaims Forensic Audit Matrix

| Claim ID | Subclaim Statement | Forensic Evidence Classification | Executable Code Evidence / Finding |
|----------|-------------------|----------------------------------|------------------------------------|
| **OBJ-001** | `milp.py` uses $10/\text{Wh}$ scalar unmet load penalty | `CURRENT_IMPLEMENTATION_FACT` | `unmet_penalty_per_wh = 10.0` in `milp.py` line 49. |
| **OBJ-002** | `milp.py` uses a single-pass scalar objective | `CURRENT_IMPLEMENTATION_FACT` | `scipy.optimize.milp` called once per step with linear cost vector $c^T x$. |
| **OBJ-003** | Governed target architecture is 4-stage lexicographic | `GOVERNED_TARGET_ARCHITECTURE` | Established in objective governance; NOT implemented as multi-pass in `milp.py`. |
| **OBJ-004** | Multi-pass sequential solver or HiGHS multi-obj path implemented | `NOT_ESTABLISHED_IN_CODE` | `milp.py` contains zero multi-pass or lexicographic locking code. |
| **OBJ-005** | $10/\text{Wh}$ scalar penalty guarantees Stage 1 reliability | `CONTRADICTED_BY_MATH` | Scalar weight combinations can trade off if fuel/startup penalties exceed unmet cost. |
| **OBJ-006** | Option D noncritical load suppression directly representable | `DIRECTLY_REPRESENTABLE` | MILP bounds $P_{\text{flex,max}} = 0$ enforce zero noncritical load. |
| **OBJ-007** | Option D dynamic $P_{\text{critical}}(t)$ representable | `REPRESENTABLE_WITH_ADDITIVE_CHANGES` | Additive `critical_demand_w` trajectory vector in `ForecastBundle`. |
| **OBJ-008** | Proportional critical shortfall allocation representable | `REPRESENTABLE_WITH_ADDITIVE_CHANGES` | Additive linear constraints $r_c = \frac{P_{\text{min},c}}{\sum P_{\text{min}}}$. |
| **OBJ-009** | Battery discharge restricted to critical load representable | `DIRECTLY_REPRESENTABLE` | Linear constraint $P_{\text{dis},j} \le P_{\text{critical},j}$. |
| **OBJ-010** | Unavoidable diesel excess battery charging representable | `DIRECTLY_REPRESENTABLE` | Energy balance constraint $P_{\text{chg},j} = P_{\text{excess},j}$ up to $P_{\text{chg,max}}$. |
| **OBJ-011** | Previous audit blurred scalar penalty with lexicographic guarantee | `CORRECTION_REQUIRED` | Calling $10/\text{Wh}$ scalar weight a "lexicographic guarantee" was an overstatement. |

---

## 3. Mandatory Separation of Implementation Facts vs. Governed Target

```text
┌─────────────────────────────────────────┐     ┌─────────────────────────────────────────┐
│     CURRENT IMPLEMENTATION FACT         │     │      GOVERNED TARGET ARCHITECTURE       │
│                                         │     │                                         │
│ • Single-pass scipy.optimize.milp solver│     │ • 4-Stage Lexicographic Hierarchy       │
│ • Scalar linear penalty c_unmet = $10/Wh│     │   - Stage 1: Critical Reliability       │
│ • Weighted sum: fuel + unmet + deg      │     │   - Stage 2: Emergency Battery Reserve  │
│ • Prototype implementation in milp.py   │     │   - Stage 3: Fuel Minimization          │
│                                         │     │   - Stage 4: Renewable Utilization      │
└─────────────────────────────────────────┘     └─────────────────────────────────────────┘
```

- **Forensic Correction Verdict**: Option D formulation mechanics are mathematically compatible with linear programming constraints, but `c_unmet = 10.0` in `milp.py` is a prototype scalar weight, **NOT** an implemented lexicographic guarantee.

Status: `OBJECTIVE_AUDIT_SEALED`
