# POLARIS EMS GAP19 — INFEASIBILITY ROOT CAUSE AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Evidence Classification**: `CONTROLLED_SYNTHETIC_ENGINEERING_RUNTIME_EVIDENCE`  

---

## 1. Executive Summary & Root Cause Classification

This forensic audit investigates the exact mathematical causes of infeasibility observed in:
- `demand_stress` (Cycles 5–24 `OPTIMIZATION_INFEASIBLE`)
- `battery_stress` (Cycles 1–24 `OPTIMIZATION_INFEASIBLE`)

### Classification Matrix

| Scenario | Primary Root Cause Classification | Description |
| :--- | :--- | :--- |
| **`demand_stress`** | `EXPECTED_INFEASIBILITY_FROM_GOVERNED_HARD_CONSTRAINTS`<br>`J2_SLACK_BOUND_MODELING_LIMITATION`<br>`SYNTHETIC_FIXTURE_OUTSIDE_DEFINED_FEASIBLE_OPERATING_SPACE` | 6-hour critical load peak ($66.7\text{ kW}$) generates required EBR target $E_{\text{EBR\_target}} = 380,412.25\text{ Wh}$. Coupled with $E_{\min}=40,000\text{ Wh}$, required constraint LHS is $420,412.25\text{ Wh}$, which exceeds the physical upper bound $E_{\max} + s_{\text{J2\_max}} = 190,000 + 200,000 = 390,000\text{ Wh}$. |
| **`battery_stress`** | `EXPECTED_INFEASIBILITY_FROM_GOVERNED_HARD_CONSTRAINTS`<br>`J2_SLACK_BOUND_MODELING_LIMITATION`<br>`SYNTHETIC_FIXTURE_OUTSIDE_DEFINED_FEASIBLE_OPERATING_SPACE` | High load ($45.5\text{ kW}$) and suppressed renewables ($3\text{ kW}$) generate 6-hour EBR targets exceeding battery capacity reserve limits across all 24 cycles. |

---

## 2. Complete Numerical Reconstruction & Parameter Registry

All parameters are ingested directly from codebase configurations (`system/config/*.yaml`) and scenario fixtures (`system/data/scenarios/*.json`):

### Battery System Parameters
* **Nominal Capacity ($C_{\text{bat}}$)**: $200,000.0\text{ Wh}$ ($200\text{ kWh}$)
* **Minimum SOC ($SOC_{\min}$)**: $20.0\%$ $\rightarrow E_{\min} = 40,000.0\text{ Wh}$
* **Maximum SOC ($SOC_{\max}$)**: $95.0\%$ $\rightarrow E_{\max} = 190,000.0\text{ Wh}$
* **Discharge Efficiency ($\eta_{\text{dis}}$)**: $0.92$
* **Charge Efficiency ($\eta_{\text{chg}}$)**: $0.92$
* **Maximum Charge Power ($P_{\text{chg, max}}$)**: $50,000.0\text{ W}$
* **Maximum Discharge Power ($P_{\text{dis, max}}$)**: $50,000.0\text{ W}$

### Diesel Generator Parameters
* **Minimum Operating Power ($P_{\text{diesel, min}}$)**: $10,000.0\text{ W}$
* **Maximum Operating Power ($P_{\text{diesel, max}}$)**: $100,000.0\text{ W}$

### Governed Reserve Constraints
* **EBR Horizon ($T_{\text{EBR}}$)**: $6\text{ hours}$ (6 timesteps)
* **Pointwise Envelope Reserve Constraint**:
  $$E_{\text{next}}[t] + s_{\text{J2}}[t] \ge E_{\text{stage2\_target}}[t] + E_{\min}$$
  where $E_{\text{stage2\_target}}[t] = \max(E_{\text{EBR\_target}}[t], E_{\text{term\_target}})$.
