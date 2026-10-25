# POLARIS Solar Forecasting Research Compendium
## Comprehensive Reference Manual of Forecasting Candidates, Architectures, Forensic Audits, and Operational Interfaces (Stages 1 through Candidate K)

> **Document Purpose**: This single master README serves as the exhaustive knowledge base and research memory for the POLARIS microgrid solar forecasting program. It contains the exact mathematical formulations, operational context, data split protocols, training procedures, forensic audit discoveries, empirical results, and failure analyses for every forecasting candidate tested to date. It is formatted so that an advanced AI research assistant (such as Gemini) can ingest the entire state of research, understand the physical and statistical constraints, and design novel, non-duplicative forecasting architectures.

---

## 1. Executive Context & Physical Microgrid Setting

### 1.1 The Operational Site: Mount Nuolja Automatic Weather Station (`ANS_NMS`)
- **Location**: Mount Nuolja ridge, Abisko National Park, Arctic Sweden ($68.362074^\circ\text{ N}$, $18.738752^\circ\text{ E}$, elevation $702.0\text{ m}$ a.s.l., UTC timezone).
- **Environment**: Extreme sub-arctic alpine environment characterized by:
  - **Polar Night**: Complete absence of extraterrestrial solar radiation for ~6 weeks in winter ($GHI_{\text{cs}} = 0$).
  - **Midnight Sun**: Continuous low-elevation daytime radiation during summer solstice.
  - **Severe Topographic Shading**: Surrounding mountain crests cast physical shadows that block direct solar beams even when astronomical elevation $> 0^\circ$.
  - **High-Albedo Snow-Cloud Interactions**: Snow-covered terrain reflects radiation back to cloud bases, distorting optical depth measurements.
  - **Fast Cloud Advection**: High-altitude Arctic winds ($700\text{ hPa}$) cause sudden occlusion and clearing cycles within 10–30 minutes.

### 1.2 Microgrid Architecture & Energy Management System (EMS)
The forecasting models generate a 24-hour day-ahead rolling forecast trajectory ($t+1 \dots t+24$, hourly resolution) initialized at daily dispatch cutoff ($t_0 = 00:00\text{ UTC}$).
The forecasts feed directly into a mixed-integer linear programming (MILP) dispatch solver (**HiGHS**), executing under the **GAP19** multi-objective lexicographic hierarchy:
1. **$J_1$ (Priority 1 - Safety Critical)**: Zero unmet critical electrical demand ($P_{\text{unmet}} = 0$).
2. **$J_2$ (Priority 2 - Operational Cost)**: Minimize diesel generator fuel consumption and start-stop cycling fatigue.
3. **$J_3$ (Priority 3 - Battery Longevity & Reserve)**: Maintain state of charge within degradation-safe limits and enforce dynamic Emergency Battery Reserve ($EBR$).
4. **$J_4$ (Priority 4 - Green Maximization)**: Minimize renewable energy curtailment.

### 1.3 Asymmetry of Operational Risk: Why Bias Matters More Than MAE
In conventional machine learning, Mean Absolute Error (MAE) or Root Mean Square Error (RMSE) is the primary loss function. In the POLARIS microgrid, **the sign of the error is existential**:
- **Forecast Overprediction ($e_t = \hat{y}_t - y_t > 0$)**: The model predicts solar generation that does not materialize. The optimizer plans on solar charging, keeps the diesel generator off, and depletes the battery. When the sun fails to appear, the battery hits low-voltage cutoff, resulting in catastrophic critical load loss or emergency diesel scram. Forensic audit (`STAGE81_UNMET_DECOMPOSITION_REPORT.md`) confirmed that **100% of realized unmet load hours coincide with forecast overprediction**.
- **Forecast Underprediction ($e_t = \hat{y}_t - y_t < 0$)**: The model predicts less solar than arrives. The optimizer schedules conservative diesel dispatch. Realized solar charges the battery; excess power is curtailed ($J_4$ penalty). **No blackout occurs.**
- **The Core Rule**: Any candidate that lowers overall MAE by increasing positive bias (especially during high solar elevation) is **operationally unacceptable**.

---

## 2. Experimental Governance & Scientific Rigor

To prevent subtle statistical contamination, POLARIS enforces strict governance standards across all forecasting experiments:

### 2.1 Partition Protocol & Calendar Vintages
The project dataset comprises pyranometer downwelling shortwave global horizontal irradiance ($SW_{\text{IN}}$, in $\text{W/m}^2$) and numerical weather prediction (NWP) forecasts across two complete annual cycles:
1. **2024 Dataset (Development & Validation)**:
   - Total Origins: 347 forecast issuance origins.
   - **EVEN Partition (Training)**: Origins with even calendar index ($n = 174$ origins; 4,176 total hours; 2,885 daytime hours).
   - **ODD Partition (Validation / Tuning)**: Origins with odd calendar index ($n = 173$ origins; 4,152 total hours; 2,883 daytime hours).
   - Both splits cover all 12 calendar months to prevent seasonal distribution shifts.
2. **2025 Dataset (Genuinely Blind Test Set)**:
   - 364 forecast origins (8,736 total hours; 5,978 daytime hours).
   - **Strictly Blind**: Never accessed, fitted, or tuned against during model selection. Only evaluated once a candidate passes validation gates.

### 2.2 Day/Night Partitioning & Physical Zeroing
- Solar forecasting metrics are computed **strictly on daytime rows** ($\text{is\_daytime} \equiv \text{actual\_SW\_IN} > 0$ or astronomical $\text{clearsky\_ghi} > 0$). Including polar night hours (where irradiance is identically 0) falsely dilutes MAE by 30–50%.
- **Causal Night Zeroing**: At inference, whenever astronomical solar elevation $\theta_{\text{elev}} \le 0^\circ$ or clear-sky irradiance $GHI_{\text{cs}} \le 0$, the forecast is forced to $0.0\text{ W/m}^2$.

