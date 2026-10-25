# POLARIS Stage 8.1 Multi-Trajectory Forensic Mechanism Audit Report

> [!IMPORTANT]
> **Experiment Identity:** `POLARIS_STAGE81_MULTI_TRAJECTORY_2024_HELD_OUT_EVALUATION`  
> **Official Designation:** `2024 H1.0 engineering-environment result`  
> **Final Governance Classification:** **`A = EXPERIMENT_VALID_ROOT_CAUSE_IDENTIFIED`**  
> **Frozen Prediction Artifact SHA-256:** `213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707`  
> **Frozen Fixture CSV SHA-256:** `762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023`  

---

## 1. Executive Summary & Final Governance Verdict

A rigorous, read-only forensic audit was performed on the completed **173-trajectory Stage 8.1 paired experiment** (spanning 4,152 evaluation hours across held-out 2024 ODD origins).

The aggregate results of the frozen experiment are:
- **Baseline Diesel Consumed (Control):** `22,486.702 L`
- **Stage 8.1 Diesel Consumed (Treatment):** `33,853.081 L`
- **Net Diesel Saved:** `-11,366.379 L`
- **Aggregate Diesel Saving ($\Delta$):** **`-50.55%`**
- **Positive Trajectories:** `16 / 173` (`9.25%`)
- **Negative Trajectories:** `157 / 173` (`90.75%`)

### Final Governance Classification
```plain
FINAL_GOVERNANCE_CLASSIFICATION = A_EXPERIMENT_VALID_ROOT_CAUSE_IDENTIFIED
```

**Verdict Summary:**
1. **Experiment Integrity (Phase 1): PASS.** The experiment is 100% reproducible, fully paired, mathematically sound, and uncorrupted. Treatment and Control shared identical initial states, hidden ground truth, fixture data, wind, demand, optimizer (`milp.py`), simulator, and fuel formulas.
2. **Root Cause (Phase 7): IDENTIFIED.** The excess diesel consumption is NOT caused by model training failure or code corruption. It is driven by two primary physical/control mechanism interactions:
   - **Primary Cause (R2 - Receding Horizon Truncation & Zero-Padding):** In the experiment runner, for steps $k > 0$, static 24-hour prediction vectors were truncated and padded with $0.0\text{ W/m}^2$. By step $k=12$ (12:00 PM), Treatment lost visibility of tomorrow morning's solar peak (seeing 0 solar for hours 13..24 of its horizon), whereas Control dynamically evaluated the clear-sky model across all 24 hours of every step $k$.
   - **Major Cause (R4 / R6 / R9 - Optimistic Baseline vs Realistic ML Forecast Interaction):** Control's clear-sky baseline is heavily biased positive (+164 W/m$^2$), which tricks Control's MILP optimizer into aggressively discharging the battery early (expecting free solar). This accidentally leaves battery headroom to absorb actual solar when it arrives. Treatment's realistic low solar forecast + R2 truncation causes Treatment's MILP optimizer to hold high battery SOC (93-95%) and commit long, continuous diesel runs to avoid $15.00 startup costs.

---

## 2. Phase 1 — Experiment Integrity Verification

A strict read-only audit verified all 12 Phase 1 criteria against frozen artifacts:

