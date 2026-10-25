# FINAL IMPLEMENTATION BLUEPRINT

## 1. AUTHORITATIVE 23-POINT ARCHITECTURAL ANSWERS (A THROUGH W)

This master blueprint provides exact, unambiguous architectural answers for handing Option D implementation off to the coding agent.

---

### A. Where ECD Lives
`EmergencyConditionDetector` lives as a pure functional evaluator in `system/control/ecd.py` ([ecd.py:L199](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py#L199)). It is invoked inside the receding horizon MPC loop in `runner.py` at step $1$ of each iteration.

### B. Where Operating Mode is Represented
Operating mode is represented as an explicit string enum (`OperatingMode`: `"NORMAL"`, `"EMERGENCY"`, `"UNKNOWN_INVALID"`) defined in `system/control/ecd.py`. It is stored in `EmergencyAssessment` and passed in `StationState.operating_mode`.

### C. Where Option D Lives
Option D lives in a decoupled policy preprocessor component (`OptionDPolicyLayer`) in `system/control/option_d_policy.py`. It sits between `ECD` and `EnergyOptimizer`.

### D. How Option D Communicates with the Optimizer
`OptionDPolicyLayer` transforms `EmergencyAssessment` into a solver-neutral `ModeConstraintSet` dataclass (hourly power upper/lower bounds and policy flags), which is passed directly to `EnergyOptimizer.optimize()`.

### E. How Critical Load is Represented
Critical load is represented as an additive 24-step forecast array (`critical_demand` in Watts) on `ForecastBundle` (schema v1.1.0). Sub-category vectors (Heating, Water, Comms) are stored in `metadata["critical_categories"]`.

### F. How Flexible/Noncritical Load is Represented
Flexible/noncritical load is represented as the difference between total demand and critical demand ($P_{\text{flexible}}[t] = P_{\text{demand}}[t] - P_{\text{critical}}[t]$) or an optional `flexible_demand` forecast vector on `ForecastBundle`.

### G. How Renewable-First is Enforced
Renewable-first behavior is enforced via explicit linear allocation constraints in MILP: $P_{\text{ren,crit}}[t] = \min(P_{\text{solar}}[t] + P_{\text{wind}}[t], P_{\text{critical}}[t])$, ensuring available renewables satisfy critical load before diesel or battery power is dispatched.

### H. How Battery Critical-Only Discharge is Enforced
During emergency modes, `ModeConstraintSet` sets the upper bound of battery discharge to hourly critical demand ($0 \le P_{\text{dis}}[t] \le P_{\text{critical}}[t]$), and battery discharge is strictly omitted from the noncritical load busbar balance equation.

### I. How Diesel Supports Critical Load
Busbar balance constraints allow diesel generation to serve remaining critical load ($P_{\text{dies,crit}}[t] = P_{\text{critical}}[t] - P_{\text{ren,crit}}[t] - P_{\text{batt,crit}}[t]$) up to generator capacity.

### J. How Diesel Minimum-Output Excess is Handled
When $u_{\text{diesel}}[t] = 1$ and $P_{\text{diesel,min}} > P_{\text{crit,net}}[t]$, excess generation $P_{\text{excess}}[t] = P_{\text{diesel,min}} - P_{\text{crit,net}}[t]$ is created.

### K. How Battery Charging from Excess Works
Linear constraints force excess generation into battery charging up to the charge power limit ($P_{\text{chg,max}} = 50$ kW) and SOC ceiling ($95\%$): $P_{\text{chg,excess}}[t] = \min(P_{\text{excess}}[t], P_{\text{chg,max}})$.

### L. How Curtailment Works After Battery Charging is Unavailable
Any remaining excess generation above battery charging capacity is curtailed: $P_{\text{curt}}[t] = P_{\text{excess}}[t] - P_{\text{chg,excess}}[t]$.

### M. How Proportional Allocation Works
When available power is insufficient for all protected critical minimums, linear equality constraints tie each category's served power to a common scalar ratio $\alpha[t] \in [0, 1]$: $P_{i,\text{served}}[t] = \alpha[t] \cdot P_{i,\text{min}}[t] \quad \forall i \in \{\text{heating}, \text{water}, \text{comms}\}$.

### N. How UNKNOWN_INVALID Differs from EMERGENCY
- `EMERGENCY`: Assessment is VALID, telemetry is trusted, but resource margin $m < 0$. Invokes Option D MILP optimization.
- `UNKNOWN_INVALID`: Assessment is UNTRUSTED due to invalid/missing/expired inputs. Bypasses solver and invokes `SafeStateFallbackRouter` for governed zero-dispatch safe state.

### O. Where Operator Escalation Lives
Operator escalation lives in the `RuntimeSupervisor` in `system/runtime/`, OUTSIDE the mathematical optimizer. It checks time duration ($t_{\text{degraded}} \ge T_{\text{max\_degraded}}$) and resource thresholds ($V_{\text{fuel}} \le V_{\text{escalate}}$).

### P. How Recovery Works Conceptually
Recovery requires ECD to evaluate $m \ge 0$ (`NORMAL`) on fresh telemetry, maintain stability for $N_{\text{stable}}$ consecutive MPC timesteps, and log an operator acknowledgment event if escalation was active.

### Q. Which Schema Extensions are Needed
- `ForecastBundle`: Optional `critical_demand` field.
- `StationState`: Optional `fuel_remaining_liters` and `operating_mode` fields.
- `DispatchPlan`: Optional `critical_load_served` and `critical_load_unmet` fields.

### R. Which MILP Variables are Needed
19 variables per timestep ($K_{\text{ext}}=19$): $P_{\text{sol,u}}$, $P_{\text{wind,u}}$, $P_{\text{curt,sol}}$, $P_{\text{curt,wind}}$, $P_{\text{chg}}$, $P_{\text{dis}}$, $E_{\text{next}}$, $P_{\text{diesel}}$, $P_{\text{serv,crit}}$, $P_{\text{unm,crit}}$, $P_{\text{serv,flex}}$, $P_{\text{unm,flex}}$, $u_{\text{chg}}$, $u_{\text{dis}}$, $u_{\text{diesel}}$, $v_{\text{start}}$, $\alpha$, $P_{\text{excess}}$, $P_{\text{chg,ex}}$.

### S. Which Objective Terms Belong to GAP19
The 4-stage lexicographic hierarchy (Stage 1: Critical Reliability, Stage 2: EBR, Stage 3: Fuel, Stage 4: Curtailment) belongs to GAP19 native multi-objective solver architecture.

### T. Which Parts Can Be Implemented Without GAP19
Interfaces, schemas, fixture provider, ECD wiring, policy router, MILP 19-variable linear constraints, fail-closed fallback router, and simulator fuel tracking (Strategy 2).

### U. Which Parts MUST Wait for GAP19
Native HiGHS C++ multi-stage sequential lexicographic solver execution and exact Pareto objective stage logging.

### V. Which Parts Require Station Engineering Data
Station-specific electrical circuit mappings and numeric minimum power thresholds ($P_{i,\text{min}}$) for real equipment.

### W. Which Parts Require Additional Governance Decisions
Operator escalation duration limit ($T_{\text{max\_degraded}}$), fuel escalation threshold ($V_{\text{escalate}}$), and automated vs manual recovery clearance rules.
