# MILP Variable & Constraint Impact Specification

## 1. Summary of Changes

By unifying EBR and Terminal Reserve into a pointwise maximum reserve envelope ($E_{\text{stage2,target}}[t]$):
- **Separate $s_{\text{terminal}}$ variable (index 408) is REMOVED / UNIFIED into $s_{J2}[23]$**.
- **Separate constraint 312 is REMOVED / UNIFIED into constraint 311**.
- **No new variables or constraints are added**.

---

## 2. Decision Variable Impact ($N = 409 \implies N = 408$)

### 2.1 Variables to Retain (Indices 0 .. 407)
1. **Base Timestep Variables (Indices 0 .. 359)**: 360 variables (96 Binary, 264 Continuous) $\implies$ `RETAIN`.
2. **Layer B Critical Shedding Variables (Indices 360 .. 383)**: 24 continuous variables $P_{\text{unmet\_crit}}[t]$ $\implies$ `RETAIN`.
3. **Layer C Reserve Shortfall Variables (Indices 384 .. 407)**: 24 continuous variables $s_{\text{EBR}}[t]$ re-labeled as $s_{J2}[t]$ $\implies$ `RETAIN`.

### 2.2 Variables to Remove (Index 408)
- Variable 408 ($s_{\text{terminal}}$) $\implies$ `REMOVE / UNIFY`.

### 2.3 Expected Final Variable Count ($N$)
$$\text{Final } N = 408 \quad \text{(96 Binary, 312 Continuous)}$$

---

## 3. Constraint Row Impact ($M = 313 \implies M = 312$)

### 3.1 Constraint Rows to Retain
1. **Base Timestep Constraints (Indices 0 .. 263)**: 264 linear constraints $\implies$ `RETAIN UNCHANGED`.
2. **Layer B Critical Demand Balance Constraints (Indices 264 .. 287)**: 24 linear constraints $\implies$ `RETAIN UNCHANGED`.

### 3.2 Constraint Rows to Modify (Indices 288 .. 311)
- 24 Layer C Stage 2 Reserve Constraints:
  - Current RHS: `ebr_target_wh + min_e_wh`
  - Updated RHS: `E_stage2_target[t] + min_e_wh`
  - Where $E_{\text{stage2,target}}[t] = E_{\text{EBR,target}}[t]$ for $t < 23$, and $E_{\text{stage2,target}}[23] = \max(E_{\text{EBR,target}}[23], E_{\text{term,target}})$.

### 3.3 Constraint Rows to Remove (Index 312)
- Separate terminal constraint 312 (`E_next[23] + s_terminal >= terminal_target_wh`) $\implies$ `REMOVE / UNIFY`.

### 3.4 Expected Final Constraint Count ($M$)
$$\text{Final } M = 312 \quad \text{Linear Constraints (in NORMAL mode)}$$

*(Note: In EMERGENCY mode, 24 additional critical-only discharge constraints are added, making $M = 336$).*

---

## 4. Objective Vector Modifications

### 4.1 Objective $J_1$ Vector ($c_1$)
- Length: 408.
- Nonzero indices: `360 .. 383` ($c_1[\text{idx\_unmet\_crit} + t] = 1.0 \cdot \Delta t$).

### 4.2 Objective $J_2$ Vector ($c_2$)
- Length: 408.
- Nonzero indices: `384 .. 407` ($c_2[\text{idx\_s\_j2} + t] = 1.0$). Index 408 eliminated.

### 4.3 Objective $J_3$ Vector ($c_3$)
- Length: 408.
- Nonzero indices: `base + 7` (diesel power), `base + 13` (diesel running), `base + 14` (diesel startup).

### 4.4 Objective $J_4$ Vector ($c_4$)
- Length: 408.
- Nonzero indices: `base + 2` (solar curt), `base + 3` (wind curt).

---

## 5. Summary Impact Table

| Model Parameter | Current Option-B | Governed J2 Design | Net Delta |
| :--- | :--- | :--- | :--- |
| **Total Variables ($N$)** | 409 | **408** | **-1 Variable** ($s_{\text{terminal}}$ unified) |
| **Binary Variables** | 96 | **96** | 0 |
| **Continuous Variables** | 313 | **312** | **-1 Variable** |
| **Total Constraints ($M$)** | 313 | **312** | **-1 Constraint** (Terminal constraint unified) |
| **Stage 2 Objective Vector ($c_2$)** | 409 elements | **408 elements** | Re-aligned to $s_{J2}[t]$ |
| **Double-Counting Status** | Present (at $t=23$) | **Eliminated** | Zero double-counting |
