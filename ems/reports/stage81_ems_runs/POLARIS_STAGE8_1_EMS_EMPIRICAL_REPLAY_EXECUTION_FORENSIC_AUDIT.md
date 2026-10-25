# POLARIS — POST-EXECUTION FORENSIC VALIDITY AUDIT REPORT
## STAGE8.1 → EMS EMPIRICAL REPLAY EXPERIMENT

**DOCUMENT ID:** `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION_FORENSIC_AUDIT`  
**DATE (UTC):** 2026-09-19  
**TRACK:** SCIENTIFIC RESEARCH & SYSTEM INTEGRATION TRACK  
**PHASE:** POST-EXECUTION FORENSIC AUDIT  
**AUDIT TYPE:** STRICT READ-ONLY FORENSIC VALIDITY AUDIT (ZERO MODIFICATIONS / ZERO RERUNS)  
**FINAL AUDIT CLASSIFICATION:** **`B — EXECUTION COMPLETED BUT HAS GOVERNED/RELEVANT DEVIATIONS REQUIRING CORRECTION BEFORE SCIENTIFIC INTERPRETATION`**  
**RESULT VALIDITY:** **`INVALID_UNDER_FROZEN_PROTOCOL`**  
**TIMESTAMP:** 2026-09-19T13:03:00+05:30  

---

> [!CAUTION]
> **STRICT READ-ONLY FORENSIC AUDIT — ZERO EXPERIMENT MODIFICATION / ZERO RERUN:**  
> This artifact records a strict, read-only forensic audit of the completed execution script (`run_polaris_stage8_1_ems_empirical_replay.py`), raw evidence (`POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_RAW.csv`), execution manifest (`POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.json`), and execution report (`POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.md`).  
> **ZERO CODE WAS MODIFIED, ZERO EXPERIMENTS WERE RERUN, ZERO ARTIFACTS WERE OVERWRITTEN, AND ALL HISTORICAL EVIDENCE HAS BEEN PRESERVED UNTOUCHED.**

---

## 1. AUTHORITATIVE PROTOCOL IDENTITY

The forensic audit evaluated the completed execution against the authoritative frozen protocol artifacts:
* `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXPERIMENT_AUTHORIZATION.md` & `.json`
* `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_AUTHORIZATION_VERIFICATION.md` & `.json`
* `POLARIS_STAGE8_1_EMPIRICAL_REPLAY_PATH_VERIFICATION.md` & `.json`

---

## 2. EXECUTION SCRIPT & ARTIFACT IDENTITY

* **Execution Script:** `run_polaris_stage8_1_ems_empirical_replay.py`
* **Raw Evidence CSV:** `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_RAW.csv` (SHA-256: `56dfeb8dcc54de380a4d1f810f796e4f5ef120a227136ead096f66968c5b4ca2`)
* **Execution JSON Manifest:** `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.json` (SHA-256: `6e31b1c1509826157ca59be9f2377c1113d23e3910bde23a743f1c18813e88ac`)
* **Execution MD Report:** `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.md` (SHA-256: `1d5ced105d8df2f4e97ad3c8bd1ae90378b945271bd68989d30f84bb918b420e`)

---

## 3. TREATMENT VALUE INTEGRITY AUDIT

* **Requirement:** Protocol Section 3 strictly required: *"The experiment MUST replay the frozen empirical prediction values exactly... Do NOT smooth, clip, interpolate, recalibrate, replace missing values, or substitute another artifact."*
* **Forensic Finding:** In `run_polaris_stage8_1_ems_empirical_replay.py`, line 141:
  ```python
  sw_in_forecast = [round(float(r["y_pred"]), 2) for r in o_rows[step_k:]]
  ```
  The execution script explicitly applied 2-decimal rounding (`round(..., 2)`) to all injected treatment $y_{\text{pred}}$ values before supplying them to `Stage81ForecastEngine.predict()`.
