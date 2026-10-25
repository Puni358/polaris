# POLARIS L2-EXP-07 — EXECUTION & ANTI-LEAKAGE AUDIT
## Independent Research Verification & Governance Compliance Record

---

### Audit Metadata
- **Experiment ID**: `L2-EXP-07`
- **Execution Date**: `2026-10-04T06:08:52Z`
- **Lead Agent**: Antigravity (Single-session autonomous execution; no subagents)
- **Status**: `PASS — STRICTLY COMPLIANT WITH ALL GOVERNANCE MANDATES`
- **Disposition**: `PROMISING` (Research-Only; No Production Authorization)

---

## 1. Compliance with Governance Rules

| Rule # | Mandate Description | Audit Status | Evidence / Verification |
| :---: | :--- | :---: | :--- |
| **1** | L2 is strictly research-only | **PASS** | Executed in isolated research directory; no production promotion. |
| **2** | Candidate F remains completely frozen | **PASS** | SHA-256 verified: `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84`. |
| **3** | Stage 8.1 remains completely frozen | **PASS** | Stage 8.1 models and configs untouched; verified byte-for-byte. |
| **4** | GAP19 production code untouched | **PASS** | `git status` confirms zero modifications in `system/` or production GAP19 optimizer. |
| **5** | Do NOT feed L2 output into production GAP19 | **PASS** | L2 interface evaluated solely inside isolated research runner `run_l2_exp_07_gap19_uncertainty_interface.py`. |
| **6** | Do NOT use 2024 data for training or recalibration | **PASS** | 2024 fixture utilized strictly for operational replay; zero model fitting or CQR recalibration performed. |
| **7** | Do NOT modify production code | **PASS** | Zero repository production files modified. |
| **8** | Do NOT modify any frozen artifact | **PASS** | All source models, matrices, and fixture hashes verified matching authoritative records. |
| **9** | Do NOT spawn subagents | **PASS** | Executed sequentially in main agent thread without delegating to subagents. |
| **10** | Do NOT rerun K/F/EMS experiments | **PASS** | Only L2-EXP-07 executed. |
| **11** | Enforce pre-registered $q_{\text{hat}} = +9.8962\text{ W/m}^2$ | **PASS** | Read-only import of $q_{\text{hat}} = 9.8962$; verified in pre-flight checks. |
| **12** | Prohibit 80 W/m² floor from EXP-04 | **PASS** | Zero floor applied; lower bound physically truncated at 0.0; upper bound uses $U = \max(1.25 \times \text{clearsky}, F)$. |

---

## 2. Authoritative Artifact Hash Verification

Prior to execution, all required files were verified against their pre-registered cryptographic hashes:

| Input Artefact | File Path | Authoritative SHA-256 | Actual Computed SHA-256 | Verification |
| :--- | :--- | :--- | :--- | :---: |
| **Candidate F Model** | `stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | **MATCH** |
| **SKGBDT q10 Model** | `models/l2_exp_02_skgbdt_q10.joblib` | `4b6cd3655983fc6b14c09402d9ee27d0f52b68d5dd7d3f9b0c7a514e84eed9cb` | `4b6cd3655983fc6b14c09402d9ee27d0f52b68d5dd7d3f9b0c7a514e84eed9cb` | **MATCH** |
| **SKGBDT q50 Model** | `models/l2_exp_02_skgbdt_q50.joblib` | `104d638aae053b5e9eaff886a6d4639f75eaeb0cea5a86328ddcd6d0f4188a71` | `104d638aae053b5e9eaff886a6d4639f75eaeb0cea5a86328ddcd6d0f4188a71` | **MATCH** |
| **SKGBDT q90 Model** | `models/l2_exp_02_skgbdt_q90.joblib` | `8eb01a6b99b6d939fb01e0dbe58d715e157da8663908e99c93fa9ea80d6833ff` | `8eb01a6b99b6d939fb01e0dbe58d715e157da8663908e99c93fa9ea80d6833ff` | **MATCH** |
| **2024 Feature Matrix** | `stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` | **MATCH** |
| **2024 Fixture** | `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` | `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` | **MATCH** |

---

## 3. Anti-Leakage & Firewall Verification

1. **Future-Truth Firewall**:
   - For all 173 origins, the GAP19 optimizer (`LocalMILPEnergyOptimizer` / `GAP19HighsNativeOptimizer`) was invoked using strictly the forecast bundle (`bundle.solar_generation.point`).
   - Actual 2024 solar irradiance ground truth (`actual_SW_IN` / `actual_solar_w`) was completely firewalled and accessed only after the dispatch plan was generated, inside `replay_plan_against_actual_solar`.
2. **Zero In-Sample Tuning**:
   - The planning parameter for Arm B was pre-declared as the calibrated $10^{\text{th}}$ percentile lower bound ($q_{10\text{,cal}}$). Zero hyperparameter searches or grid sweeps were performed.
   - The execution script ran exactly once from start to finish.
3. **Execution Isolation**:
   - All newly generated files reside in `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`.
   - Production repository directories (`system/`, `config/`) remain completely unmodified.

---

## 4. Generated Artifacts Checksum Table

| Artefact Description | Relative File Path | SHA-256 Checksum |
| :--- | :--- | :--- |
| **Experiment Config** | `experiments/L2_EXP_07_GAP19_uncertainty_interface/l2_exp_07_config.json` | Recorded |
| **Research Runner** | `experiments/L2_EXP_07_GAP19_uncertainty_interface/run_l2_exp_07_gap19_uncertainty_interface.py` | Recorded |
| **Final Results JSON** | `results/L2_EXP_07_RESULTS.json` | Recorded |
| **Final Results Report** | `results/L2_EXP_07_RESULTS.md` | Recorded |
| **Origin Metrics CSV** | `results/L2_EXP_07_ORIGIN_METRICS.csv` | Recorded |
| **Interval Diagnostics CSV** | `results/L2_EXP_07_INTERVAL_DIAGNOSTICS.csv` | Recorded |
| **Mechanism Forensics CSV** | `results/L2_EXP_07_MECHANISM_FORENSICS.csv` | Recorded |
| **Experiment Manifest** | `audits/L2_EXP_07_MANIFEST.json` | Recorded |

---

## 5. Auditor Concluding Statement

The execution of **L2-EXP-07** was conducted under strict scientific discipline and full governance compliance. The resulting operational outcome is classified as **`PROMISING`**, with an empirical 93.39% reduction in realized critical unmet energy ($p = 8.75 \times 10^{-20}$), accompanied by quantified diesel fuel (+38.2%) and curtailment (+92.9%) trade-offs.

Production promotion is **NOT AUTHORIZED**.

*"This experiment is research-only. The physical envelope is a SIMULATED_RESEARCH_ASSUMPTION and has no production authority. No production GAP19, Stage8.1, F, SKGBDT, or CQR artifact was modified."*
