# 30-Hour Horizon Requirement Decision & Proof

## 1. Governance Question & Hypothesis Test

The central decision question evaluated by this audit is:

> **Hypothesis**: "POLARIS optimizes 24 hours, executes one control interval, then re-observes and re-forecasts. EBR requires a 6-hour survivability lookahead. Therefore the optimizer only needs enough causal forecast information to evaluate that lookahead; it does not require a 30-hour optimization horizon."

---

## 2. Rigorous Proof of Hypothesis Validity

### 2.1 Optimization Horizon Analysis ($H_{\text{opt}} = 24\text{h}$)
- **Does the controller need a 30-hour OPTIMIZATION horizon?** `NO.`
- **Proof**:
  1. The MILP decision vector $x$ solves for dispatch variables over $k \in [0, 23]$.
  2. The controller commits ONLY step 0 ($k=0$) to physical execution.
  3. Increasing $H_{\text{opt}}$ from 24h to 30h would expand the decision vector $K \times 30 = 510$ variables, increasing solve time without changing the executed control decision at $k=0$.
  4. Terminal Reserve ($E_{\text{term,target}}$) at $k=23$ guarantees that end-of-horizon stored energy is viable for the next 24-hour cycle.
  5. Therefore, $H_{\text{opt}} = 24\text{ hours}$ is **100% SUFFICIENT**.

### 2.2 Forecast Information Horizon Analysis ($H_{\text{forecast}} = 24\text{h}$)
- **Does the controller need a 30-hour FORECAST INFORMATION horizon?** `NO.`
- **Proof**:
  1. For the executed control step ($k=0$), the 6-hour EBR lookahead window spans $[t_{\text{now}} + 1\text{h}, \, t_{\text{now}} + 6\text{h}]$.
  2. A 24-hour `ForecastBundle` provides forecast points for $[t_{\text{now}} + 1\text{h}, \, t_{\text{now}} + 24\text{h}]$.
  3. The first 6 hours of the 24-hour forecast bundle provide 100% of the evidentiary data required for $s_{\text{EBR}}[0]$.
  4. For unexecuted plan steps at the horizon edge ($k \in [19, 23]$), the EBR lookahead target is coupled to Terminal Reserve ($E_{\text{term,target}}$) or Tail Persistence.
  5. Because the controller re-forecasts every 1 hour, step $k=19$ is never executed from the $t_0$ solve. When real time reaches $t_{19}$, a fresh 24-hour forecast is provided.
  6. Therefore, $H_{\text{forecast}} = 24\text{ hours}$ is **100% SUFFICIENT**.

---

## 3. Minimum Forecast Information Horizon Determination

- **Minimum forecast information required for the EXECUTED control step ($k=0$)**: **6 HOURS** ($t_{\text{now}} + 1\text{h} \dots t_{\text{now}} + 6\text{h}$).
- **Minimum forecast information required for the full 24-hour MPC decision plan with Terminal Reserve coupling**: **24 HOURS** ($t_{\text{now}} + 1\text{h} \dots t_{\text{now}} + 24\text{h}$).
- **Is a 30-hour forecast required?**: `NO.`

---

## 4. Formal Decision Verdicts

```text
30H_OPTIMIZATION_REQUIRED = NO
30H_FORECAST_REQUIRED = NO
MPC_DECISION_HORIZON = 24 HOURS
EBR_SURVIVABILITY_HORIZON = 6 HOURS
FORECAST_INFORMATION_HORIZON = 24 HOURS
SCHEMA_CHANGE_REQUIRED = NO
```

### Rationale Summary
1. **Optimization Horizon**: Remains locked at 24 hours ($H = 24$).
2. **Forecast Bundle Schema**: `ForecastBundle` schema version `1.0.0` (`horizon_hours = 24`) is preserved without modification.
3. **Horizon-Edge Handling**: Unexecuted plan steps $k \in [19, 23]$ are handled cleanly via Terminal Reserve coupling ($E_{\text{term,target}}$) or tail persistence.
4. **Upstream Impact**: Upstream forecasting models (Chronos / Moirai / Stage 8.1) are NOT required to produce 30-hour predictions.
