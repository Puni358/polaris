# POLARIS Step 10E: Stage 8.1 ML Forecast Treatment vs Control Comparison Report

## Executive Summary

The paired same-truth engineering counterfactual comparison between the Step 10E Stage 8.1 ML solar forecast treatment trajectory and the paired baseline control trajectory (`POLARIS_BASELINE_RULE_BASED_CONTROL`) has been completed.

- **Origin Timestamp ($t_0$):** `2024-06-01T00:00:00Z`
- **Treatment Policy:** `POLARIS_STAGE8_1_H10_ML_FORECAST_TREATMENT`
- **Control Policy:** `POLARIS_BASELINE_RULE_BASED_CONTROL`
- **Stage 8.1 ML Forecast Injected:** **`TRUE`**
- **Same Initial State:** Verified (`e5883089fd82...`)
- **Same Ground Truth:** Verified (Identical H1.0 hidden solar/wind/demand trajectory)
- **Primary Endpoint (Delta Fuel):** **`-3.997 L`** (-3.19%)

---

## 1. Primary & Secondary Paired Differences

| Metric | Treatment (`Stage 8.1 ML Forecast`) | Control (`Baseline Clear-Sky`) | Paired Difference ($\Delta = \text{Treatment} - \text{Control}$) |
| :--- | :---: | :---: | :---: |
| **Diesel Fuel Consumed** | **`121.463 L`** | **`125.461 L`** | **`-3.997 L`** (`-3.19%`) |
| **Diesel Generation** | `325.854 kWh` | `321.843 kWh` | `+4.011 kWh` |
| **Solar Generation Used** | `251.900 kWh` | `310.686 kWh` | `-58.786 kWh` |
| **Wind Generation Used** | `78.215 kWh` | `78.215 kWh` | `+0.000 kWh` |
| **Renewable Curtailment** | `0.000 kWh` | `0.000 kWh` | `+0.000 kWh` |
| **Battery Charge Throughput** | `181.424 kWh` | `193.150 kWh` | `-11.726 kWh` |
| **Battery Discharge Throughput** | `162.802 kWh` | `119.753 kWh` | `+43.049 kWh` |
| **Unmet Load** | `0.000 kWh` | `0.000 kWh` | `+0.000 kWh` |

---

## 2. Methodological Statement & Interpretation

Under the controlled H1.0 hybrid engineering environment for origin `2024-06-01T00:00:00Z`, replacing the clear-sky baseline forecast with the frozen Stage 8.1 ML solar forecast resulted in a paired diesel consumption difference of **`-3.997 L`** (`-3.19%`).

---

## 3. Claim Boundary Statement

- **Allowed Claim:** *"Under the controlled H1.0 hybrid engineering environment for origin 2024-06-01T00:00:00Z, the Stage 8.1 ML solar forecast treatment achieved a paired diesel difference of -3.997 L (-3.19%) compared to the same-truth baseline control under identical initial conditions and hidden ground truth."*
- **Prohibited Claims:** *"Stage 8.1 achieved 3.997 L real-world fuel savings at Nuolja"*, *"Stage 8.1 is an EMS production champion"*, or *"Stage 8.1 guarantees real station diesel reduction"*.
