# POLARIS — SOLAR FORECAST BRANCH 01
## FINAL STATIC INTEGRATION EVIDENCE REVIEW REPORT

**Governance Gate**: Final Static Integration Evidence Review  
**Date**: 2026-09-21  
**Author**: Antigravity Autonomous Governance & Static Review Committee  
**Status**: **PASS**  

---

### 1. EXECUTIVE & GOVERNANCE SUMMARY

The **Final Static Integration Evidence Review** for `POLARIS_SOLAR_FORECAST_BRANCH_01` has been executed under strict **READ-ONLY** audit procedures.

- **Authoritative Model Identity**:
  - Model ID: `POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1` (Version 1.0.0)
  - Model Artifact Path: `artifacts/model_runs/RUN_BRANCH01_CANDIDATE_A_HGB/model.joblib`
  - Model SHA-256 Checksum: `65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781`
- **Verification Result**: 100% agreement across physical joblib artifact, canonical `MODEL_FREEZE_MANIFEST.json`, training campaign reports, model review authorization, runtime `Branch01ForecastEngine` adapter, and static integration test suite.
- **Integration Test Suite Status**: 30 out of 30 static/interface tests passed (`INT_STATIC_01` through `INT_STATIC_30`).

---

### 2. SIXTEEN-PILLAR EVIDENCE ASSESSMENT

| Pillar | Requirement | Evidence Type | Status | Evidence Details |
|---|---|---|---|---|
| 1. `MODEL_IDENTITY` | Exact SHA-256 & identity match | `ARTIFACT_HASH_AND_MANIFEST` | **PASS** | `65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781` verified |
| 2. `FEATURE_CONTRACT` | Exact governed 18 features in order | `MANIFEST_VERIFICATION_AND_SOURCE_AUDIT` | **PASS** | 18 features matched |
| 3. `TARGET_CONTRACT` | Target `SW_IN` ($W/m^2$) for 24 horizons | `MANIFEST_VERIFICATION_AND_SOURCE_AUDIT` | **PASS** | $t+1 \dots t+24$ $W/m^2$ |
| 4. `CAUSALITY` | Lookback uses only historical data $\le t$ | `EXECUTED_TEST_AND_SOURCE_AUDIT` | **PASS** | `INT_STATIC_13` passed |
| 5. `NWP_CAUSALITY` | $t_\text{issue} \le t_\text{origin}$, lead 1..48h | `EXECUTED_TEST_AND_SOURCE_AUDIT` | **PASS** | `INT_STATIC_14`, `15` passed |
| 6. `HORIZON_ALIGNMENT` | Exactly 24 prediction points | `EXECUTED_TEST_AND_SOURCE_AUDIT` | **PASS** | `INT_STATIC_09` passed |
| 7. `TIMESTAMP_ALIGNMENT` | Monotonic 1h cadence in UTC | `EXECUTED_TEST_AND_SOURCE_AUDIT` | **PASS** | `INT_STATIC_10`, `11`, `12` passed |
| 8. `PREPROCESSING` | Matching training preprocessing | `SOURCE_AUDIT` | **PASS** | Raw 18-vector passed to HGB |
| 9. `FORECASTBUNDLE` | Valid Bundle Version 1.0.0 schema | `EXECUTED_TEST_AND_SCHEMA_AUDIT` | **PASS** | `INT_STATIC_17`, `28`, `29` passed |
| 10. `PV_MAPPING` | $P_\text{solar} = \min(\text{SW\_IN} \times 51.0, 60\text{kW})$ | `EXECUTED_TEST_AND_SOURCE_AUDIT` | **PASS** | `INT_STATIC_18` passed |
| 11. `FAIL_CLOSED` | Raise exception on invalid input/state | `EXECUTED_TEST_AND_SOURCE_AUDIT` | **PASS** | `INT_STATIC_05`..`08`, `16`, `27` passed |
| 12. `TRUTH_FIREWALL` | No hidden actuals or Digital Twin truth | `EXECUTED_TEST_AND_STATIC_ANALYSIS` | **PASS** | `INT_STATIC_21` passed |
| 13. `DETERMINISM` | Same input + model $\implies$ 0 diff | `EXECUTED_TEST` | **PASS** | `INT_STATIC_22` diff = 0.0 |
| 14. `SOURCE_PROVENANCE` | Adapter identified, protected code untouched | `ARTIFACT_HASH` | **PASS** | All source SHAs registered |
| 15. `PROTECTED_ARTIFACTS_UNCHANGED` | Stage8.1, EMS, Twin, Schemas untouched | `ARTIFACT_HASH` | **PASS** | Stage8.1 SHA `d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c` |
| 16. `TEST_EVIDENCE` | 30 static test suite executed | `EXECUTED_TEST_SUITE_30_OF_30` | **PASS** | 30/30 tests passed |

---

### 3. SCIENTIFIC QUALIFICATION & REGIME CHARACTERIZATION

- **Overall Test Set Metrics**:
  - Test MAE: `4.3687 W/m^2`
  - Test RMSE: `8.4466 W/m^2`
- **Regime Characterization Notice**:
  - **Zero Irradiance Target Percentage**: `67.76%` (1,464 origins $\times$ 24 horizons during Nov–Dec 2024 Arctic polar night).
  - **Low Irradiance ($\le 5\text{ W/m}^2$) Target Percentage**: `92.36%`.
  - **Daytime Irradiance ($\text{SW\_IN} > 5\text{ W/m}^2$) Subset MAE**: `16.4046 W/m^2`.
- **Governance Finding**: The model remains approved under Branch01 governance decision, but its aggregate `4.37 W/m^2` test MAE must NOT be cited as a universally representative daytime error.

---

### 4. MANDATORY FINAL STATUS BLOCK

```
STATIC_INTEGRATION_EVIDENCE_REVIEW =
PASS

MODEL_IDENTITY =
PASS

AUTHORITATIVE_MODEL_SHA256 =
65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781

FEATURE_CONTRACT =
PASS

TARGET_CONTRACT =
PASS

CAUSALITY =
PASS

NWP_CAUSALITY =
PASS

HORIZON_ALIGNMENT =
PASS

TIMESTAMP_ALIGNMENT =
PASS

PREPROCESSING =
PASS

FORECASTBUNDLE =
PASS

PV_MAPPING =
PASS

FAIL_CLOSED =
PASS

TRUTH_FIREWALL =
PASS

DETERMINISM =
PASS

SOURCE_PROVENANCE =
PASS

PROTECTED_ARTIFACTS_UNCHANGED =
PASS

TEST_EVIDENCE =
PASS

MODEL_RETRAINED =
NO

MODEL_TUNED =
NO

STAGE8_1_MODIFIED =
NO

EMS_MODIFIED =
NO

EMS_EXECUTED =
NO

MPC_EXECUTED =
NO

MILP_EXECUTED_AS_EMS_EXPERIMENT =
NO

DIGITAL_TWIN_EXECUTED =
NO

EMS_EXECUTION_AUTHORIZATION =
NOT_GRANTED

MPC_EXECUTION_AUTHORIZATION =
NOT_GRANTED

PRODUCTION_DEPLOYMENT =
NOT_AUTHORIZED

NEXT_GOVERNED_STEP =
CONTROLLED_EMS_INTEGRATION_VALIDATION_REVIEW
```
