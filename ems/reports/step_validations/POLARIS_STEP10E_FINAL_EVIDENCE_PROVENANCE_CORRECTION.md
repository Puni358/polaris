# POLARIS Step 10E: Final Evidence Provenance Correction Report

> [!IMPORTANT]
> **Audit Type:** FINAL READ-ONLY GOVERNANCE AUDIT  
> **Rerun / Reconstruction / New Solves:** `FALSE` (0 MILP solves / 0 simulator steps / 0 trajectory reruns)  
> **Source Modifications:** `0`  
> **Governance Status:**
> - `STEP10E_TREATMENT_EVIDENCE = FROZEN_VALID`
> - `STEP10E_CONTROL_RAW_EVIDENCE = NOT_AVAILABLE`
> - `STEP10E_REPORTED_PAIRED_RESULT = PRESERVED`
> - `STEP10E_INDEPENDENT_PAIRED_REPRODUCIBILITY = NOT_ESTABLISHED`
>
> **Final Evidence Classification:** **`B — REPORTED IN FROZEN COMPARISON ARTIFACTS BUT CONTROL LACKS INDEPENDENT RAW TELEMETRY`**  
> **JSON Artifact SHA-256:** `0c22168f9470c9fbededa4b33509544b20d688da41943e3b529639cee88b7b0a`

---

## 1. Scope & Strict Governance Constraints

This report provides the final read-only evidence provenance correction for Step 10E:
- **Treatment Policy:** `POLARIS_STAGE8_1_H10_ML_FORECAST_TREATMENT`
- **Control Policy:** `POLARIS_BASELINE_RULE_BASED_CONTROL`
- **Treatment Trajectory Origin:** `2024-06-01T00:00:00Z`

### Absolute Governance Constraints
1. **ZERO Reruns or Solves:** No MILP solves (`control_optimizer.optimize()`), simulator steps (`simulator.step()`), forecast predictions (`predict()`), or trajectory reconstructions were performed.
2. **Read-Only Evidence Firewall:** All evaluations are strictly grounded in existing frozen files.
3. **Historical Evidence Preservation:** Historical evidence files remain untouched. This document and `POLARIS_STEP10E_FINAL_EVIDENCE_PROVENANCE_CORRECTION.json` are standalone final correction artifacts.

---

## 2. Frozen Artifact Inventory & SHA-256 Hashes

The exact frozen Step 10E evidence inventory is as follows:

| Category | File Path | Origin Timestamp | SHA-256 Hash | Evidence Status |
| :--- | :--- | :---: | :--- | :---: |
| **A. Treatment Raw Telemetry** | `POLARIS_HYBRID_H1_0_STAGE81_TREATMENT_RAW.csv` | `2024-06-01T00:00:00Z` | `3d514b6ef45b63dcafaf7077497142c240e9cdd8a76cb37c295973ea16805546` | **`FROZEN_VALID`** |
| **A. Treatment Manifest** | `POLARIS_HYBRID_H1_0_STAGE81_TREATMENT.json` | `2024-06-01T00:00:00Z` | `61dafd11a2a185472a38d453c271c167edd7b49d16e3673fb600c6414b8511c3` | **`FROZEN_VALID`** |
| **B. Control Raw Telemetry** | `POLARIS_HYBRID_H1_0_CONTROL_RAW.csv` | `2024-01-01T00:00:00Z` | `ae51359b145f92f8b24169aef1f70b701de56b06cbab77aca4ca5f1df8c5a1a8` | **`VALID_FOR_2024_01_01_ONLY`** |
| **B. Control Manifest** | `POLARIS_HYBRID_H1_0_CONTROL.json` | `2024-01-01T00:00:00Z` | `dc8b7dc89576732a4d5d1a5c5b09a7f031809e848207f145a3b531b0c6ba52de` | **`VALID_FOR_2024_01_01_ONLY`** |
| **C. Comparison Metadata** | `POLARIS_HYBRID_H1_0_STAGE81_TREATMENT_CONTROL_COMPARISON.json` | `2024-06-01T00:00:00Z` | `8a6b7a6e7c542baa7e84867b1e7b9eaa61223f84036c66793f04aa5eb5f78aae` | **`PRESERVED_METADATA`** |

