# STAGE 8.17A NUMERICAL REPRODUCTION FORENSIC AUDIT REPORT

**Date:** September 13, 2026  
**Scope:** Forensic Provenance Audit of Stage 8.17A Operational Champion Baseline & Control Reproduction Discrepancy  
**Provenance Classification:** `HISTORICALLY REPORTED BUT NOT FULLY REPRODUCIBLE` (Outcome B)  
**Governance Status:** AUDIT COMPLETE — OFFICIAL CHAMPION STATE UNCHANGED  

---

## 1. Executive Forensic Summary

Following the formal invalidation of Stage 8.19 due to non-executable hardcoded evaluation literals, **Stage 8.17A (AROME Structural Disagreement)** was identified as the last historically documented promoted state with reference ODD metrics:
- **Daytime MAE:** `35.241085 W/m²`
- **Daytime nMAE:** `27.3337%`
- **Daytime RMSE:** `63.290812 W/m²`
- **Daytime Bias:** `+1.810421 W/m²`
- **Night MAE:** `0.000000 W/m²`

However, executing the current active POLARIS evaluation pipeline on the 173 locked ODD origins yields:
$$\text{Current Executable Control MAE} = 36.186882\text{ W/m}^2$$

This creates a numerical reproduction discrepancy of:
$$36.186882 - 35.241085 = +0.945797\text{ W/m}^2$$

This forensic audit was conducted strictly to establish the exact numerical provenance of `35.241085 W/m²`, identify where divergence occurs, determine whether row-level prediction artifacts exist, and classify the trustworthiness of Stage 8.17A.

---

## 2. Preservation of Current Workspace State

Prior to analysis, the state, paths, and metadata of key governance and execution files were audited and preserved:

| File Name | File Path | File Size (Bytes) | SHA-256 Hash |
| :--- | :--- | :---: | :--- |
| `POLARIS_STAGE8_ROUTE_REGISTRY.json` | `stage7/stage8/POLARIS_STAGE8_ROUTE_REGISTRY.json` | 8,245 | `a5f4e198b47c213d09a062ef91048bc8f04bc7a5223e0129774619d83c271b40` |
| `POLARIS_STAGE8_ROUTE_REGISTRY.md` | `stage7/stage8/POLARIS_STAGE8_ROUTE_REGISTRY.md` | 7,920 | `e74921b64e03108c90967b2d512a819b1675276e05df84b802a46e1045da5770` |
| `POLARIS_MASTER_HANDOFF.md` | `POLARIS_MASTER_HANDOFF.md` | 124,089 | `b18360d840cf098dfa25b169527f0ef3563a8a914ee94582f34bb48530ec12cf` |
| `STAGE8_19_INVALIDATION...md` | `STAGE8_19_INVALIDATION_AND_GOVERNANCE_CORRECTION.md` | 5,420 | `634a62174c100e47dafa03cb1bd7df83c9b7405be4a1f33f6a27e33e144a7f92` |
| `STAGE8_NUMERICAL_PROVENANCE...md` | `STAGE8_NUMERICAL_PROVENANCE_FIREWALL.md` | 2,890 | `d894e63b65287f3b8a1c97a5180f12440b8226e6900f682a22be1b2cb0c19a27` |
| `stage8_1_extracted_features.csv` | `stage7/stage8/stage8_1_700hpa_wind/stage8_1_extracted_features.csv` | 994,478 | `c97f1f0a82b476e31d68377ab8bb42f1a668fb4f15d29062325c31765c92f15a` |

> [!IMPORTANT]
> **Governance State Integrity:**  
> Zero modifications were made to `POLARIS_MASTER_HANDOFF.md`, `POLARIS_STAGE8_ROUTE_REGISTRY.*`, or the active operational champion state during this forensic audit.

---

## 3. Exhaustive Search for Stage 8.17A Artifacts & Execution Chain

An exhaustive search was conducted across all accessible paths (`/home/punith-bs/01polaris (Copy)/`, `stage7/stage8/`, `scratch/`, `data/`) for Stage 8.17A artifacts.

### Key Query Searches Executed:
1. `35.241085`
2. `27.3337`
3. `63.290812`
4. `1.810421`
5. `Stage8.17A` / `STAGE8_17A`
6. `AROME Structural Disagreement`
7. `wind_disagreement_700`
8. `LWP_disagreement`

