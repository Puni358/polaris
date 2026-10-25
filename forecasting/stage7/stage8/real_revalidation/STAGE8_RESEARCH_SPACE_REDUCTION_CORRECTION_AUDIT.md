# POLARIS STAGE 8 — RESEARCH-SPACE REDUCTION CORRECTION AUDIT

> [!IMPORTANT]
> **GOVERNANCE STATUS: FORMAL PROVENANCE CORRECTION AUDIT ONLY**
> - **Purpose:** Correct the recorded classification and scientific rationale for Stage 8.24 and Stage 8.17A in the Research-Space Reduction Report to ensure future Opus research handoffs receive accurate provenance.
> - **Operational Champion:** **Stage 8.1 37-feature HGB Model**
> - **Protected Held-out ODD Metrics:** **MAE 36.188657 W/m² \| nMAE 28.0688% \| RMSE 64.219495 W/m² \| Bias +1.439399 W/m²**
> - **ODD Benchmark Status:** **100% UNTOUCHED & PROTECTED (`ODD_RUN = FALSE`)**
> - **No models trained, no ODD evaluations executed, no route registries modified.**

---

## Executive Summary of Corrections

This audit records two critical provenance corrections applied to the POLARIS Research-Space Reduction Report ([`STAGE8_RESEARCH_SPACE_REDUCTION_REPORT.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_RESEARCH_SPACE_REDUCTION_REPORT.md)):

1. **Correction 1 (Stage 8.24 Orographic Flow):** Updated classification from generic `REJECTED_BY_EXPERIMENT` to **`PROVISIONAL_REJECTION_IMPLEMENTATION_QUALIFIED`**. The executed experiment degraded EVEN CV ($\Delta\text{MAE} = +0.3972\text{ W/m}^2$), but used an approximate 2-point implementation rather than the exact pre-registered $P_{\text{sfc}} \to 700\text{ hPa}$ continuous Brunt–Väisälä stability formulation.
2. **Correction 2 (Stage 8.17A AROME Disagreement):** Updated classification from "lack of causal delivery" to **`REJECTED_BY_REAL_DATA_REVALIDATION`**. Canonical real AROME data (`arome_arctic_347_origins_real_subset.csv`) was recovered with 100% coverage across all 347 origins, and a formal real-data revalidation proved that AROME disagreement features degraded held-out ODD performance ($\Delta\text{MAE} = +0.2154\text{ W/m}^2$).

---

## 1. Detailed Audit: Correction 1 — Stage 8.24 Orographic Flow

### A. Problem Statement & Original Wording
- **Original Wording:** Classified Stage 8.24 as `REJECTED_BY_EXPERIMENT` with the claim that "GBT already infers stability from 3D winds, therefore Froude is redundant."
- **Defect:** This wording implied the executed script was a fully faithful test of the pre-registered specification, and asserted an unproven hypothesis as a established fact.

### B. Forensic & Empirical Facts
1. **Executed Numerical Result (Preserved Intact):**
   - Control EVEN MAE: `37.6308 W/m²`
   - Candidate EVEN MAE: `38.0280 W/m²`
   - Delta MAE: **`+0.3972 W/m²`** (Degraded)
   - Improving Folds: `1 / 5 folds` (Worst fold degradation: `+1.1857 W/m²`)
   - Gates: G1–G4 **FAIL**, G5–G6 **PASS**
   - ODD Run: **NOT EXECUTED**
2. **Implementation Qualification:**
   - The pre-registered spec required continuous layer-integrated Brunt–Väisälä stability $N$ over $P_{\text{sfc}} \to 700\text{ hPa}$.
   - The executed script utilized an approximate 2-point construction ($p_{\text{sfc}} = 93500\text{ Pa}$, $p_{700} = 70000\text{ Pa}$, $t_{700}$ estimated from $t_{\text{2m}}$, $q_{700}$ estimated from $q_{\text{sfc}}$).

### C. Corrected Classification & Handoff Wording
- **Corrected Classification:** **`PROVISIONAL_REJECTION_IMPLEMENTATION_QUALIFIED`**
- **Corrected Statement:**
  > "The Stage 8.24 executed candidate degraded under EVEN validation, but the executed Froude implementation did not exactly match the pre-registered atmospheric-definition specification. Therefore the result is not a fully faithful validation of the pre-registered Froude formulation."
- **Exact Handoff Boundaries:**
  - *Demonstrated:* The executed approximate 2-point $U_\perp$ + Froude implementation degraded the EVEN benchmark.
  - *NOT Demonstrated:* The scientifically exact pre-registered Froude formulation has NOT been independently validated as ineffective.
  - *Reopen Condition:* Only reopen if a governance-approved rerun using the exact pre-registered Froude/N definition is scientifically justified and authorized.

---

## 2. Detailed Audit: Correction 2 — Stage 8.17A AROME Disagreement

### A. Problem Statement & Original Wording
- **Original Wording:** "AROME point subset lacked causal real-time delivery; feature extraction failed EVEN CV robustness gates."
- **Defect:** Conflated earlier missing input artifacts with the final real-data revalidation result, incorrectly presenting "lack of causal delivery" as the primary closure reason.

### B. Forensic & Empirical Facts
1. **Canonical Real Data Recovery:**
   - Dataset: `arome_arctic_347_origins_real_subset.csv`
   - Coverage: 347/347 benchmark origins (100% complete, 8,328 horizon tuples, 0 synthetic/padded values).
2. **Formal Real-Data Revalidation Results:**
   - EVEN Validation: Control MAE $= 44.7189\text{ W/m}^2$, Candidate MAE $= 44.5535\text{ W/m}^2$, Delta $= -0.1654\text{ W/m}^2$ (Passed EVEN gates).
   - Held-out ODD Evaluation:
     - Control MAE $= \mathbf{36.2110\text{ W/m}^2}$ \| Candidate MAE $= \mathbf{36.4264\text{ W/m}^2}$ \| Delta MAE $= \mathbf{+0.2154\text{ W/m}^2}$ (Degraded)
     - Control nMAE $= \mathbf{28.0861\%}$ \| Candidate nMAE $= \mathbf{28.2532\%}$ \| Delta nMAE $= \mathbf{+0.1671\text{ pp}}$ (Degraded)
     - Control RMSE $= \mathbf{64.2305\text{ W/m}^2}$ \| Candidate RMSE $= \mathbf{64.6116\text{ W/m}^2}$ \| Delta RMSE $= \mathbf{+0.3811\text{ W/m}^2}$ (Degraded)
     - Control Bias $= +0.9946\text{ W/m}^2$ \| Candidate Bias $= +0.5380\text{ W/m}^2$
     - Bootstrap mean delta $= +0.1774\text{ W/m}^2$ ($95\%$ CI $[-0.1127, +0.4749]$, only $11.81\%$ resamples improving).

### C. Corrected Classification & Handoff Wording
- **Corrected Classification:** **`REJECTED_BY_REAL_DATA_REVALIDATION`**
- **Corrected Scientific Rationale:**
  > "AROME-Arctic disagreement features (`wind_disagreement_700` and `LWP_disagreement`) failed to provide incremental predictive skill on the locked real-data ODD benchmark and degraded MAE/nMAE/RMSE relative to the frozen Stage 8.1 control."
- **Exact Handoff Boundaries:**
  - Historical unverified results are NOT the basis for closure. The **real-data revalidation IS the sole basis for closure**.
  - Does NOT demonstrate that AROME data is unusable or unavailable; real data is 100% complete.
  - *Reopen Condition:* Only reopen if a materially different AROME physical representation is proposed and independently justified with verified causal real-data provenance.

---

## 3. Comparison Matrix of Corrections

| Route | Original Incorrect Wording | Corrected Handoff Wording | Corrected Classification |
| :--- | :--- | :--- | :---: |
| **Stage 8.24** | "Proven redundant; GBT already infers Froude" | Executed candidate degraded EVEN (+0.3972 W/m²), but implementation used a 2-point approximation. Pre-registered spec remains un-falsified. | **`PROVISIONAL_REJECTION_IMPLEMENTATION_QUALIFIED`** |
| **Stage 8.17A** | "Lacked causal real-time delivery; feature extraction failed EVEN" | Real AROME revalidation (100% coverage) degraded held-out ODD (+0.2154 W/m² MAE, +0.1671 pp nMAE). | **`REJECTED_BY_REAL_DATA_REVALIDATION`** |

---

## Final Governance Confirmation

- **Operational Champion:** Stage 8.1 37-feature HGB Model (ODD daytime nMAE 28.0688%)
- **ODD Benchmark Dataset:** **100% UNTOUCHED & PROTECTED (`ODD_RUN = FALSE`)**
- **Master Handoff (`POLARIS_MASTER_HANDOFF.md`):** UNTOUCHED
- **Route Registry (`POLARIS_STAGE8_ROUTE_REGISTRY`):** UNTOUCHED
- **Historical Numerical Metrics:** 100% PRESERVED

---

*Correction Audit generated under POLARIS Stage 8 Governance Guidelines on 2026-09-13.*
