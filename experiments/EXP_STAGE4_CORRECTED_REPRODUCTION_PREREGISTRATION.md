# POLARIS Preregistration: Stage 4 Corrected Reproduction (2025 Holdout)

**Experiment Identifier:** `EXP-STAGE4-CORRECTED-REPRODUCTION-2025-HOLDOUT`  
**Design Version:** `STAGE4-CORRECTED-REPRO-PREREG-v1.0`  
**Date (UTC):** 2026-10-06  
**Governance Status:** `PREREGISTRATION FROZEN — NOT IMPLEMENTED — NOT EXECUTED`  
**Execution Mode:** `SINGLE AGENT — NO SUBAGENTS — CAMPAIGN NOT STARTED`  
**Primary Governing Defect Record:** `experiments/RESEARCH_HARNESS_ROUTE_MODE_FIX_RECORD.md`  
**Historical Evidence Frozen Reference:** `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md` / `.json`  
**Original Preregistration Reference:** `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md` / `.json`  
**Holdout Governance Resolution:** `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.md` / `.json`  

---

## 1. Executive Purpose & Scope

This document defines the formal, pre-execution preregistration for a **corrected reproduction** of the POLARIS Stage 4 confirmatory experiment across the 123 origins of the 2025 holdout population (`2025-05-01` through `2025-08-31`).

### The Defect Being Corrected
In the original Stage 4 campaign execution (`experiments/stage4_sw_low_sun_2025_holdout/run_stage4_sw_low_sun_2025_campaign.py`), the `EMSControlRouter.evaluate_and_route()` method correctly assessed microgrid survivability under emergency conditions and returned `route_mode = "EMERGENCY"`. However, the runner passed the unmutated `StationState` (carrying the default `operating_mode = "NORMAL"`) into the research MILP optimizer (`ResearchNumericalGAP19Optimizer`). 

As a consequence, the Layer D emergency constraint:
$$p_{\text{dis}}(t) - p_{\text{served}}(t) \le 0 \quad \forall t \in \{0, \dots, 23\}$$
was never constructed or activated during the original Stage 4 execution, despite 8,288 hourly telemetry rows being labelled `EMERGENCY`.

### Scope of This Reproduction
1. **Target of the Reproduction:** Evaluate the closed-loop performance, safety gates, and diesel reduction of the five Stage-4 arms when the router-assessed operating mode (`route_mode`) is faithfully propagated into the planning `StationState` consumed by the research MILP optimizer via the verified helper `propagate_route_mode()`.
2. **Immutable Historical Status:** The original Stage 4 campaign results remain **frozen historical evidence**. This corrected reproduction does **not** overwrite, mutate, or retroactively invalidate the historical records in `experiments/stage4_sw_low_sun_2025_holdout/`.
3. **Research Boundary:** This reproduction is strictly a research experiment on synthetic microgrid benchmarks (Mount Nuolja `ANS_NMS`). It does **not** authorize production code promotion and does **not** validate physical operational deployment.

---

## 2. Verification Status of the Corrected Research Harness

Prior to the creation of this preregistration, the corrected research harness was verified through focused unit testing and end-to-end closed-loop smoke testing:

1. **Focused Regression Test Suite:** `tests/test_research_route_mode_propagation.py`
   - **8 / 8 tests passed** in 1.82 s.
   - Proved:
     - Real router produces `NORMAL` for high-resource state, `EMERGENCY` for low-resource state.
     - `propagate_route_mode()` creates a shallow planning copy with normalized case and leaves original execution state unmutated.
     - `NORMAL` assessment builds 0 emergency rows in the research MILP.
     - `EMERGENCY` assessment builds exactly 24 emergency rows ($p_{\text{dis}} \le p_{\text{served}}$ for $t \in [0, 23]$) in the research MILP.
     - Unpropagated state reproduces the historical defect (0 emergency rows built under router emergency).
     - Both shared research runner files (`closed_loop_causal_nwp_runner.py` and `research_critical_demand_adapter.py`) propagate route mode before invoking `optimize()`.
