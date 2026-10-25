# POLARIS Step 10C: Read-Only Forensic Audit — Treatment vs Control Trajectory

## Executive Summary

A read-only forensic audit has been performed to investigate why the Step 10B H1.0 treatment trajectory and the Step 10C baseline control trajectory produced **100% bit-for-bit identical dispatch commands** and an identical observed fuel consumption of **195.500 L**.

- **Executed Treatment Optimizer:** `LocalMILPEnergyOptimizer` (Unweighted MILP, `gamma=1.0`)
- **Executed Control Optimizer:** `LocalMILPEnergyOptimizer` (Unweighted MILP, `gamma=1.0`)
- **Treatment Policy Metadata Label:** `POLARIS_STAGE8_1_EMS_V4G`
- **Control Policy Metadata Label:** `POLARIS_BASELINE_RULE_BASED_CONTROL`
- **Forecast Input Comparison:** **100% Bit-for-Bit Identical across all 24 MPC cycles**
- **Dispatch Decision Comparison:** **100% Bit-for-Bit Identical across all 24 MPC cycles**
- **Same-Truth & Firewall Status:** **`PASS`**
- **Solver Identity & Solves:** `scipy.optimize.milp` / HiGHS — **24/24 `OPTIMAL` solves** for both runs
- **Mechanism Classification:** **`B`** (*Forecasts were effectively identical, so the experiment did not test forecast sensitivity*)

---

## 1. Files Inspected & Cryptographic Hashes

| File Path | SHA-256 Hash | Status / Purpose |
| :--- | :--- | :---: |
| `POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv` | `762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023` | **FROZEN** (Input Fixture) |
| `system/optimization/implementations/milp.py` | `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35` | **FROZEN** (MILP Optimizer) |
| `POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION_RAW.csv` | `27a2f6b260dc759526f4c3feb2e329d32a802945d85cefc9159219d2870ac81b` | **FROZEN** (Treatment Telemetry) |
| `POLARIS_HYBRID_H1_0_CONTROL_RAW.csv` | `ae51359b145f92f8b24169aef1f70b701de56b06cbab77aca4ca5f1df8c5a1a8` | **FROZEN** (Control Telemetry) |
| `POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION.json` | `c5ce9864b83c5d0972082b67a80ed2c17cd7593a29c4d1e9c79451dcae0e3276` | Treatment Manifest |
| `POLARIS_HYBRID_H1_0_CONTROL.json` | `dc8b7dc89576732a4d5d1a5c5b09a7f031809e848207f145a3b531b0c6ba52de` | Control Manifest |
| `POLARIS_HYBRID_H1_0_TREATMENT_CONTROL_COMPARISON.json` | `449a14ebf73f57acb689df93ea72db2176fcc2dab183428871d1785a4e0bb56e` | Comparison Manifest |
| `scripts/execute_step10b_validation.py` | `14e20dcf06c50c2171fbc0338e3cffaf9652ac3b8ae5b68579250c8d4c00d080` | Treatment Execution Code |
| `scripts/execute_step10c_control.py` | `f89fd44dfea9a4f29bbf91e5004022b4f949f2dddf259ecd7e43631cdb11abff` | Control Execution Code |

---

## 2. Exact Treatment Identity & Configuration Verification

- **Stated Metadata Label:** `POLARIS_STAGE8_1_EMS_V4G`
- **Executed Script:** `scripts/execute_step10b_validation.py`
- **Executed Optimizer Class:** `LocalMILPEnergyOptimizer`
- **V4.G Single-Horizon Mode Enabled:** **`False`** (Omitted from `configs["optimizer"]`; defaulted to `False`)
- **Custom Objective Weights Active:** **`False`** (`custom_weight_vector = None`)
- **Horizon Discount Factor ($\gamma$):** **`1.0`** (Unweighted baseline horizon cost accumulation)
- **Discrepancy Findings:**
  1. The label `POLARIS_STAGE8_1_EMS_V4G` in the execution manifests was a carried-over metadata designation.
  2. The actual optimizer configuration executed in Step 10B treatment was standard unweighted MILP (`gamma=1.0`), which is identical to the optimizer configuration executed in Step 10C control.

---

## 3. Forecast Difference Verification

Comparing the exact 24-step forecast vectors generated and consumed at every MPC cycle $k \in [0..23]$:

- **Solar Irradiance & Generation Forecast:** **100% Bit-for-Bit Identical**
- **Wind Generation Forecast:** **100% Bit-for-Bit Identical**
- **Demand Forecast:** **100% Bit-for-Bit Identical**
- **Timestamps & Horizon Alignment:** **100% Bit-for-Bit Identical**

### Mechanism of Forecast Identity:
In Step 10B, `Stage81ForecastEngine.predict()` was invoked without passing a precomputed ML prediction vector (`stage81_sw_in_forecast`) in `runtime_context`. Consequently, `Stage81ForecastEngine` executed its internal fallback clear-sky model:
$$\text{irr} = \text{round}\left(800.0 \times \sin\left(\frac{(\text{hour} - 4)\pi}{16}\right) \times 0.75, 2\right)$$
`LocalBaselineForecastEngine.predict()` (used in Step 10C control) evaluates the exact same clear-sky formula for solar irradiance and calls the same persistence generators for wind and demand. As a result, both engines generated **100% bit-for-bit identical ForecastBundle objects** for all 24 MPC cycles.

---

## 4. Step-by-Step 24-Cycle Dispatch Comparison

| Cycle $k$ | Timestamp | Treatment Diesel (W) | Control Diesel (W) | Treatment Charge (W) | Control Charge (W) | Treatment Discharge (W) | Control Discharge (W) | Treatment SOC (%) | Control SOC (%) | Objective Value |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **00** | 00:00 | 68,818.87 | 68,818.87 | 46,821.09 | 46,821.09 | 0.00 | 0.00 | 71.54 | 71.54 | 163.87 |
| **01** | 01:00 | 0.00 | 0.00 | 0.00 | 0.00 | 21,997.78 | 21,997.78 | 59.58 | 59.58 | 116.03 |
| **02** | 02:00 | 0.00 | 0.00 | 0.00 | 0.00 | 21,997.78 | 21,997.78 | 47.63 | 47.63 | 132.52 |
| **03** | 03:00 | 0.00 | 0.00 | 0.00 | 0.00 | 21,997.78 | 21,997.78 | 35.67 | 35.67 | 156.38 |
| **04** | 04:00 | 0.00 | 0.00 | 0.00 | 0.00 | 16,028.23 | 16,028.23 | 26.96 | 26.96 | 173.49 |
| **05** | 05:00 | 42,247.45 | 42,247.45 | 31,959.78 | 31,959.78 | 0.00 | 0.00 | 41.66 | 41.66 | 203.58 |
| **06** | 06:00 | 49,290.66 | 49,290.66 | 39,808.46 | 39,808.46 | 0.00 | 0.00 | 59.97 | 59.97 | 258.34 |
| **07** | 07:00 | 41,309.19 | 41,309.19 | 26,548.67 | 26,548.67 | 0.00 | 0.00 | 72.19 | 72.19 | 448.22 |
| **08** | 08:00 | 66,231.49 | 66,231.49 | 46,276.59 | 46,276.59 | 0.00 | 0.00 | 93.47 | 93.47 | 605.88 |
| **09** | 09:00 | 0.00 | 0.00 | 0.00 | 0.00 | 10,526.95 | 10,526.95 | 87.75 | 87.75 | 435.81 |
| **10** | 10:00 | 0.00 | 0.00 | 0.00 | 0.00 | 8,582.35 | 8,582.35 | 83.09 | 83.09 | 443.21 |
| **11** | 11:00 | 0.00 | 0.00 | 0.00 | 0.00 | 8,197.78 | 8,197.78 | 78.63 | 78.63 | 457.95 |
| **12** | 12:00 | 0.00 | 0.00 | 0.00 | 0.00 | 8,785.81 | 8,785.81 | 73.86 | 73.86 | 465.60 |
| **13** | 13:00 | 0.00 | 0.00 | 0.00 | 0.00 | 10,526.95 | 10,526.95 | 68.14 | 68.14 | 476.48 |
| **14** | 14:00 | 0.00 | 0.00 | 0.00 | 0.00 | 13,354.90 | 13,354.90 | 60.88 | 60.88 | 484.24 |
| **15** | 15:00 | 0.00 | 0.00 | 0.00 | 0.00 | 16,326.20 | 16,326.20 | 52.01 | 52.01 | 485.15 |
| **16** | 16:00 | 0.00 | 0.00 | 0.00 | 0.00 | 19,945.34 | 19,945.34 | 41.17 | 41.17 | 486.55 |
| **17** | 17:00 | 0.00 | 0.00 | 0.00 | 0.00 | 24,377.86 | 24,377.86 | 27.92 | 27.92 | 500.35 |
| **18** | 18:00 | 36,488.23 | 36,488.23 | 0.00 | 0.00 | 0.00 | 0.00 | 27.92 | 27.92 | 643.91 |
| **19** | 19:00 | 44,563.46 | 44,563.46 | 0.00 | 0.00 | 0.00 | 0.00 | 27.92 | 27.92 | 662.93 |
| **20** | 20:00 | 36,397.78 | 36,397.78 | 0.00 | 0.00 | 0.00 | 0.00 | 27.92 | 27.92 | 493.73 |
| **21** | 21:00 | 36,397.78 | 36,397.78 | 0.00 | 0.00 | 0.00 | 0.00 | 27.92 | 27.92 | 486.70 |
| **22** | 22:00 | 63,459.27 | 63,459.27 | 36,661.49 | 36,661.49 | 0.00 | 0.00 | 44.78 | 44.78 | 288.88 |
| **23** | 23:00 | 76,797.78 | 76,797.78 | 50,000.00 | 50,000.00 | 0.00 | 0.00 | 67.78 | 67.78 | 256.89 |

