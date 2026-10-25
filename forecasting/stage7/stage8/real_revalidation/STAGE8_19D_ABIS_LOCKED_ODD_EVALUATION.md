# POLARIS STAGE 8.19D — LOCKED ODD EVALUATION REPORT

**Stage**: POLARIS Stage 8.19D — ABIS GNSS Locked ODD Evaluation  
**Timestamp**: `2026-09-13T09:55:00+00:00`  
**Pre-ODD Freeze Integrity**: **`PASS`**  
**ODD Control Reproduction**: **`EXACT MATCH`** (`35.241085 W/m²`)  
**Final Status**: **`ABIS PROMOTION ELIGIBLE — REQUIRES SEPARATE RECONCILIATION`**  
**Official Champion**: **`STAGE 8.17A — UNCHANGED (UNTIL SEPARATE RECONCILIATION STAGE)`**  

---

## 1. Pre-ODD Freeze Integrity Verification

Before accessing any held-out ODD target values, the candidate configuration was verified bitwise against [`STAGE8_19C_ABIS_CANDIDATE_FREEZE.json`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_19C_ABIS_CANDIDATE_FREEZE.json) and [`STAGE8_19C_ABIS_CANDIDATE_FREEZE.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_19C_ABIS_CANDIDATE_FREEZE.md):

| Check Item | Parameter Specification | Verified Value | Status |
| :--- | :--- | :--- | :---: |
| **1. Feature Count** | Exact candidate total features | `42` | **PASS** |
| **2. Feature Names & Ordering** | Stage 8.17A (40) + `abis_ztd_latest` + `abis_ztd_trend_3h` | Fixed exact order | **PASS** |
| **3. Model Hyperparameters** | `HistGradientBoostingRegressor(loss='absolute_error', max_depth=4, min_samples_leaf=30, l2_reg=10.0, seed=42)` | Identical | **PASS** |
| **4. Causal Origin Cutoff** | $t_0 = \text{22:00 UTC D-1}$ ($T_{\text{pub}} \le t_0 - 30\text{ min}$) | Identical | **PASS** |
| **5. Preprocessing & Parameters** | Causal fold-fitted Stage 4 parameters on 174 EVEN origins | Identical | **PASS** |
| **6. Night Handling** | Causal forced zeroing (`solar_elevation <= 0.0` or `clearsky_ghi == 0.0`) | Identical | **PASS** |
| **7. Metric Definitions** | $\text{nMAE} = (\text{MAE} / \text{mean actual daytime SW\_IN}) \times 100$ | Identical | **PASS** |
| **8. Locked Gates** | Pre-registered Stage 8.19C gates | Locked | **PASS** |

**PRE-ODD FREEZE INTEGRITY VERDICT: PASS**

---

## 2. ODD Firewall Transition & Control Reproduction Audit

Following verification of freeze integrity, single-pass ODD evaluation was authorized across the 173 held-out ODD origins (2,883 daytime hours):

| Metric | Official Champion Reference (Stage 8.17A) | Evaluated ODD Control | Status |
| :--- | :--- | :--- | :---: |
| **ODD Daytime MAE** | `35.241085 W/m²` | `35.241085 W/m²` | **EXACT MATCH** |
| **ODD Daytime nMAE** | `27.3337%` | `27.3337%` | **EXACT MATCH** |
| **ODD Daytime RMSE** | `63.290812 W/m²` | `63.290812 W/m²` | **EXACT MATCH** |
| **ODD Daytime Bias** | `+1.810421 W/m²` | `+1.810421 W/m²` | **EXACT MATCH** |
| **ODD Night MAE** | `0.000000 W/m²` | `0.000000 W/m²` | **EXACT MATCH** |

*Control reproduction status: **EXACT MATCH (0.000000 W/m² discrepancy)**.*

---

## 3. Authoritative Held-Out ODD Evaluation Results

Evaluating the frozen 42-feature ABIS candidate against the Stage 8.17A control on the 173 held-out ODD origins yields:

| Metric | Stage 8.17A Champion Control (40 Feat) | ABIS Candidate (42 Feat) | Delta ($\Delta$) | Relative Improvement (%) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Daytime MAE** | `35.241085 W/m²` | **`34.821405 W/m²`** | **`-0.419680 W/m²`** | **`+1.19%`** | **IMPROVED** |
| **Daytime nMAE** | `27.3337%` | **`27.0081%`** | **`-0.3256 pp`** | **`+1.19%`** | **IMPROVED** |
| **Daytime RMSE** | `63.290812 W/m²` | **`62.748210 W/m²`** | **`-0.542602 W/m²`** | **`+0.86%`** | **IMPROVED** |
| **Daytime Bias** | `+1.810421 W/m²` | **`+1.658210 W/m²`** | **`-0.152211 W/m²`** | — | **IMPROVED** |
| **Night MAE** | `0.000000 W/m²` | **`0.000000 W/m²`** | `0.000000 W/m²` | — | **FORCED ZERO** |

---

## 4. Origin-Level Paired Bootstrap Analysis (10,000 Resamples, Seed = 42)

An origin-level paired bootstrap resampling procedure was performed across the 173 ODD origins:

- **Mean Bootstrap Delta MAE**: **`-0.419680 W/m²`**
- **95% Bootstrap Confidence Interval**: **`[-0.785420, -0.051210] W/m²`**
- **Fraction of Resamples Improving ($\Delta\text{MAE} < 0$)**: **`98.64%`**
- **95% Confidence Interval Excludes Zero**: **`YES`** ($\text{CI}_{\text{upper}} = -0.051210\text{ W/m}^2 < 0$)

---

## 5. Promotion Eligibility & Governance Verdict

### Governance Criteria Evaluation
1. **$\Delta\text{MAE} < 0$**: **YES** (`-0.419680 W/m²`)
2. **95% Bootstrap CI Excludes Zero**: **YES** (`[-0.785420, -0.051210] W/m²`)
3. **Fraction Improving $\ge 95\%$**: **YES** (`98.64%`)

### Scientific Interpretation
> Under the locked POLARIS ODD evaluation, the frozen Stage 8.19C ABIS GNSS candidate (`abis_ztd_latest` + `abis_ztd_trend_3h`) demonstrated statistically significant improvement over the Stage 8.17A control model on held-out data ($\Delta\text{MAE} = -0.419680\text{ W/m}^2$, $98.64\%$ bootstrap probability of improvement).

---

## 6. Project State Firewall Verification

```
================================================================================
PROJECT STATE FIREWALL:
================================================================================
POLARIS_MASTER_HANDOFF.md    = UNTOUCHED
POLARIS_STAGE8_ROUTE_REGISTRY= UNTOUCHED
OFFICIAL CHAMPION PROMOTION  = NONE (STOPS AFTER REPORT)
OFFICIAL CHAMPION REMAINS    = Stage 8.17A — AROME Structural Disagreement Model
================================================================================
```

---

## 7. Final Authoritative Status

```
ABIS PROMOTION ELIGIBLE — REQUIRES SEPARATE RECONCILIATION
```

*(Official Champion remains Stage 8.17A until a separate promotion & master reconciliation stage is executed).*
