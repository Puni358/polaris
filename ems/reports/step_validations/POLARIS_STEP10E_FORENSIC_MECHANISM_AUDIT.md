# POLARIS Step 10E: Forensic Mechanism Audit Report

> [!NOTE]
> **Audit Type:** READ-ONLY Forensic Mechanism Audit  
> **Experiment ID:** `POLARIS_STAGE8_1_H10_ML_FORECAST_TREATMENT_VS_BASELINE`  
> **Trajectory Origin:** `2024-06-01T00:00:00Z`  
> **Rerun Performed:** `False` (Zero MILP solves / zero simulator steps during audit execution)  
> **Source Modifications:** `0`  
> **Result Classification:** **`A — MECHANISM FULLY RECONCILED`**

---

## 1. Scope & Read-Only Governance Constraints

This audit report delivers an empirical, read-only forensic explanation of the completed Step 10E paired experiment comparing the Stage 8.1 ML forecast treatment (`POLARIS_STAGE8_1_H10_ML_FORECAST_TREATMENT`) against the clear-sky baseline control (`POLARIS_BASELINE_RULE_BASED_CONTROL`).

Per governance rules:
- No experiment rerun was executed during this audit.
- No Stage8.1 retraining or prediction regeneration was performed.
- All protected source code, schemas, H1.0 fixtures, optimizer implementations, and telemetry CSVs remained 100% byte-for-byte untouched.
- Observed experimental results were audited and explained strictly from empirical evidence.

---

## 2. Authoritative Step 10E Experiment Identity

- **Treatment Policy:** `POLARIS_STAGE8_1_H10_ML_FORECAST_TREATMENT`
- **Control Policy:** `POLARIS_BASELINE_RULE_BASED_CONTROL`
- **Trajectory Origin:** `2024-06-01T00:00:00Z`
- **Horizon & MPC Cycles:** 24 cycles (1-hour timesteps, 24-hour lookahead horizon)
- **Initial StationState:** SOC = 50.0% (100,000 Wh), Diesel = OFF (`e5883089fd82ea51...`)
- **Ground Truth Fixture:** `POLARIS_HYBRID_FIXTURE_H1_0` (`762297aae21c0cb9...`)
- **MILP Optimizer Identity:** `system/optimization/implementations/milp.py` (`ee913b68b736602e...`)
- **Stage8.1 Prediction Artifact:** `stage8_1_official_odd_predictions.csv` (`213a71e132f51ed5...`)
- **Solver Status:** All 24 Treatment and 24 Control solves achieved `OPTIMAL`. Zero fallbacks activated.

---

## 3. Frozen Paired Result Summary

| Metric | Treatment (`Stage 8.1 ML`) | Control (`Baseline Clear-Sky`) | Paired Difference ($\Delta = 	ext{Treatment} - 	ext{Control}$) |
| :--- | :---: | :---: | :---: |
| **Diesel Fuel Consumed** | **`121.463 L`** | **`125.461 L`** | **`-3.997 L`** (`-3.19%`) |
| **Diesel Generation** | `325.854 kWh` | `321.843 kWh` | `+4.011 kWh` |
| **Solar Generation Used** | `251.900 kWh` | `310.686 kWh` | `-58.786 kWh` |
| **Wind Generation Used** | `78.215 kWh` | `78.215 kWh` | `0.000 kWh` |
| **Renewable Curtailment** | `0.000 kWh` | `0.000 kWh` | `0.000 kWh` |
| **Battery Charge Throughput** | `181.424 kWh` | `193.150 kWh` | `-11.726 kWh` |
| **Battery Discharge Throughput** | `162.802 kWh` | `119.753 kWh` | `+43.049 kWh` |
| **Unmet Load** | `0.000 kWh` | `0.000 kWh` | `0.000 kWh` |
| **Generator Operating Hours** | **`8 Hours`** | **`9 Hours`** | **`-1 Hour`** |

---

## 4. Reconstructed 24 MPC Cycles Comparison Table

The cycle-level telemetry reconstructed from the frozen treatment and control runs:

| Cycle | Timestamp | Trt Diesel (W) | Ctl Diesel (W) | Trt Chg (W) | Ctl Chg (W) | Trt Dis (W) | Ctl Dis (W) | Trt PV (W) | Ctl PV (W) | Trt SOC | Ctl SOC | Trt Fcst (W/m²) | Ctl Fcst (W/m²) | Actual (W/m²) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 00 | 2024-06-01T00:00:00Z | 42794.1 | 10153.7 | 27513.7 | 0.0 | 0.0 | 5544.1 | 417.4 | 0.0 | 50.0% | 50.0% | 8.2 | 0.0 | 4.0 |
| 01 | 2024-06-01T01:00:00Z | 14769.2 | 10000.0 | 0.0 | 0.0 | 327.1 | 5697.8 | 601.5 | 0.0 | 62.7% | 47.0% | 11.8 | 0.0 | 15.3 |
| 02 | 2024-06-01T02:00:00Z | 14365.6 | 0.0 | 508.0 | 0.0 | 0.0 | 15697.8 | 1840.2 | 0.0 | 62.5% | 43.9% | 36.1 | 0.0 | 37.5 |
| 03 | 2024-06-01T03:00:00Z | 14163.3 | 0.0 | 1205.6 | 0.0 | 0.0 | 15697.8 | 2740.1 | 0.0 | 62.7% | 35.4% | 53.7 | 0.0 | 47.1 |
| 04 | 2024-06-01T04:00:00Z | 0.0 | 0.0 | 0.0 | 0.0 | 9766.5 | 9728.2 | 5931.3 | 5969.6 | 63.3% | 26.8% | 116.3 | 117.0 | 73.5 |
| 05 | 2024-06-01T05:00:00Z | 0.0 | 20857.8 | 0.0 | 16870.1 | 10024.7 | 0.0 | 5673.1 | 11710.1 | 58.0% | 21.5% | 111.2 | 229.6 | 127.7 |
| 06 | 2024-06-01T06:00:00Z | 0.0 | 0.0 | 0.0 | 0.0 | 9857.2 | 2097.4 | 9240.6 | 17000.3 | 52.5% | 29.3% | 181.2 | 333.3 | 118.6 |
| 07 | 2024-06-01T07:00:00Z | 0.0 | 0.0 | 0.0 | 0.0 | 14644.3 | 4260.5 | 11253.5 | 21637.3 | 47.1% | 28.2% | 220.7 | 424.3 | 113.6 |
| 08 | 2024-06-01T08:00:00Z | 46747.2 | 55804.8 | 26941.8 | 48549.8 | 0.0 | 0.0 | 12892.3 | 25442.9 | 39.2% | 25.9% | 252.8 | 498.9 | 170.1 |
| 09 | 2024-06-01T09:00:00Z | 0.0 | 0.0 | 0.0 | 673.0 | 9332.0 | 0.0 | 18265.8 | 28270.8 | 51.6% | 48.2% | 358.1 | 554.3 | 290.7 |
| 10 | 2024-06-01T10:00:00Z | 0.0 | 0.0 | 0.0 | 2414.2 | 5824.2 | 0.0 | 21773.5 | 30012.0 | 46.5% | 48.5% | 426.9 | 588.5 | 368.7 |
| 11 | 2024-06-01T11:00:00Z | 0.0 | 0.0 | 674.1 | 3002.2 | 0.0 | 0.0 | 28271.9 | 30600.0 | 43.4% | 49.6% | 554.4 | 600.0 | 380.6 |
| 12 | 2024-06-01T12:00:00Z | 0.0 | 0.0 | 5710.6 | 5611.7 | 0.0 | 0.0 | 30110.9 | 30012.0 | 43.7% | 51.0% | 590.4 | 588.5 | 310.2 |
| 13 | 2024-06-01T13:00:00Z | 0.0 | 0.0 | 3762.5 | 1233.0 | 0.0 | 0.0 | 30800.3 | 28270.8 | 46.3% | 53.6% | 603.9 | 554.3 | 347.6 |
| 14 | 2024-06-01T14:00:00Z | 0.0 | 0.0 | 0.0 | 0.0 | 1276.5 | 2154.9 | 26321.3 | 25442.9 | 48.0% | 54.1% | 516.1 | 498.9 | 252.7 |
| 15 | 2024-06-01T15:00:00Z | 0.0 | 0.0 | 2632.5 | 3696.0 | 0.0 | 0.0 | 20573.7 | 21637.3 | 47.3% | 53.0% | 403.4 | 424.3 | 177.2 |
| 16 | 2024-06-01T16:00:00Z | 0.0 | 0.0 | 0.0 | 0.0 | 15613.8 | 10597.4 | 11984.0 | 17000.3 | 48.5% | 54.7% | 235.0 | 333.3 | 78.6 |
| 17 | 2024-06-01T17:00:00Z | 63334.7 | 0.0 | 42754.3 | 0.0 | 0.0 | 12939.1 | 4068.8 | 11710.1 | 40.0% | 48.9% | 79.8 | 229.6 | 96.5 |
| 18 | 2024-06-01T18:00:00Z | 75787.4 | 0.0 | 50000.0 | 0.0 | 0.0 | 23176.1 | 3358.2 | 5969.6 | 59.7% | 41.9% | 65.8 | 117.0 | 69.3 |
| 19 | 2024-06-01T19:00:00Z | 53892.5 | 86097.8 | 19720.8 | 50000.0 | 0.0 | 0.0 | 1926.0 | 0.0 | 82.7% | 29.3% | 37.8 | 0.0 | 47.8 |
| 20 | 2024-06-01T20:00:00Z | 0.0 | 65429.4 | 0.0 | 39531.6 | 24294.5 | 0.0 | 1603.3 | 0.0 | 91.8% | 52.3% | 31.4 | 0.0 | 21.8 |
| 21 | 2024-06-01T21:00:00Z | 0.0 | 47465.9 | 0.0 | 21568.1 | 24832.4 | 0.0 | 1065.3 | 0.0 | 78.6% | 70.5% | 20.9 | 0.0 | 5.5 |
| 22 | 2024-06-01T22:00:00Z | 0.0 | 10000.0 | 0.0 | 0.0 | 18655.9 | 9097.8 | 441.9 | 0.0 | 65.1% | 80.4% | 8.7 | 0.0 | 5.3 |
| 23 | 2024-06-01T23:00:00Z | 0.0 | 16034.0 | 0.0 | 0.0 | 18352.7 | 3063.8 | 745.1 | 0.0 | 55.0% | 75.4% | 14.6 | 0.0 | 6.8 |

