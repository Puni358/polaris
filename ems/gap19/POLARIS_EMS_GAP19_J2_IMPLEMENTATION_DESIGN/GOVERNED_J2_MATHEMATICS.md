# Governed J2 Mathematical Specifications

## 1. Governance Foundation

The sealed governance decisions establish:
- **Lexicographic Stage 2 Objective ($J_2$)**: Minimization of battery reserve shortfall below the governed Stage 2 target trajectory.
- **EBR Component**: Dynamic protected-critical-service energy lookahead requirement over governed $T_{\text{REQUIRED}} = 6\text{ hours}$.
- **Terminal Reserve Component**: End-of-horizon viability requirement for the subsequent 24-hour MPC horizon.
- **Non-Additive Unification**: EBR and Terminal Reserve are unified into a **pointwise maximum reserve envelope** to prevent double-counting.
- **Symbolic Policy Mandate**: All policy parameters ($E_{\text{EBR,target}}[t]$, $E_{\text{term,target}}$) remain symbolic quantities until authorized by human governance.

---

## 2. Discrete Time & Horizon Notation

- Optimization Horizon: $H = 24$ timesteps ($t \in \{0, 1, \dots, 23\}$).
- Timestep Size: $\Delta t = 1.0\text{ hour}$.
- Governed EBR Lookahead Window: $N_{\text{req}} = 6$ timesteps ($T_{\text{REQUIRED}} = 6.0\text{h}$).
- For any timestep $t \in [0, 23]$, the 6-hour lookahead window index set is:
  $$W(t) = \{k \in \mathbb{Z} \mid t \le k \le \min(t + 5, 23)\}$$

---

## 3. Mathematical EBR Target Formulation ($E_{\text{EBR,target}}[t]$)

Let $P_{\text{crit}}[k]$ denote the protected critical demand power forecast at timestep $k$ (in Watts).
Accounting for battery discharge efficiency $\eta_{\text{dis}} \in (0, 1]$ and usable capacity above physical minimum floor $E_{\text{min}}$, the required stored energy target for 6-hour critical load survivability at timestep $t$ is:

$$E_{\text{EBR,target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k \in W(t)} P_{\text{crit}}[k] \cdot \Delta t \quad \text{[Watt-hours]}$$

### Properties:
- For $t \in [0, 18]$: $W(t) = [t, t+5]$ (full 6-hour lookahead within 24h bundle).
- For $t \in [19, 23]$: $W(t) = [t, 23]$ (lookahead window truncated to available 24h bundle, with horizon-edge hand-off to Terminal Reserve).

---

## 4. Mathematical Terminal Reserve Target Formulation ($E_{\text{term,target}}$)

Let $E_{\text{term,target}}$ denote the symbolic stored energy requirement evaluated at the final timestep $t = 23$ (representing stored energy state $E[24]$ at horizon boundary $t = 24\text{h}$).

$$E_{\text{term,target}} = \text{SymbolicViabilityFunction}\left(E_{\text{bat}}[0], \, E_{\text{max}}, \, E_{\text{min}}, \, \text{PolicyInputs}\right) \quad \text{[Watt-hours]}$$

### Candidate Structural Functions (Symbolic):
- **Model A (Cyclic)**: $E_{\text{term,target}} = E_{\text{bat}}[0]$ (Initial state restoration).
- **Model B (Capacity Ratio)**: $E_{\text{term,target}} = E_{\text{min}} + \alpha_{\text{term}} (E_{\text{max}} - E_{\text{min}})$.
- **Model C (Next-Horizon Lookahead)**: $E_{\text{term,target}} = \frac{1}{\eta_{\text{dis}}} \sum_{k=24}^{29} P_{\text{crit}}[k] \cdot \Delta t$.

---

## 5. Pointwise Maximum Reserve Envelope Formulation

To mathematically prevent double-counting between EBR and Terminal Reserve at the horizon boundary, the unified Stage 2 target vector $E_{\text{stage2,target}}[t]$ is defined for all $t \in [0, 23]$ as:

$$E_{\text{stage2,target}}[t] = \begin{cases} 
E_{\text{EBR,target}}[t] & \text{for } 0 \le t < 23 \\ 
\max\left( E_{\text{EBR,target}}[23], \, E_{\text{term,target}} \right) & \text{for } t = 23 
\end{cases} \quad \text{[Watt-hours]}$$

---

## 6. Unified Stage 2 MILP Constraint & Objective

### 6.1 Shortfall Slack Variable ($s_{J2}[t]$)
For each timestep $t \in [0, 23]$, define continuous decision variable $s_{J2}[t] \ge 0$ (re-labeled from `s_EBR[t]`):

$$E[t+1] + s_{J2}[t] \ge E_{\text{stage2,target}}[t] + E_{\text{min}}, \quad \forall t \in \{0, 1, \dots, 23\}$$

Where $E[t+1]$ is the battery stored energy decision variable at the end of timestep $t$ (`base + 6`).

### 6.2 Lexicographic Stage 2 Objective ($J_2$)
$$J_2 = \sum_{t=0}^{23} w_{J2}[t] \cdot s_{J2}[t] \quad \text{[Watt-hours]}$$

Where $w_{J2}[t] = 1.0$ (or governed discount factor).