* **Root Cause Analysis:** `Stage81ForecastEngine.validate_stage81_solar_metadata` in `system/forecasting/implementations/s81_solar.py` enforces a strict $1 \times 10^{-4}$ tolerance on the D3 PV transformation ($P = SW_{\text{IN}} \times 51.0$). Because `s81_solar.py` internally rounds $P_{\text{solar}}$ to 2 decimal places while leaving raw $SW_{\text{IN}}$ unrounded, unrounded high-precision floats from `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` (e.g. `12.744275635189387`) trigger a validation `ValueError`. The execution script introduced 2-decimal rounding to bypass this validation crash.
* **Audit Verdict:** **`TREATMENT_VALUE_EXACTNESS = FAIL`** (The injected values were altered by rounding rather than replaying exact frozen CSV floats).

---

## 4. MPC HORIZON SEMANTICS AUDIT

* **Forensic Inspection:** In `run_polaris_stage8_1_ems_empirical_replay.py`, lines 141–143:
  ```python
  sw_in_forecast = [round(float(r["y_pred"]), 2) for r in o_rows[step_k:]]
  if len(sw_in_forecast) < 24:
      sw_in_forecast += [0.0] * (24 - len(sw_in_forecast))
  ```
* **Reconstructed Treatment Forecast Vector per MPC Timestep:**
  * **Step 0 ($k=0$):** Horizons $h_1 \dots h_{24}$ (24 valid empirical prediction values).
  * **Step 1 ($k=1$):** Horizons $h_2 \dots h_{24} + [0.0]$ (23 empirical predictions + 1 trailing zero pad).
  * **Step 2 ($k=2$):** Horizons $h_3 \dots h_{24} + [0.0, 0.0]$ (22 empirical predictions + 2 trailing zero pads).
  * **Step $k$:** Horizons $h_{k+1} \dots h_{24} + k$ trailing zeros.
  * **Step 23 ($k=23$):** Horizon $h_{24} + 23$ trailing zeros (1 empirical prediction + 23 trailing zero pads).
* **Audit Verdict:** The treatment forecast horizon shrank by 1 step at every MPC iteration and was padded with zeroes ($0.0\,\text{W/m}^2$), forcing an artificial zero-solar forecast over increasing portions of the 24-step horizon.

---

## 5. PROTOCOL SEMANTICS AUDIT

* **QUESTION A (Intended origin forecast replay):** Was the frozen empirical artifact intended to provide a 24-hour forecast at origin $t_0$ for the 24-hour replay horizon?  
  * **Answer:** YES. The artifact `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` is an out-of-distribution origin-level forecast dataset containing 173 unique origins ($t_0$), each issued at 24-hour intervals with a 24-step horizon ($h=1 \dots 24$).
* **QUESTION B (New forecast per MPC step):** Was a new 24-hour forecast expected at every MPC step?  
  * **Answer:** Receding-horizon MPC requires a 24-step forecast starting at $t_k$. However, the frozen CSV does **not** contain sub-origin forecasts issued at intermediate steps $t_0 + k$.
* **QUESTION C (Sufficient information in CSV for sub-origin 24h forecasts):** Does the CSV contain sub-origin predictions for $t_0 + k$?  
  * **Answer:** NO. The CSV contains predictions **only** for origin timestamps $t_0$, spaced 24 hours apart.
* **QUESTION D (Does zero-padding represent authorized Stage8.1 forecast?):**  
  * **Answer:** NO. Zero-padding ($0.0\,\text{W/m}^2$) is an arbitrary synthetic fallback, not an authorized Stage8.1 model prediction.
* **QUESTION E (Experimental difference beyond treatment vs control):** Does shrinking the forecast horizon introduce an experimental confound?  
  * **Answer:** YES. Shrinking the treatment horizon while zero-padding forces the Treatment optimizer to operate under severe artificial information truncation relative to Control.

---

## 6. CONTROL VS TREATMENT SEMANTICS COMPARISON