---

## 5. First Material Dispatch Divergence Analysis

### Earliest Divergent Cycle: **Cycle 00 (`2024-06-01T00:00:00Z`)**

1. **Treatment Solar Forecast ($t=0$):** `8.2 W/m²` (PV generation = 417.4 W). Lookahead vector correctly anticipated reduced daytime solar.
2. **Control Solar Forecast ($t=0$):** `0.0 W/m²` (PV generation = 0.0 W). Lookahead vector assumed ideal clear-sky solar (peaking at 600 W/m² at $t=11$).
3. **Forecast Difference ($\Delta$):** `+8.2 W/m²` at $t=0$; daytime lookahead difference up to `-246.1 W/m²` at $t=6$.
4. **Hidden Actual Solar Truth:** `4.0 W/m²` (PV generation = 204.0 W).
5. **Treatment Forecast Error:** `+4.2 W/m²` at $t=0$.
6. **Control Forecast Error:** `-4.0 W/m²` at $t=0$.
7. **Treatment Dispatch Decision:** `Diesel = 42,794.1 W`, `Battery Charge = 27,513.7 W`, `Battery Discharge = 0.0 W`.
8. **Control Dispatch Decision:** `Diesel = 10,153.7 W`, `Battery Charge = 0.0 W`, `Battery Discharge = 5,544.1 W`.
9. **Battery State Entering Cycle 00:** SOC = 50.0% (100,000.0 Wh) for both.
10. **Decision Variables Changed:** `diesel_power_command_w`, `battery_charge_command_w`, `battery_discharge_command_w`.

### Propagation Tracing:
- **Early Phase (Cycles 00-03):** Treatment pre-charges battery early at night to 62.7% SOC. Control operates diesel at minimum power (10 kW), letting battery drain to 21.5% SOC at Cycle 05.
- **Midday Phase (Cycles 04-16):** Control's over-optimistic clear-sky forecast fails as actual solar is overcast. Control is forced to discharge battery to cover load shortfalls.
- **Evening Phase (Cycles 17-19):** Treatment executes concentrated diesel block-charging (63.3 kW - 75.8 kW) raising battery SOC to **91.79%** at Cycle 20.
- **Final Phase (Cycles 20-23):** Treatment **shuts off the diesel generator completely for 4 consecutive hours** (Cycles 20-23), discharging 86.1 kWh from the battery. Control, lacking sufficient battery reserve, is forced to run diesel continuously for Cycles 19-23.

