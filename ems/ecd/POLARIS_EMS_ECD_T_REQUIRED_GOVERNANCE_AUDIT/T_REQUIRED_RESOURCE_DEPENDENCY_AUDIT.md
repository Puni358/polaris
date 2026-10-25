# POLARIS EMS — T_REQUIRED RESOURCE DEPENDENCY AUDIT

## 1. Physical Survivability Model in ECD Prototype

The Emergency Condition Detector (ECD) evaluates station survivability by computing independent endurance horizons for battery storage ($T_{\text{battery}}$) and diesel generation ($T_{\text{diesel}}$) under zero-renewable stress conditions ($P_{\text{solar}}=0, P_{\text{wind}}=0$).

---

## 2. Resource Endurance Formulations

### Battery Endurance Horizon ($T_{\text{battery}}$)
In the prototype fixture, battery endurance is calculated as:
$$T_{\text{battery}} = \frac{C_{\text{bat}} \times (\text{SOC} - \text{SOC}_{\text{min}}) \times \eta_{\text{dis}}}{P_{\text{crit}}}$$

- **Prototype Constants**: $C_{\text{bat}} = 200\text{ kWh}$, $\text{SOC}_{\text{min}} = 20\%$, $\eta_{\text{dis}} = 0.92$.
- **Audit Status**:
  - $C_{\text{bat}}$, $\text{SOC}_{\text{min}}$, $\eta_{\text{dis}}$ are prototype configuration parameters in `battery.yaml`.
  - Temperature effects on battery capacity, dynamic internal resistance, and degradation factors are `NOT_ESTABLISHED_IN_CODE`.
  - Battery survivability calculation is currently **PROTOTYPE-READY ONLY**.

### Diesel Generator Endurance Horizon ($T_{\text{diesel}}$)
In the prototype fixture, diesel endurance is calculated as:
$$T_{\text{diesel}} = \frac{\text{Fuel}_{\text{rem}}}{f_{\text{rate}}(P_{\text{crit}})}$$
where fuel consumption rate is modeled as:
$$f_{\text{rate}}(P) = a + b \cdot P = 5.0\text{ L/h} + 0.00025 \times P_{\text{crit}}\text{ [W]}$$

- At $P_{\text{crit}} = 30\text{ kW}$, $f_{\text{rate}} = 12.5\text{ L/h}$.
- **Audit Status**:
  - Linear fuel consumption model parameters $a=5.0\text{ L/h}$ and $b=0.00025\text{ L/Wh}$ are prototype estimates from `diesel.yaml`.
  - Generator minimum operating load ($P_{\text{gen,min}} = 10\text{ kW}$), physical startup fuel ($0\text{ L}$ in prototype), continuous runtime limits, and maintenance constraints are `ENGINEERING_REQUIRED` / `NOT_ESTABLISHED`.

---

## 3. Decision Rule Evaluation Structure

The prototype ECD decision rule tests both resource endurance horizons against the target horizon $T_{\text{target}}$:

$$\text{Mode} = \begin{cases} 
\text{NORMAL} & \text{if } T_{\text{battery}} \ge T_{\text{target}} \text{ AND } T_{\text{diesel}} \ge T_{\text{target}} \\ 
\text{EMERGENCY} & \text{if } T_{\text{battery}} < T_{\text{target}} \text{ OR } T_{\text{diesel}} < T_{\text{target}} \\ 
\text{UNKNOWN\_INVALID} & \text{if inputs are missing, invalid, or expired} 
\end{cases}$$

- **Target Horizon**: $T_{\text{target}} = T_{\text{required}}$ (in production) or $T_{\text{test}}$ (in logic validation tests).
- **Governance Question**: Should battery endurance and diesel endurance be tested against the **identical** required horizon $T_{\text{required}}$, or should they have independent governed target horizons ($T_{\text{req,battery}}$ vs $T_{\text{req,diesel}}$)? This remains `UNRESOLVED_GOVERNANCE`.

---

## 4. Critical Load Trajectory Dependency

Option D policy specifies dynamic protected critical load $P_{\text{critical}}(t)$.

- **Prototype Assumption**: $P_{\text{crit}} = 30,000\text{ W}$ constant (`SYNTHETIC_ENGINEERING_TEST_PARAMETER`).
- **Production Requirement**: Evaluating endurance over $T_{\text{required}}$ with time-varying demand requires integral trajectory evaluation:
  $$\int_{0}^{T_{\text{battery}}} P_{\text{critical}}(t) \, dt = C_{\text{bat}} \times (\text{SOC} - \text{SOC}_{\text{min}}) \times \eta_{\text{dis}}$$
  $$\int_{0}^{T_{\text{diesel}}} f_{\text{rate}}(P_{\text{critical}}(t)) \, dt = \text{Fuel}_{\text{rem}}$$
- **Audit Status**: $P_{\text{critical}}(t)$ integration logic is `NOT_ESTABLISHED_IN_CODE` and requires formal engineering definition (`ENGINEERING_DEFINITION_REQUIRED`).

---

## 5. Renewable Generation Assumption

- **Prototype Fixture Assumption**: Strict zero-renewable stress scenario ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$).
- **Candidate Production Models**:
  1. Strict zero-renewable baseline ($P_{\text{renewable}}(t) = 0$).
  2. Conservative lower-bound renewable quantile (e.g. P10 exceedance forecast).
  3. Forecasted renewable trajectory over $T_{\text{required}}$.
- **Audit Status**: `RENEWABLE_SURVIVABILITY_ASSUMPTION = GOVERNANCE/ENGINEERING DECISION REQUIRED`. Zero-renewable stress is the established conservative baseline, but production policy must explicitly confirm whether non-zero renewable expectations are permitted.
