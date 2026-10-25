# POLARIS L2 Uncertainty-Aware Forecasting — Feasibility & Design Audit

**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Date**: October 4, 2026  
**Status**: FEASIBILITY AUDIT COMPLETE — GO (RESEARCH-ONLY DESIGN PHASE)  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.36207412° N, 18.73875158° E`)  
**Strict Scope Compliance**: FEASIBILITY AUDIT ONLY. No neural network was trained, no candidate model created, no new experiments run, no historical replays rerun, and no modifications made to Candidate F, Stage 8.1, GAP19, production code, or frozen artifacts.

---

## 1. Executive Conclusion

The feasibility audit confirms that **it is scientifically and operationally legitimate to build a calibrated uncertainty-quantification model (L2) on top of frozen Candidate F using the existing historical F residual dataset**. 

Key findings supporting this conclusion:
1. **Target Defensibility**: Predicting conditional quantiles ($q_{0.10}, q_{0.50}, q_{0.90}$) of solar irradiance / residual via Pinball loss (or Conformalized Quantile Regression) is vastly superior and more defensible than directly predicting a standard deviation $\sigma$. Solar irradiance errors at Mount Nuolja are non-Gaussian, strictly bounded from below by $0\text{ W/m}^2$, bounded above by clear-sky geometry, and heavily skewed by cloud regimes.
2. **Causal Residual History**: The established residual persistence signal ($r = 0.4641$, $p = 3.43 \times 10^{-66}$, $R^2 = 21.54\%$) across 1,220 consecutive daily forecast origins can be accessed **strictly causally** by ingesting lag-1 completed origin daytime error statistics ($\bar{R}_{n-1}$, $\overline{|R|}_{n-1}$) without any intraday or lookahead leakage.
3. **Point Forecast Anchor**: Unlike Candidate K, which directly shifted the point forecast and caused severe 2024 EMS battery-dispatch mismatch, L2 retains frozen Candidate F as an untouched point forecast anchor and only quantifies the conditional uncertainty around it.
4. **Data Sufficiency & Clean Splits**: The 2020–2023 dataset (26,011 rows across 1,369 forecast origins) provides sufficient statistical support for a low-capacity uncertainty model across horizons and weather regimes, while preserving the proven temporal split: **TRAIN (2020–2021)**, **VALIDATION (2022)**, and **BLIND (Jan–Sep 2023)**. Calendar year 2024 remains untouched for future out-of-sample operational testing.

**Final Feasibility Verdict**: **GO for minimal first experiment design (research-only)** under strict calibration gates and governance locks.

---

## 2. Evidence Categorization: VERIFIED, INFERRED, UNKNOWN

### A. VERIFIED (Empirically Proven by Authoritative Artifacts)
- **Candidate F Integrity**: Candidate F GBDT model (`candidateF_elevation_x_cloud.joblib`, SHA256: `e8b89b27...`) produces 26,011 valid predictions across 2020–2023 with $0\text{ NaNs}$, $0\text{ Infs}$, overall MAE of $45.53\text{ W/m}^2$, daytime MAE of $74.02\text{ W/m}^2$, and bias of $+17.45\text{ W/m}^2$.
- **Residual Dataset Provenance**: `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` (SHA256: `1337a568...`) contains 26,011 rows across 1,369 origins, paired with authoritative SITES Nuolja AWS observations, with verified temporal causality (MEPS initialized at $t_{\text{init}} = t_0 - 6\text{h}$, context ending at $t_0 - 1\text{h}$).
- **Residual Temporal Persistence**: Testing residual correlation across 1,220 consecutive daily forecast origins yields Pearson $r = 0.4641$ ($p = 3.43 \times 10^{-66}$), Spearman $\rho = 0.4969$, and linear fit $R^2 = 21.54\%$.
- **Candidate K Degradation Mechanism**: Ablation forensics (`TERMINAL_RESERVE_ABLATION_REPORT.md` and `K_F_DISPATCH_INTERACTION_FORENSICS_RESERVE_OFF.md`) proved that Candidate K's EMS degradation in 2024 was caused by day-to-day point forecast volatility altering battery dispatch ($r = -0.657$ vs realized discharge delta), and that terminal reserve was **not** the dominant mechanism (double-difference 95% CI $[-119.35, +41.58]\text{ Wh/origin}$ includes zero).
- **Optimization Authority**: GAP19 remains the sole decision authority; L2 cannot directly alter optimizer dispatch decisions.

### B. INFERRED (Scientifically Grounded Deductions)
- **Quantile over Gaussianity**: Because solar irradiance errors are zero-bounded at night, clear-sky capped during the day, and multimodal under broken clouds, symmetric Gaussian or variance-only uncertainty ($\pm k\sigma$) will produce unphysical negative irradiance intervals or severely uncalibrated risk bounds. Asymmetric quantile intervals ($q_{10}, q_{50}, q_{90}$) naturally adapt to these physical limits.
- **Uncertainty vs Shift**: While using residual persistence to shift point forecasts (Candidate K) destabilized battery scheduling, using residual persistence and recent error variance to widen or narrow uncertainty bounds provides risk awareness without inducing volatile dispatch plan shifts.
- **Model Capacity Limit**: Given 13,889 training rows, a high-capacity deep neural network would overfit; a compact 2-layer MLP (e.g., 32–64 hidden units) or Quantile GBDT is the appropriate capacity regime.

### C. UNKNOWN (Requires Experimental Quantification)
- **Empirical Coverage of L2**: The exact out-of-sample coverage of an L2 quantile network across Mount Nuolja solar regimes has not yet been measured.
- **Horizon Calibration Degradation**: The extent to which uncertainty calibration degrades at longer horizons ($h \in [18..24]$) in this subarctic complex-terrain environment.
- **Conformal Correction Necessity**: Whether raw pinball loss quantiles are sufficiently well-calibrated or whether Split Conformalized Quantile Regression (CQR) on 2022 validation is required to guarantee nominal coverage.
- **GAP19 Mathematical Interface**: The precise mathematical formulation (e.g., chance constraint, risk-adjusted net load, or penalty term) by which GAP19 will eventually ingest validated L2 intervals remains to be designed in a future stage.

---

## 3. Audit Question 1: Valid Uncertainty Targets

### Target Options Evaluated
1. **Direct Standard Deviation Prediction ($\hat{\sigma}$ or $\hat{\sigma}^2$)**:
   - *Mechanism*: Model outputs error variance $\sigma^2(t)$ using Gaussian negative log-likelihood (heteroscedastic regression) or targets squared residuals $(y_t - \hat{y}_{F, t})^2$.
   - *Audit Verdict*: **REJECTED AS INFERIOR / INDEFENSIBLE**.
   - *Rationale*:
     - Assumes error distribution is Gaussian or symmetric.
     - Solar irradiance is strictly non-negative ($SW_{IN} \ge 0$) and physically bounded by clear-sky geometry ($SW_{IN} \le GHI_{\text{clearsky}} \times 1.25$).
     - At low sun elevations or overcast regimes, errors are heavily skewed. Under broken cloud fields, errors are heavy-tailed and bimodal.
     - Direct $\sigma$ prediction yields symmetric intervals $[\hat{y}_F - 1.28\sigma, \hat{y}_F + 1.28\sigma]$ that frequently penetrate below zero or exceed clear-sky maximums.

2. **Quantile / Prediction Interval Target ($q_{\tau}$ with $\tau \in \{0.10, 0.50, 0.90\}$)**:
   - *Mechanism*: Model outputs conditional quantiles directly using the tilted absolute loss (Pinball loss):
     $$\mathcal{L}_{\tau}(y, \hat{q}_{\tau}) = \max(\tau(y - \hat{q}_{\tau}), (\tau - 1)(y - \hat{q}_{\tau}))$$
   - *Audit Verdict*: **RECOMMENDED AS DEFENSIVE AND SOUND**.
   - *Rationale*:
     - Non-parametric: makes zero distributional assumptions.
     - Naturally captures skewness, heteroscedasticity, and asymmetric risks (e.g., probability of severe solar drop vs clear-sky peak).
     - Directly supplies nominal coverage intervals (e.g., 80% prediction interval $[\hat{q}_{0.10}, \hat{q}_{0.90}]$ and median $\hat{q}_{0.50}$).
     - Directly maps to downstream chance-constrained reserve formulations in EMS (e.g., ensuring solar availability with $90\%$ confidence: $P(SW_{IN} \ge \hat{q}_{0.10}) \ge 0.90$).

### Recommended Target Formulation
- **Target Variable**: Conditional quantiles of authoritative actual solar irradiance $SW_{IN}$ (column `actual` in the residual dataset), anchored to frozen Candidate F prediction $\hat{y}_F$ (column `prediction`).
- **Network Parametrization**: The network predicts quantile residual offsets $\boldsymbol{\delta q} = [\delta q_{0.10}, \delta q_{0.50}, \delta q_{0.90}]$ such that:
  $$\hat{q}_{\tau} = \max(0.0, \min(GHI_{\text{clearsky\_adj}}, \hat{y}_F + \delta q_{\tau}))$$
  with non-crossing ordering $\delta q_{0.10} \le \delta q_{0.50} \le \delta q_{0.90}$.

---

## 4. Audit Question 2: Causal Feature Availability

All candidate features from the 38-feature matrix and residual dataset were audited against the exact forecast issuance timestamp $t_0$ (MEPS 18Z initialization $t_{\text{init}} = t_0 - 6\text{h}$; issuance at $t_0$; target valid times $t \in [t_0, t_0 + 24\text{h}]$).

### A. Valid Forecast-Time Features (Genuinely Available at Issuance)
1. **Candidate F Point Forecast**: `prediction` ($\hat{y}_F$) — generated deterministically by frozen Candidate F at $t_0$.
2. **Astronomical & Geometric Context**:
   - `solar_elevation`: Perfectly deterministic astronomical angle for target time $t$.
   - `solar_zenith`: Deterministic astronomical zenith angle.
   - `clearsky_ghi`, `clearsky_ghi_terrain_adjusted`: Deterministic clear-sky irradiance at target time $t$.
   - `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`: Static terrain topography mask.
3. **Temporal Metadata**:
   - `horizon_hour`: Forecast lead time $h \in [1..24]$ (or $[6..29]$ relative to MEPS run).
   - `month`, `hour`, `day_of_year`: Calendar/time coordinates.
4. **MEPS NWP Forecast Features (Initialized at $t_0 - 6\text{h}$, valid for target time $t$)**:
   - `fc_cloud_cover`, `cloud_frac`: NWP cloud fraction forecast.
   - `fc_temperature_2m`: NWP 2m temperature forecast.
   - `fc_relative_humidity_2m`: NWP 2m relative humidity forecast.
   - `u700`, `v700`: NWP 700 hPa wind vector components.
   - `lwp_latest`, `iwp_latest`, `lwp_x_cloud`: NWP cloud water path fields.
   - `elevation_x_cloud_frac`: Solar elevation $\times$ cloud fraction interaction.
5. **Upstream Model Stage Outputs**:
   - `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`: Upstream pipeline signals computed at or before $t_0$.
6. **Station Telemetry Context (Ending strictly at $t_0 - 1\text{h}$)**:
   - `ctx_last_obs`: SITES Nuolja observation at $t_0 - 1\text{h}$.
   - `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`: Standard deviations over past context windows $[t_0 - K\text{h}, t_0 - 1\text{h}]$.
   - `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`: Ramp metrics ending at $t_0 - 1\text{h}$.
   - `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`: Historical context ending at $t_0 - 1\text{h}$.
   - `ctx_mean_24h`, `ctx_max_24h`: Historical 24h context summary ending at $t_0 - 1\text{h}$.

### B. Features Containing Future / Realized Information (MUST BE EXCLUDED)
1. **Target Realizations at Target Time $t > t_0$**:
   - `actual_SW_IN` / `actual`: Mount Nuolja ground pyranometer measurement at future target hour $t$.
   - `residual`: $SW_{IN}(t) - \hat{y}_F(t)$.
   - `forecast_error`: $\hat{y}_F(t) - SW_{IN}(t)$.
   - `absolute_error`: $|SW_{IN}(t) - \hat{y}_F(t)|$.
   - `squared_error`: $(SW_{IN}(t) - \hat{y}_F(t))^2$.
2. **Intraday Future Realizations**:
   - Any ground station measurement occurring during the forecast execution horizon $t \in [t_0, t_0 + 24\text{h}]$.

### C. Features with Uncertain Operational Availability
- **Live Station Telemetry (`ctx_*`) in Real-Time Operations**:
  - In the historical dataset, `ctx_*` features are 100% complete and causally verified.
  - In real-time field operations, satellite/cellular telemetry from Mount Nuolja (702 m a.s.l. Arctic terrain) may suffer occasional transmission dropouts or latency $> 1\text{h}$.
  - *Recommendation*: While valid for historical research modeling, L2 design must verify robustness to missing telemetry or define a fallback mode.

### D. Features That Must Be Excluded from Model Inputs
- All target columns (`actual`, `residual`, `forecast_error`, `absolute_error`, `squared_error`).
- `split`: Dataset index partition label.
- Non-causal identifiers or future origin indices.

---

## 5. Audit Question 3: Residual-History Feasibility

### Assessment of Established Persistence Finding ($r = 0.4641, R^2 = 21.54\%$)
The historical replay forensic audit established a statistically significant lag-1 correlation between consecutive daily forecast origins:
- $1,220$ consecutive daily origin pairs (24h origin step).
- Pearson $r = 0.4641$ ($p = 3.43 \times 10^{-66}$).
- Linear regression: $\text{Next\_Origin\_Residual} = -11.74 + 0.4646 \cdot \text{Prev\_Origin\_Residual}$.

### Can This Signal Be Legitimately Used by L2?
**YES, under strict causal isolation:**
- At forecast origin $n$ (issuance timestamp $t_0^{(n)}$), origin $n-1$'s 24-hour horizon ($[t_0^{(n-1)}, t_0^{(n-1)} + 24\text{h}]$) has completely concluded ($t_0^{(n-1)} + 24\text{h} \le t_0^{(n)}$).
- All actual observations and residuals from origin $n-1$ are fully historical and strictly in the past.
- Therefore, summary metrics of origin $n-1$ residuals can be computed causally at $t_0^{(n)}$ without lookahead leakage.

### Causal Residual-History Features Constructible Without Leakage
1. **Lag-1 Completed Origin Mean Daytime Residual ($\bar{R}_{n-1}$)**:
   $$\bar{R}_{n-1} = \frac{1}{|T_{\text{day}, n-1}|} \sum_{t \in T_{\text{day}, n-1}} (SW_{IN}(t) - \hat{y}_F(t))$$
   Captures whether Candidate F was systematically over-predicting or under-predicting during the immediately preceding day.
2. **Lag-1 Completed Origin Daytime Mean Absolute Error ($\overline{|R|}_{n-1}$)**:
   $$\overline{|R|}_{n-1} = \frac{1}{|T_{\text{day}, n-1}|} \sum_{t \in T_{\text{day}, n-1}} |SW_{IN}(t) - \hat{y}_F(t)|$$
   Provides an explicit scalar measure of recent forecast error magnitude/volatility.
3. **Causal Multi-Day EWMA of Error Volatility ($S_{n-1}$)**:
   Exponential moving average of past origin MAEs, reflecting whether the local synoptic weather regime is in a persistent high-volatility or low-volatility state.

### Contrast with Candidate K's Failure Mode
- **Candidate K**: Ingested residual persistence to modify the point forecast: $\hat{y}_K = \hat{y}_F + c$. In 2024, origin-to-origin volatility in $c$ caused large swings in late-window solar forecasts, leading the optimizer to discharge the battery prematurely and run out of reserve ($+516.6\text{ Wh/origin}$ unmet load).
- **L2 Uncertainty Model**: Candidate F point forecast $\hat{y}_F$ is **NEVER modified**. Residual history is ingested exclusively to modulate the uncertainty interval $[\hat{q}_{10}, \hat{q}_{90}]$ around $\hat{y}_F$.

---

## 6. Audit Question 4: Temporal Splitting

### Historical Partition Structure (2020–2023)
The authoritative historical dataset is structured into three strictly sequential partitions:
1. **TRAIN (2020–2021)**:
   - Calendar range: January 1, 2020 00:00 UTC to December 31, 2021 23:00 UTC (731 calendar days).
   - Rows: 13,889.
   - Origins: 730 daily forecast origins.
2. **VALIDATION (2022)**:
   - Calendar range: January 1, 2022 00:00 UTC to December 31, 2022 23:00 UTC (365 calendar days).
   - Rows: 6,935.
   - Origins: 365 daily forecast origins.
3. **BLIND TEST (Jan–Sep 2023)**:
   - Calendar range: January 1, 2023 00:00 UTC to September 30, 2023 23:00 UTC (273 calendar days).
   - Rows: 5,187.
   - Origins: 274 daily forecast origins.

### Reusability Verdict: REUSE AS-IS
- **Strict Temporal Ordering**: Preserves natural time direction (2020–2021 $\rightarrow$ 2022 $\rightarrow$ 2023). Zero shuffle or random splitting.
- **Cross-Candidate Parity**: Candidate F and Candidate K were tuned on 2022 and evaluated blindly on Jan–Sep 2023. Reusing this exact split ensures direct comparability.
- **Conformal Calibration Protocol**:
  - Model weights trained strictly on **TRAIN (2020–2021)**.
  - Hyperparameter tuning and Conformal Calibration (non-conformity score distribution) conducted strictly on **VALIDATION (2022)**.
  - Held-out verification conducted strictly once on **BLIND TEST (2023)**.

### Policy on Calendar Year 2024: DO NOT TOUCH
- Year 2024 contains the operational EMS replay dataset used in the Candidate K forensics.
- Touching 2024 during L2 model design, feature selection, training, or calibration is **STRICTLY PROHIBITED**.
- Year 2024 must remain fully quarantined for future out-of-sample operational dispatch evaluation.

---

## 7. Audit Question 5: Calibration Requirements

An uncertainty forecast cannot be evaluated by MAE or RMSE. Before any uncertainty signal could be considered for downstream GAP19 coupling, it must pass a formal **Multi-Pillar Out-of-Sample Calibration Gate**.

### Pillar 1: Empirical Coverage Gate
- For nominal coverage $(1 - \alpha) = 80\%$ (target interval $[\hat{q}_{0.10}, \hat{q}_{0.90}]$):
  $$\hat{C}_{80} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(y_i \in [\hat{q}_{0.10, i}, \hat{q}_{0.90, i}])$$
  - **Proposed Research Gate**: Empirical coverage on Validation (2022) and Blind (2023) must satisfy:
    $$78.0\% \le \hat{C}_{80} \le 84.0\%$$
    Under-coverage is strictly bounded ($\le 2\%$ below nominal), preventing dangerous overconfidence.
- For nominal coverage $(1 - \alpha) = 90\%$ (target interval $[\hat{q}_{0.05}, \hat{q}_{0.95}]$):
  - **Proposed Research Gate**: $88.0\% \le \hat{C}_{90} \le 93.0\%$.

### Pillar 2: Sharpness (Interval Width) Gate
- High coverage achieved by trivially wide intervals ($[0, GHI_{\text{clearsky}}]$) is useless for EMS optimization.
- **Metrics**:
  - Mean Prediction Interval Width (MPIW): $\frac{1}{N} \sum_{i=1}^N (\hat{q}_{0.90, i} - \hat{q}_{0.10, i})$.
  - Winkler Score / Interval Score:
    $$S_{\alpha}(l, u, y) = (u - l) + \frac{2}{\alpha}(l - y)\mathbb{I}(y < l) + \frac{2}{\alpha}(y - u)\mathbb{I}(y > u)$$
  - **Proposed Research Gate**: L2 interval score on daytime hours must achieve at least a **$10\%$ improvement** over a naive climatological empirical quantile baseline derived from 2020–2021 training residuals.

### Pillar 3: Calibration by Forecast Horizon Gate
- Solar uncertainty naturally grows with lead time ($h=1$ to $h=24$).
- The model must not compensate for severe near-horizon under-coverage with far-horizon over-conservatism.
- **Proposed Research Gate**: In each 6-hour lead-time block ($h \in [1..6], [7..12], [13..18], [19..24]$), daytime empirical coverage $\hat{C}_{80}$ must not fall below **$75.0\%$**.

### Pillar 4: Calibration by Solar & Cloud Regime Gate
- Mount Nuolja exhibits extreme regime-dependent error structures:
  - **Night ($\theta \le 0^\circ$)**: Deterministic zero. Interval width must strictly collapse to $0.0\text{ W/m}^2$; coverage must be $100.0\%$.
  - **Clear Sky ($c_f < 0.2$)**: Low variance. Empirical coverage must satisfy $76.0\% \le \hat{C}_{80} \le 86.0\%$.
  - **Overcast ($c_f > 0.8$)**: Moderate variance, persistent bias. Empirical coverage must satisfy $76.0\% \le \hat{C}_{80} \le 86.0\%$.
  - **Partial / Broken Cloud ($0.2 \le c_f \le 0.8$)**: Maximum variance. Empirical coverage must satisfy $74.0\% \le \hat{C}_{80} \le 86.0\%$.

### Pillar 5: Mandatory Blind-Set Verification
- Passing on 2022 validation is a necessary screening filter, but **blind-set performance on 2023 is mandatory**.
- A candidate model that passes 2022 validation but experiences coverage collapse ($< 75\%$) or extreme width expansion on 2023 Blind Test is automatically **FAILED**.

---

## 8. Audit Question 6: Data Sufficiency

### Sample Size Breakdown
- Total available rows: **26,011** across **1,369 origins**.
- Partition allocation:
  - **TRAIN (2020–2021)**: 13,889 rows (9,052 daytime rows, 4,837 night rows).
  - **VALIDATION (2022)**: 6,935 rows (4,528 daytime rows, 2,407 night rows).
  - **BLIND (2023)**: 5,187 rows (3,466 daytime rows, 1,721 night rows).

### Component-by-Component Sufficiency Assessment
1. **First Low-Capacity NN Uncertainty Model**:
   - *Status*: **SUFFICIENT**.
   - *Rationale*: A compact MLP with 1 or 2 hidden layers (32 to 64 units) has $\approx 1,500$ to $3,500$ parameters. A training set of 9,052 active daytime samples yields a parameter-to-sample ratio $> 2.5:1$, well within standard generalization bounds for regularized neural architectures.
2. **Horizon-Specific Uncertainty ($h \in [1..24]$)**:
   - *Status*: **SUFFICIENT**.
   - *Rationale*: In the training set, each individual lead hour $h \in [1..24]$ has $\approx 578$ total observations and $\approx 377$ daytime observations. Because the model conditions continuously on `horizon_hour` (rather than fitting 24 isolated disjoint models), cross-horizon weight sharing provides robust generalization.
3. **Regime-Conditioned Uncertainty**:
   - *Status*: **SUFFICIENT for Broad Regimes; INSUFFICIENT for Granular Discrete Slices**.
   - *Rationale*: Across the dataset, broad regimes are heavily populated (Clear: 7,321 rows; Partial: 7,125 rows; Overcast: 11,565 rows). However, granular intersectional bins (e.g., $h=18$ $\times$ Low Sun $\times$ Partial Cloud $\times$ High Wind) have fewer than 25 samples. The model must therefore learn a continuous representation rather than relying on discrete lookup tables.
4. **Residual-History Inputs**:
   - *Status*: **SUFFICIENT for Daily Origin Lag Features; INSUFFICIENT for Intraday Dynamic Updating**.
   - *Rationale*: There are 730 training origins with consecutive origin pairs (1,220 total pairs across 2020–2023). This is fully sufficient to learn the relationship between yesterday's daytime mean residual and today's uncertainty bounds. However, because forecasts are issued once daily for the full 24-hour cycle, intraday real-time residual updating ($h \rightarrow h+1$) is not supported by the existing operational format.

---

## 9. Audit Question 7: Leakage & Contamination Risks

A rigorous audit identified six distinct leakage and contamination risks that must be safeguarded against in L2 pipeline design:

| # | Risk Category | Specific Leakage Mechanism | Prevention & Enforcement Rule |
|---|---|---|---|
| 1 | **Target Leakage via Residuals** | Using contemporaneous residual $R(t)$ or actual $SW_{IN}(t)$ as model inputs. | Target columns (`actual`, `residual`, error metrics) are strictly isolated and barred from input tensors. |
| 2 | **Intraday Origin Leakage** | Using realized errors from early hours of origin $n$ (e.g., $h=1..3$) to predict uncertainty for later hours ($h=12..24$) of origin $n$. | In a day-ahead operational architecture, all 24 hours are issued simultaneously at $t_0$. Residual history must strictly originate from completed origin $n-1$ or earlier ($t \le t_0 - 1\text{h}$). |
| 3 | **Preprocessing Scaling Contamination** | Fitting input scalers (mean, std, min, max) on the entire 2020–2023 dataset or validation set. | Feature transformers (`StandardScaler`, `QuantileTransformer`) must be fit **strictly on TRAIN (2020–2021)** and applied frozen to Validation and Blind sets. |
| 4 | **Conformal Calibration Set Leakage** | Computing conformal non-conformity scores on the training set (yielding over-optimistic widths) or on the 2023 blind set. | Conformal calibration scores must be computed strictly on held-out **VALIDATION (2022)**. |
| 5 | **Blind-Set Peeking / Overfitting** | Tuning neural network hyperparameters, layer counts, or loss weights against the 2023 Blind Test set. | Blind 2023 data must be loaded **only once** for final frozen evaluation after all hyperparameters are locked. |
| 6 | **NWP Issuance Lookahead** | Ingesting NWP analysis fields rather than operational forecast runs. | Audited and verified: all MEPS features originate from 18Z operational runs initialized 6 hours prior to forecast start. |

---

## 10. Audit Question 8: Recommended First L2 Design Summary

The simplest, most defensible, and methodologically sound first experiment is a **Compact Quantile Regression Multi-Layer Perceptron (QR-MLP)** with Conformal Calibration:
- **Base Anchor**: Frozen Candidate F point forecast $\hat{y}_F$ (completely unaltered).
- **Network Task**: Predict conditional quantile offsets $\boldsymbol{\delta q} = [\delta q_{0.10}, \delta q_{0.50}, \delta q_{0.90}]$ relative to $\hat{y}_F$.
- **Inputs**: 12 selected causal features (point forecast, elevation, clearsky, NWP cloud, horizon, 3 key station context metrics, and 2 lag-1 completed origin residual stats).
- **Physical Bounding**: Strict post-processing clamping ensuring non-negativity ($SW_{IN} \ge 0$), clear-sky upper capping, and zero width at night.
- **Independence**: GAP19 remains completely untouched; the experiment operates strictly as an offline forecast-uncertainty benchmark.

*(See [`design/L2_FIRST_EXPERIMENT_DESIGN.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/design/L2_FIRST_EXPERIMENT_DESIGN.md) for full design contract.)*

