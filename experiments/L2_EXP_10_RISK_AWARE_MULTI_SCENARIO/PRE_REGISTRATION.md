# POLARIS L2-EXP-10: PRE-REGISTRATION PROTOCOL
**Experiment Title:** Risk-Aware Multi-Scenario Trade-Off Optimization  
**Experiment ID:** `L2-EXP-10`  
**Classification:** STRICTLY RESEARCH-ONLY — NOT A PRODUCTION PROMOTION  
**Pre-Registration Status:** `LOCKED_PRIOR_TO_EVALUATION`  
**Pre-Registration Timestamp:** `2026-10-04T10:05:00Z`  
**Evaluation Data:** Held-out 2024 window (173 odd origins: 123 NORMAL route, 50 EMERGENCY route)  

---

## 1. Executive Summary & Core Research Question

L2-EXP-09 demonstrated that a Two-Stage Stochastic Multi-Scenario MILP (Arm D) achieved massive advantages over static $q_{10}$ conservative control (Arm B) in solar curtailment (-35.0%, avoiding 3.10 MWh of curtailment) and battery degradation (-42.3% in Equivalent Full Cycles). However, Arm D suffered an unacceptable operational trade-off:
- Diesel consumption rose dramatically (+1,463.3 L, +20.2% above Arm B).
- Total realized unmet critical load was slightly higher than Arm B (86.7 kWh vs 64.0 kWh).
- A minor SOC-floor excursion (19.61% vs 20.00% floor) occurred on Origin 77.

### Core Research Question
> *"Can the multi-scenario optimizer (Arm D) achieve static-$q_{10}$ (Arm B) level reliability/unmet-load performance WITHOUT paying Arm D's large diesel penalty, while retaining some of Arm D's advantages in battery cycling (EFC) and solar curtailment?"*

We do **not** assume the answer is yes.

---

## 2. Established Reference Ladder & Benchmarks

The evaluation reproduces the exact 5-arm reference ladder from L2-EXP-09 across the identical 123 NORMAL origins:
1. **Arm A (Candidate F Point-Control):** Deterministic GAP19 using Stage 8.1 Candidate F point forecast.
2. **Arm B (Static $q_{10}$ Conservative Control):** Deterministic GAP19 using conformalized $q_{10\text{,cal}}$ lower bound. **Primary reliability benchmark.**
3. **Arm C (L2-EXP-08 Adaptive Risk-Budget Interface):** Dynamic interpolation heuristic $\lambda_t$ between Candidate F and $q_{10\text{,cal}}$.
4. **Arm D (L2-EXP-09 Multi-Scenario Stochastic MILP):** Re-evaluated unmodified from frozen L2-EXP-09 formulation.
5. **Arm E (Perfect-Foresight Diagnostic Benchmark):** Diagnostic upper bound using realized actual solar generation.

Arm D is **not** considered the winner. Arm B is the primary benchmark.

---

## 3. The New Research Arm: Arm F (Risk-Aware Multi-Scenario Optimizer)

Arm F starts directly from the validated L2-EXP-09 Arm D formulation and introduces a principled risk-aware and resource-aware refinement addressing the observed root causes of Arm D's diesel and reliability penalties:

### Root Mechanism Forensic Diagnosed from Arm D
1. **Accidental HiGHS Priority Inversion:** In the L2-EXP-09 implementation, priorities were configured as `priority = 1, 2, 3, 4` under the assumption that priority 1 is solved first. However, native HiGHS solves multi-objectives in **descending** priority order (priority 4 is solved first). Consequently, Arm D prioritized curtailment minimization ($J_4$) above diesel ($J_3$), reserve shortfall ($J_2$), and critical deficit ($J_1$). This caused the optimizer to aggressively discharge the battery during early morning hours to make room for high solar scenarios, depleting battery energy so severely that when low solar materialized, emergency diesel had to be committed in evening hours.
2. **Risk-Neutral vs Downside Reserve Coupling:** Solving expected reserve shortfall ($J_2$) without strict tolerance coupling or resource awareness forced diesel commitment across all scenarios to satisfy reserve targets, even when central and upside scenarios were energy-rich.

