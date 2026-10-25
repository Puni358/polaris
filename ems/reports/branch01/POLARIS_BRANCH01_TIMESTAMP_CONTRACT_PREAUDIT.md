# POLARIS — Branch 01 Timestamp Contract Pre-Correction Audit

**Date**: 2026-09-21  
**Phase**: **PHASE A — READ-ONLY PRE-CORRECTION AUDIT**  
**Target Component**: `scripts/run_polaris_branch01_remediated_campaign.py`  

---

### 1. Source Inspection Findings

- **A. Timestamp Normalization Function**:
  - File: `scripts/run_polaris_branch01_remediated_campaign.py` (lines 38–39)
  - Implementation:
    ```python
    def norm_ts(ts_str: str) -> str:
        return ts_str.strip().replace(" ", "T").replace("+00:00", "Z")
    ```
  - Defect: When converting space-separated string `"2024-01-23 00:00:00"`, `.replace("+00:00", "Z")` has no effect, producing `"2024-01-23T00:00:00"` without a trailing `'Z'`.

- **B. Source CSV Format**:
  - File: `(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv`
  - Format: `"2024-01-23 00:00:00"` (space separated, no timezone suffix).

- **C. Runtime StationState Timestamp Format**:
  - Provider: `H10RuntimeAdapter` & `DigitalTwinSimulator`
  - Format: `"2024-01-23T00:00:00Z"` (ISO-8601 with trailing `'Z'`).

- **D. Observation Map Construction**:
  - Line 110: `obs_ts_map = {ts: idx for idx, ts in enumerate(obs_df["timestamp"])}`
  - Resulting keys: `"2024-01-23T00:00:00"` (missing `'Z'`).

- **E. Feature Vector Lookup & Fallback**:
  - Lines 156–162:
    ```python
    curr_ts = norm_ts(state_t.timestamp)
    if curr_ts in obs_ts_map:
        obs_i = obs_ts_map[curr_ts]
        f_vec = FeatureMatrixBuilder.build_feature_vector(...)
        rt_ctx_t["feature_vector"] = f_vec
    else:
        rt_ctx_t["feature_vector"] = [0.0] * 18
    ```
  - `curr_ts` was `"2024-01-23T00:00:00Z"`, whereas keys in `obs_ts_map` were `"2024-01-23T00:00:00"`.
  - Lookup evaluated to `False` on **every single MPC step**.

---

### 2. Failure Mechanism Summary

The timestamp string mismatch forced every MPC cycle into the `else` block, injecting `[0.0] * 18` as the feature vector. The frozen HGB model was invoked 24 times per trajectory, but repeatedly on the identical zero vector, producing the static solar forecast hash `a4563d489ba318ccf17fca95c8a408c314de0c07253cac46c50b88dc24d01fe0`.

---

### 3. Canonical Remediation Target

1. Implement `canonicalize_ts(ts_str: str) -> str` to guarantee all timestamps formatted as `YYYY-MM-DDTHH:MM:SSZ`.
2. Remove the `[0.0] * 18` zero-vector fallback and raise an explicit `ModelGovernanceError` if timestamp lookup fails.
