# POLARIS L2-EXP-12: PRE-REGISTRATION DOCUMENT
## Horizon-Aware q10 Risk-Budget Comparison

**Experiment ID:** `L2-EXP-12`  
**Date of Pre-Registration:** `2026-10-04T11:25:00.000000+00:00`  
**Policy JSON Hash (SHA-256):** `cb47c15baaf954f9ed5b7481dcd8cb6399703d487fe58c12a989574de542b52d`  
**Governance Mode:** `STRICTLY_RESEARCH_ONLY`  
**Production Authorization:** `NO PRODUCTION PROMOTION AUTHORIZED`  

> **Pre-Registration Lock Statement:**  
> *"2024 evaluation outcomes were not used to select, tune, or modify the L2-EXP-12 formulation, arms, risk budgets, or acceptance criteria after pre-registration."*

---

## 1. Core Research Objective & Motivation

### Context of L2-EXP-11 Failure Mechanism
In L2-EXP-11, an hour-by-hour adaptive quantile selector using a low-capacity neural network failed the primary reliability gate ($D_{\text{unmet}} = 134.1\text{ kWh}$ vs $B_{\text{unmet}} = 65.0\text{ kWh}$, $+106.3\%$). Mechanism forensics revealed why:
1. **Asymmetric Pointwise Optimization:** Pointwise hour-by-hour relaxation relaxed $q_t > 0.10$ in $69.2\%$ of daytime hours whenever local weather features looked benign.
2. **Horizon Shortfall Accumulation:** Microgrid EMS operates over a continuous 24-hour physical state horizon. Suppressing early-morning diesel generation based on localized morning optimism left the battery with insufficient energy when afternoon cloud troughs materialized, causing severe late-day critical deficits.

### Core Research Question
> *"Can we recover some of $q_{10}$'s diesel and curtailment efficiency while retaining its reliability advantage by allocating a bounded reliability-risk budget across the full 24h horizon, rather than relaxing $q$ on an uncoordinated hour-by-hour basis?"*

---

## 2. Experimental Arms & Mathematical Formulations

### Arm A: Candidate F Point Control
Standard Candidate F / Stage8.1 point forecast control. Unmodified. Represents an uncertainty-unaware baseline.

### Arm B: Static $q_{10}$ Safety Benchmark (Primary Reference)
Frozen calibrated SKGBDT $q_{10}$ lower bound forecast ($q_{10}^{\text{raw}} - \hat{q}$, where $\hat{q} = 9.8962$). Unmodified.

### Arm C: Fixed Modest $q$ Relaxation (Diagnostic Baseline)
Applies a single, constant modest relaxation for all daytime hours without state or weather adaptation:
- Daytime hours ($\text{clearsky}_t > 0$, $\text{solar\_elevation}_t > 0$): $q_t = 0.15$
- Nighttime hours: $q_t = 0.10$
$$p_{\text{solar}, t}(q_t) = q_{10, t}^{\text{power}} + \frac{0.15 - 0.10}{0.50 - 0.10} \cdot \max\left(0, q_{50, t}^{\text{power}} - q_{10, t}^{\text{power}}\right)$$
This arm evaluates whether simple static relaxation is viable or whether any relaxation without state-awareness incurs unmet load penalties.

### Arm D: SOC-Aware $q$ Relaxation
Relaxes $q_t$ up to $q_{\max} = 0.20$ only when the initial battery SOC is comfortably above the critical reserve floor, with continuous afternoon horizon damping:
1. **Reserve Margin Scaling:**
   $$\gamma_{\text{soc}} = \text{clip}\left(\frac{\text{SOC}_0 - 40.0\%}{80.0\% - 40.0\%}, 0.0, 1.0\right)$$
   If $\text{SOC}_0 \le 40\%$, $\gamma_{\text{soc}} = 0 \implies q_t = 0.10$.
2. **Afternoon Horizon Decay:**
   $$\gamma_{\text{horizon}}(t) = \max\left(0.0, 1.0 - \frac{t}{18.0}\right)$$
3. **Adaptive Quantile:**
   $$q_t = 0.10 + (0.20 - 0.10) \cdot \gamma_{\text{soc}} \cdot \gamma_{\text{horizon}}(t)$$
   ensuring that as evening approaches ($t \to 18$), $q_t$ monotonically returns to $q_{10}$.