2. **End-to-End Closed-Loop Smoke Test:**
   - **Scenario A (NORMAL):** Router assessed `NORMAL` $\to$ optimizer received `NORMAL` $\to$ 0 emergency rows built $\to$ solver status `OPTIMAL` $\to$ step completed $\to$ original execution state unmutated $\to$ energy balance error $0.00\text{ W}$.
   - **Scenario B (EMERGENCY):** Router assessed `EMERGENCY` $\to$ optimizer received `EMERGENCY` $\to$ 24 emergency rows built $\to$ solver status `OPTIMAL` $\to$ plan strictly enforces $p_{\text{dis}}(t) \le p_{\text{served}}(t)$ $\to$ step completed $\to$ original execution state unmutated $\to$ energy balance error $0.00\text{ W}$.
   - **Scenario C (3-Step Receding Horizon):** 3 sequential receding-horizon cycles executed $\to$ 3 reoptimizations `OPTIMAL` $\to$ physical transitions verified $\to$ zero balance or safety invariant violations.
3. **Integrity Confirmation:** All production files and frozen Stage-4 files remain bit-for-bit identical to their frozen cryptographic hashes.

---

## 3. Explicitly Frozen Research Semantics (Unchanged)

To preserve scientific control and isolate the specific causal effect of closed-loop operating-mode propagation, **all other research semantics remain strictly frozen**. No silent modifications or tangential bug-fixes are permitted.

The following elements are explicitly declared unchanged from the original Stage 4 preregistration:

1. **Reserve / EBR Formulation:** 6-hour lookahead window with efficiency factor $\eta = 0.92$, identical per-arm renewable subtraction equations (Section 5).
2. **15° Low-Sun Rule:** Strict threshold $L_k = 1[e_k < 15.0^\circ]$. No tuning or alteration of the 15° convention.
3. **Solar-Elevation Ephemeris & Offset:** PVLib 0.16.1 at latitude 68.362074°N, longitude 18.738752°E, localized to `Etc/GMT-1`. The frozen 1-hour timestamp offset is retained and reported.
4. **Terminal Energy Target:** $E_{\text{term}} = 100,000\text{ Wh}$ at horizon index 23 ($E_{\text{stage2}}[23] = \max(E_{\text{arm}}[23], E_{\text{term}})$) across all arms.
5. **Battery Limits & Efficiencies:** Capacity $200\text{ kWh}$, SOC bounds $[20.0\%, 95.0\%]$, max charge $50\text{ kW}$, max discharge $50\text{ kW}$, charge efficiency $\eta_c = 0.92$, discharge efficiency $\eta_d = 0.92$.
6. **Diesel Limits & Consumption Model:** Min power $10\text{ kW}$, max power $100\text{ kW}$, base fuel $5.0\text{ L/h}$, marginal fuel $0.00025\text{ L/Wh}$, startup fuel $0.0\text{ L}$ (mathematical model).
7. **Fuel Accounting & Simulator Cap:** Simulation carries $100.0\text{ L}$ initial fuel per origin; cumulative fuel accounting tracks total litres consumed without artificial clipping.
8. **Forecast Generation:** Causal NWP physics engine using Open-Meteo `previous_day1` seamless variables, strict causal firewalling (zero actual solar, wind, or demand ground-truth exposed to forecaster or optimizer).
9. **Synthetic Realization Data:** Synthetic demand and synthetic wind power profiles identical to the frozen 2025 holdout inputs.
10. **Lexicographic Objective Hierarchy:** Highs native multi-objective hierarchy ($J_1$ critical unmet deficit $\to$ $J_2$ reserve shortfall $\to$ $J_3$ diesel fuel $\to$ $J_4$ operational wear / curtailment).
11. **Candidate Adapters:** Mathematical definitions of S, SW, S-L, and SW-L EBR modifications are unchanged.
12. **Numerical Residue Boundary:** $\tau = 0.055\text{ W}$ residue zeroing rule from `EXP_CANDIDATE_S_SW_PREREGISTRATION_ADDENDUM_NUMERICAL_BOUNDARY.md` applied identically to all arms.

*Governance Flag Rule:* If any of these frozen semantics are found during implementation or execution to require modification, the execution must STOP immediately and flag the issue for governance resolution.

---

## 4. Confirmatory Population & Holdout Definition

- **Population:** Exactly the 123 calendar origins from `2025-05-01 00:00:00` to `2025-08-31 00:00:00` inclusive.
- **Hourly Horizon:** 24 hours per origin (total 2,952 hours per arm; 14,760 total arm-hours across 5 arms).
- **Inclusion / Exclusion Rules:** Identical to original Stage 4 preregistration Section 8. All 123 origins are included based on verified input completeness. No origin may be excluded post-hoc based on solver performance, route mode, solar elevation, or candidate results.