```plain
CRITICAL FINDING: The frozen control raw CSV (POLARIS_HYBRID_H1_0_CONTROL_RAW.csv) is for origin 2024-01-01T00:00:00Z.
No separate frozen raw control CSV exists for origin 2024-06-01T00:00:00Z.
THEREFORE: CONTROL_RAW_EVIDENCE_FOR_2024_06_01 = NOT_AVAILABLE
```

---

## 3. Critical Issue #1: Gross Metrics Evaluation

The larger metric values reported in previous specification summaries:
- **Solar:** Treatment 417.828 kWh / Control 476.614 kWh
- **Wind:** Treatment 121.465 kWh / Control 121.465 kWh
- **Battery Charge:** Treatment 348.650 kWh / Control 360.376 kWh
- **Battery Discharge:** Treatment 304.538 kWh / Control 261.489 kWh

### Governance Evaluation:
Forensic inspection of all frozen CSVs, JSON manifests, and Python scripts in the Step 10E repository confirms that **no frozen file or formula derives or records these exact numbers**.

Per governance rule:
> *"DO NOT call 417.828, 121.465, 348.650, or 304.538 authoritative merely because they appear in a prior report... If this cannot be demonstrated from frozen evidence, classify the gross metric as `NOT_PROVEN_AS_AUTHORITATIVE`."*

```plain
CLASSIFICATION: ALL GROSS METRICS (417.828, 476.614, 121.465, 348.650, 360.376, 304.538, 261.489) ARE 
CLASSIFIED AS NOT_PROVEN_AS_AUTHORITATIVE.
```

The verifiable metrics directly summed from frozen treatment raw telemetry (`POLARIS_HYBRID_H1_0_STAGE81_TREATMENT_RAW.csv`) are:
- **Diesel Generation:** `325.854 kWh`
- **Solar Used:** `251.900 kWh`
- **Wind Used:** `78.215 kWh`
- **Battery Charge:** `181.424 kWh`
- **Battery Discharge:** `162.802 kWh`
- **Unmet Load / Curtailment:** `0.000 kWh`
- **Generator ON Hours:** `8 Hours`
- **Diesel Fuel:** `121.463 L`

---

## 4. Provenance of Step 10E Paired Metrics

| Metric | Treatment Value | Control Value | Reported Difference (Delta) | Provenance & Evidence Category |
| :--- | :---: | :---: | :---: | :--- |
| **Diesel Fuel** | `121.463 L` | `125.461 L` | `-3.997 L` (`-3.19%`) | **Treatment:** Confirmed from raw telemetry & `treatment.json`.<br>**Control:** Preserved in comparison metadata (`comparison.json`). |
| **Diesel Generation** | `325.854 kWh` | `321.843 kWh` | `+4.011 kWh` | **Treatment:** Confirmed from raw telemetry column sum.<br>**Control:** Preserved in comparison metadata (`comparison.json`). |
| **Solar Generation Used** | `251.900 kWh` | `310.686 kWh` | `-58.786 kWh` | **Treatment:** Confirmed from raw telemetry `solar_used_command_w`.<br>**Control:** Preserved in comparison metadata. |
| **Wind Generation Used** | `78.215 kWh` | `78.215 kWh` | `0.000 kWh` | **Treatment:** Confirmed from raw telemetry `wind_used_command_w`.<br>**Control:** Preserved in comparison metadata. |
| **Battery Charge Throughput** | `181.424 kWh` | `193.150 kWh` | `-11.726 kWh` | **Treatment:** Confirmed from raw telemetry `battery_charge_command_w`.<br>**Control:** Preserved in comparison metadata. |
| **Battery Discharge Throughput** | `162.802 kWh` | `119.753 kWh` | `+43.049 kWh` | **Treatment:** Confirmed from raw telemetry `battery_discharge_command_w`.<br>**Control:** Preserved in comparison metadata. |

---

## 5. Diesel Fuel Equation Reconciliation

