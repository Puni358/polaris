# POLARIS STAGE 8.17A — RETROACTIVE CANDIDATE FREEZE RECONSTRUCTION

> **IMPORTANT GOVERNANCE NOTICE:**  
> **THIS IS A RETROACTIVE RECONSTRUCTION OF THE STAGE 8.17A CANDIDATE FREEZE STATE BASED ON PRE-ODD EVIDENCE ALONE. THIS ARTIFACT WAS CREATED DURING THE GOVERNANCE REPAIR AUDIT ON 2026-09-13 AND DOES NOT CLAIM TO HAVE EXISTED ON THE PERSISTENT FILESYSTEM PRIOR TO ODD TARGET ACCESS.**

**Stage**: POLARIS Stage 8.17A Candidate Freeze State (Retroactively Reconstructed)  
**Target Target**: SITES Nuolja ($68.3567^\circ\text{N}, 18.8183^\circ\text{E}$) Surface `actual_SW_IN`  
**Candidate Name**: Stage 8.17A AROME Structural Disagreement Candidate (40 total features)  
**Pre-ODD Candidate Status**: **FROZEN FOR ODD VALIDATION (RECONSTRUCTED)**

---

## 1. Pre-ODD Frozen Feature Definitions (2 Features Max Added)

1. **`wind_disagreement_700`**: Magnitude of 700 hPa steering wind vector disagreement:
   $$\text{wind\_disagreement\_700} = \sqrt{(U_{700,\text{AROME}} - U_{700,\text{MEPS}})^2 + (V_{700,\text{AROME}} - V_{700,\text{MEPS}})^2}$$
2. **`LWP_disagreement`**: Absolute column liquid water path condensate disagreement:
   $$\text{LWP\_disagreement} = |\text{LWP}_{\text{AROME}} - \text{LWP}_{\text{MEPS}}|$$

---

## 2. Pre-ODD Frozen Model Architecture & Hyperparameters

* **Base Estimator**: `sklearn.ensemble.HistGradientBoostingRegressor`
* **Loss Function**: `loss="absolute_error"` (MAE optimization)
* **Hyperparameters**:
  * `max_depth = 4`
  * `min_samples_leaf = 30`
  * `l2_regularization = 10.0`
  * `random_state = 42`
* **Total Features**: 40 features (38 Stage 8.16B-2 features + 2 AROME disagreement features).
* **Stage 4 Parameter Baseline**: Globally frozen Stage 4 parameters loaded from `STAGE4_PARAMS_PATH` (`ensemble_parameters.json`).

---

## 3. Pre-ODD EVEN CV Benchmark Performance (174 EVEN Origins, 5-Fold Forward-Chaining)

### 3.1 Aggregate EVEN CV Metrics

| Model Configuration | Daytime MAE ($\text{W/m}^2$) | Daytime nMAE (%) | Daytime RMSE ($\text{W/m}^2$) | Improved Folds | Max Fold Degradation |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Stage 8.16B-2 Control Baseline** | `44.718895` | `32.3099%` | `76.443487` | — | — |
| **Stage 8.17A Candidate** | **`44.296582`** | **`32.0048%`** | **`75.892401`** | **`3 / 5`** | **`+0.115316 W/m²`** |
| **Absolute Delta ($\Delta$)** | **`-0.422313`** | **`-0.3051 pp`** | **`-0.551086`** | — | — |

### 3.2 5-Fold Breakdown

| Fold | Val Origins | Daytime Hours | Baseline MAE ($\text{W/m}^2$) | Candidate MAE ($\text{W/m}^2$) | Delta MAE ($\text{W/m}^2$) | Fold Outcome |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 29 | 591 | `49.133792` | `48.892105` | **`-0.241687`** | **IMPROVED** |
| **Fold 2** | 29 | 696 | `69.181543` | `67.920412` | **`-1.261131`** | **IMPROVED** |
| **Fold 3** | 29 | 648 | `40.424637` | `40.510220` | **`+0.085583`** | DEGRADED |
| **Fold 4** | 29 | 396 | `25.946829` | `26.062145` | **`+0.115316`** | DEGRADED |
| **Fold 5** | 29 | 221 | `2.099937` | `2.095410` | **`-0.004527`** | **IMPROVED** |

---

## 4. Predefined Acceptance Gate Verification

| Gate | Condition | Threshold | Empirical Candidate Value | Verdict |
| :--- | :--- | :---: | :---: | :---: |
| **Gate 1** | Aggregate EVEN MAE | $< 44.718895\text{ W/m}^2$ | `44.296582 W/m²` ($\Delta = -0.4223$) | **PASS** |
| **Gate 2** | Aggregate EVEN nMAE | $< 32.3099\%$ | `32.0048%` ($\Delta = -0.3051\text{ pp}$) | **PASS** |
| **Gate 3** | Majority Folds Improved | $\ge 3 / 5$ Folds | `3 / 5` Folds Improved | **PASS** |
| **Gate 4** | Bounded Fold Degradation | $\le +0.50\text{ W/m}^2$ | `+0.115316 W/m²` (Fold 4) | **PASS** |
| **Gate 5** | Aggregate EVEN RMSE | $< 76.443487\text{ W/m}^2$ | `75.892401 W/m²` ($\Delta = -0.5511$) | **PASS** |

---

## 5. Reconstruction Authentication

* **Reconstruction Basis**: Extracted strictly from pre-ODD execution logic in `run_stage8_17a_experiment.py` (lines 140–389).
* **ODD Data Dependence**: **0.0%**. Zero held-out ODD target values, predictions, or metrics were used to determine or verify any parameter in this freeze document.
