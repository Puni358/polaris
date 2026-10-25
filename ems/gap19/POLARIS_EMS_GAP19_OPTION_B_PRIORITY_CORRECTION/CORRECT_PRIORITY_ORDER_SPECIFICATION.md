# Correct Priority Order Specification

## Semantic Hierarchy Requirement

POLARIS EMS governance strictly mandates the following lexicographic priority order:

$$\text{Stage 1 } (J_1: \text{Critical Deficit}) \succ \text{Stage 2 } (J_2: \text{EBR Shortfall}) \succ \text{Stage 3 } (J_3: \text{Diesel Fuel}) \succ \text{Stage 4 } (J_4: \text{Curtailment})$$

## HiGHS Representation Requirement

Under the verified HiGHS convention (`HIGHER_NUMBER_IS_HIGHER_PRIORITY`), the native HiGHS integer priorities assigned to objectives $J_1, J_2, J_3, J_4$ must strictly satisfy:

$$\text{priority}(J_1) > \text{priority}(J_2) > \text{priority}(J_3) > \text{priority}(J_4)$$

## Formal Mapping Table

| POLARIS Objective | Symbol | Physical Unit | Required Relative Priority | Valid Integer Assignment (Example A) | Valid Integer Assignment (Example B) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Critical Deficit** | $J_1$ | Watt-hours (Wh) | Highest | `4` | `100` |
| **Reserve Shortfall** | $J_2$ | Watt-hours (Wh) | 2nd Highest | `3` | `80` |
| **Diesel Fuel** | $J_3$ | Liters (L) | 3rd Highest | `2` | `60` |
| **Curtailment** | $J_4$ | Watt-hours (Wh) | Lowest | `1` | `40` |