The diesel fuel consumption formula is defined in `system/optimization/implementations/milp.py` and `system/config/diesel.yaml`:

$$\text{Fuel (L)} = (H_{\text{on}} \times 5.0 \text{ L/h}) + (E_{\text{gen, Wh}} \times 0.00025 \text{ L/Wh})$$

### Treatment Verification (Raw Telemetry Confirmed):
- Generator ON Hours ($H_{\text{on}}$): `8 Hours`
- Diesel Generation ($E_{\text{gen, Wh}}$): `325,853.99 Wh` (`325.854 kWh`)
- Base Overhead Fuel: $8 \times 5.0 = 40.000 \text{ L}$
- Marginal Energy Fuel: $325,853.99 \times 0.00025 = 81.4635 \text{ L}$
- Total Treatment Fuel: $40.000 + 81.4635 = 121.4635 \text{ L} \approx 121.463 \text{ Liters}$ -> **`CONFIRMED FROM RAW TELEMETRY`**

### Control Arithmetic (Derived from Metadata):
- Reported ON Hours: `9 Hours`
- Reported Generation: `321,843.00 Wh` (`321.843 kWh`)
- Base Overhead Fuel: $9 \times 5.0 = 45.000 \text{ L}$
- Marginal Energy Fuel: $321,843.00 \times 0.00025 = 80.4608 \text{ L}$
- Total Control Fuel: $45.000 + 80.4608 = 125.4608 \text{ L} \approx 125.461 \text{ Liters}$ -> **`DERIVED FROM METADATA`**

### Paired Fuel Difference:
$$\Delta \text{Fuel} = -5.000 \text{ L (Base Overhead Saved)} + 1.0028 \text{ L (Extra Marginal Fuel)} = -3.9972 \text{ L} \approx -3.997 \text{ Liters (-3.19%)} -> \mathbf{PRESERVED}$$

---

## 6. Strict Evidence Boundary Classification

| Evidence Category | Boundary Definition & Items |
| :--- | :--- |
| **`OBSERVED`** | - Stage 8.1 ML forecast treatment was injected for 24 steps on origin `2024-06-01T00:00:00Z`.<br>- Treatment raw telemetry contains 24 MPC steps with 8 generator ON hours and 325.854 kWh diesel generation.<br>- Treatment raw telemetry sums: solar used = 251.900 kWh, wind used = 78.215 kWh, battery charge = 181.424 kWh, battery discharge = 162.802 kWh.<br>- Treatment diesel fuel formula evaluates to 121.463 L. |
| **`REPORTED`** | - `comparison.json` reports Control fuel = 125.461 L and paired fuel difference = -3.997 L (-3.19%).<br>- `comparison.json` reports Control generation = 321.843 kWh and paired differences. |
| **`DERIVED`** | - Treatment piecewise-affine fuel formula ($8\text{h} \times 5.0\text{ L/h} + 325.854\text{ kWh} \times 0.25\text{ L/kWh}$) yields 121.463 L.<br>- Base overhead saved (-5.000 L) + extra marginal fuel (+1.003 L) = -3.997 L. |
| **`NOT ESTABLISHED`** | - Independently verifiable raw control telemetry CSV for origin `2024-06-01T00:00:00Z` (frozen control raw CSV is for `2024-01-01T00:00:00Z`).<br>- Independently reproducible causal chain from forecast to paired fuel difference from raw telemetry alone.<br>- Authoritative status for gross metric values (417.828 solar, 121.465 wind, 348.650 charge, 304.538 discharge). |

---

## 7. Final Governance Status Block

```plain
STEP10E_TREATMENT_EVIDENCE = FROZEN_VALID
STEP10E_CONTROL_RAW_EVIDENCE = NOT_AVAILABLE
STEP10E_REPORTED_PAIRED_RESULT = PRESERVED
STEP10E_INDEPENDENT_PAIRED_REPRODUCIBILITY = NOT_ESTABLISHED

FINAL_EVIDENCE_CLASSIFICATION = B_REPORTED_IN_FROZEN_COMPARISON_ARTIFACTS_BUT_CONTROL_LACKS_INDEPENDENT_RAW_TELEMETRY
```
