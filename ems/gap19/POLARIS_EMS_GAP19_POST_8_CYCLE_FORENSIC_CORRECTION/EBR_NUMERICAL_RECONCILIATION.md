# EBR Numerical Reconciliation Audit (`EBR_NUMERICAL_RECONCILIATION.md`)

**FORENSIC CORRECTION PASS**: POLARIS EMS GAP19 — Post-8-Cycle Forensic Audit Correction  
**FORMULATION SOURCE**: `system/optimization/implementations/gap19_highs_native.py` (Line 130)  
**VERDICT**: `PREVIOUS_EBR_REPORT_CORRECTION_REQUIRED = YES`

---

## 1. Source-Level Formulation Reconciliation

In `system/optimization/implementations/gap19_highs_native.py` (lines 127-131):
```python
for t in range(24):
    end_k = min(t + 6, 24)
    w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, end_k))
    ebr_req_wh = (1.0 / eta_dis) * w_crit_sum_wh
    ebr_target_wh_list.append(ebr_req_wh)
```

### 1.1 Authoritative Equation
$$E_{\text{EBR\_target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{\min(t+5, 23)} P_{\text{critical}}[k] \cdot \Delta t$$

---

## 2. Unit & Numerical Reconciliation

| Audit Dimension | AC-Side Load Energy Requirement | Battery-Side Stored Energy Requirement ($E_{\text{EBR\_target}}$) |
| :--- | :--- | :--- |
| **Physical Definition** | Critical load energy delivered at the AC busbar | Stored DC battery energy required to deliver load through $\eta_{\text{dis}}$ |
| **Formula** | $\sum_{k=t}^{t+5} P_{\text{critical}}[k] \cdot \Delta t$ | $\frac{1}{\eta_{\text{dis}}} \cdot \sum_{k=t}^{t+5} P_{\text{critical}}[k] \cdot \Delta t$ |
| **Numerical Calculation** | $20,000\text{ W} \times 6\text{h} = 120,000.0\text{ Wh}$ | $\frac{120,000.0}{0.92} = 130,434.78\text{ Wh}$ |
| **Solver Constraint Target** | Auxiliary load metric | **Enforced $J_2$ Reserve Target in MILP Constraint 304** |

---

## 3. Explanation of Previous Audit Discrepancy

- **Previous Forensic Audit Error**: Reported the raw AC-side load energy sum ($120,000.0\text{ Wh}$), omitting discharge efficiency conversion.
- **Authoritative Optimizer Behavior**: The HiGHS native solver explicitly enforced the battery-side stored energy reserve constraint $E_{\text{next}}[t] + s_{J2}[t] \ge 130,434.78 + E_{\text{min}}$.

```text
PREVIOUS_EBR_REPORT_CORRECTION_REQUIRED = YES
AC_CRITICAL_LOAD_ENERGY_WH = 120000.0
DC_BATTERY_EBR_RESERVE_TARGET_WH = 130434.78
FINAL_EBR_INTERPRETATION = BATTERY_SIDE_STORED_ENERGY_REQUIREMENT
```
