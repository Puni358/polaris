# Hourly Baseline Reconciliation Report: Frozen Control B (123 Origins)

**Date:** 2026-10-05  
**Artifact Directory:** `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/hourly_trace_123_frozen_b/`  
**Serialized Telemetry Artifact:** `hourly_telemetry_123_frozen_b.json`  
**Telemetry SHA-256:** `13359f2742a0eecce14dc1c506ce0a933a9a5a441082120f83adf21d8c3f48e5`  
**Summary JSON:** `hourly_telemetry_123_frozen_b_summary.json`  
**Summary SHA-256:** `46c412837c5713877c42aabb223b7d22be47bca09eeba25472aa675eb009396f`  
**Governance Status:** `PREREGISTRATION FROZEN — CANDIDATE EXECUTION AUTHORIZED`  

---

## 1. Executive Summary

This report establishes the exact, hourly dual-accounting baseline metrics for `Control_Frozen_B` across all 123 NORMAL origins (May 1 to August 31, 2024) of the closed-loop microgrid campaign (`EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024`).

All $123 \times 24 = 2,952$ operating hours have been deterministically executed using the frozen campaign machinery, verified against the frozen per-origin totals (123/123 origins match frozen fuel, total unmet, served load, and curtailment to numerical precision), and serialized to disk.

---

## 2. Telemetry Integrity Verification

- **Unique Origins Evaluated:** Exactly **123** (Origins 1 through 123, matching `ARM_B_CANDIDATE`).
- **Total Serialized Hourly Records:** Exactly **2,952** rows.
- **Record Integrity:** Exactly 24 chronological hours (0 to 23) per origin. Zero missing, zero duplicate origin-hour keys.
- **Reproduction Gate:** 123 / 123 origins reproduce frozen `ARM_B_CANDIDATE` totals:
  - Total Diesel Fuel: **6603.9802 L** ($\Delta = 0.0000\text{ L}$)
  - Total Realized Served: **36,435.58 kWh** ($36,435,580.83\text{ Wh}$, $\Delta = 0.00\text{ Wh}$)
  - Total Realized Unmet: **7,844.42 kWh** ($7,844,419.08\text{ Wh}$, $\Delta = 0.00\text{ Wh}$)
  - Total Curtailment: **9,477.70 kWh** ($9,477,704.0\text{ Wh}$, $\Delta = 0.00\text{ Wh}$)
  - Minimum Realized SOC: **54.97%** (0 violations $< 20.00\%$)

---

## 3. Exact Dual-Accounting Baseline Results

### 3.1 Common Demand Accounting & Synthetic Limitations
- Realized Demand Generator: $D_{\mathrm{realized}}[h] = \max(10000.0, \, \text{round}(15000.0 + 3000.0\cos(h\pi/12), 2))$
- Minimum Realized Demand: $12,000.0\text{ W} > 11,600.0\text{ W}$ at all hours.
- Hourly Critical Demand: $D_{\mathrm{crit}}[t] = \min(11600.0\text{ W}, D_{\mathrm{realized}}[t]) \equiv 11,600.0\text{ W}$ constant across all evaluated hours.
- Realized Wind Generator: $P_{\mathrm{wind\_realized}}[h] = \max(0.0, \, \text{round}(4500.0 + 5000.0\sin(h\pi/6), 2))$. Coupled with persistence forecasts, this creates a deterministic, non-physical 12-hour periodic error cycle ($-5\text{ kW}$ to $0\text{ kW}$).
- **Synthetic Limitation:** Both demand and wind are deterministic synthetic benchmarks; results represent synthetic research evidence and cannot be generalized as physical observations.
- **Total Campaign Critical Demand:** **34,243,200.00 Wh (34,243.20 kWh)**.
- **Total Campaign Realized Demand:** **44,280,000.00 Wh (44,280.00 kWh)**.

### 3.2 Dual-Accounting Baseline Metrics