---

## 5. The Five Arms and Governing Equations

All five arms will be executed on the identical 123 origins under identical corrected closed-loop machinery:

| Arm | Description | Renewable Credit in EBR | Low-Sun Protection ($L_k=1$) | Role |
|---|---|---|---|---|
| **Control B** | Unconditional EBR | None | — | Safety and fuel reference |
| **Candidate S** | Solar Net | Solar only | OFF | Efficiency reference |
| **Candidate SW** | Solar+Wind Net | Solar + Wind | OFF | Unprotected baseline |
| **Candidate S-L** | Protected Solar | Solar only | ON (reverts to Control B at low sun) | Efficiency reference |
| **Candidate SW-L** | Protected Solar+Wind | Solar + Wind | ON (reverts to Control B at low sun) | **Primary Decision Candidate** |

### Stored-Energy Reserve Target Equations ($E_{\text{arm}}[t]$)
For origin-day hour $t \in \{0, \dots, 23\}$, lookahead index $k \in \{t, \dots, \min(t+5, 23)\}$, $c_k = \min(11600\text{ W}, D_{\text{forecast}}[k])$, $s_k = \text{solar forecast (W)}$, $w_k = \text{wind forecast (W)}$, $\eta = 0.92$, $\Delta t = 1.0\text{ h}$:

1. **Control B:**
   $$E_B[t] = \frac{1}{\eta} \sum_{k=t}^{\min(t+5, 23)} c_k \cdot \Delta t$$
2. **Candidate S:**
   $$E_S[t] = \frac{1}{\eta} \sum_{k=t}^{\min(t+5, 23)} \max(0, c_k - s_k) \cdot \Delta t$$
3. **Candidate SW:**
   $$E_{SW}[t] = \frac{1}{\eta} \sum_{k=t}^{\min(t+5, 23)} \max(0, c_k - s_k - w_k) \cdot \Delta t$$
4. **Candidate S-L:**
   $$E_{SL}[t] = \frac{1}{\eta} \sum_{k=t}^{\min(t+5, 23)} \max\big(0, c_k - (1 - L_k) \cdot s_k\big) \cdot \Delta t$$
5. **Candidate SW-L:**
   $$E_{SWL}[t] = \frac{1}{\eta} \sum_{k=t}^{\min(t+5, 23)} \max\big(0, c_k - (1 - L_k) \cdot (s_k + w_k)\big) \cdot \Delta t$$

Horizon edge condition for all arms: $E_{\text{stage2}}[23] = \max(E_{\text{arm}}[23], 100000\text{ Wh})$.

---

## 6. Primary Purpose and Research Hypotheses

### Primary Purpose
Quantify exactly how faithful closed-loop propagation of `route_mode = "EMERGENCY"` (activating $p_{\text{dis}} \le p_{\text{served}}$ when microgrid survivability is critical) impacts:
1. Candidate diesel consumption and percentage diesel savings vs Control B.
2. Proportional and critical-first reliability safety margins.
3. Battery utilization, minimum SOC, diesel startups, and equivalent full cycles.
4. The statistical validity of the low-sun stored-energy protection mechanism ($C_4$ interaction).

### Hypotheses
- **$H_{\text{repro-0}}$ (Null):** Operating-mode propagation has negligible impact on diesel reduction and reliability; candidates reproduce historical Stage-4 outcomes within numerical tolerances.
- **$H_{\text{repro-1}}$ (Restricted Discharge Impact):** Activating the emergency discharge constraint ($p_{\text{dis}} \le p_{\text{served}}$) during emergency hours reduces unconstrained battery discharge, altering diesel dispatch and increasing diesel consumption relative to the unconstrained historical run, while improving or maintaining critical reliability.

---

## 7. Safety Gates, Diesel Gate, and Statistical Protocol

### Safety Gates (Deterministic, Zero Tolerance)
A candidate must pass all three safety gates against re-executed Control B on the 123 origins:
1. **Gate 1 — Critical-First Reliability:**
   $$\Delta R_{\text{CF}} = R_{\text{CF}}(\text{candidate}) - R_{\text{CF}}(\text{Control B}) \ge 0.00\text{ pp}$$
