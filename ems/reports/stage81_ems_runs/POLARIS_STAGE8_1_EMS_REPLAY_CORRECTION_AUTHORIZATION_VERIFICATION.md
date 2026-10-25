# POLARIS — STAGE8.1 → EMS EMPIRICAL REPLAY CORRECTION
## AUTHORIZATION-COMPATIBILITY VERIFICATION REPORT

**DOCUMENT ID:** `POLARIS_STAGE8_1_EMS_REPLAY_CORRECTION_AUTHORIZATION_VERIFICATION`  
**DATE (UTC):** 2026-09-19  
**TRACK:** SCIENTIFIC RESEARCH & SYSTEM INTEGRATION TRACK  
**PHASE:** AUTHORIZATION-COMPATIBILITY VERIFICATION GATE  
**TASK TYPE:** READ-ONLY GOVERNANCE VERIFICATION GATE (ZERO EXECUTION / ZERO CODE MODIFICATION)  
**AUTHORIZATION COMPATIBILITY:** **`PASS`**  
**IMPLEMENTATION AUTHORIZED:** **`YES`**  
**EXPERIMENT EXECUTION AUTHORIZED:** **`NO`**  
**TIMESTAMP:** 2026-09-19T13:08:45+05:30  

---

> [!IMPORTANT]
> **READ-ONLY AUTHORIZATION-COMPATIBILITY VERIFICATION COMPLETE:**  
> This artifact performs the read-only governance verification of the proposed replay architecture correction (`POLARIS_STAGE8_1_EMS_REPLAY_ARCHITECTURE_CORRECTION.md`) against the authoritative frozen experiment authorization package (`POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXPERIMENT_AUTHORIZATION.md`).  
> **ZERO CODE WAS MODIFIED, ZERO EXPERIMENTS WERE EXECUTED, ZERO ORIGINS WERE REPLAYED, AND ZERO SCIENTIFIC OR SCHEMATIC CONTRACTS WERE CHANGED.**

---

## 1. COMMON-BASELINE CONTINUATION AUDIT

* **Question:** Does the frozen authorization explicitly permit, implicitly define, or not define a common baseline continuation for MPC forecast hours beyond the available Stage8.1 empirical horizon ($h > 24-k$)?
* **Forensic Verification:**
  * In `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXPERIMENT_AUTHORIZATION.md`:
    * Section 5 & Section 10 establish `LocalBaselineForecastEngine` as the authoritative control forecast engine.
    * Section 10 defines the experimental contrast: Treatment (Stage8.1) vs Control (Baseline) executed under identical non-forecast conditions.
    * Section 12 & 18 mandate: *"The only intended experimental difference is the solar forecast supplied to the EMS."*
  * For target hours beyond the 24-hour horizon issued at origin $t_0$ ($h > 24-k$), no empirical Stage8.1 predictions exist in `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`.
  * Providing the baseline clear-sky forecast for $h > 24-k$ to **both** Treatment and Control ensures that Treatment and Control receive identical, zero-contrast baseline forecast information for hours where no empirical Stage8.1 predictions exist.
* **Classification:** **`COMMON_BASELINE_CONTINUATION_STATUS: AUTHORITATIVELY_IMPLIED`**

---

## 2. SCIENTIFIC CONTRAST VERIFICATION

* **Treatment Structure at MPC cycle $k$:**  
  $$\hat{y}_{\text{Treatment}, k}(h) = \begin{cases} \text{Stage8.1 empirical prediction } \hat{y}_{k+h} & \text{for } 1 \le h \le 24-k \\ \text{Baseline clear-sky forecast } \hat{y}_{\text{Baseline}, k}(h) & \text{for } 24-k < h \le 24 \end{cases}$$
* **Control Structure at MPC cycle $k$:**  
  $$\hat{y}_{\text{Control}, k}(h) = \text{Baseline clear-sky forecast } \hat{y}_{\text{Baseline}, k}(h) \quad \text{for } 1 \le h \le 24$$
* **Paired Difference ($\Delta \hat{y}_k$):**  
  $$\Delta \hat{y}_k(h) = \begin{cases} \hat{y}_{\text{Stage8.1}, k+h} - \hat{y}_{\text{Baseline}, k}(h) & \text{for } 1 \le h \le 24-k \\ 0.0 & \text{for } 24-k < h \le 24 \end{cases}$$
* **Verification Finding:** **`PASS`**. The ONLY difference between Treatment and Control at any MPC cycle $k$ is the Stage8.1 empirical forecast information that actually exists in the frozen artifact for origin $t_0$.

---

## 3. HORIZON SYMMETRY VERIFICATION

* **MPC Forecast Vector Length:** Exactly 24 forecast values at every MPC cycle $k \in \{0 \dots 23\}$ for both arms.
* **Target Timestamp Symmetry:** Both arms optimize over identical 24-hour target timestamp sequences ($t_k + 1 \dots t_k + 24$).
* **Distinction:**
  * 24-value MPC Horizon: Solver receives 24 forecast values at every iteration.
  * Stage8.1 Empirical Values: Exactly $24-k$ values at step $k$.
  * Baseline Continuation Values: Exactly $k$ values at step $k$.