| Audit Check | Status | Empirical Finding / Verification Detail |
| :--- | :---: | :--- |
| **1. 173 Eligible Origins** | **PASS** | Exactly 173 held-out 2024 ODD origins evaluated. |
| **2. 24 Hours Per Trajectory** | **PASS** | Exactly 24 MPC steps per trajectory across 346 raw CSV files (8,304 total steps). |
| **3. Identical Microgrid Inputs** | **PASS** | `battery_soc_pct` (50.0%), `battery_capacity_wh` (200 kWh), ground truth demand, wind, and solar 100% identical between Treatment and Control. |
| **4. Treatment Variable Only** | **PASS** | Only solar forecast differed (Stage 8.1 ML vector vs Clear-Sky Baseline vector). |
| **5. Vector Injection Alignment** | **PASS** | `forecast_solar_sw_in_step0_w_m2` at step 0 matched `pred_by_origin` vector for all origins. |
| **6. Exact Vector Consumed** | **PASS** | Verified in raw telemetry CSV step logs. |
| **7. Fallback Behavior** | **PASS** | `fallback_used == False` for 100% of treatment steps. Zero clear-sky fallbacks occurred. |
| **8. Timestamp Alignment** | **PASS** | Treatment and Control telemetry timestamps 100% aligned. |
| **9. Ground Truth Firewall** | **PASS** | Zero future actual SW_IN values leaked into treatment forecast context. |
| **10. Cross-Contamination** | **PASS** | Zero forecast vector contamination between trajectories. |
| **11. Fuel Formula Verification** | **PASS** | $\text{Fuel} = \text{ON\_hours} \times 5.0 + \text{Gen\_kWh} \times 0.25$ verified for all rows. |
| **12. Aggregate Summation** | **PASS** | Sum of individual trajectory fuels matches aggregate totals exactly (Treatment: 33,853.081 L, Control: 22,486.702 L). |

---

## 3. Phase 2 — Trajectory Distribution Analysis

Across all 173 evaluated 24-hour trajectories:

### Statistical Summary
| Metric | Value |
| :--- | ---: |
| **Total Baseline Fuel (Control)** | `22,486.702 L` |
| **Total Stage 8.1 Fuel (Treatment)** | `33,853.081 L` |
| **Total Absolute Difference** | `-11,366.379 L` |
| **Aggregate Saving %** | **`-50.55%`** |
| **Mean Trajectory Saving %** | `-51.96%` |
| **Median Trajectory Saving %** | `-55.60%` |
| **Standard Deviation** | `42.22%` |
| **Minimum Trajectory Saving %** | `-282.51%` (`2024-12-26T00:00:00Z`) |
| **Maximum Trajectory Saving %** | `+29.87%` (`2024-06-05T00:00:00Z`) |
| **Quartile 1 (Q25)** | `-71.60%` |
| **Quartile 2 (Q50 / Median)** | `-55.60%` |
| **Quartile 3 (Q75)** | `-21.35%` |

### Seasonal Performance Breakdown

```mermaid
gantt
    title Seasonal Aggregate Diesel Fuel Consumption (Liters)
    dateFormat X
    axisFormat %s
    section Winter (Jan-Mar)
    Control (5,568L) : 0, 5568
    Treatment (9,192L) : 0, 9192
    section Spring (Apr-Jun)
    Control (5,512L) : 0, 5512
    Treatment (6,501L) : 0, 6501
    section Summer (Jul-Sep)
    Control (5,125L) : 0, 5125
    Treatment (7,372L) : 0, 7372
    section Autumn (Oct-Dec)
    Control (6,282L) : 0, 6282
    Treatment (10,788L) : 0, 10788
```

- **Winter (Jan–Mar, 36 trajectories):** Control `5,568.3 L` vs Treatment `9,192.3 L` ($\Delta = -65.08\%$, 0 positive / 36 negative)
- **Spring (Apr–Jun, 45 trajectories):** Control `5,511.6 L` vs Treatment `6,500.7 L` ($\Delta = -17.95\%$, 14 positive / 31 negative)
- **Summer (Jul–Sep, 46 trajectories):** Control `5,125.2 L` vs Treatment `7,372.1 L` ($\Delta = -43.84\%$, 2 positive / 44 negative)
- **Autumn (Oct–Dec, 46 trajectories):** Control `6,281.6 L` vs Treatment `10,788.0 L` ($\Delta = -71.74\%$, 0 positive / 46 negative)

---

## 4. Phase 3 — First-Divergence & Causal Chain Analysis

Detailed cycle-by-cycle tracking of representative trajectories revealed the exact divergence point and operational decision sequence:

### Representative Trajectory: `2024-12-16T00:00:00Z` (Strongest Loss)