### 2.3 Corrected Origin-Level Clustered Block Bootstrap
Individual hourly errors within a 24-hour forecast origin are autocorrelated ($\rho_1 \approx 0.64$). Treating individual hourly rows as independent identically distributed (i.i.d.) samples severely under-estimates confidence interval widths.
- **Protocol**: 2,000 paired bootstrap resamples drawn at the **forecast origin level** ($N = 173$ clusters for 2024-ODD, $N = 364$ clusters for 2025). Entire 24-hour trajectory blocks are resampled with replacement (`research_utils.bootstrap_mae_diff_ci_corrected`).
- **Promotion Threshold**: A candidate can only claim superiority over a baseline if the **95% bootstrap confidence interval upper bound of $\Delta\text{MAE} = \text{MAE}_{\text{cand}} - \text{MAE}_{\text{base}}$ is strictly negative ($< 0.0\text{ W/m}^2$)**. If the interval crosses zero, the improvement is statistically indistinguishable from noise.

### 2.4 Cryptographic Provenance & Fail-Closed Assertions
- Every data matrix, baseline prediction, and serialized model artifact (`.joblib`) is bound to a SHA-256 cryptographic hash.
- Training scripts verify input hashes prior to execution and fail closed (`SystemExit` / `RuntimeError`) upon any byte mismatch.

---

## 3. Historical Chronology of Forecasting Stages (1 through 8.1)

### 3.1 Pre-Stage: Foundation Time-Series Models (Chronos-2 & TimesFM)
Before gradient boosted trees were adopted, foundational zero-shot deep time-series models were benchmarked:
- **Google TimesFM 3.0**:
  - Evaluated across rolling 24-hour windows using historical context.
  - While it captured seasonal diurnal curves, it lacked physical NWP feature conditioning. Under sudden Arctic storm fronts, it persisted clear-sky shapes, resulting in large overprediction errors (daytime MAE $> 48\text{ W/m}^2$).
- **Amazon Chronos-2 (T5-based autoregressive probabilistic architecture)**:
  - Tested zero-shot and LoRA fine-tuned on Nuolja data (500 and 1,000 steps; `polaris_lora_500`, `polaris_lora_1000`).
  - Univariate Chronos-2 exhibited smooth inertia but suffered from severe lag during rapid cloud overcast. Multivariate experiments conditioning Chronos-2 on NWP forecasts showed improvements in low-to-moderate solar regimes, but deteriorated during peak midday hours due to tokenizer quantization blur.

### 3.2 Stage 3: Physics & Clear-Sky Baselines
- **Stage 3a (Solar Geometry Baseline)**: Ineichen clear-sky model ($GHI_{\text{cs}}$) based purely on astronomical solar position. Serves as theoretical upper ceiling.
- **Stage 3b (Chronos-2 + Cloud NWP)**: Locked Chronos-2 model conditioned on MetCoOp cloud cover forecast (`fc_cloud_cover`). Daytime MAE: $\approx 46.5\text{ W/m}^2$.
- **Stage 3c (Full NWP Injection)**: Adding surface temperature, relative humidity, and pressure.

### 3.3 Stage 4: Horizon-Adaptive Cloud-Damped Clearsky Ensemble
Stage 4 introduced a physical ensemble combining Chronos-3B with cloud-damped clear-sky radiation:
$$\hat{y}(h) = \max\left(0, \; w_h \cdot \text{Chronos\_3B}(h) + (1 - w_h) \cdot \max\left(0, \; GHI_{\text{cs}}(h) \cdot (1 - k_h \cdot \text{cloud\_frac}(h))\right)\right)$$
- $w_h \in [0, 1]$: Learned weight assigning authority to Chronos-3B vs physical clear-sky attenuation per horizon $h \in \{1 \dots 24\}$.
- $k_h \in [0, 1]$: Learned cloud extinction coefficient per horizon.
- Parameters fitted strictly on 2024-EVEN daytime rows via Nelder-Mead optimization.
- **Failure of Residual Corrections**: Five distinct post-hoc residual corrections (Global Ridge, Horizon-Specific Affine, Regime-Conditioned Affine, Ridge with Physics Interactions, Isotonic Regression) were trained to predict Stage 4 residuals. **Every single correction worsened test MAE by $+1.5$ to $+32\text{ W/m}^2$** due to overfitting odd/even weather distribution mismatches.

### 3.4 Stages 5–7: Physical & Spatial Feature Expansion
- **Stage 5 (Spatial NWP & Advection)**: Investigated 3x3 and 21x21 AROME/MEPS grid domains around Mount Nuolja to track cloud fronts upwind. Proved that local terrain causes micro-scale cloud trapping not captured by coarse grids.
- **Stage 6 (Cloud Microphysics & Remote Sensing)**:
  - Extracted Liquid Water Path (LWP) and Ice Water Path (IWP) from MEPS atmospheric model levels at 700 hPa.
  - Added snow-cover / ground-albedo interaction flags.
- **Stage 7 (Topographic Shading & Upper Winds)**:
  - **High-Resolution DEM Shading**: Derived local ridge horizon profile (`terrain_horizon_elevation_deg`), solar clearance margin (`terrain_elevation_margin_deg`), and obstruction flag (`terrain_solar_obstruction_flag`). When the sun dips behind Mount Nuolja's peak, clear-sky irradiance is clipped to diffuse-only levels (`clearsky_ghi_terrain_adjusted`).
  - **Upper-Air Wind Vectors**: Extracted 700 hPa horizontal wind components ($u_{700}, v_{700}$) to represent steering velocity of cloud decks.

### 3.5 Stage 8.1 Frozen Production Control Model
The culmination of Stages 1–7 was frozen as the official production control model:
- **Algorithm**: `sklearn.ensemble.HistGradientBoostingRegressor`
- **Hyperparameters**:
  ```python
  HistGradientBoostingRegressor(
      loss="absolute_error",  # L1 loss (median regression, robust to solar spikes)
      max_depth=4,
      min_samples_leaf=30,
      l2_regularization=10.0,
      random_state=42,
  )
```
- **Frozen 37-Feature Contract**:
  1. *Astronomical Geometry*: `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`
  2. *Surface NWP*: `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`
  3. *Stage 4 Derived*: `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`
  4. *Rolling 24h Context Stats*: `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`
  5. *Cloud Microphysics*: `lwp_latest`, `iwp_latest`, `lwp_x_cloud`
  6. *Topographic Shading*: `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`
  7. *Upper-Air Steering Wind*: `u700`, `v700` (horizons 20–24 natively allowed NaN due to NWP 3h cadence).
