# POLARIS_SOLAR_FORECAST_BRANCH_01 — TRAINING SPECIFICATION GOVERNANCE CORRECTION REPORT

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `TRAINING SPECIFICATION GOVERNANCE CORRECTION`  
**Authorization:** `READ-ONLY CORRECTION ONLY`  
**Correction Gate Status:** **`PASS`**  
**Training Authorization State:** **`MODEL_TRAINING_AUTHORIZATION = NOT_GRANTED`**  

---

## 1. Summary of Applied Documentation Corrections

The two documentation corrections required by the Training Specification Governance Review have been applied across all affected specification artifacts:

### 1.1 Corrected Observations vs. Supported Origins (`PASS`)
- **Raw Hourly Observations ($N_{\text{OBSERVATIONS}}$)**: `8,832` raw hourly rows in 2024.
- **Supported MPC Origins ($N_{\text{SUPPORTED\_ORIGINS}}$)**: `8,784` valid hourly forecast origins ($8,832 - 48$).
- **Applied Changes**: `POLARIS_SOLAR_FORECAST_BRANCH_01_TRAINING_SPECIFICATION.md` (Section 2 & 3), `POLARIS_SOLAR_FORECAST_BRANCH_01_TRAINING_SPECIFICATION.json`, and `POLARIS_SOLAR_FORECAST_BRANCH_01_TRAINING_DATA_CONTRACT.csv` now explicitly state raw observation count $N_{\text{OBSERVATIONS}} = 8,832$ and derived origin count $N_{\text{SUPPORTED\_ORIGINS}} = 8,784$.

### 1.2 Removed Unauthorized "20-Point" Terminology (`PASS`)
- **Terminology Purged**: Removed all instances of `"20-Point Reproducibility Package"` and `"20-Point Permanent Training Governance Rule"`.
- **Authoritative Terminology Enforced**: All artifacts now strictly reference `MODEL_RUN_MANIFEST_SCHEMA` and the `34-item TRAINING_REPRODUCIBILITY_CHECKLIST`.
- **Applied Changes**: Updated `POLARIS_SOLAR_FORECAST_BRANCH_01_TRAINING_SPECIFICATION.md` (Section 10) and `POLARIS_SOLAR_FORECAST_BRANCH_01_TRAINING_REPRODUCIBILITY_PLAN.md` (Section 1).

---

## 2. Preserved Governed Contracts

1. **Feature Contract (`UNCHANGED`)**:
   - Reconciled 18-feature contract preserved ($7 \text{ sampled lags} + 4 \text{ statistics} + 6 \text{ astronomical} + 1 \text{ physical clear-sky} = 18$).
2. **Architecture Status (`AUTHORIZED_MULTIPLE_CANDIDATES`)**:
   - `ARCHITECTURE_STATUS = AUTHORIZED_MULTIPLE_CANDIDATES` (`HistGradientBoostingRegressor` vs. `Ridge`).
   - `ARCHITECTURE_SELECTION = REQUIRES_GOVERNANCE_DECISION`.
3. **Preprocessing Contract (`AUTHORIZED_TRAIN_ONLY`)**:
   - `StandardScaler` parameter fitting restricted strictly to Training split.
4. **Firewall & Immutability**:
   - `Stage 8.1`, `EMS`, and `Candidate A` remain 100% frozen and untouched.
   - `NEW_MODEL_TRAINED = NO`, `NEW_MODEL_INFERRED = NO`.

---

## 3. Required Final Status Block

```
OBSERVATIONS_VS_ORIGINS_CORRECTION =
PASS

REPRODUCIBILITY_TERMINOLOGY_CORRECTION =
PASS

FEATURE_CONTRACT =
UNCHANGED

ARCHITECTURE_STATUS =
AUTHORIZED_MULTIPLE_CANDIDATES

ARCHITECTURE_SELECTION =
REQUIRES_GOVERNANCE_DECISION

NEW_MODEL_TRAINED =
NO

NEW_MODEL_INFERRED =
NO

MODEL_TRAINING_AUTHORIZATION =
NOT_GRANTED

NEXT_GOVERNED_STEP =
TRAINING_SPECIFICATION_GOVERNANCE_REVIEW
```
