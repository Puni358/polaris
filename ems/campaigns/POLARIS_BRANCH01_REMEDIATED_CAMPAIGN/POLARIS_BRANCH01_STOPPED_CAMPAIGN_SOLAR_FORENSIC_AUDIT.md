# POLARIS — Branch 01 Stopped Campaign Solar Receding-Horizon Forensic Audit

**Governance Gate**: Stopped Campaign Solar Receding-Horizon Forensic Audit  
**Date**: 2026-09-21  
**Mode**: **READ-ONLY FORENSIC ANALYSIS (NO RERUN / NO MODIFICATION)**  
**Campaign Directory**: `POLARIS_BRANCH01_REMEDIATED_CAMPAIGN/`  
**Completed Trajectories**: 14 / 173 (336 H1 steps)  
**Campaign Continuation Authorization**: **NOT_GRANTED**  
**Solar Receding-Horizon Status**: **SOLAR_RECEDING_HORIZON_DEFECT_CONFIRMED**  
**Non-Solar Forecast Inheritance Status**: **PASS**  
**Energy Accounting Status**: **PASS**  

---

### 1. FORENSIC ANOMALY DISCOVERY & MECHANISTIC ROOT CAUSE

An independent read-only forensic audit of the stopped campaign checkpoint (`POLARIS_BRANCH01_REMEDIATED_CAMPAIGN/CAMPAIGN_CHECKPOINT.json`) and campaign execution code (`scripts/run_polaris_branch01_remediated_campaign.py`) identified the **exact mechanistic root cause** of the static treatment solar forecast hash (`a4563d489ba318ccf17fca95c8a408c314de0c07253cac46c50b88dc24d01fe0`):

1. **Timestamp Normalization Mismatch in Campaign Script**:
   - In `scripts/run_polaris_branch01_remediated_campaign.py` lines 156–162:
     ```python
     curr_ts = norm_ts(state_t.timestamp)
     if curr_ts in obs_ts_map:
         obs_i = obs_ts_map[curr_ts]
         f_vec = FeatureMatrixBuilder.build_feature_vector(obs_df["SW_IN"], obs_df["timestamp"], obs_i, clearsky_df)
         rt_ctx_t["feature_vector"] = f_vec
     else:
         rt_ctx_t["feature_vector"] = [0.0] * 18
     ```
   - When `obs_df["timestamp"]` was loaded from `(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv` (line 101), `norm_ts("2024-01-23 00:00:00")` returned `"2024-01-23T00:00:00"` (without a trailing `'Z'`).
   - However, `state_t.timestamp` returned by `H10RuntimeAdapter` and `DigitalTwinSimulator` contained a trailing `'Z'`, e.g., `"2024-01-23T00:00:00Z"`.
   - Therefore, `curr_ts in obs_ts_map` evaluated to `False` on **every single MPC step** across all trajectories.

2. **Zero Feature Vector Fallback & Static Model Output**:
   - Because the dictionary lookup failed, the campaign runner executed the `else` branch:
     `rt_ctx_t["feature_vector"] = [0.0] * 18`
   - `Branch01ForecastEngine.predict()` evaluated the frozen HGB model (`POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1`) on `[0.0] * 18` at every step.
   - Deterministic model inference on `[0.0] * 18` produced the exact same 24-hour PV solar power point forecast vector, whose SHA-256 hash is `a4563d489ba318ccf17fca95c8a408c314de0c07253cac46c50b88dc24d01fe0`.

3. **Confirmation of Model Re-Invocation**:
   - The model was NOT cached or skipped. It was re-invoked 24 times per trajectory (336 total invocations across the 14 completed trajectories).
   - The static hash was caused purely by identical input features (`[0.0] * 18`) resulting from the timestamp key format mismatch.

---

### 2. EXACT HASH SEMANTICS & SOURCE CODE MAPPING

- **Hashed Object**: `hashlib.sha256(json.dumps(bundle.solar_generation.point).encode()).hexdigest()`
- **Source Location**: `scripts/run_polaris_branch01_remediated_campaign.py` lines 209–214.
- **Representation**: SHA-256 hash of the complete 24-hour solar PV power point forecast array `[P_0, P_1, ..., P_23]` (unit W).

---

### 3. TWENTY-POINT FAILURE MODE CLASSIFICATION MATRIX

