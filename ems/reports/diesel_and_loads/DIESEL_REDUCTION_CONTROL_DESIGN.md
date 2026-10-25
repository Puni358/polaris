# POLARIS EMS Diesel-Reduction Control Design Study (Final Governed Specification)
## First-Principles Mathematical Re-Engineering of Reserve Sizing & Critical Protection

**Document:** `DIESEL_REDUCTION_CONTROL_DESIGN.md`  
**Date:** 2026-10-05  
**Audit Reference:** Final Governance Audit per Independent AI assistant Forensic Review  
**Status:** DESIGN ONLY — ZERO PRODUCTION CODE MODIFICATIONS — ZERO EXPERIMENTS EXECUTED  
**Target Architecture:** GAP19 HiGHS Native Lexicographic MILP (`system/optimization/implementations/gap19_highs_native.py`)  
**Final Design Verdict:** **`RESEARCH_DESIGN_COMPLETE — AWAITING SAFETY-GATE PREREGISTRATION`**  

---

## 1. Executive Summary & Epistemic Taxonomy

The POLARIS 2024 closed-loop campaign (`EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024`) demonstrated that Arm B (causal MEPS NWP + physics) burned **+1,125.7 L (+20.5%)** more diesel than the persistence baseline (Arm A) over 123 origins, failing in 87 of 123 origins.

A synthesis of forensic artifacts (`EBR_BRANCH_FINAL_SYNTHESIS.md`, `HOURLY_TRACE_REPORT.md`, `TERMINAL_ABLATION_REPORT.md`, `EBR_ABLATION_REPORT.md`, and `CRITICAL_AWARE_EBR_FAILURE_REVIEW.md`) proved that this diesel penalty was driven by the optimizer-reserve interface: an unconditional 6-hour reserve ranked above fuel in a lexicographic solver forcing early diesel charging, followed by solar curtailment via the executor's same-hour discharge realization rule.

Every claim in this document is classified according to strict epistemic standards:
- **`[VERIFIED]`**: Directly proven by production code, frozen artifacts, or reproducible simulation outputs.
- **`[INFERRED]`**: Logically follows from verified facts but not directly measured as an isolated single-variable counterfactual.
- **`[UNSUPPORTED]`**: Hypotheses, uncalibrated constants, or speculative projections excised from baseline assertions.
- **`[REQUIRES-EXPERIMENT]`**: Formally posed research candidates and variants requiring isolated closed-loop campaign testing.

---

## 2. Mathematical Forensic Analysis of Current GAP19 Formulation

