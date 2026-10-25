# POLARIS EMS — OBJECTIVE HIERARCHY SPECIFICATION

**Document Version**: 2.3.0 (Final Bounded Governed Draft)  
**Governance Reference**: Decision D15 (Option A — Strict Lexicographic Priority Structure)  
**Status**: `OBJECTIVE_HIERARCHY = FULLY_SPECIFIED`  

---

## 1. LEXICOGRAPHIC OPTIMIZATION PRINCIPLE

The POLARIS Energy Management System (EMS) utilizes a **Strict Lexicographic Optimization Hierarchy** to resolve trade-offs between competing operational objectives. 

Under Decision D15 (Option A), objectives are ordered in a strict sequence:
$$	ext{Stage 1: Critical Reliability} \succ 	ext{Stage 2: Emergency Resilience} \succ 	ext{Stage 3: Fuel Conservation} \succ 	ext{Stage 4: Renewable Utilization}$$

### Rejection of Scalar Weighting
The existing prototype implementation (`milp.py`) combines unmet load penalties ($c_{	ext{unmet}} = \$10,000/	ext{kWh}$) and fuel cost proxies ($c_{	ext{marg}} = \$0.625/	ext{kWh}$) into a single composite scalar objective function. This formulation is explicitly **REJECTED** as a policy model because:
1. Scalar weights permit implicit economic trade-offs (e.g., sacrificing critical load to save diesel fuel if penalty ratios align).
2. Arbitrary scalar coefficients lack stakeholder policy authorization.
3. Lexicographic optimization guarantees absolute mathematical dominance of higher-priority SLAs over lower-priority objectives.

---

## 2. FORMAL MULTI-STAGE MATHEMATICAL PROBLEM DEFINITION

Let $\Omega_0 \subset \mathbb{R}^n 	imes \{0,1\}^m$ be the feasible set defined by all physical, hardware, and safety hard constraints (Stage 0: energy balance, battery power/SOC cell protection limits, diesel generator min/max power, charging exclusivity, physical fuel inventory $F_{	ext{rem}} \ge 0$).

### Stage 0 — Physical Hard & Safety Constraints
$$\Omega_0 = \left\{ x \in \mathbb{R}^n 	imes \{0,1\}^m \ \middle|\ 	ext{Busbar Balance, Battery Cell Floor } (	ext{SOC} \ge 20\%), 	ext{Generator Bounds, Exclusivity, } F_{	ext{rem}} \ge 0 ight\}$$

---

### Stage 1 — Critical Reliability Optimization
**Objective**: Eliminate unmet Critical Load.
$$Z_1^* = \min_{x \in \Omega_0} J_1(x) = \sum_{t=1}^{H} \sum_{i \in L_C} P_{	ext{unmet, } i}(t) \cdot \Delta t$$

**Policy SLA Requirement**:
In Normal Governed Operation, $Z_1^* = 0	ext{ Wh}$.

**Inherited Constraint Set for Stage 2**:
$$\Omega_1 = \left\{ x \in \Omega_0 \ \middle|\ J_1(x) \le Z_1^* + \epsilon_1 ight\}$$

---

### Stage 2 — Emergency Battery Resilience (Target-Shortfall Minimization)
**Objective**: Minimize target shortfall relative to the dynamic Emergency Battery Reserve (EBR) target and horizon terminal SOC requirement, while subject to hard baseline EBR floor constraints.

$$Z_2^* = \min_{x \in \Omega_1} J_2(x) = \sum_{t=1}^{H} \max\left(0, 	ext{SOC}_{	ext{EBR\_target}}(t) - 	ext{SOC}(t)ight) + \max\left(0, 	ext{SOC}_{	ext{terminal\_target}}(H) - 	ext{SOC}(H)ight)$$

*(where $	ext{SOC}(t) \ge 	ext{SOC}_{	ext{EBR\_floor}}$ is enforced as a hard constraint in Stage 0/1; "reserve-headroom maximization" is descriptive).*  
Set $\Omega_2 = \left\{ x \in \Omega_1 \mid J_2(x) \le Z_2^* + \epsilon_2 ight\}$.

---

### Stage 3 — Fuel Conservation Optimization
**Objective**: Minimize actual physical diesel fuel volume consumed in liters ($L$).

$$Z_3^* = \min_{x \in \Omega_2} J_3(x) = \sum_{t=1}^{H} 	ext{Fuel}_{	ext{liter}}(t)$$

where:
$$	ext{Fuel}_{	ext{liter}}(t) = \left[ a \cdot P_{	ext{diesel}}(t)^2 + b \cdot P_{	ext{diesel}}(t) + c \cdot u_{	ext{diesel}}(t) ight] \Delta t + 	ext{Fuel}_{	ext{start}} \cdot v_{	ext{start}}(t)$$

**Inherited Constraint Set for Stage 4**:
$$\Omega_3 = \left\{ x \in \Omega_2 \ \middle|\ J_3(x) \le Z_3^* + \epsilon_3 ight\}$$

---

### Stage 4 — Renewable Utilization & Avoidable Curtailment Minimization
**Objective**: Minimize avoidable renewable curtailment among solutions that satisfy Stages 1–3.

$$Z_4^* = \min_{x \in \Omega_3} J_4(x) = \sum_{t=1}^{H} P_{	ext{curt, avoidable}}(t) \cdot \Delta t$$

---

## 3. SUMMARY OF STAGE COUPLING & FEASIBLE SET CONTRACTION

$$\Omega_0 \supseteq \Omega_1 \supseteq \Omega_2 \supseteq \Omega_3 \supseteq \Omega_4^*$$

1. $\Omega_0 	o \Omega_1$: Constrains dispatch to solutions guaranteeing 100% Critical Load service.
2. $\Omega_1 	o \Omega_2$: Restricts dispatch to solutions minimizing EBR target shortfall above baseline reserve floor.
3. $\Omega_2 	o \Omega_3$: Restricts dispatch to solutions minimizing diesel fuel liters without violating Stage 1 or 2.
4. $\Omega_3 	o \Omega_4^*$: Selects the final dispatch plan maximizing renewable utilization.
