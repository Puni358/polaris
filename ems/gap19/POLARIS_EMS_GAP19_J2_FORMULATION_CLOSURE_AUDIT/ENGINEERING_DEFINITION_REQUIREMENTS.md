# Engineering Definition Requirements Register

## Scope & Purpose

This document details all technical specifications, mathematical equations, MILP matrix additions, schema class structures, and interface contracts required for the implementation of Stage 2 $J_2$ reserve optimization once human governance authorizes the remaining policy choices.

Unlike governance decisions, engineering definitions represent pure technical mechanics and system design specifications.

---

## Technical Engineering Requirements Register

### 1. Decision Variable Vector Specification ($K = 17$)
Expand the decision variable array per timestep $t \in [0, 23]$ in `milp.py` from 15 to 17 variables:
- `base + 15`: $s_{\text{EBR}}[t]$ (Continuous slack variable, $0 \le s_{\text{EBR}}[t] \le E_{\text{max}}$).
- `base + 16`: $s_{\text{term}}[t]$ (Continuous slack variable, $0 \le s_{\text{term}}[t] \le E_{\text{max}}$ for $t=23$; $0$ for $t < 23$).

### 2. MILP Constraint Matrix Construction for Unified $J_2$ Pointwise Maximum Envelope
Add linear constraint rows to $A x \ge b$:

#### 2.1 Intra-Horizon EBR Shortfall Constraints ($t \in [0, 22]$)
For each timestep $t \in [0, 22]$:
$$s_{\text{EBR}}[t] + E[t+1] \ge E_{\text{EBR,target}}[t] + E_{\text{min}}$$
In standard $A x \ge b$ form:
$$s_{\text{EBR}}[t] + E[t+1] \ge \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{\min(t+5, 23)} P_{\text{crit}}[k] \Delta t + E_{\text{min}}$$

#### 2.2 Terminal Timestep Pointwise Envelope Constraint ($t = 23$)
For $t = 23$ (evaluating end-of-horizon state $E[24]$):
$$s_{J2}[23] + E[24] \ge \max\left( E_{\text{EBR,target}}[23], \, E_{\text{term,target}} \right) + E_{\text{min}}$$

### 3. Sequential Lexicographic Orchestrator Implementation (Option A)
Implement `SequentialLexicographicMILPOptimizer` class executing four sequential solves per MPC cycle:
- **Pass 1**: Solve $\min J_1(x)$. Record optimal critical shortfall $J_1^*$. Add lock constraint: $J_1(x) \le J_1^* + \epsilon_1$.
- **Pass 2**: Solve $\min J_2(x) = \sum_{t=0}^{23} w_{J2}[t] s_{J2}[t]$ subject to Pass 1 lock. Record $J_2^*$. Add lock constraint: $J_2(x) \le J_2^* + \epsilon_2$.
- **Pass 3**: Solve $\min J_3(x) = \text{Fuel}(x)$ subject to Pass 1 and Pass 2 locks. Record $J_3^*$. Add lock constraint: $J_3(x) \le J_3^* + \epsilon_3$.
- **Pass 4**: Solve $\min J_4(x) = \text{Curtailment}(x)$ subject to Pass 1, 2, and 3 locks. Return final dispatch schedule $x^*$.

### 4. Additive Python Schema Classes
Specify exact Pydantic/dataclass schema modifications:
- `ForecastBundle`: Add `demand_critical: Optional[TimeseriesForecast]` field with validation logic `0 <= demand_critical.point[t] <= demand.point[t]`.
- `StationState`: Add `operating_mode: str` with validation `value in {"NORMAL", "EMERGENCY"}`.
- `DispatchPlan`: Add `j1_objective`, `j2_objective`, `j3_objective`, `j4_objective`, and `reserve_shortfall` fields.

### 5. Verification & Unit Testing Suite Requirements
Develop automated unit tests for J2 formulation verification:
- **Test 1: Zero Shortfall Baseline**: Verify $J_2^* = 0$ when initial battery SOC is 100% and solar generation is high.
- **Test 2: Double-Counting Prevention**: Verify that a $10\text{ kWh}$ deficit at $t=23$ incurs exactly a $10 \cdot w_{J2}[23]$ penalty, regardless of whether $E_{\text{EBR}} > E_{\text{term}}$ or $E_{\text{term}} > E_{\text{EBR}}$.
- **Test 3: Lexicographic Priority Lock**: Verify that when critical load shedding ($J_1$) is threatened, the optimizer discharges the battery down to $E_{\text{min}}$ (incurring $J_2 > 0$) to keep $J_1^* = 0$.
