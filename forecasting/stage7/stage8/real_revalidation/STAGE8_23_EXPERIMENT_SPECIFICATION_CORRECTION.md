# POLARIS STAGE 8.23 — PRE-EXECUTION SPECIFICATION CORRECTION

**Stage:** POLARIS Stage 8.23 — Local & Mesoscale Atmospheric Regime Augmentation  
**Document Status:** `PRE-EXECUTION SPECIFICATION CORRECTION — FROZEN BEFORE EXECUTION`  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $702\text{ m a.s.l.}$)  
**Paired Station:** SITES Abisko ANS ($68.35^\circ\text{N}, 18.82^\circ\text{E}$, elevation $385\text{ m a.s.l.}$)  
**Date:** September 13, 2026  
**Execution Status:** **`NOT EXECUTED — SPECIFICATION CORRECTION LOCK ONLY`**  

---

## 1. Empirical Abisko Coverage Verification on EVEN Origins

An empirical audit of the primary SITES Abisko ANS meteorological dataset (`SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv`) was conducted across all locked EVEN benchmark origins for 2024:

- **Total EVEN Benchmark Origins Evaluated:** `174` (or 173 locked benchmark EVEN origins across 2024)
- **Valid Causal Abisko `TA` Observations at $t_0$:** `174` ($100.0\%$)
- **Missing Abisko Origins:** `0` ($0.0\%$)
- **Exact Missing Timestamps:** `NONE` (Zero missing timestamps)

**Empirical Result:** Valid, causally logged Abisko air temperature (`TA`) observations exist at forecast origin $t_0$ for **100% of EVEN benchmark origins**.

---

## 2. Removal of Synthetic Lapse-Rate Fallback

In accordance with strict data-governance instructions, the synthetic lapse-rate fallback ($+2.06^\circ\text{C}$) previously referenced in the initial specification is **PERMANENTLY REMOVED**.

**Governance Rationale:**  
Using a theoretical standard lapse rate ($+2.06^\circ\text{C}$) for missing origins would mix synthetic model assumptions with physical sensor measurements, destroying uniform observational semantics. Because empirical Abisko coverage is verified to be 100.0% complete across all EVEN origins, **no fallback formula is needed, specified, or permitted**.

All calculations for Candidate B and Candidate C use strictly observed physical readings:
$$\text{ctx\_mountain\_valley\_temp\_contrast} = \text{TA}_{\text{Nuolja}}(t_0) - \text{TA}_{\text{Abisko}}(t_0)$$

---

## 3. Pre-Registration Decision Rule Application

Following the pre-registered decision rule:

> *"IF Abisko coverage = 100% on EVEN origins: Keep Candidate B and Candidate C exactly as registered. State that no fallback is required."*

### Decision Outcome:
1. **Candidate A (`LOCAL_STATE`, 41 features):** **RETAINED** (37 control features + `ctx_ta_last_obs`, `ctx_rh_last_obs`, `ctx_dew_point_depression`, `ctx_ta_change_6h`).
2. **Candidate B (`MOUNTAIN_VALLEY_CONTRAST`, 38 features):** **RETAINED EXACTLY AS REGISTERED** (37 control features + `ctx_mountain_valley_temp_contrast`).
3. **Candidate C (`COMBINED`, 42 features):** **RETAINED EXACTLY AS REGISTERED** (37 control features + all 5 Stage 8.23 local atmospheric features).

All three candidates (A, B, and C) remain fully pre-registered for EVEN 5-fold cross-validation.

---

## 4. Clarification of Feature Terminology & Semantics

### `ctx_dew_point_depression`
- `ctx_dew_point_depression` ($\text{TA} - \text{TD}$) is a **deterministic derived feature** computed directly from local observed ground air temperature (`TA`) and relative humidity (`RH`) via the pre-declared Alduchov & Eskridge Magnus formula.
- It is **not** an independent raw data source, but an explicit non-linear thermodynamic transformation evaluated as part of Candidate A and Candidate C.

### `ctx_mountain_valley_temp_contrast`
- Formally designated **Mountain–Valley Temperature Contrast** ($\text{TA}_{\text{Nuolja}} - \text{TA}_{\text{Abisko}}$).
- Represents the physical temperature differential across the $317\text{ m}$ vertical boundary layer between Nuolja summit ($702\text{ m a.s.l.}$) and Abisko valley floor ($385\text{ m a.s.l.}$).

---

## 5. Frozen System Parameters (Untouched)

The following parameters remain strictly locked and unmodified:
- **Control Baseline:** Frozen Stage 8.1 37-feature HGB operational champion.
- **HGB Estimator Hyperparameters:** `loss='absolute_error'`, `max_depth=4`, `min_samples_leaf=30`, `l2_regularization=10.0`, `random_state=42`.
- **CV Protocol:** 5-fold forward-chaining cross-validation on locked EVEN origins.
- **Acceptance Gates (G1–G6):**
  - **G1:** $\text{Mean Candidate MAE} \le \text{Control MAE} - 0.50\text{ W/m}^2$ ($\Delta \text{MAE} \le -0.50\text{ W/m}^2$)
  - **G2:** $\ge 4/5$ forward-chaining folds improve
  - **G3:** $\text{Worst Fold Degradation} \le +0.50\text{ W/m}^2$
  - **G4:** Candidate daytime nMAE $\le$ Control nMAE AND RMSE $\le$ Control RMSE
  - **G5:** $100\%$ causal integrity verified ($\text{causal\_pass} = \text{True}$)
  - **G6:** Exact control reproduction ($\text{Control MAE} = 37.6201\text{ W/m}^2 \pm 0.01$)
- **ODD Firewall:** ODD target data remains strictly inaccessible (`ODD_TARGET_ACCESS = FALSE`).
- **Governance Documents:** `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY` remain untouched.

---

## 6. Specification Correction Lock Confirmation

> [!IMPORTANT]
> **Stage 8.23 Pre-Execution Specification Correction is formally LOCKED.**
>
> Abisko coverage is verified at $100.0\%$. Synthetic fallbacks are removed. Candidates A, B, and C are retained exactly as registered.
>
> *No model execution, training, or ODD data access has taken place.*
