# Single-Cycle Runtime Test Specification

## 1. Test Objectives & Scope

The purpose of this test is to verify that the governed Option-B native HiGHS multi-objective optimizer (`GAP19HighsNativeOptimizer`) successfully formulates and solves the $N = 408$ variable, $M = 312$ constraint MILP model with the pointwise maximum reserve envelope under a single deterministic synthetic test scenario.

---

## 2. Test Input Parameters (Labelled: `SYNTHETIC_ENGINEERING_TEST_VALUE`)

### Battery Parameters:
- `capacity_wh`: $200,000\text{ Wh}$
- `initial_soc_pct`: $80.0\%$ ($\implies \text{initial energy } = 160,000\text{ Wh}$)
- `min_soc_pct`: $20.0\%$ ($\implies \text{minimum energy } = 40,000\text{ Wh}$)
- `max_soc_pct`: $95.0\%$ ($\implies \text{maximum energy } = 190,000\text{ Wh}$)
- `charge_efficiency`: $0.92$
- `discharge_efficiency`: $0.92$
- `max_charge_power_w`: $50,000\text{ W}$
- `max_discharge_power_w`: $50,000\text{ W}$

### Diesel Generator Parameters:
- `min_power_w`: $10,000\text{ W}$
- `max_power_w`: $100,000\text{ W}$
- `base_fuel_consumption_l_per_h`: $5.0\text{ L/h}$
- `marginal_fuel_consumption_l_per_wh`: $0.00025\text{ L/Wh}$
- `startup_fuel_l`: $2.0\text{ L}$

### Demand & Critical Load Trajectories:
- `demand.point`: Constant $20,000\text{ W}$ across all 24 hours.
- `demand_critical.point`: Constant $20,000\text{ W}$ across all 24 hours.

### Renewable Generation Trajectories:
- `solar_generation.point`: Bell curve peaking at $15,000\text{ W}$ between hours 6 and 18.
- `wind_generation.point`: Constant $5,000\text{ W}$ across all 24 hours.

### Governed Reserve Targets:
- **EBR Lookahead Target**: Governed formula $E_{\text{EBR,target}}[t] = \frac{1}{0.92} \sum_{k=t}^{\min(t+5, 23)} P_{\text{crit}}[k] \cdot \Delta t$.
  - For $t \in [0, 18]$ (6-hour window): $20,000 \times 6 / 0.92 = 130,434.78\text{ Wh}$.
- **Terminal Reserve Target**: Explicit synthetic test input $E_{\text{term,target}} = 100,000\text{ Wh}$ (clearly labelled `SYNTHETIC_ENGINEERING_TEST_VALUE`).
  - Pointwise target at $t=23$: $\max(21,739.13, 100,000) = 100,000\text{ Wh}$.

---

## 3. Strict Boundary Rules

1. Solves executed: **EXACTLY 1**.
2. Fallbacks: **NONE**.
3. MPC loops: **NONE**.
4. ECD / Option D calls: **NONE**.
5. Real data used: **NONE**.
