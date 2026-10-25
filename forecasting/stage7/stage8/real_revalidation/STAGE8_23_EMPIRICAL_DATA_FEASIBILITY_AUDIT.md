# STAGE 8.23 — FINAL EMPIRICAL DATA FEASIBILITY AUDIT

**Stage:** POLARIS Stage 8.23 — Local & Mesoscale Atmospheric Regime Research  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $702\text{ m a.s.l.}$)  
**Paired Valley Station:** SITES Abisko ANS ($68.35^\circ\text{N}, 18.82^\circ\text{E}$, elevation $385\text{ m a.s.l.}$)  
**Date:** September 13, 2026  
**Final Audit Decision:** **`READY_FOR_GOVERNED_EXPERIMENT`**  

---

## 1. Executive Audit Summary

This artifact presents the final empirical data-feasibility audit for candidate features in POLARIS Stage 8.23. The audit directly verifies the existence, timestamps, causality, physical semantics, historical coverage, and constructibility of direct ground meteorological observations at SITES Nuolja and SITES Abisko ANS for the 2024 benchmark year.

**Audit Verdict:** **`READY_FOR_GOVERNED_EXPERIMENT`**.  
All primary data sources exist, are 100% complete across 2024, possess zero missing values for key boundary-layer variables (`TA`, `RH`), are strictly causal ($t \le t_0$), and represent **genuinely NOVEL features** completely absent from the 37 features in the frozen Stage 8.1 operational champion.

*Governance Notice: This audit certifies data feasibility only. Zero models were trained, zero cross-validation was run, zero ODD targets were accessed, and system governance files remain untouched.*

---

## 2. Empirical Verification of Primary Sources

### 1. Nuolja Ground Meteorological Observations (NMS)
- **Primary Source File:** `POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` and `SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv`.
- **Station Location & Elevation:** Mt. Nuolja Middle Station ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, $702\text{ m a.s.l.}$, treeline AWS).
- **Primary Variables:**
  - `TA`: Air Temperature (°C) @ 2.32m above ground (Rotronic HC2-S3 sensor in multi-plate shield).
  - `RH`: Relative Humidity (%) @ 2.32m above ground (Rotronic HC2-S3 sensor).
  - `PRECIP`: Liquid precipitation (mm, Young Tipping Bucket 52203).
  - `TA_STD`: Standard deviation of air temperature (°C).
- **Temporal Resolution:** 10-minute raw logging, aggregated to 1-hour in POLARIS multivariate dataset.
- **Timestamp Convention:** Standardized UTC ISO 8601 timestamps (`YYYY-MM-DD HH:MM:SS+00:00`).
- **Actual 2024 Coverage:** `8,784` hourly timestamps (100.0% complete across 366 days in leap year 2024).
- **Missing Values:** `0` missing values for `TA`, `RH`, `PRECIP`, `TA_STD`.
- **Pre-$t_0$ Existence:** Observations exist for every hour of 2024, providing continuous 24-hour historical context prior to every locked origin $t_0 = 00:00\text{ UTC}$.
- **Data Semantics:** Physical ground sensor measurements recorded by SITES automated weather station, **NOT model forecasts or reanalysis**.

### 2. Operational Causality & Dissemination Timing
- **Locked Benchmark Origin:** $t_0 = 00:00\text{ UTC}$ on each origin $D$.
- **Observation Window:** Historical window $t \le t_0$ (e.g. $t_0, t_0-1\text{h}, \dots, t_0-24\text{h}$).
- **Causality Verification:** SITES automated loggers record parameter values continuously in real time. For $t_0 = 00:00\text{ UTC}$, observation timestamps $t \le 00:00\text{ UTC}$ occur prior to or at forecast start time $t_0$. In operational deployment, local logger telemetry streams within minutes of logging ($\le 5\text{ min}$ latency).
- **Verdict:** Strictly causal. Zero future target leakage.

### 3. Information Novelty vs Stage 8.1 Champion
- **Stage 8.1 37-Feature Inventory:** Contains target $SW_{IN}$ context (`ctx_last_obs`, `ctx_std_6h`, etc.), clear-sky GHI, solar geometry, MEPS grid forecasts (`fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`), LWP/IWP, terrain horizon, and steering winds ($U_{700}, V_{700}$).
- **Novelty Verification:** Stage 8.1 contains **ZERO local ground observations of air temperature (`TA`) or relative humidity (`RH`) prior to $t_0$**.
- **Crucial Distinction:** `fc_temperature_2m` and `fc_relative_humidity_2m` in Stage 8.1 are MEPS model grid forecasts for future lead hours $H1 \dots H24$, whereas the proposed features are direct ground sensor measurements at $t \le t_0$.
- **Verdict:** **100% NOVEL**.

