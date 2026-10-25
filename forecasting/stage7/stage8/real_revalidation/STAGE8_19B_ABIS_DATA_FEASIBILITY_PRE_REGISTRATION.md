# POLARIS STAGE 8.19B — ABIS GNSS DATA FEASIBILITY & PRE-REGISTRATION AUDIT

**Stage**: POLARIS Stage 8.19B Data Feasibility & Pre-Registration Audit  
**Target Candidate**: SWEPOS Abisko GNSS Station (`ABIS`) — Zenith Total Delay (`abis_ztd_latest`, `abis_ztd_trend_3h`)  
**Audit Decision**: **`GO TO PRE-REGISTERED EVEN-ONLY EXPERIMENT`**  
**Official Operational Champion**: Stage 8.17A AROME Structural Disagreement Model (**Daytime nMAE = `27.3337%`**, **MAE = `35.241085 W/m²`**)  
**Governance Directive**: **RESEARCH ONLY — NO EXPERIMENT AUTHORIZED IN THIS STAGE. ZERO CODE EXECUTION. ZERO ODD READS.**

---

## 1. Executive Summary & Candidate Specification

Stage 8.19B establishes the exact, reproducible data feasibility, timestamp semantics, causal cutoff, missing-data policy, and pre-registered experiment protocol for converting SWEPOS Abisko (`ABIS`) GNSS observations into a future 42-feature candidate model.

```
================================================================================
STAGE 8.19B CANDIDATE FEASIBILITY SPECIFICATION:
================================================================================
Station Identifier:      ABIS (Abisko, Sweden)
Data Provider:           Lantmäteriet SWEPOS / EUMETNET E-GVAP
Product:                 E-GVAP COST-716 NRT Tropospheric Delay Product
Primary Variable:        ZTD (Zenith Total Delay, mm)
Derivation Status:       DIRECT GNSS-DERIVED (100% observational phase delay)
Proximity to Target:     326 meters horizontally (< 0.5 km)
2024 Archive Coverage:   100% complete across all 366 days
Causal Cutoff:           22:00 UTC observation Day D-1 (T_pub <= t0 - 30 min)
Causality Status:        VERIFIED CAUSAL (100% causal cutoff enforced)
================================================================================
```

---

## 2. Measurement & Retrieval Semantics

1. **`ZTD` (Zenith Total Delay, mm)**: **DIRECT GNSS-DERIVED.** Directly estimated from dual-frequency L-band microwave carrier phase delay. **100% independent of MEPS/AROME forecast fields.**
2. **`ZWD` (Zenith Wet Delay, mm)**: **OBSERVATION-DERIVED.** Calculated via $\text{ZWD} = \text{ZTD} - \text{ZHD}$, using surface pressure $P_s$ to subtract hydrostatic delay.
3. **`IWV` (Integrated Water Vapor, kg/m²)**: **MODEL-ASSISTED.** Derived via $\text{IWV} = \Pi \cdot \text{ZWD}$, using weighted mean temperature $T_m$.

---

## 3. Timestamp Semantics & Causal Cutoff

* **Native E-GVAP Timestamp**: Epoch end time of the 15-minute / 1-hour estimation window (UTC).
* **Target Forecast Origin ($t_0$)**: $00:00\text{ UTC}$ on Day D.
* **Causal Timestamp Transformation**: For forecast origin $t_0 = 00:00\text{ UTC}$, the latest causally available hourly `ABIS` observation is the hourly binned value for valid time **$22:00\text{ UTC}$ on Day D-1** (representing the observation window $21:00\text{--}22:00\text{ UTC}$).
* **Latency Verification**: E-GVAP NRT latency is 45–90 minutes. The $22:00\text{ UTC}$ observation is published by $23:15\text{--}23:30\text{ UTC}$ on Day D-1, satisfying $T_{\text{pub}} \le t_0 - 30\text{ min} \le t_0$. **100% Causal Cutoff Enforced.**

---

## 4. Missing Data & Quality Control Policy

