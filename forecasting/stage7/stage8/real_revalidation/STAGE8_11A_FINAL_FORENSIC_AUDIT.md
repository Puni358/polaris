# POLARIS STAGE 8.11A — FINAL FORENSIC AUDIT REPORT
**Target Decision**: `STAGE_8_11_ROUTE_NOT_NOVEL`  
**Official Champion**: Stage 8.1 700 hPa Steering Wind Model  
**Official Frozen ODD Daytime Metrics**:  
- MAE = 36.188657 W/m²  
- nMAE = 28.0688%  
- RMSE = 64.219495 W/m²  
- Bias = +1.439399 W/m²  
- Night MAE = 0.000000 W/m²  

---

## Executive Summary

This forensic audit independently verified whether the Stage 8.11A conclusion:
```
STAGE_8_11_ROUTE_NOT_NOVEL = CONFIRMED
```
is scientifically and technically correct.

After inspecting the actual feature extraction implementation in [`stage6/stage6_6_lwp_iwp/run_stage6_6.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage6/stage6_6_lwp_iwp/run_stage6_6.py), the underlying feature data in [`lwp_iwp_extracted_features.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv), and the feature ingestion pipeline in [`stage7/stage8/stage8_1_700hpa_wind/run_stage8_1.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_700hpa_wind/run_stage8_1.py), we conclude:

1. **Option B Confirmed**: `lwp_latest` and `iwp_latest` are **independently calculated at $t_0+h$ for each horizon hour $h \in \{1 \dots 24\}$**. The name `lwp_latest` is a historical artifact from Stage 6.6, but the data represents per-horizon forecast trajectories.
2. **Consumed by Stage 8.1**: The Stage 8.1 feature assembly code explicitly merges [`lwp_iwp_extracted_features.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv) on **both** `["forecast_start", "horizon_hour"]`. Each prediction row $H_h$ receives the exact corresponding horizon-$h$ MEPS LWP and IWP values.
3. **Exact Duplication**: Executing a new Stage 8.11 experiment to add per-horizon LWP/IWP trajectories would yield an **EXACT DUPLICATE** of feature information already ingested by the frozen Stage 8.1 champion (37 features).
4. **Decision**: `STAGE_8_11_ROUTE_NOT_NOVEL` is **100% CONFIRMED**, and `Stage 8.11B` is **NOT JUSTIFIED**.

---

## 1. Source-Time Semantics Audit

