# Terminal Reserve Implementation Design

## 1. Symbolic Definition of $E_{\text{term,target}}$

Terminal Reserve ($E_{\text{term,target}}$) represents the required stored energy buffer at the horizon boundary $t = 24\text{h}$ (end of timestep $t=23$, i.e. decision variable $E[24]$) designated to ensure that the subsequent 24-hour MPC optimization cycle begins from a viable operating state.

Symbolically, $E_{\text{term,target}}$ is defined as:

$$E_{\text{term,target}} = f_{\text{term}}\left( E_{\text{bat}}[0], \, E_{\text{min}}, \, E_{\text{max}}, \, \mathbf{\Theta}_{\text{policy}} \right) \quad \text{[Watt-hours]}$$

Where $\mathbf{\Theta}_{\text{policy}}$ is an unresolved policy parameter vector that must remain strictly symbolic until authorized by human governance.

---

## 2. Distinction Between EBR and Terminal Reserve

| Operational Dimension | Emergency Battery Reserve (EBR) | Terminal Reserve |
| :--- | :--- | :--- |
| **Operational Purpose** | Guarantees dynamic 6-hour survivability for protected critical loads during unexpected outages. | Ensures finite-horizon MPC optimization continuity into the subsequent 24-hour control horizon. |
| **Temporal Scope** | Dynamic intra-horizon lookahead evaluated at every timestep $t \in [0, 23]$. | Fixed end-of-horizon boundary target evaluated specifically at $t = 23$ ($E[24]$). |
| **Data Driving Target** | Forward 6-hour critical load forecast trajectory $P_{\text{crit}}[k]$. | Horizon continuity policy (e.g. initial state restoration $E[0]$ or standing morning peak buffer). |
| **Horizon Boundary Effect** | Shrinks near horizon edge ($t \in [19, 23]$) due to finite 24h forecast window. | Dominates at horizon edge ($t = 23$) to hand off viable state to next cycle. |

---

## 3. Engineering Inputs Required to Instantiate Terminal Reserve

To compute and instantiate $E_{\text{term,target}}$ in Python/HiGHS once governed:

1. **Initial Stored Energy State ($E_{\text{bat}}[0]$)**: Passed via `station_state.battery_energy_wh`.
2. **Battery Hardware Floor & Ceiling ($E_{\text{min}}, E_{\text{max}}$)**: Computed from `config["battery"]` capacity and SOC bounds.
3. **Terminal Target Function / Override**: Transported via `config["terminal_target_wh"]` or additive field `StationState.terminal_target_wh_override`.
4. **Pointwise Envelope Integration**: Evaluated at $t=23$ as $\max\left(E_{\text{EBR,target}}[23], \, E_{\text{term,target}}\right)$.

---

## 4. Preservation of Symbolic Policy Values

```text
NUMERICAL_TERMINAL_TARGET = NOT_AUTHORIZED (PRESERVED AS SYMBOLIC VARIABLE)
```

No numerical value for $\mathbf{\Theta}_{\text{policy}}$ (such as $E_{\text{term,target}} = E[0]$ or $E_{\text{term,target}} = 0.5 E_{\text{max}}$) is authorized by this design package.