### Principled Arm F Refinement
Arm F explicitly restores the governed lexicographic hierarchy with exact zero tolerances (`abs_tolerance = 0.0`, `rel_tolerance = 0.0`):
$$\text{Priority 4: } J_1 \text{ (Critical Deficit)} \quad \longrightarrow \quad \text{Priority 3: } J_2 \text{ (Reserve Shortfall)} \quad \longrightarrow \quad \text{Priority 2: } J_3 \text{ (Diesel Fuel)} \quad \longrightarrow \quad \text{Priority 1: } J_4 \text{ (Curtailment)}$$
By solving diesel fuel ($J_3$) at Priority 2 **before** curtailment ($J_4$) at Priority 1, Arm F strictly prevents the optimizer from ever discharging the battery or committing diesel merely to avoid curtailment.

---

## 4. Exact Mathematical Formulation of Arm F

### 4.1 Scenario Set ($S = 3$)
Over horizon $H = 24$ hours ($t \in \{0, \dots, 23\}$):
1. **Scenario 0 ($s=0$, Downside Solar):** Irradiance $q_{10\text{,cal}} = \max\left(0, F_t + r_{10, t} - \hat{q}\right)$, causal night zeroed, inversion-guarded $p_{\text{solar}, t, 0} \le p_{\text{solar}, t, 1}$. Probability mass $\pi_0 = 0.25$.
2. **Scenario 1 ($s=1$, Central Expectation):** Candidate F point forecast $F_t = \max(0, \text{Stage4}_t + \Delta F_t)$. Probability mass $\pi_1 = 0.50$.
3. **Scenario 2 ($s=2$, Upside Solar):** $q_{90\text{,cal}} = F_t + r_{90, t} + \hat{q}$, capped by research envelope $U_t = \max(1.25 \times \text{clearsky\_ghi}_t, F_t)$ (`SIMULATED_RESEARCH_ASSUMPTION`). Probability mass $\pi_2 = 0.25$.

### 4.2 Decision Variables
- **First-Stage Variables (Scenario-Independent, Non-Anticipative across all $s$):**
  - $u_{\text{diesel}}[t] \in \{0, 1\}$: Diesel commitment
  - $v_{\text{start}}[t] \in \{0, 1\}$: Diesel startup event
  - $p_{\text{diesel}}[t] \in [0, 100\text{ kW}]$: Continuous diesel power setpoint
  - $u_{\text{chg}}[t] \in \{0, 1\}$: Inverter charge mode binary
  - $u_{\text{dis}}[t] \in \{0, 1\}$: Inverter discharge mode binary
  - $p_{\text{dis}}[t] \in [0, 50\text{ kW}]$: Continuous battery discharge setpoint
  - $p_{\text{wind\_used}}[t] \in [0, p_{\text{wind}}[t]]$: Dispatched deterministic wind power
  - $p_{\text{chg\_plan}}[t] \in [0, 50\text{ kW}]$: Shared planned battery charging ceiling

- **Second-Stage Recourse Variables (for each scenario $s \in \{0, 1, 2\}$):**
  - $p_{\text{sol\_used}}[t, s] \ge 0$: Solar power consumed
  - $p_{\text{curt\_sol}}[t, s] \ge 0$: Solar power curtailed
  - $p_{\text{curt\_wind}}[t, s] \ge 0$: Wind power curtailed
  - $p_{\text{chg}}[t, s] \ge 0$: Realized battery charge power ($p_{\text{chg}}[t, s] \le p_{\text{chg\_plan}}[t]$)
  - $p_{\text{served}}[t, s] \ge 0$: Load served
  - $p_{\text{unmet}}[t, s] \ge 0$: Total load deficit
  - $p_{\text{flex}}[t, s] \in [0, 500\text{ W}]$: Flexible load served
  - $E[t+1, s] \in [E_{\text{min}}, E_{\text{max}}]$: Battery state of charge
  - $P_{\text{unmet\_crit}}[t, s] \ge 0$: Critical load deficit
  - $s_{J2}[t, s] \ge 0$: Governed reserve shortfall

Total variables: 984 (96 binary, 888 continuous).