* **Verification Finding:** **`HORIZON_SYMMETRY: PASS`**

---

## 4. TEMPORAL ALIGNMENT VERIFICATION

* **Origin Timestamp:** $t_0$
* **MPC Cycle $k \in \{0 \dots 23\}$:** Current timestamp $t_k = t_0 + k$ hours.
* **Horizon Step $j \in \{1 \dots 24\}$:** Target timestamp $t_{\text{target}} = t_k + j = t_0 + (k+j)$ hours.
  * For $k + j \le 24$: Target timestamp matches origin horizon $h = k+j$. Treatment ingests exact raw Stage8.1 $y_{\text{pred}}$ float for horizon $k+j$.
  * For $k + j > 24$: Target timestamp exceeds $t_0 + 24$. Target timestamp $t_0 + k + j$ is passed to `LocalBaselineForecastEngine._irradiance_to_power_w()` to compute clear-sky diurnal solar generation.
* **Verification Finding:** **`TEMPORAL_ALIGNMENT: PASS`**

---

## 5. 48-HOUR ORIGIN SPACING AUDIT

* **Dataset Structure:** 173 unique origins spaced 48 hours apart (odd calendar days: Jan 21, Jan 23, Jan 25, ..., Dec 30).
* **Audit Impact:**
  1. **Origin Independence:** 48-hour spacing eliminates temporal overlap between adjacent 24-hour origin replays, reinforcing independent origin sampling across the annual dataset.
  2. **MPC Replay Bounds:** Each origin $t_0$ is executed as an independent 24-hour MPC simulation ($k=0 \dots 23$).
  3. **Experimental Unit Count:** $N=173$ complete 24-hour origin replays remains the authoritative, pre-registered experimental unit count.
* **Verification Finding:** **`ORIGIN_SPACING_IMPACT: NONE`**

---

## 6. PRECISION CORRECTION & CONTRACT AUDIT

* **Proposed Fix in `system/forecasting/implementations/s81_solar.py` (Line 98):**
  Update `validate_stage81_solar_metadata` to compare `expected_gen` rounded to 2 decimal places:
  ```python
  expected_gen = round(min(expected_raw, 60000.0), 2)
  if abs(gen_p - expected_gen) > 1e-4:
      raise ValueError(...)
  ```
* **Contract Analysis:**
  * `solar_irradiance`: Ingests exact raw high-precision floats from CSV (unrounded, e.g. `12.744275635189387 W/m^2`).
  * `solar_generation`: $P = \min(SW_{\text{IN}} \times 51.0, 60000.0)$ rounded to 2 decimal places for power in Watts.
  * Schema Version: `ForecastBundle` v1.0.0 unchanged.
  * Interval Semantics: Degenerate point representation ($lower = point = upper$) unchanged.
* **Verification Finding:** **`PRECISION_FIX_CONTRACT_STATUS: CONTRACT-PRESERVING`**

---

## 7. GOVERNANCE IMPACT & AMENDMENT AUDIT

* **Governance Amendment Required:** **`NO`**
* **Authorization Status:** The proposed replay architecture correction aligns 100% with the existing frozen authorization artifact `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXPERIMENT_AUTHORIZATION.md`.
* **Implementation Authorization:** **`YES`** (Code changes to `s81_solar.py` and `run_polaris_stage8_1_ems_empirical_replay.py` are authorized for a dedicated harness update step).
* **Experiment Execution Authorization:** **`NO`** (Execution remains locked until the harness update is complete and verified).

---

## 8. FINAL EXPERIMENTAL CLAIM

* **Authorized Scientific Question:**  
  > *"Under an identical controlled POLARIS station environment, what downstream EMS operational differences are associated with replacing the control forecast with the frozen empirical Stage8.1 solar forecast, while the realized future solar trajectory and all other non-forecast conditions remain identical?"*
* **Mandatory Framing:**  
  > *"Empirical Stage8.1 solar forecasts replayed through the frozen POLARIS EMS under the controlled POLARIS synthetic station environment."*
* **Verification Finding:** **`PASS`**. The corrected architecture preserves the full scientific validity and claim boundaries of the authorized experiment.

---

## MANDATORY FINAL DECISION BLOCK

```yaml
AUTHORIZATION_COMPATIBILITY: PASS
COMMON_BASELINE_CONTINUATION_STATUS: AUTHORITATIVELY_IMPLIED
TEMPORAL_ALIGNMENT: PASS
HORIZON_SYMMETRY: PASS
TREATMENT_VALUE_PRECISION: PASS
ORIGIN_SPACING_IMPACT: NONE
PRECISION_FIX_CONTRACT_STATUS: CONTRACT-PRESERVING
GOVERNANCE_AMENDMENT_REQUIRED: NO
IMPLEMENTATION_AUTHORIZED: YES
EXPERIMENT_EXECUTION_AUTHORIZED: NO
REQUIRED_NEXT_STEP: EXECUTE_GOVERNED_CODE_CORRECTION_FOR_S81_SOLAR_AND_REPLAY_HARNESS
```