---

## 6. Solar Forecast Mechanism & Error Analysis

Across all 24 hours of the trajectory:
- **Hours with Different Forecasts:** **`24 / 24`**
- **Max Absolute Difference:** **`246.09 W/m²`** (at Cycle 06)
- **Mean Absolute Difference:** **`72.35 W/m²`**
- **Mean Signed Difference:** **`-48.03 W/m²`** (Stage8.1 ML forecast is less optimistic than clear-sky baseline)
- **Hours ML > Baseline:** `12 Hours` (night/early morning and solar elevation edge cases)
- **Hours ML < Baseline:** `12 Hours` (daytime overcast hours 04-11, 15-18)
- **Hours ML Closer to Actual Truth:** **`18 / 24 Hours`**
- **Hours ML Farther from Actual Truth:** `6 / 24 Hours`
- **Irradiance MAE:** ML = **`78.16 W/m²`** vs Baseline = **`137.80 W/m²`**
- **Irradiance RMSE:** ML = **`121.20 W/m²`** vs Baseline = **`178.23 W/m²`**

> [!IMPORTANT]
> **Scientific Integrity Guardrail:** Stage 8.1 ML is demonstrably more accurate in MAE/RMSE on this trajectory, but the lower diesel consumption is a consequence of how the MILP optimizer responded to the lower predicted solar, NOT proof of universal forecasting superiority.

---

## 7. Battery & SOC Mechanism

- **Initial State:** 100,000 Wh (50.0% SOC) for both Treatment and Control.
- **Treatment Final State:** 89,951.5 Wh (44.98% SOC, net $\Delta E = -10.05$ kWh).
- **Control Final State:** 147,531.8 Wh (73.77% SOC, net $\Delta E = +47.53$ kWh).
- **Treatment Battery Discharging:** `162.802 kWh` (+43.049 kWh vs Control `119.753 kWh`).
- **Treatment Battery Charging:** `181.424 kWh` (-11.726 kWh vs Control `193.150 kWh`).

### Mechanistic Role of Increased Battery Discharge:
Treatment utilized the battery as a buffer to shift energy temporally:
1. Block-charged battery to 91.8% SOC during evening generator operation (Cycles 17-19).
2. Deep-discharged the battery during night hours (Cycles 20-23) to eliminate generator runtime.
3. Control over-charged the battery at the end of the horizon, ending at 73.77% SOC (leaving 57.58 kWh more stored energy in the battery at the expense of 1 additional generator operating hour).

---

## 8. Solar Used vs Diesel Fuel — Resolution of Apparent Paradox

### The Apparent Paradox:
How did Treatment consume **3.997 L LESS diesel fuel** while using **58.786 kWh LESS solar energy** and generating **4.011 kWh MORE diesel electrical energy**?

### Mechanistic Resolution:
1. **Non-Linear / Affine Diesel Fuel Formula:**
   $$	ext{Fuel (L)} = egin{cases} 5.0 	ext{ L/h} + 0.00025 	ext{ L/Wh} 	imes P_{	ext{diesel}} & 	ext{if } P_{	ext{diesel}} > 0 \ 0 & 	ext{if } P_{	ext{diesel}} = 0 \end{cases}$$
   Every operating hour incurs a **fixed base overhead penalty of 5.0 Liters**, regardless of load.
2. **Reduction in Generator Operating Hours:**
   - Treatment operated diesel for **8 hours** (Base fuel = $8 	imes 5.0 = 40.000$ L).
   - Control operated diesel for **9 hours** (Base fuel = $9 	imes 5.0 = 45.000$ L).
   - **Base Fuel Difference:** **`-5.000 Liters`** (1 full generator operating hour saved).
3. **Higher Power Load Factor:**
   - Treatment generated 325.854 kWh over 8 hours (average power when ON = 40.73 kW). Marginal fuel = $325.854 	imes 0.25 = +81.463$ L.
   - Control generated 321.843 kWh over 9 hours (average power when ON = 35.76 kW). Marginal fuel = $321.843 	imes 0.25 = +80.461$ L.
   - **Marginal Fuel Difference:** **`+1.003 Liters`**.
