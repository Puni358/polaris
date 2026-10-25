# Double-Counting & Reserve Overlap Proof / Audit

## 1. Governance Problem Statement

Human governance has mandated:
> "EBR and Terminal Reserve have distinct purposes. They must NOT be blindly additive. The formulation must prevent double-counting."

Double-counting occurs when a single physical kWh deficiency in battery stored energy at a specific timestep (most notably the terminal timestep $t = H-1 = 23$) incurs multiple independent mathematical penalties in the Stage 2 objective $J_2$, or when reserve targets are summed blindly ($E_{\text{target}} = E_{\text{EBR}} + E_{\text{term}}$) forcing an artificially inflated battery capacity requirement.

---

## 2. Four Boundary Case Analysis

Let $E_{\text{EBR,target}}[23]$ be the 6-hour EBR stored energy target evaluated at timestep $t = 23$ (covering critical load for interval $[23, 28]$).
Let $E_{\text{term,target}}$ be the Terminal Reserve target evaluated at $t = 23$ (for next-horizon viability).
Let $E_{\text{usable}}[23] = E_{\text{bat}}[24] - E_{\text{min}}$ be the actual usable stored energy remaining at the horizon boundary.

### Case 1: EBR Target > Terminal Target ($E_{\text{EBR,target}}[23] > E_{\text{term,target}}$)
- **Physical Situation**: The 6-hour critical load requirement starting at $t=23$ exceeds the general terminal viability buffer requirement.
- **Blindly Additive Flaw**: Setting $E_{\text{target}}[23] = E_{\text{EBR,target}}[23] + E_{\text{term,target}}$ forces the battery to hold energy to cover BOTH targets simultaneously, effectively double-counting the required kWh buffer.
- **Summed Shortfall Flaw**: If $s_{\text{EBR}}[23] = \max(0, E_{\text{EBR,target}}[23] - E_{\text{usable}}[23])$ and $s_{\text{term}} = \max(0, E_{\text{term,target}} - E_{\text{usable}}[23])$, then if $E_{\text{usable}}[23] = 0$, the total penalty is $E_{\text{EBR,target}}[23] + E_{\text{term,target}}$, over-penalizing the zero-energy state by counting the same missing energy twice.
- **Governed Correct Resolution**: The physical requirement at $t=23$ is governed by the larger of the two demands: $E_{\text{stage2,target}}[23] = E_{\text{EBR,target}}[23]$.

### Case 2: Terminal Target > EBR Target ($E_{\text{term,target}} > E_{\text{EBR,target}}[23]$)
- **Physical Situation**: Terminal viability (e.g. initial state restoration $E_{\text{bat}}[0]$ or extended morning peak reserve) requires more stored energy than the immediate 6-hour critical load.
- **Blindly Additive Flaw**: Forcing $E_{\text{target}}[23] = E_{\text{EBR,target}}[23] + E_{\text{term,target}}$ locks excessive battery capacity, potentially triggering unnecessary diesel generation during hours $20..23$.
- **Governed Correct Resolution**: The physical requirement at $t=23$ is governed by Terminal Reserve: $E_{\text{stage2,target}}[23] = E_{\text{term,target}}$.

### Case 3: EBR Target = Terminal Target ($E_{\text{EBR,target}}[23] = E_{\text{term,target}} = E^*$)
- **Physical Situation**: Both reserve concepts demand the exact same stored energy level $E^*$ at the horizon boundary.
- **Summed Shortfall Flaw**: If shortfalls are summed ($J_2 = \sum s_{\text{EBR}}[t] + s_{\text{term}}$), the penalty coefficient for timestep $t=23$ is effectively DOUBLED ($2 \cdot w_{J2}$) relative to timesteps $t < 23$. This distorts the lexicographic stage priority, causing the optimizer to unnaturally prioritize $t=23$ reserve over earlier timesteps.
- **Governed Correct Resolution**: The unified target is $E_{\text{stage2,target}}[23] = E^*$, penalized with standard single weight $w_{J2}$.

