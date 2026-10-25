# POLARIS — FORECAST UNCERTAINTY → RISK → EMS INTERFACE DESIGN
## Mathematical Formulation, Interface Architecture, and Falsification Protocol for Risk-Aware Lookahead Microgrid Dispatch

**Document Version:** 1.0.0-RESEARCH-DESIGN  
**Branch:** `POLARIS — NEW RESEARCH BRANCH: FORECAST UNCERTAINTY → RISK → EMS INTERFACE DESIGN`  
**Target Station:** Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.362074° N, 18.738875° E`)  
**Design Phase:** DESIGN ONLY (Zero Code Modifications, Zero Optimizer Runs, Zero Experiment Execution)  
**Governance Status:** STRICT RESEARCH SEPARATION. No modifications to GAP19, EMS, Stage 8.1/Candidate F frozen models, Causal NWP physics, or production configs.  
**Date:** October 05, 2026  

---

## 1. Executive Summary & Problem Framing

### 1.1 The Fundamental Dilemma of POLARIS Lookahead Dispatch
Past research across the POLARIS microgrid EMS has revealed a persistent, recurring failure mode when connecting solar forecasting to energy management:
1. **Candidate F / Stage 8.1 Point Forecaster:** Achieving lower MAE/RMSE on solar irradiance did **not** translate to lower diesel consumption in closed-loop EMS operations. Point forecasts suffer from persistent sub-Arctic over-prediction bias during overcast/transient cloud regimes, causing the optimizer to optimistically defer diesel starts and deplete battery storage, resulting in catastrophic critical-load shortfalls (983.3 kWh unmet across 123 origins in L2-EXP-07 Arm A).
2. **Static Quantile Heuristics ($q_{10}$ Benchmark):** Forcing the optimizer to plan against an unconditioned or calibrated 10th percentile point forecast ($q_{10}$) dramatically slashed critical unmet load by 93.4%, but caused an unacceptable **+38.2% diesel fuel penalty** and a **+92.9% solar curtailment spike** (L2-EXP-07 Arm B). Every daylight hour was pessimistically assumed to experience extreme cloud-cover simultaneously, forcing premature diesel burns that resulted in spilled solar energy once actual irradiance materialized.
3. **Repeated Quantile Tuning as a Dead End:** Successive experiments attempting to relax $q_{10}$—via neural-network adaptive relaxation (L2-EXP-11), horizon risk budgets (L2-EXP-12), or fixed intermediate quantiles ($q=0.15$)—consistently failed the pre-registered critical reliability gate (+23% to +106% higher unmet load than $q_{10}$).
4. **Causal NWP + Physics Failure:** In closed-loop testing (`EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024`), planning against causal MEPS NWP + physics increased diesel fuel by **+20.5% (+1,125.7 L)** over Candidate F baseline, losing in 87 of 123 origins.
5. **Fixed Energy Buffer Reserve (EBR) Interaction:** Forensic analysis revealed that the governed 6-hour EBR reserve (`E_EBR_target = 38.6 kWh`, forcing min SOC to 57.83%) resides at Priority 3 (J2) of the HiGHS lexicographic objective, **above** diesel fuel minimization at Priority 2 (J3). Whenever a forecast is solar-poor or cloud-delayed, GAP19 burns diesel at step 0 to satisfy the unconditional reserve, only for the subsequent solar realization to force massive same-hour curtailment.

### 1.2 The Root Cause: Conflation of Uncertainty, Risk, and Control
The fundamental scientific flaw in all previous iterations is the direct, ad-hoc coupling of raw forecast uncertainty to optimizer inputs:
$$\text{Forecast Uncertainty } (q_{10}) \xrightarrow{\text{Direct Substitution}} \hat{y}_{\text{solar}} \xrightarrow{\text{Optimizer}} \text{Excessive Fuel}$$
or:
$$\text{Rigid Fixed Reserve } (EBR_{6h}) \xrightarrow{\text{Unconditional Constraint}} J_2 \xrightarrow{\text{Priority 3 > Priority 2}} \text{Unnecessary Diesel Startup}$$

A scientifically defensible EMS interface must decouple the pipeline into four distinct, mathematically formal layers:
```
+---------------------------------------------------------------------------------------------------+
|                                 THE SEPARATED INTERFACE PIPELINE                                  |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ LAYER 1: FORECAST ]                                                                            |
|      Point trajectory: y_hat_t, t in {1..24} (Class-A Causal NWP / Stage 8.1)                     |
|                                     |                                                             |
|                                     v                                                             |
|  [ LAYER 2: UNCERTAINTY ]                                                                         |
|      Temporal error process: e_t = phi * e_{t-1} + epsilon_t (AR(1) with non-Gaussian kurtosis)   |
|      Scale conditioning: sigma_t = sigma(clearsky_ghi_t, solar_elevation_t, cloud_frac_t)         |
|                                     |                                                             |
|                                     v                                                             |
|  [ LAYER 3: PHYSICAL RISK ]                                                                       |
|      Cumulative deficit distribution: Delta E_{crit, k} conditional on SOC_0, P_crit, P_diesel    |
|      Distinction: 90% solar interval != 10% battery reserve != 10% critical failure               |
|                                     |                                                             |
|                                     v                                                             |
|  [ LAYER 4: EMS CONTROL INTERFACE ]                                                               |
|      Dynamic reserve requirement trajectory: R_k^{dyn}(t) or Chance-Constrained Battery Trajectory |
|      Insertion Point: GAP19 Layer C (J2 Reserve Envelope), replacing unconditional EBR             |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Evidence Base & Audit Synthesis

