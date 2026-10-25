# POLARIS SOLAR FORECAST BRANCH 01
## TEST-REGIME SENSITIVITY ADDENDUM

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Addendum Mode:** `READ-ONLY FORENSIC EVALUATION ONLY`  
**Aggregate TEST MAE Verification:** **`4.3687 W/m^2` (EXACT MATCH RECOVERED)**  
**TEST_REGIME_CHARACTERIZATION:** **`SUFFICIENT`**  
**POLAR_NIGHT_EFFECT_ON_TEST_ERROR:** **`QUANTIFIED`**  

---

### 1. Executive Summary
This read-only addendum quantifies the exact contribution of Arctic polar-night zero-irradiance conditions to the reported held-out TEST split performance (4.3687 W/m^2 MAE). Using strictly frozen prediction artifacts and ground-truth targets (Nov 1 – Dec 31, 2024, 1,464 origins x 24 horizons = 35,136 target points), this analysis breaks down errors by month and irradiance regime without any model refitting or artifact alteration.

---

### 2. Monthly TEST Split Breakdown

| Month | Origins | Target Points | Target Mean (W/m^2) | Target Max (W/m^2) | Zero-Target % | MAE (W/m^2) | RMSE (W/m^2) | Bias (W/m^2) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **November 2024** | 720 | 17280 | 2.5749 | 72.7967 | 63.50% | **5.4876** | 10.7753 | 5.1579 |
| **December 2024** | 744 | 17856 | 0.3282 | 8.3622 | 71.88% | **3.2859** | 5.2942 | 3.2344 |

**Key Insight**: December 2024 is in continuous polar night (SW_IN mean = 0.33 W/m^2, 71.86% zero targets), yielding an MAE of **`3.2859 W/m^2`**. November 2024 contains early-month daylight transitions (SW_IN mean = 2.57 W/m^2, max = 72.80 W/m^2), yielding an MAE of **`5.4876 W/m^2`**.

---

### 3. Irradiance Partitioning (SW_IN = 0 vs SW_IN > 0)

| Target Regime | Target Point Count | Test Fraction % | Target Mean (W/m^2) | MAE (W/m^2) | RMSE (W/m^2) | Bias (W/m^2) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Target SW_IN = 0 W/m^2** | 23807 | 67.76% | 0.0000 | **1.9729** | 3.0313 | 1.9293 |
| **Target SW_IN > 0 W/m^2** | 11329 | 32.24% | 4.4447 | **9.4033** | 14.2114 | 8.9109 |

**Key Insight**: Across all 35,136 test points, **67.76% of all hourly target points are exactly zero**. On zero-irradiance night points, Candidate A HGB achieves an MAE of **`1.9729 W/m^2`**. On daytime points (SW_IN > 0), Candidate A HGB achieves an MAE of **`9.4033 W/m^2`**.

---

### 4. Irradiance Threshold Partitioning (SW_IN <= 5 W/m^2 vs SW_IN > 5 W/m^2)

| Threshold Partition | Target Point Count | Test Fraction % | Target Mean (W/m^2) | MAE (W/m^2) | RMSE (W/m^2) | Bias (W/m^2) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Target SW_IN <= 5 W/m^2** | 32451 | 92.36% | 0.2956 | **3.3728** | 5.8617 | 3.3345 |
| **Target SW_IN > 5 W/m^2** | 2685 | 7.64% | 15.1807 | **16.4046** | 22.7674 | 14.4033 |

---

### 5. Verification Assertions
1. **Re-Evaluation Only**: 100% evaluation-only pass on frozen artifacts; zero model fitting or retraining occurred.
2. **Immutability**: Zero source code or frozen model/prediction artifact changes were made.
3. **Exact Recovery**: The aggregate TEST MAE of **`4.3687 W/m^2`** is exactly recovered from the 35,136 test target and prediction points (4.368735 W/m^2).
4. **Previous Result Unchanged**: The frozen test result and prior governance audit classification remain 100% preserved.

---

### 6. Required Final Classifications

```
TEST_REGIME_CHARACTERIZATION =
SUFFICIENT

POLAR_NIGHT_EFFECT_ON_TEST_ERROR =
QUANTIFIED
```
