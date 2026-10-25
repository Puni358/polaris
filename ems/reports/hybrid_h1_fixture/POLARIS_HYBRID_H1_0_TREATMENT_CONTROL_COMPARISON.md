# POLARIS Step 10C: H1.0 Treatment vs Control Paired Comparison Report

## Executive Summary

The paired same-truth engineering counterfactual comparison between the Step 10B H1.0 treatment trajectory and the Step 10C control trajectory (`POLARIS_BASELINE_RULE_BASED_CONTROL`) has been completed.

- **Treatment Policy:** `POLARIS_STAGE8_1_EMS_V4G`
- **Control Policy:** `POLARIS_BASELINE_RULE_BASED_CONTROL`
- **Trajectory Window:** `2024-01-01T00:00:00Z` to `2024-01-01T23:00:00Z` (24 timesteps)
- **Same Initial State:** Verified (`3e38d4f5e304...`)
- **Same Ground Truth:** Verified (Identical H1.0 hidden solar/wind/demand trajectory)
- **Primary Endpoint (Delta Fuel):** **`-0.000 L`** (-0.00%)

---

## 1. Primary & Secondary Paired Differences

| Metric | Treatment Value | Control Value | Paired Difference (Delta = Treatment - Control) |
| :--- | :---: | :---: | :---: |
| **Diesel Fuel Consumed** | **`195.500 L`** | **`195.500 L`** | **`-0.000 L`** (`-0.00%`) |
| **Diesel Generation** | `562.002 kWh` | `562.002 kWh` | `+0.000 kWh` |
| **Solar Generation Used** | `310.686 kWh` | `310.686 kWh` | `+0.000 kWh` |
| **Wind Generation Used** | `67.889 kWh` | `67.889 kWh` | `-0.000 kWh` |
| **Renewable Curtailment** | `0.000 kWh` | `0.000 kWh` | `+0.000 kWh` |
| **Battery Charge Throughput** | `278.076 kWh` | `278.076 kWh` | `-0.000 kWh` |
| **Battery Discharge Throughput** | `202.646 kWh` | `202.646 kWh` | `+0.000 kWh` |
| **Unmet Load** | `0.000 kWh` | `0.000 kWh` | `+0.000 kWh` |

---

## 2. Methodological Statement & Interpretation

Under the controlled H1.0 hybrid engineering environment, the treatment policy used **`0.000 L`** **more** diesel than the same-truth baseline control over the 24-hour trajectory (`-0.00%` difference).

---

## 3. Claim Boundary Statement

- **Allowed Claim:** *"Under the controlled H1.0 hybrid engineering environment, the treatment policy achieved a paired diesel difference of -0.000 L (-0.00%) compared to the same-truth baseline control under identical initial conditions and hidden ground truth."*
- **Prohibited Claims:** *"POLARIS achieved 0.000 L real-world fuel savings at Nuolja"*, *"POLARIS demonstrated real station fuel reduction"*, or *"POLARIS is production-ready"*.