To ground this design in empirical reality, we synthesize findings from the frozen codebase, previous audits, and closed-loop forensic reports.

### 2.1 Summary of Verified Empirical Facts vs Inferred Hypotheses

| Fact / Finding | Classification | Source Artifact | Forensic Implication |
|---|:---:|---|---|
| First-order AR(1) temporal error structure ($\phi \approx 0.6386$, PACF cuts off at lag 1) | **VERIFIED** | `FORECAST_ERROR_TRAJECTORY_AUDIT.md` | Hourly solar errors are strongly persistent; independent hourly quantiles are mathematically invalid. |
| Non-Gaussian AR(1) innovations (excess kurtosis $\kappa = 3.4452$, Ljung-Box $p < 10^{-6}$) | **VERIFIED** | `AR1_INNOVATION_DIAGNOSTICS.csv` | Trajectory error distribution has fat tails; Gaussian confidence intervals severely underestimate multi-hour shortfall. |
| Consecutive shortfall runs average 4.25 hours (max 19h; 48.8% last $\ge 4\text{ h}$) | **VERIFIED** | `FORECAST_ERROR_TRAJECTORY_AUDIT.md` | Solar deficits do not oscillate; cloud systems create multi-hour sustained energy starvation. |
| Intraday maximum shortfall timing: 40.5% occurs midday ($k \in [5..18]$), not at sunset | **VERIFIED** | `FORECAST_ERROR_TRAJECTORY_AUDIT.md` | Single terminal reserve ($t=23$) is inadequate; intraday storage reserves are required. |
| Clear-sky normalization eliminates 92x seasonal raw variance ratio | **VERIFIED** | `FORECAST_ERROR_TRAJECTORY_AUDIT.md` | Raw Wh/m² error envelopes cannot transfer across seasons; clear-sky scaling is essential. |
| Pointwise cross-year coverage transfers ($92.96\%\text{--}94.98\%$ on blind 2023) | **VERIFIED** | `TRAJECTORY_REQUALIFICATION_REPORT.md` | Conditioning on Class-A states stabilizes hourly variance. |
| Simultaneous 13h trajectory coverage collapsed ($81.68\%\text{--}86.45\%$ on blind 2023) | **VERIFIED** | `TRAJECTORY_COVERAGE_COMPARISON.csv` | Single-multiplier static envelopes cannot guarantee joint multi-hour trajectory coverage under climate drift. |
| Static $q_{10}$ slashes unmet load 93.4% but costs +38.2% fuel and +92.9% curtailment | **VERIFIED** | `L2_EXP_07_RESULTS.md` | Point forecast replacement overprotects and destroys economic efficiency. |
| Causal NWP closed-loop increases diesel +20.5% (+1,125.7 L) over Candidate F | **VERIFIED** | `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` | Causal NWP under-forecasts solar; rigid EBR forces diesel charging at step 0. |
| EBR reserve is tight at step 0 in 100% of origins; removing EBR cuts fuel 68.4% | **VERIFIED** | `EBR_BRANCH_FINAL_SYNTHESIS.md` | The reserve constraint, not terminal target, forces premature diesel starts. |
| EBR-OFF increases total unmet load by +16.9% and fails reliability gate in 101/123 origins | **VERIFIED** | `EBR_ABLATION_123_REPORT.md` | Completely removing reserves is unacceptable; an active protection reserve is necessary. |
| GAP19 HiGHS lexicographic hierarchy places J2 (Reserve) at Priority 3 > J3 (Fuel) at Priority 2 | **VERIFIED** | `gap19_highs_native.py` (lines 366-385) | Optimizer will burn diesel to satisfy any reserve requirement before minimizing fuel. |
| GAP19 natively accepts 24-element dynamic reserve array without code modification | **VERIFIED** | `gap19_highs_native.py` (lines 118-124) | Clean insertion point exists via `config["ebr_target_wh"]` or `station_state.ebr_target_wh_override`. |
| Current research harness uses synthetic wind and synthetic load profiles | **VERIFIED** | `system/config/loads.yaml`, `EBR_BRANCH_FINAL_SYNTHESIS.md` | Harness results cannot be treated as real-world microgrid proof; wind error is an artifact. |
| Missing solar horizons $k \in [20..24]$ in historical archive | **BLOCKED** | `FINAL_STAGE8_1_FORECASTING_FREEZE.md` | Historical MEPS wind/irradiance terminates at $H=19$ for polar darkness. |
| Real-time ground sensor context (`ctx_*`) lacking telemetry latency modeling | **BLOCKED** | `CROSS_YEAR_ERROR_STABILITY_AUDIT.md` | Class-B features quarantined from non-anticipative forecasting. |

