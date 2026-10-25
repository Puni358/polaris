# POLARIS STAGE 8.16B-2 — CANDIDATE FREEZE / PROMOTION CHECKPOINT

**Stage**: POLARIS Stage 8.16B-2 Candidate Freeze  
**Candidate Name**: Stage 8.1 + $\Phi_{inconsist}$  
**Status**: **PASSED EVEN-CV → CANDIDATE FOR ODD VALIDATION**  
**ODD Benchmark (173 Origins)**: **UNTOUCHED (0 Reads, 0 Evaluations prior to this checkpoint)**  
**Operational Champion**: Frozen Stage 8.1 700 hPa Steering Wind Model (Daytime nMAE = `28.0688%`)  

---

## 1. Candidate Specification & Formula

$$\Phi_{inconsist} = \lvert N_{total} - (1.0 - e^{-0.02 \cdot LWP_{latest}})\rvert$$

- **Feature Name**: `phi_inconsist`
- **Extinction Coefficient ($\alpha$)**: `0.02` (FROZEN)
- **Model Architecture**: `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)` (FROZEN)
- **Feature Inventory**: 38 total features (Stage 8.1 Control 37 features + `phi_inconsist`) (FROZEN)
- **Stage 4 Fitting**: Stage 4 parameters fit on training split only (FROZEN)

---

## 2. Authoritative EVEN-CV Development Results (174 EVEN Origins)

| Metric / Evaluation Gate | Control Baseline (37 Feat) | Candidate ($\Phi_{inconsist}$) (38 Feat) | Delta ($\Delta$) | Gate Status |
| :--- | :---: | :---: | :---: | :---: |
| **Daytime MAE** | `45.091280 W/m²` | `44.718895 W/m²` | **`-0.372385 W/m²`** | **G1 PASS** |
| **Daytime nMAE** | `32.5790%` | `32.3099%` | **`-0.2691 pp`** | **G2 PASS** |
| **Daytime RMSE** | `76.985584 W/m²` | `76.443487 W/m²` | **`-0.542097 W/m²`** | **G5 PASS** |
| **Improved Folds Count** | — | — | **`3 / 5` (F1, F2, F5)** | **G3 PASS** |
| **Worst-Fold Degradation** | — | — | **`+0.176410 W/m²` (Fold 4)** | **G4 PASS** |

---

## 3. Mandatory Candidate Freeze Rules Enforced

1. **Zero Model Modifications**: No changes to features, hyperparameters, or architecture.
2. **Zero $\alpha$ Tuning**: Extinction parameter fixed at $\alpha = 0.02$.
3. **Zero ODD Retraining**: The candidate model will be fit on the 174 EVEN origins and evaluated once on ODD.
4. **Firewall Verification**: 0 ODD target reads occurred prior to writing this checkpoint.

---

## 4. Checkpoint Artifacts Created

- [STAGE8_16B_2_PHI_INCONSIST_CANDIDATE_FREEZE.md](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_16B_2_PHI_INCONSIST_CANDIDATE_FREEZE.md)
- [STAGE8_16B_2_PHI_INCONSIST_CANDIDATE_FREEZE.json](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_16B_2_PHI_INCONSIST_CANDIDATE_FREEZE.json)