### Arm E: Horizon Risk-Budget $q$ Relaxation (Primary Research Arm)
Defines a finite cumulative **optimism energy budget** across the full 24-hour horizon.
1. **Risk Budget Definition & Units:**
   Let $\Delta p_t = \max\left(0, q_{50, t}^{\text{power}} - q_{10, t}^{\text{power}}\right)$ be the solar uncertainty spread (Watts).
   The "optimism energy" committed in hour $t$ is:
   $$E_{\text{opt}, t} = \frac{q_t - 0.10}{0.50 - 0.10} \cdot \Delta p_t \cdot \Delta t \quad (\text{Wh})$$
   The finite horizon risk budget is pre-registered as:
   $$\mathcal{B}_{\max} = 15,000\text{ Wh} \quad (7.5\% \text{ of battery capacity})$$
2. **Remaining Budget & Horizon Accounting:**
   At each hour $t \in \{1, \dots, 24\}$:
   $$\mathcal{B}_t^{\text{rem}} = \max\left(0.0, \mathcal{B}_{\max} - \sum_{\tau < t} E_{\text{opt}, \tau}\right)$$
   $$N_t^{\text{rem}} = \sum_{\tau \ge t} \mathbb{I}(\text{daytime}_\tau)$$
   $$b_t = \frac{\mathcal{B}_t^{\text{rem}}}{\max(1, N_t^{\text{rem}})}$$
3. **State-Aware Damping:**
   $$\rho_{\text{soc}} = \text{clip}\left(\frac{\text{SOC}_0 - 30.0\%}{70.0\% - 30.0\%}, 0.0, 1.0\right)$$
4. **Hourly Allocation:**
   $$E_{\text{opt}, t} = \min\left(b_t \cdot \rho_{\text{soc}}, \frac{q_{\max} - 0.10}{0.50 - 0.10} \cdot \Delta p_t \cdot \Delta t\right)$$
   $$q_t = 0.10 + 0.40 \cdot \frac{E_{\text{opt}, t}}{\max(\Delta p_t \cdot \Delta t, 1.0)}$$
   where $q_{\max} = 0.20$.
5. **Natural Conservation Property:**
   - During high-spread midday hours ($\Delta p \approx 16\text{ kW}$), allocating a bounded energy budget automatically forces $q_t$ closer to $q_{10}$ ($\approx 0.138$), preventing massive over-optimism.
   - If morning hours consume optimism energy, afternoon hours automatically collapse back to $q_{10}$ as $\mathcal{B}^{\text{rem}} \to 0$.

### Arm F: Perfect Foresight Diagnostic
Dispatches with actual realized solar power. Upper bound on achievable efficiency.

---

## 3. Primary Safety & Acceptance Gates

Arm E is classified as **`PROMISING`** if and only if ALL gates pass:
- **G1 (SOC Safety):** 0 floor violations ($< 20\%$) and 0 ceiling violations ($> 95\%$) across all origins.
- **G2 (Accounting):** Exact energy balance accounting and non-anticipativity verification.
- **G3 (Reliability Gate):** Realized unmet critical load:
  $$E_{\text{unmet}} \le B_{\text{unmet}} \times 1.10 = 65,026.9 \times 1.10 = 71,529.6\text{ Wh}$$
- **G4 (Reliability Consistency):** Critical reliability statistically consistent with static $q_{10}$.
- **G5 (Efficiency):** Statistically significant reduction in diesel fuel and/or solar curtailment vs Arm B.

If Gate G3 fails, Arm E must be classified as **`NO-GO`**.

---

## 4. Evaluation Scope & Cryptographic Hashes

- Scope: 173 odd origins (123 NORMAL route, 50 EMERGENCY route) across 2024 held-out data.
- Input Hashes:
  - `candidate_f_model`: `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84`
  - `skgbdt_q10`: `4b6cd3655983fc6b14c09402d9ee27d0f52b68d5dd7d3f9b0c7a514e84eed9cb`
  - `skgbdt_q50`: `104d638aae053b5e9eaff886a6d4639f75eaeb0cea5a86328ddcd6d0f4188a71`
  - `skgbdt_q90`: `8eb01a6b99b6d939fb01e0dbe58d715e157da8663908e99c93fa9ea80d6833ff`
  - `matrix_2024`: `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43`
  - `treatment_fixture_2024`: `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`