---

## 3. The Critical Design Question: Mathematical Bridge

### 3.1 Why a 90% Solar Interval $\ne$ 10% Battery Reserve $\ne$ 10% Probability of Critical Deficit

A persistent source of confusion in heuristic EMS design is the assumption that statistical forecast intervals map directly to storage reserves or reliability margins. We formally demonstrate why this equivalence is mathematically false.

#### 1. Pointwise Coverage vs Cumulative Energy Integration
Let $y_t$ be realized solar generation and $\hat{y}_t$ be the point forecast. A nominal $90\%$ lower bound $q_{10, t}$ satisfies:
$$\mathbb{P}(y_t \ge q_{10, t}) = 0.90 \quad \forall t$$
However, battery storage is an energy integrator across time:
$$E_{t+k} = E_t + \sum_{j=1}^k \left( \eta_{chg} P_{chg, t+j} - \frac{1}{\eta_{dis}} P_{dis, t+j} \right) \Delta t$$
Because forecast errors $e_t = \hat{y}_t - y_t$ follow an AR(1) process with autocorrelation $\phi \approx 0.6386$, errors compound over lookahead prefix $k$:
$$C_k = \sum_{j=1}^k e_{t+j}$$
The variance of cumulative error $C_k$ is not $k \sigma^2$ (as in independent random walks), but:
$$\text{Var}(C_k) = \sum_{j=1}^k \sum_{l=1}^k \text{Cov}(e_{t+j}, e_{t+l}) = \sigma^2 \left[ k + 2 \sum_{j=1}^{k-1} (k - j) \phi^j \right] \gg k \sigma^2$$
For $\phi = 0.64$ and $k=6$, $\text{Var}(C_6) \approx 4.8 \times (6 \sigma^2) \approx 28.8 \sigma^2$.  
Consequently, an hourly 90% quantile envelope fails to cover the cumulative trajectory ($1 - 0.90^k \ll 0.10$). Conversely, assuming worst-case $q_{10}$ at every hour simultaneously corresponds to a joint probability of $\ll 0.01\%$, imposing massive, unnecessary conservatism.

#### 2. Microgrid Physical Buffering and Diesel Schedulability
Even if cumulative solar shortfall $\Delta C_k$ occurs, battery reserve is **not** the only balancing asset:
- **Diesel Generation:** The generator has maximum capacity $P_{diesel}^{max} = 100\text{ kW}$ and minimum runtime requirements. Over a $k$-hour deficit window, diesel can supply up to $k \cdot P_{diesel}^{max} \cdot \Delta t$ of energy, provided it is committed in advance.
- **Battery Usable Headroom:** Existing energy above the minimum safety floor, $E_t - E_{min}$, acts as an initial shock absorber. If $E_t = 80\%$ ($160\text{ kWh}$) and $E_{min} = 20\%$ ($40\text{ kWh}$), the battery has $120\text{ kWh}$ of available energy—sufficient to power 10.3 hours of critical load ($11.6\text{ kW}$) with zero solar and zero diesel!
- **Non-Critical Load Shedding:** Total demand $P_{dem}$ contains deferrable and curtailable components. In an emergency, dropping non-critical demand incurs zero critical reliability penalty.

#### 3. Formal Definition of Critical-Energy Deficit
Let critical load demand over lead time $j \in \{1..k\}$ be $P_{crit, t+j}$. The physical critical-energy deficit over lookahead prefix $k$ is:
$$\Delta E_{crit, k} = \max \left( 0, \; \sum_{j=1}^k \frac{P_{crit, t+j}}{\eta_{dis}} \Delta t - (E_t - E_{min}) - \sum_{j=1}^k \left[ \eta_{pv} y_{t+j} + y_{wind, t+j} + P_{diesel, t+j}^{max} \right] \Delta t \right)$$
Notice that:
$$\mathbb{P}(\text{Critical Failure in } k\text{ hours}) = \mathbb{P}(\Delta E_{crit, k} > 0)$$
This probability is a non-linear function of:
$$\mathbb{P} \left( \sum_{j=1}^k \eta_{pv} y_{t+j} \Delta t < \sum_{j=1}^k \frac{P_{crit, t+j}}{\eta_{dis}} \Delta t - (E_t - E_{min}) - \sum_{j=1}^k [y_{wind, t+j} + P_{diesel, t+j}^{max}] \Delta t \right)$$

#### Mathematical Bridge Summary:
1. Sizing reserve purely to solar uncertainty $\sigma_{solar}$ ignores initial battery state $E_t$ and diesel capacity $P_{diesel}^{max}$.
2. If battery state $E_t$ is already high, solar uncertainty poses **zero** critical risk.
3. If battery state $E_t$ is low and diesel startup requires notice, solar uncertainty translates directly into critical risk.
4. Therefore, the required reserve is **not** a function of forecast uncertainty alone, but a function of **state-dependent shortfall survivability**.

---

