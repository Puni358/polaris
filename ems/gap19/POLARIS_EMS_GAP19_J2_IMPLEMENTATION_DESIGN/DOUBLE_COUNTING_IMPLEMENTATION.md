# Pointwise Maximum Reserve Envelope & Double-Counting Elimination Design

## 1. Audit of Current Option-B $J_2$ Formulation

In the existing `gap19_highs_native.py` implementation:

```python
# Current Layer C Constraints in gap19_highs_native.py (lines 240-252)
# 24 EBR Constraints:
E_next[t] + s_EBR[t] >= ebr_target_wh  # for t = 0 .. 23 (indices 288 .. 311)

# 1 Terminal Constraint:
E_next[23] + s_terminal >= terminal_target_wh  # index 312

# Current J2 Objective Vector (lines 280-292)
c2[idx_s_ebr_start + t] = 1.0  # for t = 0 .. 23
c2[idx_s_term] = 1.0           # index 408
```

### Flaw Identification:
In the current implementation, $J_2$ is formulated as:
$$J_2 = \sum_{t=0}^{23} s_{\text{EBR}}[t] + s_{\text{terminal}}$$

At timestep $t = 23$:
- $s_{\text{EBR}}[23]$ penalizes stored energy deficit below $ebr\_target\_wh$.
- $s_{\text{terminal}}$ penalizes stored energy deficit below $terminal\_target\_wh$.
- At $t=23$, BOTH penalties apply to the exact same stored energy state $E[24]$.
- **Result**: Deficits at timestep $t=23$ incur DOUBLE penalties ($2 \cdot w_{J2}$), violating governance mandates against double-counting and distorting lexicographic stage priorities.

---

## 2. Required Change Verdict

```text
CURRENT_J2_FORMULATION = MUST_BE_CHANGED
REASON = DOUBLE_COUNTING_VIOLATION_AT_TIMESTEP_23
REPLACEMENT = POINTWISE_MAXIMUM_RESERVE_ENVELOPE
```

---

## 3. Exact Mathematical Implementation Design

### 3.1 Unified Stage 2 Target Vector ($E_{\text{stage2,target}}[t]$)
Construct a single 24-element target array $E_{\text{stage2,target}}[t]$ for $t \in [0, 23]$:

$$E_{\text{stage2,target}}[t] = \begin{cases} 
E_{\text{EBR,target}}[t] & \text{for } 0 \le t \le 22 \\ 
\max\left( E_{\text{EBR,target}}[23], \, E_{\text{term,target}} \right) & \text{for } t = 23 
\end{cases} \quad \text{[Watt-hours]}$$

### 3.2 Unified Stage 2 Constraint Set ($M_{\text{stage2}} = 24$)
Replace the 25 separate constraints (24 EBR + 1 Terminal) with exactly **24 unified Stage 2 constraints**:

$$E[t+1] + s_{J2}[t] \ge E_{\text{stage2,target}}[t] + E_{\text{min}}, \quad \forall t \in \{0, 1, \dots, 23\}$$

Where:
- $s_{J2}[t]$ is the continuous Stage 2 shortfall variable for timestep $t$ (re-labeled from `s_EBR[t]`, indices `384 .. 407`).
- The separate variable $s_{\text{terminal}}$ (index `408`) and separate constraint 312 are **ELIMINATED**.

### 3.3 Unified Lexicographic Stage 2 Objective ($J_2$)
$$J_2 = \sum_{t=0}^{23} w_{J2}[t] \cdot s_{J2}[t] \quad \text{[Watt-hours]}$$

Where $c_2$ coefficient vector is:
$$c_2[j] = \begin{cases} 1.0 & \text{for } j \in [384, 407] \text{ (i.e. } s_{J2}[t]\text{)} \\ 0.0 & \text{otherwise} \end{cases}$$

---

## 4. Mathematical Proof of Double-Counting Elimination

At timestep $t = 23$:
- The target $E_{\text{stage2,target}}[23] = \max(E_{\text{EBR,target}}[23], E_{\text{term,target}})$ takes the pointwise upper bound of both reserve requirements.
- If $E[24]$ falls short of $E_{\text{stage2,target}}[23]$ by $\Delta E\text{ kWh}$, $s_{J2}[23] = \Delta E$.
- $J_2$ increases by exactly $1.0 \cdot \Delta E$, never $2.0 \cdot \Delta E$.
- Every kWh of stored energy deficit is penalized **EXACTLY ONCE** across all 24 timesteps.
- Double-counting is **100% ELIMINATED**.