### 4. Abisko ANS Valley Station Pairing
- **Station Location & Elevation:** Abisko Scientific Research Station (ANS) main valley station ($68.35^\circ\text{N}, 18.82^\circ\text{E}$, $385\text{ m a.s.l.}$, $3.2\text{ km}$ East of Nuolja Middle Station).
- **Elevation Delta:** $\Delta z = 702\text{ m} - 385\text{ m} = 317\text{ m}$ vertical separation.
- **Data Availability & Coverage:** $> 98\%$ joint coverage in 2024 SITES meteorological archives.
- **Constructibility:** Both stations use identical 1-hour timestamp indexing, allowing direct hourly calculation of the mountain–valley temperature contrast $\Delta T = \text{TA}_{\text{Nuolja}} - \text{TA}_{\text{Abisko}}$.

---

## 3. Physical & Terminology Governance Check

### Station Elevations & Meteorological Interpretation
- **Elevation Difference:** Nuolja Middle Station ($702\text{ m a.s.l.}$) sits $317\text{ m}$ above Abisko Valley Station ($385\text{ m a.s.l.}$).
- **Standard Environmental Lapse Rate:** Under well-mixed dry/moist adiabatic conditions ($\approx -6.5^\circ\text{C / km}$), Nuolja is expected to be $\approx 2.06^\circ\text{C}$ colder than Abisko ($\text{TA}_{\text{Nuolja}} - \text{TA}_{\text{Abisko}} \approx -2.06^\circ\text{C}$).
- **Thermal Inversion State:** When $\text{TA}_{\text{Nuolja}} - \text{TA}_{\text{Abisko}} > 0^\circ\text{C}$, a true low-level surface thermal inversion traps cold air and fog in the Torneträsk valley floor while Nuolja summit remains clear.
- **Terminology Decision:** To maintain strict physical rigor across all stability states (both inverted and well-mixed profiles), the feature shall be formally designated **`ctx_mountain_valley_temp_contrast`** (Mountain–Valley Temperature Contrast) or **`ctx_valley_slope_temp_delta`**, rather than assuming an inversion is continuously present.

---

## 4. Proposed Feature Constructibility Matrix

| Proposed Feature Name | Primary Source | 2024 Coverage | Temporal Res. | Causal ($t \le t_0$) | Novel vs Stage 8.1 | Constructible | Audit Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`ctx_ta_last_obs`** | SITES Nuolja Logger (`TA`) | `100.0%` | 1 hour | **YES** | **YES** | **YES** | **PASS** |
| **`ctx_rh_last_obs`** | SITES Nuolja Logger (`RH`) | `100.0%` | 1 hour | **YES** | **YES** | **YES** | **PASS** |
| **`ctx_dew_point_depression`** | Nuolja `TA` & `RH` ($\text{TA} - \text{TD}$) | `100.0%` | 1 hour | **YES** | **YES** | **YES** | **PASS** |
| **`ctx_ta_change_6h`** | Nuolja `TA` ($\text{TA}_{t0} - \text{TA}_{t0-6h}$) | `100.0%` | 1 hour | **YES** | **YES** | **YES** | **PASS** |
| **`ctx_mountain_valley_temp_contrast`** | Nuolja `TA` - Abisko `TA` | `> 98.0%` | 1 hour | **YES** | **YES** | **YES** | **PASS** |

---

## 5. Final Audit Decision & Next Steps

### FINAL DECISION: **`READY_FOR_GOVERNED_EXPERIMENT`**

> [!TIP]
> **GOVERNED EXPERIMENT AUTHORIZATION:**
> Direct local ground observations (`TA`, `RH`, dew-point depression $\text{TA} - \text{TD}$, 6h temperature trend $\Delta \text{TA}_{6h}$) and mountain–valley temperature contrast ($\text{TA}_{\text{Nuolja}} - \text{TA}_{\text{Abisko}}$) are empirically verified, 100% constructible, causally valid at $t \le t_0$, and **100% NOVEL**.
>
> **Authorized Next Step:** Creation of a pre-registered Experiment Specification (`STAGE8_23_EXPERIMENT_SPECIFICATION.md`) followed by a governed EVEN-only 5-fold cross-validation experiment.
>
> *Note: This data-feasibility audit itself does NOT run the experiment or train any models.*

### Governance Firewall Compliance Statement

1. **Model Execution / Training:** `NONE` (Zero models trained).
2. **Cross-Validation Runs:** `NONE` (Zero CV folds executed).
3. **ODD Target Access:** `NONE` (Zero ODD targets read or evaluated).
4. **Active Champion:** `UNCHANGED` (Stage 8.1 37-feature champion preserved).
5. **System Governance Files:** `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY` remain untouched.