## 4. Evaluation of Candidate Interface Formulations

We formulate and analyze six candidate interfaces across the design spectrum, establishing their mathematical definitions, advantages, and empirical limitations.

```
+---------------------------------------------------------------------------------------------------------+
|                                    CANDIDATE INTERFACE FORMULATIONS                                     |
+------+---------------------------+-----------------------------------+----------------------------------+
| Code | Formulation Name          | Mathematical Nature               | Empirical Status                 |
+------+---------------------------+-----------------------------------+----------------------------------+
| A    | Static Quantile (q10)     | Point replacement: y_hat = q10    | REJECTED (High fuel/curtailment) |
| B    | Fixed Reserve (EBR 6h)    | Constant constraint: E >= EBR     | REJECTED (Unconditional diesel)  |
| C    | Cumulative Shortfall Risk | Autoregressive cumulative bound   | SCIENTIFICALLY SOUND (Offline)   |
| D    | Chance-Constrained Res.   | State-aware probabilistic reserve | RECOMMENDED PRIMARY CANDIDATE    |
| E    | Scenario-Based Multi-MILP | Scenario tree with weights        | REJECTED (HiGHS priority defect) |
| F    | Economic Risk Pricing     | Marginal cost vs risk penalty     | THEORETICAL BENCHMARK            |
+------+---------------------------+-----------------------------------+----------------------------------+
```

---

### Candidate A: Static Quantile (Existing $q_{10}$ Benchmark)
- **Formulation:**  
  Replace the solar generation point vector in the forecast bundle with an empirical lower quantile:
  $$\hat{y}_{t+j}^{plan} = \hat{y}_{t+j}^{q10} = \max(0, \hat{y}_{t+j}^{F} - \Delta_{q10, j})$$
- **GAP19 Entry:** `forecast_bundle.solar_generation.point = y_q10`
- **Why It Fails:**
  - Treats each hour as an independent failure, assuming a 1-in-10 year simultaneous cloud storm across all 24 hours.
  - Forces early morning diesel dispatch to compensate for phantom deficits.
  - Empirically proven in L2-EXP-07 to burn **+38.18% more fuel** (+2,012 L) and cause **+92.87% more curtailment** (+4,262 kWh).

---

### Candidate B: Fixed Reserve (Existing Governed EBR)
- **Formulation:**  
  Maintain an unconditional 6-hour lookahead critical survivability buffer:
  $$E_{t+k} \ge E_{min} + \frac{1}{\eta_{dis}} \sum_{j=t+k}^{t+k+5} P_{crit, j} \Delta t \quad \approx 40\text{ kWh} + 75.65\text{ kWh} = 115.65\text{ kWh} \; (57.83\% \text{ SOC})$$
- **GAP19 Entry:** Constrained at Layer C, Priority 3 (J2 objective).
- **Why It Fails:**
  - Completely blind to incoming solar generation. Even on pristine clear-sky days with $50\text{ kW}$ solar expected in 2 hours, if current SOC is $50\%$, GAP19 dispatches diesel immediately at step 0 to satisfy J2 before minimizing fuel in J3.
  - Empirically proven in causal NWP closed-loop testing to cause a **+20.5% fuel penalty**. Removing it cuts fuel by 68.4%, but completely eliminating it drops critical reliability below acceptable limits.

---

### Candidate C: Cumulative Shortfall Risk (AR(1) Multi-Horizon Envelopes)
- **Formulation:**  
  Model Candidate F forecast errors via an AR(1) process with clear-sky scaling:
  $$e_{t+j} = \mu(x_{t+j}) + \phi \cdot (e_{t+j-1} - \mu(x_{t+j-1})) + \epsilon_{t+j}, \quad \epsilon_{t+j} \sim \mathcal{D}(0, \sigma_j^2)$$
  where $\sigma_j = \alpha_0 + \alpha_1 \cdot \text{clearsky\_ghi}_{t+j}$.  
  Compute the distribution of cumulative solar shortfall over lookahead $k$:
  $$C_k = \sum_{j=1}^k e_{t+j}$$
  The $1-\epsilon$ upper envelope of cumulative solar shortfall is:
  $$U_k(1-\epsilon) = \mathbb{E}[C_k \mid x_t] + z_{1-\epsilon} \cdot \sqrt{\text{Var}(C_k \mid x_t)}$$
- **Evaluation:**  
  While mathematically rigorous, Candidate C focuses strictly on the **solar error distribution**. It does not incorporate the battery's current state $E_t$ or diesel ramp capabilities. If used directly as a reserve, it overprotects when the battery is full.

---

