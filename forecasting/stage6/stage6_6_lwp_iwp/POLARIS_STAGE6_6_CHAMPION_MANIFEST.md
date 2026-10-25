# POLARIS STAGE 6.6 CHAMPION MANIFEST

**Status:** OFFICIAL FROZEN OPERATIONAL CHAMPION  
**Date:** September 12, 2026  
**Target Station:** Nuolja ($68.355701^\circ\text{N}, 18.763666^\circ\text{E}$, Elev: $702\text{ m a.s.l.}$)  
**Champion ID:** `STAGE_6_6_LWP_IWP`  
**Audit Status:** `READ_ONLY_NUMERICAL_AUDIT_PASSED`  

---

## 1. AUTHORITATIVE ODD TEST METRICS

Evaluated under the **True Frozen Stage 5.2 Evaluation Pipeline** (`pred_stage4_full`) on all 173 held-out ODD test origins ($4,152$ total hours, $2,883$ daytime validation hours):

| Metric | Stage 5.2 Frozen Control | Stage 6.6 Champion | Absolute Delta ($\Delta$) | Relative Change |
| :--- | :---: | :---: | :---: | :---: |
| **Daytime MAE** | $39.084821\text{ W/m}^2$ | **$37.005888\text{ W/m}^2$** | **$-2.078933\text{ W/m}^2$** | **$-5.32\%$** |
| **Daytime nMAE** | $30.3151\%$ | **$28.7026\%$** | **$-1.6125\text{ pp}$** | **$-5.32\%$** |
| **Daytime RMSE** | $68.993487\text{ W/m}^2$ | **$65.671702\text{ W/m}^2$** | **$-3.321785\text{ W/m}^2$** | **$-4.81\%$** |
| **Daytime Bias $(\text{pred}-\text{actual})$** | $+1.934725\text{ W/m}^2$ | **$+1.144965\text{ W/m}^2$** | **$-0.789760\text{ W/m}^2$** | **$-40.82\%$** |
| **Night MAE** | $0.000000\text{ W/m}^2$ | $0.000000\text{ W/m}^2$ | $0.000000\text{ W/m}^2$ | $0.00\%$ |

---

## 2. STATISTICAL SIGNIFICANCE (10,000 BOOTSTRAP RESAMPLES)

* **Resampling Protocol:** $10,000$ paired origin-level bootstrap resamples ($N=173$ origins).
* **Random Seed:** 42
* **Mean Bootstrapped $\Delta\text{MAE}$:** **$-2.078277\text{ W/m}^2$**
* **95% Confidence Interval:** **$[-2.809838, -1.344760]\text{ W/m}^2$**
* **Fraction of Resamples $< 0$:** **$1.000000$** ($100.000\%$ of all 10,000 resamples confirm candidate superiority, $p < 0.0001$).

---

## 3. CHAMPION MODEL & HYPERPARAMETERS

```python
from sklearn.ensemble import HistGradientBoostingRegressor

champion_model = HistGradientBoostingRegressor(
    loss="absolute_error",
    max_depth=4,
    min_samples_leaf=30,
    l2_regularization=10.0,
    random_state=42
)
```

---

## 4. CHAMPION FEATURE SET (31 FEATURES TOTAL)

### New Cloud Microphysics Features (3 Features)
1. `lwp_latest`: Surface-aware integrated Liquid Water Path ($	ext{kg/m}^2$) derived via vertical pressure-level integration from MEPS 3D fields, truncated at MEPS surface pressure ($p_{	ext{sfc}} pprox 891.8..974.1	ext{ hPa}$).
2. `iwp_latest`: Surface-aware integrated Ice Water Path ($	ext{kg/m}^2$) derived via vertical pressure-level integration from MEPS 3D fields, truncated at MEPS surface pressure.
3. `lwp_x_cloud`: Interaction feature computed as `lwp_latest` $	imes$ `cloud_frac`.

### Baseline Stage 5.2 Features (28 Features)
* `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`
* Pre-forecast context features: `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`.

---

## 5. DATA SOURCES & LOCKED PROTOCOL

* **Observation Ground Truth:** SITES Nuolja 2024 hourly solar radiation ($obs\_SW\_IN$).
* **Clear-Sky Decomposition:** PVLIB Ineichen model ($clearsky\_ghi$, $solar\_elevation$, $solar\_zenith$, $kt$).
* **3D Cloud Condensate Fields:** MEPS OpenData 2.5km spatial grid (13 pressure levels: 50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000 hPa).
* **NWP Surface Weather:** Open-Meteo hourly forecast.
* **Locked Dataset Split:** 347 clean origins ($8,328$ forecast hours). EVEN origins ($174$ origins) = Train/CV. ODD origins ($173$ origins) = Held-out ODD Test Set.
* **Causal Night Rule:** Hard-forced to $0.0000	ext{ W/m}^2$ when $	ext{solar\_elevation} \le 0.0^\circ$ OR $	ext{clearsky\_ghi} == 0.0	ext{ W/m}^2$.

---

## 6. RESOLVED FORENSIC ISSUE RECORD

* **Issue:** In `run_official_odd_evaluation.py`, Stage 4 parameters ($w_h, k_h$) were dynamically refitted on EVEN data, producing an unanchored control baseline of $39.3927	ext{ W/m}^2$.
* **Resolution:** Audit confirmed that the globally frozen Stage 5.2 benchmark uses `pred_stage4_full` from `stage4_results/ensemble_predictions.csv`. Re-evaluating both control and candidate under the exact frozen Stage 5.2 pipeline reproduces the $39.084821	ext{ W/m}^2$ control baseline to 100.000% precision and yields the final authoritative candidate MAE of **$37.005888	ext{ W/m}^2$** ($\Delta	ext{MAE} = -2.078933	ext{ W/m}^2$).

---

## 7. ARTIFACT LOCATIONS

* `POLARIS_STAGE6_6_CHAMPION_MANIFEST.json` — Machine-readable manifest
* `POLARIS_STAGE6_6_CHAMPION_MANIFEST.md` — Formal markdown champion manifest
* `control_discrepancy_forensic_audit.json` — Detailed forensic audit of control reconstruction
* `lwp_iwp_extracted_features.csv` — Extracted surface-aware LWP/IWP features across 347 origins
* `odd_predictions_comparison.csv` — Row-level predictions for control vs candidate on ODD test set
* `odd_evaluation_results.json` — Authoritative ODD metrics and bootstrap results
* `gate_decision.json` — Pre-CV, EVEN CV gates, and ODD decision log
* `final_stage6_6_report.md` — Complete Stage 6.6 experiment report
* `POLARIS_MASTER_HANDOFF.md` — Updated master project handoff document
