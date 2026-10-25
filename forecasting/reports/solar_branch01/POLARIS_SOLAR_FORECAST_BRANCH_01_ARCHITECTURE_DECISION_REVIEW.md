# POLARIS_SOLAR_FORECAST_BRANCH_01 — ARCHITECTURE DECISION REVIEW REPORT

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `ARCHITECTURE DECISION & TRAINING AUTHORIZATION REVIEW`  
**Authorization Mode:** `READ-ONLY ARCHITECTURE REVIEW ONLY`  
**Review Status:** **`PASS`**  
**Architecture Status:** **`AUTHORIZED_MULTIPLE_CANDIDATES`**  
**Architecture Selection State:** **`ARCHITECTURE_SELECTION = REQUIRES_GOVERNANCE_DECISION`**  
**Training Authorization State:** **`MODEL_TRAINING_AUTHORIZATION = NOT_GRANTED`**  

---

## 1. Executive Summary

This independent read-only review establishes the factual engineering and mathematical comparison between the two candidate architectures authorized by the Branch 01 specification:

- **Candidate A**: `sklearn.ensemble.HistGradientBoostingRegressor`
- **Candidate B**: `sklearn.linear_model.Ridge`

Both candidates are fully compatible with the frozen input contract ($X(t) \in \mathbb{R}^{18}$), output target contract ($Y(t) \in \mathbb{R}^{24}$), causality rules ($t_{\text{issue}} \le t$), split boundaries (Train/Val/Test with 24h embargo), train-only `StandardScaler` preprocessing, and reproducibility package (`MODEL_RUN_MANIFEST_SCHEMA` + 34-item checklist).

**No model winner or performance ranking is selected in this review.** Empirical performance comparison is `NOT_AVAILABLE_WITHOUT_TRAINING`.

---

## 2. Governance State & Authoritative Contracts Reviewed

- **N_OBSERVATIONS**: `8,832` raw hourly observations in 2024.
- **N_SUPPORTED_ORIGINS**: `8,784` valid hourly MPC forecast origins ($8,832 - 48$).
- **Feature Contract (18 Authorized Features)**:
  - 7 Sampled Lags: `sw_in_lag_0h`..`sw_in_lag_23h`
  - 4 Summary Statistics: `sw_in_mean_24h`, `sw_in_std_24h`, `sw_in_max_24h`, `sw_in_min_24h`
  - 6 Astronomical Features: `solar_elevation`, `solar_zenith`, `sin_hour`, `cos_hour`, `sin_doy`, `cos_doy`
  - 1 Physical Clear-Sky Reference: `clearsky_sw_in_origin`
- **Target Contract**: $Y(t) = [SW\_IN(t+1)...SW\_IN(t+24)]$, $t+0$ excluded.
- **Causality & NWP Rules**: $t_{\text{issue}} \le t$, $H_{\text{effective}} = h + (t - t_{\text{issue}})$, 1h..42h effective lead range verified with 100.0% coverage.
- **Splits & Embargo**: Train (Jan-Aug), Val (Sep-Oct), Test (Nov-Dec) with 24h embargo.
- **Preprocessing**: `StandardScaler` fitted strictly on Training split ($X_{\text{train}}$).

---

## 3. Candidate A — HistGradientBoostingRegressor

- **Model Class**: `sklearn.ensemble.HistGradientBoostingRegressor`
- **Multi-Output Strategy**: Wrapped in `sklearn.multioutput.MultiOutputRegressor` fitting 24 separate tree ensembles (one per horizon $h=1..24$).
- **Key Hyperparameters**: `learning_rate=0.05`, `max_iter=100`, `max_depth=6`, `min_samples_leaf=20`, `l2_regularization=1.0`, `random_state=42`.
- **Scaling Requirement**: Compatible (StandardScaler fitted strictly on Train split).
- **Strengths**: Captures non-linear solar regime interactions and threshold behaviors.
- **Limitations**: Higher computational complexity (24 separate tree ensembles); bounded by min/max training target range.

---

## 4. Candidate B — Ridge Regressor

- **Model Class**: `sklearn.linear_model.Ridge`
- **Multi-Output Strategy**: Native 2D target matrix regression fitting weight matrix $W \in \mathbb{R}^{18 \times 24}$ in closed form.
- **Key Hyperparameters**: `alpha=1.0`, `fit_intercept=True`, `solver='auto'`, `random_state=42`.
- **Scaling Requirement**: **MANDATORY** Z-score scaling via `StandardScaler` fitted strictly on Train split ($X_{\text{train}}$).
- **Strengths**: Extremely fast closed-form solution; native multi-output matrix operations; highly interpretable linear weights.
- **Limitations**: Strictly linear hypothesis space without explicit polynomial/non-linear feature expansions.

