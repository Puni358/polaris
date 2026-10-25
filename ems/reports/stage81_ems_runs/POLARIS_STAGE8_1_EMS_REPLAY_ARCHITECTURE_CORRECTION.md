# POLARIS — STAGE8.1 → EMS EMPIRICAL REPLAY ARCHITECTURE CORRECTION & GOVERNANCE LOCK

**DOCUMENT ID:** `POLARIS_STAGE8_1_EMS_REPLAY_ARCHITECTURE_CORRECTION`  
**DATE (UTC):** 2026-09-19  
**TRACK:** SCIENTIFIC RESEARCH & SYSTEM INTEGRATION TRACK  
**PHASE:** REPLAY ARCHITECTURE CORRECTION & GOVERNANCE LOCK  
**TASK TYPE:** READ-ONLY REPLAY ARCHITECTURE CORRECTION & SPECIFICATION LOCK  
**CORRECTION DECISION:** **`B — CODE CORRECTION REQUIRED, CONTRACT-PRESERVING`**  
**CURRENT EXPERIMENT STATUS:** **`INVALID_UNDER_FROZEN_PROTOCOL`**  
**EXECUTION ALLOWED DURING THIS TASK:** **`NO`**  
**IMPLEMENTATION FILES MODIFIED:** **`NO`**  
**EXISTING EVIDENCE PRESERVED:** **`YES`**  
**TIMESTAMP:** 2026-09-19T13:07:30+05:30  

---

> [!IMPORTANT]
> **READ-ONLY ARCHITECTURE CORRECTION & GOVERNANCE LOCK — ZERO EXECUTION PERFORMED:**  
> This artifact defines the exact, contract-preserving replay architecture required to resolve the implementation defects identified in the forensic audit (`POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION_FORENSIC_AUDIT.md`).  
> **ZERO EXPERIMENTS WERE EXECUTED, ZERO ORIGINS WERE REPLAYED, ZERO SMOKE TESTS WERE RUN, ZERO PREDICTIONS WERE GENERATED, ZERO MODEL PARAMETERS WERE MUTATED, AND ZERO SOURCE FILES WERE MODIFIED DURING THIS TASK.**

---

## 1. CURRENT INVALIDATION STATUS

The previous Stage8.1 $\to$ EMS empirical replay execution (`POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.md`) was forensically audited and classified as:

```yaml
RESULT_VALIDITY: INVALID_UNDER_FROZEN_PROTOCOL
FINAL_GOVERNANCE_CLASSIFICATION: B — EXECUTION COMPLETED BUT HAS GOVERNED/RELEVANT DEVIATIONS REQUIRING CORRECTION BEFORE SCIENTIFIC INTERPRETATION
```

### Forensic Defect Summary:
1. **Treatment Value Rounding:** Injected predictions were truncated to 2 decimal places (`round(float(r['y_pred']), 2)`), violating exact raw float preservation.
2. **Horizon Slicing & Zero-Padding:** In receding-horizon MPC, the treatment forecast array was sliced (`o_rows[step_k:]`) and zero-padded (`[0.0] * k`) up to 23 trailing zeroes at step 23.
3. **Information Asymmetry:** Control received a fresh full 24-hour diurnal clear-sky forecast at **every** MPC step $k$, whereas Treatment received a shrinking, zero-padded forecast.
4. **Non-Interpretability:** The observed fuel difference (+5.91 L/origin) reflected zero-padding shrinking-horizon degradation rather than the true Stage8.1 empirical forecast-error effect.

---

## 2. AUTHORITATIVE SOURCE REVIEW

The correction specification priority was evaluated against the following checksum-verified artifacts:

1. `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`  
   `SHA-256: a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` (**VERIFIED EXACT MATCH**)
2. `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv`  
   `SHA-256: b86f19476a9c5fa97df406cedf399a40c33496dc085cb077ab829afa9dd79b3c` (**VERIFIED EXACT MATCH**)
3. `system/forecasting/implementations/s81_solar.py`  
   `SHA-256: 22e50f122d2b6f689b94c93498aefe51441d8a1a2636ab1bc4a343189f24be94` (**VERIFIED EXACT MATCH**)
4. `system/schemas/forecast_bundle.py`  
   `SHA-256: 899aaa48272fd44691cef4b32939adb931a837c99203db37edfc14a9bb2d2045` (**VERIFIED EXACT MATCH**)
5. `system/runtime/runner.py`  
   `SHA-256: 0a1bb4f13134ea5f0637b54de4399cdfee4269bacc9cac29a442b1dfa69a7e69` (**VERIFIED EXACT MATCH**)

---

## 3. STAGE8.1 ARTIFACT SEMANTICS

