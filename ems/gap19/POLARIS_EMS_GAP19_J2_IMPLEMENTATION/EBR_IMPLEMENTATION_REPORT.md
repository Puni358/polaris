# EBR Implementation Report

## 1. Technical Specification of EBR Implementation

The governed Emergency Battery Reserve (EBR) target $E_{\text{EBR,target}}[t]$ is implemented in `gap19_highs_native.py` according to the sealed mathematical formulation:

$$E_{\text{EBR,target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{\min(t+5, 23)} P_{\text{crit}}[k] \cdot \Delta t \quad \text{[Watt-hours]}$$

### 1.1 Ingestion of Protected Critical Demand ($P_{\text{crit}}[k]$)
1. The solver inspects `forecast_bundle.demand_critical`.
2. If `demand_critical` is present, $P_{\text{crit}}[k] = \text{demand\_critical.point}[k]$.
3. `P_crit[k]` is strictly validated: $0.0 \le P_{\text{crit}}[k] \le P_{\text{demand}}[k]$. Total station demand $P_{\text{demand}}[k]$ is NEVER reinterpreted as critical demand without explicit authorization.
4. If `demand_critical` is absent, the solver checks for explicit `config["critical_demand_w"]` or `config["critical_demand_ratio"]`.
5. **Failure Mode**: If no protected critical demand information is provided, the solver raises:
   `ValueError("MISSING_GOVERNED_INPUT: Protected critical load trajectory (demand_critical) is missing or unspecified.")`.
   Silently substituting total demand or hardcoded numbers is **STRICTLY PROHIBITED**.

### 1.2 Hourly Indexing & Lookahead Window
- For decision step $t \in [0, 23]$, lookahead window is $W(t) = [t, \min(t+5, 23)]$.
- $k=t$ represents the current forecast hour; $k=t+5$ represents 6 hours ahead from $t$.
- Units: Watt-hours (Wh) after multiplying power (W) by $\Delta t = 1.0\text{h}$ and dividing by $\eta_{\text{dis}} = 0.92$.

### 1.3 Causal Compliance & Rolling-MPC Semantics
- $P_{\text{crit}}[k]$ is sourced strictly from `ForecastBundle` at $t_{\text{now}}$. Future ground truth actuals are NEVER accessed.
- For the executed control step ($k=0$), lookahead covers $W(0) = [0, 5]$ (first 6 hours of forecast bundle), guaranteeing 100% complete lookahead data at every MPC cycle.

---

## 2. Implementation Verification Verdict

```text
EBR_CRITICAL_DEMAND_EXPLICIT = YES
TOTAL_DEMAND_REINTERPRETATION = NO (PROHIBITED)
SURVIVABILITY_WINDOW = 6 HOURS
EBR_CALCULATION_UNITS = WH
MISSING_INPUT_FALLBACK = REJECTED (RAISES EXPLICIT ERROR)
EBR_IMPLEMENTATION_STATUS = PASS
```
