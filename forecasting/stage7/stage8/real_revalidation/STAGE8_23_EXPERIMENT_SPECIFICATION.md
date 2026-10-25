# POLARIS STAGE 8.23 — GOVERNED EVEN-ONLY EXPERIMENT SPECIFICATION

**Stage:** POLARIS Stage 8.23 — Local & Mesoscale Atmospheric Regime Augmentation  
**Document Status:** `PRE-REGISTERED EXPERIMENT SPECIFICATION — FROZEN BEFORE EXECUTION`  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $702\text{ m a.s.l.}$)  
**Paired Station:** SITES Abisko ANS ($68.35^\circ\text{N}, 18.82^\circ\text{E}$, elevation $385\text{ m a.s.l.}$)  
**Date:** September 13, 2026  
**Execution Status:** **`NOT EXECUTED — SPECIFICATION LOCK ONLY`**  

---

## 1. Objective

The primary objective of Stage 8.23 is to test whether incorporating direct, causally available **local ground boundary-layer observations** and **mountain–valley thermal contrast indicators** at forecast origin $t_0$ provides incremental, non-redundant predictive power beyond the frozen **Stage 8.1 37-Feature Operational Champion**.

The empirical data feasibility audit ([`STAGE8_23_EMPIRICAL_DATA_FEASIBILITY_AUDIT.md`](file:///home/punith-bs/01polaris%20(Copy)/stage7/stage8/real_revalidation/STAGE8_23_EMPIRICAL_DATA_FEASIBILITY_AUDIT.md)) verified that direct ground temperature (`TA`), relative humidity (`RH`), dew-point depression ($\text{TA} - \text{TD}$), 6-hour thermal trend ($\Delta \text{TA}_{6h}$), and mountain–valley temperature contrast ($\text{TA}_{\text{Nuolja}} - \text{TA}_{\text{Abisko}}$) at $t \le t_0$ are 100% constructible, 100% causal, and represent a **genuinely novel information axis** absent from Stage 8.1.

---

## 2. Frozen Control Baseline

All candidates in Stage 8.23 are evaluated strictly against the frozen **Stage 8.1 Operational Champion**:
- **Baseline Feature Count:** 37 features (target context, solar geometry, clearsky decomposition, MEPS cloud fraction, MEPS 2m T/RH, MEPS LWP/IWP, DEM terrain horizon, $U_{700}/V_{700}$ steering winds).
- **Model Estimator:** `sklearn.ensemble.HistGradientBoostingRegressor`
- **Locked Hyperparameters:**
  ```python
  HistGradientBoostingRegressor(
      loss='absolute_error',
      max_depth=4,
      min_samples_leaf=30,
      l2_regularization=10.0,
      random_state=42
  )
  ```
- **Hyperparameter Policy:** **FROZEN**. Hyperparameter tuning or structural model alterations are strictly prohibited.

---

## 3. Pre-Registered Candidate Feature Sets

Three candidate feature sets are pre-registered for evaluation against the 37-feature control:

### Candidate A — `LOCAL_STATE` (41 Features)
Includes the frozen 37 control features plus 4 local ground boundary-layer features:
1. `ctx_ta_last_obs`
2. `ctx_rh_last_obs`
3. `ctx_dew_point_depression`
4. `ctx_ta_change_6h`

### Candidate B — `MOUNTAIN_VALLEY_CONTRAST` (38 Features)
Includes the frozen 37 control features plus 1 local thermal gradient feature:
1. `ctx_mountain_valley_temp_contrast`

### Candidate C — `COMBINED` (42 Features)
Includes the frozen 37 control features plus all 5 Stage 8.23 local atmospheric features:
1. `ctx_ta_last_obs`
2. `ctx_rh_last_obs`
3. `ctx_dew_point_depression`
4. `ctx_ta_change_6h`
5. `ctx_mountain_valley_temp_contrast`

*Governance Rule: No additional features may be added. No control features may be removed.*

---

## 4. Exact Mathematical Feature Definitions & Psychrometric Formulas

All features must be computed deterministically using the following exact formulas:

### 1. `ctx_ta_last_obs`
$$\text{ctx\_ta\_last\_obs} = \text{TA}(t_0)$$
Latest completed local air temperature observation at SITES Nuolja ($702\text{ m a.s.l.}$) recorded at timestamp $t_0$.

### 2. `ctx_rh_last_obs`
$$\text{ctx\_rh\_last\_obs} = \text{RH}(t_0)$$
Latest completed local relative humidity observation at SITES Nuolja recorded at timestamp $t_0$ (expressed as a percentage, $0 \dots 100\%$).

### 3. `ctx_dew_point_depression`
$$\text{ctx\_dew\_point\_depression} = \text{TA}(t_0) - \text{TD}(t_0)$$
Dew-point depression at $t_0$, where dew-point temperature $\text{TD}(t_0)$ is computed deterministically using the **Alduchov & Eskridge (1996) Magnus approximation**:
$$\gamma(T, \text{RH}) = \frac{a \cdot T}{b + T} + \ln\left(\frac{\text{RH}}{100}\right)$$
$$\text{TD}(T, \text{RH}) = \frac{b \cdot \gamma(T, \text{RH})}{a - \gamma(T, \text{RH})}$$
**Pre-declared Psychrometric Constants:**
- $a = 17.625$
- $b = 243.04^\circ\text{C}$  
*(Valid over $-40^\circ\text{C} \le T \le +50^\circ\text{C}$ with relative error $< 0.1\%$).*

### 4. `ctx_ta_change_6h`
$$\text{ctx\_ta\_change\_6h} = \text{TA}(t_0) - \text{TA}(t_0 - 6\text{h})$$
6-hour thermal trend prior to origin $t_0$. Both $\text{TA}(t_0)$ and $\text{TA}(t_0 - 6\text{h})$ must be completed historical ground observations. No future interpolation or missing-data fill using $t > t_0$ is permitted.

### 5. `ctx_mountain_valley_temp_contrast`
$$\text{ctx\_mountain\_valley\_temp\_contrast} = \text{TA}_{\text{Nuolja}}(t_0) - \text{TA}_{\text{Abisko}}(t_0)$$
Local vertical thermal contrast between SITES Nuolja summit ($702\text{ m a.s.l.}$) and SITES Abisko ANS valley floor ($385\text{ m a.s.l.}$) at timestamp $t_0$.  
*Terminology Rule: Formally designated "Mountain–Valley Temperature Contrast" to cover both surface inversion states ($\Delta T > 0^\circ\text{C}$) and well-mixed adiabatic lapse rate states ($\Delta T \approx -2.06^\circ\text{C}$).*

---

## 5. Timestamp Semantics, Causality, & Missing-Data Policy

### Period-Ending Hourly Semantics
- In accordance with SITES L2 logging specifications, a timestamp `YYYY-MM-DD HH:00:00` represents the arithmetic mean of readings collected during the 60 minutes leading up to `HH:00:00`.
- For forecast origin $t_0 = 00:00\text{ UTC}$, the observation $\text{TA}(t_0)$ represents readings from $23:00\text{ UTC}$ to $00:00\text{ UTC}$, completed exactly at $00:00\text{ UTC}$.

### Strict Causal Rule
$$\text{observation\_timestamp} \le t_0$$
No observation from lead hours $H1 \dots H24$ ($t > t_0$) may enter feature construction. Local logger telemetry streams within $\le 5\text{ minutes}$ of logging, ensuring complete operational availability before MEPS forecast availability on $D-1$ 18Z.

### Pre-Declared Missing-Data Policy for Abisko
- In the event that SITES Abisko ANS valley data is missing for a specific origin timestamp $t_0$, `ctx_mountain_valley_temp_contrast` shall be filled using the deterministic standard lapse rate fallback:
  $$\text{ctx\_mountain\_valley\_temp\_contrast}_{\text{fallback}} = -\gamma_{\text{std}} \cdot \Delta z = -(-6.5^\circ\text{C/km}) \cdot (0.317\text{ km}) = +2.06^\circ\text{C}$$
- **Benchmark Denominator Rule:** Zero origins shall be dropped. The benchmark denominator remains locked at 173 EVEN origins (347 total origins).

---

## 6. Evaluation Protocol & Pre-Registered Acceptance Gates

### EVEN Cross-Validation Protocol
- **Population:** 173 EVEN-indexed benchmark origins across 2024.
- **Fold Structure:** 5 forward-chaining temporal folds (identical to Stage 8.1 split).
- **Candidate Evaluation:** Candidates A, B, and C must be trained and evaluated under the exact same 5 folds.

### Pre-Registered Acceptance Gates (Applied Independently to A, B, and C)

| Gate ID | Description | Pre-Registered Pass Criterion |
| :--- | :--- | :--- |
| **G1** | MAE Improvement Margin | $\text{Mean Candidate MAE} \le \text{Control MAE} - 0.50\text{ W/m}^2$ ($\Delta \text{MAE} \le -0.50\text{ W/m}^2$) |
| **G2** | Fold Consistency | $\ge 4 / 5$ forward-chaining folds improve ($\Delta \text{MAE}_{\text{fold}} < 0$) |
| **G3** | Worst-Fold Degradation | $\text{Worst Fold Degradation} \le +0.50\text{ W/m}^2$ |
| **G4** | nMAE & RMSE Non-Degradation | $\text{Candidate Daytime nMAE} \le \text{Control nMAE}$ AND $\text{Candidate RMSE} \le \text{Control RMSE}$ |
| **G5** | Causal Integrity | $100\%$ causal integrity verified ($\text{causal\_pass} = \text{True}$) |
| **G6** | Exact Control Reproduction | $\text{Control MAE} = 37.6201\text{ W/m}^2 \pm 0.01$ |

*Failure Rule: If any candidate fails any gate G1–G6 on EVEN validation, that candidate is classified as `REJECTED ON EVEN` and must NOT proceed to ODD evaluation.*

---

## 7. Governance Rules & ODD Firewall

1. **ODD Firewall:** ODD target data ($SW_{IN}$) remains strictly inaccessible during EVEN validation (`ODD_TARGET_ACCESS = FALSE`).
2. **Candidate Freeze:** No hyperparameter tuning, feature pruning, or post-hoc model modifications based on EVEN fold results are permitted.
3. **Multi-Candidate Promotion Policy:**
   - ODD results must **NOT** be used to select between Candidates A, B, and C.
   - If multiple candidates pass all 6 EVEN acceptance gates (G1–G6), **all passing candidates shall be frozen and evaluated on ODD**.
   - If no candidate passes all EVEN gates, execution stops (`ODD_RUN = FALSE`, `FINAL_VERDICT = REJECTED_ON_EVEN`).
4. **Primary Evaluation Metric:** Daytime nMAE ($\%$, relative to mean daytime $SW_{IN}$). MAPE is strictly prohibited.
5. **Statistical Significance:** If ODD evaluation occurs, 10,000 origin-level bootstrap resamples (seed 42) shall be computed against the Stage 8.1 control.
6. **Master Handoff & Registry Rule:** `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY` shall NOT be modified during experiment execution. Promotion is a separate governance action following independent verification.

---

## 8. Specification Lock Confirmation

> [!IMPORTANT]
> **Stage 8.23 Experiment Specification is formally LOCKED.**
>
> All candidate feature definitions, psychrometric formulas, missing-data policies, cross-validation folds, and acceptance gates G1–G6 are frozen.
>
> *No model execution or data extraction has taken place.*