* **Control Behavior (`LocalBaselineForecastEngine`):** Generated a full 24-hour diurnal clear-sky forecast at **every** MPC step $k \in \{0 \dots 23\}$.
* **Treatment Behavior (`Stage81ForecastEngine` with sliced CSV):** Received a shrinking forecast horizon ($24-k$ steps) padded with $k$ trailing zeros at every MPC step $k \in \{0 \dots 23\}$.
* **Summary Table:**

| Semantic Dimension | Control Condition (Baseline) | Treatment Condition (Stage8.1) | Structural Match? |
| :--- | :--- | :--- | :--- |
| **Forecast Origin** | $t_k$ (Re-computed at each step $k$) | $t_0$ (Sliced from origin CSV) | ❌ **MISMATCH** |
| **Horizon Length** | 24 valid forecast hours at all steps | $24-k$ valid hours + $k$ zero pads | ❌ **MISMATCH** |
| **Trailing Padding** | None (Full diurnal curve) | Up to 23 trailing zeros ($0.0\,\text{W/m}^2$) | ❌ **MISMATCH** |
| **HORIZON_SEMANTICS_MATCH** | — | — | **`NO`** |

* **Confound Severity:** **HIGH.** The observed fuel deficit in Treatment (+5.91 L/origin) was heavily driven by the fact that Treatment was forced to optimize under zero-padded shrinking horizons, whereas Control enjoyed a complete 24-hour solar forecast at every step.

---

## 7. PAIRING INTEGRITY & FUTURE-TRUTH FIREWALL AUDIT

* **Initial-State Identity (`CONTROL_INITIAL_STATE_ID == TREATMENT_INITIAL_STATE_ID`):** **`VERIFIED`**. Initial state snapshot ($\text{SOC}_0 = 50.0\%$, $E_0 = 100\,\text{kWh}$) was identical for both conditions.
* **Realized-Trajectory Identity (`CONTROL_REALIZED_TRAJECTORY_ID == TREATMENT_REALIZED_TRAJECTORY_ID`):** **`VERIFIED`**. Ground truth actuals ($y_{\text{true}}$, wind, demand) were 100% identical.
* **Future-Truth Firewall:** **`VERIFIED`**. Ground-truth actuals were fetched **after** optimization and supplied strictly to simulator/evaluator.

---

## 8. RAW EVIDENCE AUDIT

* **Audited Artifact:** `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_RAW.csv`
* **Finding:** `RAW.csv` preserves origin-level summary endpoints (total fuel, energy, throughput) but does **not** log the step-level injected 24-step forecast arrays or per-step dispatch decisions.
* **Implication:** Step-level zero-padding cannot be detected directly from `RAW.csv` alone; it was identified via code auditing of `run_polaris_stage8_1_ems_empirical_replay.py`.

---

## 9. REPORTED RESULTS VALIDITY ASSESSMENT

* **Reported Results:** Total Treatment Fuel: $5,694.24\text{ L}$ vs Control: $4,671.00\text{ L}$ ($\Delta = +5.9147\text{ L/origin}$, Wilcoxon $p = 1.8637 \times 10^{-3}$, 95% CI $[+1.5662\text{ L}, +10.2804\text{ L}]$).
* **Audit Verdict:** **`RESULT_VALIDITY = INVALID_UNDER_FROZEN_PROTOCOL`**
* **Reasoning:** The reported fuel deficit of Stage8.1 relative to Control cannot be attributed to empirical Stage8.1 forecast error because the Treatment condition was severely confounded by the shrinking-horizon zero-padding implementation bug.

---

## 10. DETERMINISM & PROTOCOL-HASH AUDIT

1. **Determinism Claim Audit:**
   * Execution report claimed: `"100% DETERMINISTIC & REPRODUCIBLE (Seed=42)"`.
   * Finding: `np.random.seed(42)` was set **only** for the bootstrap resampling loop. Seed=42 guarantees bootstrap reproducibility given fixed raw data, but does **not** prove full physical MPC replay determinism.
2. **Protocol Hash Claim Audit:**
   * Execution report claimed: `PROTOCOL_HASH: a4d288f9bba4a57c...`.
   * Finding: `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` is the SHA-256 hash of `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` (the dataset), not the protocol document hash.

