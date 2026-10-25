# POLARIS STAGE 8.17A — AROME GOVERNANCE / PRE-ODD SELECTION AUDIT

**Stage**: POLARIS Stage 8.17A Forensic Governance & Pre-ODD Selection Audit  
**Audit Status**: **GOVERNANCE AUDIT COMPLETED**  
**Final Governance Verdict**: **`STAGE8_17A_GOVERNANCE: NOT PROVEN`**  
**Reason for Verdict**: Missing explicit, timestamped, standalone `STAGE8_17A_AROME_CANDIDATE_FREEZE.md/.json` artifact written to the filesystem prior to ODD target data access.  
**Active Operational Champion**: **Stage 8.16B-2 ($\text{Stage 8.1} + \Phi_{\text{inconsist}}$, 38 features | Daytime nMAE = `27.7111%`)**  
**Stage 8.17A Status**: **`ODD RESULT — GOVERNANCE REVIEW REQUIRED`**  
**Registry & Master Handoff**: **UNTOUCHED** (per governance directive)

---

## 1. Timeline of AROME Development & Execution Trace

Using filesystem timestamps, script execution code, and artifact metadata:

1. **Phase 1 — Pre-Registration & Adversarial Audit**:
   * Pre-registered the 2 candidate features (`wind_disagreement_700` and `LWP_disagreement`), 5 EVEN acceptance gates, and control baseline (`44.718895 W/m²` EVEN MAE, `35.727549 W/m²` ODD MAE).
2. **Phase 2 — Data Verification Pass**:
   * Verified spatial bounds ($700\text{ km}$ interior from Nuolja), causal timeline ($T_{\text{pub}} = t_0 - 2.5\text{h} \le t_0$), units ($\text{m/s}$ and $\text{g/m}^2$), and temporal forecast-vs-forecast alignment.
3. **Phase 3 — Unified Pipeline Execution (`run_stage8_17a_experiment.py`)**:
   * Script executed data ingestion, 5-fold forward-chaining EVEN CV, EVEN gate evaluation, and (upon passing gates) single-pass ODD evaluation in a single script run.
4. **Phase 4 — Checkpoint & Promotion Report Generation**:
   * Written to disk: `STAGE8_17A_AROME_STRUCTURAL_DISAGREEMENT_CHECKPOINT.md/.json` and `STAGE8_17A_AROME_STRUCTURAL_DISAGREEMENT_PROMOTION_CHECKPOINT.md/.json`.

---

## 2. Detailed Audit Checklist & Item Verification

### 1. Earliest AROME Structural Disagreement Artifact
* `STAGE8_17A_AROME_STRUCTURAL_DISAGREEMENT_CHECKPOINT.md` (Created: 2026-09-13T09:05:20+05:30).

### 2. First Definition of Features
* `wind_disagreement_700` and `LWP_disagreement` were defined during Pre-Registration and instantiated in `run_stage8_17a_experiment.py`.

### 3. EVEN-Only CV Results Verification
* Control EVEN MAE = `44.718895 W/m²` (reproduced exactly).
* Candidate EVEN MAE = `44.296582 W/m²` ($\Delta\text{MAE} = -0.422313\text{ W/m}^2$).
* Control EVEN nMAE = `32.3099%`, Candidate EVEN nMAE = `32.0048%` ($\Delta\text{nMAE} = -0.3051\text{ pp}$).
* EVEN RMSE = `75.892401 W/m²` (Control: `76.443487 W/m²`).
* Fold-by-fold deltas: Fold 1 ($-0.2417$), Fold 2 ($-1.2611$), Fold 3 ($+0.0856$), Fold 4 ($+0.1153$), Fold 5 ($-0.0045$).
* Improved Folds: $3 / 5$ (Folds 1, 2, 5). Worst fold degradation: $+0.115316\text{ W/m}^2$ (Fold 4).

### 4. Predefined Acceptance Gates
* All 5 predefined EVEN acceptance gates were embedded in `run_stage8_17a_experiment.py` prior to ODD evaluation:
  * Gate 1 (MAE < 44.718895): PASS
  * Gate 2 (nMAE < 32.3099%): PASS
  * Gate 3 (Folds $\ge 3/5$): PASS
  * Gate 4 (Degradation $\le +0.50$): PASS
  * Gate 5 (RMSE < 76.443487): PASS

### 5. Candidate Freeze Artifact Verification
* **FORENSIC AUDIT FINDING**: While `run_stage8_17a_experiment.py` programmatically evaluated EVEN gates before calling the ODD validation code block, **no standalone `STAGE8_17A_AROME_CANDIDATE_FREEZE.md/.json` artifact** was written to the persistent filesystem prior to ODD target access.
* In contrast, Stage 8.16B-2 generated `STAGE8_16B_2_PHI_INCONSIST_CANDIDATE_FREEZE.md/.json` as a separate, distinct file before any ODD execution script was executed.

### 6. Exact Point of ODD Target Access
* Occurred within `run_stage8_17a_experiment.py` at line 489 during script execution.

### 7. ODD Firewall & Contamination Check
* **NO** ODD tuning, **NO** ODD feature selection, **NO** ODD hyperparameter adjustment, **NO** ODD model selection occurred. Features were strictly fixed prior to script execution.

### 8. AROME Causality Evidence ($T_{\text{pub}} \le t_0$)
* Verified across all 173 ODD origins: MET Norway AROME-Arctic $18:00\text{ UTC}$ run (Day D-1) published by $21:30\text{ UTC}$ on Day D-1 ($T_{\text{pub}} = t_0 - 2.5\text{h} \le t_0$). **173/173 Causal Cutoff Verified.** No future observations or reanalyses substituted.

### 9. Protocol Equivalence
* Final ODD evaluation used identical 173 ODD origins, identical daytime mask (`actual_SW_IN > 0`), identical H1–H24 mapping, identical globally frozen Stage 4 parameters baseline (`ensemble_parameters.json`), identical nMAE denominator, identical night-zeroing rule.

---

## 3. Governance Audit Decision & Action

```
================================================================================
POLARIS STAGE 8.17A GOVERNANCE AUDIT VERDICT:
================================================================================
STAGE 8.17A GOVERNANCE: NOT PROVEN

REASON FOR VERDICT:
  The experimental script embedded EVEN CV and ODD evaluation in a single
  run, but failed to write an explicit, timestamped standalone artifact:
  STAGE8_17A_AROME_CANDIDATE_FREEZE.md / .json
  to disk prior to ODD target access.

GOVERNANCE MANDATED ACTIONS:
  1. DO NOT claim Stage 8.17A as the official operational champion.
  2. Mark Stage 8.17A held-out ODD result (Daytime nMAE = 27.3337%) as:
     "ODD RESULT — GOVERNANCE REVIEW REQUIRED"
  3. PRESERVE all existing Stage 8.17A artifacts (no deletions, no modifications).
  4. KEEP Stage 8.16B-2 (Daytime nMAE = 27.7111%) as the official operational
     champion until the governance chain is formally repaired.
  5. POLARIS_MASTER_HANDOFF.md and route registry left UNTOUCHED.
================================================================================
```

---

## 4. Generated Artifact Paths

- [STAGE8_17A_AROME_GOVERNANCE_AUDIT.md](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_17A_AROME_GOVERNANCE_AUDIT.md)
- [STAGE8_17A_AROME_GOVERNANCE_AUDIT.json](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_17A_AROME_GOVERNANCE_AUDIT.json)
