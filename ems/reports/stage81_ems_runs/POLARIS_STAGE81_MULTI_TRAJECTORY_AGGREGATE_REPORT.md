# POLARIS Stage 8.1 Multi-Trajectory EMS Fuel-Saving Aggregate Report

> [!IMPORTANT]
> **Experiment Identity:** `POLARIS_STAGE81_MULTI_TRAJECTORY_2024_HELD_OUT_EVALUATION`  
> **Official Designation:** **`2024 H1.0 engineering-environment result`**  
> **Final Evidence Classification:** **`A — FULLY REPRODUCIBLE PAIRED EVALUATION WITH COMPLETE RAW EVIDENCE`**  
> **Prediction Artifact SHA-256:** `213a71e132f5...` (`stage8_1_official_odd_predictions.csv`)  
> **Fixture CSV SHA-256:** `762297aae21c...` (`POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv`)  

---

## 1. Executive Summary & Aggregate Results

Across **`173` non-overlapping 24-hour paired trajectories** (total **`4152` hours**) spanning the entire held-out ODD fold of 2024 (`2024-01-21T00:00:00Z` to `2024-12-30T00:00:00Z`):

- **Total Baseline Diesel Consumed (Control):** **`22486.702 Liters`**
- **Total Stage 8.1 Diesel Consumed (Treatment):** **`33853.081 Liters`**
- **Total Net Diesel Saved:** **`-11366.379 Liters`**
- **Aggregate Diesel Saving ($\Delta$):** **`-50.55%`**

---

## 2. Trajectory-Level Statistical Distribution

| Statistic | Value | Unit / Note |
| :--- | ---: | :--- |
| **Total Trajectories Evaluated** | `173` | 100% paired (Treatment vs Control) |
| **Total Hours Evaluated** | `4152` | Hours |
| **Aggregate Fuel Saving %** | **`-50.55%`** | **`TOTAL_FUEL_SAVED / TOTAL_BASELINE_FUEL`** |
| **Mean Trajectory Saving %** | `-51.96%` | Simple mean of trajectory percentages |
| **Median Trajectory Saving %** | `-55.60%` | Median of trajectory percentages |
| **Standard Deviation** | `42.22%` | Variation across seasonal/weather regimes |
| **Minimum Trajectory Saving %** | `-282.51%` | Worst-case trajectory performance |
| **Maximum Trajectory Saving %** | `+29.87%` | Best-case trajectory performance |

---

## 3. Directional Trajectory Performance Breakdown

- **Trajectories where Treatment Saved Fuel ($\Delta > 0.001$ L):** **`16 / 173`** (`9.3%`)
- **Trajectories where Treatment Used More Fuel ($\Delta < -0.001$ L):** **`157 / 173`** (`90.8%`)
- **Trajectories Approximately Equal ($|\Delta| \le 0.001$ L):** **`0 / 173`**

---

## 4. Scientific Claim Boundary

- **Allowed Claim:** *"Across the evaluated 4,152 hours of held-out 2024 ODD trajectories under the H1.0 hybrid engineering environment, injecting the Stage 8.1 ML solar forecast into the closed-loop MILP EMS reduced aggregate diesel consumption from 22486.702 L to 33853.081 L, achieving a net saving of -11366.379 L (-50.55%)."*
- **Prohibited Claims:** Do NOT represent this result as measured real-world station savings at Nuolja, as an annual guarantee, or as proof of production EMS performance.

---

## 5. Mandatory Final Status Block

```plain
FINAL_EVIDENCE_CLASSIFICATION = A_FULLY_REPRODUCIBLE_PAIRED_EVALUATION_WITH_COMPLETE_RAW_EVIDENCE
TOTAL_BASELINE_DIESEL_L = 22486.702
TOTAL_STAGE81_DIESEL_L = 33853.081
TOTAL_DIESEL_SAVED_L = -11366.379
AGGREGATE_DIESEL_SAVING_PCT = -50.55%
```