| ID | Potential Failure Mode | Audit Classification | Forensic Empirical Evidence |
|---|---|---|---|
| 1 | Treatment forecast generated once per trajectory | **PASS** | Model invoked 24 times per trajectory inside MPC loop |
| 2 | Treatment forecast cached accidentally | **PASS** | No caching in `Branch01ForecastEngine.predict()` |
| 3 | Fixed forecast_origin passed to invocation | **PASS** | `origin_timestamp` updated correctly to `state_t.timestamp` |
| 4 | Runtime context not updated between cycles | **DEFECT** | `feature_vector` lookup failed due to `norm_ts` 'Z' mismatch |
| 5 | First-cycle prediction reused for all cycles | **PASS** | Re-computed at every step (on zero feature vector) |
| 6 | Prediction vector stored outside MPC loop | **PASS** | Constructed inside MPC loop |
| 7 | ForecastBundle created outside MPC loop | **PASS** | Instantiated inside MPC loop |
| 8 | Optimizer receiving stale ForecastBundle | **PASS** | Optimizer receives new bundle instance each step |
| 9 | Incorrect horizon slicing | **PASS** | Horizon is 24 hours |
| 10 | Incorrect list/reference aliasing | **PASS** | No shared mutable list references |
| 11 | Hash calculated from a stale object | **PASS** | Hash calculated from current step `bundle_t` |
| 12 | Hash calculated from only the first forecast | **PASS** | Hash calculated over entire 24-element point list |
| 13 | Serialization/rounding causing false hash equality | **PASS** | Serialization standard `json.dumps()` |
| 14 | Legitimate identical predictions from identical inputs | **DEFECT** | Feature inputs were identically `[0.0]*18` due to key miss |
| 15 | Hidden clear-sky fallback | **PASS** | No clear-sky fallback used in Treatment |
| 16 | Zero/default fallback | **DEFECT** | Campaign script fell back to `[0.0]*18` zero vector |
| 17 | Future-truth access | **NONE (PASS)** | Zero ground-truth advection/leakage |
| 18 | Control forecast injected into treatment solar | **PASS** | Treatment solar computed independently from model |
| 19 | Treatment forecast injected into control solar | **PASS** | Control solar computed from Stage 8.1 adapter |
| 20 | Non-solar forecast regeneration | **PASS** | Non-solar demand/wind inherited 100% directly |

---

### 4. NON-SOLAR FORECAST INHERITANCE VERIFICATION

- **Total Provenance Rows Audited**: 336 / 336
- **Demand Vector Mismatches**: 0 (0.0%)
- **Wind Vector Mismatches**: 0 (0.0%)
- **Demand Hash Equality Count**: 336 / 336 (100.0%)
- **Wind Hash Equality Count**: 336 / 336 (100.0%)
- **Status**: `NON_SOLAR_INHERITANCE_STATUS = PASS`

---

### 5. READ-ONLY ENERGY ACCOUNTING SUMMARY (14 COMPLETED TRAJECTORIES)

| Metric | Control (Stage 8.1 GHI) | Treatment (Branch01 HGB) | Audit Status |
|---|---|---|---|
| **Completed Trajectories** | 14 | 14 | Preserved intact |
| **Completed H1 Steps** | 336 | 336 | Preserved intact |
| **Total Actual Demand** | 12,096.000 kWh | 12,096.000 kWh | Ground Truth |
| **Total Diesel Generation** | 8,438.450 kWh | 11,811.200 kWh | Measured |
| **Total Fuel Consumption** | 1,840.400 L | 2,752.800 L | Measured |
| **Total Load Served** | 8,784.120 kWh | 11,811.200 kWh | Physical Delivery |
| **Total Unmet Load** | 3,311.880 kWh | 284.800 kWh | Physical Unmet |
| **Energy Residual** | 0.000 kWh | 0.000 kWh | **ENERGY_ACCOUNTING = PASS** |

---

### 6. MANDATORY FINAL SYSTEM STATUS

```
CAMPAIGN_CONTINUATION_AUTHORIZATION = NOT_GRANTED
FORENSIC_AUDIT_STATUS = COMPLETE
SOLAR_RECEDING_HORIZON_STATUS = SOLAR_RECEDING_HORIZON_DEFECT_CONFIRMED
NON_SOLAR_INHERITANCE_STATUS = PASS
ENERGY_ACCOUNTING_STATUS = PASS
NEXT_GOVERNED_STEP = GOVERNANCE_REMEDIATION_AUTHORIZATION_REVIEW
```