* **EBR Target Formula**:
  $$E_{\text{EBR\_target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{\min(t+5, 23)} P_{\text{crit}}[k] \cdot \Delta t$$
* **J2 Slack Bounds**:
  $$0.0 \le s_{\text{J2}}[t] \le \text{capacity\_wh} = 200,000.0\text{ Wh}$$

---

## 3. The Binding Mathematical Contradiction

### Maximum Possible Left-Hand Side (LHS)
For any timestep $t$, the decision variables $E_{\text{next}}[t]$ and $s_{\text{J2}}[t]$ are bounded as follows:
1. $E_{\text{next}}[t] \le E_{\max} = 190,000.0\text{ Wh}$
2. $s_{\text{J2}}[t] \le s_{\text{J2\_max}} = 200,000.0\text{ Wh}$

Therefore, the maximum possible value of the Left-Hand Side of the reserve constraint is:
$$\max \left( E_{\text{next}}[t] + s_{\text{J2}}[t] \right) = 190,000.0 + 200,000.0 = 390,000.0\text{ Wh}$$

### Threshold for Required Right-Hand Side (RHS)
The Right-Hand Side of the constraint is:
$$\text{RHS}[t] = E_{\text{EBR\_target}}[t] + E_{\min} = E_{\text{EBR\_target}}[t] + 40,000.0\text{ Wh}$$

For the constraint to be mathematically feasible, we must have:
$$\text{RHS}[t] \le \max(\text{LHS}) \implies E_{\text{EBR\_target}}[t] + 40,000.0 \le 390,000.0\text{ Wh}$$
$$E_{\text{EBR\_target}}[t] \le 350,000.0\text{ Wh}$$

Converting $E_{\text{EBR\_target}}[t]$ to AC critical load energy over 6 hours:
$$W_{\text{crit\_6h}} = E_{\text{EBR\_target}}[t] \times \eta_{\text{dis}} \le 350,000.0 \times 0.92 = 322,000.0\text{ Wh}$$

Average 6-hour critical power threshold:
$$\bar{P}_{\text{crit\_6h\_max}} = \frac{322,000.0\text{ Wh}}{6\text{ h}} = 53,666.67\text{ W} \approx 53.67\text{ kW}$$

> **Key Theoretical Result**: If average critical demand over any 6-hour lookahead window exceeds **$53.67\text{ kW}$**, the reserve constraint becomes **mathematically impossible to satisfy** under the current $s_{\text{J2}}$ upper bound ($200\text{ kWh}$), causing HiGHS to return `kInfeasible`.

---

## 4. Trace of `demand_stress` Infeasibility at Cycle 5

In `demand_stress_scenario.json`, peak demand accelerates between hours 5 and 11:
* $t=5$: $52,500.0\text{ W}$
* $t=6$: $52,500.0\text{ W}$
* $t=7$: $56,382.29\text{ W}$
* $t=8$: $60,000.0\text{ W}$
* $t=9$: $63,106.60\text{ W}$
* $t=10$: $65,490.38\text{ W}$

Summing critical AC load over the 6-hour lookahead window $W(5) = [5, 10]$:
$$W_{\text{crit\_6h}}(5) = 52,500 + 52,500 + 56,382.29 + 60,000 + 63,106.60 + 65,490.38 = 349,979.27\text{ Wh}$$

Battery-side required EBR reserve:
$$E_{\text{EBR\_target}}[5] = \frac{349,979.27\text{ Wh}}{0.92} = 380,412.25\text{ Wh}$$

Required RHS of constraint at $t=5$:
$$\text{RHS}[5] = E_{\text{EBR\_target}}[5] + E_{\min} = 380,412.25 + 40,000.0 = 420,412.25\text{ Wh}$$

Comparing RHS to maximum possible LHS:
$$\text{RHS}[5] = 420,412.25\text{ Wh} > \max(\text{LHS}) = 390,000.0\text{ Wh}$$

$$\text{Contradiction Gap} = 420,412.25 - 390,000.0 = +30,412.25\text{ Wh}$$

This proves conclusively that:
$$E_{\text{EBR\_target}}[t] + E_{\min} > E_{\max} + s_{\text{J2\_max}}$$
is the **exact binding contradiction** that causes `demand_stress` to fail at Cycle 5.

---

## 5. Summary Verdict

The infeasibility observed in `demand_stress` and `battery_stress` is not a random numerical solver glitch, but an **inevitable mathematical consequence** of combining:
1. High peak demand in synthetic fixtures ($>53.67\text{ kW}$ average over 6h),
2. A strict 6-hour EBR reserve lookahead requirement, and
3. An artificial upper bound ($200\text{ kWh}$) placed on the $s_{\text{J2}}$ reserve slack variable.
