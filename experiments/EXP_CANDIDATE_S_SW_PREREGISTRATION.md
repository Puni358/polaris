# POLARIS Preregistration: Candidate S & SW Closed-Loop Diesel Reduction

**Experiment Identifier:** `EXP-CANDIDATE-S-SW-DIESEL-REDUCTION-2024`  
**Governance Status:** `PREREGISTRATION FROZEN — CANDIDATE EXECUTION AUTHORIZED`  
**Execution Gate:** `AUTHORIZED FOR EXECUTION ACROSS 123 NORMAL ORIGINS`  
**Date:** October 5, 2026  
**Artifact Directory:** `experiments/`  

---

## 1. Research Objectives & Scope

This experiment evaluates whether forecast-conditioned net-critical-deficit energy buffer reserve (EBR) mechanisms can safely eliminate unnecessary diesel generation forced by unconditional reserve margins during high-renewable hours, while preserving microgrid critical-load survivability and battery physical constraints.

- **Primary Research Candidate:** **Candidate 2, Variant S (Solar-Only Net EBR)**.
- **Comparative Research Candidate:** **Candidate 2, Variant SW (Solar + Synthetic Wind Net EBR)**.
- **Control Baseline:** **Control_Frozen_B** (MEPS Causal NWP + 6h Unconditional EBR + 100 kWh Terminal Target).

---

## 2. Mathematical Candidate Formulations

### 2.1 Variant S (Primary Candidate — Solar Credit Only)
For each reoptimization time step $t \in \{0 \dots 22\}$:
$$E_{\mathrm{EBR\_S}}[t] = \frac{1}{\eta_{\mathrm{dis}}} \sum_{k=t}^{\min(t+5, 23)} \max\left(0, \, \text{critical\_demand}[k] - \text{solar\_generation\_point}[k]\right) \cdot \Delta t$$
At horizon edge $t=23$:
$$E_{\mathrm{stage2\_target}}[23] = \max\left(\frac{1}{\eta_{\mathrm{dis}}} \max\left(0, \text{critical\_demand}[23] - \text{solar\_generation\_point}[23]\right) \cdot \Delta t, \, E_{\mathrm{term\_target}}\right)$$
- Direct electrical PV input: Consumes `bundle.solar_generation.point` in Watts.
- Zero wind credit in reserve sizing (unaffected by wind forecast errors; wind remains active in busbar balance).
- Reverts to governed unconditional EBR when forecast solar is zero across the entire window.

### 2.2 Variant SW (Comparative Candidate — Solar + Wind Credit)
Adds $-\text{wind\_generation\_point}[k]$ within the deficit bracket:
$$E_{\mathrm{EBR\_SW}}[t] = \frac{1}{\eta_{\mathrm{dis}}} \sum_{k=t}^{\min(t+5, 23)} \max\left(0, \, \text{critical\_demand}[k] - \text{solar\_generation\_point}[k] - \text{wind\_generation\_point}[k]\right) \cdot \Delta t$$
- **Synthetic Wind Caveat:** Wind series in this benchmark is synthetic ($4500 + 5000\sin$); results represent synthetic research evidence and cannot be generalized to physical wind regimes.

---

## 3. Evaluation Dataset & Benchmark Constraints

- **Dataset:** Exactly **123 NORMAL origins** (May 1 to August 31, 2024), identical to `Control_Frozen_B`.
- **Synthetic Demand:** $D_{\mathrm{realized}}[h] = \max(10000.0, \, \text{round}(15000.0 + 3000.0\cos(h\pi/12), 2)) \ge 12,000.0\text{ W} > 11,600.0\text{ W}$.
- **Constant Critical Demand:** $D_{\mathrm{crit}}[t] = \min(11600.0\text{ W}, D_{\mathrm{realized}}[t]) \equiv 11,600.0\text{ W}$ across all 2,952 operating hours ($34,243.20\text{ kWh}$ total).
- **Synthetic Wind:** $P_{\mathrm{wind\_realized}}[h] = \max(0.0, \, \text{round}(4500.0 + 5000.0\sin(h\pi/6), 2))$.

---

## 4. Frozen Baselines (Control_Frozen_B across 2,952 Hourly Records)