- **Frozen Benchmark Performance**:
  - **2024-ODD Validation**: MAE = $36.2040\text{ W/m}^2$, RMSE = $64.5752\text{ W/m}^2$, Bias = $+0.9605\text{ W/m}^2$, nMAE = $28.08\%$
  - **2025 Blind Test**: MAE = $35.9745\text{ W/m}^2$, RMSE = $65.9427\text{ W/m}^2$, Bias = $+4.0802\text{ W/m}^2$, nMAE = $28.25\%$
  - **High-Elevation Blind ($\theta_{\text{elev}} \ge 30^\circ$, $n=978$)**: MAE = $100.9250\text{ W/m}^2$, Bias = $+13.7469\text{ W/m}^2$ (severe overprediction).

---

## 4. The Station-Tuning Research Campaign (Candidates A through K)

Following the freeze of Stage 8.1, a systematic research campaign was conducted to address the high-elevation overprediction bias and improve blind accuracy.

```
                                  [Stage 8.1 Frozen Control] (Candidate A)
                                       MAE: 35.97 W/m², Bias: +4.08 W/m²
                                                    |
       +-----------------------+--------------------+--------------------+-----------------------+
       |                       |                    |                    |                       |
 [Candidate B]           [Candidate C]        [Candidate D]        [Candidate E]         [Sample Weighting]
 Data Expansion        Horizon Bucketing     2-Stage Residual    Hyperparam Search       Elevation Weight
 (INFEASIBLE)             (FAILED)             (FAILED)             (FAILED)                 (FAILED)
 ΔMAE: N/A             ΔMAE: +0.40 W/m²     Overfit on ODD       Bias: +5.37 W/m²        High-Elev Bias: +19.95
                                                    |
                                          [Candidate F] (PASSED)
                                    Feature: solar_elevation × cloud_frac
                                  ΔMAE: -0.48 W/m² (CI: [-0.73, -0.23])
                                                    |
                      +-----------------------------+-----------------------------+
                      |                                                           |
                [Candidate G]                                               [Candidate H]
            Transition Cloud Flag                                       Asymmetric Pinball Loss
                 (REDUNDANT)                                                    (FAILED)
              ΔMAE: -0.44 W/m²                                              Bias: -10.33 W/m²
                      |                                                           |
                [Candidate I]                                                     |
             Targeted Residual                                                    |
                 (FAILED)                                                         |
             High-Elev Overfit                                                    |
                      |                                                           |
                      +-----------------------------+-----------------------------+
                                                    |
                                          [Candidate J] (PASSED)
                                   Candidate F + elevation × transition
                                  ΔMAE vs F: -0.19 W/m² (CI: [-0.35, -0.04])
                                  Overall Blind MAE: 35.30 W/m²
```

### Detailed Candidate Dossiers

#### Candidate A: Frozen Stage 8.1 Control
- **Role**: Reference baseline for all experiments. Cryptographically verified before and after each run.

#### Candidate B: Expanded Historical Vintage
- **Concept**: Expand training set to multi-year history (e.g., 2020–2023).
- **Verdict**: **INFEASIBLE**. Repository only contained quality-controlled station pyranometer data for 2024 and 2025. Training on 2024-ODD violates validation isolation; training on 2025 destroys blind testing. No workaround invented.

#### Candidate C: Horizon-Specific Models (4 Buckets: H1–6, H7–12, H13–18, H19–24)
- **Concept**: Fit 4 separate HGB models, one for each 6-hour lookahead window.
- **Empirical Result**: Blind MAE = $36.3793\text{ W/m}^2$ (Control: $35.9745\text{ W/m}^2$, $\Delta = +0.40\text{ W/m}^2$). Bootstrap 95% CI: $[-0.03, +0.85]\text{ W/m}^2$.
- **Failure Analysis**: Splitting 174 training origins into 4 slices reduced training sample size to $n=478\dots 969$ rows per bucket. Sample starvation destroyed generalization. The unified single model with `horizon_hour` as a feature already splits on horizon without sacrificing sample size.

#### Candidate D: Two-Stage Out-Of-Fold Residual Correction
- **Concept**: Stage 1 fits base HGB model on 2024-EVEN. Generate 2-fold out-of-fold (OOF) predictions within EVEN. Stage 2 HGB model is trained on OOF residuals ($r = y - \hat{y}_{\text{oof}}$). Final prediction = $\hat{y}_{\text{base}} + \hat{r}$.
- **Empirical Result**:
  - 2024-ODD Validation: MAE dropped to $35.5313\text{ W/m}^2$ (Control: $36.2040\text{ W/m}^2$, apparent $-0.67\text{ W/m}^2$ gain).
  - 2025 Blind Test: MAE was $36.0656\text{ W/m}^2$ (Control: $35.9745\text{ W/m}^2$, $\Delta = +0.09\text{ W/m}^2$, flat/worse). Bootstrap 95% CI: $[-0.49, +0.66]\text{ W/m}^2$.
- **Failure Analysis**: Textbook validation overfitting. Residual patterns learned on 2024 did not transfer to the distinct weather regimes of 2025.

#### Candidate E: 144-Point Hyperparameter Grid Search
- **Concept**: Optimize `max_depth` $\in \{3,4,5,6\}$, `min_samples_leaf` $\in \{15,30,50,100\}$, `l2_regularization` $\in \{1,10,30\}$, `learning_rate` $\in \{0.05,0.1,0.2\}$. Selected by ODD MAE.
- **Selected Best**: `max_depth=5, min_samples_leaf=50, l2=30.0, lr=0.2`.
- **Empirical Result**: Blind MAE = $35.7928\text{ W/m}^2$ (apparent $-0.18\text{ W/m}^2$ gain), but Bootstrap 95% CI $[-0.66, +0.29]\text{ W/m}^2$ spanned zero. Crucially, **bias worsened from $+4.08$ to $+5.37\text{ W/m}^2$** (+31.7% more overprediction).
- **Verdict**: **REJECTED**. The small MAE shift was statistically insignificant and paid for by higher overprediction risk.

#### Phase 3 Experiment: Solar-Elevation Sample Weighting
- **Concept**: Weight training samples by solar elevation: $w_i = 1.0 + \text{clip}(\theta_{\text{elev}}, 0, 90) / 30.0$ to force the tree to prioritize high-elevation errors.
- **Empirical Result**: Blind MAE = $35.8626\text{ W/m}^2$ (CI spanned zero). In the targeted high-elevation subset ($\theta_{\text{elev}} \ge 30^\circ$), **bias exploded from $+13.75$ to $+19.95\text{ W/m}^2$**.
- **Failure Analysis**: Weighting rows under symmetric L1 loss distorted the median estimator, pushing predictions upward into the heavy right-tail errors.