---

## 11. Audit Question 9: Stop Conditions

The L2 research branch must be halted immediately without progressing to training or downstream integration if any of the following conditions are met:

1. **Failure to Beat Static Climatological Baseline**: If the L2 model on the 2022 validation set cannot achieve at least a $10\%$ improvement in Interval Score (Winkler Score) over a naive static empirical quantile baseline derived from historical residuals.
2. **Severe Empirical Under-Coverage ($< 75\%$)**: If the validation set coverage for nominal 80% intervals falls below $75.0\%$ in daytime hours or in any single 6-hour horizon block, indicating persistent overconfidence.
3. **Quantile Inversion / Instability**: If the unconstrained neural network suffers chronic quantile crossing ($\hat{q}_{0.90} < \hat{q}_{0.10}$) across $> 5\%$ of daytime predictions, demonstrating optimization failure.
4. **Candidate F Prediction Discrepancy**: If the predictions generated by `candidateF_elevation_x_cloud.joblib` differ by more than $10^{-5}\text{ W/m}^2$ from the authoritative frozen prediction file (`CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv`), indicating model corruption.
5. **Real-Time Context Telemetry Missingness**: If operational requirements reveal that station telemetry from Mount Nuolja is unavailable $> 20\%$ of the time at forecast issuance, rendering station-feedback features non-viable in field deployment.

---

## 12. Final Feasibility Decision

### **GO (PROCEED TO DESIGN & BENCHMARK EXPERIMENT SPECIFICATION)**

**Justification**:
1. The mathematical foundation (quantile regression on frozen residual distribution) is sound and resolves the structural failure of Candidate K.
2. All required data artifacts are frozen, verified, and free of target leakage.
3. The historical temporal persistence ($r = 0.4641$) provides a genuine, causally accessible physical signal for uncertainty quantification.
4. All governance locks remain intact: Candidate F is not modified, no candidate model is promoted, and GAP19 remains untouched.
