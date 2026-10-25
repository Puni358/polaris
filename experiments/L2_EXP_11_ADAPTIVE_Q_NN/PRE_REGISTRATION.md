# POLARIS L2-EXP-11: PRE-REGISTRATION DOCUMENT
## Adaptive q10 Relaxation Using a Low-Capacity Neural Network

**Experiment ID:** `L2-EXP-11`  
**Date of Pre-Registration:** `2026-10-04T10:45:00.000000+00:00`  
**Policy JSON Hash (SHA-256):** `4d5d98e3b1102582e1eb96ccb29fb2fb46b8e2fc2248fafc2da1f390aeec3b8b`  
**Governance Mode:** `STRICTLY_RESEARCH_ONLY`  
**Production Authorization:** `NO PRODUCTION PROMOTION AUTHORIZED`  

> **Pre-Registration Lock Statement:**  
> *"2024 evaluation outcomes were not used to select, tune, or modify the L2-EXP-11 formulation, candidate architectures, hyperparameters, or acceptance criteria after pre-registration."*

---

## 1. Core Research Question & Hypothesis

### Research Question
Static $q_{10}$ is the established uncertainty-aware benchmark for microgrid EMS dispatch. It guarantees high critical load reliability but suffers from excessive pessimism, resulting in high diesel fuel consumption and substantial solar curtailment.

> *"Can a low-capacity neural network learn WHEN static $q_{10}$ is unnecessarily pessimistic, and safely relax $q_{10}$ only in those low-risk situations while retaining $q_{10}$-level reliability?"*

### Core Hypothesis
Static $q_{10}$ applies a rigid, constant level of conservatism everywhere regardless of forecast regime. An adaptive $q$-level selector can identify regimes where the forecast is highly trustworthy (clear sky, low cloud fraction, high NWP consensus) and relax the planning quantile upward (e.g. up to $q = 0.25$), while remaining anchored at $q_{10}$ during volatile, cloudy, or high-risk regimes. This selective relaxation can substantially reduce diesel starts and solar curtailment without violating critical reliability.

---

## 2. Model Role & Architectural Constraints

### What the NN Does (and Does NOT Do)
1. **NOT a Solar Predictor:** The NN does not predict raw solar power directly. Candidate F and the frozen SKGBDT models ($q_{10}, q_{50}, q_{90}$) remain the authoritative base models.
2. **NOT an EMS Controller:** The NN does not directly set battery charging, discharging, diesel power, or SOC.
3. **Adaptive Quantile Selector:** The NN maps contextual weather and forecast features to an adaptive planning quantile $q_t \in [0.10, 0.25]$.

```
Candidate-F Forecast + Context Features
                  ↓
          Low-Capacity MLP (16,)
                  ↓
     Predicted Downside Shortfall s_t
                  ↓
      Isotonic Calibration Mapping
                  ↓
       Adaptive Quantile q_t ∈ [0.10, 0.25]
                  ↓
      Solar Planning Trajectory p_solar(q_t)
                  ↓
           GAP19 Optimizer
```

---

## 3. Training Target & Feature Specification

### 3.1 Training Target: Normalized Downside Shortfall
The target is constructed purely from historical forecast error without access to future dispatch or EMS states:
$$s_t = \text{clip}\left(\frac{\max(0, F_t - Y_t)}{\max(\text{clearsky}_t, 25.0)}, 0.0, 1.0\right)$$
where:
- $F_t$ is the frozen Candidate F solar irradiance forecast ($\text{W/m}^2$),
- $Y_t$ is the ground-truth observed solar irradiance ($\text{W/m}^2$),
- $\text{clearsky}_t$ is the clear-sky GHI ($\text{W/m}^2$).

This target represents the fraction of clear-sky irradiance lost due to forecast overprediction (downside risk). When the forecast is accurate or conservative ($Y_t \ge F_t$), $s_t = 0$. When severe cloud attenuation occurs unexpectedly, $s_t > 0$.

### 3.2 Feature Availability Audit
All 38 features are verified to be strictly available at forecast issuance ($T=0$):
- Horizon and temporal features: `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`.
- Clear-sky and NWP inputs: `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`.
- Historical causal observation statistics: `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`.
- Cloud water & terrain context: `lwp_latest`, `iwp_latest`, `lwp_x_cloud`, `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`, `u700`, `v700`, `elevation_x_cloud_frac`.

**Prohibited Features:** Realized solar, realized residuals, future SOC, future diesel, optimizer decisions, and all 2024 data.

---

## 4. Architecture Selection & Low-Capacity Constraints

Four candidate architectures were defined and evaluated strictly on pre-2024 training (2020–2021) and validation (2022) data before locking pre-registration:

| Candidate Architecture | Hidden Layers | Parameter Count | Val MAE (2022) | Val MSE (2022) | Val $R^2$ (2022) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Arch-1 (Tiny)** | **(16,)** | **641** | **0.13718** | **0.03376** | **0.4252** |
| Arch-2 (Small) | (32,) | 1,281 | 0.14000 | 0.03413 | 0.4188 |
| Arch-3 (2-Layer) | (32, 16) | 1,793 | 0.13980 | 0.03462 | 0.4106 |
| Arch-4 (Wider) | (64, 32) | 4,609 | 0.14338 | 0.03898 | 0.3363 |

### Selected Architecture
`Arch-1 (16,)` was selected because it achieved the lowest Validation MAE (0.13718), lowest MSE (0.03376), and highest $R^2$ (0.4252) while maintaining the minimal model capacity (only 641 parameters).

