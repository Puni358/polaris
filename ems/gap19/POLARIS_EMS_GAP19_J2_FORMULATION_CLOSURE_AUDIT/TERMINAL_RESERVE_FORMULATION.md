# Terminal Reserve Mathematical Formulation

## 1. Governed Semantics

The human governance decision establishes:
- **Semantics**: Terminal Reserve is a distinct end-of-horizon reserve evaluated at the final timestep of the current 24-hour MPC horizon ($t = H = 24\text{h}$, or end of interval $t = 23$).
- **Purpose**: To ensure that the subsequent 24-hour MPC horizon (starting at origin $t_0 + 24\text{h}$) begins from a viable operating state, preventing finite-horizon optimization artifacts where the optimizer depletes stored battery energy to zero at $t = 24\text{h}$ to artificially optimize current-horizon costs.
- **Relationship**: Terminal Reserve has a distinct operational purpose from intra-horizon EBR. It must NOT be blindly added to EBR.

---

## 2. Mathematical Definition of "Viable Operating State"

Without inventing an unauthorized numerical policy value, a "viable operating state" at the horizon boundary $t = H$ can be defined mathematically under four candidate structural formulations.

### Candidate Structural Models

#### Model A: Cyclic Initial-State Continuity
Requires end-of-horizon battery stored energy to match or exceed the initial stored energy at the start of the horizon:
$$E_{\text{term,target}} = E_{\text{bat}}[0] \quad \text{[Watt-hours]}$$
- **Mathematical Meaning**: Guarantees non-negative net daily stored energy balance across rolling 24-hour cycles.
- **Properties**: Requires no forward forecast beyond current horizon; prevents systematic battery depletion.

#### Model B: Fixed Proportion of Usable Battery Capacity
Requires end-of-horizon stored energy to maintain a governed minimum buffer fraction $\alpha_{\text{term}} \in [0, 1]$ of total battery capacity $E_{\text{max}}$:
$$E_{\text{term,target}} = E_{\text{min}} + \alpha_{\text{term}} \cdot \left(E_{\text{max}} - E_{\text{min}}\right) \quad \text{[Watt-hours]}$$
- **Mathematical Meaning**: Enforces a standing state-of-charge floor at $t = 24\text{h}$.
- **Properties**: $\alpha_{\text{term}}$ is an explicit governance policy parameter (unauthorized at present).

#### Model C: Forward Critical-Load Survivability Continuation
Requires end-of-horizon stored energy to cover the initial 6-hour critical load requirement of the *next* 24-hour MPC horizon ($t \in [24, 29]$):
$$E_{\text{term,target}} = \frac{1}{\eta_{\text{dis}}} \sum_{k=24}^{29} P_{\text{crit}}[k] \cdot \Delta t \quad \text{[Watt-hours]}$$
- **Mathematical Meaning**: Direct extension of EBR survivability semantics into the next control horizon.
- **Properties**: Provides seamless rolling-horizon continuity for critical load coverage.

#### Model D: Net Deficit / Fuel-Decoupled Viability Envelope
Requires end-of-horizon stored energy to cover expected net demand deficit (demand minus renewable generation) during the initial non-solar hours of the subsequent morning:
$$E_{\text{term,target}} = \max\left( E_{\text{min}}, \frac{1}{\eta_{\text{dis}}} \sum_{k=24}^{24+M-1} \max\left(0, P_{\text{crit}}[k] - P_{\text{pv}}[k] - P_{\text{wind}}[k]\right) \cdot \Delta t \right)$$
- **Mathematical Meaning**: Accounts for renewable generation expected at dawn of the next day.

---

## 3. Terminal Reserve Shortfall Variable ($s_{\text{term}}$)

In the Stage 2 MILP formulation ($J_2$), the Terminal Reserve target is enforced via a single terminal shortfall slack variable $s_{\text{term}}$:
$$\begin{aligned}
s_{\text{term}} &\ge E_{\text{term,target}} - \left(E_{\text{bat}}[H] - E_{\text{min}}\right) \\
s_{\text{term}} &\ge 0
\end{aligned}$$

Where $E_{\text{bat}}[H]$ is the final stored energy state at the end of timestep $t = 23$ (i.e. $E[24]$ in discrete transition equations).

---

## 4. Information Requirements Audit

The information required to compute and enforce Terminal Reserve depends on the selected structural model:

| Information Category | Model A (Cyclic) | Model B (Capacity Ratio) | Model C (Forward Critical) | Model D (Net Deficit Envelope) | Governance / Schema Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Initial Battery State ($E_{\text{bat}}[0]$)** | **REQUIRED** | Not Required | Not Required | Not Required | Available in `StationState` |
| **Battery Capacity ($E_{\text{min}}, E_{\text{max}}$)** | **REQUIRED** | **REQUIRED** | **REQUIRED** | **REQUIRED** | Available in `config["battery"]` |
| **Next-Horizon Forecast ($t \ge 24\text{h}$)** | Not Required | Not Required | **REQUIRED** ($P_{\text{crit}}[24..29]$) | **REQUIRED** ($P_{\text{crit}}, P_{\text{pv}}, P_{\text{wind}}$) | `ADDITIVE_EXTENSION_REQUIRED` |
| **Critical-Load Trajectory** | Not Required | Not Required | **REQUIRED** | **REQUIRED** | `ADDITIVE_EXTENSION_REQUIRED` |
| **Renewable Forecast** | Not Required | Not Required | Not Required | **REQUIRED** | Available if horizon extended |
| **Generator / Fuel Information** | Not Required | Not Required | Not Required | Optional | Available in `StationState` |
| **Uncertainty Margins** | Optional | Optional | Optional | Optional | `NOT_AUTHORIZED` |

---

## 5. Summary Finding

Terminal Reserve cannot be evaluated without selecting one of the four mathematical structural models (A, B, C, or D).
While Model A (Cyclic) and Model B (Capacity Ratio) can be evaluated using existing 24-hour horizon data, Model C and Model D require **next-horizon forecast information** extending beyond $t = 23\text{h}$.
Selecting among Models A, B, C, or D is a **GOVERNANCE DECISION** that remains open.
