# MILP CONSTRAINT AUTHORIZATION SCOPE

## 21-Variable Linear Constraint Formulation

This document defines the exact mathematical formulation for extending `system/optimization/implementations/milp.py` from 13 variables to 21 variables per timestep $t \in \{1, \dots, H\}$.

---

## 21 Decision Variables per Timestep $t$

1. $P_{\text{solar,crit}}(t)$: Solar power allocated to protected critical load ($\ge 0$).
2. $P_{\text{solar,flex}}(t)$: Solar power allocated to flexible load ($\ge 0$).
3. $P_{\text{solar,bat}}(t)$: Solar power allocated to battery charging ($\ge 0$).
4. $P_{\text{solar,curt}}(t)$: Solar power curtailed ($\ge 0$).
5. $P_{\text{wind,crit}}(t)$: Wind power allocated to protected critical load ($\ge 0$).
6. $P_{\text{wind,flex}}(t)$: Wind power allocated to flexible load ($\ge 0$).
7. $P_{\text{wind,bat}}(t)$: Wind power allocated to battery charging ($\ge 0$).
8. $P_{\text{wind,curt}}(t)$: Wind power curtailed ($\ge 0$).
9. $P_{\text{diesel,crit}}(t)$: Diesel power allocated to protected critical load ($\ge 0$).
10. $P_{\text{diesel,flex}}(t)$: Diesel power allocated to flexible load ($\ge 0$).
11. $P_{\text{diesel,bat}}(t)$: Diesel power allocated to battery charging ($\ge 0$).
12. $P_{\text{diesel,curt}}(t)$: Diesel power curtailed ($\ge 0$).
13. $P_{\text{bat,dis,crit}}(t)$: Battery discharge power allocated to protected critical load ($\ge 0$).
14. $P_{\text{bat,dis,flex}}(t)$: Battery discharge power allocated to flexible load ($\ge 0$).
15. $P_{\text{bat,ch}}(t)$: Total battery charging power ($\ge 0$).
16. $P_{\text{crit,served}}(t)$: Protected critical load power served ($\ge 0$).
17. $P_{\text{flex,served}}(t)$: Flexible load power served ($\ge 0$).
18. $u_{\text{gen}}(t)$: Binary generator status ($\in \{0, 1\}$).
19. $u_{\text{start}}(t)$: Binary generator start indicator ($\in \{0, 1\}$).
20. $\text{SOC}(t)$: Battery state of charge ($\text{SOC}_{\text{min}} \le \text{SOC}(t) \le \text{SOC}_{\text{max}}$).
21. $\alpha(t)$: D4 critical load proportionality factor ($0 \le \alpha(t) \le 1$).

---

## Governing Linear Constraints

### 1. Resource Availability Split Balance
$$P_{\text{solar,crit}}(t) + P_{\text{solar,flex}}(t) + P_{\text{solar,bat}}(t) + P_{\text{solar,curt}}(t) = P_{\text{solar,avail}}(t)$$
$$P_{\text{wind,crit}}(t) + P_{\text{wind,flex}}(t) + P_{\text{wind,bat}}(t) + P_{\text{wind,curt}}(t) = P_{\text{wind,avail}}(t)$$

### 2. Generator Output Split & Minimum Operating Bounds
$$P_{\text{diesel,crit}}(t) + P_{\text{diesel,flex}}(t) + P_{\text{diesel,bat}}(t) + P_{\text{diesel,curt}}(t) = P_{\text{diesel,gen}}(t)$$
$$P_{\text{diesel,min}} \cdot u_{\text{gen}}(t) \le P_{\text{diesel,gen}}(t) \le P_{\text{diesel,max}} \cdot u_{\text{gen}}(t)$$

### 3. Protected Critical Power Balance Equation
$$P_{\text{crit,served}}(t) = P_{\text{solar,crit}}(t) + P_{\text{wind,crit}}(t) + P_{\text{diesel,crit}}(t) + P_{\text{bat,dis,crit}}(t)$$

### 4. Flexible Power Balance Equation
$$P_{\text{flex,served}}(t) = P_{\text{solar,flex}}(t) + P_{\text{wind,flex}}(t) + P_{\text{diesel,flex}}(t) + P_{\text{bat,dis,flex}}(t)$$

### 5. D4 Proportional Critical Load Allocation
$$P_{\text{crit,served}}(t) = \alpha(t) \cdot P_{\text{crit,min}}(t) \quad \text{where } 0 \le \alpha(t) \le 1$$
$$P_{i,\text{served}}(t) = \alpha(t) \cdot P_{i,\text{min}}(t) \quad \forall \text{ critical categories } i$$

### 6. D2 Battery Critical-Only Discharge Constraint
In `OPTION_D` mode, enforce strict zero flexible battery discharge via physical bus separation:
$$P_{\text{bat,dis,flex}}(t) = 0 \quad \forall t$$

### 7. D6 Excess Diesel Generation Routing Constraints
When diesel generation is active ($u_{\text{gen}}(t) = 1$):
- Prevent diesel allocation to flexible load in Option D: $P_{\text{diesel,flex}}(t) = 0$.
- Route diesel excess ($P_{\text{diesel,gen}}(t) - P_{\text{diesel,crit}}(t)$) to battery charging ($P_{\text{diesel,bat}}(t)$) up to battery charge capacity.
- Prevent diesel start solely for battery charging:
  $$P_{\text{diesel,bat}}(t) \le M \cdot \text{IsCriticalDeficient}(t)$$
  $$\text{where } \text{IsCriticalDeficient}(t) = 1 \iff (P_{\text{solar,crit}}(t) + P_{\text{wind,crit}}(t) < P_{\text{crit,min}}(t))$$

### 8. Flexible Load Shedding in Option D
$$P_{\text{flex,served}}(t) = 0 \quad \forall t \text{ in OPTION_D}$$