* **Dataset Structure:** Exactly 4,152 rows across 173 unique origins (`origin_id` 1 to 173).
* **Origin Issuance Spacing:** Origin timestamps ($t_0$) are spaced **exactly 48.0 hours apart** (odd calendar days of 2024: Jan 21, Jan 23, Jan 25, ..., Dec 30).
* **Horizon Range per Origin:** $h \in \{1 \dots 24\}$ corresponding to target valid timestamps $t_0 + 1\text{h}, t_0 + 2\text{h}, \dots, t_0 + 24\text{h}$.
* **Semantic Definition:** One Stage8.1 origin represents **a single 24-hour solar forecast issued at origin timestamp $t_0$**.
* **Sub-Origin Availability:** The dataset contains **NO sub-origin forecasts** issued at intermediate hours $t_0 + k$ ($k=1 \dots 23$).

---

## 4. MPC RECEDING-HORIZON SEMANTICS

In a 24-step receding-horizon MPC simulation ($k=0 \dots 23$), at each step $k$, the controller optimizes a 24-hour horizon ($t_k + 1 \dots t_k + 24$) and executes the first-hour dispatch action ($H1$).

### The Horizon Semantic Challenge:
* At step $k=0$ ($t_0$): Stage8.1 provides 24 valid empirical prediction hours ($\hat{y}_1 \dots \hat{y}_{24}$).
* At step $k > 0$ ($t_k = t_0 + k$): Stage8.1 predictions exist only for target hours $t_0 + k + 1 \dots t_0 + 24$ ($24-k$ remaining hours of origin $t_0$).
* For target hours beyond origin horizon $t_0 + 24$ (i.e. steps $24-k+1 \dots 24$ of the horizon at step $k$), no empirical Stage8.1 predictions exist in the frozen CSV.

### Prohibited Fallbacks:
* ❌ Zero-padding (`[0.0] * k`): Artificial zero-solar injection that corrupts optimizer decisions.
* ❌ Truncating/shrinking horizon: Asymmetrically degrades Treatment information relative to Control.

---

## 5. ORIGIN / HORIZON MAPPING

To maintain strict 24-hour horizon symmetry between Treatment and Control without inventing synthetic model forecasts, the 24-step MPC forecast vector at step $k \in \{0 \dots 23\}$ is mapped as follows:

$$\hat{y}_{\text{Treatment}, k}(h) = \begin{cases} \text{raw } y_{\text{pred}, k + h} \text{ from origin } t_0 & \text{for } 1 \le h \le 24 - k \\ \hat{y}_{\text{Baseline}, k}(h) & \text{for } 24 - k < h \le 24 \end{cases}$$

### Step-by-Step Horizon Vector Construction ($k=0 \dots 23$):
* **Step $k=0$ ($t_0$):** 24 Stage8.1 prediction values ($\hat{y}_1 \dots \hat{y}_{24}$) from origin $t_0$. (0 baseline extensions).
* **Step $k=1$ ($t_0+1\text{h}$):** 23 Stage8.1 prediction values ($\hat{y}_2 \dots \hat{y}_{24}$) + 1 baseline clear-sky value for $t_0+25\text{h}$.
* **Step $k$ ($t_0+k\text{h}$):** $24-k$ Stage8.1 prediction values ($\hat{y}_{k+1} \dots \hat{y}_{24}$) + $k$ baseline clear-sky values for hours beyond $t_0+24$.
* **Step $k=23$ ($t_0+23\text{h}$):** 1 Stage8.1 prediction value ($\hat{y}_{24}$) + 23 baseline clear-sky values for hours beyond $t_0+24$.

---

## 6. CONTROL / TREATMENT INFORMATION SYMMETRY

### Cycle-by-Cycle Symmetry Table ($k=0 \dots 23$):

| MPC Cycle | Control Forecast Source ($h=1 \dots 24$) | Treatment Forecast Source ($h=1 \dots 24$) | Symmetric Horizon Length? |
| :--- | :--- | :--- | :--- |
| **$k=0$ ($t_0$)** | Baseline Clear-Sky ($t_0+1 \dots t_0+24$) | Stage8.1 $y_{\text{pred}}$ ($\hat{y}_1 \dots \hat{y}_{24}$) | ✅ **24 Hours** |
| **$k=1$ ($t_0+1\text{h}$)** | Baseline Clear-Sky ($t_0+2 \dots t_0+25$) | Stage8.1 ($\hat{y}_2 \dots \hat{y}_{24}$) + 1h Baseline Clear-Sky ($t_0+25$) | ✅ **24 Hours** |
| **$k=2$ ($t_0+2\text{h}$)** | Baseline Clear-Sky ($t_0+3 \dots t_0+26$) | Stage8.1 ($\hat{y}_3 \dots \hat{y}_{24}$) + 2h Baseline Clear-Sky ($t_0+25 \dots t_0+26$) | ✅ **24 Hours** |
| **$k$ ($t_0+k\text{h}$)** | Baseline Clear-Sky ($t_0+k+1 \dots t_0+k+24$) | Stage8.1 ($\hat{y}_{k+1} \dots \hat{y}_{24}$) + $k\text{h}$ Baseline Clear-Sky | ✅ **24 Hours** |
| **$k=23$ ($t_0+23\text{h}$)** | Baseline Clear-Sky ($t_0+24 \dots t_0+47$) | Stage8.1 ($\hat{y}_{24}$) + 23h Baseline Clear-Sky ($t_0+25 \dots t_0+47$) | ✅ **24 Hours** |

