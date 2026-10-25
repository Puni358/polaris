# POLARIS SOLAR FORECAST BRANCH 01
## MODEL EVIDENCE, REPRODUCIBILITY & VALIDATION/TEST ANOMALY AUDIT REPORT

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Audit Scope:** `READ-ONLY SCIENTIFIC AND GOVERNANCE EVIDENCE AUDIT`  
**Audit Status:** `COMPLETE`  
**Reproducibility Classification:** **`A — REPRODUCIBLE_AND_AUDIT_VERIFIED`**  
**Scientific Validity:** **`PASS`**  
**Model Review Status:** **`MODEL_REVIEW_READY = YES`**  
**EMS Integration Authorization State:** **`EMS_INTEGRATION_AUTHORIZATION = NOT_GRANTED`**  

---

### 1. Audit Scope & Authorization Boundaries
This audit was performed in strict READ-ONLY mode. Zero model fitting, retraining, hyperparameter tuning, feature modification, or EMS execution was performed. All serialized models, predictions, manifests, code files, datasets, and split boundaries were independently inspected, hashed, re-evaluated, and verified.

---

### 2. Governance State
- **TRAINING_SPECIFICATION_GOVERNANCE_REVIEW**: `PASS`
- **ARCHITECTURE_DECISION_REVIEW**: `PASS`
- **TRAINING_AUTHORIZATION**: `CONSUMED_FOR_FIRST_CONTROLLED_CAMPAIGN`
- **AUDIT_AUTHORIZATION**: `READ_ONLY_EVIDENCE_VERIFICATION_ONLY`

---

### 3. Artifact Inventory & Verification Summary
All 11 campaign artifacts were verified against disk:
- Raw SITES Dataset SHA-256: `6842e0f71b1b1d4a3ea40d56cb620fd88ca7daa1701177dbf8954680795f45f3` (`PASS`)
- Clear-Sky Dataset SHA-256: `3cb49a4f475a34ec8a1ffac15b81a742ea3bfa0ef6cfa3296c00fdfbf6fbf918` (`PASS`)
- Stage 8.1 Firewall SHA-256: `d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c` (`PASS - Untouched`)
- Candidate A HGB Model SHA-256: `65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781` (`PASS`)
- Candidate A HGB Val Preds SHA-256: `41b8aa410d86b97623fd8c983d582d0013d2f254bc282dfebfcbc16578a0b0d3` (`PASS`)
- Candidate A HGB Test Preds SHA-256: `8ff3bb8ceff70c0d2ab04d7517b627bee7dfcb8354b48bea808748d9256d625c` (`PASS`)

---

### 4. Split Reconciliation Audit
The dataset contains $N_{	ext{SUPPORTED\_ORIGINS}} = 8,784$ valid hourly forecast origins (Jan 1 00:00 UTC through Dec 31 23:00 UTC).
- **TRAIN** (Jan 1 – Aug 31): 5,832 origins
- **EMBARGO 1** (Aug 31 00:00 – Aug 31 23:00): 24 origins excluded to protect validation boundary
- **VALIDATION** (Sep 1 – Oct 31): 1,440 origins
- **EMBARGO 2** (Oct 31 00:00 – Oct 31 23:00): 24 origins excluded to protect test boundary
- **TEST** (Nov 1 – Dec 31): 1,464 origins
- **Total Reconciled**: $5,832 + 24 + 1,440 + 24 + 1,464 = 8,784$ origins ($100\%$ reconciled).

---

### 5. Validation vs. Test Discrepancy Forensic Audit
The audit investigated the large difference between Validation MAE ($26.3503	ext{ W/m}^2$) and Test MAE ($4.3687	ext{ W/m}^2$).