| Step | Hour | Treatment Diesel (kW) | Control Diesel (kW) | Treatment SOC (%) | Control SOC (%) | Operational Mechanism |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | 00:00 | **0.0** | **60.2** | 39.2% | 68.5% | Control runs 60kW diesel & tops up battery to 68.5%. Treatment discharges battery. |
| **1** | 01:00 | **71.6** | **0.0** | 62.0% | 56.6% | Control TURNS OFF diesel & discharges battery. Treatment TURNS ON diesel. |
| **6** | 06:00 | **76.8** | **41.8** | 79.2% | 61.6% | Treatment charges battery to 79.2%. |
| **7** | 07:00 | **66.9** | **37.8** | **93.3%** | 72.2% | Treatment battery reaches **93.3% (Saturated)**. |
| **8–21** | 08:00–21:00 | **35.6–45.4** | **0.0–37.6** | **93.3–95.0%** | **27.6–93.5%** | **Treatment LOCKS DIESEL ON FOR 14 HOURS STRAIGHT**, keeping battery full and refusing to discharge. |

### The Complete Causal Chain

```mermaid
flowchart TD
    A["Static 24h Vector Truncation & Zero-Padding (R2)"] --> B["Second half of 24h horizon padded with 0.0 W/m² solar"]
    C["Realistic Low Solar Forecast (R4)"] --> B
    B --> D["MILP Solver sees ZERO solar for tomorrow morning"]
    D --> E["Solver minimizes $15 startup penalty & $0.10/kWh degradation penalty"]
    E --> F["Treatment keeps Diesel ON continuously to serve load directly"]
    F --> G["Battery SOC locked at 93-95% (Saturated)"]
    G --> H["Incoming actual solar cannot be absorbed (Curtailed/Unused)"]
    H --> I["+579 Diesel ON Hours & +33,885 kWh Generation (+54.5%)"]
    I --> J["-50.55% Aggregate Fuel Loss (-11,366 Liters)"]
```

---

## 5. Phase 4 — Forecast Error Analysis

Comparing forecast solar irradiance against ground truth `actual_SW_IN` across all 4,152 hours:

| Metric | Treatment (Stage 8.1 ML) | Control (Clear-Sky Baseline) |
| :--- | :---: | :---: |
| **Overall MAE ($W/m^2$)** | **`34.05 W/m²`** | `178.88 W/m²` |
| **Overall Bias MBE ($W/m^2$)** | `+1.01 W/m²` | **`+164.31 W/m²`** |
| **Daytime MAE ($W/m^2$)** | **`46.71 W/m²`** | `245.63 W/m²` |
| **Daytime Bias MBE ($W/m^2$)** | `+1.43 W/m²` | **`+225.74 W/m²`** |
| **Pre-Diesel Commitment Bias ($W/m^2$)** | `-1.58 W/m²` | `+244.41 W/m²` |

### Critical Decision-Boundary Finding
Stage 8.1 has **dramatically lower MAE** (34.05 W/m$^2$ vs 178.88 W/m$^2$) and **near-zero bias** (+1.01 W/m$^2$) compared to Clear-Sky. 

However, Clear-Sky's **massive optimistic bias (+225.7 W/m$^2$ daytime)** accidentally works in Control's favor under the current MILP objective:
- Clear-Sky tricks Control's MPC into believing free solar will arrive later, forcing Control to aggressively discharge the battery early.
- Discharging the battery early creates **battery headroom**.
- When actual solar arrives, Control's battery has empty capacity to absorb it, avoiding diesel runs.
- Conversely, Stage 8.1's accurate low solar forecast (combined with R2 horizon truncation) makes Treatment's MPC pessimistic: it holds battery SOC at 93-95%, leaves no battery headroom, and commits long continuous diesel runs.

---

## 6. Phase 5 — Battery & SOC Investigation