Line-by-line inspection of [`stage6/stage6_6_lwp_iwp/run_stage6_6.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage6/stage6_6_lwp_iwp/run_stage6_6.py#L211-L262):

```python
# Lines 211-262 of run_stage6_6.py:
for h_idx in range(24):
    h = h_idx + 1
    valid_time = origin_dt + pd.Timedelta(hours=h)
    
    p_sfc = surface_air_pressure_series[h_idx]
    q_l_profile = q_l_series[h_idx] # shape (13,)
    q_i_profile = q_i_series[h_idx] # shape (13,)
    
    lwp_sa, iwp_sa = compute_surface_aware_lwp_iwp(
        p_levels, q_l_profile, q_i_profile, p_sfc
    )
    
    rows.append({
        "origin_index": idx,
        "forecast_start": origin_str,
        "horizon_hour": h,
        "valid_time": valid_time.strftime("%Y-%m-%d %H:%M:%S%z"),
        "lwp_latest": round(float(lwp_sa), 6),
        "iwp_latest": round(float(iwp_sa), 6),
    })
```

### Verified Semantics:
- **`t0`**: Represents the forecast origin timestamp (00:00:00 UTC on day $D$).
- **`h_idx`**: Loop index from `0` to `23`, representing forecast horizon hour $h = \text{h\_idx} + 1 \in \{1 \dots 24\}$.
- **Timestamp / Valid Time**: `valid_time = origin_dt + pd.Timedelta(hours=h)` strictly equals $t_0 + h$.
- **Synchronous Retrieval**: `surface_air_pressure`, $q_l$ (liquid water content profile), and $q_i$ (ice water content profile) are all retrieved synchronously for the exact same forecast lead step $h$.
- **Independent Evaluation**: `compute_surface_aware_lwp_iwp()` is called independently for every horizon $h$.
- **Per-Horizon Storage**: Results are stored in separate rows indexed by `horizon_hour = h`.

---

## 2. Feature-Construction Semantics Classification

- **Option A**: One value calculated at $t_0$ and repeated across $H1 \dots H24$. (**FALSE**)
- **Option B**: Independently calculated at $t_0+h$ for each horizon. (**TRUE**)
- **Option C**: Other timestamp convention. (**FALSE**)

**Classification: OPTION B**.  
The feature name `lwp_latest` is a legacy identifier from Stage 6.6 ("latest" MEPS 18Z run available prior to 00Z), but the values contained in the column represent full **per-horizon forecast trajectories**.

---

## 3. Horizon Alignment Audit

POLARIS Horizon Convention:
- $H1 = t_0 + 01\text{h}$
- $\dots$
- $H24 = t_0 + 24\text{h}$

### Mapping Verification:
- `h_idx = 0` $\rightarrow$ `horizon_hour = 1` ($t_0 + 1\text{h}$, $H1$)
- `h_idx = 23` $\rightarrow$ `horizon_hour = 24` ($t_0 + 24\text{h}$, $H24$)
- Underlying MEPS valid time spans $t_0 + 1\text{h}$ through $t_0 + 24\text{h}$.
- **Zero hidden shift or off-by-one error**. Alignment is 1-to-1 with POLARIS prediction targets.

---

## 4. Causality Audit

- **MEPS Issuance**: $D-1$ 18:00:00 UTC.
- **Forecast Origin ($t_0$)**: Day $D$ 00:00:00 UTC.
- **Issuance Margin**: $t_{\text{issuance}} \le t_0$ (issued 6 hours prior to $t_0$).
- **Valid Forecast Lead Steps**: $+6\text{h}$ (for $H1$) to $+29\text{h}$ (for $H24$).
- **Causality Status**: Strictly causal. All MEPS data used were generated prior to $t_0$.

---

## 5. Data Artifact Verification (True EVEN-Origin Spot-Check)

We inspected [`lwp_iwp_extracted_features.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv) across 7 representative EVEN origins:

| Origin Index | `forecast_start` | $H1$ LWP (g/m²) | $H24$ LWP (g/m²) | $H1$ IWP (g/m²) | $H24$ IWP (g/m²) | Unique LWP Count | Unique IWP Count | Horizon Variation? |
|---|---|---|---|---|---|---|---|---|
| **0** | 2024-01-20 | 0.000000 | 1.382741 | 0.074906 | 8.240578 | 13 | 20 | **YES** |
| **2** | 2024-01-22 | 5.382813 | 0.869852 | 37.168788 | 0.003023 | 19 | 21 | **YES** |
| **4** | 2024-01-24 | 3.608826 | 0.000000 | 0.395063 | 0.005342 | 8 | 18 | **YES** |
| **10** | 2024-01-30 | 27.662536 | 0.989571 | 8.329922 | 0.424761 | 24 | 22 | **YES** |
| **20** | 2024-02-09 | 0.000000 | 0.000000 | 0.681874 | 0.106365 | 2 | 13 | **YES** |
| **50** | 2024-03-10 | 15.814143 | 4.751760 | 0.010536 | 0.000148 | 24 | 23 | **YES** |
| **100** | 2024-04-29 | 0.440654 | 1.848087 | 0.000006 | 0.211542 | 17 | 7 | **YES** |

All sampled origins exhibit significant non-constant variation across $H1 \dots H24$.

---

## 6. Stage 8.1 Feature Consumption Verification