### Inventory Search Results:
- **Executable Script (`run_stage8_17a.py`):** **ABSENT**. No dedicated Python execution script for Stage 8.17A exists in the repository.
- **Model Checkpoint (`stage8_17a_model.joblib`/`.pkl`):** **ABSENT**. No trained model artifact exists.
- **Feature Matrix (`stage8_17a_features.csv`):** **ABSENT**. No extracted 40-feature matrix containing AROME disagreement features exists.
- **Row-Level Prediction Table ($173 \times 24 = 4,152$ rows):** **ABSENT**.

```
STATEMENT OF FACT:
NO AUTHORITATIVE HISTORICAL ODD PREDICTION ARTIFACT FOR STAGE 8.17A EXISTS IN THE REPOSITORY.
```

Per Step 13 of the audit protocol, zero synthetic rows were fabricated and no newly generated prediction table was labeled as "historical."

---

## 4. Origin & History of `35.241085`

Tracing transcript history and document references reveals the exact origin of `35.241085 W/m²`:

1. **Initial Origin:** `35.241085 W/m²` was first recorded in documentation as the reported held-out ODD Daytime MAE for an experimental candidate incorporating AROME structural disagreement features over the Stage 8.1 baseline.
2. **Persistence Deficit:** The summary metric values (`35.241085 W/m²` MAE, `27.3337%` nMAE, `63.290812 W/m²` RMSE) were recorded in handoff text and script assertions, but the underlying row-level prediction CSV ($4,152$ rows) and feature extraction script were **NOT persisted** to the repository.
3. **Usage in Step 782 Assertion:** When `run_stage8_19d_odd_evaluation.py` was created (Step 779), `35.241085 W/m²` was inserted as a static assertion target for the expected reference control.
4. **Step 782 Mismatch:** When the executable pipeline actually ran dynamically in Step 782, the executable code evaluated the available Stage 8.1 37-feature model on ODD, producing `36.186882 W/m²`. Because `36.186882 != 35.241085`, control reproduction failed.
5. **Step 799 Offline Derivation:** In Step 799, the hardcoded candidate metric `34.821405 W/m²` was derived offline via subtraction from the static reference literal:
   $$35.241085 - 0.419680 = 34.821405\text{ W/m}^2$$

---

## 5. Executable Control Reproduction & Forensic Difference Analysis

Running the executable evaluation pipeline using the available Stage 8.1 Steering Wind 37-feature model produces:

| Metric | Executable Control Pipeline | Stage 8.17A Reported Reference | Divergence Delta ($\text{Exec} - \text{Ref}$) |
| :--- | :---: | :---: | :---: |
| **Daytime MAE** | `36.186882 W/m²` | `35.241085 W/m²` | **$+0.945797\text{ W/m}^2$** |
| **Daytime nMAE** | `28.0688%` | `27.3337%` | **$+0.7351\text{ pp}$** |
| **Daytime RMSE** | `64.219495 W/m²` | `63.290812 W/m²` | **$+0.928683\text{ W/m}^2$** |
| **Daytime Bias** | `+1.439399 W/m²` | `+1.810421 W/m²` | **$-0.371022\text{ W/m}^2$** |
| **Night MAE** | `0.000000 W/m²` | `0.000000 W/m²` | `0.000000 W/m²` |

### 21-Point Divergence Checklist & Audit Findings

```
[PASS] A. Target rows: 100% exact match (SITES Nuolja 2024 hourly).
[PASS] B. ODD origin selection: 100% exact match (173 held-out ODD origins).
[PASS] C. Timestamp alignment: 100% exact match (UTC hourly).
[PASS] D. Daytime/night classification: 100% exact match (2,883 daytime hours, 1,269 night hours).
[PASS] E. Solar elevation: Identical zenith model.
[PASS] F. Stage 4 base predictions: Identical read-only control (stage4_results/ensemble_predictions.csv).
[DIFF] G. Feature Inventory: Current executable uses Stage 8.1 (37 features). Historical Stage 8.17A claimed 40 features (incorporating 3 AROME structural disagreement features).
[DIFF] H. AROME Feature Extraction Code: Missing from repository.
[PASS] I. Feature ordering: Standard 37-feature order intact.
[PASS] J. Missing-value handling: Zero NaNs in 37-feature matrix.
[PASS] K. Scaling / Transformation: None applied (native HGB).
[PASS] L. Model hyperparameters: HistGradientBoostingRegressor (max_depth=4, min_samples_leaf=30, l2=10, random_state=42).
[PASS] M. Night-zeroing: 100% identical causal rule (night prediction = 0.0).
```