---

## 11. SUMMARY OF IDENTIFIED DEVIATIONS

1. **DEVIATION 1 (Value Truncation):** Injected predictions were rounded to 2 decimal places (`round(float(r['y_pred']), 2)`), violating exact raw float preservation.
2. **DEVIATION 2 (Horizon Slicing & Zero-Padding):** Treatment forecast array was sliced (`o_rows[step_k:]`) and zero-padded in receding-horizon MPC, reducing valid forecast length by 1 hour at each step.
3. **DEVIATION 3 (Asymmetric Horizon Semantics):** Control received a full 24-hour diurnal clear-sky forecast at all 24 MPC steps, while Treatment received a shrinking, zero-padded forecast.
4. **DEVIATION 4 (Protocol Hash Mislabling):** Prediction dataset SHA-256 was reported in the manifest as `PROTOCOL_HASH`.
5. **DEVIATION 5 (Determinism Scope Mislabling):** Bootstrap random seed (`Seed=42`) was cited as proof of full experiment determinism.

---

## 12. FINAL GOVERNANCE CLASSIFICATION

```yaml
FINAL_GOVERNANCE_CLASSIFICATION: B — EXECUTION COMPLETED BUT HAS GOVERNED/RELEVANT DEVIATIONS REQUIRING CORRECTION BEFORE SCIENTIFIC INTERPRETATION
RESULT_VALIDITY: INVALID_UNDER_FROZEN_PROTOCOL
```

* **Classification Rationale:** The 173-origin replay execution completed cleanly without solver or runtime crashes, but contains material implementation deviations (2-decimal rounding, zero-padded shrinking-horizon asymmetry) that invalidate the reported scientific endpoints.

---

## 13. EXPLICIT NEXT GOVERNED STEP

1. **Preserve Historical Evidence:** Do **NOT** rerun, overwrite, or delete `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.md`, `.json`, or `RAW.csv`.
2. **Submit Replay Architecture Correction Plan:** Formalize a governance correction plan to resolve the MPC replay horizon architecture for origin-based empirical forecast artifacts:
   * Either execute origin replays as single 24-hour horizon open-loop optimizations (matching single-origin forecast issuance), OR
   * Formalize an explicit sub-origin forecast provider contract if receding-horizon MPC is required.
3. **Fix Validator Floating-Point Tolerance:** Update `Stage81ForecastEngine` PV metadata validation tolerance to support exact unrounded high-precision floats from `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`.

---

## 14. FINAL AUDIT SUMMARY BLOCK

```yaml
AUDIT_STATUS: FORENSIC_AUDIT_COMPLETE
AUDIT_DECISION: B — EXECUTION COMPLETED BUT HAS GOVERNED/RELEVANT DEVIATIONS REQUIRING CORRECTION BEFORE SCIENTIFIC INTERPRETATION
RESULT_VALIDITY: INVALID_UNDER_FROZEN_PROTOCOL
TREATMENT_VALUE_EXACTNESS: FAIL (2-decimal rounding applied)
HORIZON_SEMANTICS_MATCH: NO (Treatment shrinking/zero-padded vs Control full 24h)
FUTURE_TRUTH_FIREWALL: VERIFIED
INITIAL_STATE_IDENTITY_STATUS: VERIFIED
REALIZED_TRAJECTORY_IDENTITY_STATUS: VERIFIED
RAW_EVIDENCE_LOGGING_STATUS: INCOMPLETE_STEP_LEVEL_LOGGING
PROTOCOL_HASH_STATUS: MISLABELED (Dataset SHA-256 reported as protocol hash)
DETERMINISM_CLAIM_STATUS: MISLABELED (Bootstrap seed reported as full experiment seed)
HISTORICAL_EVIDENCE_PRESERVED: YES (Zero files modified or overwritten during audit)
NEXT_GOVERNED_STEP: Submit formal correction plan to align MPC replay horizon architecture before re-executing.
```
