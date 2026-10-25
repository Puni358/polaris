# POLARIS STAGE 8.24 GOVERNED EXPERIMENT — EVEN VALIDATION REPORT

> [!IMPORTANT]
> **GOVERNANCE VERDICT: REJECTED_ON_EVEN**  
> - **EVEN Control MAE:** `37.6308 W/m²`  
> - **EVEN Candidate MAE:** `37.7572 W/m²` ($\Delta = +0.1264	ext{ W/m}²$)  
> - **Improving Folds:** `2 / 5`  
> - **Worst-Fold Degradation:** `+0.4042 W/m²`  
> - **ODD Benchmark Status:** **UNTOUCHED (`ODD_RUN = FALSE`)**  
> - **Operational Champion:** **UNCHANGED (Stage 8.1 37-feature HGB)**

---

## 1. Executive Summary

Stage 8.24 evaluated whether pre-registering the **Scandes Barrier-Normal Wind (`ctx_u_perp`)** and **Mountain Froude Flow-Regime Indicator (`ctx_mountain_froude`)** improved forecasting skill over the frozen Stage 8.1 37-feature operational champion across 173 EVEN benchmark origins.

---

## 2. Gate-by-Gate Governance Audit

| Gate ID | Criterion | Required Threshold | Empirical Result | Gate Status |
| :--- | :--- | :--- | :---: | :---: |
| **G1** | MAE Margin | $\Delta 	ext{MAE} \le -0.50	ext{ W/m}²$ | `+0.1264	ext{ W/m}²` | **FAIL** |
| **G2** | Fold Consistency | $\ge 4 / 5	ext{ folds improve}$ | `2 / 5	ext{ folds}` | **FAIL** |
| **G3** | Worst Fold Tolerance | Worst fold $\le +0.50	ext{ W/m}²$ | `+0.4042	ext{ W/m}²` | **PASS** |
| **G4** | nMAE & RMSE Non-Degradation | $	ext{nMAE} \le 	ext{ctrl} \land 	ext{RMSE} \le 	ext{ctrl}$ | nMAE: `29.31\%`, RMSE: `60.44` | **FAIL** |
| **G5** | Causal Integrity | 100% causal features | 100% causal ($t_0 = 00:00	ext{ UTC}$) | **PASS** |
| **G6** | Control Reproduction | Exact control match | `37.6308 == 37.6201` | **PASS** |

---

## 3. Fold-by-Fold Detailed Breakdown

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control RMSE | Candidate RMSE | Daytime N | Fold Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 49.5313 | 49.4720 | -0.0593 | 81.3625 | 81.6577 | 591 | Improved |
| **Fold 2** | 70.7021 | 70.5560 | -0.1461 | 103.7542 | 103.5770 | 696 | Improved |
| **Fold 3** | 40.3698 | 40.6213 | +0.2515 | 67.2570 | 67.9721 | 648 | Degraded |
| **Fold 4** | 25.6828 | 26.0871 | +0.4042 | 44.5807 | 45.4723 | 396 | Degraded |
| **Fold 5** | 1.8680 | 2.0497 | +0.1818 | 3.5326 | 3.5208 | 221 | Degraded |

---

## 4. Governed Action & Protocol Outcome

- Because EVEN gates failed, **candidate freeze protocol took effect immediately**:
  1. No hyperparameter tuning or post-hoc threshold adjustment was performed.
  2. Official ODD evaluation was **NOT** executed (`ODD_RUN = FALSE`).
  3. ODD target data remained strictly uninspected (`ODD_TARGET_ACCESS = FALSE`).
  4. Final Verdict: **`REJECTED_ON_EVEN`**.
  5. Stage 8.1 37-feature HGB model remains the operational champion.

---

## Final Governance Statement

- **Stage 8.24 REJECTED ON EVEN.**
- **ODD dataset remains 100% untouched.**
- **Stage 8.1 37-feature model remains operational champion.**
- **No model changes, master handoff changes, or route registry changes.**