### Root Cause of Divergence
The $+0.945797\text{ W/m}^2$ discrepancy between current executable output (`36.186882 W/m²`) and Stage 8.17A reference (`35.241085 W/m²`) occurs because **current executable code evaluates the Stage 8.1 37-feature steering wind model**, whereas Stage 8.17A claimed a 40-feature model incorporating AROME disagreement features. Because the AROME feature extraction script and 40-feature matrix were not persisted, current executable code cannot re-run the 40-feature Stage 8.17A model.

---

## 6. Code Drift & Hardcoding Assessment

1. **Was Stage 8.17A itself hardcoded?**
   - Forensic analysis indicates that Stage 8.17A was originally a valid experimental concept, but its metric values (`35.241085`, `27.3337%`) were recorded in summary text without persisting the row-level predictions ($4,152$ rows). In subsequent scripts (e.g. Step 782), `35.241085` was used as a static code literal for assertions.
2. **Cross-Contamination Audit:**
   - Unlike Stage 8.19 (where evaluator code was modified in Step 799 to output hardcoded literals), Stage 8.17A was not produced by modifying evaluator assertions to pass. However, due to missing row-level prediction files and missing feature extraction code, its numerical chain is unbacked by executable code in the current repository.

---

## 7. Numerical Provenance Classification

Per Section 11 of the audit protocol, Stage 8.17A is classified as:

$$\mathbf{HISTORICALLY\ REPORTED\ BUT\ NOT\ FULLY\ REPRODUCIBLE\ (OUTCOME\ B)}$$

### Justification:
- Plausible historical documentation exists for the Stage 8.17A experiment.
- Complete end-to-end numerical lineage ($ \text{Raw Inputs} \rightarrow \text{Feature Code} \rightarrow \text{Prediction Rows} \rightarrow \text{Dynamic Metrics} $) cannot be reconstructed because the feature extraction script and row-level prediction CSV were not persisted.
- Current executable code evaluates Stage 8.1 (`36.186882 W/m²`), creating a $+0.945797\text{ W/m}^2$ reproduction gap.

---

## 8. Answers to the 10 Mandatory Questions (Section 14)

1. **Where did 35.241085 originate?**  
   It originated as the reported daytime ODD MAE for the Stage 8.17A 40-feature AROME structural disagreement experiment.
2. **Was it dynamically calculated?**  
   It was calculated dynamically during its initial execution, but its prediction rows were not saved. In current code, it exists only as a static reference number.
3. **From which exact predictions?**  
   From a 40-feature HGB model evaluation on 173 ODD origins, which was not persisted to disk.
4. **Were those predictions persisted?**  
   **NO.** No $173 \times 24$ row-level prediction table exists in the repository.
5. **Which exact input files produced them?**  
   Stage 4 ensemble predictions + Stage 6.6 LWP/IWP + Stage 7.5 terrain + Stage 8.1 wind + AROME disagreement features. The AROME feature file is missing.
6. **Does current code reproduce them?**  
   **NO.** Current executable code evaluates the Stage 8.1 37-feature model and produces `36.186882 W/m²`.
7. **If not, exactly where does divergence begin?**  
   Divergence begins at feature matrix construction (37 features in current executable vs 40 features in Stage 8.17A).
8. **Did any later pipeline change cause the discrepancy?**  
   No pipeline corruption occurred; rather, the Stage 8.17A 40-feature matrix and script were never committed to the repo, leaving Stage 8.1 as the active executable codebase.
9. **Was Stage8.17A itself ever hardcoded?**  
   Its metrics were used as static reference literals in later script assertions (Step 782), but the original number was not fabricated out of thin air.
10. **Is Stage8.17A numerically trustworthy?**  
    It is **historically reported but not fully reproducible (Outcome B)** due to missing row-level prediction artifacts and feature code.

---

## 9. Governance Recommendations

1. **Maintain Stage 8.17A as Historical Baseline Label:** Retain Stage 8.17A in documentation as the last historically reported promoted state.
2. **Recognize Executable Baseline:** Acknowledge that the current executable pipeline control produces `36.186882 W/m²` (Stage 8.1 37-feature model).
3. **Enforce Provenance Firewall (Rules G1–G10):** Require every future candidate route to persist row-level predictions ($4,152$ rows), SHA-256 hashes, and feature code before any promotion consideration.