#### Candidate F: Additive Interaction Feature (`solar_elevation × cloud_frac`)
- **Concept**: Error forensics revealed that high solar elevation combined with broken clouds produced the largest errors. Candidate F added exactly ONE continuous multiplicative feature:
  $$\text{elevation\_x\_cloud\_frac} = \text{solar\_elevation} \times \text{cloud\_frac}$$
  Total features: 38. Exact same HGB architecture and hyperparameters as control.
- **Empirical Result**:
  - 2024-ODD Validation: MAE $35.4438\text{ W/m}^2$ ($-0.76\text{ W/m}^2$).
  - **2025 Blind Test**: MAE = **$35.4948\text{ W/m}^2$** (Control: $35.9745\text{ W/m}^2$, **$\Delta = -0.4797\text{ W/m}^2$**).
  - **Bootstrap 95% CI**: **$[-0.7307, -0.2338]\text{ W/m}^2$** (Corrected origin bootstrap: $[-0.8040, -0.1515]\text{ W/m}^2$). **Excludes zero entirely on the improving side!**
  - **High-Elevation Subset**: MAE dropped from $100.93$ to $98.68\text{ W/m}^2$ ($-2.24\text{ W/m}^2$), and bias improved from $+13.75$ to $+12.74\text{ W/m}^2$.
- **Verdict**: **PASSED**. First candidate in POLARIS history to break the blind barrier with statistical significance while simultaneously improving bias.