---

## 5. Factual Side-by-Side Comparison Matrix

| Evaluation Dimension | Candidate A: HistGradientBoostingRegressor | Candidate B: Ridge Regressor | Governance Status |
| :--- | :--- | :--- | :--- |
| **Input Dimension** | 18 features ($X(t) \in \mathbb{R}^{18}$) | 18 features ($X(t) \in \mathbb{R}^{18}$) | `MATCH / PASS` |
| **Output Dimension** | 24 targets ($Y(t) \in \mathbb{R}^{24}$) | 24 targets ($Y(t) \in \mathbb{R}^{24}$) | `MATCH / PASS` |
| **Multi-Output Implementation** | `MultiOutputRegressor` (24 sub-estimators) | Native 2D matrix regression ($W \in \mathbb{R}^{18 \times 24}$) | `BOTH COMPATIBLE` |
| **Scaling Requirement** | Compatible (`StandardScaler` Train-only) | Mandatory (`StandardScaler` Train-only) | `BOTH COMPATIBLE` |
| **Causality & NWP Rules** | Fully compliant ($t_{\text{issue}} \le t$) | Fully compliant ($t_{\text{issue}} \le t$) | `BOTH COMPATIBLE` |
| **Reproducibility Schema** | `MODEL_RUN_MANIFEST_SCHEMA` + 34-item checklist | `MODEL_RUN_MANIFEST_SCHEMA` + 34-item checklist | `BOTH COMPATIBLE` |
| **Replay Tolerance** | $\text{atol}=1e-5$, $\text{rtol}=1e-5$ | $\text{atol}=1e-5$, $\text{rtol}=1e-5$ | `BOTH COMPATIBLE` |
| **Empirical Performance** | `NOT_AVAILABLE_WITHOUT_TRAINING` | `NOT_AVAILABLE_WITHOUT_TRAINING` | `UNRANKED` |

---

## 6. Identification of Blockers & Gaps

- **Architecture-Specific Blockers**: None detected.
- **Governance Blockers**: None.
- **Implementation Gaps**: None. All interfaces exist in `forecasting/solar_branch_01/implementation/`.
- **Information Not Yet Available**: Empirical validation RMSE/MAE metrics on validation set (requires authorized training).

---

## 7. Required Training Configuration Readiness Checklist

Before training authorization is granted, the following exact fields must be frozen in a formal authorization decision:
1. **Selected Candidate**: Candidate A (`HistGradientBoosting`) OR Candidate B (`Ridge`).
2. **Hyperparameter Set**: Exact frozen hyperparameter values.
3. **Scaler & Preprocessing**: `StandardScaler` Train-only.
4. **Dataset Hashes**: File SHA-256 for `SITES_Nuolja_2024` and `AROME_21x21_Cache`.
5. **Split Boundaries**: Train Jan-Aug, Val Sep-Oct, Test Nov-Dec with 24h embargo.
6. **Resource Config**: 8 workers default, thermal/CPU/RAM logging, interruption policy.

---

## 8. Required Final Status Block

```
ARCHITECTURE_DECISION_REVIEW = PASS

CANDIDATE_HISTGRADIENTBOOSTING =
COMPATIBLE

CANDIDATE_RIDGE =
COMPATIBLE

INPUT_CONTRACT = PASS
OUTPUT_CONTRACT = PASS
CAUSALITY_CONTRACT = PASS
NWP_CONTRACT = PASS
SPLIT_CONTRACT = PASS
PREPROCESSING_CONTRACT = PASS
REPRODUCIBILITY_CONTRACT = PASS
EMS_INTERFACE_COMPATIBILITY = PASS

ARCHITECTURE_STATUS =
AUTHORIZED_MULTIPLE_CANDIDATES

ARCHITECTURE_SELECTION =
REQUIRES_GOVERNANCE_DECISION

NEW_MODEL_TRAINED = NO
NEW_MODEL_INFERRED = NO
REAL_BRANCH01_MODEL_LOADED = NO
EMS_EXECUTED = NO
STAGE8_1_MODIFIED = NO
CANDIDATE_A_IMPLEMENTED = NO
CANDIDATE_A_EXECUTED = NO

MODEL_TRAINING_AUTHORIZATION =
NOT_GRANTED

NEXT_GOVERNED_STEP =
EXPLICIT_ARCHITECTURE_SELECTION_AND_TRAINING_AUTHORIZATION
```
