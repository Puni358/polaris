# HiGHSpy Option-B Native Objective Mapping Specification

## 1. HiGHSpy Multi-Objective Native Architecture

Option B utilizes the native C++ multi-objective optimization engine of HiGHS exposed via the Python `highspy` API (`highspy.Highs()`).

In `highspy`, multiple objectives are registered using `HighsLinearObjective` objects, with priorities specified via the `.priority` attribute:
- Higher integer priority values indicate higher lexicographic importance.
- `blend_multi_objectives = False` forces strict lexicographic multi-pass solves within HiGHS C++ core.

---

## 2. Governed Mapping of Objectives

| Stage | Objective Description | Physical Unit | HiGHS Objective Object | `priority` Attribute | Objective Vector Length | Nonzero Variable Indices |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 ($J_1$)** | Protected Critical Load Deficit | Watt-hours (Wh) | `obj1 = HighsLinearObjective()` | `4` (Highest) | 408 | `360 .. 383` ($P_{\text{unmet\_crit}}[t]$) |
| **Stage 2 ($J_2$)** | Unified Reserve Shortfall Envelope | Watt-hours (Wh) | `obj2 = HighsLinearObjective()` | `3` | 408 | `384 .. 407` ($s_{J2}[t]$) |
| **Stage 3 ($J_3$)** | Diesel Fuel Consumption | Liters (L) | `obj3 = HighsLinearObjective()` | `2` | 408 | `base+7`, `base+13`, `base+14` |
| **Stage 4 ($J_4$)** | Renewable Curtailment | Watt-hours (Wh) | `obj4 = HighsLinearObjective()` | `1` (Lowest) | 408 | `base+2`, `base+3` |

---

## 3. Answers to Specific Mapping Questions

### Question 1: Is one additional objective vector required?
- **Answer**: `NO.`
- The four-stage lexicographic hierarchy ($J_1, J_2, J_3, J_4$) is preserved. $J_2$ encompasses BOTH EBR and Terminal Reserve via the pointwise maximum envelope ($E_{\text{stage2,target}}[t]$). No fifth objective vector is needed.

### Question 2: Are auxiliary variables required?
- **Answer**: `NO.`
- The 24 continuous shortfall variables $s_{J2}[t]$ (indices `384 .. 407`) are fully sufficient. Variable 408 ($s_{\text{terminal}}$) is eliminated.

### Question 3: Are additional constraints required?
- **Answer**: `NO.`
- The 24 Stage 2 reserve constraints (`E_next[t] + s_J2[t] >= E_stage2_target[t]`) replace the previous 25 constraints (24 EBR + 1 Terminal). Total constraints decrease from $M=313$ to $M=312$.

### Question 4: Does the objective priority order change?
- **Answer**: `NO.`
- The priority order remains strictly $J_1$ (Priority 4) $\succ J_2$ (Priority 3) $\succ J_3$ (Priority 2) $\succ J_4$ (Priority 1).

---

## 4. `highspy` Code Integration Template (Design Only)

```python
# Objective 1: J1 (Critical Deficit Wh) - Priority 4
obj1 = highspy.HighsLinearObjective()
obj1.priority = 4; obj1.weight = 1.0; obj1.offset = 0.0
obj1.coefficients = c1.tolist() # Length 408

# Objective 2: J2 (Unified Stage 2 Pointwise Envelope Shortfall Wh) - Priority 3
obj2 = highspy.HighsLinearObjective()
obj2.priority = 3; obj2.weight = 1.0; obj2.offset = 0.0
obj2.coefficients = c2.tolist() # Length 408 (c2[384..407] = 1.0)

# Objective 3: J3 (Diesel Fuel Liters) - Priority 2
obj3 = highspy.HighsLinearObjective()
obj3.priority = 2; obj3.weight = 1.0; obj3.offset = 0.0
obj3.coefficients = c3.tolist() # Length 408

# Objective 4: J4 (Renewable Curtailment Wh) - Priority 1
obj4 = highspy.HighsLinearObjective()
obj4.priority = 1; obj4.weight = 1.0; obj4.offset = 0.0
obj4.coefficients = c4.tolist() # Length 408

h.addLinearObjective(obj1)
h.addLinearObjective(obj2)
h.addLinearObjective(obj3)
h.addLinearObjective(obj4)
```

---

## 5. Summary Mapping Verdict

```text
HIGHSPY_OBJECTIVE_MAPPING = NATIVE_LEXICOGRAPHIC_J1_J2_J3_J4_PRESERVED
ADDITIONAL_OBJECTIVE_VECTORS = NONE (EXACTLY 4 OBJECTIVES)
AUXILIARY_VARIABLES = NONE (N = 408)
ADDITIONAL_CONSTRAINTS = NONE (M = 312)
PRIORITY_ORDER_STABILITY = VERIFIED (4 > 3 > 2 > 1)
```