4. **Net Fuel Calculation:**
   $$\Delta 	ext{Fuel} = -5.000 	ext{ L (fixed base overhead)} + 1.003 	ext{ L (extra marginal energy)} = \mathbf{-3.997 	ext{ Liters}}$$

---

## 9. Diesel Fuel Accounting Reconciliation

| Metric | Treatment | Control | Difference ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Total Diesel Generation** | `325.854 kWh` | `321.843 kWh` | `+4.011 kWh` |
| **Generator Operating Hours** | `8 Hours` | `9 Hours` | `-1 Hour` |
| **Base Overhead Fuel ($5.0$ L/h)** | `40.000 L` | `45.000 L` | `-5.000 L` |
| **Marginal Energy Fuel ($0.25$ L/kWh)** | `81.463 L` | `80.461 L` | `+1.003 L` |
| **Total Observed Diesel Fuel** | **`121.463 L`** | **`125.461 L`** | **`-3.997 L`** |
| **Effective Fuel Rate (L/kWh)** | **`0.3728 L/kWh`** | **`0.3898 L/kWh`** | **`-0.0170 L/kWh`** (`-4.36%`) |

---

## 10. Energy-Balance Reconciliation

### Treatment Case Reconciliation:
- **Total Generation:** Diesel ($325.854$) + Solar Used ($251.900$) + Wind Used ($78.215$) = **`655.969 kWh`**
- **Initial Stored Energy:** **`100.000 kWh`**
- **Total Energy Input:** $655.969 + 100.000 = \mathbf{755.969 	ext{ kWh}}$
- **Load Served:** **`637.347 kWh`**
- **Final Stored Energy:** **`89.952 kWh`**
- **Battery Losses:** Charge Loss ($181.424 	imes 0.08 = 14.514$) + Discharge Loss ($162.802 	imes (1/0.92 - 1) = 14.157$) = **`28.671 kWh`**
- **Curtailment & Unmet Load:** `0.000 kWh`
- **Total Energy Accounting:** $637.347 + 89.952 + 28.671 = \mathbf{755.970 	ext{ kWh}}$
- **Energy Balance Residual:** **`0.001 kWh`** (100% mathematically exact reconciliation).

### Control Case Reconciliation:
- **Total Generation:** Diesel ($321.843$) + Solar Used ($310.686$) + Wind Used ($78.215$) = **`710.744 kWh`**
- **Initial Stored Energy:** **`100.000 kWh`**
- **Total Energy Input:** $710.744 + 100.000 = \mathbf{810.744 	ext{ kWh}}$
- **Load Served:** **`637.347 kWh`**
- **Final Stored Energy:** **`147.532 kWh`**
- **Battery Losses:** Charge Loss ($193.150 	imes 0.08 = 15.452$) + Discharge Loss ($119.753 	imes (1/0.92 - 1) = 10.413$) = **`25.865 kWh`**
- **Curtailment & Unmet Load:** `0.000 kWh`
- **Total Energy Accounting:** $637.347 + 147.532 + 25.865 = \mathbf{810.744 	ext{ kWh}}$
- **Energy Balance Residual:** **`0.000 kWh`** (100% mathematically exact reconciliation).

---

## 11. SOC Reporting Anomaly Audit

- **Reported Range Summary:** Treatment SOC: `39.2–91.8%`, Control SOC: `21.5% → 80.4%`.
- **Raw Telemetry Verification:**
  - Treatment min entering SOC = `39.19%` (Cycle 08), max = `91.79%` (Cycle 20).
  - Control min entering SOC = `21.54%` (Cycle 05), max = `80.38%` (Cycle 22).
- **Audit Findings:**
  1. Both ranges are **genuine min/max SOC boundaries** recorded during the 24 MPC cycles.
  2. The string `21.5% → 80.4%` represents min-to-max boundary range (`21.5% min to 80.4% max`), NOT start-to-end SOC trajectory.
  3. Both runs initialized at exactly 50.0% SOC (100,000 Wh). Final SOC at cycle 23 was 44.98% (Treatment) vs 73.77% (Control).

---