#### Candidate G: Transition-Cloud Discontinuous Indicator
- **Concept**: Forensics showed cloud fraction in $[0.2, 0.6)$ had the highest error and bias. Added binary flag $\text{is\_transition\_cloud} = \mathbb{I}(0.2 \le \text{cloud\_frac} < 0.6)$ on top of Candidate F.
- **Empirical Result**: Blind MAE = $35.5386\text{ W/m}^2$ (worse than F's $35.4948\text{ W/m}^2$). Bias in transition regime rose from $+12.15$ to $+13.07\text{ W/m}^2$.
- **Verdict**: **REDUNDANT / REJECTED**. The step discontinuity split trees prematurely.

#### Candidate H: Asymmetric Quantile Loss ($\tau = 0.35$)
- **Concept**: Train HGB with pinball loss at quantile $\tau = 0.35$ instead of median ($\tau = 0.50$) to penalize overprediction more heavily than underprediction.
- **Empirical Result**: Blind MAE worsened to $36.3222\text{ W/m}^2$ ($+0.35\text{ W/m}^2$). Bias collapsed into an extreme negative overshoot: **$-10.3269\text{ W/m}^2$** overall, and **$-21.67\text{ W/m}^2$** at high elevation.
- **Verdict**: **FAILED**. Shifting global quantile to 0.35 destroyed calibration, causing massive daytime under-generation predictions.

#### Candidate I: Targeted High-Elevation Residual Correction
- **Concept**: Train a secondary residual correction model *only* on high-elevation rows ($\theta_{\text{elev}} \ge 30^\circ$).
- **Empirical Result**: Blind MAE = $35.5239\text{ W/m}^2$ (CI: $[-1.35, +0.43]$ spanned zero). In the targeted high-elevation regime, bias worsened from $+12.74$ to **$+20.07\text{ W/m}^2$**.
- **Failure Analysis**: High-elevation training rows on EVEN numbered only $n=489$. Severe sample starvation led to catastrophic overfitting.

#### Candidate J: Candidate F + Joint Elevation × Transition Interaction
- **Concept**: Candidate F's continuous interaction diluted the specific cell "high elevation AND transition cloud". Candidate J crossed elevation directly with the transition flag:
  $$\text{elevation\_x\_transition\_cloud} = \text{solar\_elevation} \times \mathbb{I}(0.2 \le \text{cloud\_frac} < 0.6)$$
  Total features: 39 (Candidate F's 38 + this joint interaction).
- **Empirical Result**:
  - 2024-ODD Validation: MAE = $35.2972\text{ W/m}^2$ ($-0.15\text{ W/m}^2$ vs F).
  - **2025 Blind Test**: MAE = **$35.3036\text{ W/m}^2$** (Control: $35.9745\text{ W/m}^2$; Candidate F: $35.4948\text{ W/m}^2$).
  - **Paired Bootstrap vs Candidate F (Corrected)**: **mean $-0.1905\text{ W/m}^2$, 95% CI: $[-0.3484, -0.0364]\text{ W/m}^2$** (Strictly below zero!).
  - **Paired Bootstrap vs Control**: **mean $-0.6682\text{ W/m}^2$, 95% CI: $[-1.0246, -0.3097]\text{ W/m}^2$**.
  - **Targeted Joint Cell**: MAE improved from $114.57$ to $113.99\text{ W/m}^2$; bias held at $+44.47\text{ W/m}^2$ (no regression).
  - High elevation MAE dropped to $98.05\text{ W/m}^2$; transition cloud MAE dropped to $45.29\text{ W/m}^2$.
- **Verdict**: **PASSED**. Outperformed Candidate F across both validation and blind evaluation.

---

## 5. The Great Forensic Audit & Clean Successor Paradigm (Candidates F Successor & Candidate K)

In October 2026, an exhaustive forensic data provenance and causality audit (`TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md`) was conducted on Candidate F and Historical Stage 8.1. The audit uncovered **two foundational integrity violations** that altered the trajectory of the research program.

### 5.1 Violation 1: Non-Causal MEPS 00Z Cloud Microphysics
- **The Issue**: Features `lwp_latest` and `iwp_latest` were extracted from MEPS model cycle `T00Z` of the same day as the forecast origin (`origin_dt = forecast_start`).
- **Physical Timeline**:
  - Decision cutoff: $00:00\text{ UTC}$.
  - MEPS 00Z nominal initialization: $00:00\text{ UTC}$.
  - Actual operational dissemination latency of MEPS NWP runs: **~135 minutes** (data published at $\approx 02:15\text{ UTC}$).
  - A numerical weather model cannot publish output at the exact second it initializes. At $00:00\text{ UTC}$, 00Z MEPS does not exist.
- **The External Audit**: Live queries to MET Norway's THREDDS OPeNDAP server confirmed:
  - 00Z MEPS is unviable at cutoff (`UNAVAILABLE_AT_CUTOFF_VERIFIED`).
  - **The Solution**: The prior-day **18Z MEPS run** (`meps_det_pl_YYYYMMDDT18Z.ncml`) is already 6 hours old at $00:00\text{ UTC}$, fully published, and covers 67 hourly steps ($0 \dots +66\text{ h}$).
  - **Exact Lead Mapping**: For base horizon $h \in \{1 \dots 24\}$, target valid time is $\text{origin} + (h-1)\text{ hours}$. Since the 18Z run initialized at $\text{origin} - 6\text{ hours}$, the required source lead time is:
    $$\text{lead} = (\text{origin} + h - 1) - (\text{origin} - 6) = 5 + h$$
    Valid across all 24 horizons ($\text{lead } 6 \dots 29 \le 67$).

### 5.2 Violation 2: Target Leakage in 2025 Stage 4 Derived Features
- **The Issue**: Stage 4 ensemble parameters ($w_h, k_h$) in `stage4_results_2025/ensemble_parameters.json` were fitted using Nelder-Mead optimization against `actual_SW_IN` from **2025 origins**!
- **Consequence**: The four derived features:
  - `pred_stage3b_cloud_nwp`
  - `phys_pred_fold`
  - `pred_stage4_fold`
  - `disagreement_fold`
  were constructed for 2025 rows using parameters learned from realized 2025 solar targets. This constituted **direct target leakage**, invalidating the claim that 2025 was a clean blind evaluation for Stage 8.1, Candidate F, and Candidate J.

### 5.3 The Clean Successor Architecture (Candidate F Successor v1 & v2)
To re-establish absolute scientific integrity, a clean rebuild was executed:
1. **Purge Leaked Features**: Dropped the 4 contaminated Stage 4 derived features.
2. **Causal 18Z Substitution**: Replaced 00Z LWP/IWP with causal 18Z MEPS features (`lwp_18z_fc`, `iwp_18z_fc`, `lwp_x_cloud_18z`) using the verified $\text{lead} = 5+h$ contract.
3. **Clean 33-Feature Contract (`SUCCESSOR_33_FEATURES`)**:
   `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`, `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`, `u700`, `v700`, `lwp_18z_fc`, `iwp_18z_fc`, `lwp_x_cloud_18z`, `elevation_x_cloud_frac`.
4. **Clean Baseline Performance (2024-ODD Validation)**:
   - Clean Stage 4 Physical Baseline: $\text{MAE} = 43.4295\text{ W/m}^2$, $\text{Bias} = -2.3544\text{ W/m}^2$.
   - Candidate F Successor v2: $\text{MAE} = 38.7742\text{ W/m}^2$, $\text{Bias} = +1.6601\text{ W/m}^2$ (Clean improvement of $-4.6553\text{ W/m}^2$ over Clean Stage 4).

### 5.4 Candidate K: Baseline Conditioning & Residual Reformulation
With a clean 33-feature foundation in place, **Candidate K** tested whether conditioning the GBDT directly on the clean baseline could close the performance gap.
- **Hypothesis**: The GBDT struggles to learn astronomical clear-sky attenuation from scratch. If we supply `pred_stage4_clean` (the clean physical baseline fitted strictly on 2024-EVEN) and `clean_attenuation = clearsky_ghi - pred_stage4_clean` as features (35 features total), and train the tree to predict the **additive residual**:
  $$r = \text{actual\_SW\_IN} - \text{pred\_stage4\_clean}$$
  then reconstruct $\hat{y} = \max(0, \text{pred\_stage4\_clean} + \hat{r})$, the tree can focus its capacity entirely on atmospheric and topographic corrections.
- **Empirical Validation Results (2024-ODD, $n=2,883$)**:
  - **Candidate K MAE**: **$37.7169\text{ W/m}^2$** (Successor v2: $38.7742\text{ W/m}^2$, Clean Stage 4: $43.4295\text{ W/m}^2$).
  - **Paired Bootstrap vs Successor v2**: **$\Delta\text{MAE} = -1.0573\text{ W/m}^2$, 95% CI: $[-1.6427, -0.4690]\text{ W/m}^2$** (Statistically significant at $p < 0.05$!).
  - **Validation Bias**: **Collapsed to $+0.1062\text{ W/m}^2$** (virtually zero bias, compared to $+1.66\text{ W/m}^2$ for Successor v2 and $-2.35\text{ W/m}^2$ for Stage 4).
  - **Feature Importance**: Permutation importance revealed `pred_stage4_clean` was overwhelmingly the **#1 feature (+8.18 W/m²)**, followed by `terrain_elevation_margin_deg` (+2.45 W/m²), `fc_relative_humidity_2m` (+2.15 W/m²), and `elevation_x_cloud_frac` (+1.33 W/m²).

### 5.5 Candidate N: Additive Physics Synthesis & Multi-Seed Specialist Ensemble (Candidate N1 & N6)
Building on Candidate K's baseline conditioning and Candidate J's cross-interaction breakthrough, **Candidate N** evaluated the unified 36-feature contract:
$$\text{CANDIDATE\_N\_36\_FEATURES} = \text{CANDIDATE\_K\_35\_FEATURES} + [\text{elevation\_x\_transition\_cloud}]$$
Two primary model variants were frozen and evaluated:
1. **Candidate N1 (Single Tree)**: A single HistGradientBoostingRegressor ($d_{\text{max}}=5, \lambda=10.0, \eta=0.1$) trained on the additive residual $r = \text{actual\_SW\_IN} - \text{pred\_stage4\_clean}$ using the 36-feature contract.
2. **Candidate N6 (Multi-Seed Specialist Blend)**: An ensemble combining:
   - **Additive Residual Model**: 25-seed bagged ensemble of HGB models on 36 features predicting additive residual $r$.
   - **Clearness-Index ($k_t$) Specialist**: 15-seed bagged ensemble of HGB models on 36 features predicting clearness index $k_t = \text{actual\_SW\_IN} / \text{clearsky\_ghi\_terrain\_adjusted}$.
   - **Elevation-Ramped Shading-Gated Blending**:
     $$\alpha(\theta) = \begin{cases} 0 & \text{if } \theta < 20^\circ \text{ or shaded} \\ \min\left(0.45, \; 0.45 \cdot \frac{\theta - 20^\circ}{20^\circ}\right) & \text{if } \theta \ge 20^\circ \text{ and unshaded} \end{cases}$$
     $$\hat{y}_{\text{N6}} = (1 - \alpha) \cdot \hat{y}_{\text{additive}} + \alpha \cdot \hat{y}_{k_t}$$

### 5.6 Official 2025 One-Shot Blind Evaluation (Clean 18Z Lineage)
In October 2026, the frozen clean 18Z models were evaluated in a strictly controlled one-shot test on the 2025 blind partition ($n=5,978$ daytime rows, 364 forecast origins) with zero retraining or parameter tuning. `blind_baseline.csv` was generated using frozen 2024-EVEN parameters without target leakage.

| Model Architecture | Features / Setup | 2025 Blind MAE | Blind RMSE | Blind Bias | LE MAE ($\theta < 30^\circ$) | HE MAE ($\theta \ge 30^\circ$) | HE Bias | 95% Bootstrap CI vs Candidate K | Gate Status |
|---|---|---|---|---|---|---|---|---|---|
| **Clean Stage 4 Baseline** | Chronos-3B + Cloud Clearsky ($w_h, k_h$) | 41.7661 | 74.1735 | -7.1523 | 27.5418 | 114.4873 | -10.9374 | +4.3058 [+3.1535, +5.4899] | BASELINE |
| **Candidate F Successor v2** | 33 Causal 18Z Features | 38.1899 | 69.8646 | -2.1984 | 24.6789 | 107.2648 | -10.3394 | +0.7297 [+0.3364, +1.1083] | BASELINE |
| **Candidate K** | 35 Features (Additive Residual) | 37.4603 | 68.7855 | -3.9954 | 23.9171 | 106.6992 | -12.5825 | +0.0000 [+0.0000, +0.0000] | CONTROL |
| **Candidate N1** | 36 Features (Single Tree) | 37.2669 | 68.4236 | -3.8720 | 23.8760 | 105.7274 | -10.5378 | -0.1934 [-0.4884, +0.1008] | HOLD |
| **Candidate N6** | 36 Features (25-seed Additive + 15-seed $k_t$) | **36.7856** | **67.1875** | **-2.9862** | **23.7924** | **103.2134** | **-8.8438** | **-0.6746 [-1.0951, -0.2779]** | **PASSED** |

**Key Findings**:
- **Candidate N6 is the first model to break below $37.0\text{ W/m}^2$ Blind MAE** ($36.7856\text{ W/m}^2$), achieving a statistically significant gain of $-0.6746\text{ W/m}^2$ over Candidate K (95% CI strictly $< 0$: $[-1.0951, -0.2779]\text{ W/m}^2$).
- **Multi-seed bagging + specialist ramp** successfully mitigated high-elevation errors: High-Elevation MAE dropped by $-3.49\text{ W/m}^2$ ($106.70 \to 103.21\text{ W/m}^2$), and high-elevation bias improved from $-12.58$ to $-8.84\text{ W/m}^2$ without degrading low-elevation performance ($23.79\text{ W/m}^2$).
- Candidate N1 achieved a directional gain of $-0.1934\text{ W/m}^2$, but its bootstrap CI crossed zero ($[-0.4884, +0.1008]$), placing it on HOLD.

---

## 6. Uncertainty-Aware Forecasting & The L2 Risk Interface (GAP19 / MILP)

Forecasting point estimates alone is insufficient for autonomous microgrid dispatch. The **L2 Uncertainty Layer** bridges point forecasts to the MILP optimizer.

### 6.1 Statistical Error Dynamics: AR(1) Autoregressive Process
Empirical diagnostics across $N=14,517$ contiguous daylight pairs proved that forecast errors $e_t = \hat{I}_t - I_t$ are highly autocorrelated:
$$e_t - \mu = \phi (e_{t-1} - \mu) + \epsilon_t \iff e_t = c + \phi e_{t-1} + \epsilon_t$$
- **Autoregressive Parameter**: $\phi = 0.6435$
- **Lag-1 ACF**: $\rho_1 = 0.6386$
- **Intercept**: $c = 11.7258\text{ W/m}^2$
- **Unconditional Stationary Mean**: $\mu = \frac{c}{1 - \phi} = 32.8914\text{ W/m}^2$

### 6.2 The Non-Gaussian Innovation Reality
Classical control theory often assumes Gaussian white noise: $\epsilon_t \sim \mathcal{N}(0, \sigma^2)$. Diagnostic testing emphatically rejected this:
- **Excess Kurtosis**: $\kappa = 3.4452$ (**Heavy-tailed distribution**).
- **Ljung-Box Test at Lag 5**: $Q_5 = 38.86, \; p = 2.54 \times 10^{-7}$ (White noise **decisively rejected**).
- **Ljung-Box Test at Lag 10**: $Q_{10} = 79.03, \; p = 7.76 \times 10^{-13}$ (White noise **decisively rejected**).
- **Operational Implication**: Closed-form Gaussian variance expansion $\text{Var}\left(\sum \epsilon_t\right) = \sum \sigma_t^2$ severely underestimates extreme solar drought events. **Distribution-free empirical conformal prediction or non-parametric quantile estimation is mathematically mandatory**.

### 6.3 Translating Forecast Uncertainty into Microgrid Reserve (GAP19 Injection)
- **Power Conversion Factor**: $K_{pv} = A_{pv} \cdot \eta_{mod} \cdot PR = 300\text{ m}^2 \times 0.20 \times 0.85 = 51.0\text{ W} / (\text{W/m}^2)$.
- **Inverter Saturation**: $P_{pv}(t) = \min(60000.0, \; 51.0 \cdot I(t))\text{ W}$.
- **Forward Survivability Window $\mathcal{W}_t$**: The reserve at hour $t$ must protect against cumulative solar shortfall over a forward lookahead horizon $\mathcal{W}_t = [\tau = t \dots \min(t+W-1, 23)]$:
  $$\Delta E_{\text{shortfall}}(t, W) = \sum_{\tau \in \mathcal{W}_t} \frac{1}{\eta_{\text{dis}}} \max\left(0, \; K_{pv} \cdot e_{\tau}\right) \Delta t$$
- **GAP19 Injection Mechanism**: Instead of modifying solver constraints or passing scalars, the risk engine computes a 24-element dynamic Emergency Battery Reserve vector:
  $$EBR(t) = \max\left(EBR_{\text{base}}, \; \text{Quantile}_{1-\alpha}\left(\Delta E_{\text{shortfall}}(t, W)\right)\right)$$
  injected directly into `config["ebr_target_wh"]`, which HiGHS natively enforces.

---

## 7. Master Comparison Matrix of All Tested Candidates

| Candidate / Model | Description / Features | 2024-ODD Validation MAE (Bias) | 2025 Blind Test MAE (Bias) | Bootstrap 95% CI vs Baseline | Verdict & Operational Status |
|---|---|---|---|---|---|
| **TimesFM 3.0** | Zero-shot foundation model | $> 48.0\text{ W/m}^2$ | $> 50.0\text{ W/m}^2$ | N/A | Base benchmark. Lacks NWP conditioning. |
| **Chronos-2 LoRA** | Fine-tuned probabilistic T5 | $\approx 46.5\text{ W/m}^2$ | $\approx 47.0\text{ W/m}^2$ | N/A | Base benchmark. Suffers from optical lag. |
| **Stage 4 Ensemble** | Chronos-3B + Cloud-Damped Clearsky ($w_h, k_h$) | $43.43\text{ W/m}^2$ ($-2.35$) | $43.85\text{ W/m}^2$ ($-1.80$) | N/A | Strong physical baseline. Residual corrections failed. |
| **Historical Stage 8.1** | 37-feature HGBR (includes 00Z MEPS + Stage 4) | $36.20\text{ W/m}^2$ ($+0.96$) | $35.97\text{ W/m}^2$ ($+4.08$) | Reference Control | **Frozen Control**. Disclosed non-causal inputs. |
| **Candidate B** | Expanded Multi-Year Vintage | N/A | N/A | N/A | **INFEASIBLE**. No clean 3rd vintage available. |
| **Candidate C** | 4-Bucket Horizon-Specific Models | $36.20\text{ W/m}^2$ ($+1.18$) | $36.38\text{ W/m}^2$ ($+5.10$) | $[-0.03, +0.85]$ | **FAILED**. Sample starvation ($n < 900$). |
| **Candidate D** | 2-Stage Out-of-Fold Residual Correction | $35.53\text{ W/m}^2$ ($-3.34$) | $36.07\text{ W/m}^2$ ($+1.14$) | $[-0.49, +0.66]$ | **FAILED**. Overfit 2024; flat on blind 2025. |
| **Candidate E** | 144-Point Hyperparameter Grid Search | $34.63\text{ W/m}^2$ ($+2.12$) | $35.79\text{ W/m}^2$ ($+5.37$) | $[-0.66, +0.29]$ | **FAILED**. CI includes 0; bias rose +32%. |
| **Phase 3 Weighting** | Solar Elevation Sample Weighting | $35.49\text{ W/m}^2$ ($+1.57$) | $35.86\text{ W/m}^2$ ($+5.19$) | $[-0.44, +0.22]$ | **FAILED**. High-elevation bias exploded to +19.95. |
| **Candidate F** | 38 Features (Stage 8.1 + `elevation × cloud_frac`) | $35.44\text{ W/m}^2$ ($+0.75$) | **$35.49\text{ W/m}^2$** ($+3.70$) | **$[-0.80, -0.15]$** | **PASSED**. Significant blind gain; lowered high-elev bias. |
| **Candidate G** | 39 Features (F + `is_transition_cloud`) | $35.41\text{ W/m}^2$ ($+0.82$) | $35.54\text{ W/m}^2$ ($+3.88$) | $[-0.77, -0.13]$ vs A | **REDUNDANT**. Failed to beat Candidate F. |
| **Candidate H** | Asymmetric Pinball Loss ($\tau = 0.35$) | $36.45\text{ W/m}^2$ ($-9.80$) | $36.32\text{ W/m}^2$ ($-10.33$) | $[-0.67, +1.35]$ vs A | **FAILED**. Massive negative bias overshoot. |
| **Candidate I** | Targeted High-Elevation Residual HGB | $35.42\text{ W/m}^2$ ($+0.80$) | $35.52\text{ W/m}^2$ ($+4.90$) | $[-1.35, +0.43]$ vs A | **FAILED**. $n=489$ rows caused extreme overfitting. |
| **Candidate J** | 39 Features (F + `elevation × transition`) | $35.30\text{ W/m}^2$ ($+0.97$) | **$35.30\text{ W/m}^2$** ($+3.66$) | **$[-0.35, -0.04]$ vs F** | **PASSED**. New best in Stage 8.1 lineage. |
| **Clean Stage 4 Baseline** | Chronos-3B + Cloud-Damped Clearsky ($w_h, k_h$) | $43.43\text{ W/m}^2$ ($-2.35$) | $41.77\text{ W/m}^2$ ($-7.15$) | $+4.31$ vs K ($[+3.15, +5.49]$) | **CLEAN PHYSICAL BASELINE**. Frozen 2024-EVEN. |
| **Clean Successor v2** | 33 Causal Features (18Z MEPS, No Stage 4) | $38.77\text{ W/m}^2$ ($+1.66$) | $38.19\text{ W/m}^2$ ($-2.20$) | $+0.73$ vs K ($[+0.34, +1.11]$) | **CLEAN BASELINE**. 100% causal, zero leakage. |
| **Candidate K** | 35 Features (Successor v2 + `pred_st4` + `attenuation`) | $37.72\text{ W/m}^2$ ($+0.11$) | $37.46\text{ W/m}^2$ ($-4.00$) | Reference Clean Control | **CONTROL (CLEAN)**. Additive conditioning. |
| **Candidate N1** | 36 Features (K + `elevation_x_transition_cloud`) | $37.46\text{ W/m}^2$ ($+0.04$) | $37.27\text{ W/m}^2$ ($-3.87$) | $[-0.49, +0.10]$ vs K | **HOLD**. Directional gain ($-0.19$), CI spans 0. |
| **Candidate N6** | 36 Features (25-seed Additive + 15-seed $k_t$ Blend) | **$37.20\text{ W/m}^2$** ($+0.37$) | **$36.79\text{ W/m}^2$** (**$-2.99$**) | **$[-1.10, -0.28]$ vs K** | **PASSED GATES 1, 2, & 3**. First $<37\text{ W/m}^2$ clean model! |

---

## 8. Lessons Learned: What Works, What Fails, and Why

### What Consistently Fails
1. **Splitting Models by Sub-Regimes (Candidates C, I)**:
   Dividing the dataset into horizon buckets or elevation slices starves tree algorithms of training examples. HistGradientBoosting already performs hierarchical axis-aligned feature splits. Explicit data carving reduces effective sample size below the variance threshold.
2. **Post-Hoc Black-Box Residual Modeling (Stage 4 Residuals, Candidate D)**:
   Fitting an unconstrained second-stage model to predict out-of-fold residuals captures idiosyncrasies of the training year's weather sequence rather than universal physical laws. It routinely produces impressive in-sample/validation drops that evaporate on blind data.
3. **Global Loss Asymmetry / Sample Weighting (Phase 3 Weighting, Candidate H)**:
   Applying an un-tuned asymmetric loss ($\tau = 0.35$) or multiplying sample weights across all hours causes extreme overshooting or inflates variance. The model sacrifices accuracy across 90% of hours to suppress a handful of outliers.
4. **Discontinuous Hard Regime Flags (Candidate G)**:
   Hard step functions (e.g. $\mathbb{I}(0.2 \le \text{cloud} < 0.6)$) create artificial boundary discontinuities that gradient boosting splits awkwardly. Smooth continuous interactions are consistently superior.

### What Consistently Works
1. **Physically-Motivated Smooth Multiplicative Interactions (Candidates F, J)**:
   Multiplying continuous solar geometry with atmospheric opacity ($\text{solar\_elevation} \times \text{cloud\_frac}$) directly mirrors the Beer-Lambert-Bouguer optical transmission law:
   $$I_{\text{direct}} = I_{\text{ext}} \cdot e^{-m \cdot \tau_{\text{cloud}}}$$
   Trees cannot easily synthesize multiplicative bilinear surfaces from orthogonal axis-aligned cuts. Supplying the interaction feature directly provides instant predictive leverage across all horizons.
2. **Baseline Conditioning & Residual Target Transformation (Candidate K)**:
   Providing a clean, deterministic physical baseline (`pred_stage4_clean`) as an input feature and training the model to predict the residual ($y - \text{baseline}$) anchors the tree. The tree does not need to learn the astronomical diurnal curve; it only learns the atmospheric perturbation.
3. **Strict Origin-Level Clustered Verification**:
   Testing on genuinely blind calendar years and evaluating paired origin-level bootstrap confidence intervals is the only protection against spurious research claims.

---

## 9. Direct Instructions & Strategic Roadmap for Gemini as Future Research Assistant

Dear Gemini: You are acting as the specialized research assistant for POLARIS solar forecasting. Your mandate is to develop **novel forecasting methodologies** that exceed Candidate K and Candidate J while preserving uncompromising scientific integrity.

### 9.1 Mandatory Rules You Must Obey
1. **Never Contaminate 2025**: The 2025 dataset is strictly held out for final blind testing. Never fit, tune, or select hyperparameters on 2025. All development must occur on 2024-EVEN (train) and 2024-ODD (validation).
2. **Causal Information Barrier at $t_0$**: Every input feature must be physically and operationally available before $00:00\text{ UTC}$.
   - MEPS 00Z products are forbidden. You must use prior-day 18Z products with source lead $\text{lead} = 5 + h$.
   - Upstream model parameters must never be fitted on evaluation-period targets.
3. **The Bias Directive**: You must evaluate both MAE and Bias. A candidate that improves MAE by increasing positive bias in high solar elevation ($\theta_{\text{elev}} \ge 30^\circ$) is **unacceptable** for microgrid operations.
4. **Clustered Bootstrap Gate**: You must report the 2,000-draw paired origin-level bootstrap 95% CI for $\Delta\text{MAE}$. The upper bound must be strictly negative to claim success.

### 9.2 Promising Architectural Frontiers to Explore
Do **not** repeat hyperparameter sweeps, generic residual regressions, or simple horizon bucketing. Focus your reasoning on these high-potential paradigms:

#### Frontier 1: Physics-Informed Neural GBDTs / Clearness Index ($k_t$) Parameterization
- Instead of predicting surface irradiance $SW_{\text{IN}}$ directly, reformulate the prediction target as the **clearness index**:
  $$k_t = \frac{SW_{\text{IN}}}{GHI_{\text{cs\_terrain}}}$$
  where $k_t \in [0, 1.2]$.
- Predicting $k_t$ automatically removes diurnal solar geometry and terrain shading from the regression target. The model only needs to predict the atmospheric transmissivity curve. At inference, irradiance is reconstructed via $\hat{y} = k_t \cdot GHI_{\text{cs\_terrain}}$.

#### Frontier 2: Multi-Horizon Joint Trajectory Modeling (Advection Aware)
- Current GBDTs predict each horizon row semi-independently. However, cloud fronts move across Mount Nuolja with velocity vector $\vec{v}_{700} = (u_{700}, v_{700})$.
- Design an architecture (such as a Lightweight Temporal Convolutional Network or structured Multi-Task MLP) that ingests the full 24-hour NWP profile and outputs the entire vector $\mathbf{\hat{y}} = [\hat{y}_1, \dots, \hat{y}_{24}]^T$, explicitly modeling the temporal covariance matrix $\boldsymbol{\Sigma}$.

#### Frontier 3: Moderate, Region-Targeted Loss Asymmetry ($\tau \in [0.44, 0.47]$)
- Candidate H proved that $\tau = 0.35$ overshoots violently. However, standard L1 loss ($\tau = 0.50$) leaves a $+4.08\text{ W/m}^2$ overprediction bias.
- Investigate a gentle asymmetric pinball loss with $\tau = 0.45$ or an asymmetric Huber loss, applied either globally or weighted specifically during high solar elevation ($\theta_{\text{elev}} \ge 30^\circ$), designed to nudge positive bias toward zero without triggering underprediction collapse.

#### Frontier 4: Split-Conformal Joint Prediction Bands for GAP19
- Extend Candidate K by training dual quantile regressors ($\tau_{0.10}$ and $\tau_{0.90}$) alongside the conditional median.
- Apply split-conformal calibration on 2024-ODD residuals to generate distribution-free, guaranteed-coverage prediction intervals $[\hat{y}_t^{\text{lower}}, \hat{y}_t^{\text{upper}}]$.
- Map $\hat{y}_t^{\text{lower}}$ directly into the GAP19 dynamic reserve vector to achieve zero critical load shedding under worst-case cloud dropouts.

---
*End of Master Compendium — Prepared for Autonomous POLARIS Research Continuity.*