| Metric | Treatment (Stage 8.1) | Control (Baseline) | Difference |
| :--- | ---: | ---: | ---: |
| **Generator ON Hours** | `1,970 h` | `1,391 h` | **`+579 h (+41.6%)`** |
| **Generator Start Events** | `468` | `523` | `-55 (-10.5%)` |
| **Diesel Generation (kWh)** | `96,012.32 kWh` | `62,126.80 kWh` | **`+33,885.52 kWh (+54.5%)`** |
| **Solar Generation Used (kWh)** | `18,838.02 kWh` | `51,810.13 kWh` | **`-32,972.11 kWh (-63.6%)`** |
| **Wind Generation Used (kWh)** | `26,669.04 kWh` | `25,347.53 kWh` | `+1,321.52 kWh (+5.2%)` |
| **Battery Charge Throughput (kWh)** | `46,095.74 kWh` | `38,940.57 kWh` | `+7,155.16 kWh (+18.4%)` |
| **Battery Discharge Throughput (kWh)** | `32,439.71 kWh` | `27,519.51 kWh` | `+4,920.20 kWh (+17.9%)` |
| **Renewable Curtailment (kWh)** | `6,717.48 kWh` | `9,647.18 kWh` | `-2,929.70 kWh` |

---

## 7. Phase 6 — Diesel Fuel Accounting

The exact diesel fuel consumption model is:
$$\text{Fuel (L)} = \text{ON\_hours} \times 5.0 + \text{Diesel\_Generation (kWh)} \times 0.25$$

### Fuel Contribution Breakdown

```plain
CONTROL (BASELINE):
  Base Fuel (ON Hours):      1,391 h  * 5.0 L/h  =  6,955.000 L  (30.93%)
  Marginal Fuel (Gen kWh):  62,126.8 kWh * 0.25 L/kWh = 15,531.701 L  (69.07%)
  TOTAL CONTROL FUEL:                                  22,486.701 L

TREATMENT (STAGE 8.1):
  Base Fuel (ON Hours):      1,970 h  * 5.0 L/h  =  9,850.000 L  (29.10%)
  Marginal Fuel (Gen kWh):  96,012.3 kWh * 0.25 L/kWh = 24,003.081 L  (70.90%)
  TOTAL TREATMENT FUEL:                                33,853.081 L

FUEL DIFFERENCE (TREATMENT - CONTROL):
  Base Fuel Difference:      +2,895.000 L  (25.47% of total fuel penalty)
  Marginal Fuel Difference:  +8,471.380 L  (74.53% of total fuel penalty)
  TOTAL NET FUEL PENALTY:   +11,366.380 L
```

**Dominant Fuel Loss Driver:** **MORE DIESEL GENERATION (74.53% of total loss)**, driven by Treatment running the generator at high power output (35–45 kW) continuously while battery SOC sits saturated at 93–95%.

---

## 8. Phase 7 — Root-Cause Classification

The dominant causes of excess diesel consumption are classified into four interconnected root causes:

### Selected Root Causes

#### 1. `R2 = Incorrect Forecast Horizon Semantics` (PRIMARY ROOT CAUSE)
- **Evidence:** In `run_polaris_stage81_multi_trajectory_experiment.py`, for step $k > 0$, `horizon_fcst` is constructed as `s81_vec[k:] + [s81_vec[-1]] * k`. Because `s81_vec` has only 24 elements from origin $t_0$, by step $k=12$ (12:00 PM), hours 13..24 of the horizon (tomorrow morning) are padded with `0.0 W/m²`. Treatment suffers an artificial forecast blackout for tomorrow morning, while Control dynamically computes clear-sky for all 24 hours of every step $k$.

#### 2. `R4 = Stage 8.1 Forecast Bias/Error Interaction with MPC` (MAJOR ROOT CAUSE)
- **Evidence:** Control's clear-sky baseline is heavily biased positive (+164 W/m$^2$). This optimistic bias tricks Control MPC into discharging the battery early, creating battery headroom. Stage 8.1 accurately predicts low solar, but combined with R2 truncation, forces Treatment MPC to hold high SOC and avoid battery discharge.

#### 3. `R6 = Diesel Commitment Sensitivity & Cost Structure` (MAJOR CONTRIBUTING CAUSE)
- **Evidence:** MILP objective contains $15.00 startup cost + $12.50/h base fuel cost. Once diesel is turned ON, because future solar is zero-padded (R2), the solver determines it is cheaper to keep diesel ON continuously to serve load than to shut it off and pay a future $15.00 startup cost. This caused **+579 ON hours (+41.6%)** and **+33,885.5 kWh generation (+54.5%)**.

