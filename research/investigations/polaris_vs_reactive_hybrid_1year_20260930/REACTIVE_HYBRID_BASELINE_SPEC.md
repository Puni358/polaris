# Reactive Hybrid Baseline Controller Specification (`ReactiveHybridBaseline`)

## 1. Overview & Purpose

The `ReactiveHybridBaseline` controller is a deterministic, rule-based microgrid energy management controller designed to provide a fair, zero-lookahead baseline for POLARIS benchmarking.

It operates using the **exact same physical hardware resources and constraints** as POLARIS (Solar PV array, Wind generator, Battery storage, Diesel generator, and Site demand), but contains **zero forecasting, zero MILP optimization, zero look-ahead, and zero access to future information**.

---

## 2. Control Logic & Equations

At each simulation timestep $t$ (duration $\Delta t = 1.0 \text{ hour}$):

### Step 1: Net Demand Calculation
Read currently available renewable generation $P_{\text{renewable}}(t) = P_{\text{solar}}(t) + P_{\text{wind}}(t)$ and current site demand $P_{\text{load}}(t)$:

$$P_{\text{net}}(t) = P_{\text{load}}(t) - P_{\text{renewable}}(t)$$

### Step 2: Renewable Surplus Logic ($P_{\text{net}}(t) \le 0$)
1. Serve 100% of site load using renewables: $P_{\text{served}}(t) = P_{\text{load}}(t)$.
2. Calculate available surplus power: $P_{\text{surplus}}(t) = |P_{\text{net}}(t)|$.
3. Charge battery using surplus power, subject to max charge power ($P_{\text{chg,max}} = 50,000 \text{ W}$) and maximum SOC ($E_{\text{max}} = 190,000 \text{ Wh}$, 95%):

$$P_{\text{chg\_possible}} = \min\left(P_{\text{surplus}}(t), P_{\text{chg,max}}, \frac{E_{\text{max}} - E_{\text{curr}}}{\eta_{\text{chg}} \cdot \Delta t}\right)$$

4. Curtail any remaining surplus:

$$P_{\text{curtailment}}(t) = P_{\text{surplus}}(t) - P_{\text{chg\_possible}}$$

5. Set $P_{\text{dis}}(t) = 0$ and $P_{\text{diesel}}(t) = 0$.

### Step 3: Renewable Deficit Logic ($P_{\text{net}}(t) > 0$)
1. Discharging battery to supply net deficit, subject to max discharge power ($P_{\text{dis,max}} = 50,000 \text{ W}$) and minimum SOC ($E_{\text{min}} = 40,000 \text{ Wh}$, 20%):

$$P_{\text{dis\_possible}} = \min\left(P_{\text{net}}(t), P_{\text{dis,max}}, \frac{(E_{\text{curr}} - E_{\text{min}}) \cdot \eta_{\text{dis}}}{\Delta t}\right)$$

2. Calculate remaining net deficit after battery discharge:

$$P_{\text{diesel\_needed}}(t) = P_{\text{net}}(t) - P_{\text{dis\_possible}}$$

### Step 4: Diesel Generator Dispatch Logic
If $P_{\text{diesel\_needed}}(t) > 0$:
- Dispatch diesel generator within physical operating limits ($P_{\text{dies,min}} = 10,000 \text{ W}$, $P_{\text{dies,max}} = 100,000 \text{ W}$):

$$P_{\text{diesel}}(t) = \max\left(P_{\text{diesel\_needed}}(t), P_{\text{dies,min}}\right)$$

Else:
- Set $P_{\text{diesel}}(t) = 0$.

---

## 3. Physical Parameters & Constraints

| Parameter | Symbol / Variable | Value | Units |
| :--- | :--- | :--- | :--- |
| **Battery Nominal Capacity** | $C_{\text{bat}}$ | 200,000 | Wh (200 kWh) |
| **Minimum SOC** | $\text{SOC}_{\text{min}}$ | 20.0% | % (40,000 Wh) |
| **Maximum SOC** | $\text{SOC}_{\text{max}}$ | 95.0% | % (190,000 Wh) |
| **Initial SOC** | $\text{SOC}_{\text{init}}$ | 50.0% | % (100,000 Wh) |
| **Charge Efficiency** | $\eta_{\text{chg}}$ | 0.92 | - |
| **Discharge Efficiency** | $\eta_{\text{dis}}$ | 0.92 | - |
| **Max Charge Power** | $P_{\text{chg,max}}$ | 50,000 | W (50 kW) |
| **Max Discharge Power** | $P_{\text{dis,max}}$ | 50,000 | W (50 kW) |
| **Diesel Minimum Power** | $P_{\text{dies,min}}$ | 10,000 | W (10 kW) |
| **Diesel Maximum Power** | $P_{\text{dies,max}}$ | 100,000 | W (100 kW) |
| **Base Fuel Consumption** | $F_{\text{base}}$ | 5.0 | L/h |
| **Marginal Fuel Consumption** | $F_{\text{marginal}}$ | 0.00025 | L/Wh |
| **Startup Fuel Penalty** | $F_{\text{startup}}$ | 6.0 | L ($15.0 startup cost @ $2.50/L) |

---

## 4. Anti-Cheating & Information-Leakage Verification

```yaml
ANTI_CHEATING_AUDIT:
  FUTURE_LOAD_LOOKAHEAD: NONE (0 hours)
  FUTURE_SOLAR_LOOKAHEAD: NONE (0 hours)
  FUTURE_WIND_LOOKAHEAD: NONE (0 hours)
  FORECAST_ENGINE_CALLS: 0
  OPTIMIZER_SOLVER_CALLS: 0
  POLARIS_DECISION_HINTS: NONE
  DETERMINISM: 100% REPRODUCIBLE
```

The `ReactiveHybridBaseline` queries ONLY the current timestep values (`actual_SW_IN`, `actual_wind_generation`, `actual_demand`, `battery_soc_pct`, `diesel_running`) from `StationState` at step $t$. It has zero access to index $t+1$ or future forecast objects.
