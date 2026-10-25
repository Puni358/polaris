# POLARIS EMS GAP19 — J2 SLACK BOUND AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `IMPLEMENTATION_FACT`  

---

## 1. Codebase Inspection of $s_{\text{J2}}$ Variable Definition

In `system/optimization/implementations/gap19_highs_native.py`:

```python
# Layer C: s_J2[t]
lb[idx_s_j2_start + t] = 0.0
ub[idx_s_j2_start + t] = capacity_wh # 200,000.0 Wh
```

The variable $s_{\text{J2}}[t]$ is created as a continuous slack variable for each timestep $t \in [0, 23]$ in the 24-hour optimization horizon.

---

## 2. Investigative Analysis

### A. Why $s_{\text{J2}}$ Exists
$s_{\text{J2}}[t]$ was introduced to convert the 6-hour EBR reserve target and 24-hour terminal reserve target into a soft penalty objective $J2 = \sum_{t=0}^{23} s_{\text{J2}}[t]$ within the lexicographic hierarchy ($J1 \succ J2 \succ J3 \succ J4$). If physical battery energy $E_{\text{next}}[t]$ falls below the reserve envelope $E_{\text{stage2\_target}}[t] + E_{\min}$, $s_{\text{J2}}[t]$ absorbs the deficit so that $J2 > 0$ without immediately causing solver infeasibility.

### B. Physical Meaning of the Upper Bound (`capacity_wh`)
* **Lower Bound**: $0.0\text{ Wh}$ (Shortfall cannot be negative).
* **Upper Bound**: `capacity_wh` ($200,000.0\text{ Wh}$).
* **Physical Significance**: Capping $s_{\text{J2}}[t] \le C_{\text{bat}}$ means the optimizer cannot recognize a reserve shortfall greater than $100\%$ of nominal battery capacity ($200\text{ kWh}$).
* However, when 6-hour critical demand exceeds $1.75 \times C_{\text{bat}}$ ($350\text{ kWh}$), the required reserve target itself exceeds $C_{\text{bat}} + E_{\max} - E_{\min}$. Capping $s_{\text{J2}}[t]$ at $200\text{ kWh}$ prevents the slack variable from absorbing shortfalls exceeding $200\text{ kWh}$, causing the MILP solver to crash into strict infeasibility!

### C. Governed vs Implementation Fact
* No governance document or PRD specified that $s_{\text{J2}}$ must be upper-bounded at `capacity_wh`.
* The upper bound `ub = capacity_wh` is an **`IMPLEMENTATION_FACT`** created as an ad-hoc choice during MILP formulation.

### D. Would Increasing the Upper Bound Restore Feasibility?
* **YES**. If `ub[idx_s_j2_start + t] = np.inf` (or a large number like $10^9$), then for any demand profile:
  $$s_{\text{J2}}[t] \ge E_{\text{stage2\_target}}[t] + E_{\min} - E_{\text{next}}[t]$$
  can always be satisfied.
* The solver will remain feasible, finding a valid physical dispatch plan (power balance, generator limits, battery bounds) while penalizing $J2 = \sum s_{\text{J2}}[t]$ at Priority 3.

### E. Would Increasing it Hide a Physical Reserve Violation?
* **NO**. $J2$ is explicitly intended to measure reserve shortfall. Allowing $s_{\text{J2}}$ to grow beyond $200\text{ kWh}$ does not hide reserve violations; it **exposes** the exact magnitude of the shortfall in the $J2$ objective value, while permitting the optimizer to continue dispatching diesel and renewables to serve load ($J1 = 0$).
* Capping $s_{\text{J2}}$ causes complete solver breakdown (`OPTIMIZATION_INFEASIBLE`), which triggers a zero-dispatch fallback plan that intentionally drops 100% of station load!

---

## 3. Audit Classification

`J2_SLACK_BOUND_STATUS = IMPLEMENTATION_FACT`

*(A modeling limitation in `gap19_highs_native.py` that truncates soft-constraint relaxation and causes artificial solver infeasibility during high-demand stress).*