### 4.3 Constraints
1. **Bus-Bar Power Balance:**
   $$p_{\text{sol\_used}}[t, s] + p_{\text{wind\_used}}[t] + p_{\text{dis}}[t] + p_{\text{diesel}}[t] = p_{\text{served}}[t, s] + p_{\text{chg}}[t, s] + p_{\text{flex}}[t, s] \quad \forall t, s$$
2. **Renewable Decomposition:**
   $$p_{\text{sol\_used}}[t, s] + p_{\text{curt\_sol}}[t, s] = p_{\text{solar}}[t, s] \quad \forall t, s$$
   $$p_{\text{wind\_used}}[t] + p_{\text{curt\_wind}}[t, s] = p_{\text{wind}}[t] \quad \forall t, s$$
3. **Critical & Total Demand Deficit Balance:**
   $$p_{\text{served}}[t, s] + p_{\text{unmet}}[t, s] = p_{\text{demand}}[t] \quad \forall t, s$$
   $$p_{\text{served}}[t, s] + P_{\text{unmet\_crit}}[t, s] = p_{\text{crit\_demand}}[t] \quad \forall t, s$$
4. **Inverter Coupling & Exclusivity:**
   $$p_{\text{chg\_plan}}[t] \le P_{\text{chg\_max}} \cdot u_{\text{chg}}[t] \quad \forall t$$
   $$p_{\text{chg}}[t, s] \le p_{\text{chg\_plan}}[t] \quad \forall t, s$$
   $$p_{\text{dis}}[t] \le P_{\text{dis\_max}} \cdot u_{\text{dis}}[t] \quad \forall t$$
   $$u_{\text{chg}}[t] + u_{\text{dis}}[t] \le 1 \quad \forall t$$
5. **Battery Dynamics & Physical State Bounds:**
   $$E[t+1, s] = E[t, s] + \left( \eta_{\text{chg}} p_{\text{chg}}[t, s] - \frac{p_{\text{dis}}[t]}{\eta_{\text{dis}}} \right) \Delta t \quad \forall t, s$$
   $$E_{\text{min}} \le E[t+1, s] \le E_{\text{max}} \quad \forall t, s$$
6. **Governed Reserve Envelope (6h Lookahead EBR + Horizon-Edge Terminal Target):**
   $$E[t+1, s] + s_{J2}[t, s] \ge E_{\text{stage2\_target}}[t] + E_{\text{min}} \quad \forall t, s$$
7. **Diesel Operation & Startup Accounting:**
   $$P_{\text{diesel\_min}} \cdot u_{\text{diesel}}[t] \le p_{\text{diesel}}[t] \le P_{\text{diesel\_max}} \cdot u_{\text{diesel}}[t] \quad \forall t$$
   $$v_{\text{start}}[t] \ge u_{\text{diesel}}[t] - u_{\text{diesel}}[t-1] \quad \forall t$$
8. **Non-Anticipativity:**
   Shared variables $u_{\text{diesel}}[t], v_{\text{start}}[t], p_{\text{diesel}}[t], u_{\text{chg}}[t], u_{\text{dis}}[t], p_{\text{dis}}[t], p_{\text{wind\_used}}[t], p_{\text{chg\_plan}}[t]$ are identical across scenarios $\forall s$.

### 4.4 Lexicographic Multi-Objective Hierarchy in HiGHS
HiGHS evaluates linear objectives in descending priority order:

1. **Priority 4 (Level 1 — Critical Reliability):**
   $$\min J_1 = \sum_{s=0}^{S-1} \pi_s \sum_{t=0}^{H-1} P_{\text{unmet\_crit}}[t, s] \cdot \Delta t, \quad \text{abs\_tolerance} = 0.0, \, \text{rel\_tolerance} = 0.0$$
2. **Priority 3 (Level 2 — Governed Reserve Envelope Protection):**
   $$\min J_2 = \sum_{s=0}^{S-1} \pi_s \sum_{t=0}^{H-1} s_{J2}[t, s], \quad \text{abs\_tolerance} = 0.0, \, \text{rel\_tolerance} = 0.0$$
