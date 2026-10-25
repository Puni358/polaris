# POLARIS 23-Horizon OFAT Experiment — Forensic Audit & Evidence Freeze Report

## 1. EVIDENCE FREEZE STATUS
- **Governance Classification**: **`A — VALID COMPLETED EXECUTION / EVIDENCE INTEGRITY VERIFIED`**
- **Freeze Status**: **FROZEN & AUTHORITATIVE**
- **MILP Solves Executed During Audit**: 0
- **Source Files Modified During Audit**: 0
- **Experiment Rerun During Audit**: NO
- **Mechanism Analysis Performed**: NO

---

## 2. ARTIFACT HASH VERIFICATION

All core execution artifacts were audited read-only using SHA-256 digest calculation:

| File Name | File Size (Bytes) | Calculated SHA-256 Digest | Expected SHA-256 Digest | Verification Result |
| :--- | :--- | :--- | :--- | :---: |
| `POLARIS_23_HORIZON_OFAT_EXECUTION_RAW.csv` | 71,714,780 | `365b477dd48b66effbeb7c4b3657901a4df0fdd02c74b9ff807ad8f88ae29d0b` | `365b477dd48b66effbeb7c4b3657901a4df0fdd02c74b9ff807ad8f88ae29d0b` | **PASS** |
| `POLARIS_23_HORIZON_OFAT_EXECUTION.json` | 6,493 | `96e24572214e358734cc7657b8b39f7bcf613417295329dceb6807b3c723f34c` | `96e24572214e358734cc7657b8b39f7bcf613417295329dceb6807b3c723f34c` | **PASS** |
| `POLARIS_23_HORIZON_OFAT_EXECUTION.md` | 403 | `9667c22bde4953c99cecd2d0666cb4ff2930dd3280f8b5c2c37fe995b2884b70` | `9667c22bde4953c99cecd2d0666cb4ff2930dd3280f8b5c2c37fe995b2884b70` | **PASS** |
| `run_polaris_23_horizon_ofat_experiment.py` | 36,379 | `63cd171c8391fbc02c571965f5508dd46ef82a5bd2c161b40dcef946b9d57b0e` | `63cd171c8391fbc02c571965f5508dd46ef82a5bd2c161b40dcef946b9d57b0e` | **PASS** |

- **Line Count Verification**: `POLARIS_23_HORIZON_OFAT_EXECUTION_RAW.csv` contains exactly **95,497 lines** (1 CSV header + 95,496 telemetry data rows).

---

## 3. STRUCTURAL COMPLETENESS & COVERAGE
- **Total Intended Solves**: 23 arms × 173 origins × 24 MPC steps = **95,496 fresh MILP solves**.
- **Actual Telemetry Rows**: **95,496**
- **Treatment Arms Coverage**: 23 / 23 treatment arms present (\(j = 1 \dots 23\)).
- **Origins Coverage**: 173 / 173 origins present per arm.
- **MPC Timestep Coverage**: 24 / 24 timesteps present per trajectory (\(k = 0 \dots 23\)).
- **Tuple Uniqueness**: 0 duplicate `(treatment_j, origin_id, mpc_timestep_idx)` tuples.
- **Missing Tuples**: 0 missing tuples.
- **Data Integrity**: 0 `NaN` or `Inf` values across numerical telemetry fields.
- **Timestamp Continuity**: 100% strict hourly timestamp continuity per trajectory.

---

## 4. EXPERIMENT SEMANTICS VERIFICATION
- **Control Semantics**: Reused frozen audited V3 Stage 8.1 control evidence (`POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv`). Zero new control solves executed.
- **Treatment Weight Matrix**: For treatment arm \(j\) (\(1 \le j \le 23\)), horizon weight \(w_j = 1.0\), and \(w_t = 0.95^t\) for all \(t \ne j\).
- **Analytical Exclusion of \(j=0\)**: \(j=0\) is mathematically identical to standard V3 (\(\gamma = 0.95\)), yielding \(\Delta_0 = 0.0\) analytically.
- **Invariants Audited**:
  - Warm starts: None (cold fresh solve per timestep).
  - Approximations: None (exact MILP solve).
  - Reduced origins: None (full 173 origins).
  - Skipped trajectories / Result-dependent stopping: None.

---

## 5. FUTURE-TRUTH FIREWALL STATUS
- **Status**: **`PASS (VERIFIED)`**
- **Evidence**: Treatment forecasts originate strictly from `Stage81ForecastEngine` backed by frozen Stage 8.1 prediction files. Future actual solar irradiance (`y_true`) is revealed only to the simulator step following optimization. Actual values were never injected into forecast vectors during optimizer execution.

---

## 6. STATE-ISOLATION STATUS
- **Status**: **`PASS (VERIFIED)`**
- **Evidence**: Initial station state at timestep 0 is initialized per origin using authoritative V3 parameters (`battery_soc_pct = 50.0%`, `battery_energy_wh = 100,000 Wh`, `diesel_running = False`). State transitions are updated strictly per origin/treatment rollout. No mutable runtime state is shared across workers or treatment arms.

---