### Model Hyperparameters & Preprocessing
- Preprocessing: `SimpleImputer(strategy='median')` fit on 2020-2021 Train data followed by `StandardScaler()`.
- Layer topology: Input (38) $\to$ Dense(16, ReLU) $\to$ Dense(1, Linear)
- Regularization: L2 penalty $\alpha = 10^{-3}$
- Optimizer: Adam ($\text{lr}_0 = 10^{-3}$, batch size $= 64$)
- Early stopping: `early_stopping=True`, `validation_fraction=0.15`, `n_iter_no_change=15`
- Deterministic Seed: `seed = 42`

---

## 5. Simple Non-NN Comparative Baseline

To ensure the NN complexity is justified, a simple linear model is trained on the exact same 38 features and target:
- **Model:** `Ridge(alpha=10.0, random_state=42)`
- **Validation Metrics (2022):** MAE $= 0.14537$, MSE $= 0.03584$
- **Blind Test Metrics (2023):** MAE $= 0.14928$, MSE $= 0.03796$ (vs MLP MAE $= 0.13857$, MSE $= 0.03386$).

---

## 6. Calibration & Adaptive-q Mapping

### 6.1 Calibration Procedure
Isotonic Regression is fit on the 2022 validation set:
$$\hat{s}_t^{\text{cal}} = \text{IsotonicRegression}(\hat{s}_t, s_{\text{val}})$$
ensuring monotonic calibration between predicted and observed shortfall.

### 6.2 Adaptive-q Mapping Function
Pre-registered parameter bounds established on 2022 validation data:
- Lower bound (safety anchor): $q_{\min} = 0.10$
- Upper bound (maximum relaxation): $q_{\max} = 0.25$
- Low-risk threshold: $s_{\text{low}} = 0.05$
- High-risk threshold: $s_{\text{high}} = 0.18$

$$\alpha_t = \text{clip}\left(\frac{\hat{s}_t^{\text{cal}} - s_{\text{low}}}{s_{\text{high}} - s_{\text{low}}}, 0.0, 1.0\right)$$
$$q_t = q_{\max} - (q_{\max} - q_{\min}) \cdot \alpha_t$$

**Safety Fallback:** If $\text{solar\_elevation}_t \le 0$ or $\text{clearsky}_t \le 0$, $q_t = 0.10$.  
**Safety Invariant:** $0.10 \le q_t \le 0.25$ strictly enforced across all timesteps.

### 6.3 Solar Planning Trajectory Formula
$$p_{\text{solar}, t}(q_t) = q_{10, t}^{\text{power}} + \frac{q_t - 0.10}{0.50 - 0.10} \cdot \max\left(0, q_{50, t}^{\text{power}} - q_{10, t}^{\text{power}}\right)$$
If $q_{50, t}^{\text{power}} \le q_{10, t}^{\text{power}}$, $p_{\text{solar}, t} = q_{10, t}^{\text{power}}$.

---

## 7. Replay Accounting Fix (L2-EXP-10 Resolution)

In L2-EXP-10, Arm F recorded 604 hourly instances where replay SOC exceeded 95% because the dispatch plan populated `battery_charge` with the unconstrained 50 kW charge capacity envelope variable instead of the central scenario planned charge.

For L2-EXP-11:
1. **Arm C (L2-EXP-10 Reference):** `plan.battery_charge` is populated with `sol[c_offset + t*K + 4]` (the central scenario planned charge, which is bounded by the MILP's battery capacity constraint).
2. **Arm D (NN Adaptive-q):** Uses the canonical GAP19 optimizer interface, where `plan.battery_charge` is constrained by $e_t \le \text{max\_e\_wh} = 190,000\text{ Wh}$.
3. **Hard Replay Constraint:** Replay strictly enforces:
$$20.0\% \le \text{SOC}_t \le 95.0\%$$
Any floor or ceiling violation automatically renders the run invalid.

---

## 8. Fixed Reference Ladder & Experimental Scope

Evaluation is conducted across all 173 held-out 2024 odd origins (123 NORMAL route, 50 EMERGENCY route):
- **Arm A:** Candidate F Point Forecast Control
- **Arm B:** Static $q_{10}$ Conservative Lower Bound (Primary Reliability Benchmark)
- **Arm C:** L2-EXP-10 Arm F (Corrected Priority Hierarchy + Replay Accounting Fix)
- **Arm D:** NN Adaptive-q (New Proposed Method)
- **Arm E:** Perfect Foresight Diagnostic Upper Bound

---

## 9. Primary Acceptance Gates & Governance Decision Rules

Arm D is classified as **`PROMISING`** if and only if ALL of the following gates pass:
1. **Gate 1 (SOC Floor):** Zero SOC floor violations ($< 20\%$).
2. **Gate 2 (SOC Ceiling):** Zero SOC upper-bound violations ($> 95\%$).
3. **Gate 3 (Replay Accounting):** Zero physical energy accounting or non-anticipativity violations.
4. **Gate 4 (Unmet Critical Load):** Realized unmet critical load:
$$D_{\text{unmet}} \le B_{\text{unmet}} + 10\% = 64,005.6 \times 1.10 = 70,406.2\text{ Wh}$$
5. **Gate 5 (Reliability):** Realized critical reliability is statistically consistent with Arm B.
6. **Gate 6 (Curtailment):** Meaningful reduction in solar curtailment vs Arm B ($D_{\text{curt}} < B_{\text{curt}}$).
7. **Gate 7 (Diesel Fuel):** Diesel consumption does not materially increase vs Arm B ($D_{\text{fuel}} \le B_{\text{fuel}} + 1\%$).

If Gate 4 fails, or if any safety/accounting violation occurs, Arm D must be declared **`NO-GO`**.
Under all circumstances: **NO PRODUCTION PROMOTION IS AUTHORIZED**.