3. **Priority 2 (Level 3 — Resource-Aware Diesel & Cycling Efficiency):**
   $$\min J_3 = \sum_{t=0}^{H-1} \left( m_{\text{fuel}} p_{\text{diesel}}[t] + b_{\text{fuel}} u_{\text{diesel}}[t] + s_{\text{fuel}} v_{\text{start}}[t] + c_{\text{deg}} p_{\text{dis}}[t] \right) \Delta t, \quad \text{abs\_tolerance} = 0.0, \, \text{rel\_tolerance} = 0.0$$
   where $m_{\text{fuel}} = 0.00025\text{ L/Wh}$, $b_{\text{fuel}} = 5.0\text{ L/h}$, $s_{\text{fuel}} = 2.0\text{ L}$, and $c_{\text{deg}} = 10^{-6}\text{ L/Wh}$ (tie-breaking cycling regularizer).
4. **Priority 1 (Level 4 — Renewable Curtailment Minimization):**
   $$\min J_4 = \sum_{s=0}^{S-1} \pi_s \sum_{t=0}^{H-1} \left( p_{\text{curt\_sol}}[t, s] + p_{\text{curt\_wind}}[t, s] \right) \Delta t, \quad \text{abs\_tolerance} = 0.0, \, \text{rel\_tolerance} = 0.0$$

---

## 5. Success / Failure Acceptance Criteria

Per Section 6 of the governance mandate:
1. **Unmet Load Gate (Primary):**
   $$\text{Total Realized Unmet Critical Load (Arm F)} \le \text{Total Realized Unmet Critical Load (Arm B)} \times 1.10$$
   *(If Arm F cannot meet this threshold, the primary objective is declared FAILED).*
2. **Diesel Resource Goal:**
   $$\text{Total Diesel (Arm F)} < \text{Total Diesel (Arm D)}$$
   *(Desirable secondary outcome: Arm F diesel approaches Arm B diesel without sacrificing reliability).*
3. **Battery Cycling Target:**
   Arm F should retain a meaningful portion of Arm D's EFC reduction relative to Arm B.
4. **Curtailment Target:**
   $$\text{Total Curtailment (Arm F)} < \text{Total Curtailment (Arm B)}$$
5. **Safety & Integrity Hard Gates (Zero Tolerance):**
   - Exactly 0 SOC-floor violations across all 123 origins.
   - Exact energy accounting at every timestep.
   - Exact scenario accounting and non-anticipativity residual $< 10^{-6}$.
   - Zero optimizer failures or infeasibilities.
   - Zero actual solar leakage into optimization.

---

## 6. Cryptographic Provenance Signatures

| Artifact Name | File Path | Frozen SHA-256 Hash |
| :--- | :--- | :--- |
| **Candidate F Model** | `stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` |
| **SKGBDT q10 Model** | `models/l2_exp_02_skgbdt_q10.joblib` | `4b6cd3655983fc6b14c09402d9ee27d0f52b68d5dd7d3f9b0c7a514e84eed9cb` |
| **SKGBDT q50 Model** | `models/l2_exp_02_skgbdt_q50.joblib` | `104d638aae053b5e9eaff886a6d4639f75eaeb0cea5a86328ddcd6d0f4188a71` |
| **SKGBDT q90 Model** | `models/l2_exp_02_skgbdt_q90.joblib` | `8eb01a6b99b6d939fb01e0dbe58d715e157da8663908e99c93fa9ea80d6833ff` |
| **Matrix 2024** | `stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| **Treatment Fixture 2024** | `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` |
| **Conformal Calibration** | Frozen CQR $\hat{q}$ (2022 validation set) | `+9.8962 W/m²` |
| **Pre-Registration JSON** | `experiments/L2_EXP_10_RISK_AWARE_MULTI_SCENARIO/pre_registration.json` | Hash computed upon lock |

---

## 7. Pre-Registration Lock Declaration

```
PRE_REGISTRATION_LOCKED = TRUE
EXPERIMENT_ID = L2-EXP-10
CLASSIFICATION = STRICTLY_RESEARCH_ONLY
NO PRODUCTION PROMOTION AUTHORIZED
2024 EVALUATION COMMENCEMENT AUTHORIZED UPON LOCK
```
