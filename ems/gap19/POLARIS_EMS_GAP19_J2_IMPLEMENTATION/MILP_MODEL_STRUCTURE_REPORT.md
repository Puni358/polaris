# MILP Model Structure Report

## 1. Matrix Specifications & Verification

The native HiGHS multi-objective MILP model in `gap19_highs_native.py` was constructed and verified against the sealed governed specifications:

```text
MODEL_VARIABLE_COUNT = 408
MODEL_CONSTRAINT_COUNT = 312
```

### 1.1 Decision Variable Breakdown ($N = 408$)
- **Base Variables (`0 .. 359`)**: 360 variables (96 Binary, 264 Continuous) $\implies$ $H=24 \times K=15$ variables per timestep.
- **Layer B Variables (`360 .. 383`)**: 24 continuous variables $P_{\text{unmet\_crit}}[t]$ ($0 \le P_{\text{unmet\_crit}}[t] \le P_{\text{crit\_dem}}[t]$).
- **Layer C Variables (`384 .. 407`)**: 24 continuous variables $s_{J2}[t]$ ($0 \le s_{J2}[t] \le E_{\text{max}}$).
- **Total Variables**: $N = 408$ (96 Binary, 312 Continuous).

### 1.2 Linear Constraint Breakdown ($M = 312$)
- **Base Constraints (`0 .. 263`)**: 264 linear constraints (11 per timestep $\times$ 24 timesteps).
- **Layer B Constraints (`264 .. 287`)**: 24 critical demand balance constraints ($P_{\text{served}}[t] + P_{\text{unmet\_crit}}[t] = P_{\text{crit\_dem}}[t]$).
- **Layer C Constraints (`288 .. 311`)**: 24 Stage 2 unified reserve envelope constraints ($E[t+1] + s_{J2}[t] \ge E_{\text{stage2,target}}[t] + E_{\text{min}}$).
- **Total Constraints**: $M = 312$ linear constraints (in NORMAL mode).

---

## 2. Objective Hierarchy & Priority Ordering

The four objective vectors $c_1, c_2, c_3, c_4$ are registered in HiGHS using `highspy.HighsLinearObjective()`:

| Objective | Priority | Status | Description |
| :--- | :--- | :--- | :--- |
| **$J_1$** | `4` (Highest) | `UNCHANGED` | $\sum P_{\text{unmet\_crit}}[t] \Delta t$ (Critical load shedding Wh) |
| **$J_2$** | `3` | `UPDATED_AS_GOVERNED_ENVELOPE` | $\sum s_{J2}[t]$ (Unified Stage 2 reserve envelope shortfall Wh) |
| **$J_3$** | `2` | `UNCHANGED` | Diesel fuel consumption (Liters) |
| **$J_4$** | `1` (Lowest) | `UNCHANGED` | Avoidable renewable curtailment (Wh) |

- **Lexicographic Solver Option**: `blend_multi_objectives = False` (strictly enforced).

---

## 3. Structural Model Verification Verdict

```text
MODEL_VARIABLE_COUNT = 408
MODEL_CONSTRAINT_COUNT = 312
J1 = UNCHANGED
J2 = UPDATED_AS_GOVERNED_ENVELOPE
J3 = UNCHANGED
J4 = UNCHANGED
OBJECTIVE_PRIORITY = J1 > J2 > J3 > J4
MILP_MODEL_STRUCTURE_STATUS = PASS
```