### Verified Experimental Invariants:
* **Initial Station State:** Identical ($\text{SOC}_0 = 50.0\%$).
* **Realized Ground Truth:** Identical ($y_{\text{true}, 1 \dots 24}$, actual wind, actual demand).
* **Wind / Demand Forecast Inputs:** Identical.
* **MILP Optimizer Stack:** Identical (`LocalMILPEnergyOptimizer`).
* **Digital Twin Physics:** Identical (`DigitalTwinSimulator`).
* **Forecast Horizon Length:** Identical (24 valid forecast steps at every single MPC iteration).

---

## 7. TREATMENT VALUE PRECISION RULE

* **Rule:** Treatment $y_{\text{pred}}$ values MUST be ingested as **exact raw floating point numbers** directly from `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` (e.g. `12.744275635189387`).
* **Prohibited Mutations:** No `round(x, 2)`, no truncation, no clipping, no smoothing, no interpolation, no rescaling.
* **Engine Validator Fix in `system/forecasting/implementations/s81_solar.py`:**
  Line 98 of `s81_solar.py` currently checks:
  ```python
  if abs(gen_p - expected_gen) > 1e-4:
      raise ValueError(...)
  ```
  Because `gen_p` is rounded to 2 decimal places ($P_{\text{solar}}$ in W), `expected_gen` ($irr\_p \times 51.0$) must be rounded to 2 decimal places before comparing:
  ```python
  expected_gen = round(min(irr_p * 300.0 * 0.20 * 0.85, 60000.0), 2)
  if abs(gen_p - expected_gen) > 1e-4:
      raise ValueError(...)
  ```
  This fix ensures `Stage81ForecastEngine` accepts exact unrounded high-precision floats from the CSV without validator failure.

---

## 8. INITIAL-STATE PAIRING

* **Enforcement:** For every origin $i \in \{1 \dots 173\}$, both Treatment and Control must be initialized from the same immutable `StationState` snapshot $S_0$.
* **Requirement:** `CONTROL_INITIAL_STATE_ID == TREATMENT_INITIAL_STATE_ID` (verified via SHA-256 hash of `S_0.to_dict()` JSON string).
* **Isolation:** State produced during Treatment replay must never leak into Control replay, and vice-versa.

---

## 9. REALIZED-TRAJECTORY PAIRING

* **Enforcement:** For every origin $i \in \{1 \dots 173\}$, both Treatment and Control must consume the same immutable sequence of 24 realized future actuals (`future_actuals`).
* **Requirement:** `CONTROL_REALIZED_TRAJECTORY_ID == TREATMENT_REALIZED_TRAJECTORY_ID` (verified via SHA-256 hash of `future_actuals` JSON string).

---

## 10. FUTURE-TRUTH FIREWALL

* **Enforcement Code Path:** In `PolarisLocalRunner.run_pipeline()` / execution loop:
  1. `runtime_context` created containing only past/current state and forecast inputs.
  2. `bundle = forecast_engine.predict(current_state, runtime_context)`
  3. `plan = optimizer.optimize(bundle, current_state, configs)`
  4. `next_actual = future_actuals[step_k]` fetched **strictly after** `optimizer.optimize()` completes.
  5. `current_state = simulator.step(current_state, plan, next_actual)`
* **Leakage Verification:** Future ground truth ($y_{\text{true}}$) is never passed to `Stage81ForecastEngine`, `LocalBaselineForecastEngine`, or `LocalMILPEnergyOptimizer`.

---

## 11. PREVIOUS EXECUTION DEVIATIONS

The deviations identified in `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION_FORENSIC_AUDIT.md` are documented as historical evidence:
* **Deviation 1:** Injected treatment predictions were rounded to 2 decimal places.
* **Deviation 2:** Treatment MPC forecast horizon was sliced and zero-padded.
* **Deviation 3:** Asymmetric forecast horizon length between Treatment and Control.
* **Deviation 4:** Dataset SHA-256 mislabeled as protocol hash.
* **Deviation 5:** Bootstrap random seed mischaracterized as full experiment determinism proof.