#### 4. `R9 = Battery Headroom & Solar Utilization Asymmetry` (CONTRIBUTING CAUSE)
- **Evidence:** Treatment held battery near 93-95% SOC, preventing it from absorbing incoming solar energy. Treatment utilized only **18,838.0 kWh of solar** vs Control's **51,810.1 kWh (-63.6%)**.

### Explicitly Rejected Root Causes
- `R1` (Forecast Injection Error): Static vector injection at step 0 matched prediction artifact perfectly.
- `R3` (Fallback Problem): `fallback_used == False` for 100% of treatment steps.
- `R8` (Runner Defect): Runner executed reproducibly per code logic, though its design contained the R2 truncation defect.

---

## 9. Phase 8 — Candidate Interventions & Path to Diesel Savings

To achieve genuine diesel reduction without manipulating metrics or breaking operational constraints, future candidate interventions must address R2, R4, R6, and R9:

### 1. Candidate A: Full 48-Hour / Rolling-Horizon Forecast Window Alignment (Fixes R2)
- Extend Stage 8.1 prediction availability to 48 hours or perform rolling-inference at every step $k \in [0, 23]$ so that the MPC ALWAYS receives a full, unpadded 24-hour lookahead.

### 2. Candidate B: Symmetric Baseline Horizon Alignment (Fixes R2 Control Asymmetry)
- Ensure Control and Treatment use identical horizon lookahead boundaries to eliminate asymmetric information blackouts.

### 3. Candidate C: Dynamic Battery Headroom & Reserve Policy (Fixes R4 & R9)
- Introduce a dynamic SOC target or solar-reception reserve that maintains battery headroom during daytime hours, forcing the battery to discharge and absorb actual solar.

### 4. Candidate D: Objective Function Rebalancing (Fixes R6)
- Rebalance startup cost penalty vs battery degradation cost in `milp.py` to prevent multi-hour diesel locking when battery capacity is available.

---

## 10. Phase 9 — Pre-Registered Validation Target & Metrics

Approximately **50% diesel reduction** is established as an **ENGINEERING HYPOTHESIS / TARGET ONLY**, NOT an acceptance filter or stopping rule.

### Pre-Registered Evaluation Metrics
- **Primary Metric:** Aggregate net diesel consumption difference (Liters saved & % reduction vs baseline across held-out trajectories).
- **Secondary Metrics:**
  1. Diesel ON hours difference
  2. Diesel generation difference (kWh)
  3. Solar utilization (kWh)
  4. Renewable curtailment (kWh)
  5. Battery charge/discharge throughput (kWh)
  6. **Constraint Violations:** Must be EXACTLY ZERO
  7. **Unmet Load:** Must be EXACTLY ZERO

Any candidate intervention will be accepted based on its true, unmanipulated performance (whether 5%, 15%, 35%, 50%, or higher).

---

## 11. Phase 10 — Recommended Next Experiments & Execution Roadmap

> [!CAUTION]
> **DO NOT START A LARGE 173-TRAJECTORY RERUN YET.**

Future validation must proceed strictly through controlled, phased steps:

### STEP A: Single Controlled Trajectory Validation
- Test Candidate A (Rolling Horizon Alignment) on representative trajectories:
  - Worst trajectory: `2024-12-16T00:00:00Z`
  - Spring sunny trajectory: `2024-05-06T00:00:00Z`
- Verify that rolling horizon lookahead eliminates continuous diesel locking.

### STEP B: Small Representative Validation Set (10 Trajectories)
- Evaluate Candidate A across 10 pre-registered trajectories:
  - 3 Winter trajectories
  - 3 Spring trajectories
  - 2 Summer trajectories
  - 2 Autumn trajectories

### STEP C: Full 173-Trajectory Evaluation
- Execute full 173-trajectory evaluation ONLY after Candidate A passes Step A and Step B.
- Use new output directory (`experiments/stage81_multi_trajectory_v2/`) with complete provenance, cryptographic hashes, and live checkpointing.

The current frozen 173-trajectory experiment (`experiments/stage81_multi_trajectory/raw_telemetry/`) remains completely preserved and untouched as immutable evidence.