2. **Gate 2 — Proportional Critical Reliability:**
   $$\Delta R_{\text{P}} = R_{\text{P}}(\text{candidate}) - R_{\text{P}}(\text{Control B}) \ge 0.00\text{ pp}$$
3. **Gate 3 — Minimum SOC Floor:**
   $$\text{Realized SOC} \ge 20.00\% \quad \forall \text{ origin-hours}$$
   (Exactly zero hours with $\text{SOC} < 20.00\%$).

*Precedence:* Safety strictly overrides efficiency. If any safety gate fails, the candidate is classified as a `SAFETY FAILURE` regardless of fuel savings.

### Statistical Diesel Gate (Evaluated Only If Safety Passes)
For S-L and SW-L vs Control B across the 123 paired origin differences $\Delta_o = \text{Fuel}_{\text{ControlB}}(o) - \text{Fuel}_{\text{candidate}}(o)$:
1. **Two-sided paired Wilcoxon signed-rank test** with Holm-Bonferroni correction across the two tests ($p_{\text{adj}} < 0.05$).
2. **BCa 95% bootstrap confidence interval** (10,000 origin resamples, seed 42) with lower bound strictly $> 0.0\text{ L/origin}$.

### 40% Diesel Reduction Target (Report-Only)
- Target: $(\text{Fuel}_{\text{ControlB}} - \text{Fuel}_{\text{SW-L}}) / \text{Fuel}_{\text{ControlB}} \ge 40.0\%$.
- **Status:** **REPORT-ONLY**. The 40% target is an efficiency benchmark, **NOT** a safety gate and **NOT** an advancement prerequisite.

### Factorial Contrasts ($2 \times 2$)
Evaluated origin-paired with BCa 95% bootstrap CIs (10,000 resamples, seed 42):
- $C_1 = SW - S$ (wind effect without protection)
- $C_2 = SW\text{-}L - SW$ (protection effect under solar+wind)
- $C_3 = S\text{-}L - S$ (protection effect under solar-only)
- $C_4 = (SW\text{-}L - SW) - (S\text{-}L - S)$ (**Primary Mechanism Interaction**)

---

## 8. Required Comparative Protocol: Frozen Stage 4 vs Corrected Reproduction

For every arm, the reproduction analysis must compute and present a side-by-side comparison of the **Old Frozen Stage-4 Result** against the **Corrected Reproduction Result**.

### Baseline Reference Table (Old Frozen Stage-4 Results to be Compared)
The following frozen values from `experiments/stage4_sw_low_sun_2025_holdout/` form the reference baseline:

| Metric | Control Frozen B | Candidate S | Candidate SW | Candidate S-L | Candidate SW-L |
|---|---|---|---|---|---|
| **Diesel Fuel (L)** | 6,117.9691 | 4,648.3272 | 3,885.0225 | 5,334.1331 | 5,221.3152 |
| **Diesel Saving vs B (%)** | 0.00% | 24.02% | 36.50% | 12.81% | 14.66% |
| **Critical-First Rel (%)** | 93.669482% | 94.327168% | 94.090514% | 94.455173% | 94.484413% |
| **$\Delta R_{\text{CF}}$ vs B (pp)** | — | +0.657686 | +0.421032 | +0.785691 | +0.814931 |
| **Proportional Rel (%)** | 83.823383% | 84.604885% | 83.467189% | 85.150455% | 85.264223% |
| **$\Delta R_{\text{P}}$ vs B (pp)** | — | +0.781502 | **-0.356194 (FAIL)** | +1.327072 | +1.440840 |
| **Total Unmet Load (MWh)** | 5.56 | 5.42 | 6.00 | 5.14 | 5.08 |
| **Total Curtailment (MWh)** | 6.55 | 9.94 | 9.79 | 10.35 | 10.40 |
| **Min Realized SOC (%)** | 54.99% | 20.00% | 20.00% | 20.00% | 20.00% |
| **SOC Floor Violations (<20%)** | 0 | 0 | 0 | 0 | 0 |
| **Diesel-On Hours (h)** | 589 | 446 | 368 | 506 | 496 |
| **Diesel Startups** | 108 | 101 | 83 | 114 | 109 |
| **Equivalent Full Cycles (EFC)** | 79.00 | 93.97 | 94.38 | 86.54 | 89.48 |