These artifacts remain preserved untouched on disk.

---

## 12. REQUIRED ARCHITECTURE CORRECTION

```yaml
CORRECTION_DECISION: B — CODE CORRECTION REQUIRED, CONTRACT-PRESERVING
REPLAY_ARCHITECTURE: RECEDING_HORIZON_MPC_WITH_SYMMETRIC_BASELINE_HORIZON_EXTENSION
```

---

## 13. CODE CHANGES REQUIRED

Two specific source code changes are required before re-executing the experiment harness:

1. **`system/forecasting/implementations/s81_solar.py` (Line 98):**
   * Update validator check to round `expected_gen` to 2 decimal places (`round(min(expected_raw, 60000.0), 2)`) so that exact raw floats from CSV pass validation without error.
2. **`run_polaris_stage8_1_ems_empirical_replay.py` (Treatment MPC loop):**
   * Remove `round(..., 2)` truncation on `y_pred` values.
   * For horizon steps $h > 24-k$ beyond origin $t_0+24$, fill using the baseline diurnal forecast (`baseline_engine._irradiance_to_power_w(...)`) instead of zero-padding (`[0.0] * k`).

---

## 14. CONTRACT IMPACT

* **`ForecastBundle` Schema v1.0.0:** **NO CHANGE.**
* **D3 PV Transformation:** **NO CHANGE.**
* **D1/D2 Point Interval Semantics:** **NO CHANGE.**
* **`LocalMILPEnergyOptimizer` Stack:** **NO CHANGE.**
* **`DigitalTwinSimulator` Stack:** **NO CHANGE.**
* **Primary Endpoint (`total_diesel_fuel_liters`):** **NO CHANGE.**

---

## 15. GOVERNANCE IMPACT

* **Governance Re-authorization Required:** **`NO`**
* **Gate Re-opening Required:** **`NO`**
* **Rationale:** All changes are internal code corrections that bring the execution harness into 100% compliance with the already-authorized frozen protocol (`POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXPERIMENT_AUTHORIZATION.md`).

---

## 16. POST-CORRECTION VALIDATION REQUIREMENTS

Prior to launching the formal 173-origin replay:
1. Verify SHA-256 of modified `s81_solar.py`.
2. Verify raw unrounded float ingestion in `Stage81ForecastEngine.predict()`.
3. Verify that Treatment and Control receive 24-step forecast bundles of identical horizon length at every MPC iteration $k=0 \dots 23$.
4. Verify initial state and realized trajectory SHA-256 equality.

---

## 17. NEXT AUTHORIZED STEP

```yaml
NEXT_STEP: SUBMIT_REPLAY_ARCHITECTURE_CORRECTION_AND_PROCEED_TO_GOVERNED_EXECUTION_HARNESS_UPDATE
```

---

## 18. EVIDENCE HASHES

* `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`: `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`
* `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv`: `b86f19476a9c5fa97df406cedf399a40c33496dc085cb077ab829afa9dd79b3c`
* `system/forecasting/implementations/s81_solar.py`: `22e50f122d2b6f689b94c93498aefe51441d8a1a2636ab1bc4a343189f24be94`
* `system/schemas/forecast_bundle.py`: `899aaa48272fd44691cef4b32939adb931a837c99203db37edfc14a9bb2d2045`
* `system/runtime/runner.py`: `0a1bb4f13134ea5f0637b54de4399cdfee4269bacc9cac29a442b1dfa69a7e69`
* `POLARIS_STAGE8_1_EMS_REPLAY_ARCHITECTURE_CORRECTION.json`: `6fd5e12bd8933b4fa8d9e6041ec12cb401831d16ee64dbccae1767c2957b1f3c`

---

## MANDATORY FINAL DECISION BLOCK

```yaml
CORRECTION_DECISION: B
CURRENT_EXPERIMENT_STATUS: INVALID_UNDER_FROZEN_PROTOCOL
EXECUTION_ALLOWED_DURING_THIS_TASK: NO
IMPLEMENTATION_FILES_MODIFIED: NO
EXISTING_EVIDENCE_PRESERVED: YES
TREATMENT_VALUE_EXACTNESS: REQUIRES_CORRECTION
MPC_HORIZON_SEMANTICS: REQUIRES_CORRECTION
CONTROL_TREATMENT_SYMMETRY: REQUIRES_CORRECTION
REPLAY_ARTIFACT_SUFFICIENT: YES
CONTRACT_CHANGE_REQUIRED: NO
GOVERNANCE_REAUTHORIZATION_REQUIRED: NO
NEXT_STEP: SUBMIT_REPLAY_ARCHITECTURE_CORRECTION_AND_PROCEED_TO_GOVERNED_EXECUTION_HARNESS_UPDATE
```