### Candidate D: Chance-Constrained / Probabilistic Dynamic Reserve (RECOMMENDED)
- **Formulation:**  
  Derive a state-dependent, dynamic reserve requirement trajectory $R_k^{dyn}(t)$ such that the probability of critical-load deficit over any lookahead prefix $k \in \{1..24\}$ is strictly bounded by risk tolerance $\epsilon$ (e.g. $\epsilon = 0.01$):
  $$\mathbb{P} \left( \Delta E_{crit, k} > 0 \right) \le \epsilon \quad \forall k \in \{1..24\}$$
  Substituting the microgrid energy balance:
  $$\mathbb{P} \left( \sum_{j=1}^k \eta_{pv} y_{t+j} \Delta t < \sum_{j=1}^k \frac{P_{crit, t+j}}{\eta_{dis}} \Delta t - (E_t - E_{min}) - \sum_{j=1}^k [y_{wind, t+j} + P_{diesel, t+j}^{sched}] \Delta t \right) \le \epsilon$$
  Let $y_{t+j} = \hat{y}_{t+j} - e_{t+j}$. The condition becomes a constraint on the cumulative solar shortfall $C_k = \sum_{j=1}^k e_{t+j}$:
  $$\mathbb{P} \left( \eta_{pv} \Delta t \cdot C_k > (E_t - E_{min}) + \sum_{j=1}^k \left[ \eta_{pv} \hat{y}_{t+j} + y_{wind, t+j} + P_{diesel}^{sched} - \frac{P_{crit, t+j}}{\eta_{dis}} \right] \Delta t \right) \le \epsilon$$
  This yields an exact, closed-form **Dynamic Reserve Requirement** $R_k^{dyn}(t)$ that must be held in the battery at step $t+k$:
  $$R_k^{dyn}(t) = \max \left( R_{base}^{surv}, \; \eta_{pv} \Delta t \cdot Q_{1-\epsilon}(C_k \mid x_t) + \sum_{j=1}^k \frac{P_{crit, t+j}}{\eta_{dis}} \Delta t - \sum_{j=1}^k \eta_{pv} \hat{y}_{t+j} \Delta t - \sum_{j=1}^k y_{wind, t+j} \Delta t \right)$$
  where:
  - $R_{base}^{surv}$ is a minimal emergency survivability floor (e.g. 1.0 hour of critical load = $12.6\text{ kWh}$, maintaining $\sim 26.3\%\text{ SOC}$) protecting against sudden diesel generator mechanical trip.
  - $Q_{1-\epsilon}(C_k \mid x_t)$ is the conditional quantile of cumulative solar shortfall derived from the calibrated AR(1) clear-sky model.
- **Why Candidate D Is Superior:**
  1. **Forecast-Aware:** When abundant solar is forecasted ($\sum \hat{y}_{t+j} \gg P_{crit}$), the required reserve shrinks down to $R_{base}^{surv}$, preventing unnecessary step-0 diesel burning.
  2. **Uncertainty-Aware:** When cloud cover creates large forecast uncertainty $Q_{1-\epsilon}(C_k)$, the reserve automatically expands to cover the worst-case cumulative deficit.
  3. **State-Aware:** If the battery already holds sufficient energy ($E_t \ge R_k^{dyn}$), no diesel is dispatched.
  4. **Drop-in Compatible with GAP19:** Directly populates the 24-element vector `E_stage2_target[t]`, requiring **zero** modifications to GAP19 MILP constraints or solver logic.

---

### Candidate E: Distribution / Scenario-Based Multi-MILP
- **Formulation:**  
  Sample $S$ discrete solar realization trajectories $\{y_t^{(s)}\}_{s=1}^S$ from the generative AR(1) innovation model and solve a two-stage stochastic program:
  $$\min \sum_{s=1}^S \pi_s \left[ J_1^{(s)} + J_2^{(s)} + J_3^{(s)} + J_4^{(s)} \right]$$
  subject to first-stage non-anticipativity ($P_{diesel, 0}, P_{chg, 0}, P_{dis, 0}$ identical across all $s$).
- **Why It Is Rejected:**
  - Evaluated extensively in L2-EXP-09 and L2-EXP-10. Multi-scenario MILP in HiGHS introduces severe lexicographic priority inversions (J4 curtailment chasing depleted battery storage prematurely on Origin 77, causing SOC floor breach to 19.61%).
  - Increases solve time from $0.4\text{ s}$ to up to $74.5\text{ s}$, creating real-time dispatch timeout risks.
  - Failed the pre-registered critical reliability gate (+23.6% unmet load over $q_{10}$ in EXP-10).

---

### Candidate F: Economic Risk Pricing Interface
- **Formulation:**  
  Eliminate the hard reserve constraint $J_2$. Instead, introduce an economic risk penalty into the objective function based on the Expected Value of Critical Shortfall:
  $$\min \quad J_{\text{economic}} = \text{Cost}(P_{diesel}) + \text{Cost}(P_{curt}) + \text{Degradation}(E_{batt}) + \lambda_{crit} \cdot \mathbb{E} \left[ \Delta E_{crit, k}(E_{batt}) \right]$$
  where $\lambda_{crit} = \$10.00 / \text{Wh}$ is the Value of Lost Load (VOLL).
- **Evaluation:**  
  While economically optimal in unconstrained theory, Candidate F destroys the strict lexicographic safety guarantee of GAP19 (where critical load is protected at Priority 4 with zero economic compromise). Under numerical scaling, linear solvers will trade small critical deficits for large fuel savings. It is preserved as a theoretical benchmark, but rejected for operational implementation.

