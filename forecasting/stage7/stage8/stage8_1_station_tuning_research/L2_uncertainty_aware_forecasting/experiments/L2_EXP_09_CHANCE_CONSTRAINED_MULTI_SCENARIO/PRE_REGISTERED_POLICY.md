# POLARIS L2-EXP-09: PRE-REGISTERED MULTI-SCENARIO STOCHASTIC MILP OPTIMIZATION POLICY
**Experiment:** `L2-EXP-09`  
**Classification:** STRICTLY RESEARCH-ONLY — NOT A PRODUCTION PROMOTION  
**Pre-Registration Status:** `PRE_REGISTERED_LOCKED = TRUE`  
**Pre-Registration Timestamp:** `2026-10-04T12:15:00Z`  
**Policy Hash (SHA-256):** `2bb76b1f4ed45299c3ddd77de781ed25fb54c6c084a6fd345124d0b3500e0f88`  
**Held-Out Evaluation Year:** 2024 (173 odd origins: 123 NORMAL, 50 EMERGENCY)

---

## 1. Executive Summary & Research Motivation

In prior experiments within the L2 uncertainty-aware forecasting workspace:
- **L2-EXP-07** demonstrated that static $q_{10}$ conservative planning reduces realized unmet critical load by 93.4% (from 7,994 Wh to 528 Wh across 123 NORMAL origins), but imposes massive operational penalties: +38.2% diesel fuel (+1,598 L) and +92.9% solar curtailment (+2.78 MWh).
- **L2-EXP-08** tested a pre-registered adaptive risk-budget heuristic ($\lambda_t$), which retained 48.94% of the unmet load reduction while avoiding 68.12% of the diesel penalty and 76.01% of the curtailment penalty. However, $\lambda_t$ remained a single-point interpolation forecast that did not expose the optimizer to multiple concurrent scenarios.

**L2-EXP-09** tests explicit uncertainty-aware optimization by answering:
> *"Can GAP19 make dispatch decisions using multiple plausible solar-generation realizations, rather than replacing the point forecast with a single conservative quantile?"*

Per Step 3 of the governance mandate, we implement **Option 1 — Two-Stage Finite-Scenario Stochastic MILP**, with shared first-stage decisions (generator commitment and power, battery operating mode and discharge, and planned charging cap) and second-stage recourse (scenario-dependent solar utilization, realized battery charging, load serving, and reserve shortfall).

---

## 2. Frozen Preconditions & Hash Verification

Before evaluating any 2024 operational data, the following artifacts must match their frozen cryptographic signatures:

