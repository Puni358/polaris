# POLARIS — Cloud-to-GHI Nonlinear Correction: Bootstrap Calendar-Gap Sensitivity Report

**Date:** 2026-10-10T04:06:23.570364+00:00
**Sensitivity Status:** `ROBUST_TO_GAP_SENSITIVITY`
**Primary Verdict:** Robust out-of-sample improvement confirmed across all calendar-gap formulations.

---

## 1. Executive Summary & Primary Question

**Primary Question:** Does the reported 95% confidence interval for candidate-minus-baseline daylight MAE remain entirely below zero when the stationary bootstrap respects the real-calendar discontinuity between April 30 and September 1, 2025?

**Answer:** **YES.** Under both segment-stratified and pooled boundary-terminating stationary bootstrap methods, the 95% confidence interval for Delta MAE (candidate minus baseline) remains **entirely below zero**:
- **Original Naive Circular Bootstrap:** `[-36.59, -14.66] W/m²`
- **Gap-Aware Stratified Combined (Primary):** `[-35.57, -15.65] W/m²`
- **Gap-Aware Boundary-Terminating:** `[-38.59, -14.92] W/m²`

Final Status: **`ROBUST_TO_GAP_SENSITIVITY`**

---

## 2. Invariance & Point Estimate Verification

A bootstrap sensitivity analysis evaluates sampling uncertainty and dependence structure; it does not alter model parameters, estimators, or empirical sample observations.
- **Frozen Gamma:** `0.25` (selected on 2024 training data only; unadjusted).
- **Baseline Daylight MAE:** `85.4084 W/m²` (exact match with original validation).
- **Candidate Daylight MAE:** `59.5419 W/m²` (exact match with original validation).
- **Paired Difference (Candidate − Baseline) Daylight MAE:** **`-25.8665 W/m²`** (exact match with original validation).
- **All-Hours Paired Difference MAE:** **`-8.3416 W/m²`** (exact match with original validation).

---

## 3. Methodological Comparison of Bootstrap Schemes

### A. Treatment of Temporal Seams in Original Implementation
The original validation runner sorted the 242 non-blind origins chronologically and executed a standard Politis & Romano (1994) stationary bootstrap with circular wrapping (`idx = (idx + 1) % 242`). While standard practice for stationary processes, this treats origin 119 (2025-04-30) and origin 120 (2025-09-01) as adjacent calendar days, allowing synthetic blocks of length $L \sim \text{Geom}(p=0.1)$ to cross the 123-day summer blind gap.

### B. Gap-Aware Methods Evaluated
1. **Segment-Stratified Stationary Bootstrap (Primary):**
   - The validation year naturally splits into two contiguous episodes: Segment 1 (Jan 1–Apr 30, $N_1=120$) and Segment 2 (Sep 1–Dec 31, $N_2=122$).
   - In each replicate, $N_1$ origin-days are sampled via stationary bootstrap within Segment 1, and $N_2$ origin-days are sampled via stationary bootstrap within Segment 2.
   - Blocks never cross the April-to-September seam, preserving intra-season autocorrelation without synthetic seam concatenation.
2. **Pooled Boundary-Terminating Stationary Bootstrap (Alternative):**
   - Blocks are initiated uniformly across all 242 origins.
   - Consecutive steps advance sequentially by $+1$ calendar day.
   - If a block reaches the April 30 boundary ($i=119$) or December 31 boundary ($i=241$), it terminates unconditionally and initiates a new block at a randomly sampled origin.

---

## 4. Empirical Bootstrap Results & Comparison

| Resampling Formulation | Scope / Strata | Resamples | Seed | Daylight Delta MAE Point Est. | 95% Percentile CI (Daylight) | Excludes Zero? |
|---|---|---|---|---|---|---|
| **1. Original Naive Circular** | Full 242 Origins | 2,000 | 20261010 | -25.87 W/m² | `[-36.59, -14.66]` W/m² | **YES** |
| **2. Gap-Aware Stratified (Primary)** | Full 242 Origins (Stratified) | 2,000 | 20261010 | -25.87 W/m² | `[-35.57, -15.65]` W/m² | **YES** |
| **3. Gap-Aware Boundary-Terminating** | Full 242 Origins (Pooled) | 2,000 | 20261010 | -25.87 W/m² | `[-38.59, -14.92]` W/m² | **YES** |
| **4. Contiguous Segment 1** | Jan 1 – Apr 30 ($N=120$) | 2,000 | 20261010 | -35.96 W/m² | `[-47.60, -20.40]` W/m² | **YES** |
| **5. Contiguous Segment 2** | Sep 1 – Dec 31 ($N=122$) | 2,000 | 20261010 | -11.63 W/m² | `[-15.47, -6.97]` W/m² | **YES** |

---

## 5. Segment-Specific Findings & Estimand Interpretation

- **Segment 1 (Jan–Apr 2025):** The candidate yields a large daylight error reduction (Delta MAE = -35.96 W/m², 95% CI: `[-47.60, -20.40] W/m²`). This corresponds to spring months (March–April) with high solar irradiance and significant cloud dynamics where baseline linear attenuation heavily overpredicts solar irradiance.
- **Segment 2 (Sep–Dec 2025):** The candidate yields a consistent daylight error reduction (Delta MAE = -11.63 W/m², 95% CI: `[-15.47, -6.97] W/m²`). In autumn/early winter, available solar flux is lower, reducing absolute error magnitude, but candidate superiority remains statistically decisive.
- **Impact of Stratification:** Stratifying by segment preserves the natural 120:122 origin balance. Because the candidate improves performance substantially in *both* non-blind segments, preventing blocks from spanning the gap does not undermine statistical significance; the upper bound moves from -14.66 W/m² to -15.65 W/m².

---

## 6. Safeguards, Integrity, and Audit Trail

- **Blind Population Protection:** 123 blind origins (May 1–Aug 31, 2025) were unconditionally excluded. Outcome values were not read or analyzed.
- **Artifact Preservation:** All files in `experiments/stage4_planner_cf_consistency_2025/cloud_to_ghi_nonlinear_experiment_20261010/results/` were preserved intact.
- **No Production / EMS Promotion:** Research sensitivity audit only. No operational code modified.