We traced [`stage7/stage8/stage8_1_700hpa_wind/run_stage8_1.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_700hpa_wind/run_stage8_1.py#L263-L265):

```python
# Lines 263-265 of run_stage8_1.py:
stage66_cols = ["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]
df = df.merge(df_66[stage66_cols], on=["forecast_start", "horizon_hour"], how="left")
df["lwp_x_cloud"] = df["lwp_latest"] * df["cloud_frac"]
```

### Key Findings:
- The join key is `["forecast_start", "horizon_hour"]`.
- The merge is **not** performed on `forecast_start` alone.
- As a result, each horizon row $H_h$ receives the corresponding horizon-$h$ values `lwp_latest` and `iwp_latest`.
- The 37-feature Stage 8.1 model consumes `lwp_latest`, `iwp_latest`, and `lwp_x_cloud` per-horizon.

---

## 7. Duplication Test

- **Proposed Stage 8.11 Experiment**: Extract per-horizon MEPS LWP/IWP forecasts and add them to the model.
- **Stage 8.1 Current Pipeline**: Already extracts per-horizon MEPS LWP/IWP forecasts (`lwp_latest`, `iwp_latest`, `lwp_x_cloud`) and feeds them into the 37-feature GBDT model.
- **Classification**: **`EXACT DUPLICATE`**.

---

## 8. Audit of Previous Stage 8.11A Sample Audit Artifact

A comparison of [`STAGE8_11A_EVEN_ORIGIN_SAMPLE_AUDIT.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_11_lwp_iwp_semantics/STAGE8_11A_EVEN_ORIGIN_SAMPLE_AUDIT.csv) against ground-truth [`lwp_iwp_extracted_features.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv) revealed transcription/sampling discrepancies in the reported unique counts and boundary values for origins 0, 4, 10, 20, 50, and 100.

These corrections are formally documented in [`STAGE8_11A_EVIDENCE_CORRECTION_AUDIT.json`](file:///home/punith-bs/.gemini/antigravity/brain/e6fa6f7a-81f8-4245-944b-829ddd9246ff/STAGE8_11A_EVIDENCE_CORRECTION_AUDIT.json).

> [!NOTE]
> The qualitative conclusion remains entirely unaffected: all origins in the ground-truth feature CSV exhibit horizon-varying LWP/IWP values (Option B).

---

## 9. Final Decision Logic

1. Stage 6.6 computes LWP/IWP independently at $t_0+h$: **CONFIRMED**
2. $H1 \dots H24$ alignment is correct (zero shift): **CONFIRMED**
3. Source is causally available (D-1 18Z run): **CONFIRMED**
4. Extracted values genuinely enter frozen Stage 8.1 feature rows at corresponding horizons: **CONFIRMED**

### Final Verdict:
```
STAGE_8_11_ROUTE_NOT_NOVEL = CONFIRMED
Stage 8.11B = NOT JUSTIFIED
```

---

## 10. Scientific Boundary Statement

### What CAN be concluded:
- The proposed per-horizon MEPS LWP/IWP trajectory information is already present in the frozen Stage 8.1 feature pipeline.
- Running Stage 8.11B would be redundant.

### What CANNOT be concluded:
- Cloud evolution is physically irrelevant to solar irradiance forecasting.
- NWP cloud forecast errors are non-existent or solved.
- All cloud temporal dynamics are fully captured by gradient-boosted trees.
- Stage 8.11 proved cloud evolution is not the bottleneck.

---

## 11. Firewall Verification Report

- **ODD target SW_IN reads**: `0`
- **ODD predictions generated**: `0`
- **ODD metrics computed**: `0`
- **Model training**: `NONE`
- **Cross-validation**: `NONE`
- **Hyperparameter tuning**: `NONE`
- **Official champion status**: `UNCHANGED` (Stage 8.1 700 hPa Steering Wind Model)
- **POLARIS_MASTER_HANDOFF.md status**: `UNTOUCHED`
