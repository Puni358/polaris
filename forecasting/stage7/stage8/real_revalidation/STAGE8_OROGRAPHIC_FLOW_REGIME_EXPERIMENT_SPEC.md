# POLARIS STAGE 8 — OROGRAPHIC FLOW REGIME EXPERIMENT PRE-REGISTRATION SPECIFICATION

> [!IMPORTANT]
> **GOVERNANCE STATUS: PRE-REGISTERED EXPERIMENT SPECIFICATION ONLY**  
> - **This experiment has NOT been executed yet.**  
> - **ODD benchmark dataset remains 100% untouched.**  
> - **Stage 8.1 37-feature HGB model remains the frozen operational champion (ODD daytime nMAE 28.0688%).**  
> - **No modifications to POLARIS_MASTER_HANDOFF.md or POLARIS_STAGE8_ROUTE_REGISTRY.**

---

## 1. Executive Summary & Objective

This document pre-registers the governed experimental protocol for **POLARIS Stage 8.24: Orographic Flow Regime Expansion**.

Following the scientific pre-experiment audit ([`STAGE8_OROGRAPHIC_CANDIDATE_PREEXPERIMENT_AUDIT.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_OROGRAPHIC_CANDIDATE_PREEXPERIMENT_AUDIT.md)), this experiment tests whether explicitly modeling the Scandes mountain barrier-normal flow coordinate ($U_\perp$) and the mountain Froude flow-regime indicator ($Fr$) provides incremental predictive skill beyond the frozen Stage 8.1 37-feature operational champion.

---

## 2. Hypothesis & Physical Rationale

### Core Hypothesis
> *"POLARIS Stage 8.1 represents steering winds using raw Cartesian components ($u_{700}, v_{700}$). By explicitly transforming 700 hPa winds into a Scandes barrier-normal inflow coordinate ($U_\perp$) and non-dimensional Froude flow-regime indicator ($Fr$), the model can discriminate between flow blocking (trapped valley cloudiness) and flow over-topping (lee-side mountain wave cloudiness), reducing short-wave irradiance ($SW\_IN$) forecast errors at SITES Nuolja."*

### Physical Interpretation
- **`ctx_u_perp`:** $U_\perp$ explicitly represents wind relative to the physically defined Scandes barrier orientation ($290^\circ$ inflow axis), providing a compact and physically interpretable barrier-normal flow coordinate. Positive $U_\perp$ indicates flow from the Norwegian Sea impinging on Mount Nuolja; negative $U_\perp$ indicates downslope Föhn flow.
- **`ctx_mountain_froude`:** $Fr = \frac{U_\perp}{N \cdot h}$ is a physically motivated flow-regime indicator whose usefulness must be empirically tested for Nuolja. $Fr < 1.0$ indicates energy-deficient flow trapped in Torneträsk valley ($341\text{ m}$ elevation), while $Fr \ge 1.0$ indicates ridge over-topping.

---

## 3. Reference Baselines & Model Definitions

### Reproducible Operational Baseline (ODD Benchmark Reference)
- **Operational Champion:** Stage 8.1 37-feature HGB
- **ODD Daytime nMAE:** **`28.0688%`**
- **ODD MAE:** **`36.188657 W/m²`**
- **ODD RMSE:** **`64.219495 W/m²`**
- **ODD Mean Bias:** **`+1.439399 W/m²`**

### EVEN Validation Benchmark Control
- **Control Baseline:** Stage 8.1 37-feature HGB on 173 EVEN origins
- **Reproduction MAE Target:** **`37.6201 W/m²`**

---

## 4. Candidate Feature Definitions (39 Features Total)

The candidate model extends the Stage 8.1 37-feature set by adding **2 new orographic flow features**:

| Feature Name | Mathematical Formula | Physical Description | Data Source & Timestamps |
| :--- | :--- | :--- | :--- |
| **`ctx_u_perp`** | $U_\perp = -0.9397 \cdot u_{700} + 0.3420 \cdot v_{700}$ | Scandes barrier-normal wind component ($\text{m/s}$). Positive $= 290^\circ$ maritime inflow. | MEPS 700 hPa $u, v$ winds at valid time $t_0 + h$. |
| **`ctx_mountain_froude`** | $Fr = \frac{U_\perp}{N \cdot h}$ | Non-dimensional mountain Froude number flow-regime indicator. | Hydrostatically derived from MEPS $P_{\text{sfc}} \to 700\text{ hPa}$ profiles; $h = 828\text{ m}$. |

### Detailed Parameter Calculation Specifications:
1. **$U_\perp$ Rotation Vector:** Unit vector along $290^\circ$ inflow axis: $\hat{n} = (\sin 290^\circ, \cos 290^\circ) = (-0.9397, +0.3420)$.
2. **Virtual Temperature Corrected Stability ($N$):** $N = \sqrt{\frac{g}{\theta_v} \frac{\partial \theta_v}{\partial z}}$, where $\theta_v = T \cdot \left( \frac{1000}{P} \right)^{0.286} \cdot (1 + 0.61 q)$.
3. **Layer Range for $N$:** Hydrostatically integrated over the $P_{\text{sfc}} \to 700\text{ hPa}$ layer ($z \approx 341\text{ m} \to 3,000\text{ m}$).
4. **Effective Mountain Relief ($h$):** Fixed at $h = z_{\text{summit}} - z_{\text{valley}} = 1,169\text{ m} - 341\text{ m} = \mathbf{828\text{ m}}$.

---

## 5. Model Architecture & Hyperparameters

Both Control (37 features) and Candidate (39 features) use the exact frozen Stage 8.1 HistGradientBoostingRegressor architecture:

```python
HistGradientBoostingRegressor(
    loss="absolute_error",
    max_depth=4,
    min_samples_leaf=30,
    l2_regularization=10.0,
    random_state=42,
)
```

---

## 6. Pre-Run Governance Checklist (10 Mandatory Checks)

Before model training, the experiment execution script must verify all 10 governance conditions:

- [ ] **Check 1:** 347-origin benchmark dataset remains strictly unchanged.
- [ ] **Check 2:** EVEN (173 origins) / ODD (174 origins) split remains strictly unchanged.
- [ ] **Check 3:** Zero access to ODD target values (`actual_SW_IN`).
- [ ] **Check 4:** All feature timestamps are 100% causal (available at or before $t_0 = 00:00\text{ UTC}$).
- [ ] **Check 5:** Brunt–Väisälä stability $N$ calculation verified over $P_{\text{sfc}} \to 700\text{ hPa}$ layer with virtual temperature correction.
- [ ] **Check 6:** Effective mountain relief height $h$ verified at $828\text{ m}$.
- [ ] **Check 7:** $U_\perp$ barrier-normal formula verified ($-0.9397 u_{700} + 0.3420 v_{700}$).
- [ ] **Check 8:** No future weather values or future forecast steps used.
- [ ] **Check 9:** No target leakage or feature column duplication.
- [ ] **Check 10:** Independent control reproduction matches exact known EVEN baseline ($37.6201\text{ W/m}^2$).

---

## 7. EVEN 5-Fold Cross-Validation Protocol

1. **Origins Subset:** Locked EVEN origins (173 forecast origins in 2024).
2. **Split Method:** Deterministic 5-fold forward-chaining split on sorted EVEN origins.
3. **Daytime Mask:** `is_daytime == True` (`solar_elevation > 0°`).
4. **Stage 4 Residual Alignment:** Fit Stage 4 physics parameters on training fold; apply to validation fold to compute Stage 4 residuals ($y - \text{pred\_stage4}$).
5. **Model Evaluation:** Train HGB on training residuals; predict validation residuals; evaluate total MAE on validation daytime points.

---

## 8. Acceptance Gates (G1 – G6) & Stop Conditions

The candidate must pass **ALL SIX GATES** on EVEN validation to be considered for promotion:

| Gate ID | Criterion Name | Strict Pass Requirement |
| :--- | :--- | :--- |
| **G1** | **MAE Improvement Margin** | $\text{Candidate MAE} \le \text{Control MAE} - \mathbf{0.50\text{ W/m}^2}$ |
| **G2** | **Fold Consistency** | At least **4 out of 5** forward-chaining folds improve ($\text{improving\_folds} \ge 4$) |
| **G3** | **Worst-Fold Degradation** | Maximum worst-fold MAE degradation $\le \mathbf{+0.50\text{ W/m}^2}$ |
| **G4** | **nMAE & RMSE Non-Degradation** | $\text{Candidate nMAE} \le \text{Control nMAE}$ AND $\text{Candidate RMSE} \le \text{Control RMSE}$ |
| **G5** | **Causal Integrity** | 100% causal feature availability for all evaluated forecast tuples |
| **G6** | **Control Reproduction** | Exact control reproduction ($\text{Control MAE} == 37.6201\text{ W/m}^2$) |

> [!CAUTION]
> **GOVERNED STOP CONDITION:**  
> If ANY gate G1–G6 fails on EVEN validation:  
> 1. **STOP IMMEDIATELY.** Do **NOT** execute ODD evaluation.  
> 2. Candidate freeze protocol takes effect.  
> 3. Route is classified as **`REJECTED_ON_EVEN`** and closed.  
> 4. Stage 8.1 37-feature model remains the operational champion.

---

## 9. ODD Evaluation Specification (Authorized ONLY IF G1–G6 Pass)

If and only if Candidate passes all six EVEN gates G1–G6, ODD evaluation is authorized under the following protocol:
- **Model State:** Fit 39-feature HGB model on 100% of EVEN origins; freeze model weights.
- **ODD Data:** Predict on 173 ODD origins ($4,152$ forecast lead hours).
- **Night Mask:** Causal night zeroing (`solar_elevation <= 0°`).
- **Metrics Computed:** Daytime MAE, nMAE%, RMSE, Bias, and Night MAE.
- **Confidence Intervals:** 10,000 origin-level bootstrap iterations (`random_state=42`).

---

## Final Governance Statement

- **Pre-Registration Specification Completed.**
- **Route Identifier:** STAGE 8.24 (Orographic Flow Regime)
- **This experiment has NOT been executed.**
- **ODD dataset remains 100% untouched.**
- **Stage 8.1 37-feature HGB model remains operational champion.**
