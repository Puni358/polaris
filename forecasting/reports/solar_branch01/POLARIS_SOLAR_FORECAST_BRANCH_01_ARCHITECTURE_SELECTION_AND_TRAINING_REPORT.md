# POLARIS_SOLAR_FORECAST_BRANCH_01 — CONTROLLED ARCHITECTURE SELECTION & TRAINING REPORT

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `FIRST GOVERNED BRANCH 01 TRAINING CAMPAIGN`  
**Campaign Authorization:** `CONSUMED FOR THIS CONTROLLED CAMPAIGN`  
**Training Execution Status:** `COMPLETE`  
**Selected Winning Architecture:** **`HISTGRADIENTBOOSTING`**  
**Selected Model Reproducibility:** **`REPRODUCIBLE`**  
**EMS Integration Authorization State:** **`EMS_INTEGRATION_AUTHORIZATION = NOT_GRANTED`**  

---

## 1. Preflight Hard Gate Summary

- **Raw Observations ($N_{OBSERVATIONS}$)**: `8,832` raw hourly rows in 2024 dataset.
- **Supported MPC Origins ($N_{SUPPORTED\_ORIGINS}$)**: `8,784` valid hourly forecast origins ($8,832 - 48$).
- **Dataset SHA-256**: `6842e0f71b1b1d4a3ea40d56cb620fd88ca7daa1701177dbf8954680795f45f3` (Verified)
- **Feature Matrix**: `18` exact governed features in exact order ($X \in \mathbb{R}^{8784 \times 18}$).
- **Target Matrix**: `24` steps ($SW\_IN(t+1)...SW\_IN(t+24)$) ($Y \in \mathbb{R}^{8784 \times 24}$).
- **Stage 8.1 Firewall SHA-256**: `d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c` (Verified 100% Untouched)

---

## 2. Validation Performance & Predeclared Selection Rule

Predeclared Rule: `VALIDATION_MAE` primary, `VALIDATION_RMSE` secondary.

| Candidate Architecture | Validation MAE (W/m^2) | Validation RMSE (W/m^2) | Replay Status | Selection Result |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate A (HistGradientBoosting)** | **26.3503** | **52.9917** | `PASS` ($\Delta \le 1e-5$) | **`SELECTED WINNER`** |
| **Candidate B (Ridge)** | 43.0529 | 58.8410 | `PASS` ($\Delta \le 1e-5$) | **`NOT SELECTED`** |

**Selection Rationale**: Candidate A (HistGradientBoosting) achieved lower Validation MAE (26.3503 vs 43.0529 W/m^2)

---

## 3. Final Held-Out TEST Evaluation (Selected Architecture: HISTGRADIENTBOOSTING)

The selected architecture (`HISTGRADIENTBOOSTING`) fitted strictly on TRAIN was evaluated ONCE on the held-out TEST split (`2024-11-01` through `2024-12-31`, 1,464 origins).

- **Final TEST MAE**: **`4.3687 W/m^2`**
- **Final TEST RMSE**: **`8.4466 W/m^2`**
- **Test Predictions SHA-256**: `8ff3bb8ceff70c0d2ab04d7517b627bee7dfcb8354b48bea808748d9256d625c`

---

## 4. Horizon-Wise TEST Error Profile (HISTGRADIENTBOOSTING)

| Target Horizon | TEST MAE (W/m^2) | TEST RMSE (W/m^2) |
| :--- | :--- | :--- |
| **H1 (t+1h)** | `1.8722` | `3.2232` |
| **H6 (t+6h)** | `5.5572` | `9.7828` |
| **H12 (t+12h)** | `2.7510` | `5.3335` |
| **H18 (t+18h)** | `2.6157` | `5.3013` |
| **H24 (t+24h)** | `2.6173` | `4.4544` |

---

## 5. Required Final Status Block

```
TRAINING_CAMPAIGN =
COMPLETE

CANDIDATE_HISTGRADIENTBOOSTING_TRAINED =
YES

CANDIDATE_RIDGE_TRAINED =
YES

CANDIDATE_HISTGRADIENTBOOSTING_SERIALIZED =
YES

CANDIDATE_RIDGE_SERIALIZED =
YES

CANDIDATE_HISTGRADIENTBOOSTING_REPLAY =
PASS

CANDIDATE_RIDGE_REPLAY =
PASS

VALIDATION_COMPARISON =
COMPLETE

ARCHITECTURE_SELECTION =
HISTGRADIENTBOOSTING

ARCHITECTURE_SELECTION_RULE =
VALIDATION_MAE_PRIMARY_RMSE_SECONDARY

TEST_EVALUATION =
COMPLETE

SELECTED_MODEL_REPRODUCIBILITY =
REPRODUCIBLE

NEW_MODEL_TRAINED =
YES

NEW_MODEL_INFERRED =
YES

EMS_MODIFIED =
NO

EMS_EXECUTED =
NO

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

MODEL_TRAINING_AUTHORIZATION =
CONSUMED_FOR_THIS_CONTROLLED_CAMPAIGN

EMS_INTEGRATION_AUTHORIZATION =
NOT_GRANTED

NEXT_GOVERNED_STEP =
MODEL_REVIEW_AND_EMS_INTEGRATION_AUTHORIZATION_REVIEW
```
