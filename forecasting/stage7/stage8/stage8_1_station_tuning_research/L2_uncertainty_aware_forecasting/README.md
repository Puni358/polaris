# POLARIS Stage 8.1 Research Branch: L2 Uncertainty-Aware Forecasting

> **Navigation & Index Workspace**  
> **Branch**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
> **Status**: ORGANIZATION + AUDIT ONLY — Self-contained index layer for future AI / AI assistant sessions.

---

## 1. Research Objective

The primary objective of the **L2 Uncertainty-Aware Forecasting** research branch is to explore and design a calibrated, uncertainty-aware forecasting layer (F + NN / L2) for the POLARIS energy management system.

While the frozen Candidate F GBDT model provides accurate point forecasts for solar irradiance ($SW_{IN}$), downstream optimizer decisions in **GAP19** require calibrated uncertainty quantification (e.g., prediction intervals, quantiles, or error variances) to hedge against persistent forecast errors without causing dispatch mismatches.

This workspace serves as the authoritative, self-contained index and navigation layer for all design specifications, audits, data references, and future experimental records associated with L2 uncertainty modeling.

---

## 2. Current Status

- **Status**: **ORGANIZATION & AUDIT ONLY**
- **Governance Locks Active**:
  - **No NN model trained**: Neural network training is currently UNAUTHORIZED.
  - **No code modified**: Candidate F, Stage 8.1, GAP19, production code, and frozen artifacts remain untouched.
  - **No experiments rerun**: Existing candidate K, F, and EMS replay experiments remain frozen.
  - **No data duplicated**: All data references point directly to existing validated artifacts.

---

## 3. Established Research Conclusions

1. **F Control Authority**: Candidate F remains the active research control model.
2. **Candidate K Trade-off**: Candidate K improved blind 2023 forecast MAE, but degraded 2024 EMS operational replay performance.
3. **K Degradation Mechanism**: K degradation is primarily driven by forecast-driven battery-dispatch mismatch; terminal reserve is **not** the dominant mechanism.
4. **F Point Forecast Limitation**: Candidate F produces point forecasts only and lacks calibrated uncertainty quantification.
5. **Residual Temporal Persistence**: Historical F residuals exhibit strong, statistically significant temporal persistence ($r = 0.4641$, $p = 3.43 \times 10^{-66}$, $R^2 = 21.54\%$), confirming the theoretical viability of L2 uncertainty modeling.
6. **Authorization Gate**: No uncertainty model is currently authorized or validated.
7. **Optimization Authority**: GAP19 remains the sole optimization authority.
8. **No Direct Overrides**: L2 must never directly override GAP19 optimizer decisions.
9. **Calibration Gate**: Any proposed uncertainty signal must pass an out-of-sample calibration gate before being supplied to GAP19.

---

## 4. Architecture

```
+-----------------------------------------------------------------------+
|                         MEPS & Station Inputs                         |
|         (38-Feature Matrix: NWP + Station Context Telemetry)          |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    Frozen Candidate F GBDT Model                      |
|                  (elevation_x_cloud.joblib, Point Preds)               |
+-----------------------------------------------------------------------+
                                   |
                                   +-------------------+
                                   |                   |
                                   v                   v
+--------------------------------------+   +----------------------------+
|        Point Forecast Signal         |   |    Historical F Residuals   |
|          (SW_IN Prediction)          |   |  (Temporal Error Pattern)  |
+--------------------------------------+   +----------------------------+
                                   |                   |
                                   +---------+---------+
                                             |
                                             v (Future Stage)
+-----------------------------------------------------------------------+
|                    L2 Uncertainty-Aware NN Model                      |
|               (Calibrated Prediction Intervals / Bounds)              |
+-----------------------------------------------------------------------+
                                   |
                                   v (Calibration Gate Passed)
+-----------------------------------------------------------------------+
|                      GAP19 Optimization Authority                     |
|                 (EMS MILP Dispatch & Reserve Controller)              |
+-----------------------------------------------------------------------+
```

---

## 5. Authoritative Input Artifacts

All key input artifacts are frozen, verified, and indexed with their SHA256 cryptographic hashes:

| # | Artifact Name | Relative File Path | SHA256 Hash |
|---|---|---|---|
| 1 | **Frozen F Model** | [`stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib) | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` |
| 2 | **Exact 2020–2023 F 38-Feature Matrix** | [`candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv) | `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde` |
| 3 | **Exact Frozen F Predictions 2020–2023** | [`candidate_L_research/CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv) | `b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0` |
| 4 | **Historical F Residual Dataset** | [`candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv) | `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` |
| 5 | **Residual Provenance Manifest** | [`candidate_L_research/CANDIDATE_F_RESIDUAL_PROVENANCE_MANIFEST.json`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_F_RESIDUAL_PROVENANCE_MANIFEST.json) | `4e0dfb08ace1ac605be6421776aa0de68c74b329620e11b565505b36c1543933` |
| 6 | **Historical Replay Forensic Audit** | [`CANDIDATE_F_HISTORICAL_REPLAY_FORENSIC_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/CANDIDATE_F_HISTORICAL_REPLAY_FORENSIC_AUDIT.md) | `cfdd3ad13769f6980230b35d3396d2848079d8a2326eacece3516cd6d23b02c2` |
| 7a | **Candidate K Manifest** | [`candidate_L_research/candidate_K_experiment/candidate_K_manifest.json`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/candidate_K_manifest.json) | `13f8f7d3f64b898bcce6004a89d6b942bb742b712aee09d6d8da956e74d32d2e` |
| 7b | **Candidate K Report** | [`candidate_L_research/candidate_K_experiment/candidate_K_report.md`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/candidate_K_report.md) | `21f48931d7aa04bf1fbfa467fbf1b6abe1def3b3a1332154189e3bc864e69897` |
| 7c | **Candidate K Blind Results** | [`candidate_L_research/candidate_K_experiment/candidate_K_blind_results.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/candidate_K_blind_results.csv) | `65d007d0ee2b2c9439ec41a0ae7c4e230e8e5ecd73276fbe614c13b19aefd261` |
| 7d | **Candidate K Validation Results** | [`candidate_L_research/candidate_K_experiment/candidate_K_validation_results.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/candidate_K_validation_results.csv) | `e2bc8daac8fcf73e6efc22da82f0670bdb2ccb780f063f9f2b2415fdd7ccd7b7` |
| 8a | **K EMS Replay Manifest** | [`candidate_L_research/candidate_K_experiment/ems_replay/EMS_REPLAY_MANIFEST.json`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/ems_replay/EMS_REPLAY_MANIFEST.json) | `77251912e433fc98f6fcfd31d7ea6c5de39e21a9ae3d7d4eeacea886f029baf1` |
| 8b | **K EMS Replay Report** | [`candidate_L_research/candidate_K_experiment/ems_replay/EMS_REPLAY_REPORT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/ems_replay/EMS_REPLAY_REPORT.md) | `c9f2dc2c0c6f24299521b702ae75ffbb016d7064ee0fe36b1fe4bdb15da32590` |
| 8c | **K EMS Degradation Forensics** | [`candidate_L_research/candidate_K_experiment/ems_replay/K_EMS_DEGRADATION_FORENSICS.md`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/ems_replay/K_EMS_DEGRADATION_FORENSICS.md) | `7a82d61bc0dc57b67583de911bd7e43fcc6c7582dbf82b81c770cc08400a51e5` |
| 8d | **K EMS Replay Results** | [`candidate_L_research/candidate_K_experiment/ems_replay/ems_replay_results.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/ems_replay/ems_replay_results.csv) | `d324c9bf8d9abb54a02ce2536b21fd45f39e3e2576dc6683f3f8bfe1c2c13c6c` |
| 9a | **Terminal Reserve Ablation Manifest** | [`candidate_L_research/candidate_K_experiment/ems_replay/TERMINAL_RESERVE_ABLATION_MANIFEST.json`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/ems_replay/TERMINAL_RESERVE_ABLATION_MANIFEST.json) | `eeb33913eeb1d7ae907107147b82e0e8f1f57ddb1764fe1b93e47893e0462195` |
| 9b | **Terminal Reserve Ablation Report** | [`candidate_L_research/candidate_K_experiment/ems_replay/TERMINAL_RESERVE_ABLATION_REPORT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/ems_replay/TERMINAL_RESERVE_ABLATION_REPORT.md) | `190fa9592d25e79dbd27dc25ffec20a29371a7b5c7c840d2aacc249c35478842` |
| 9c | **Terminal Reserve Ablation Results** | [`candidate_L_research/candidate_K_experiment/ems_replay/terminal_reserve_ablation_results.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/ems_replay/terminal_reserve_ablation_results.csv) | `f26b6757300eb1c861649274ed7facd66fb8fffbc838add8e44b848516804107` |
| 10 | **K/F Dispatch Interaction Forensics (Reserve Off)** | [`candidate_L_research/candidate_K_experiment/ems_replay/K_F_DISPATCH_INTERACTION_FORENSICS_RESERVE_OFF.md`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/candidate_K_experiment/ems_replay/K_F_DISPATCH_INTERACTION_FORENSICS_RESERVE_OFF.md) | `c7eb017adb913a3dc9a38e4f085a39227ba2d808e761b370de453c02301f75d1` |

---

## 6. What is VERIFIED

- **Candidate F Control Stability**: Candidate F yields consistent 2020–2023 predictions with $0\text{ NaNs}$ or $0\text{ Infs}$.
- **Residual Dataset Integrity**: 26,011 rows across 1,369 forecast origins fully verified against SITES Nuolja observations.
- **Error Persistence Signal**: Statistically significant lag-1 residual correlation ($r = 0.4641, p = 3.43 \times 10^{-66}$), establishing over $21.5\%$ variance predictability.
- **K Degradation Diagnosis**: Proven by forensic ablation that Candidate K's EMS performance loss stems from battery-dispatch mismatch rather than terminal reserve constraints.
- **Optimization Boundaries**: GAP19 remains intact, isolated, and verified as the single source of truth for MILP dispatch optimization.

---

## 7. What is UNKNOWN

- **Optimal Uncertainty Model Architecture**: Neural network architecture choices (e.g. Pinball loss multi-quantile network vs. Deep Ensembles vs. Conformalized Quantile Regression) are unassessed.
- **Calibration Empirical Coverage**: Empirical coverage (e.g. 80%, 90%, 95% nominal bounds) across solar regimes has not been calculated or verified.
- **GAP19 Interface Mechanism**: Mathematical translation of L2 uncertainty estimates into GAP19 chance constraints or penalty formulations remains to be formulated.
- **Out-of-Sample EMS Impact**: Performance impact of uncertainty-aware inputs on full-horizon 2024 EMS operating costs is unquantified.

---

## 8. Explicit "DO NOT REOPEN" Items

> [!CAUTION]
> The following research findings and governance decisions are **LOCKED** and must **NOT** be reopened, retested, or modified in future sessions:

1. **DO NOT attempt to replace Candidate F as the control model** without prior forensic authorization.
2. **DO NOT retrain or alter Candidate K**.
3. **DO NOT attribute Candidate K's EMS degradation to terminal reserve**. The ablation forensic audit conclusively proved battery dispatch mismatch is the primary cause.
4. **DO NOT build an L2 model that directly overrides GAP19 optimization decisions**.
5. **DO NOT supply uncalibrated uncertainty signals to GAP19**. Passing an out-of-sample calibration gate is mandatory.
6. **DO NOT modify frozen artifacts, Stage 8.1 code, or production modules**.

---

## 9. Directory Structure

```
L2_uncertainty_aware_forecasting/
├── README.md                           # This primary navigation & index document
├── L2_RESEARCH_MANIFEST.json           # Machine-readable provenance & hash manifest
├── design/                             # Architecture specifications & design contracts
├── data/                               # Data index & reference pointers (no large copies)
├── audits/                             # Feasibility, forensic, & calibration gate audits
├── experiments/                        # Experiment specifications & runner scripts
├── results/                            # Evaluation metrics & summary tables
└── scripts/                            # Self-contained audit & helper utilities
```

---

## 10. Next Planned Step

**Phase 1 Execution**: Conduct the **L2 Uncertainty-Model Feasibility & Design Audit**.
- Formulate model requirements (loss functions, interval bounds, input features).
- Establish the formal **Out-of-Sample Calibration Gate** criteria.
- Draft the **GAP19 Uncertainty Interface Specification** (ensuring GAP19 retains full decision authority).
