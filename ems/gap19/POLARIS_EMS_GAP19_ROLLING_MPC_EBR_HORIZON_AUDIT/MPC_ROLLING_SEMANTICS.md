# Receding Horizon MPC Semantics & Structural Horizons

## 1. Distinction Between Three Structural Horizons

To analyze the horizon-edge problem rigorously, we must explicitly separate three distinct operational concepts:

```text
+-------------------------------------------------------------------------+
| 1. DECISION / OPTIMIZATION HORIZON (H_opt = 24 Hours)                  |
|    The discrete mathematical optimization window solved by MILP         |
|    (timesteps k = 0, 1, ..., 23).                                       |
+-------------------------------------------------------------------------+

+-------------------------------------------------------------------------+
| 2. FORECAST INFORMATION HORIZON (H_forecast = 24 Hours)                 |
|    The temporal range of predicted solar, wind, and demand data         |
|    supplied by ForecastBundle (timestamps t0+1h ... t0+24h).            |
+-------------------------------------------------------------------------+

+-------------------------------------------------------------------------+
| 3. EBR SURVIVABILITY HORIZON (T_REQUIRED = 6 Hours)                     |
|    The governed dynamic emergency reserve lookahead window for          |
|    protected critical load service (lookahead W(t) = [t, min(t+5, 23)]).|
+-------------------------------------------------------------------------+
```

---

## 2. Receding Horizon Mechanics in POLARIS

### 2.1 Optimization vs Execution Lifecycle

In each MPC cycle at real-world time $t_{\text{now}}$:
1. **Forecast Generation**: `ForecastEngine` receives $t_{\text{now}}$ and generates a 24-hour forecast bundle for $[t_{\text{now}} + 1\text{h}, \dots, t_{\text{now}} + 24\text{h}]$.
2. **Optimization Solve**: `LocalMILPEnergyOptimizer` formulates a 24-hour MILP problem over $k \in [0, 23]$ and outputs a 24-hour `DispatchPlan`:
   - `battery_charge`: $[P_{\text{chg}}[0], P_{\text{chg}}[1], \dots, P_{\text{chg}}[23]]$
   - `battery_discharge`: $[P_{\text{dis}}[0], P_{\text{dis}}[1], \dots, P_{\text{dis}}[23]]$
   - `diesel_power`: $[P_{\text{diesel}}[0], P_{\text{diesel}}[1], \dots, P_{\text{diesel}}[23]]$
3. **Execution Commitment (Step 0 Only)**: `PolarisLocalRunner` passes `plan` to `DigitalTwinSimulator.step()`. The simulator **extracts and executes ONLY step index 0** ($P_{\text{chg}}[0]$, $P_{\text{dis}}[0]$, $P_{\text{diesel}}[0]$).
4. **Discarding Future Plan Steps ($k=1 \dots 23$)**: The remaining 23 hours of planned dispatch ($k=1 \dots 23$) are **NEVER EXECUTED**. They serve solely as lookahead trajectory guidance to prevent myopic control decisions at $k=0$.
5. **State Advancement & Re-Observation**: The simulator updates physical state ($E_{\text{bat}}$, SOC, fuel) and advances time to $t_{\text{next}} = t_{\text{now}} + 1\text{h}$.

### 2.2 Re-Forecasting Verification (Question 6)
- **Question 6**: Does each MPC cycle request a fresh 24-hour forecast?
- **Finding**: `YES. ABSOLUTELY.`
- At $t_{\text{next}} = t_{\text{now}} + 1\text{h}$, the runner loops back to `forecast_engine.predict()`. A **brand new 24-hour `ForecastBundle`** is generated for $[t_{\text{next}} + 1\text{h}, \dots, t_{\text{next}} + 24\text{h}]$.
- Therefore, every executed control decision occurs at step 0 of a fresh 24-hour optimization cycle with a fresh 24-hour forecast information window.

---

## 3. Impact on EBR Lookahead Evaluation

Because **only step 0 is executed** and **re-forecasting occurs every 1 hour**:

1. For the executed control step ($k=0$), the required 6-hour EBR lookahead spans $[t_{\text{now}} + 1\text{h}, \, t_{\text{now}} + 6\text{h}]$.
2. The fresh `ForecastBundle` provides forecasts for $[t_{\text{now}} + 1\text{h}, \, t_{\text{now}} + 24\text{h}]$.
3. The executed control step ($k=0$) **ALWAYS HAS 100% COMPLETE, UN-TRUNCATED 6-HOUR EVIDENTIARY FORECAST DATA** at every single MPC cycle.
4. The horizon-edge truncation at $k \in [19, 23]$ affects ONLY the unexecuted tail of the 24-hour optimization plan.