## 12. Forecast → Optimizer → Battery → Diesel Causal Chain

```plain
Stage 8.1 ML forecast provided lower daytime solar (-48.03 W/m² mean signed diff, MAE 78.16 vs 137.80 W/m²)
        ↓
Optimizer at Cycle 00 & Cycles 17-19 foresaw lower solar availability and high evening load
        ↓
Optimizer dispatched high-power diesel block-charging (42.8 kW at C0, 63.3-75.8 kW at C17-18)
        ↓
Battery SOC reached 91.79% at C20 (vs Control min 21.54% at C5 and gradual charging)
        ↓
Treatment shut OFF generator for Cycles 20-23 (4 consecutive hours), reducing total generator ON hours from 9 to 8
        ↓
Non-linear fuel curve (5 L/h base + 0.00025 L/Wh marginal) saved 5.000 L base overhead fuel while consuming +1.003 L extra marginal fuel
        ↓
Observed paired diesel fuel reduction of -3.997 Liters (-3.19%)
```

---

## 13. Artifact & Accounting Integration Anomaly Audit

- **Inconsistent SOC Reporting:** Resolved (min/max range representation confirmed).
- **Aggregate vs Cycle Metrics:** 100% consistent across raw CSV, JSON manifests, and simulator steps.
- **Sign Errors / Double Counting:** None detected.
- **Initial State & Ground Truth Mismatch:** Verified 100% identical.
- **Fallback Activation / Hidden Leakage:** Zero fallbacks activated, firewall passed 100%.

---

## 14. Evidence Classification

- **`OBSERVED` Facts:**
  - Treatment Diesel Fuel: 121.463 L; Control Diesel Fuel: 125.461 L ($\Delta = -3.997$ L).
  - Treatment Generator ON Hours: 8 Hours; Control: 9 Hours ($\Delta = -1$ Hour).
  - Treatment Battery Discharge: 162.802 kWh; Control: 119.753 kWh ($\Delta = +43.049$ kWh).
  - Treatment Final SOC: 44.98%; Control Final SOC: 73.77%.
- **`DERIVED` Facts:**
  - Base fuel overhead saved: $1 	ext{ hour} 	imes 5.0 	ext{ L/h} = 5.000$ Liters.
  - Extra marginal energy fuel: $+4.011 	ext{ kWh} 	imes 0.25 	ext{ L/kWh} = +1.003$ Liters.
  - Net fuel savings: $-5.000 + 1.003 = -3.997$ Liters.
- **`INFERRED` Mechanisms:**
  - High battery SOC at Cycle 20 (91.79%) directly enabled the MILP solver to leave the diesel generator OFF during Cycles 20-23.
- **`NOT ESTABLISHED` Claims:**
  - That Stage 8.1 ML forecast will achieve 3.19% fuel savings across other weather regimes or real station operations.

---

## 15. Final Mechanism Classification

### Classification: **`A — MECHANISM FULLY RECONCILED`**

The telemetry, MPC solver decisions, simulator energy accounting, and affine diesel generator fuel curve provide a complete, mathematically exact, and empirical explanation for the observed result.

---

## 16. Exact Limitations & Claim Boundaries

- **Allowed Claim:** *"Under the controlled H1.0 hybrid engineering environment for origin 2024-06-01T00:00:00Z, the Stage 8.1 ML solar forecast treatment achieved a paired diesel reduction of -3.997 L (-3.19%) compared to the same-truth baseline control by eliminating 1 generator operating hour."*
- **Prohibited Claims:** Do NOT claim real-world station fuel savings, universal 3.19% savings, or production readiness.

---

## 17. SHA-256 Hashes of Audit Outputs

- **`POLARIS_STEP10E_FORENSIC_MECHANISM_AUDIT.json` SHA-256:** `468b28bbf65720f7fc4878f3aa786874233d4a7a261f273ddb19c8066c25f0e3`
- **`POLARIS_STEP10E_FORENSIC_MECHANISM_AUDIT.md` SHA-256:** `b78c0879b828ee159e3ca77d10769a82abbc56e7214f680927ebf5b46471e21d`

```plain
STEP10E_RESULT = VALID_PAIRED_EXPERIMENT
RESULT_CLASSIFICATION = A_MECHANISM_FULLY_RECONCILED
```
