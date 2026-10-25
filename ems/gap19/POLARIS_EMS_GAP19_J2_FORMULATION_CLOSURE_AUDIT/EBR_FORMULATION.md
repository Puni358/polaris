# Emergency Battery Reserve (EBR) Mathematical Formulation

## 1. Governed Semantics

The human governance decision establishes:
- **Semantics**: Emergency Battery Reserve (EBR) is a dynamic emergency-survivability reserve designated specifically for protected critical service over the governed lookahead duration $T_{\text{REQUIRED}} = 6\text{ hours}$.
- **Scope**: EBR target dynamically scales with the expected critical load trajectory across the forward 6-hour lookahead window. It is decoupled from non-critical load demands.
- **Status**: Semantics are GOVERNED; numerical policy multipliers or static reserve overrides remain UNAUTHORIZED.

---

## 2. Discrete Time & Horizon Notation

Let the MPC optimization problem be formulated over a discrete finite horizon:
- Timesteps: $t \in \mathcal{T} = \{0, 1, 2, \dots, H-1\}$, where $H = 24$.
- Timestep duration: $\Delta t = 1.0\text{ hour}$.
- Governed survivability window duration: $T_{\text{REQUIRED}} = 6.0\text{ hours}$.
- Governed lookahead horizon in timesteps: $N_{\text{req}} = \frac{T_{\text{REQUIRED}}}{\Delta t} = \frac{6.0}{1.0} = 6\text{ timesteps}$.

At any timestep $t \in \mathcal{T}$, the forward 6-hour lookahead window index set is defined as:
$$W(t) = \left\{ k \in \mathbb{Z} \mid t \le k \le \min\left(t + N_{\text{req}} - 1, H - 1\right) \right\}$$

---

## 3. Mathematical EBR Target & Shortfall Formulation

### 3.1 Protected Critical Demand Energy Requirement
Let $P_{\text{crit}}[k]$ denote the protected critical load power forecast at timestep $k$ (in Watts).
The total energy required to sustain protected critical service across lookahead window $W(t)$ is:
$$E_{\text{crit,req}}[t] = \sum_{k \in W(t)} P_{\text{crit}}[k] \cdot \Delta t \quad \text{[Watt-hours]}$$

Accounting for battery discharge efficiency $\eta_{\text{dis}} \in (0, 1]$, the required stored energy target in the battery at timestep $t$ to guarantee 6-hour critical load survivability is:
$$E_{\text{EBR,target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k \in W(t)} P_{\text{crit}}[k] \cdot \Delta t \quad \text{[Watt-hours]}$$

### 3.2 Usable Battery Energy State
Let $E_{\text{bat}}[t]$ denote the total stored energy in the battery at timestep $t$ (in Watt-hours).
Let $E_{\text{min}} = \text{capacity\_wh} \cdot \frac{\text{min\_soc\_pct}}{100.0}$ denote the technical minimum stored energy floor mandated for battery health preservation (e.g., 20% SOC).

The usable stored energy available for critical dispatch above hardware floor $E_{\text{min}}$ is:
$$E_{\text{usable}}[t] = E_{\text{bat}}[t] - E_{\text{min}} \quad \text{[Watt-hours]}$$

### 3.3 Stage 2 EBR Shortfall Variable ($s_{\text{EBR}}[t]$)
In the Stage 2 MILP formulation ($J_2$), the EBR target is enforced via a non-negative shortfall slack variable $s_{\text{EBR}}[t]$:
$$\begin{aligned}
s_{\text{EBR}}[t] &\ge E_{\text{EBR,target}}[t] - \left(E_{\text{bat}}[t] - E_{\text{min}}\right), \quad \forall t \in \{0, \dots, H-1\} \\
s_{\text{EBR}}[t] &\ge 0, \quad \forall t \in \{0, \dots, H-1\}
\end{aligned}$$

When usable battery energy meets or exceeds the governed 6-hour requirement ($E_{\text{usable}}[t] \ge E_{\text{EBR,target}}[t]$), $s_{\text{EBR}}[t] = 0$.
When usable battery energy falls below the 6-hour requirement, $s_{\text{EBR}}[t] > 0$ represents the exact Watt-hour deficit penalizing the Stage 2 objective $J_2$.

---

## 4. Information Requirements Matrix

To calculate $E_{\text{EBR,target}}[t]$ and enforce the EBR constraints in the optimizer, the following information inputs are strictly required:

| Information Category | Specific Variable / Input | Source / Schema Component | Role in EBR Calculation |
| :--- | :--- | :--- | :--- |
| **Critical Load Trajectory** | $P_{\text{crit}}[k]$ for $k \in [t, t+5]$ | `ForecastBundle.demand.critical` (Additive Extension) | Defines exact 6-hour energy requirement for protected loads. |
| **Timestep Parameter** | $\Delta t$ (hours) | `config["optimizer"]["timestep_hours"]` | Converts power forecasts (W) to energy quantities (Wh). |
| **Battery State** | $E_{\text{bat}}[t]$ or $E[t+1]$ | Decision variable $E[t]$ in `milp.py` / `StationState` | Represents stored energy state evaluated against target. |
| **Battery Technical Limits** | $E_{\text{min}}, E_{\text{max}}, \eta_{\text{dis}}, P_{\text{dis,max}}$ | `config["battery"]` | Establishes usable capacity floor and discharge losses. |
| **Forecast Horizon** | $H = 24\text{h}$, $N_{\text{req}} = 6\text{h}$ | Optimization Horizon Specification | Defines lookahead boundary and window truncation rules. |
| **Operating Mode** | $\text{MODE} \in \{\text{NORMAL}, \text{EMERGENCY}\}$ | ECD / `StationState.operating_mode` | Determines objective weighting and priority enforcement. |