---

## 5. Detailed Specification of Recommended Interface (Candidate D)

### 5.1 Mathematical Formulation of the Dynamic Reserve Trajectory

Let dispatch origin be $t$. For each lookahead horizon step $k \in \{1, \dots, 24\}$:

#### 1. Conditional Mean Forecast Error Trajectory
$$\hat{e}_{t+k \mid t} = \mu(x_{t+k}) \cdot \left(1 - \phi^k\right) + \phi^k \cdot e_t^{obs}$$
where:
- $\phi = 0.6386$ is the frozen AR(1) persistence parameter.
- $e_t^{obs}$ is the most recently observed forecast error at issuance (set to $0.0$ at $00:00\text{ UTC}$ origin if sensor telemetry is unavailable).
- $\mu(x_{t+k})$ is the causal regime bias shift conditioned on forecast cloud cover:
  $$\mu(x) = \begin{cases} +22.10\text{ W/m}^2 & \text{if } fc\_cloud\_cover < 0.20 \text{ (Clear)} \\ +5.10\text{ W/m}^2 & \text{if } 0.20 \le fc\_cloud\_cover \le 0.80 \text{ (Partial)} \\ -13.30\text{ W/m}^2 & \text{if } fc\_cloud\_cover > 0.80 \text{ (Overcast)} \end{cases}$$

#### 2. Cumulative Error Variance Scale
$$\sigma_{C, k}^2 = \sum_{j=1}^k \left( \sum_{l=j}^k \phi^{l-j} \right)^2 \sigma_{innov}^2(x_{t+j})$$
where innovation standard deviation scales linearly with clear-sky GHI:
$$\sigma_{innov}(x_{t+j}) = 24.03 + 0.1464 \cdot \text{clearsky\_ghi}_{t+j} \quad [\text{W/m}^2]$$

#### 3. Empirical Cumulative Shortfall Quantile
Because innovations exhibit excess kurtosis ($\kappa = 3.4452$), we apply the calibrated nonconformity quantile multiplier $q_{cal}(1-\epsilon)$ estimated on the calibration dataset:
$$Q_{1-\epsilon}(C_k) = \sum_{j=1}^k \hat{e}_{t+j \mid t} + q_{cal}(1-\epsilon) \cdot \sigma_{C, k}$$

#### 4. Dynamic Critical Reserve Requirement $R_k^{dyn}(t)$
Convert irradiance shortfall into electrical energy deficit via PV array parameters ($A_{pv} = 300\text{ m}^2$, $\eta_{mod} = 0.20$, $PR = 0.85$, yielding $K_{pv} = 51.0\text{ W} / (\text{W/m}^2)$):
$$\Delta E_{sol, k}^{risk} = K_{pv} \cdot \Delta t \cdot \max\left(0, \; Q_{1-\epsilon}(C_k)\right) \quad [\text{Wh}]$$
The net critical reserve target for step $k$ is:
$$E_{target}[k] = \max \left( R_{base}^{surv}, \; \Delta E_{sol, k}^{risk} + \sum_{j=1}^k \frac{P_{crit, t+j}}{\eta_{dis}} \Delta t - \sum_{j=1}^k \left[ P_{pv, t+j}^{point} + P_{wind, t+j}^{point} \right] \Delta t \right)$$
To avoid horizon-edge depletion, we enforce terminal alignment at $k=24$:
$$E_{stage2\_target}[k] = \begin{cases} \min\left(E_{target}[k], \; E_{batt}^{usable}\right) & \text{for } k \in \{1, \dots, 23\} \\ \max\left(E_{target}[23], \; E_{term}^{governed}\right) & \text{for } k = 24 \end{cases}$$

---

### 5.2 GAP19 Integration Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                 GAP19 HIGHS INTEGRATION ARCHITECTURE                              |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   station_state              forecast_bundle             loads.yaml                               |
|        |                           |                          |                                   |
|        v                           v                          v                                   |
|   [ CANDIDATE D: PROBABILISTIC DYNAMIC RESERVE CALCULATOR ]                                       |
|        |                                                                                          |
|        | Computes 24-element dynamic reserve trajectory:                                          |
|        | E_stage2_target = [E_0, E_1, ..., E_23]                                                  |
|        |                                                                                          |
|        v                                                                                          |
|   GAP19 Optimizer Ingestion:                                                                      |
|   config["ebr_target_wh"] = E_stage2_target (24-element array)                                    |
|        |                                                                                          |
|        v                                                                                          |
|   system/optimization/implementations/gap19_highs_native.py                                        |
|   Line 118-124: Directly ingests 24-element array into ebr_target_wh_list                         |
|   Line 298-305: Enforces Layer C Constraints:                                                     |
|                 E_next[t] + s_J2[t] >= E_stage2_target[t] + min_e_wh                              |
|   Line 366-385: Solves Lexicographic Hierarchy:                                                  |
|                 Priority 4: J1 (Critical Unmet Wh) == 0                                           |
|                 Priority 3: J2 (Dynamic Reserve Slack s_J2) -> Minimized                          |
|                 Priority 2: J3 (Diesel Fuel Liters) -> Minimized                                  |
|                 Priority 1: J4 (Curtailment Wh) -> Minimized                                      |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