All baseline values are verified from the serialized telemetry artifact `hourly_telemetry_123_frozen_b.json`:
- **Critical-First Reliability Baseline ($R_{\mathrm{CRITICAL\_FIRST}}$):** **93.470303%**
  - Critical Served: $32,007,222.81\text{ Wh}$ ($32,007.22\text{ kWh}$)
  - Critical Unmet: $2,235,977.19\text{ Wh}$ ($2,235.98\text{ kWh}$)
- **Exact Hourly Proportional Reliability Baseline ($R_{\mathrm{PROPORTIONAL}}$):** **83.694610%**
  - Critical Served: $28,659,712.84\text{ Wh}$ ($28,659.71\text{ kWh}$)
  - Critical Unmet: $5,583,487.16\text{ Wh}$ ($5,583.49\text{ kWh}$)
- **Flat Proportional Value ($82.284510\%$):** Formally designated as an **approximation only, NOT an authorized baseline**.
- **Total Diesel Fuel:** **6603.9802 L**
- **Total Curtailment:** **9,477.70 kWh** ($9,477,704.0\text{ Wh}$)
- **Minimum Realized SOC:** **54.97%**
- **SOC Floor Violations ($< 20.00\%$):** **0**

---

## 5. Frozen Decision Rules & Acceptance Gates

A candidate controller must satisfy all safety gates simultaneously before any fuel reduction is evaluated:

1. **Critical-First Reliability Safety Gate:**
   $$\Delta R_{\mathrm{CRITICAL\_FIRST}} = R_{\mathrm{CRITICAL\_FIRST}}(\text{Candidate}) - 93.470303\% \ge 0.00\text{ percentage points}$$
2. **Proportional Reliability Safety Gate:**
   $$\Delta R_{\mathrm{PROPORTIONAL}} = R_{\mathrm{PROPORTIONAL}}(\text{Candidate}) - 83.694610\% \ge 0.00\text{ percentage points}$$
3. **Hard SOC Floor Invariant:**
   $$\text{Zero realized } \mathrm{SOC} < 20.00\% \text{ across all 123 origins (zero violations)}.$$
4. **Statistical Fuel Reduction Gate (Evaluated Only if Gates 1–3 Pass):**
   $$\text{Paired Wilcoxon signed-rank, two-sided } p < 0.05 \quad \text{AND} \quad \text{BCa } 95\% \text{ CI for mean fuel saving (Frozen B minus candidate, litres) strictly } > 0.$$

**Safety Precedence Invariant:** A candidate failing either reliability convention or the SOC gate is rejected regardless of fuel savings.

---

## 6. Cryptographic Integrity and Artifact Hashes

- **Production Integrity Verification Method:** GAP19 solver and Causal NWP forecaster integrity are verified strictly by SHA-256 cryptographic hashes. Git diff is not relied upon to prove production immutability because untracked repository artifacts exist.
- **Frozen Hashes:**
  - **Serialized Telemetry Artifact (`hourly_telemetry_123_frozen_b.json`):**  
    `13359f2742a0eecce14dc1c506ce0a933a9a5a441082120f83adf21d8c3f48e5`
  - **Telemetry Summary Metadata (`hourly_telemetry_123_frozen_b_summary.json`):**  
    `46c412837c5713877c42aabb223b7d22be47bca09eeba25472aa675eb009396f`
  - **Reconciliation Report (`HOURLY_BASELINE_RECONCILIATION_REPORT.md`):**  
    `70985bc3ba9e5909fb2ac43fa46feae3a81cc569b65c2a67c334ab40f3f6ce08`
  - **GAP19 Native HiGHS Implementation (`system/optimization/implementations/gap19_highs_native.py`):**  
    `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737`
  - **Causal NWP Forecaster (`system/forecasting/implementations/causal_nwp_physics.py`):**  
    `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710`

---

## 7. Execution Authorization

- **Implementation Status:** Candidate S and Candidate SW are **NOT YET IMPLEMENTED** in this step.
- **Execution Status:** **AUTHORIZED FOR EVALUATION HARNESS IMPLEMENTATION AND EXECUTION**.
