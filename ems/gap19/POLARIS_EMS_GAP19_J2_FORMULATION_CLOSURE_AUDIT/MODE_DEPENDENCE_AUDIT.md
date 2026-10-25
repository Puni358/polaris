# Operating Mode Dependence Audit (NORMAL vs EMERGENCY)

## 1. Governed Operating Mode Architecture

Existing POLARIS EMS governance dictates:
1. **Emergency Condition Detector (ECD)**: An external, deterministic detector evaluates telemetry and determines the operating mode ($\text{MODE} \in \{\text{NORMAL}, \text{EMERGENCY}\}$).
2. **Optimizer Role**: The optimizer NEVER determines operating mode. It receives $\text{MODE}$ as an immutable input in `StationState`.
3. **NORMAL Mode Semantics**: The system operates under standard economic dispatch, preserving battery life (limiting degradation) and maintaining the Stage 2 Emergency Battery Reserve (EBR) to ensure readiness for unexpected grid outages or resource failures.
4. **EMERGENCY Mode Semantics**: The system experiences an active emergency (e.g. grid loss, low fuel, generator fault). The primary objective is 100% protection of critical load ($J_1$). Battery stored energy MAY be discharged down to physical floor $E_{\text{min}}$ whenever necessary to serve critical load.
5. **No Permanent Priority Lock**: There is NO hard-coded permanent priority of battery over diesel or diesel over battery during an emergency. The optimizer dispatches available resources flexibly to maximize critical load survivability.

---

## 2. Mathematical Proof of Mode Independence in Lexicographic Hierarchy

The Lexicographic EMS Objective Specification defines four strictly ordered optimization stages:
$$\min \quad \left[ J_1(x), \, J_2(x), \, J_3(x), \, J_4(x) \right]$$

Where:
- **Stage 1 ($J_1$)**: Minimization of unserved critical load energy shortfall:
  $$J_1 = \sum_{t=0}^{H-1} s_{\text{crit}}[t] \quad \text{[kWh]}$$
- **Stage 2 ($J_2$)**: Minimization of reserve target shortfall:
  $$J_2 = \sum_{t=0}^{H-1} w_{J2}[t] \cdot s_{J2}[t] \quad \text{[kWh]}$$
- **Stage 3 ($J_3$)**: Minimization of diesel fuel consumption:
  $$J_3 = \text{Fuel}_{\text{total}} \quad \text{[Liters]}$$
- **Stage 4 ($J_4$)**: Minimization of renewable curtailment:
  $$J_4 = \sum_{t=0}^{H-1} P_{\text{curt}}[t] \cdot \Delta t \quad \text{[kWh]}$$

### Lexicographic Priority Proof: $J_1 \succ \succ J_2$

By mathematical definition of lexicographic optimization:
Stage 1 is solved first: $J_1^* = \min J_1(x)$.
In Pass 2, $J_2$ is minimized subject to the hard lock constraint:
$$J_1(x) \le J_1^* + \epsilon_1$$

#### Case A: Normal Operation (No Critical Load Threat)
In normal operation, solar, wind, battery, and diesel resources are sufficient to cover critical load ($J_1^* = 0$).
The solver then minimizes $J_2$ (EBR shortfall). The optimizer avoids unnecessary battery discharge below $E_{\text{stage2,target}}[t]$ because doing so would increase $J_2$ without any benefit to $J_1$. Battery reserve and battery life are preserved.

#### Case B: Emergency Operation (Resource Deficit / Grid Outage)
Suppose a grid outage occurs and renewable generation is zero. To serve critical load ($P_{\text{crit}}$) and keep $J_1^* = 0$, the battery must discharge below $E_{\text{stage2,target}}[t]$.
Because Stage 1 ($J_1$) strictly dominates Stage 2 ($J_2$), the solver WILL discharge the battery down to $E_{\text{min}}$ (incurring $J_2 > 0$) to maintain $s_{\text{crit}}[t] = 0$.

#### Proof Conclusion
The lexicographic hierarchy $J_1 \succ \succ J_2$ **NATIVELY GUARANTEES** that:
- Normal mode preserves battery reserve.
- Emergency mode automatically uses battery stored energy down to $E_{\text{min}}$ to prevent critical load shedding.
- NO mode-dependent structural mutation of MILP constraints is required!

---

## 3. Interaction Between ECD Mode and Objective Stage Weights / Locks

While the structural MILP matrix remains invariant, the operating mode passed by ECD can adjust stage parameters if authorized by governance:

| Operating Mode | $J_1$ Lock Tolerance ($\epsilon_1$) | $J_2$ Reserve Penalty Weight ($w_{J2}$) | Diesel Startup Penalty ($C_{\text{start}}$) | Optimizer Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **NORMAL** | Standard ($\epsilon_1$) | Standard ($w_{J2}$) | Standard ($C_{\text{start}}$) | Preserves EBR reserve buffer; uses diesel efficiently; limits battery degradation cycling. |
| **EMERGENCY** | Strict ($\epsilon_1 \to 0$) | De-emphasized or Invariant | Reduced / Zero | Dispatches ALL available battery energy and diesel capacity to ensure $s_{\text{crit}} = 0$. |

---

## 4. Audit Verdict on Mode Semantics

- **Preservation of ECD Authority**: `VERIFIED`. The optimizer remains a passive consumer of `StationState.operating_mode`.
- **Battery-vs-Diesel Priority**: `VERIFIED`. No permanent hard-coded priority exists. In Stage 3 ($J_3$), diesel fuel is minimized; in Stage 2 ($J_2$), reserve shortfall is minimized. When $J_1$ is locked, the optimizer uses the exact combination of battery and diesel that minimizes Stage 2 and Stage 3 lexicographically.
- **Structural Constraint Stability**: `VERIFIED`. The unified Stage 2 pointwise envelope formulation $s_{J2}[t]$ holds identically in both NORMAL and EMERGENCY modes.