### Case 4: Infeasible Reserve Requirement ($E_{\text{target}} > E_{\text{max}} - E_{\text{min}}$)
- **Physical Situation**: Either individual target or a blindly additive target exceeds total usable battery capacity $E_{\text{usable,max}} = E_{\text{max}} - E_{\text{min}}$.
- **Consequence**: If enforced as a hard constraint, the MILP solver returns `status = 2` (INFEASIBLE), triggering governed emergency fallback routines. If blindly additive targets are used, infeasibility occurs even when the battery has sufficient capacity to satisfy both purposes individually.
- **Governed Correct Resolution**: Envelope unification bounds the target by $E_{\text{usable,max}}$ and retains $J_2$ as a soft slack variable penalty, guaranteeing primal MILP feasibility.

---

## 3. Mathematical Proof of Zero Double-Counting via Pointwise Maximum Envelope

To satisfy governance mandates and prevent double-counting across all 4 boundary cases, the Stage 2 reserve target MUST be formulated as a **Pointwise Maximum Envelope** across timesteps.

### 3.1 Pointwise Target Vector Definition
For every timestep $t \in \{0, 1, \dots, H-1\}$:
$$E_{\text{stage2,target}}[t] = \begin{cases} 
E_{\text{EBR,target}}[t] & \text{for } 0 \le t < H-1 \\ 
\max\left(E_{\text{EBR,target}}[H-1], E_{\text{term,target}}\right) & \text{for } t = H-1 
\end{cases}$$

### 3.2 Unified Stage 2 Shortfall Decision Variable
Define a single Stage 2 shortfall vector $s_{J2}[t] \ge 0$ for $t \in \{0, \dots, H-1\}$:
$$\begin{aligned}
s_{J2}[t] &\ge E_{\text{stage2,target}}[t] - \left(E_{\text{bat}}[t+1] - E_{\text{min}}\right), \quad \forall t \in \{0, \dots, H-1\} \\
s_{J2}[t] &\ge 0, \quad \forall t \in \{0, \dots, H-1\}
\end{aligned}$$

### 3.3 Stage 2 Objective Function ($J_2$) Options

#### Option 1: Timestep-Weighted Sum of Shortfalls (Recommended for MILP)
$$J_2 = \sum_{t=0}^{H-1} w_{J2}[t] \cdot s_{J2}[t] \quad \text{[Watt-hours]}$$
- **Double-Counting Audit**: Proof of ZERO double-counting. At timestep $t=H-1$, $s_{J2}[H-1]$ measures the exact non-negative deficit below the upper envelope $\max(E_{\text{EBR}}, E_{\text{term}})$. A $1\text{ kWh}$ deficit increases $J_2$ by exactly $w_{J2}[H-1] \cdot 1.0$, never $2.0$.

#### Option 2: Maximum Shortfall Across Horizon (Minimax Lexicographic)
$$J_2 = \max_{t \in \{0, \dots, H-1\}} s_{J2}[t] \quad \implies \quad J_2 = z, \quad \text{s.t. } z \ge s_{J2}[t], \, \forall t$$
- **Double-Counting Audit**: Proof of ZERO double-counting. Penalizes only the worst-case reserve deficit across the horizon.

---

## 4. Audit Verdict on $J_2$ Representation

- **Sum of Separate Shortfalls ($s_{\text{EBR}} + s_{\text{term}}$)**: `REJECTED` (Violates governance by double-counting terminal timestep shortfall).
- **Blindly Additive Targets ($E_{\text{EBR}} + E_{\text{term}}$)**: `REJECTED` (Violates governance by inflating physical capacity requirements).
- **Pointwise Maximum Envelope ($E_{\text{stage2,target}}[t]$)**: `APPROVED` (Mathematically guarantees zero double-counting, preserves non-additive governance semantics, and guarantees MILP feasibility).