| Metric | Critical-First Priority Allocation | Exact Hourly Proportional Allocation | Flat Proportional Approx (Old) |
|---|---:|---:|---:|
| **Formula** | $\text{served}_c = \min(D_c, S)$ | $\text{served}_c = S_{\mathrm{tot}} \cdot (D_c / D)$ | $\text{unmet}_c = \text{unmet}_{\mathrm{tot}} \cdot (\sum D_c / \sum D)$ |
| **Critical Demand** | 34,243,200.00 Wh | 34,243,200.00 Wh | 34,243,200.00 Wh |
| **Critical Served** | **32,007,222.81 Wh** (32,007.22 kWh) | **28,659,712.84 Wh** (28,659.71 kWh) | 28,176,851.52 Wh (28,176.85 kWh) |
| **Critical Unmet** | **2,235,977.19 Wh** (2,235.98 kWh) | **5,583,487.16 Wh** (5,583.49 kWh) | 6,066,348.48 Wh (6,066.35 kWh) |
| **Baseline Reliability** | **93.470303%** | **83.694610%** | **82.284510%** *(approx only)* |

---

## 4. Comparison: Exact Hourly Proportional vs. Flat Approximation

- **Exact Hourly Proportional Reliability:** **$83.694610\%$**
- **Old Flat Proportional Approximation:** **$82.284510\%$**
- **Discrepancy:** **$+1.410101\text{ percentage points}$**

### Mathematical Basis of Discrepancy:
The hourly allocation ratio $\frac{D_{\mathrm{crit}}[t]}{D_{\mathrm{realized}}[t]} = \frac{11,600}{D_{\mathrm{realized}}[t]}$ varies throughout the diurnal cycle between $0.6444$ ($18\text{ kW}$ peak) and $0.9667$ ($12\text{ kW}$ trough), rather than remaining constant at the 24-hour aggregate demand ratio $\frac{278.4}{360} = 0.7733$. Because the hourly served load $S_{\mathrm{tot}}[t]$ and the allocation ratio vary concurrently across the 2,952 operating hours, exact hourly proportional allocation directly computes $\sum_t S_{\mathrm{tot}}[t] \cdot \frac{D_{\mathrm{crit}}[t]}{D_{\mathrm{realized}}[t]}$, eliminating the aggregation bias inherent in using the scalar 24-hour mean ratio. The flat approximation ($82.284510\%$) is formally designated as an approximation only, NOT an authorized baseline.

---

## 5. Frozen Preregistered Decision Gates for Candidate S / SW

With the exact baselines locked from serialized hourly data, the project-manager dual-accounting gates are:

1. **Critical-First Reliability Safety Gate:**
   $$\Delta R_{\mathrm{CRITICAL\_FIRST}} = R_{\mathrm{CRITICAL\_FIRST}}(\text{Candidate}) - 93.470303\% \ge 0.00\text{ pp}$$
2. **Proportional Reliability Safety Gate:**
   $$\Delta R_{\mathrm{PROPORTIONAL}} = R_{\mathrm{PROPORTIONAL}}(\text{Candidate}) - 83.694610\% \ge 0.00\text{ pp}$$
3. **Hard SOC Floor Safety Gate:**
   $$\text{Zero realized } \mathrm{SOC} < 20.00\% \text{ across all 123 origins (zero violations)}.$$
4. **Statistical Fuel Reduction Gate (Evaluated Only if Gates 1–3 Pass):**
   $$\text{Paired Wilcoxon signed-rank, two-sided } p < 0.05 \quad \text{AND} \quad \text{BCa } 95\% \text{ CI for mean fuel saving (Frozen B minus candidate, litres) strictly } > 0.$$

**Safety Precedence Invariant:** A candidate failing either reliability convention or the SOC gate is rejected regardless of fuel savings.

---

## 6. Cryptographic Integrity and Immutability Affirmation

- **Production Integrity Verification Method:** GAP19 solver and Causal NWP forecaster integrity are verified strictly by SHA-256 cryptographic hashes. Git diff is not relied upon to prove production immutability because untracked repository artifacts exist.
- **GAP19 Hash (`system/optimization/implementations/gap19_highs_native.py`):**  
  `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` (`UNCHANGED`)
- **Causal NWP Forecaster Hash (`system/forecasting/implementations/causal_nwp_physics.py`):**  
  `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` (`UNCHANGED`)
- **Telemetry Artifact Hash (`hourly_telemetry_123_frozen_b.json`):**  
  `13359f2742a0eecce14dc1c506ce0a933a9a5a441082120f83adf21d8c3f48e5` (`VERIFIED`)
- **Summary Artifact Hash (`hourly_telemetry_123_frozen_b_summary.json`):**  
  `46c412837c5713877c42aabb223b7d22be47bca09eeba25472aa675eb009396f` (`VERIFIED`)
- **Candidate S / SW Execution:** `ZERO (0)` solves. Neither candidate was implemented or executed.