| Artifact Name | File Path | Frozen SHA-256 Hash |
| :--- | :--- | :--- |
| **Candidate F Model** | `stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` |
| **SKGBDT q10 Model** | `models/l2_exp_02_skgbdt_q10.joblib` | `4b6cd3655983fc6b14c09402d9ee27d0f52b68d5dd7d3f9b0c7a514e84eed9cb` |
| **SKGBDT q50 Model** | `models/l2_exp_02_skgbdt_q50.joblib` | `104d638aae053b5e9eaff886a6d4639f75eaeb0cea5a86328ddcd6d0f4188a71` |
| **SKGBDT q90 Model** | `models/l2_exp_02_skgbdt_q90.joblib` | `8eb01a6b99b6d939fb01e0dbe58d715e157da8663908e99c93fa9ea80d6833ff` |
| **Feature Matrix 2024** | `stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| **Treatment Fixture 2024**| `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` |
| **Conformal Calibration**| Frozen CQR correction $\hat{q}$ (from 2022 validation set) | `+9.8962 W/m²` |
| **Policy JSON** | `experiments/L2_EXP_09_CHANCE_CONSTRAINED_MULTI_SCENARIO/pre_registered_policy.json` | `2bb76b1f4ed45299c3ddd77de781ed25fb54c6c084a6fd345124d0b3500e0f88` |

---

## 3. Solar Scenario Construction & Weighting

We construct $S = 3$ deterministic solar generation scenarios per origin over horizon $H = 24$ hours ($t \in \{0, \dots, 23\}$):

1. **Scenario 0: Conservative / Low Solar ($s = 0$)**
   - Irradiance (SW_IN): $q_{10\text{,cal}} = \max\left(0, F_t + r_{10, t} - \hat{q}\right)$
   - Causal night enforcement: If $\text{solar\_elevation}_t \le 0^\circ$ or $\text{clearsky\_ghi}_t = 0$, $p_{\text{solar}, t, 0} = 0.0\text{ W}$.
   - PV conversion: $p_{\text{solar}, t, 0} = \text{round}(\text{sw\_in\_to\_power\_w}(q_{10\text{,cal}}), 2)$.
   - Probability Weight: $\pi_0 = 0.25$.

2. **Scenario 1: Central Expectation / Point Forecast ($s = 1$)**
   - Irradiance (SW_IN): Candidate F point forecast $F_t = \max(0, \text{Stage4}_t + \Delta F_t)$.
   - Causal night enforcement: If $\text{solar\_elevation}_t \le 0^\circ$ or $\text{clearsky\_ghi}_t = 0$, $p_{\text{solar}, t, 1} = 0.0\text{ W}$.
   - PV conversion: $p_{\text{solar}, t, 1} = \text{round}(\text{sw\_in\_to\_power\_w}(F_t), 2)$.
   - Inversion guard: $p_{\text{solar}, t, 0} = \min(p_{\text{solar}, t, 0}, p_{\text{solar}, t, 1})$.
   - Probability Weight: $\pi_1 = 0.50$.

3. **Scenario 2: Optimistic / High Solar ($s = 2$)**
   - Irradiance (SW_IN): $q_{90\text{,cal}} = F_t + r_{90, t} + \hat{q}$.
   - Physical upper envelope: $U_t = \max(1.25 \times \text{clearsky\_ghi}_t, F_t)$ (`SIMULATED_RESEARCH_ASSUMPTION`, not production authorized).
   - Upper irradiance: $\text{upper\_sw}_t = \max(q_{10\text{,cal}}, \min(U_t, q_{90\text{,cal}}))$.
   - Causal night enforcement: If $\text{solar\_elevation}_t \le 0^\circ$ or $\text{clearsky\_ghi}_t = 0$, $p_{\text{solar}, t, 2} = 0.0\text{ W}$.
   - PV conversion: $p_{\text{solar}, t, 2} = \text{round}(\text{sw\_in\_to\_power\_w}(\text{upper\_sw}_t), 2)$.
   - Probability Weight: $\pi_2 = 0.25$.

### Weight Derivation Rationale
The weights $\pi = [0.25, 0.50, 0.25]$ represent a symmetric, non-informative discretization of the predictive uncertainty distribution: 50% mass allocated to the central forecast, with 25% allocated to each 10th/90th percentile tail of the calibrated 80% coverage interval. Zero weights were swept or tuned on 2024 data.

---

## 4. Mathematical Formulation of the Stochastic MILP

### 4.1 Decision Variables
Across $S = 3$ scenarios and $H = 24$ timesteps:
- **First-Stage Variables (Scenario-Independent, $7 \times 24 = 168$ variables):**
  - $u_{\text{diesel}}[t] \in \{0, 1\}$: Diesel generator commitment
  - $v_{\text{start}}[t] \in \{0, 1\}$: Diesel generator startup command
  - $p_{\text{diesel}}[t] \in [0, 100\text{ kW}]$: Continuous diesel generation setpoint
  - $u_{\text{chg}}[t] \in \{0, 1\}$: Battery inverter charge mode
  - $u_{\text{dis}}[t] \in \{0, 1\}$: Battery inverter discharge mode
  - $p_{\text{dis}}[t] \in [0, 50\text{ kW}]$: Continuous battery discharge setpoint
  - $p_{\text{chg\_plan}}[t] \in [0, 50\text{ kW}]$: Continuous battery planned charging ceiling
  - $p_{\text{wind\_used}}[t] \in [0, p_{\text{wind}}[t]]$: Continuous wind power dispatched (deterministic wind)

- **Second-Stage Recourse Variables ($11 \times 24 \times 3 = 792$ variables):**
  For each scenario $s \in \{0, 1, 2\}$:
  - $p_{\text{sol\_used}}[t, s] \ge 0$: Solar power consumed
  - $p_{\text{curt\_sol}}[t, s] \ge 0$: Solar power curtailed
  - $p_{\text{curt\_wind}}[t, s] \ge 0$: Wind power curtailed
  - $p_{\text{chg}}[t, s] \ge 0$: Realized battery charge power
  - $p_{\text{served}}[t, s] \ge 0$: Load served
  - $p_{\text{unmet}}[t, s] \ge 0$: Total load deficit
  - $p_{\text{flex}}[t, s] \in [0, 500\text{ W}]$: Flexible load served
  - $E[t+1, s] \in [E_{\text{min}}, E_{\text{max}}]$: Battery energy state of charge
  - $P_{\text{unmet\_crit}}[t, s] \ge 0$: Critical load deficit
  - $s_{J2}[t, s] \ge 0$: Governed reserve shortfall

Total Variables: $168 + 792 = 960$ (96 binary, 864 continuous).

### 4.2 Constraints

1. **Solar Decomposition:**
   $$p_{\text{sol\_used}}[t, s] + p_{\text{curt\_sol}}[t, s] = p_{\text{solar}}[t, s] \quad \forall t, s$$

2. **Wind Decomposition:**
   $$p_{\text{wind\_used}}[t] + p_{\text{curt\_wind}}[t, s] = p_{\text{wind}}[t] \quad \forall t, s$$

3. **Bus-Bar Power Balance:**
   $$p_{\text{sol\_used}}[t, s] + p_{\text{wind\_used}}[t] + p_{\text{dis}}[t] + p_{\text{diesel}}[t] = p_{\text{served}}[t, s] + p_{\text{chg}}[t, s] + p_{\text{flex}}[t, s] \quad \forall t, s$$

4. **Demand Deficit Balance:**
   $$p_{\text{served}}[t, s] + p_{\text{unmet}}[t, s] = p_{\text{demand}}[t] \quad \forall t, s$$

5. **Critical Demand Balance:**
   $$p_{\text{served}}[t, s] + P_{\text{unmet\_crit}}[t, s] = p_{\text{crit\_demand}}[t] \quad \forall t, s$$

6. **Battery Inverter Limits & Exclusivity:**
   $$p_{\text{chg\_plan}}[t] \le P_{\text{chg\_max}} \cdot u_{\text{chg}}[t] \quad \forall t$$
   $$p_{\text{chg}}[t, s] \le p_{\text{chg\_plan}}[t] \quad \forall t, s$$
   $$p_{\text{dis}}[t] \le P_{\text{dis\_max}} \cdot u_{\text{dis}}[t] \quad \forall t$$
   $$u_{\text{chg}}[t] + u_{\text{dis}}[t] \le 1 \quad \forall t$$

7. **Battery Energy Dynamics & SOC Bounds:**
   $$E[t+1, s] = E[t, s] + \left( \eta_{\text{chg}} p_{\text{chg}}[t, s] - \frac{p_{\text{dis}}[t]}{\eta_{\text{dis}}} \right) \Delta t \quad \forall t, s$$
   $$E_{\text{min}} \le E[t+1, s] \le E_{\text{max}} \quad \forall t, s$$

8. **Governed Stage 2 Reserve Envelope (EBR + Terminal Target):**
   $$E[t+1, s] + s_{J2}[t, s] \ge E_{\text{stage2\_target}}[t] + E_{\text{min}} \quad \forall t, s$$

9. **Diesel Operating Envelope & Startup Tracking:**
   $$p_{\text{diesel}}[t] \ge P_{\text{diesel\_min}} \cdot u_{\text{diesel}}[t] \quad \forall t$$
   $$p_{\text{diesel}}[t] \le P_{\text{diesel\_max}} \cdot u_{\text{diesel}}[t] \quad \forall t$$
   $$v_{\text{start}}[t] \ge u_{\text{diesel}}[t] - u_{\text{diesel}}[t-1] \quad \forall t$$

10. **Non-Anticipativity:**
   Shared variables $u_{\text{diesel}}[t], v_{\text{start}}[t], p_{\text{diesel}}[t], u_{\text{chg}}[t], u_{\text{dis}}[t], p_{\text{dis}}[t], p_{\text{wind\_used}}[t], p_{\text{chg\_plan}}[t]$ are strictly identical across scenarios $\forall s$.

### 4.3 Native Lexicographic Multi-Objective Hierarchy

HiGHS evaluates lexicographic multi-objective programs by sorting priority integers in ascending order: **Priority 1 is solved first**, followed by Priority 2, Priority 3, and Priority 4:

$$\begin{aligned}
\text{Priority 1 (Level 1 - Critical Reliability):} & \quad \min \sum_{s=0}^{S-1} \pi_s \sum_{t=0}^{H-1} P_{\text{unmet\_crit}}[t, s] \cdot \Delta t \\
\text{Priority 2 (Level 2 - Reserve Protection):} & \quad \min \sum_{s=0}^{S-1} \pi_s \sum_{t=0}^{H-1} s_{J2}[t, s] \\
\text{Priority 3 (Level 3 - Diesel Efficiency):} & \quad \min \sum_{t=0}^{H-1} \left( m_{\text{fuel}} p_{\text{diesel}}[t] + b_{\text{fuel}} u_{\text{diesel}}[t] + s_{\text{fuel}} v_{\text{start}}[t] \right) \Delta t \\
\text{Priority 4 (Level 4 - Curtailment Minimization):} & \quad \min \sum_{s=0}^{S-1} \pi_s \sum_{t=0}^{H-1} \left( p_{\text{curt\_sol}}[t, s] + p_{\text{curt\_wind}}[t, s] \right) \Delta t
\end{aligned}$$

---

## 5. Non-Anticipativity Verification & Information Barrier

1. **Firewall:** No ground-truth 2024 solar generation ($y_{\text{actual}}$) enters the optimizer. Actual solar is strictly quarantined until post-dispatch replay in `replay_plan_against_actual_solar`.
2. **First-Stage Enforcement:** Controllable commands passed to the EMS hardware execution plan (`diesel_power[t]`, `battery_discharge[t]`, `battery_charge[t]`) are strictly non-anticipative and cannot depend on which scenario materializes.
3. **Replay Validation:** Replay enforces exact committed power commands for diesel and battery discharge; charging is opportunistically realized up to $p_{\text{chg\_plan}}[t]$ if excess renewable energy exists after serving critical load.

---

## 6. Pre-Registration Declaration

```
PRE_REGISTRATION_LOCKED = TRUE
POLICY_HASH = 2bb76b1f4ed45299c3ddd77de781ed25fb54c6c084a6fd345124d0b3500e0f88
EVALUATION_MODE = RESEARCH_ONLY
NO PRODUCTION PROMOTION AUTHORIZED
```