#### Verification of Zero Production Code Modification:
In `system/optimization/implementations/gap19_highs_native.py` (lines 118–124):
```python
elif "ebr_target_wh" in config and config["ebr_target_wh"] is not None:
    ebr_cfg = config["ebr_target_wh"]
    if isinstance(ebr_cfg, (list, tuple)) and len(ebr_cfg) == 24:
        ebr_target_wh_list = [float(v) for v in ebr_cfg]
```
GAP19 **already contains** native support for receiving a 24-element custom reserve trajectory!  
No modifications to GAP19 MILP constraints, variable indexing, or solver options are required.

#### Replace, Augment, or Bypass?
- **DECISION:** **REPLACE** the rigid 6-hour static formula with the dynamic trajectory $E_{stage2\_target}[t]$ inside the research experiment harness.
- **RATIONALE:** Forensic analysis proved that fixed EBR is the direct cause of step-0 diesel burning (+20.5% fuel). Augmenting EBR (adding uncertainty on top of 6-hour fixed critical load) would exacerbate diesel over-consumption. Bypassing EBR entirely (EBR-OFF) causes critical reliability collapse (-16.9% unmet load). Replacing the static formula with a state-aware dynamic reserve preserves critical protection while eliminating spurious diesel commitment.

---

## 6. Causality and Data Provenance Audit

Strict non-anticipativity is mandatory. Every input utilized by Candidate D is audited below:

| Variable / Parameter | Source | Class | Real-Time Causal Availability | Status |
|---|---|:---:|---|:---:|
| Solar Elevation Angle ($\theta_{el}$) | Deterministic astronomical ephemeris (PVLIB) | Class A | Available at forecast issuance | **VERIFIED** |
| Clear-Sky Irradiance ($GHI_{cs}$) | Deterministic clear-sky model (Ineichen) | Class A | Available at forecast issuance | **VERIFIED** |
| NWP Cloud Cover ($fc\_cloud$) | Causal MEPS NWP 18Z run | Class A | Available at forecast issuance | **VERIFIED** |
| Point Forecast ($\hat{y}_{t+k}$) | Frozen Stage 8.1 37-feature model | Class A | Available at forecast issuance | **VERIFIED** |
| Station Battery Energy ($E_t$) | SCADA telemetry at origin | Class A | Available at forecast issuance | **VERIFIED** |
| Diesel Running State | SCADA telemetry at origin | Class A | Available at forecast issuance | **VERIFIED** |
| AR(1) Parameters ($\phi, \mu, \sigma$) | Pre-fit on 2020–2021 training dataset | Static | Frozen prior to evaluation | **VERIFIED** |
| Multiplier $q_{cal}(1-\epsilon)$ | Calibrated on 2022 validation dataset | Static | Frozen prior to evaluation | **VERIFIED** |
| Recent Error Observation ($e_t^{obs}$) | Real-time pyranometer vs forecast | Class B | Quarantined in Step 1 (set to 0.0) | **BLOCKED** |
| Realized Pyranometer ($y_{t+k}$) | Future ground station actual | Class C | Forbidden during planning | **STRICTLY BLOCKED** |
| Realized Wind / Load actuals | Future simulation realization | Class C | Forbidden during planning | **STRICTLY BLOCKED** |

---

## 7. Falsification Validation Protocol (Pre-Registered Experiment Design)

To prevent circular tuning and self-fulfilling confirmation bias, we pre-register the complete validation protocol that would falsify this interface.

### 7.1 Dataset Chronological Splitting & Quarantine Protocol
To prevent data contamination, we prohibit reusing the 2024 operational fixture for model calibration or reserve tuning:
1. **Model Estimation Period (2020–2021, 731 origins):**  
   Fit AR(1) persistence $\phi = 0.6386$, baseline clear-sky variance scaling coefficients $\alpha_0, \alpha_1$, and causal cloud bias shifts.
2. **Conformal Risk Calibration Period (2022, 365 origins):**  
   Calibrate quantile multiplier $q_{cal}(1-\epsilon)$ at nominal risk levels $\epsilon \in \{0.05, 0.02, 0.01\}$. Freeze all parameters into a tamper-proof SHA-256 JSON manifest.
3. **Genuinely Untouched Blind Evaluation Period (2025 Blind Dataset, 364 origins):**  
   Evaluate across the 364 origins of the newly created 2025 blind dataset (`stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv`). **Zero parameters may be tuned or adjusted on 2025 data.**

### 7.2 Experimental Arms (Closed-Loop Reoptimization Harness)
Every origin is simulated in full closed-loop receding-horizon control across 24 hours:

| Arm Code | Name | Solar Forecast Input | Reserve Interface | Reoptimization | Realization Layer |
|:---:|---|---|---|:---:|---|
| **Arm 0** | Candidate F Baseline | Stage 8.1 Point | Governed Static EBR (6h) | Hourly Receding | Exact Busbar Replay |
| **Arm 1** | Static Quantile ($q_{10}$) | Stage 8.1 $q_{10}$ | Governed Static EBR (6h) | Hourly Receding | Exact Busbar Replay |
| **Arm 2** | Candidate D (Proposed) | Stage 8.1 Point | **Dynamic Risk Reserve $R_k^{dyn}(t)$** | Hourly Receding | Exact Busbar Replay |
| **Arm 3** | Perfect Foresight | Actual Solar | Zero Reserve | Hourly Receding | Exact Busbar Replay |

### 7.3 Primary Operational Metrics & Evaluation Gates

1. **Safety & Reliability Gate (FAIL-CLOSED):**
   - Realized Critical Unmet Energy:
     $$\Delta_{\text{unmet}} = \text{Unmet}_{\text{Arm 2}} - \text{Unmet}_{\text{Arm 1}} \le 0.05 \cdot \text{Unmet}_{\text{Arm 1}}$$
   - Absolute Critical Reliability: $\ge 99.80\%$.
   - SOC Floor Excursions: Exactly **0** instances of realized $SOC < 20.0\%$.
2. **Economic Resource Efficiency Metrics:**
   - Realized Diesel Fuel: $\Delta_{\text{fuel}} = \text{Fuel}_{\text{Arm 2}} - \text{Fuel}_{\text{Arm 1}}$ (Target: $\ge 15\%$ fuel reduction relative to Arm 1).
   - Renewable Curtailment: $\Delta_{\text{curt}} = \text{Curt}_{\text{Arm 2}} - \text{Curt}_{\text{Arm 1}}$ (Target: $\ge 30\%$ curtailment reduction relative to Arm 1).
   - Battery Cycling: Equivalent Full Cycles (EFC) $\le \text{EFC}_{\text{Arm 1}}$.
3. **Statistical Significance Testing:**
   - Paired Wilcoxon signed-rank test across all common origins ($p < 0.01$).
   - 10,000-sample BCa bootstrap confidence interval for mean paired fuel savings excluding zero.

---

### 7.4 Falsification / Decision Criteria

```
+----------------------------------------------------------------------------------------------------+
|                                    OFFICIAL DECISION MATRIX                                        |
+---------------+------------------------------------------------------------------------------------+
| OUTCOME       | QUANTITATIVE CRITERIA                                                              |
+---------------+------------------------------------------------------------------------------------+
| PASS          | 1. Critical Reliability >= 99.80% (matches Arm 1 within 5% tolerance).             |
| (Validated)   | 2. Zero SOC floor excursions (< 20.0%).                                            |
|               | 3. Diesel fuel consumption is statistically significantly LOWER than Arm 1         |
|               |    (paired Wilcoxon p < 0.01, mean reduction >= 10.0%).                            |
|               | 4. Solar curtailment is reduced by >= 25.0% relative to Arm 1.                     |
+---------------+------------------------------------------------------------------------------------+
| FAIL          | 1. Critical unmet load exceeds Arm 1 by > 10.0%, OR reliability < 99.75%.          |
| (Falsified)   | 2. ANY realized SOC floor violation (< 20.0%).                                     |
|               | 3. Diesel fuel consumption shows no statistically significant reduction vs Arm 1.  |
+---------------+------------------------------------------------------------------------------------+
| INCONCLUSIVE  | Fuel is reduced but critical unmet load falls in the ambiguous [100%, 110%] band;  |
|               | or statistical power is inadequate (Wilcoxon p >= 0.05).                           |
+---------------+------------------------------------------------------------------------------------+
```

---

## 8. Summary of Status Classifications

- **VERIFIED:**
  - AR(1) temporal correlation structure ($\phi = 0.6386$) and non-Gaussian fat-tailed innovations ($\kappa = 3.4452$).
  - Clear-sky normalization eliminates cross-season variance drift ($92\times$ raw vs $0.19\times$ normalized).
  - Unconditional 6-hour EBR causes step-0 diesel dispatch (+20.5% fuel penalty in Causal NWP closed-loop).
  - Static $q_{10}$ achieves 99.81% reliability at the cost of +38.2% diesel fuel and +92.9% curtailment.
  - Multi-scenario stochastic MILP introduces lexicographic priority defects in HiGHS.
  - GAP19 accepts 24-element custom reserve arrays natively via existing configuration contracts.
- **INFERRED:**
  - Dynamic risk-based reserve sizing $R_k^{dyn}(t)$ can capture $q_{10}$-level critical protection while cutting diesel fuel by $\ge 15\%$ and curtailment by $\ge 30\%$.
  - State conditioning and clear-sky scaling will generalize to the untouched 2025 blind evaluation period.
- **UNRESOLVED:**
  - Telemetry ingestion latency for real-time sensor updating ($e_t^{obs}$).
  - Realistic wind forecast-error distribution (current research harness uses synthetic wind profiles).
- **BLOCKED:**
  - Historical solar horizons $k \in [20..24]$ (missing from MEPS archive).
  - All closed-loop controller execution on production code.
