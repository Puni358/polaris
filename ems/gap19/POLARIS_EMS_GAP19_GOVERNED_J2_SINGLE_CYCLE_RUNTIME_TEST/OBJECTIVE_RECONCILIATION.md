# Objective Hierarchy & Values Reconciliation Report

## 1. Objective Values Summary

The single-cycle solve of `GAP19HighsNativeOptimizer` produced the following objective vector across the 4 lexicographic stages:

| Stage | Objective Name | Physical Meaning | Priority | Value | Units | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **$J_1$** | Protected Critical Deficit | Unmet protected critical load energy | **4** | **$0.0000$** | Wh | **ZERO DEFICIT** |
| **$J_2$** | Governed Reserve Shortfall | Pointwise reserve envelope shortfall | **3** | **$0.0000$** | Wh | **ZERO SHORTFALL** |
| **$J_3$** | Diesel Fuel Consumption | Total generator fuel consumed | **2** | **$116.5076$** | Liters | **MINIMIZED** |
| **$J_4$** | Renewable Curtailment | Curtailed solar & wind energy | **1** | **$0.0000$** | Wh | **ZERO CURTAILMENT** |

---

## 2. Priority Hierarchy & Lexicographic Verification

1. `h.setOptionValue("blend_multi_objectives", False)` was explicitly set in HiGHS solver options.
2. HiGHS solved 4 sequential sub-problems in order of priority:
   - Priority 4 ($J_1$): Minimized critical deficit to $0.0\text{ Wh}$.
   - Priority 3 ($J_2$): Minimized reserve shortfall to $0.0\text{ Wh}$ while holding $J_1 \le 0.0\text{ Wh}$.
   - Priority 2 ($J_3$): Minimized diesel fuel consumption to $116.5076\text{ L}$ while holding $J_1 \le 0.0$ and $J_2 \le 0.0$.
   - Priority 1 ($J_4$): Minimized renewable curtailment to $0.0\text{ Wh}$ while holding $J_1, J_2, J_3$ at their optimal bounds.

---

## 3. Verdict

```
LEXICOGRAPHIC_PRIORITY_ORDER = J1 > J2 > J3 > J4 (4, 3, 2, 1)
BLEND_MULTI_OBJECTIVES = FALSE
OBJECTIVE_RECONCILIATION_STATUS = PASS
```
