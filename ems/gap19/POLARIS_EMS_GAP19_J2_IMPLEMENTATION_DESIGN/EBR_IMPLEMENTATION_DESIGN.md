# EBR Calculation & Implementation Design

## 1. Mathematical Equation for $E_{\text{EBR,target}}[t]$

For each optimization decision timestep $t \in \{0, 1, \dots, 23\}$:

$$E_{\text{EBR,target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{\min(t+5, 23)} P_{\text{crit}}[k] \cdot \Delta t \quad \text{[Watt-hours]}$$

Where:
- $t$: Optimization decision timestep index ($0 \le t \le 23$).
- $P_{\text{crit}}[k]$: Protected critical load power forecast at timestep $k$ (in Watts).
- $\Delta t$: Timestep duration parameter ($\Delta t = 1.0\text{ hour}$).
- $\eta_{\text{dis}}$: Battery discharge efficiency ($\eta_{\text{dis}} = 0.92$ default).
- Lookahead Window: $W(t) = [t, \min(t+5, 23)]$.

---

## 2. Parameter Specifications & Conventions

### 2.1 Critical-Demand Trajectory ($P_{\text{crit}}[k]$)
- **Source**: Transported via additive field `ForecastBundle.demand_critical.point` (or fallback ratio $P_{\text{crit}}[k] = \gamma_{\text{crit}} P_{\text{demand}}[k]$).
- **Units**: Watts (W).
- **Length**: Exactly 24 point forecast values corresponding to timesteps $k = 0 \dots 23$.

### 2.2 Timestep & Indexing Convention
- **Origin $t_0$**: Current observation timestamp $t_{\text{now}}$ (e.g. `"2024-01-01T00:00:00Z"`).
- **Timestep $k=0$**: Interval $[t_0, t_0+1\text{h}]$ (the EXECUTED control step).
- **Timestep $k=23$**: Interval $[t_0+23\text{h}, t_0+24\text{h}]$ (the final step of the decision plan).
- **Current-vs-Future Convention**: $E[t+1]$ represents stored energy at the END of timestep $t$. The target $E_{\text{EBR,target}}[t]$ evaluates required stored energy to sustain critical service across lookahead window starting at $t$.

### 2.3 Horizon-Edge Behavior ($t \in [19, 23]$)
- At $t=18$: Lookahead covers $k \in [18, 23]$ (6 full forecast steps).
- At $t=19$: Lookahead covers $k \in [19, 23]$ (5 available forecast steps).
- At $t=23$: Lookahead covers $k = 23$ (1 available forecast step).
- At $t=23$, the horizon edge is coupled directly to Terminal Reserve:
  $$E_{\text{stage2,target}}[23] = \max\left(E_{\text{EBR,target}}[23], \, E_{\text{term,target}}\right)$$

### 2.4 Rolling-MPC Behavior
- Because `PolarisLocalRunner` executes ONLY step $k=0$ and re-forecasts every 1 hour:
  - At every executed control step ($k=0$), the lookahead window is ALWAYS $W(0) = [0, 5]$ (6 complete hours).
  - Unexecuted plan tail steps ($k \in [19, 23]$) are superseded by 19 rolling re-forecast cycles before real time ever reaches them.

---

## 3. Confirmation of Forecast Horizon Sufficiency

```text
30H_FORECAST_REQUIRED = NO
24H_FORECAST_SUFFICIENT = YES
```

**Formal Confirmation**:
No 30-hour forecast bundle is required. The 24-hour `ForecastBundle` schema (`horizon_hours = 24`) combined with Terminal Reserve coupling at $t=23$ provides complete mathematical closure for EBR lookahead under rolling MPC.