The corrected reproduction report must populate the exact corresponding metrics from the corrected campaign and report the $\Delta (\text{Corrected} - \text{Frozen})$ for every cell.

---

## 9. Decision & Winner Rules

1. **Winner Rule:** The winning candidate shall be the candidate achieving the **highest statistically significant diesel reduction** among all safety-qualified candidates (candidates passing Gates 1, 2, and 3).
2. **Safety Override:** Safety precedes efficiency unconditionally. No candidate failing any safety gate may be declared winner.
3. **No Automatic Production Promotion:** Achieving a positive result in this research reproduction does **NOT** authorize production code modification or live operational promotion. Production deployment remains gated by prospective real-world trials and independent governance review.
4. **Supersession Rule:** The results of this reproduction supersede the historical Stage 4 results **strictly for future research decision-making and subsequent research phases**. The historical Stage 4 records remain permanently archived, immutable evidence of the unpropagated harness behavior.

---

## 10. Cryptographic Provenance & Hash Manifest

Before executing any campaign runner, the reproduction harness must verify the following exact cryptographic SHA-256 hashes:

### Original Frozen Stage-4 Artifacts & Preregistration
| Component | Path | Cryptographic SHA-256 Hash |
|---|---|---|
| Stage 4 Freeze MD | `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md` | `e73558cfd03acd35fc55d24a055f7ccc6a31d0d973a3cc2e4443a8665ac21cd7` |
| Stage 4 Freeze JSON | `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.json` | `6b0bb6f7af44ef06731180d50239de222f301fa571c5862d115f7644d3be7b87` |
| Stage 4 Preregistration MD | `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md` | `9cb2d5459894be8add07a3bd01595f40ab2485c2a18510765c4d8f0264fe4e46` |
| Stage 4 Preregistration JSON | `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.json` | `9a16ccc8c28267331da2816fe0c7c04aeb9afd6f963e49673eb6c3872d892623` |
| Holdout Governance MD | `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.md` | `22e67a16a90ef90fa88b248614a83d853511a33619548272535e05615314d7a7` |
| Holdout Governance JSON | `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.json` | `f96fd97c812f44e88455c966c500a3874a99f07b8ae94744759d0fac6b461bf7` |

### Defect Fix & Corrected Research Harness Files
| Component | Path | Cryptographic SHA-256 Hash |
|---|---|---|
| Fix Record MD | `experiments/RESEARCH_HARNESS_ROUTE_MODE_FIX_RECORD.md` | `0d5c95b3132fec9c21ec12d2129073ed35011893e9af133df431ef3c24b748e0` |
| Propagation Helper | `system/research/route_mode_propagation.py` | `80456f8776925860ad20c407ec92f3ac78dbd387f4863ea48dc1917490e89376` |
| Closed-Loop Runner | `system/research/closed_loop_causal_nwp_runner.py` | `ef7bbd33ef3d216513b33c535b3ed345a60a412e1f5c90f035237434da047265` |
| Critical Demand Adapter | `system/research/research_critical_demand_adapter.py` | `0601e57c0a0f5f6cb37f463b9d6a35ed23ffa29a6501d2f46902e356c82a6b85` |
| Focused Regression Suite | `tests/test_research_route_mode_propagation.py` | `4e0afaa8bc31fe54987dbe69f76aa41c75c6983512d2e62cec8c4219627e4298` |

### Production Code Boundary (Untouched)
| Component | Path | Cryptographic SHA-256 Hash |
|---|---|---|
| Native HiGHS GAP19 | `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| Dispatch Plan Schema | `system/schemas/dispatch_plan.py` | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` |
| Causal NWP Forecaster | `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` |
| EMS Control Router | `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` |
| Realization Executor | `system/simulation/research_realization_executor.py` | `c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b` |
| Station State Schema | `system/schemas/station_state.py` | `e763439a6ddecbbadb9287f99258e595ab7f23f0eb9a7377f5a54beb7661df88` |

---

## 11. Immutability Declaration

This preregistration document is frozen upon creation and hash-registered in `experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.json`. No alterations to design, thresholds, origins, or hypotheses may occur after registration. Execution of the campaign is forbidden until authorized by governance.