#### Forensic Target & Feature Distribution Analysis
| Split | Period | SW_IN Target Mean | SW_IN Target Max | Zero/Night % | Solar Elevation Mean |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TRAIN** | Jan 1 – Aug 31 | $115.06	ext{ W/m}^2$ | $745.87	ext{ W/m}^2$ | $22.00\%$ | $+15.2^\circ$ |
| **VALIDATION** | Sep 1 – Oct 31 | $47.30	ext{ W/m}^2$ | $543.60	ext{ W/m}^2$ | $39.95\%$ | $+5.4^\circ$ |
| **TEST** | Nov 1 – Dec 31 | **`1.43 W/m^2`** | **`72.80 W/m^2`** | **`67.76%`** | **`-15.8 deg` (Polar Night)** |

#### Discrepancy Audit Conclusion:
The held-out test distribution is strongly dominated by low-irradiance conditions: 67.76% of target points are exactly zero and 92.36% are <=5 W/m^2. Performance is materially better in this low-irradiance regime than at SW_IN >5 W/m^2. Therefore, the aggregate 4.3687 W/m^2 test MAE is not representative of the model's performance on substantial daytime irradiance.

---

### 6. Horizon-Wise TEST Error Profile Verification
| Target Horizon | TEST MAE (W/m^2) | TEST RMSE (W/m^2) | Audit Verification |
| :--- | :--- | :--- | :--- |
| **H1 (t+1h)** | `1.8722` | `3.2232` | `VERIFIED_MATCH` |
| **H6 (t+6h)** | `5.5572` | `9.7828` | `VERIFIED_MATCH` |
| **H12 (t+12h)** | `2.7510` | `5.3335` | `VERIFIED_MATCH` |
| **H18 (t+18h)** | `2.6157` | `5.3013` | `VERIFIED_MATCH` |
| **H24 (t+24h)** | `2.6173` | `4.4544` | `VERIFIED_MATCH` |

---

### 7. Fresh-Process Replay Audit
Fresh-process replay was verified by loading the serialized models (`model.joblib`, `scaler.joblib`) from disk in a separate process:
- Candidate A (HGB) Validation Replay: Max absolute difference $= 5.68 	imes 10^{-14}$ W/m² ($	ext{PASS} \le 1e-5$)
- Candidate B (Ridge) Validation Replay: Max absolute difference $= 5.68 	imes 10^{-14}$ W/m² ($	ext{PASS} \le 1e-5$)
- Candidate A (HGB) Test Replay: Max absolute difference $= 1.42 	imes 10^{-14}$ W/m² ($	ext{PASS} \le 1e-5$)

---

### 8. Required Final Status Block

```
MODEL_EVIDENCE_AUDIT =
COMPLETE

DATASET_INTEGRITY =
PASS

FEATURE_CONTRACT =
PASS

TARGET_CONTRACT =
PASS

CAUSALITY =
PASS

NWP_CAUSALITY =
PASS

SPLIT_INTEGRITY =
PASS

TRAINING_ISOLATION =
PASS

VALIDATION_METRICS =
PASS

ARCHITECTURE_SELECTION =
PASS

TEST_FIREWALL =
PASS

TEST_RESULT =
VERIFIED

REPLAY_VERIFICATION =
PASS

MODEL_RUN_MANIFEST =
PASS

34_ITEM_CHECKLIST =
PASS

SOURCE_PROVENANCE =
PASS

CLEARSKY_CAUSALITY =
PASS

STAGE8_1_MODIFIED =
NO

EMS_MODIFIED =
NO

EMS_EXECUTED =
NO

RETRAINING_PERFORMED_DURING_AUDIT =
NO

HYPERPARAMETER_SEARCH_PERFORMED_DURING_AUDIT =
NO

REPRODUCIBILITY_CLASSIFICATION =
A

SCIENTIFIC_VALIDITY =
PASS

MODEL_REVIEW_READY =
YES

EMS_INTEGRATION_AUTHORIZATION =
NOT_GRANTED

NEXT_GOVERNED_STEP =
MODEL_REVIEW_AND_EMS_INTEGRATION_AUTHORIZATION_REVIEW
```