### 2.1 The Native HiGHS Lexicographic Model `[VERIFIED]`
The production model in [`system/optimization/implementations/gap19_highs_native.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/gap19_highs_native.py) is a 408-variable, 312-constraint mixed-integer linear program solved via `highspy` with strict lexicographic priority:
$$\min_{\mathbf{x}} \left[ J_1(\mathbf{x}), \, J_2(\mathbf{x}), \, J_3(\mathbf{x}), \, J_4(\mathbf{x}) \right]$$
with `blend_multi_objectives = False` and strict priority hierarchy:
- **$J_1$ (Priority 4 - Highest):** Critical Load Deficit (Wh)
  $$J_1 = \sum_{t=0}^{23} P_{\mathrm{unmet\_crit}}[t] \cdot \Delta t$$
- **$J_2$ (Priority 3):** Governed Reserve Shortfall Slack (Wh)
  $$J_2 = \sum_{t=0}^{23} s_{J2}[t]$$
- **$J_3$ (Priority 2):** Diesel Fuel Consumption (Liters)
  $$J_3 = \sum_{t=0}^{23} \left( c_{\mathrm{marg}} \cdot p_{\mathrm{diesel}}[t] + c_{\mathrm{base}} \cdot u_{\mathrm{diesel}}[t] + c_{\mathrm{start}} \cdot v_{\mathrm{start}}[t] \right) \cdot \Delta t$$
  with parameters: $c_{\mathrm{marg}} = 0.00025\text{ L/Wh}$, $c_{\mathrm{base}} = 5.0\text{ L/h}$, and code default $c_{\mathrm{start}} = 2.0\text{ L}$.
- **$J_4$ (Priority 1 - Lowest):** Renewable Curtailment (Wh)
  $$J_4 = \sum_{t=0}^{23} \left( p_{\mathrm{curt\_sol}}[t] + p_{\mathrm{curt\_wind}}[t] \right) \cdot \Delta t$$

### 2.2 Governed Critical-Demand Input Vector `[VERIFIED]`
In the research closed-loop runner ([`system/research/research_critical_demand_adapter.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/research/research_critical_demand_adapter.py#L36-L41)), GAP19 receives the canonical critical-demand array via `step_configs["critical_demand_w"]`:
$$\text{critical\_demand}[t] = \min\left(11{,}600.0\text{ W}, \, \text{demand.point}[t]\right)$$
This vector represents the governed critical load ceiling clipped to total demand. It is **not** total demand.

### 2.3 Governed EBR Forward Window and Horizon Edge Shrinkage `[VERIFIED]`
The Layer C reserve constraint is formulated as:
$$E_{\mathrm{next}}[t] + s_{J2}[t] \ge E_{\mathrm{stage2\_target}}[t] + E_{\min} \quad \forall t \in \{0 \dots 23\}$$
where $E_{\min} = 0.20 \times 200{,}000\text{ Wh} = 40{,}000\text{ Wh}$ ($20\%$ SOC physical battery floor).

The governed forward lookahead window for every $t \in \{0 \dots 23\}$ is explicitly:
$$W(t) = \{t \dots \min(t+5, 23)\} \equiv \text{range}(t, \min(t+6, 24))$$
The lookahead window **shrinks toward the horizon edge**:
- For $t \in \{0 \dots 18\}$ (full 6-hour window):
  $$E_{\mathrm{EBR\_target}}[t] = \frac{1}{\eta_{\mathrm{dis}}} \sum_{k=t}^{t+5} \text{critical\_demand}[k] \cdot \Delta t = \frac{6 \times 11{,}600\text{ W} \times 1\text{h}}{0.92} \approx 75{,}652.17\text{ Wh}$$
  Target with physical floor: $75{,}652.17 + 40{,}000 = 115{,}652.17\text{ Wh}$ ($57.83\%$ SOC).
- For $t = 19$ (5-hour window): $E_{\mathrm{EBR\_target}}[19] = 5 \times 11{,}600 / 0.92 \approx 63{,}043.48\text{ Wh}$.
- For $t = 20$ (4-hour window): $E_{\mathrm{EBR\_target}}[20] = 4 \times 11{,}600 / 0.92 \approx 50{,}434.78\text{ Wh}$.
- For $t = 21$ (3-hour window): $E_{\mathrm{EBR\_target}}[21] = 3 \times 11{,}600 / 0.92 \approx 37{,}826.09\text{ Wh}$.
- For $t = 22$ (2-hour window): $E_{\mathrm{EBR\_target}}[22] = 2 \times 11{,}600 / 0.92 \approx 25{,}217.39\text{ Wh}$.
- For $t = 23$ (1-hour window): $E_{\mathrm{EBR\_target}}[23] = 1 \times 11{,}600 / 0.92 \approx 12{,}608.70\text{ Wh}$.

At the horizon boundary ($t = 23$), the terminal reserve target is applied via the pointwise maximum:
$$E_{\mathrm{stage2\_target}}[23] = \max\left(E_{\mathrm{EBR\_target}}[23], \, E_{\mathrm{term\_target}}\right) = \max(12{,}608.70\text{ Wh}, \, 100{,}000\text{ Wh}) = 100{,}000\text{ Wh}$$
Target with physical floor at $t=23$: $100{,}000 + 40{,}000 = 140{,}000\text{ Wh}$ ($70.0\%$ SOC).

### 2.4 Lexicographic Forcing Mechanism `[VERIFIED]`
Because $J_2 \succ J_3$ in lexicographic priority:
$$\text{HiGHS strictly enforces } s_{J2}[t] = 0 \implies E_{\mathrm{next}}[t] \ge E_{\mathrm{stage2\_target}}[t] + E_{\min}$$
before fuel consumption $J_3$ is minimized.
If initial battery energy is below the target, or if forecasted renewables are insufficient to sustain the trajectory, the optimizer **must** dispatch diesel ($u_{\mathrm{diesel}}[t] = 1, p_{\mathrm{diesel}}[t] \ge 10\text{ kW}$) to eliminate $s_{J2}$, regardless of fuel cost.

---

## 3. Systematic Investigation of the Eight Design Dimensions

1. **How Diesel is Forced `[VERIFIED]`:** Diesel commitment is forced at step 0 by the combination of an unconditional reserve target (57.83% SOC for $t \le 18$) ranked above fuel ($J_2 \succ J_3$), diesel's minimum generation floor ($10\text{ kW}$), and startup/base fuel costs ($2.0\text{ L} + 5.0\text{ L/h}$).
2. **Governing Constraint `[VERIFIED]`:** Layer C reserve constraints (Constraints 288–311) enforce $E_{\mathrm{next}}[t] + s_{J2}[t] \ge E_{\mathrm{stage2\_target}}[t] + E_{\min}$, evaluated at HiGHS Priority 3.
3. **What Reserve Protects `[VERIFIED]`:** Currently, EBR protects a static gross critical load assuming zero renewables and zero diesel generation for 6 consecutive hours. In physical reality, diesel is operational and starts within the optimization timestep in the model.
4. **Renewable Availability vs State-Triggered Commitment `[INFERRED]`:** Scheduling diesel hours in advance based on distant forecasted cloudiness causes irreversible fuel burn when clouds fail to materialize. Committing diesel based on actual battery depletion near physical minimums is causally immune to downstream forecast errors.
5. **Terminal Reserve Duplication `[VERIFIED]`:** In the 6-origin terminal ablation (`TERMINAL_ABLATION_REPORT.md`), setting $E_{\mathrm{term\_target}} = 0.0$ reduced diesel fuel by $-14.6\%$ (−56.6 L) and curtailment by $-10.2\%$, but **increased cumulative unmet load by +6.3% (+20.2 kWh)**. Terminal reserve is a partial contributor to diesel consumption, but removing it carries an unmet-load penalty that must be evaluated independently.
6. **Battery Headroom & Curtailment Pathology `[VERIFIED]`:** When diesel charges the battery to high SOC before sunrise, battery charge headroom collapses ($E_{\max} - E \to 0$). The executor realization rule curtails surplus when the plan discharges in the same hour (~93–96% of curtailment), converting burned diesel into curtailed solar.
7. **Startup and Base Fuel Economics `[VERIFIED]`:** Diesel efficiency scales from $0.75\text{ L/kWh}$ at $10\text{ kW}$ to $0.35\text{ L/kWh}$ at $50\text{ kW}$ and $0.30\text{ L/kWh}$ at $100\text{ kW}$. To amortize base and startup penalties, the optimizer plans high-power multi-hour blocks ($40\text{--}50\text{ kW}$), accelerating headroom saturation.
8. **Uncertainty Interface Role `[INFERRED]`:** An uncertainty representation cannot simply be added on top of unconditional EBR. To reduce fuel without losing safety, uncertainty must dynamically scale the allowable renewable credit against critical demand.

---

## 4. Primary Research Candidate: Forecast-Conditioned Net-Critical-Deficit EBR

### 4.1 Relationship to Prior Research `[VERIFIED]`
Candidate 2 belongs to the same broad forecast-conditioned EBR family as the prior critical-aware EBR experiments (`CRITICAL_AWARE_EBR_EXPERIMENT.md`), which achieved $-33.9\%$ to $-35.0\%$ diesel reduction but failed the reliability gate ($-0.29$ to $-0.46$ pp critical reliability).
- **Variant SW** is substantively the same wind-inclusive formulation previously tested and serves as a **replication/confirmation arm**, not a novel controller.
- **Variant S** was previously tested on six diagnostic origins (`SOLAR_ONLY_EBR_EXPERIMENT.md`).
Neither variant is an unexplored or newly proven controller. Both represent candidate hypotheses to be evaluated under clean causal isolation.

### 4.2 Exact Formulation: Variant S (Solar-Only Net EBR)
Variant S credits forecasted solar power against the forward critical-load window:
$$E_{\mathrm{EBR\_S}}[t] = \frac{1}{\eta_{\mathrm{dis}}} \sum_{k=t}^{\min(t+5, 23)} \max\left(0, \, \text{critical\_demand}[k] - \text{solar\_generation\_point}[k]\right) \cdot \Delta t \quad \forall t \in \{0 \dots 22\}$$
$$E_{\mathrm{stage2\_target}}[23] = \max\left(\frac{1}{\eta_{\mathrm{dis}}} \max\left(0, \text{critical\_demand}[23] - \text{solar\_generation\_point}[23]\right) \cdot \Delta t, \, E_{\mathrm{term\_target}}\right)$$

#### Invariants & Execution Rules:
1. **Direct Electrical Input:** $\text{solar\_generation\_point}[k]$ is taken directly in Watts from `bundle.solar_generation.point`. The controller does **not** compute $51 \times I$ or apply a 60 kW cap; this conversion is handled upstream in the forecast engine. (The $51\text{ W}/(\text{W/m}^2)$ ratio is an upstream prototype mapping, not an authorized physical constant).
2. **Critical Demand Input:** $\text{critical\_demand}[k]$ is the exact clipped array $\min(11{,}600.0\text{ W}, \, \text{demand.point}[k])$.
3. **No Additional Floors:** No arbitrary energy floor or reserve constant is added. Physical battery protection is provided exclusively by the governed physical floor $E_{\min} = 40\text{ kWh}$ ($20\%$ SOC).
4. **Behavior Under Overcast:** Variant S equals the existing governed EBR **only when** forecast solar generation is zero for every step of the reserve window and the critical-demand vector is identical.
5. **Wind Interaction:** Variant S is unaffected by wind forecast error **in the reserve sizing equation**, but wind generation remains active in the optimizer busbar balance.

---

### 4.3 Exact Formulation: Variant SW (Solar + Wind Net EBR)
Variant SW credits both forecasted solar and point forecasted wind against the forward critical-load window:
$$E_{\mathrm{EBR\_SW}}[t] = \frac{1}{\eta_{\mathrm{dis}}} \sum_{k=t}^{\min(t+5, 23)} \max\left(0, \, \text{critical\_demand}[k] - \text{solar\_generation\_point}[k] - \text{wind\_generation\_point}[k]\right) \cdot \Delta t \quad \forall t \in \{0 \dots 22\}$$
$$E_{\mathrm{stage2\_target}}[23] = \max\left(\frac{1}{\eta_{\mathrm{dis}}} \max\left(0, \text{critical\_demand}[23] - \text{solar\_generation\_point}[23] - \text{wind\_generation\_point}[23]\right) \cdot \Delta t, \, E_{\mathrm{term\_target}}\right)$$

#### Invariants & Caveats:
1. **Synthetic Wind Warning:** In the current campaign framework, the wind series is synthetic ($4500 + 5000\sin$). Therefore, results from Variant SW represent **synthetic-wind research evidence** and must **not** be generalized to real wind forecasting performance.
2. **Busbar Invariance:** Wind credit applies only inside reserve sizing; wind remains in the normal optimizer busbar balance.

---

## 5. Status of Alternative Controller Mechanisms

- **Candidate 1 (Solar Headroom Reservation): `BLOCKED / NOT READY`**  
  The formula lacked a lower clamp, causing negative values and mathematical infeasibility on 53/173 fixture origins. Furthermore, under $J_2 \succ J_3$, an upper bound below the reserve forces $s_{J2} > 0$ and compels the solver to burn diesel to charge toward the cap. Dropped from the shortlist.
- **Candidate 3 (Elastic Reserve Slack): `DEFERRED / FUTURE RESEARCH ONLY`**  
  The $\lambda$ derivation was mathematically refuted. Merging $J_2$ and $J_3$ requires modifying production GAP19 objective code. Reclassified as a future parametric sweep.
- **Candidate 4 (State-Triggered JIT Diesel): `BLOCKED / NOT READY`**  
  Attribution corrected (68.4% is total EBR-OFF fuel reduction); non-linear for $t \ge 1$ without big-M; lacks verified equipment start-delay model.
- **Terminal Target Removal: `DEFERRED TO SEPARATE ABLATION`**  
  Must remain unchanged ($100\text{ kWh}$) in the primary experiment to preserve causal isolation (prior evidence showed $-14.6\%$ fuel, but $+6.3\%$ unmet load).

---

## 6. Qualitative Candidate Evaluation Matrix

Numerical 0–10 scores are removed as subjective:

| Candidate Mechanism | Primary Diesel-Reduction Mechanism | Critical Safety Risk | Causal Data Availability | Implementation Complexity | Causal Isolation | Research Readiness |
|---|---|---|---|---|---|:---:|
| **Candidate 2: Net-Deficit EBR (Variant S)** | Releases reserve during daytime solar hours | Low risk in reserve sizing (no wind credit) | Complete (`bundle.solar_generation.point`) | Low (Layer C RHS modification) | Excellent (reserve sizing only) | **READY FOR PREREGISTRATION** |
| **Candidate 2: Net-Deficit EBR (Variant SW)** | Releases reserve during solar & wind hours | Medium-High (vulnerable to wind over-forecast) | Complete (uses synthetic wind forecast) | Low (Layer C RHS modification) | Excellent (reserve sizing only) | **REPLICATION ARM ONLY** |
| **Candidate 1: Solar Headroom** | Caps pre-dawn battery charging | High (risk of MILP infeasibility) | Complete (astronomical sunrise) | Medium (requires soft clamp & slack) | Poor (conflicts with J2 priority) | **BLOCKED / NOT READY** |
| **Candidate 4: State-Triggered JIT** | Inhibits diesel when battery energy is safe | Medium (lacks verified start-delay model) | Complete (state-based) | High (requires big-M reformulation) | Moderate (receding-horizon shift) | **BLOCKED / NOT READY** |
| **Candidate 3: Elastic Reserve Slack** | Co-optimizes fuel and reserve shortfall | High (optimizer indifferent to reserve) | Complete | High (modifies GAP19 objective code) | Poor (blends J2 and J3 priorities) | **DEFERRED** |

---

## 7. Preregistered Closed-Loop Validation Protocol (Design Only)

### 7.1 Evaluation Dataset
The experiment will evaluate across the full **123-origin closed-loop campaign framework** (`EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024`).  
This set is explicitly designated as a **pre-specified paired historical evaluation set; not a pristine holdout**. The 6 diagnostic origins are rejected as a test set due to selection bias and small sample size.

### 7.2 Experimental Arms & Strict Causal Isolation
To isolate causality, the first experiment modifies **only** the EBR reserve-target calculation:
- **Control Arm (Frozen Arm B):** Unchanged GAP19 (`gap19_highs_native.py`) with governed 6h EBR and 100 kWh terminal target.
- **Treatment Arm S:** Variant S (solar-only credit in reserve sizing).
- **Treatment Arm SW:** Variant SW (solar + wind credit in reserve sizing).

All other components remain identical:
- `terminal_target_wh = 100000.0 Wh` ($70\%$ SOC at $t=23$)
- Physical battery SOC bounds: $[20.0\%, 95.0\%]$
- Diesel model parameters: $P_{\min} = 10\text{ kW}$, $P_{\max} = 100\text{ kW}$, $c_{\mathrm{base}} = 5.0\text{ L/h}$, $c_{\mathrm{marg}} = 0.00025\text{ L/Wh}$, $c_{\mathrm{start}} = 2.0\text{ L}$
- Objective vector and priority structure ($J_1 \succ J_2 \succ J_3 \succ J_4$)
- Router, realization executor, forecast engine, and demand adapter
- Hourly receding-horizon closed-loop simulation

### 7.3 Critical-Load Evaluation & Dual-Accounting Framework
Following the project-manager governance decision, safety evaluation requires **Dual Accounting**:
1. **Critical-First Priority Allocation:**
   $$D_{\mathrm{crit}}[t] = \min(11{,}600\text{ W}, \, D_{\mathrm{realized}}[t]) \equiv 11{,}600\text{ W}$$
   $$\text{served}_{\mathrm{crit\_first}}[t] = \min(D_{\mathrm{crit}}[t], \, S[t]), \quad \text{unmet}_{\mathrm{crit\_first}}[t] = D_{\mathrm{crit}}[t] - \text{served}_{\mathrm{crit\_first}}[t]$$
   $$R_{\mathrm{CRITICAL\_FIRST}} = 1.0 - \frac{\sum_t \text{unmet}_{\mathrm{crit\_first}}[t]}{\sum_t D_{\mathrm{crit}}[t]}$$
   - *Control_Frozen_B Baseline:* **$93.470303\%$** ($2,235.98\text{ kWh}$ unmet over $34,243.20\text{ kWh}$ critical demand across 123 origins, verified from 2,952 serialized hourly records).

2. **Proportional Allocation:**
   $$\text{served}_{\mathrm{crit\_prop}}[t] = \text{served}_{\mathrm{total}}[t] \times \frac{D_{\mathrm{crit}}[t]}{D_{\mathrm{realized}}[t]}$$
   $$\text{unmet}_{\mathrm{crit\_prop}}[t] = D_{\mathrm{crit}}[t] - \text{served}_{\mathrm{crit\_prop}}[t]$$
   $$R_{\mathrm{PROPORTIONAL}} = 1.0 - \frac{\sum_t \text{unmet}_{\mathrm{crit\_prop}}[t]}{\sum_t D_{\mathrm{crit}}[t]}$$
   - *Control_Frozen_B Baseline:* **$83.694610\%$** ($5,583.49\text{ kWh}$ unmet over $34,243.20\text{ kWh}$ critical demand across 123 origins, computed exactly from 2,952 serialized hourly records).
   - *Comparison to Old Flat Approximation:* The old flat proportional approximation ($82.284510\%$) is formally designated as an approximation only, NOT an authorized baseline. It differed by $-1.410101\text{ pp}$ from exact hourly proportional reliability because the hourly allocation ratio $D_{\mathrm{crit}}[t] / D_{\mathrm{realized}}[t]$ varies throughout the diurnal cycle between $0.6444$ and $0.9667$ rather than remaining constant at the 24-hour aggregate mean ratio ($0.7733$).
   - *Synthetic Benchmark Limitation:* Realized demand and wind are deterministic synthetic benchmark curves; results represent synthetic research evidence and cannot be generalized to physical grid observations.

The campaign's legacy `reliability_pct` field is **prohibited** as an authoritative metric.

### 7.4 Paired Statistical Framework
The evaluation will employ the established campaign statistical methodology across all 123 paired origins:
- Two-sided paired Wilcoxon signed-rank test.
- Bias-Corrected and Accelerated (BCa) bootstrap 95% confidence intervals using the campaign methodology and fixed seed.
- **Primary Comparison:** Cumulative diesel fuel consumption (Control vs Treatment).
- **Safety Comparisons:** Critical reliability under both conventions and minimum observed SOC.
- **Secondary Metrics:** Diesel run hours, startups, curtailment, battery EFC/throughput, SOC min/max, SOC floor violations, optimizer status codes, and accounting residuals.

### 7.5 Formal Safety Gates & Decision Rules (Project-Manager Decision)
A candidate controller must satisfy all safety gates simultaneously before any fuel reduction is considered:
1. **Critical-First Reliability Gate:**
   $$\Delta R_{\mathrm{CRITICAL\_FIRST}} = R_{\mathrm{CRITICAL\_FIRST}}(\text{Candidate}) - 93.470303\% \ge 0.00\text{ percentage points}$$
2. **Proportional Reliability Gate:**
   $$\Delta R_{\mathrm{PROPORTIONAL}} = R_{\mathrm{PROPORTIONAL}}(\text{Candidate}) - 83.694610\% \ge 0.00\text{ percentage points}$$
3. **Hard SOC Floor Invariant:**
   $$\text{Zero realized } \mathrm{SOC} < 20.00\% \text{ across all 123 origins (zero violations)}.$$
4. **Statistical Fuel Gate (Only Evaluated if Gates 1–3 Pass):**
   $$\text{Paired Wilcoxon signed-rank, two-sided } p < 0.05 \quad \text{AND} \quad \text{BCa } 95\% \text{ CI for mean fuel saving (Frozen B minus candidate, litres) strictly } > 0.$$

**Safety Precedence Invariant:** A candidate failing either reliability convention or the SOC gate is rejected regardless of fuel savings.

---

## 8. Governance Affirmation & Cryptographic Freeze

- **Final Preregistration Verdict:** **`PREREGISTRATION FROZEN — CANDIDATE EXECUTION AUTHORIZED`**
- **Production Immutability Verification:** GAP19 solver and Causal NWP forecaster integrity are verified strictly by SHA-256 cryptographic hashes. Git diff is not relied upon to prove production immutability because untracked repository artifacts exist.
- **Frozen Production & Research Hashes:**
  - **GAP19 Native HiGHS Implementation (`system/optimization/implementations/gap19_highs_native.py`):**  
    `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` (`UNCHANGED`)
  - **Causal NWP Forecaster (`system/forecasting/implementations/causal_nwp_physics.py`):**  
    `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` (`UNCHANGED`)
  - **Serialized 2,952-Row Telemetry Artifact (`hourly_telemetry_123_frozen_b.json`):**  
    `13359f2742a0eecce14dc1c506ce0a933a9a5a441082120f83adf21d8c3f48e5` (`FROZEN`)
  - **Telemetry Summary Metadata (`hourly_telemetry_123_frozen_b_summary.json`):**  
    `46c412837c5713877c42aabb223b7d22be47bca09eeba25472aa675eb009396f` (`FROZEN`)
- **Production Files Modified:** **`ZERO (0)`**
- **Experiments Run:** **`ZERO (0)`** (Candidate S / SW not implemented; baseline telemetry generation for Control B only)
- **EMS Controller Logic / Router:** `UNCHANGED`
- **Stage 8.1 Model Artifact:** `UNCHANGED`