## 7. PRIMARY ENDPOINT RECONCILIATION
Independently re-calculated paired fuel differences and Wilcoxon signed-rank tests directly from `POLARIS_23_HORIZON_OFAT_EXECUTION_RAW.csv` vs `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv`:

| Treatment Arm \(j\) | Mean Fuel Diff (L) | Median Fuel Diff (L) | Pos / Neg / Zero | Wilcoxon Stat | Raw \(p\)-value | Holm Alpha (\(\alpha_i\)) | Significant (FWER \(\le 0.05\)) | Reconciled vs JSON |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Arm 1** | +23.8149 | +23.7712 | 173 / 0 / 0 | 0.0 | \(1.62 \times 10^{-15}\) | 0.00217 | **True** | **EXACT MATCH** |
| **Arm 2** | +22.3055 | +22.2575 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00250 | **True** | **EXACT MATCH** |
| **Arm 3** | +22.5357 | +22.5020 | 173 / 0 / 0 | 0.0 | \(3.46 \times 10^{-15}\) | 0.00227 | **True** | **EXACT MATCH** |
| **Arm 4** | +22.6584 | +22.6105 | 173 / 0 / 0 | 0.0 | \(3.46 \times 10^{-15}\) | 0.00238 | **True** | **EXACT MATCH** |
| **Arm 5** | +23.9756 | +23.9298 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00263 | **True** | **EXACT MATCH** |
| **Arm 6** | +22.4884 | +22.4513 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00278 | **True** | **EXACT MATCH** |
| **Arm 7** | +23.9482 | +23.9022 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00294 | **True** | **EXACT MATCH** |
| **Arm 8** | +23.9168 | +23.8698 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00313 | **True** | **EXACT MATCH** |
| **Arm 9** | +22.3857 | +22.3482 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00333 | **True** | **EXACT MATCH** |
| **Arm 10** | +22.2915 | +22.2541 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00357 | **True** | **EXACT MATCH** |
| **Arm 11** | +23.9756 | +23.9298 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00385 | **True** | **EXACT MATCH** |
| **Arm 12** | +22.3857 | +22.3482 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00417 | **True** | **EXACT MATCH** |
| **Arm 13** | +24.0783 | +24.0321 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00455 | **True** | **EXACT MATCH** |
| **Arm 14** | +22.4786 | +22.4415 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00500 | **True** | **EXACT MATCH** |
| **Arm 15** | +22.5892 | +22.5518 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00556 | **True** | **EXACT MATCH** |
| **Arm 16** | +23.9858 | +23.9398 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00625 | **True** | **EXACT MATCH** |
| **Arm 17** | +23.9756 | +23.9298 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00714 | **True** | **EXACT MATCH** |
| **Arm 18** | +23.9756 | +23.9298 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.00833 | **True** | **EXACT MATCH** |
| **Arm 19** | +22.3857 | +22.3482 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.01000 | **True** | **EXACT MATCH** |
| **Arm 20** | +23.9756 | +23.9298 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.01250 | **True** | **EXACT MATCH** |
| **Arm 21** | +23.9756 | +23.9298 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.01667 | **True** | **EXACT MATCH** |
| **Arm 22** | +23.9756 | +23.9298 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.02500 | **True** | **EXACT MATCH** |
| **Arm 23** | +23.9756 | +23.9298 | 173 / 0 / 0 | 0.0 | \(5.06 \times 10^{-15}\) | 0.05000 | **True** | **EXACT MATCH** |

- **Reconciliation Verdict**: Zero discrepancies found between RAW CSV calculations and execution JSON/MD summaries.

---

## 8. CHECKPOINT ↔ RAW CSV RECONCILIATION
- **Total Checkpoint Artifacts**: 3,979 JSON trajectory files in `POLARIS_23_HORIZON_OFAT_CHECKPOINT/`.
- **Manifest Integration**: `manifest.json` correctly tracks all 3,979 trajectories (95,496 implied solves).
- **Data Integrity**: 100% of trajectory JSON files contain valid 24-step telemetry records matching `POLARIS_23_HORIZON_OFAT_EXECUTION_RAW.csv` line by line.

---

## 9. ARTIFACT CONSISTENCY & LIMITATIONS
- **Artifact Consistency**: All core files (`RAW.csv`, `JSON`, `MD`, `manifest.json`, checkpoint JSON files, harness script, specification files, authorization files) are 100% mutually consistent.
- **Limitations / Unverified Items**:
  - The primary endpoint analysis establishes statistical significance across all 23 treatment arms relative to V3 control.
  - Per governance directives, zero causal mechanism interpretation or horizon ranking was performed during this freeze phase.

---

## 10. FINAL CLASSIFICATION
**`A — VALID COMPLETED EXECUTION / EVIDENCE INTEGRITY VERIFIED`**

---

OFAT_EVIDENCE_FREEZE_STATUS = A

MILP_SOLVES_EXECUTED_DURING_AUDIT = 0

SOURCE_FILES_MODIFIED_DURING_AUDIT = 0

EXPERIMENT_RERUN_DURING_AUDIT = NO

MECHANISM_ANALYSIS_PERFORMED = NO

THE COMPLETED OFAT DATASET IS NOW FROZEN AS THE AUTHORITATIVE EVIDENCE FOR THE NEXT ANALYSIS PHASE.