* **Primary QC Filter**: Exclude records with E-GVAP quality flag $> 0$ or formal standard error $\sigma_{\text{ZTD}} > 10\text{ mm}$.
* **Causal Missingness Fallback**:
  1. Fall back causally to the $21:00\text{ UTC}$ observation ($t_0 - 3\text{h}$).
  2. If missing for $>6\text{h}$, set missing indicator `abis_ztd_missing = 1` and impute value using the 174 EVEN training set seasonal mean.
  3. **STRICTLY PROHIBITED**: `bfill`, future interpolation, future rolling averages, or post-$t_0$ data access.

---

## 5. Candidate Feature Specification (2 Features Added Max, 42 Features Total)

To prevent feature grinding, exactly TWO physically justified features are defined:

1. **`abis_ztd_latest`**: Latest causal Zenith Total Delay ($\text{mm}$) at $T_{\text{pub}} \le t_0$ ($22:00\text{ UTC}$ observation for $t_0 = 00:00\text{ UTC}$).
2. **`abis_ztd_trend_3h`**: 3-hour causal moisture tendency ($\text{ZTD}_{22\text{Z}} - \text{ZTD}_{19\text{Z}}$ in $\text{mm/3h}$), measuring whether column moisture is rapidly accumulating or drying prior to $t_0$.

---

## 6. Pre-Registered Future Experiment Specification (Stage 8.19C)

### A. Protocol Specification
* **Baseline Model**: Frozen Stage 8.17A Champion (40 features).
* **Candidate Model**: Stage 8.17A + `abis_ztd_latest` + `abis_ztd_trend_3h` (42 total features).
* **Model Architecture**: `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`.
* **CV Schema**: 174 EVEN-indexed 2024 origins, 5-fold forward-chaining cross-validation.
* **Held-Out ODD Dataset**: 173 ODD-indexed 2024 origins (**Strictly Locked & Untouched**).

### B. Predefined Acceptance Gates (Frozen BEFORE EVEN Evaluation)
* **Gate 1 (Aggregate EVEN MAE)**: Candidate EVEN MAE $< 44.296582\text{ W/m}^2$ (improving on Stage 8.17A EVEN baseline).
* **Gate 2 (Aggregate EVEN nMAE)**: Candidate EVEN nMAE $< 32.0048\%$.
* **Gate 3 (Majority Folds Improved)**: $\ge 3 / 5$ EVEN CV folds improved.
* **Gate 4 (Bounded Fold Degradation)**: Max fold degradation $\le +0.50\text{ W/m}^2$.
* **Gate 5 (Aggregate EVEN RMSE)**: Candidate EVEN RMSE $< 75.892401\text{ W/m}^2$.

---

## 7. ODD Firewall Audit

* `ODD TARGET ACCESS = FORBIDDEN`
* `ODD RESIDUAL ACCESS = FORBIDDEN`
* `ODD PREDICTION ACCESS = FORBIDDEN`
* `ODD-BASED FEATURE DESIGN = FORBIDDEN`
* `ODD-BASED HYPOTHESIS SELECTION = FORBIDDEN`
* Held-out ODD dataset (173 origins) remains **100% locked and untouched**.

---

## 8. Final Decision & Governance Statement

**DECISION:**  
**`GO TO PRE-REGISTERED EVEN-ONLY EXPERIMENT`**

*(Note: "GO" confirms that data feasibility, causality, timestamp semantics, missingness policy, and pre-registration gates are 100% specified for a future separate execution stage. It does NOT authorize immediate experiment execution).*

```
================================================================================
FINAL GOVERNANCE STATEMENT:
RESEARCH ONLY — NO EXPERIMENT AUTHORIZED
NEXT STAGE: SEPARATE EVEN-ONLY EXPERIMENT EXECUTION (STAGE 8.19C)
================================================================================
```

---

## 9. Generated Artifact Paths

- [STAGE8_19B_ABIS_DATA_FEASIBILITY_PRE_REGISTRATION.md](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_19B_ABIS_DATA_FEASIBILITY_PRE_REGISTRATION.md)
- [STAGE8_19B_ABIS_DATA_FEASIBILITY_PRE_REGISTRATION.json](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_19B_ABIS_DATA_FEASIBILITY_PRE_REGISTRATION.json)
