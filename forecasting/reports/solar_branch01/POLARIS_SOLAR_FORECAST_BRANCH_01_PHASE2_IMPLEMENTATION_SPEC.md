# POLARIS_SOLAR_FORECAST_BRANCH_01 — PHASE 2 GOVERNED IMPLEMENTATION SPECIFICATION

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `PHASE 2 GOVERNED IMPLEMENTATION SPECIFICATION`  
**Authorization:** `PHASE 2 IMPLEMENTATION SPECIFICATION ONLY`  
**Phase 2 Status:** `PASS`  
**Next Governed Step:** `PHASE2_GOVERNANCE_REVIEW`  

---

## 1. Executive Summary & Authorization Boundary

This document defines the implementation architecture for converting the approved Phase 1 specification of `POLARIS_SOLAR_FORECAST_BRANCH_01` into a deterministic, fully testable, and reproducible software design.

### Strict Firewall Assertions:
- **STAGE 8.1 FIREWALL**: `STAGE8_1_MODIFIED = NO`, `STAGE8_1_RETRAINED = NO`. Stage 8.1 champion files remain 100% isolated.
- **CANDIDATE A FIREWALL**: `CANDIDATE_A_IMPLEMENTED = NO`, `CANDIDATE_A_EXECUTED = NO`.
- **EMS FIREWALL**: `EMS_MODIFIED = NO`, `EMS_EXECUTED = NO`. No EMS optimization or simulation executed.
- **TRAINING FIREWALL**: `NEW_MODEL_TRAINED = NO`, `NEW_MODEL_INFERRED = NO`, `PHASE3_TRAINING_STARTED = NO`. No model fitting or hyperparameter tuning has been performed.

---

## 2. Dedicated Branch Namespace & Architecture

All Branch 01 components are assigned to a dedicated directory structure:

```
forecasting/
└── solar_branch_01/
    ├── specification/
    ├── implementation/
    │   ├── data_loader.py
    │   ├── nwp_selector.py
    │   ├── feature_builder.py
    │   ├── split_builder.py
    │   ├── baseline_engine.py
    │   └── model_interface.py
    ├── tests/
    ├── configs/
    ├── datasets/
    ├── models/
    ├── runs/
    └── governance/
```

---

## 3. NWP Implementation & Lead-Coverage Audit

### Read-Only Coverage Audit Summary:
- **Total Supported MPC Origins**: 8,784 hourly origins across calendar year 2024.
- **Base Issue Run**: 00:00 UTC daily AROME 21x21 forecast runs.
- **Lead Shifting Formula**: For MPC origin $t$ and target horizon $h \in [1..24]$, the effective lead index is:
  $$H_{\text{effective}} = h + (t - t_{\text{issue}})$$
- **Lead Range**: Spans 1h (origin 00:00 UTC, $H1$) up to 42h (origin 18:00 UTC, $H24$).
- **Horizon Coverage**: 100.0% (8,784 complete origins, 0 missing horizons).
- **Causality Rule**: $t_{\text{issue}} \le t$. Future issue runs are strictly forbidden.

---

## 4. Train / Validation / Test Implementation with 24h Embargo

- **Train Split**: `2024-01-01T00:00:00Z` to `2024-08-31T23:00:00Z` (5,856 hours)
- **Validation Split**: `2024-09-01T00:00:00Z` to `2024-10-31T23:00:00Z` (1,464 hours)
- **Test Split (Frozen)**: `2024-11-01T00:00:00Z` to `2024-12-31T23:00:00Z` (1,464 hours)
- **24-Hour Boundary Embargo**: Origins $t \in [\text{split\_end} - 24h, \text{split\_end}]$ are excluded from feature/target construction to guarantee zero $t+24h$ target leakage across split boundaries.

---

## 5. Model Serialization & Independent Replay Architecture

- **Fitted Binary Format**: `.joblib` for tabular tree/linear models; `.pt` for PyTorch neural models.
- **SHA-256 Hashing**: Computed directly on model binary bytes and stored in `model.sha256`.
- **Process-Isolated Independent Replay**: Spawns a separate Python process loading serialized model binaries from disk to run inference on test features and compare output predictions against `predictions.json` within tolerance ($\text{atol}=1e-5$).

---

## 6. Substantial Training Execution Rule

For all future authorized model training runs:
- **Parallel Workers**: 8 workers where technically appropriate (or explicit technical reason if inappropriate).
- **Execution Monitoring**: Checkpoint/resume capability, live progress reporting, CPU/RAM/GPU and thermal monitoring, persistent logging (`training.log`), and SIGINT/SIGTERM handlers.
- **Immutable Run Storage**: `artifacts/model_runs/RUN_<YYYYMMDD_HHMMSS>_<HASH>/`. Never overwrite previous runs.

---

## 7. Required Final Status Block

```
BRANCH_ID =
POLARIS_SOLAR_FORECAST_BRANCH_01

PHASE0_RECONNAISSANCE =
COMPLETE

PHASE0_GOVERNANCE_REVIEW =
COMPLETE

PHASE1_SPECIFICATION =
COMPLETE

PHASE1_GOVERNANCE_REVIEW =
PASS

PHASE2_IMPLEMENTATION_SPECIFICATION =
PASS

STAGE8_1_MODIFIED =
NO

STAGE8_1_RETRAINED =
NO

STAGE8_1_REPLACED =
NO

CANDIDATE_A_IMPLEMENTED =
NO

CANDIDATE_A_EXECUTED =
NO

NEW_MODEL_TRAINED =
NO

NEW_MODEL_INFERRED =
NO

EMS_MODIFIED =
NO

EMS_EXECUTED =
NO

NWP_ISSUE_TIME_CAUSALITY =
PASS

NWP_LEAD_COVERAGE =
CONDITIONAL

24H_CAUSAL_HORIZON =
PASS

IMPLEMENTATION_MATRIX =
COMPLETE

TEST_PLAN =
COMPLETE

MODEL_RUN_MANIFEST_SCHEMA =
COMPLETE

TRAINING_REPRODUCIBILITY_CHECKLIST =
COMPLETE

MODEL_TRAINING_AUTHORIZATION =
NOT_GRANTED

EMS_INTEGRATION_AUTHORIZATION =
NOT_GRANTED

NEXT_GOVERNED_STEP =
PHASE2_GOVERNANCE_REVIEW
```