*Verification:* Zero difference across all 24 timesteps for every decision vector.

---

## 5. Same-Truth Pairing Verification

- **Initial StationState SHA-256:** `3e38d4f5e3046d642c26b56a84e9e0130b0bfddea24be37640b90a4fd2c55fbd` (**PASS**)
- **Input Fixture CSV SHA-256:** `762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023` (**PASS**)
- **Trajectory Window:** `2024-01-01T00:00:00Z` to `2024-01-01T23:00:00Z` (**PASS**)
- **Same-Truth Firewall:** Verified zero future ground truth passed to optimizer (**PASS**)
- **Treatment Telemetry Integrity:** [POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION_RAW.csv](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION_RAW.csv) hash `27a2f6b2...` (**100% UNTOUCHED**)

---

## 6. Solver Verification

- **Solver Engine:** `scipy.optimize.milp` / HiGHS C++ solver backend
- **Treatment Solves:** 24/24 `OPTIMAL`
- **Control Solves:** 24/24 `OPTIMAL`
- **Fallback Solver Triggered:** `False`
- **Solver Settings / Tolerances Difference:** None (`100% identical`)

---

## 7. Metric Reconciliation

- **Treatment Diesel Fuel:** `195.500 L`
- **Control Diesel Fuel:** `195.500 L`
- **Paired Fuel Difference ($\Delta$):** `0.000 L` (`0.00%`)
- **Unrounded Exact Equality:** Verified. Raw float sum of fuel consumption equals `195.500332... L` in both trajectories.
- **Secondary Quantities:**
  - Diesel Electrical Generation: `562.002 kWh`
  - Solar Used: `310.686 kWh`
  - Wind Used: `67.889 kWh`
  - Renewable Curtailment: `0.000 kWh`
  - Load Served: `865.147 kWh`
  - Unmet Load: `0.000 kWh`
  - Battery Charge Throughput: `278.076 kWh`
  - Battery Discharge Throughput: `202.646 kWh`
  - Battery SOC Range: `26.96% – 93.47%`

---

## 8. Scientific Interpretation Statement

**Question:** *"Did this experiment demonstrate that the Stage8.1 forecasting model improved EMS optimization?"*

**Strict Evidence Statement:** **`NO.`** Because the H1.0 adapter path did not pass a precomputed Stage8.1 ML forecast array into `runtime_context`, `Stage81ForecastEngine` defaulted to the exact same diurnal clear-sky persistence fallback as `LocalBaselineForecastEngine`. As a result, both treatment and control received 100% identical forecast inputs and produced 100% identical dispatch decisions (195.500 L fuel). While the closed-loop MPC execution, Same-Truth Firewall, and MILP solver correctness were successfully validated, this specific paired trajectory did not evaluate forecast sensitivity or demonstrate an operational fuel improvement from Stage8.1.

---

## Final Classification

```plain
STEP10C_FORENSIC_RESULT = B
```
